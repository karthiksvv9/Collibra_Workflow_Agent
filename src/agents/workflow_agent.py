from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
        api_key = self.config.openai.api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            from openai import OpenAI

            kwargs = {"timeout": self.config.models.request_timeout_seconds, "api_key": api_key}
            if self.config.openai.organization:
                kwargs["organization"] = self.config.openai.organization
            if self.config.openai.project:
                kwargs["project"] = self.config.openai.project
            if self.config.openai.base_url:
                kwargs["base_url"] = self.config.openai.base_url
            client = OpenAI(**kwargs)
            prompt = build_design_prompt(master_prompt, context)
            response = client.responses.create(
                model=self.config.models.chat_model,
                input=prompt,
                temperature=self.config.models.temperature,
                max_output_tokens=self.config.models.max_output_tokens,
            )
            text = response.output_text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None
            return json.loads(match.group(0))
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
