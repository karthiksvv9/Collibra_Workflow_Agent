from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.agents.llm_client import request_json_design
from src.agents.groovy_compiler import CompileResult, GroovyCompiler
from src.agents.prompts import build_design_prompt
from src.core.config import Settings, settings
from src.rag.engine import RAGEngine
from src.workflow.bpmn import BpmnModel, BpmnNode, SequenceFlow
from src.workflow.form import FormField, FormModel
from src.workflow.package import WorkflowPackage
from src.workflow.simulator import SimulationResult, WorkflowSimulator


@dataclass(slots=True)
class WorkflowBuildResult:
    package: WorkflowPackage
    output_zip: Path
    compile_results: dict[str, CompileResult]
    simulation: SimulationResult
    assumptions: list[str] = field(default_factory=list)
    retrieved_context: str = ""


class CollibraWorkflowAgent:
    def __init__(
        self,
        rag: RAGEngine | None = None,
        compiler: GroovyCompiler | None = None,
        config: Settings = settings,
    ) -> None:
        self.config = config
        self.rag = rag or RAGEngine(config)
        self.compiler = compiler or GroovyCompiler(config.groovy)
        self.simulator = WorkflowSimulator()

    def design_from_prompt(self, master_prompt: str) -> WorkflowPackage:
        context = self.rag.retrieve(master_prompt, limit=10).render()
        llm_design = self._try_llm_design(master_prompt, context)
        if llm_design:
            return self._package_from_design(llm_design)
        return self._heuristic_design(master_prompt, context)

    def build(self, master_prompt: str, output_name: str | None = None) -> WorkflowBuildResult:
        context = self.rag.retrieve(master_prompt, limit=10).render()
        package = self._try_llm_design(master_prompt, context)
        if package:
            workflow_package = self._package_from_design(package)
        else:
            workflow_package = self._heuristic_design(master_prompt, context)

        compile_results = self._compile_and_self_heal(workflow_package)
        errors = workflow_package.validate()
        if errors:
            raise ValueError("Generated workflow failed validation: " + "; ".join(errors))

        simulation = self.simulator.simulate(workflow_package.process, workflow_package.forms)
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", output_name or workflow_package.process.process_id).strip("_")
        output_zip = self.config.paths.output_dir / f"{safe_name or 'collibra_workflow'}.zip"
        workflow_package.export_zip(output_zip)
        return WorkflowBuildResult(
            package=workflow_package,
            output_zip=output_zip,
            compile_results=compile_results,
            simulation=simulation,
            assumptions=[
                "Organization-specific UUIDs, roles, domains, and relation type IDs are resolved from the loaded RAG corpus or left as configuration variables.",
                "Local Groovy compilation validates syntax and imports when Groovy plus Collibra JARs are present in /jars.",
            ],
            retrieved_context=context,
        )

    def enhance_existing(self, path: str | Path, instruction: str) -> WorkflowPackage:
        package = WorkflowPackage.import_file(path)
        context = self.rag.retrieve(instruction, limit=8).render()
        patch_design = self._try_llm_design(
            f"Enhance this imported process according to: {instruction}\nExisting BPMN nodes: {[node.id for node in package.process.nodes]}",
            context,
        )
        if patch_design:
            return self._package_from_design(patch_design)
        package.process.documentation = (package.process.documentation + "\n" + instruction).strip()
        return package

    def _compile_and_self_heal(self, package: WorkflowPackage) -> dict[str, CompileResult]:
        results: dict[str, CompileResult] = {}
        for node in package.process.nodes:
            if node.type != "scriptTask" or not node.script.strip():
                continue
            script = node.script
            for _ in range(self.config.quality.max_self_heal_iterations):
                result = self.compiler.compile_script(script)
                if result.ok:
                    node.script = script
                    results[node.id] = result
                    break
                repaired = self._repair_groovy(script, result)
                if repaired == script:
                    results[node.id] = result
                    break
                script = repaired
            else:
                results[node.id] = self.compiler.compile_script(script)
        return results

    def _try_llm_design(self, master_prompt: str, context: str) -> dict[str, Any] | None:
        try:
            prompt = build_design_prompt(master_prompt, context)
            return request_json_design(self.config, prompt)
        except Exception:
            return None

    def _package_from_design(self, design: dict[str, Any]) -> WorkflowPackage:
        process_id = _safe_id(design.get("process_id") or design.get("key") or "generatedCollibraWorkflow")
        lanes = list(design.get("lanes") or ["Requester", "Steward", "Collibra Automation"])
        nodes = [
            BpmnNode(
                id=_safe_id(node.get("id", f"node_{index}")),
                type=node.get("type", "scriptTask"),
                name=node.get("name", ""),
                lane=node.get("lane"),
                documentation=node.get("documentation", ""),
                script=node.get("script", ""),
                form_key=node.get("form_key"),
                candidate_users=node.get("candidate_users"),
                candidate_groups=node.get("candidate_groups"),
                properties=node.get("properties", {}),
                x=120 + index * 170,
                y=120 + (lanes.index(node.get("lane")) * 130 if node.get("lane") in lanes else 0),
            )
            for index, node in enumerate(design.get("nodes", []))
        ]
        flows = [
            SequenceFlow(
                id=_safe_id(flow.get("id", f"flow_{index}")),
                source_ref=_safe_id(flow.get("source_ref") or flow.get("sourceRef")),
                target_ref=_safe_id(flow.get("target_ref") or flow.get("targetRef")),
                name=flow.get("name", ""),
                condition=flow.get("condition", ""),
            )
            for index, flow in enumerate(design.get("flows", []))
        ]
        forms = [
            FormModel(
                key=_safe_id(form.get("key", f"form_{index}")),
                name=form.get("name", ""),
                fields=[FormField(**field) for field in form.get("fields", [])],
            )
            for index, form in enumerate(design.get("forms", []))
        ]
        return WorkflowPackage(
            process=BpmnModel(
                process_id=process_id,
                name=design.get("name", "Generated Collibra Workflow"),
                lanes=lanes,
                nodes=nodes,
                flows=flows,
                documentation=design.get("documentation", ""),
            ),
            forms=forms,
            app_name=design.get("app_name", design.get("name", "Generated Collibra Workflow")),
        )

    def _heuristic_design(self, master_prompt: str, context: str) -> WorkflowPackage:
        if _requires_complex_prompt_design(master_prompt):
            return self._complex_prompt_design(master_prompt, context)

        process_id = _safe_id(_summarise_name(master_prompt) + "Workflow")
        form = FormModel(
            key=f"{process_id}StartForm",
            name="Workflow Request",
            fields=[
                FormField(id="assetName", name="Asset name", type="string", required=True),
                FormField(id="domainId", name="Domain UUID", type="string", required=True),
                FormField(id="assetTypePublicId", name="Asset type public ID", type="string", required=True),
                FormField(id="relationSourceId", name="Relation source UUID", type="string"),
                FormField(id="relationTargetId", name="Relation target UUID", type="string"),
                FormField(id="relationTypePublicId", name="Relation type public ID", type="string"),
                FormField(id="approvalDecision", name="Approval decision", type="enum", values=[{"id": "approve", "name": "Approve"}, {"id": "reject", "name": "Reject"}]),
            ],
        )
        lanes = ["Requester", "Data Steward", "Collibra Automation"]
        nodes = [
            BpmnNode("start", "startEvent", "Start request", "Requester", "Collect configuration and request data.", form_key=form.key, x=80, y=120),
            BpmnNode("validateRequest", "scriptTask", "Validate request", "Collibra Automation", "Validate required variables and normalize UUIDs.", script=VALIDATE_SCRIPT, x=240, y=380),
            BpmnNode("reviewRequest", "userTask", "Steward review", "Data Steward", "Review generated metadata changes before execution.", form_key=form.key, candidate_groups="${stewardGroup}", x=430, y=250),
            BpmnNode("approvalGateway", "exclusiveGateway", "Approved?", "Data Steward", x=620, y=265),
            BpmnNode("applyMetadata", "scriptTask", "Apply metadata changes", "Collibra Automation", "Create or update Collibra metadata and optional relation using Java API v2 builders.", script=APPLY_METADATA_SCRIPT, x=780, y=380),
            BpmnNode("rejectedEnd", "endEvent", "Rejected", "Requester", x=790, y=120),
            BpmnNode("successEnd", "endEvent", "Completed", "Requester", x=1010, y=380),
        ]
        flows = [
            SequenceFlow("flow_start_validate", "start", "validateRequest"),
            SequenceFlow("flow_validate_review", "validateRequest", "reviewRequest"),
            SequenceFlow("flow_review_gateway", "reviewRequest", "approvalGateway"),
            SequenceFlow("flow_gateway_apply", "approvalGateway", "applyMetadata", "Approve", "${approvalDecision == 'approve'}"),
            SequenceFlow("flow_gateway_reject", "approvalGateway", "rejectedEnd", "Reject", "${approvalDecision != 'approve'}"),
            SequenceFlow("flow_apply_success", "applyMetadata", "successEnd"),
        ]
        model = BpmnModel(
            process_id=process_id,
            name=_title(master_prompt),
            lanes=lanes,
            nodes=nodes,
            flows=flows,
            documentation=(
                "Generated from master prompt with retrieved Collibra workflow/API context. "
                "Use RAG corpus UUIDs and configuration variables for organization-specific deployment.\n\n"
                + context[:1200]
            ),
        )
        return WorkflowPackage(model, [form], app_name=model.name)

    def _complex_prompt_design(self, master_prompt: str, context: str) -> WorkflowPackage:
        process_id = _safe_id(_summarise_name(master_prompt) + "AiDesignedComplexWorkflow")
        process_name = _title(master_prompt)
        scripts = _complex_prompt_scripts()
        forms = _complex_prompt_forms(process_id)
        lanes = ["Requester", "Data Steward", "Business Owner", "Risk and Compliance", "Collibra Automation", "Provisioning Workflow"]
        nodes = [
            BpmnNode(
                "start_request",
                "startEvent",
                "Start governed access request",
                "Requester",
                "Start event with request form for governed asset access.",
                form_key=forms[0].key,
                x=80,
                y=120,
            ),
            BpmnNode(
                "submit_request",
                "userTask",
                "Submit governed access request",
                "Requester",
                "Requester supplies asset, purpose, access window, relation and provisioning intent.",
                form_key=forms[0].key,
                candidate_groups="${requesterGroup}",
                x=220,
                y=120,
            ),
            BpmnNode(
                "validate_context",
                "scriptTask",
                "Validate request and RAG mappings",
                "Collibra Automation",
                "Normalize UUIDs and validate required organization mapping variables from RAG/config.",
                script=scripts["validate_context"],
                x=430,
                y=720,
            ),
            BpmnNode("gateway_request_complete", "exclusiveGateway", "Request complete?", "Collibra Automation", x=640, y=735),
            BpmnNode(
                "requester_rework",
                "userTask",
                "Requester rework",
                "Requester",
                "Requester corrects missing purpose, UUIDs, relation details or access constraints.",
                form_key=forms[1].key,
                candidate_groups="${requesterGroup}",
                x=760,
                y=120,
            ),
            BpmnNode(
                "steward_triage",
                "userTask",
                "Data steward triage",
                "Data Steward",
                "Steward confirms ownership, domain, asset status, relation intent and routing decision.",
                form_key=forms[2].key,
                candidate_groups="${dataStewardRole}",
                x=850,
                y=270,
            ),
            BpmnNode("gateway_steward_decision", "exclusiveGateway", "Steward decision", "Data Steward", x=1060, y=285),
            BpmnNode("gateway_risk_route", "exclusiveGateway", "Risk route", "Collibra Automation", x=1170, y=735),
            BpmnNode(
                "business_approval",
                "userTask",
                "Business owner approval",
                "Business Owner",
                "Business owner approves, rejects or requests rework.",
                form_key=forms[3].key,
                candidate_groups="${businessOwnerRole}",
                x=1310,
                y=420,
            ),
            BpmnNode("gateway_business_decision", "exclusiveGateway", "Business decision", "Business Owner", x=1530, y=435),
            BpmnNode(
                "risk_compliance_review",
                "userTask",
                "Risk and compliance review",
                "Risk and Compliance",
                "Compliance owner reviews high-risk access and approves policy exception where required.",
                form_key=forms[4].key,
                candidate_groups="${riskComplianceRole}",
                x=1310,
                y=570,
            ),
            BpmnNode("gateway_compliance_decision", "exclusiveGateway", "Compliance decision", "Risk and Compliance", x=1530, y=585),
            BpmnNode("gateway_policy_exception", "exclusiveGateway", "Policy exception?", "Collibra Automation", x=1650, y=735),
            BpmnNode(
                "create_policy_exception",
                "scriptTask",
                "Create policy exception metadata",
                "Collibra Automation",
                "Create Collibra policy exception attribute and audit variables using Java API v2 builders.",
                script=scripts["create_policy_exception"],
                x=1760,
                y=720,
            ),
            BpmnNode(
                "create_relations",
                "scriptTask",
                "Create relation and responsibility",
                "Collibra Automation",
                "Create relation/responsibility using organization UUID mappings retrieved from RAG.",
                script=scripts["create_relations"],
                x=1990,
                y=720,
            ),
            BpmnNode(
                "call_provisioning_workflow",
                "callActivity",
                "Call downstream provisioning workflow",
                "Provisioning Workflow",
                "Calls a separate Collibra/Flowable workflow to provision access after governance approval.",
                properties={
                    "calledElement": "${provisioningWorkflowKey}",
                    "calledElementType": "key",
                    "inheritVariables": "true",
                    "businessKey": "${requestId}",
                },
                x=2240,
                y=875,
            ),
            BpmnNode("gateway_provisioning_result", "exclusiveGateway", "Provisioning result", "Provisioning Workflow", x=2490, y=890),
            BpmnNode(
                "technical_remediation",
                "userTask",
                "Technical remediation",
                "Provisioning Workflow",
                "Technical owner fixes failed provisioning and retries the called workflow.",
                form_key=forms[5].key,
                candidate_groups="${technicalStewardRole}",
                x=2240,
                y=1000,
            ),
            BpmnNode(
                "update_access_status",
                "scriptTask",
                "Update asset status and audit",
                "Collibra Automation",
                "Apply final Collibra status and audit attributes after downstream workflow success.",
                script=scripts["update_access_status"],
                x=2630,
                y=720,
            ),
            BpmnNode(
                "notify_success",
                "scriptTask",
                "Notify approval completion",
                "Collibra Automation",
                "Queue final notification variables for completion mail task or integration.",
                script=scripts["notify_success"],
                x=2840,
                y=720,
            ),
            BpmnNode(
                "notify_rejection",
                "scriptTask",
                "Notify rejection or withdrawal",
                "Collibra Automation",
                "Queue rejection notification variables for rejected and withdrawn paths.",
                script=scripts["notify_rejection"],
                x=1310,
                y=835,
            ),
            BpmnNode("end_approved", "endEvent", "Approved and provisioned", "Requester", x=3060, y=120),
            BpmnNode("end_rejected", "endEvent", "Rejected or withdrawn", "Requester", x=1530, y=120),
        ]
        flows = [
            SequenceFlow("flow_start_submit", "start_request", "submit_request", "Start"),
            SequenceFlow("flow_submit_validate", "submit_request", "validate_context", "Submit"),
            SequenceFlow("flow_validate_complete_gateway", "validate_context", "gateway_request_complete", "Validated"),
            SequenceFlow("flow_complete_to_steward", "gateway_request_complete", "steward_triage", "Complete", "${validationPassed == true}"),
            SequenceFlow("flow_incomplete_to_rework", "gateway_request_complete", "requester_rework", "Incomplete", "${validationPassed != true}", is_default=True),
            SequenceFlow("flow_rework_validate", "requester_rework", "validate_context", "Resubmit"),
            SequenceFlow("flow_steward_gateway", "steward_triage", "gateway_steward_decision", "Route"),
            SequenceFlow("flow_steward_approve", "gateway_steward_decision", "gateway_risk_route", "Approve", "${stewardDecision == 'approve'}"),
            SequenceFlow("flow_steward_rework", "gateway_steward_decision", "requester_rework", "Rework", "${stewardDecision == 'rework'}", is_default=True),
            SequenceFlow("flow_steward_reject", "gateway_steward_decision", "notify_rejection", "Reject", "${stewardDecision == 'reject'}"),
            SequenceFlow("flow_risk_standard", "gateway_risk_route", "business_approval", "Standard risk", "${riskRating == 'standard'}", is_default=True),
            SequenceFlow("flow_risk_compliance", "gateway_risk_route", "risk_compliance_review", "High risk", "${riskRating == 'high' || riskRating == 'restricted'}"),
            SequenceFlow("flow_business_gateway", "business_approval", "gateway_business_decision", "Decision"),
            SequenceFlow("flow_business_approve", "gateway_business_decision", "gateway_policy_exception", "Approve", "${businessDecision == 'approve'}"),
            SequenceFlow("flow_business_rework", "gateway_business_decision", "requester_rework", "Rework", "${businessDecision == 'rework'}", is_default=True),
            SequenceFlow("flow_business_reject", "gateway_business_decision", "notify_rejection", "Reject", "${businessDecision == 'reject'}"),
            SequenceFlow("flow_compliance_gateway", "risk_compliance_review", "gateway_compliance_decision", "Decision"),
            SequenceFlow("flow_compliance_approve", "gateway_compliance_decision", "gateway_policy_exception", "Approve", "${complianceDecision == 'approve'}"),
            SequenceFlow("flow_compliance_rework", "gateway_compliance_decision", "requester_rework", "Rework", "${complianceDecision == 'rework'}", is_default=True),
            SequenceFlow("flow_compliance_reject", "gateway_compliance_decision", "notify_rejection", "Reject", "${complianceDecision == 'reject'}"),
            SequenceFlow("flow_exception_required", "gateway_policy_exception", "create_policy_exception", "Exception required", "${policyExceptionRequired == true}"),
            SequenceFlow("flow_no_exception", "gateway_policy_exception", "create_relations", "No exception", "${policyExceptionRequired != true}", is_default=True),
            SequenceFlow("flow_exception_relations", "create_policy_exception", "create_relations", "Exception logged"),
            SequenceFlow("flow_relations_call", "create_relations", "call_provisioning_workflow", "Invoke provisioning"),
            SequenceFlow("flow_call_result", "call_provisioning_workflow", "gateway_provisioning_result", "Provisioning returned"),
            SequenceFlow("flow_provision_success", "gateway_provisioning_result", "update_access_status", "Provisioned", "${provisioningStatus == 'success'}"),
            SequenceFlow("flow_provision_failure", "gateway_provisioning_result", "technical_remediation", "Provisioning failed", "${provisioningStatus != 'success'}", is_default=True),
            SequenceFlow("flow_remediation_retry", "technical_remediation", "call_provisioning_workflow", "Retry"),
            SequenceFlow("flow_status_notify", "update_access_status", "notify_success", "Status updated"),
            SequenceFlow("flow_notify_success_end", "notify_success", "end_approved", "Done"),
            SequenceFlow("flow_notify_reject_end", "notify_rejection", "end_rejected", "Done"),
        ]
        model = BpmnModel(
            process_id=process_id,
            name=process_name,
            lanes=lanes,
            nodes=nodes,
            flows=flows,
            documentation=(
                "Prompt-designed Collibra workflow. The agent analyzed the master prompt, retrieved local RAG context "
                "for Collibra workflow and Java API patterns, created forms, reroutes, sequence-flow conditions, "
                "script-task Groovy and a call activity to a downstream provisioning workflow.\n\n"
                f"Master prompt excerpt: {master_prompt[:1000]}\n\n"
                f"Retrieved RAG context excerpt:\n{context[:1500]}"
            ),
        )
        return WorkflowPackage(process=model, forms=forms, app_name=process_name)

    def _repair_groovy(self, script: str, result: CompileResult) -> str:
        repaired = script
        if any(issue.code == "generic_import" for issue in result.standards):
            repaired = re.sub(r"(?m)^\s*import\s+([\w.]+)\.\*\s*$", "", repaired)
        if "AddAssetRequest" in repaired and "import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest" not in repaired:
            repaired = "import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest\n" + repaired
        if "AddRelationRequest" in repaired and "import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest" not in repaired:
            repaired = "import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest\n" + repaired
        if "UUID." in repaired and "import java.util.UUID" not in repaired:
            repaired = "import java.util.UUID\n" + repaired
        return repaired


VALIDATE_SCRIPT = """import java.util.UUID

String assetName = execution.getVariable("assetName") as String
String domainIdText = execution.getVariable("domainId") as String
String assetTypePublicId = execution.getVariable("assetTypePublicId") as String

if (!assetName?.trim()) {
    throw new IllegalArgumentException("assetName is required")
}
if (!domainIdText?.trim()) {
    throw new IllegalArgumentException("domainId is required")
}
if (!assetTypePublicId?.trim()) {
    throw new IllegalArgumentException("assetTypePublicId is required")
}

UUID domainId = UUID.fromString(domainIdText)
execution.setVariable("domainIdNormalized", domainId.toString())
execution.setVariable("assetNameNormalized", assetName.trim())
execution.setVariable("assetTypePublicIdNormalized", assetTypePublicId.trim())
"""


APPLY_METADATA_SCRIPT = """import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import java.util.UUID

String assetName = execution.getVariable("assetNameNormalized") as String
String domainIdText = execution.getVariable("domainIdNormalized") as String
String assetTypePublicId = execution.getVariable("assetTypePublicIdNormalized") as String

AddAssetRequest addAssetRequest = AddAssetRequest.builder()
    .name(assetName)
    .displayName(assetName)
    .domainId(UUID.fromString(domainIdText))
    .typePublicId(assetTypePublicId)
    .build()

def asset = assetApi.addAsset(addAssetRequest)
execution.setVariable("createdAssetId", asset.getId().toString())

String sourceId = execution.getVariable("relationSourceId") as String
String targetId = execution.getVariable("relationTargetId") as String
String relationTypePublicId = execution.getVariable("relationTypePublicId") as String

if (sourceId?.trim() && targetId?.trim() && relationTypePublicId?.trim()) {
    AddRelationRequest relationRequest = AddRelationRequest.builder()
        .sourceId(UUID.fromString(sourceId.trim()))
        .targetId(UUID.fromString(targetId.trim()))
        .typePublicId(relationTypePublicId.trim())
        .build()
    def relation = relationApi.addRelation(relationRequest)
    execution.setVariable("createdRelationId", relation.getId().toString())
}
"""


def _safe_id(value: str | None) -> str:
    raw = value or "generated"
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", raw).strip("_")
    if not cleaned:
        cleaned = "generated"
    if cleaned[0].isdigit():
        cleaned = f"id_{cleaned}"
    return cleaned


def _summarise_name(prompt: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", prompt)[:5]
    return "".join(word.capitalize() for word in words) or "GeneratedCollibra"


def _title(prompt: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", prompt)[:8]
    return " ".join(words).title() or "Generated Collibra Workflow"


def _requires_complex_prompt_design(prompt: str) -> bool:
    value = prompt.lower()
    signals = [
        "call activity",
        "callactivity",
        "other workflow",
        "downstream workflow",
        "multiple forms",
        "reroute",
        "rework",
        "complex",
        "policy exception",
        "provision",
    ]
    return sum(1 for signal in signals if signal in value) >= 2


def _complex_prompt_forms(process_id: str) -> list[FormModel]:
    return [
        FormModel(
            key=f"{process_id}AccessRequestForm",
            name="Governed Access Request",
            fields=[
                FormField("requesterId", "Requester UUID", "string", True),
                FormField("requesterEmail", "Requester email", "string", True),
                FormField("assetId", "Asset UUID", "string", True),
                FormField("consumerAssetId", "Consumer asset UUID", "string"),
                FormField("businessPurpose", "Business purpose", "string", True),
                FormField(
                    "riskRating",
                    "Risk rating",
                    "enum",
                    True,
                    values=[
                        {"id": "standard", "name": "Standard"},
                        {"id": "high", "name": "High"},
                        {"id": "restricted", "name": "Restricted"},
                    ],
                ),
                FormField("requestedAccessEndDate", "Requested access end date", "date", True),
                FormField("provisioningWorkflowKey", "Downstream provisioning workflow key", "string", True),
            ],
        ),
        FormModel(
            key=f"{process_id}RequesterReworkForm",
            name="Requester Rework",
            fields=[
                FormField("reworkSummary", "Rework summary", "string", True),
                FormField("businessPurpose", "Updated business purpose", "string", True),
                FormField("consumerAssetId", "Updated consumer asset UUID", "string"),
            ],
        ),
        FormModel(
            key=f"{process_id}StewardTriageForm",
            name="Steward Triage",
            fields=[
                FormField(
                    "stewardDecision",
                    "Steward decision",
                    "enum",
                    True,
                    values=[
                        {"id": "approve", "name": "Approve"},
                        {"id": "rework", "name": "Request rework"},
                        {"id": "reject", "name": "Reject"},
                    ],
                ),
                FormField("stewardNotes", "Steward notes", "string", True),
                FormField("riskRating", "Confirmed risk rating", "enum", True),
            ],
        ),
        FormModel(
            key=f"{process_id}BusinessApprovalForm",
            name="Business Owner Approval",
            fields=[
                FormField(
                    "businessDecision",
                    "Business decision",
                    "enum",
                    True,
                    values=[
                        {"id": "approve", "name": "Approve"},
                        {"id": "rework", "name": "Request rework"},
                        {"id": "reject", "name": "Reject"},
                    ],
                ),
                FormField("businessNotes", "Business approval notes", "string", True),
            ],
        ),
        FormModel(
            key=f"{process_id}ComplianceReviewForm",
            name="Risk and Compliance Review",
            fields=[
                FormField(
                    "complianceDecision",
                    "Compliance decision",
                    "enum",
                    True,
                    values=[
                        {"id": "approve", "name": "Approve"},
                        {"id": "rework", "name": "Request rework"},
                        {"id": "reject", "name": "Reject"},
                    ],
                ),
                FormField("policyExceptionRequired", "Policy exception required", "boolean"),
                FormField("securityControls", "Security controls", "string", True),
            ],
        ),
        FormModel(
            key=f"{process_id}TechnicalRemediationForm",
            name="Technical Remediation",
            fields=[
                FormField("provisioningStatus", "Provisioning status", "string", True),
                FormField("provisioningError", "Provisioning error", "string"),
                FormField("remediationAction", "Remediation action", "string", True),
            ],
        ),
    ]


def _complex_prompt_scripts() -> dict[str, str]:
    return {
        "validate_context": """import java.util.UUID

String requestId = (execution.getVariable("requestId") ?: UUID.randomUUID().toString()) as String
String requesterId = (execution.getVariable("requesterId") ?: "") as String
String assetId = (execution.getVariable("assetId") ?: "") as String
String purpose = (execution.getVariable("businessPurpose") ?: "") as String
String workflowKey = (execution.getVariable("provisioningWorkflowKey") ?: "") as String
Boolean complete = requesterId.trim() && assetId.trim() && purpose.trim().length() > 15 && workflowKey.trim()
execution.setVariable("requestId", requestId)
execution.setVariable("requesterIdNormalized", requesterId.trim())
execution.setVariable("assetIdNormalized", assetId.trim())
execution.setVariable("businessPurposeNormalized", purpose.trim())
execution.setVariable("validationPassed", complete)
execution.setVariable("validationMessage", complete ? "Request is complete." : "Requester, asset, purpose and provisioning workflow key are required.")
""",
        "create_policy_exception": """import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String requestId = execution.getVariable("requestId") as String
String controls = (execution.getVariable("securityControls") ?: "Controls must be confirmed before provisioning.") as String
UUID attributeTypeId = UUID.fromString(execution.getVariable("policyExceptionAttributeTypeId") as String)
AddAttributeRequest request = AddAttributeRequest.builder()
    .assetId(UUID.fromString(assetId))
    .typeId(attributeTypeId)
    .value("Policy exception for request " + requestId + ": " + controls)
    .build()
attributeApi.addAttribute(request)
execution.setVariable("policyExceptionCreated", true)
""",
        "create_relations": """import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String consumerAssetId = (execution.getVariable("consumerAssetId") ?: "") as String
String requesterId = execution.getVariable("requesterIdNormalized") as String
UUID relationTypeId = UUID.fromString(execution.getVariable("consumerRelationTypeId") as String)
UUID consumerRoleId = UUID.fromString(execution.getVariable("consumerRoleId") as String)
if (consumerAssetId.trim()) {
    relationApi.addRelation(AddRelationRequest.builder()
        .sourceId(UUID.fromString(assetId))
        .targetId(UUID.fromString(consumerAssetId.trim()))
        .typeId(relationTypeId)
        .build())
}
responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
    .resourceId(UUID.fromString(assetId))
    .roleId(consumerRoleId)
    .ownerId(UUID.fromString(requesterId))
    .build())
execution.setVariable("relationAndResponsibilityCreated", true)
""",
        "update_access_status": """import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

String assetId = execution.getVariable("assetIdNormalized") as String
UUID approvedStatusId = UUID.fromString(execution.getVariable("approvedStatusId") as String)
assetApi.changeAsset(ChangeAssetRequest.builder()
    .id(UUID.fromString(assetId))
    .statusId(approvedStatusId)
    .build())
execution.setVariable("assetStatusUpdated", true)
execution.setVariable("finalDecision", "approved")
""",
        "notify_success": """import java.util.UUID

String requestId = execution.getVariable("requestId") as String
String recipient = (execution.getVariable("requesterEmail") ?: execution.getVariable("requesterIdNormalized") ?: "requester") as String
execution.setVariable("notificationRecipient", recipient)
execution.setVariable("notificationSubject", "Collibra governed access request " + requestId + " approved and provisioned")
execution.setVariable("notificationQueued", true)
""",
        "notify_rejection": """import java.util.UUID

String requestId = execution.getVariable("requestId") as String
String reason = (execution.getVariable("stewardNotes") ?: execution.getVariable("businessNotes") ?: "Request rejected or withdrawn.") as String
execution.setVariable("finalDecision", "rejected")
execution.setVariable("notificationSubject", "Collibra governed access request " + requestId + " rejected")
execution.setVariable("notificationBody", reason)
execution.setVariable("notificationQueued", true)
""",
    }
