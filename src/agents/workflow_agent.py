from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.agents.llm_client import LLMRequestError, request_json_design
from src.agents.groovy_compiler import CompileResult, GroovyCompiler
from src.agents.prompts import build_design_prompt
from src.core.config import Settings, settings
from src.rag.engine import RAGEngine
from src.workflow.bpmn import BpmnModel, BpmnNode, BpmnPool, SequenceFlow
from src.workflow.form import FormField, FormModel, form_field_from_mapping
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

    def design_from_prompt(self, master_prompt: str, model_id: str | None = None) -> WorkflowPackage:
        context = self.rag.retrieve(master_prompt, limit=10).render()
        llm_design = self._try_llm_design(master_prompt, context, model_id=model_id)
        if llm_design and _design_satisfies_prompt(master_prompt, llm_design):
            return self._package_from_design(llm_design)
        return self._heuristic_design(master_prompt, context)

    def build(
        self,
        master_prompt: str,
        output_name: str | None = None,
        model_id: str | None = None,
        require_ai: bool = False,
    ) -> WorkflowBuildResult:
        context = self.rag.retrieve(master_prompt, limit=10).render()
        package = self._try_llm_design(master_prompt, context, model_id=model_id, raise_on_error=require_ai)
        used_llm_design = False
        if package and _design_satisfies_prompt(master_prompt, package):
            workflow_package = self._package_from_design(package)
            used_llm_design = True
        elif package and require_ai:
            raise ValueError(
                "AI workflow design returned valid JSON but did not satisfy the prompt complexity requirements. "
                "For complex workflows it must include multiple forms, reroutes, a call activity when requested, and complete sequence flows."
            )
        elif require_ai:
            raise ValueError(
                "AI workflow design did not return a valid JSON BPMN design. Check the selected model, API key, and prompt, then try again."
            )
        else:
            workflow_package = self._heuristic_design(master_prompt, context)

        compile_results = self._compile_and_self_heal(workflow_package)
        compile_failures = _compile_failure_summaries(compile_results)
        if compile_failures and used_llm_design and not require_ai:
            workflow_package = self._heuristic_design(master_prompt, context)
            compile_results = self._compile_and_self_heal(workflow_package)
            compile_failures = _compile_failure_summaries(compile_results)
        if compile_failures:
            raise ValueError("Generated Groovy failed compilation/lint validation: " + "; ".join(compile_failures))
        errors = workflow_package.validate()
        if errors and used_llm_design and not require_ai:
            workflow_package = self._heuristic_design(master_prompt, context)
            compile_results = self._compile_and_self_heal(workflow_package)
            compile_failures = _compile_failure_summaries(compile_results)
            if compile_failures:
                raise ValueError("Generated Groovy failed compilation/lint validation: " + "; ".join(compile_failures))
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

    def _try_llm_design(
        self,
        master_prompt: str,
        context: str,
        model_id: str | None = None,
        raise_on_error: bool = False,
    ) -> dict[str, Any] | None:
        try:
            prompt = build_design_prompt(master_prompt, context)
            return request_json_design(
                self.config,
                prompt,
                model_id=model_id,
                action="workflow_design",
                raise_on_error=raise_on_error,
            )
        except LLMRequestError:
            if raise_on_error:
                raise
            return None
        except Exception:
            if raise_on_error:
                raise
            return None

    def _package_from_design(self, design: dict[str, Any]) -> WorkflowPackage:
        process_id = _safe_id(design.get("process_id") or design.get("key") or "generatedCollibraWorkflow")
        lanes = [str(lane) for lane in (design.get("lanes") or ["Requester", "Data Steward", "Collibra Automation"]) if str(lane).strip()]
        lanes = lanes or ["Requester", "Data Steward", "Collibra Automation"]
        nodes: list[BpmnNode] = []
        flow_like_nodes: list[dict[str, Any]] = []
        for index, node in enumerate(design.get("nodes", [])):
            if not isinstance(node, dict):
                continue
            node_type = _normalize_node_type(node.get("type", "scriptTask"))
            if node_type == "sequenceFlow":
                flow_like_nodes.append(node)
                continue
            lane = _lane_for_node({**node, "type": node_type}, lanes)
            script = _sanitize_generated_groovy(str(node.get("script") or ""))
            if script and node_type not in {"scriptTask", "serviceTask", "sendTask"}:
                node_type = "scriptTask"
            nodes.append(
                BpmnNode(
                    id=_safe_id(node.get("id", f"node_{index}")),
                    type=node_type,
                    name=node.get("name", ""),
                    lane=lane,
                    documentation=node.get("documentation", ""),
                    script=script,
                    form_key=node.get("form_key") or node.get("formKey"),
                    candidate_users=node.get("candidate_users"),
                    candidate_groups=node.get("candidate_groups"),
                    properties=node.get("properties", {}),
                    x=int(node.get("x") or (180 + index * 180)),
                    y=int(node.get("y") or _lane_y(lane, lanes)),
                )
            )
        nodes = _ensure_start_end_nodes(nodes, lanes)
        raw_flows = list(design.get("flows") or design.get("sequence_flows") or design.get("sequenceFlows") or [])
        raw_flows.extend(flow_like_nodes)
        flows = [
            SequenceFlow(
                id=_safe_id(flow.get("id", f"flow_{index}")),
                source_ref=_safe_id(flow.get("source_ref") or flow.get("sourceRef")),
                target_ref=_safe_id(flow.get("target_ref") or flow.get("targetRef")),
                name=flow.get("name", ""),
                condition=_normalize_expression(flow.get("condition", "")),
                skip_expression=_normalize_expression(flow.get("skip_expression") or flow.get("skipExpression", "")),
                flow_type=flow.get("flow_type") or flow.get("flowType") or ("conditional" if flow.get("condition") else "normal"),
                is_default=bool(flow.get("is_default") or flow.get("isDefault", False)),
                documentation=flow.get("documentation", ""),
                listener_code=flow.get("listener_code") or flow.get("listenerCode", ""),
                properties=flow.get("properties", {}),
            )
            for index, flow in enumerate(raw_flows)
            if isinstance(flow, dict)
        ]
        flows = _repair_linear_flow_continuity(nodes, flows)
        forms = [
            FormModel(
                key=_safe_id(form.get("key", f"form_{index}")),
                name=form.get("name", ""),
                fields=[form_field_from_mapping(field) for field in form.get("fields", []) if isinstance(field, dict)],
            )
            for index, form in enumerate(design.get("forms", []))
            if isinstance(form, dict)
        ]
        forms = _ensure_referenced_forms(forms, nodes)
        width = max([node.x for node in nodes] or [1000]) + 260
        height = 80 + len(lanes) * 170
        return WorkflowPackage(
            process=BpmnModel(
                process_id=process_id,
                name=design.get("name", "Generated Collibra Workflow"),
                pools=[
                    BpmnPool(
                        id=f"{process_id}_pool",
                        name=design.get("pool_name") or design.get("name", "Generated Collibra Workflow"),
                        process_ref=process_id,
                        width=max(1240, width),
                        height=max(520, height),
                    )
                ],
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
            pools=[BpmnPool(id=f"{process_id}_pool", name=_title(master_prompt), process_ref=process_id)],
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
        profile = _complex_prompt_profile(master_prompt)
        scripts = _complex_prompt_scripts()
        forms = _complex_prompt_forms(process_id, profile)
        lanes = ["Requester", "Data Steward", "Business Owner", "Risk and Compliance", "Collibra Automation", profile["called_lane"]]
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
                profile["call_activity_name"],
                profile["called_lane"],
                profile["call_activity_documentation"],
                properties={
                    "calledElement": profile["called_element"],
                    "calledElementType": "key",
                    "inheritVariables": "true",
                    "businessKey": "${requestId}",
                },
                x=2240,
                y=875,
            ),
            BpmnNode("gateway_provisioning_result", "exclusiveGateway", profile["result_gateway_name"], profile["called_lane"], x=2490, y=890),
            BpmnNode(
                "technical_remediation",
                "userTask",
                profile["remediation_task_name"],
                profile["called_lane"],
                profile["remediation_documentation"],
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
            SequenceFlow("flow_relations_call", "create_relations", "call_provisioning_workflow", profile["invoke_flow_name"]),
            SequenceFlow("flow_call_result", "call_provisioning_workflow", "gateway_provisioning_result", profile["returned_flow_name"]),
            SequenceFlow("flow_provision_success", "gateway_provisioning_result", "update_access_status", profile["success_flow_name"], "${provisioningStatus == 'success'}"),
            SequenceFlow("flow_provision_failure", "gateway_provisioning_result", "technical_remediation", profile["failure_flow_name"], "${provisioningStatus != 'success'}", is_default=True),
            SequenceFlow("flow_remediation_retry", "technical_remediation", "call_provisioning_workflow", "Retry"),
            SequenceFlow("flow_status_notify", "update_access_status", "notify_success", "Status updated"),
            SequenceFlow("flow_notify_success_end", "notify_success", "end_approved", "Done"),
            SequenceFlow("flow_notify_reject_end", "notify_rejection", "end_rejected", "Done"),
        ]
        model = BpmnModel(
            process_id=process_id,
            name=process_name,
            pools=[
                BpmnPool(
                    id=f"{process_id}_pool",
                    name=process_name,
                    process_ref=process_id,
                    width=3420,
                    height=1180,
                )
            ],
            lanes=lanes,
            nodes=nodes,
            flows=flows,
            documentation=(
                "Prompt-designed Collibra workflow. The agent analyzed the master prompt, retrieved local RAG context "
                "for Collibra workflow and Java API patterns, created forms, reroutes, sequence-flow conditions, "
                f"script-task Groovy and a call activity to {profile['called_element']}.\n\n"
                f"Master prompt excerpt: {master_prompt[:1000]}\n\n"
                f"Retrieved RAG context excerpt:\n{context[:1500]}"
            ),
        )
        return WorkflowPackage(process=model, forms=forms, app_name=process_name)

    def _repair_groovy(self, script: str, result: CompileResult) -> str:
        repaired = script
        if any(issue.code == "generic_import" for issue in result.standards):
            repaired = re.sub(r"(?m)^\s*import\s+([\w.]+)\.\*\s*$", "", repaired)
        if any(issue.code in {"invalid_uuid_import", "unused_uuid_import", "java_class_wrapper"} for issue in result.standards):
            repaired = re.sub(r"(?m)^\s*import\s+(?:uuid|UUID|[\w.]*\.uuid(?:\.[\w.*]+)?)\s*;?\s*\n?", "", repaired, flags=re.IGNORECASE)
            repaired = re.sub(r"(?m)^\s*import\s+java\.util\.UUID\s*;?\s*\n?", "", repaired)
        repaired = repaired.replace("UUID.randomUUID()", "java.util.UUID.randomUUID()")
        repaired = re.sub(r"\bUUID\.fromString\s*\(", "string2Uuid(", repaired)
        repaired = re.sub(r"\bUUID\s+([A-Za-z_]\w*)\s*=", r"def \1 =", repaired)
        if "AddAssetRequest" in repaired and "import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest" not in repaired:
            repaired = "import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest\n" + repaired
        if "AddRelationRequest" in repaired and "import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest" not in repaired:
            repaired = "import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest\n" + repaired
        return repaired


VALIDATE_SCRIPT = """// #importFile NONE

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

def domainId = string2Uuid(domainIdText.trim())
execution.setVariable("domainIdNormalized", domainId.toString())
execution.setVariable("assetNameNormalized", assetName.trim())
execution.setVariable("assetTypePublicIdNormalized", assetTypePublicId.trim())
"""


APPLY_METADATA_SCRIPT = """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest

String assetName = execution.getVariable("assetNameNormalized") as String
String domainIdText = execution.getVariable("domainIdNormalized") as String
String assetTypePublicId = execution.getVariable("assetTypePublicIdNormalized") as String

AddAssetRequest addAssetRequest = AddAssetRequest.builder()
    .name(assetName)
    .displayName(assetName)
    .domainId(string2Uuid(domainIdText))
    .typePublicId(assetTypePublicId)
    .build()

def asset = assetApi.addAsset(addAssetRequest)
execution.setVariable("createdAssetId", asset.getId().toString())

String sourceId = execution.getVariable("relationSourceId") as String
String targetId = execution.getVariable("relationTargetId") as String
String relationTypePublicId = execution.getVariable("relationTypePublicId") as String

if (sourceId?.trim() && targetId?.trim() && relationTypePublicId?.trim()) {
    AddRelationRequest relationRequest = AddRelationRequest.builder()
        .sourceId(string2Uuid(sourceId.trim()))
        .targetId(string2Uuid(targetId.trim()))
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


SUPPORTED_NODE_TYPES = {
    "startEvent",
    "endEvent",
    "userTask",
    "scriptTask",
    "serviceTask",
    "manualTask",
    "businessRuleTask",
    "sendTask",
    "receiveTask",
    "exclusiveGateway",
    "parallelGateway",
    "inclusiveGateway",
    "eventBasedGateway",
    "subProcess",
    "callActivity",
    "intermediateCatchEvent",
    "intermediateThrowEvent",
    "boundaryEvent",
    "textAnnotation",
}


def _normalize_node_type(value: Any) -> str:
    raw = str(value or "scriptTask").strip()
    raw = raw.split(":", 1)[-1]
    lowered = raw[:1].lower() + raw[1:]
    aliases = {
        "task": "userTask",
        "formTask": "userTask",
        "approvalTask": "userTask",
        "groovyTask": "scriptTask",
        "apiTask": "serviceTask",
        "gateway": "exclusiveGateway",
        "sequenceflow": "sequenceFlow",
        "sequenceFlow": "sequenceFlow",
        "flow": "sequenceFlow",
    }
    normalized = aliases.get(raw) or aliases.get(lowered) or lowered
    if normalized in SUPPORTED_NODE_TYPES or normalized == "sequenceFlow":
        return normalized
    if normalized.lower().endswith("gateway"):
        return "exclusiveGateway"
    if normalized.lower().endswith("event"):
        return "intermediateCatchEvent"
    return "scriptTask"


def _sanitize_generated_groovy(script: str) -> str:
    repaired = str(script or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    repaired = re.sub(r"```(?:groovy|java|text)?\s*(.*?)```", r"\1", repaired, flags=re.DOTALL | re.IGNORECASE).strip()
    repaired = re.sub(r"(?m)^\s*import\s+[\w.]+\.\*\s*;?\s*\n?", "", repaired)
    repaired = re.sub(r"(?m)^\s*import\s+(?:package\s+)?(?:uuid|UUID|[\w.]*\.uuid(?:\.[\w.*]+)?)\s*;?\s*\n?", "", repaired, flags=re.IGNORECASE)
    repaired = re.sub(r"(?m)^\s*import\s+java\.util\.UUID\s*;?\s*\n?", "", repaired)
    repaired = repaired.replace("UUID.randomUUID()", "java.util.UUID.randomUUID()")
    repaired = re.sub(r"\bUUID\.fromString\s*\(", "string2Uuid(", repaired)
    repaired = re.sub(r"\bUUID\s+([A-Za-z_]\w*)\s*=", r"def \1 =", repaired)
    if repaired and not repaired.lstrip().startswith("// #importFile NONE"):
        repaired = "// #importFile NONE\n" + repaired.lstrip()
    return repaired


def _ensure_referenced_forms(forms: list[FormModel], nodes: list[BpmnNode]) -> list[FormModel]:
    by_key = {form.key: form for form in forms}
    for node in nodes:
        if not node.form_key or node.form_key in by_key:
            continue
        by_key[node.form_key] = _placeholder_form(node.form_key, node.name or node.id)
    return list(by_key.values())


def _placeholder_form(form_key: str, task_name: str) -> FormModel:
    lowered = form_key.lower()
    if any(token in lowered for token in ("review", "approval", "decision", "steward")):
        return FormModel(
            key=form_key,
            name=f"{task_name} Form",
            fields=[
                FormField(
                    id="decision",
                    name="Decision",
                    type="enum",
                    required=True,
                    values=[{"id": "approve", "name": "Approve"}, {"id": "reject", "name": "Reject"}],
                ),
                FormField(id="comments", name="Comments", type="string"),
            ],
        )
    if "relation" in lowered:
        return FormModel(
            key=form_key,
            name=f"{task_name} Form",
            fields=[
                FormField(id="sourceAssetId", name="Source asset UUID", type="string", required=True),
                FormField(id="targetAssetId", name="Target asset UUID", type="string", required=True),
                FormField(id="relationTypeId", name="Relation type UUID", type="string", required=True),
            ],
        )
    if "validation" in lowered or "validate" in lowered:
        return FormModel(
            key=form_key,
            name=f"{task_name} Form",
            fields=[
                FormField(id="validationResult", name="Validation result", type="boolean", required=True),
                FormField(id="validationNotes", name="Validation notes", type="string"),
            ],
        )
    return FormModel(
        key=form_key,
        name=f"{task_name} Form",
        fields=[
            FormField(id="assetId", name="Asset UUID", type="string", required=True),
            FormField(id="comments", name="Comments", type="string"),
        ],
    )


def _normalize_expression(value: Any) -> str:
    expression = str(value or "").strip()
    if not expression:
        return ""
    if expression.startswith("${") and expression.endswith("}"):
        return expression
    if expression.lower() in {"true", "false"}:
        return "${" + expression.lower() + "}"
    if any(operator in expression for operator in ("==", "!=", ">=", "<=", ">", "<", "&&", "||")):
        return "${" + expression + "}"
    return expression


def _lane_for_node(node: dict[str, Any], lanes: list[str]) -> str:
    lane = str(node.get("lane") or "").strip()
    if lane in lanes:
        return lane
    node_type = str(node.get("type") or "").lower()
    node_name = str(node.get("name") or "").lower()
    if any(token in node_name for token in ("request", "submit", "rework")) and "Requester" in lanes:
        return "Requester"
    if "business" in node_name and "Business Owner" in lanes:
        return "Business Owner"
    if ("risk" in node_name or "compliance" in node_name) and "Risk and Compliance" in lanes:
        return "Risk and Compliance"
    if ("steward" in node_name or "review" in node_name) and "Data Steward" in lanes:
        return "Data Steward"
    if "callactivity" in node_type or "provision" in node_name:
        return "Provisioning Workflow" if "Provisioning Workflow" in lanes else lanes[-1]
    if any(token in node_type for token in ("script", "service", "send")):
        return "Collibra Automation" if "Collibra Automation" in lanes else lanes[-1]
    return lanes[0]


def _lane_y(lane: str, lanes: list[str]) -> int:
    index = lanes.index(lane) if lane in lanes else 0
    return 105 + index * 170


def _ensure_start_end_nodes(nodes: list[BpmnNode], lanes: list[str]) -> list[BpmnNode]:
    result = list(nodes)
    if not any(node.type == "startEvent" for node in result):
        result.insert(0, BpmnNode("start", "startEvent", "Start", lanes[0], x=120, y=_lane_y(lanes[0], lanes)))
    if not any(node.type == "endEvent" for node in result):
        result.append(
            BpmnNode(
                "end",
                "endEvent",
                "Completed",
                lanes[0],
                x=max([node.x for node in result] or [920]) + 220,
                y=_lane_y(lanes[0], lanes),
            )
        )
    return result


def _repair_linear_flow_continuity(nodes: list[BpmnNode], flows: list[SequenceFlow]) -> list[SequenceFlow]:
    node_ids = {node.id for node in nodes}
    repaired = [flow for flow in flows if flow.source_ref in node_ids and flow.target_ref in node_ids]
    if len(nodes) < 2:
        return repaired
    ordered_nodes = _ordered_executable_nodes(nodes)
    if len(ordered_nodes) < 2:
        return repaired
    flow_keys = {(flow.source_ref, flow.target_ref) for flow in repaired}

    if not repaired:
        for source, target in zip(ordered_nodes, ordered_nodes[1:]):
            _append_repair_flow(repaired, flow_keys, source.id, target.id)
        return repaired

    incoming = _incoming_counts(repaired)
    outgoing = _outgoing_counts(repaired)
    start = next((node for node in ordered_nodes if node.type == "startEvent"), ordered_nodes[0])
    end = next((node for node in reversed(ordered_nodes) if node.type == "endEvent"), ordered_nodes[-1])

    for index, node in enumerate(ordered_nodes):
        if node.type == "startEvent":
            continue
        if incoming.get(node.id, 0) > 0:
            continue
        source = _nearest_previous_with_outgoing_capacity(ordered_nodes, index, outgoing) or start
        if source.id != node.id:
            _append_repair_flow(repaired, flow_keys, source.id, node.id)
            outgoing[source.id] = outgoing.get(source.id, 0) + 1
            incoming[node.id] = incoming.get(node.id, 0) + 1

    for index, node in enumerate(ordered_nodes):
        if node.type == "endEvent":
            continue
        if outgoing.get(node.id, 0) > 0:
            continue
        target = _nearest_next_node(ordered_nodes, index) or end
        if target.id != node.id:
            _append_repair_flow(repaired, flow_keys, node.id, target.id)
            outgoing[node.id] = outgoing.get(node.id, 0) + 1
            incoming[target.id] = incoming.get(target.id, 0) + 1
    return repaired


def _ordered_executable_nodes(nodes: list[BpmnNode]) -> list[BpmnNode]:
    executable = [node for node in nodes if node.type not in {"textAnnotation", "boundaryEvent"}]
    return sorted(executable, key=lambda node: (0 if node.type == "startEvent" else 2 if node.type == "endEvent" else 1, node.x, node.y, node.id))


def _incoming_counts(flows: list[SequenceFlow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for flow in flows:
        counts[flow.target_ref] = counts.get(flow.target_ref, 0) + 1
    return counts


def _outgoing_counts(flows: list[SequenceFlow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for flow in flows:
        counts[flow.source_ref] = counts.get(flow.source_ref, 0) + 1
    return counts


def _nearest_previous_with_outgoing_capacity(nodes: list[BpmnNode], index: int, outgoing: dict[str, int]) -> BpmnNode | None:
    for candidate in reversed(nodes[:index]):
        if candidate.type != "endEvent" and outgoing.get(candidate.id, 0) > 0:
            return candidate
    for candidate in reversed(nodes[:index]):
        if candidate.type != "endEvent":
            return candidate
    return None


def _nearest_next_node(nodes: list[BpmnNode], index: int) -> BpmnNode | None:
    for candidate in nodes[index + 1 :]:
        if candidate.type != "startEvent":
            return candidate
    return None


def _append_repair_flow(repaired: list[SequenceFlow], flow_keys: set[tuple[str, str]], source_ref: str, target_ref: str) -> None:
    if source_ref == target_ref or (source_ref, target_ref) in flow_keys:
        return
    flow_keys.add((source_ref, target_ref))
    repaired.append(SequenceFlow(_safe_id(f"flow_{source_ref}_{target_ref}"), source_ref, target_ref, "Auto-connected"))


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


def _complex_prompt_profile(prompt: str) -> dict[str, str]:
    value = prompt.lower()
    focus = _prompt_focus_label(prompt)
    seed = _lower_camel(_safe_id(f"{_summarise_name(prompt)}CalledWorkflow"))
    themes = [
        (
            ("privacy", "pii", "personal data", "data protection", "gdpr"),
            "Privacy Assessment",
            "Privacy Assessment Workflow",
            "Call privacy assessment workflow",
            "Calls a separate workflow to assess privacy, PII, data protection controls and required remediation.",
            "Privacy assessment result",
            "Privacy remediation",
            "Privacy owner fixes assessment failures and retries the called workflow.",
            "Invoke privacy assessment",
            "Privacy assessment returned",
            "Privacy approved",
            "Privacy remediation required",
        ),
        (
            ("obsolete", "deletion", "delete", "retire", "archive"),
            "Asset Obsolescence",
            "Asset Obsolescence Workflow",
            "Call asset obsolescence workflow",
            "Calls a separate workflow to validate obsolete asset deletion, archive evidence and dependency cleanup.",
            "Deletion workflow result",
            "Deletion remediation",
            "Technical owner fixes deletion blockers and retries the called workflow.",
            "Invoke deletion workflow",
            "Deletion workflow returned",
            "Deletion complete",
            "Deletion remediation required",
        ),
        (
            ("quality", "data quality", "dq", "certification", "certify"),
            "Data Quality Certification",
            "Data Quality Workflow",
            "Call data quality certification workflow",
            "Calls a separate workflow to certify data quality controls, issue remediation and final governance evidence.",
            "Certification result",
            "Certification remediation",
            "Quality owner fixes certification blockers and retries the called workflow.",
            "Invoke certification workflow",
            "Certification returned",
            "Certification passed",
            "Certification remediation required",
        ),
        (
            ("relation", "responsibility", "ownership", "stewardship", "assignment"),
            "Stewardship Assignment",
            "Stewardship Workflow",
            "Call stewardship assignment workflow",
            "Calls a separate workflow to create relations, assign responsibilities and verify ownership standards.",
            "Stewardship workflow result",
            "Stewardship remediation",
            "Stewardship owner fixes relation or responsibility blockers and retries the called workflow.",
            "Invoke stewardship workflow",
            "Stewardship workflow returned",
            "Stewardship complete",
            "Stewardship remediation required",
        ),
        (
            ("risk", "security", "exception", "control", "compliance"),
            "Risk Control",
            "Risk Control Workflow",
            "Call risk control workflow",
            "Calls a separate workflow to validate risk controls, policy exceptions and compliance evidence.",
            "Risk control result",
            "Risk remediation",
            "Risk owner fixes control blockers and retries the called workflow.",
            "Invoke risk control workflow",
            "Risk control returned",
            "Risk control approved",
            "Risk remediation required",
        ),
        (
            ("provision", "access", "entitlement", "permission"),
            "Access Provisioning",
            "Provisioning Workflow",
            "Call downstream provisioning workflow",
            "Calls a separate Collibra/Flowable workflow to provision access after governance approval.",
            "Provisioning result",
            "Technical remediation",
            "Technical owner fixes failed provisioning and retries the called workflow.",
            "Invoke provisioning",
            "Provisioning returned",
            "Provisioned",
            "Provisioning failed",
        ),
    ]
    selected = themes[-1]
    for theme in themes:
        if any(token in value for token in theme[0]):
            selected = theme
            break
    suffix = _safe_id(selected[1])
    called_element = _lower_camel(_safe_id(f"{focus}{suffix}Workflow")) or seed
    return {
        "called_element": called_element,
        "called_lane": selected[2],
        "call_activity_name": selected[3],
        "call_activity_documentation": selected[4],
        "result_gateway_name": selected[5],
        "remediation_task_name": selected[6],
        "remediation_documentation": selected[7],
        "invoke_flow_name": selected[8],
        "returned_flow_name": selected[9],
        "success_flow_name": selected[10],
        "failure_flow_name": selected[11],
        "form_workflow_label": f"{selected[1]} workflow key",
        "form_status_label": f"{selected[1]} status",
    }


def _prompt_focus_label(prompt: str) -> str:
    stop_words = {
        "a",
        "an",
        "and",
        "as",
        "based",
        "build",
        "call",
        "collibra",
        "complex",
        "create",
        "for",
        "from",
        "governance",
        "governed",
        "in",
        "of",
        "process",
        "the",
        "to",
        "workflow",
        "with",
    }
    words = [word for word in re.findall(r"[A-Za-z0-9]+", prompt) if word.lower() not in stop_words]
    return "".join(word.capitalize() for word in words[:4]) or "Generated"


def _lower_camel(value: str) -> str:
    safe = _safe_id(value)
    return safe[:1].lower() + safe[1:] if safe else safe


def _design_satisfies_prompt(prompt: str, design: dict[str, Any]) -> bool:
    if not _requires_complex_prompt_design(prompt):
        return True
    nodes = [node for node in design.get("nodes", []) if isinstance(node, dict)]
    flows = [flow for flow in (design.get("flows") or design.get("sequence_flows") or design.get("sequenceFlows") or []) if isinstance(flow, dict)]
    forms = [form for form in design.get("forms", []) if isinstance(form, dict)]
    node_types = {_normalize_node_type(node.get("type")) for node in nodes}
    has_call_activity = "callActivity" in node_types
    has_reroute = any(
        any(token in str(flow.get(key, "")).lower() for token in ("rework", "reroute", "retry", "remediation"))
        for flow in flows
        for key in ("id", "name", "target_ref", "targetRef")
    )
    return len(nodes) >= 18 and len(flows) >= 20 and len(forms) >= 4 and has_call_activity and has_reroute


def _compile_failure_summaries(results: dict[str, CompileResult]) -> list[str]:
    failures: list[str] = []
    for element_id, result in results.items():
        if result.ok:
            continue
        if result.skipped:
            detail = result.stderr or "Groovy runtime unavailable; compile was skipped."
        else:
            detail = result.stderr or "; ".join(issue.message for issue in result.standards if issue.severity == "error") or "Compilation failed."
        failures.append(f"{element_id}: {detail.strip()}")
    return failures


def _complex_prompt_forms(process_id: str, profile: dict[str, str] | None = None) -> list[FormModel]:
    profile = profile or _complex_prompt_profile("")
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
                FormField("provisioningWorkflowKey", profile["form_workflow_label"], "string", True, default=profile["called_element"]),
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
            name=profile["remediation_task_name"],
            fields=[
                FormField("provisioningStatus", profile["form_status_label"], "string", True),
                FormField("provisioningError", f"{profile['form_status_label']} error", "string"),
                FormField("remediationAction", "Remediation action", "string", True),
            ],
        ),
    ]


def _complex_prompt_scripts() -> dict[str, str]:
    return {
        "validate_context": """// #importFile NONE

String requestId = (execution.getVariable("requestId") ?: java.util.UUID.randomUUID().toString()) as String
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
        "create_policy_exception": """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String requestId = execution.getVariable("requestId") as String
String controls = (execution.getVariable("securityControls") ?: "Controls must be confirmed before provisioning.") as String
def attributeTypeId = string2Uuid(execution.getVariable("policyExceptionAttributeTypeId") as String)
AddAttributeRequest request = AddAttributeRequest.builder()
    .assetId(string2Uuid(assetId))
    .typeId(attributeTypeId)
    .value("Policy exception for request " + requestId + ": " + controls)
    .build()
attributeApi.addAttribute(request)
execution.setVariable("policyExceptionCreated", true)
""",
        "create_relations": """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String consumerAssetId = (execution.getVariable("consumerAssetId") ?: "") as String
String requesterId = execution.getVariable("requesterIdNormalized") as String
def relationTypeId = string2Uuid(execution.getVariable("consumerRelationTypeId") as String)
def consumerRoleId = string2Uuid(execution.getVariable("consumerRoleId") as String)
if (consumerAssetId.trim()) {
    relationApi.addRelation(AddRelationRequest.builder()
        .sourceId(string2Uuid(assetId))
        .targetId(string2Uuid(consumerAssetId.trim()))
        .typeId(relationTypeId)
        .build())
}
responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
    .resourceId(string2Uuid(assetId))
    .roleId(consumerRoleId)
    .ownerId(string2Uuid(requesterId))
    .build())
execution.setVariable("relationAndResponsibilityCreated", true)
""",
        "update_access_status": """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

String assetId = execution.getVariable("assetIdNormalized") as String
def approvedStatusId = string2Uuid(execution.getVariable("approvedStatusId") as String)
assetApi.changeAsset(ChangeAssetRequest.builder()
    .id(string2Uuid(assetId))
    .statusId(approvedStatusId)
    .build())
execution.setVariable("assetStatusUpdated", true)
execution.setVariable("finalDecision", "approved")
""",
        "notify_success": """// #importFile NONE

String requestId = execution.getVariable("requestId") as String
String recipient = (execution.getVariable("requesterEmail") ?: execution.getVariable("requesterIdNormalized") ?: "requester") as String
execution.setVariable("notificationRecipient", recipient)
execution.setVariable("notificationSubject", "Collibra governed access request " + requestId + " approved and provisioned")
execution.setVariable("notificationQueued", true)
""",
        "notify_rejection": """// #importFile NONE

String requestId = execution.getVariable("requestId") as String
String reason = (execution.getVariable("stewardNotes") ?: execution.getVariable("businessNotes") ?: "Request rejected or withdrawn.") as String
execution.setVariable("finalDecision", "rejected")
execution.setVariable("notificationSubject", "Collibra governed access request " + requestId + " rejected")
execution.setVariable("notificationBody", reason)
execution.setVariable("notificationQueued", true)
""",
    }
