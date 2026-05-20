from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class GeneratedScenarioPackage:
    output_dir: Path
    zip_path: Path
    bpmn_path: Path
    app_path: Path
    forms: int
    scripts: int
    nodes: int
    flows: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "outputDir": str(self.output_dir),
            "zipPath": str(self.zip_path),
            "bpmnPath": str(self.bpmn_path),
            "appPath": str(self.app_path),
            "forms": self.forms,
            "scripts": self.scripts,
            "nodes": self.nodes,
            "flows": self.flows,
            "zipBytes": self.zip_path.stat().st_size if self.zip_path.exists() else 0,
        }


PROCESS_ID = "complexDataProductAccessGovernance"
PROCESS_NAME = "Complex Data Product Access Governance"
PACKAGE_NAME = "complex-data-product-access-governance-production.zip"


def generate_complex_data_product_access_package(root: str | Path | None = None) -> GeneratedScenarioPackage:
    project_root = Path(root or Path.cwd())
    output_dir = project_root / "output" / "complex-data-product-access-governance"
    forms_dir = output_dir / "forms"
    scripts_dir = output_dir / "scripts"
    docs_dir = output_dir / "docs"
    for directory in (output_dir, forms_dir, scripts_dir, docs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    scripts = _scripts()
    forms = _forms()
    nodes = _nodes(scripts)
    flows = _flows()
    lanes = _lanes()

    bpmn_xml = _build_bpmn_xml(nodes, flows, lanes)
    bpmn_path = output_dir / f"{PROCESS_ID}.bpmn"
    bpmn_path.write_text(bpmn_xml, encoding="utf-8")

    for key, form in forms.items():
        (forms_dir / f"{key}.form").write_text(json.dumps(form, indent=2, sort_keys=True), encoding="utf-8")
    for key, code in scripts.items():
        (scripts_dir / f"{key}.groovy").write_text(code.rstrip() + "\n", encoding="utf-8")

    sidecar_model = _app_model(generated_at, forms, scripts, nodes, flows)
    app_model = _collibra_app_model(forms)
    app_path = output_dir / f"{PROCESS_ID}.app"
    app_path.write_text(json.dumps(app_model, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / f"{PROCESS_ID}.dsc-sidecar.json").write_text(json.dumps(sidecar_model, indent=2, sort_keys=True), encoding="utf-8")

    (docs_dir / "scenario-overview.md").write_text(_scenario_overview(generated_at), encoding="utf-8")
    (docs_dir / "scenario-test-cases.md").write_text(_scenario_test_cases(), encoding="utf-8")

    zip_path = project_root / "output" / PACKAGE_NAME
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as package:
        package.write(bpmn_path, f"{PROCESS_ID}.bpmn")
        package.write(app_path, f"{PROCESS_ID}.app")
        for path in sorted(forms_dir.glob("*.form")):
            package.write(path, f"form-{path.name}")

    return GeneratedScenarioPackage(
        output_dir=output_dir,
        zip_path=zip_path,
        bpmn_path=bpmn_path,
        app_path=app_path,
        forms=len(forms),
        scripts=len(scripts),
        nodes=len(nodes),
        flows=len(flows),
    )


def _collibra_app_model(forms: dict[str, dict]) -> dict:
    return {
        "key": f"{PROCESS_ID}App",
        "name": f"{PROCESS_NAME}App",
        "description": "Generated Collibra workflow package.",
        "theme": "theme-1",
        "icon": "glyphicon-asterisk",
        "usersAccess": None,
        "groupsAccess": None,
        "flowApp": False,
        "url": None,
        "paletteDefinitionCategory": "core",
        "extension": {
            "design": {
                "childModels": [
                    *[{"key": key, "type": "form"} for key in forms],
                    {"key": PROCESS_ID, "type": "bpmn"},
                ]
            }
        },
    }


def _scripts() -> dict[str, str]:
    return {
        "task_ValidateRequestContext": """// #importFile NONE

String requestId = (execution.getVariable('requestId') ?: java.util.UUID.randomUUID().toString()) as String
String requester = (execution.getVariable('requesterId') ?: execution.getVariable('initiator') ?: 'unknown-requester') as String
String assetId = (execution.getVariable('assetId') ?: '') as String
String purpose = (execution.getVariable('businessPurpose') ?: '') as String
String riskRating = (execution.getVariable('riskRating') ?: 'standard') as String
Boolean complete = assetId.trim().length() > 0 && purpose.trim().length() > 15
execution.setVariable('requestId', requestId)
execution.setVariable('requesterId', requester)
execution.setVariable('riskRating', riskRating)
execution.setVariable('validationPassed', complete)
execution.setVariable('validationMessage', complete ? 'Request context is complete.' : 'Asset and business purpose are required before steward triage.')
""",
        "task_OpenPolicyException": """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest

String requestId = execution.getVariable('requestId') as String
String assetId = execution.getVariable('assetId') as String
String controls = (execution.getVariable('securityControls') ?: 'Compensating control review required') as String
def targetAssetId = string2Uuid(assetId)
AddAttributeRequest attributeRequest = AddAttributeRequest.builder()
    .assetId(targetAssetId)
    .typeId(string2Uuid(execution.getVariable('policyExceptionAttributeTypeId') as String))
    .value('Policy exception approved for request ' + requestId + ': ' + controls)
    .build()
attributeApi.addAttribute(attributeRequest)
execution.setVariable('policyExceptionCreated', true)
execution.setVariable('policyExceptionReference', requestId + '-EXCEPTION')
""",
        "task_CreateRelationAndResponsibility": """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

String assetId = execution.getVariable('assetId') as String
String consumerAssetId = execution.getVariable('consumerAssetId') as String
String requesterId = execution.getVariable('requesterId') as String
def relationTypeId = string2Uuid(execution.getVariable('consumerRelationTypeId') as String)
def roleId = string2Uuid(execution.getVariable('consumerRoleId') as String)
try {
    if (consumerAssetId?.trim()) {
        relationApi.addRelation(AddRelationRequest.builder()
            .sourceId(string2Uuid(assetId))
            .targetId(string2Uuid(consumerAssetId))
            .typeId(relationTypeId)
            .build())
    }
    responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
        .resourceId(string2Uuid(assetId))
        .roleId(roleId)
        .ownerId(string2Uuid(requesterId))
        .build())
    execution.setVariable('relationApiSucceeded', true)
    execution.setVariable('relationApiMessage', 'Relation and responsibility created.')
} catch (Exception ex) {
    execution.setVariable('relationApiSucceeded', false)
    execution.setVariable('relationApiMessage', ex.getMessage())
}
""",
        "task_UpdateAssetStatus": """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

String assetId = execution.getVariable('assetId') as String
String statusId = execution.getVariable('approvedStatusId') as String
ChangeAssetRequest request = ChangeAssetRequest.builder()
    .id(string2Uuid(assetId))
    .statusId(string2Uuid(statusId))
    .build()
assetApi.changeAsset(request)
execution.setVariable('assetStatusUpdated', true)
execution.setVariable('finalDecision', 'approved')
""",
        "task_RollbackAndNotify": """// #importFile NONE

String requestId = execution.getVariable('requestId') as String
String apiMessage = (execution.getVariable('relationApiMessage') ?: 'Unknown API error') as String
execution.setVariable('remediationRequired', true)
execution.setVariable('remediationSummary', 'Request ' + requestId + ' requires technical remediation: ' + apiMessage)
execution.setVariable('finalDecision', 'technical-remediation')
""",
        "task_NotifyCompletion": """// #importFile NONE

String requestId = execution.getVariable('requestId') as String
String finalDecision = (execution.getVariable('finalDecision') ?: 'approved') as String
String recipient = (execution.getVariable('requesterEmail') ?: execution.getVariable('requesterId') ?: 'requester') as String
execution.setVariable('notificationRecipient', recipient)
execution.setVariable('notificationSubject', 'Collibra data product access request ' + requestId + ' ' + finalDecision)
execution.setVariable('notificationQueued', true)
""",
        "task_NotifyRejection": """// #importFile NONE

String requestId = execution.getVariable('requestId') as String
String reason = (execution.getVariable('rejectionReason') ?: execution.getVariable('triageNotes') ?: execution.getVariable('approvalNotes') ?: 'Request rejected by governance review.') as String
execution.setVariable('finalDecision', 'rejected')
execution.setVariable('notificationSubject', 'Collibra data product access request ' + requestId + ' rejected')
execution.setVariable('notificationBody', reason)
execution.setVariable('notificationQueued', true)
""",
    }


def _forms() -> dict[str, dict[str, Any]]:
    return {
        "dataAccessRequestForm": _form(
            "Data Product Access Request",
            "Requester intake form for governed data product access.",
            [
                _field("requesterId", "Requester UUID", required=True),
                _field("requesterEmail", "Requester email", required=True),
                _field("assetId", "Data product asset UUID", required=True),
                _field("consumerAssetId", "Consuming application asset UUID"),
                _field("businessPurpose", "Business purpose", "multiLineText", True),
                _field("riskRating", "Risk rating", "dropdown", True, ["standard", "high", "restricted"]),
                _field("requestedAccessEndDate", "Access end date", "date", True),
                _field("acceptUsagePolicy", "Accept usage policy", "checkbox", True),
            ],
            "dataAccessRequestForm",
            ["Submit", "Save draft"],
        ),
        "reworkForm": _form(
            "Requester Rework",
            "Requester correction form for rerouted governance requests.",
            [
                _field("reworkSummary", "Rework summary", "multiLineText", True),
                _field("businessPurpose", "Updated business purpose", "multiLineText", True),
                _field("consumerAssetId", "Updated consumer asset UUID"),
            ],
            "reworkForm",
            ["Resubmit", "Withdraw"],
        ),
        "stewardTriageForm": _form(
            "Steward Triage",
            "Data steward routing and completeness decision.",
            [
                _field("triageDecision", "Triage decision", "dropdown", True, ["approve", "rework", "reject"]),
                _field("triageNotes", "Triage notes", "multiLineText", True),
                _field("riskRating", "Confirmed risk rating", "dropdown", True, ["standard", "high", "restricted"]),
            ],
            "stewardTriageForm",
            ["Route"],
        ),
        "businessApprovalForm": _form(
            "Business Owner Approval",
            "Business owner approval with reject and rework reroutes.",
            [
                _field("businessOwnerDecision", "Business owner decision", "dropdown", True, ["approve", "rework", "reject"]),
                _field("approvalNotes", "Approval notes", "multiLineText", True),
            ],
            "businessApprovalForm",
            ["Submit decision"],
        ),
        "securityReviewForm": _form(
            "Security and Privacy Review",
            "Security/privacy review for high-risk or restricted requests.",
            [
                _field("securityDecision", "Security decision", "dropdown", True, ["approve", "rework", "reject"]),
                _field("policyExceptionRequired", "Policy exception required", "checkbox"),
                _field("securityControls", "Required controls", "multiLineText", True),
            ],
            "securityReviewForm",
            ["Submit review"],
        ),
        "remediationForm": _form(
            "Technical Remediation",
            "Technical steward action form after Collibra API failure.",
            [
                _field("remediationAction", "Remediation action", "multiLineText", True),
                _field("relationApiMessage", "API message", "multiLineText"),
                _field("technicalRetryApproved", "Retry approved", "checkbox", True),
            ],
            "remediationForm",
            ["Retry automation", "Cancel"],
        ),
    }


def _field(
    field_id: str,
    label: str,
    field_type: str = "string",
    required: bool = False,
    values: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": field_id,
        "name": label,
        "label": label,
        "type": field_type,
        "required": required,
        "visible": True,
        "enabled": True,
        "writable": True,
        "readable": True,
    }
    if values:
        payload["values"] = [{"label": value.replace("-", " ").title(), "value": value} for value in values]
    return payload


def _form(
    name: str,
    description: str,
    fields: list[dict[str, Any]],
    key: str,
    outcomes: list[str],
) -> dict[str, Any]:
    return {
        "metadata": {
            "key": key,
            "name": name,
            "modelType": "form",
            "version": "1.0.0",
            "description": description,
        },
        "key": key,
        "name": name,
        "description": description,
        "fields": fields,
        "outcomes": [
            {"label": label, "value": label.lower().replace(" ", "_"), "primary": index == 0}
            for index, label in enumerate(outcomes)
        ],
    }


def _nodes(scripts: dict[str, str]) -> list[dict[str, Any]]:
    return [
        _node("start_Request", "startEvent", "Start request", "Lane_Requester", 190, 130, 36, 36, form_key="dataAccessRequestForm"),
        _node("task_RequestDataAccess", "userTask", "Submit data product access request", "Lane_Requester", 280, 108, 170, 80, form_key="dataAccessRequestForm", candidate_groups="Data Consumers"),
        _node("task_ValidateRequestContext", "scriptTask", "Validate request context", "Lane_Automation", 500, 748, 170, 80, script=scripts["task_ValidateRequestContext"]),
        _node("gw_RequestComplete", "exclusiveGateway", "Request complete?", "Lane_Automation", 720, 763, 50, 50, default="flow_IncompleteToRework"),
        _node("task_ReworkRequest", "userTask", "Requester rework", "Lane_Requester", 805, 108, 160, 80, form_key="reworkForm", candidate_groups="Data Consumers"),
        _node("task_StewardTriage", "userTask", "Steward triage and route", "Lane_Steward", 850, 258, 180, 80, form_key="stewardTriageForm", candidate_groups="Data Stewards"),
        _node("gw_TriageDecision", "exclusiveGateway", "Triage decision", "Lane_Steward", 1080, 273, 50, 50, default="flow_TriageToRework"),
        _node("gw_RiskRouting", "exclusiveGateway", "Risk routing", "Lane_Automation", 1185, 763, 50, 50, default="flow_RiskToBusiness"),
        _node("task_BusinessApproval", "userTask", "Business owner approval", "Lane_Business", 1310, 408, 180, 80, form_key="businessApprovalForm", candidate_groups="Business Owners"),
        _node("gw_BusinessDecision", "exclusiveGateway", "Business decision", "Lane_Business", 1535, 423, 50, 50, default="flow_BusinessToRework"),
        _node("task_SecurityReview", "userTask", "Security and privacy review", "Lane_Security", 1310, 558, 190, 80, form_key="securityReviewForm", candidate_groups="Privacy Owners,Security Owners"),
        _node("gw_SecurityDecision", "exclusiveGateway", "Security decision", "Lane_Security", 1535, 573, 50, 50, default="flow_SecurityToRework"),
        _node("gw_PolicyException", "exclusiveGateway", "Policy exception?", "Lane_Automation", 1640, 763, 50, 50, default="flow_NoPolicyException"),
        _node("task_OpenPolicyException", "scriptTask", "Open policy exception record", "Lane_Automation", 1745, 748, 190, 80, script=scripts["task_OpenPolicyException"]),
        _node("task_CreateRelationAndResponsibility", "scriptTask", "Create relation and responsibility", "Lane_Automation", 1985, 748, 210, 80, script=scripts["task_CreateRelationAndResponsibility"]),
        _node("gw_RelationApiOk", "exclusiveGateway", "API success?", "Lane_Automation", 2245, 763, 50, 50, default="flow_ApiFailure"),
        _node("task_UpdateAssetStatus", "scriptTask", "Update asset status", "Lane_Automation", 2350, 748, 170, 80, script=scripts["task_UpdateAssetStatus"]),
        _node("task_RollbackAndNotify", "scriptTask", "Record API failure and notify", "Lane_Automation", 2350, 858, 190, 80, script=scripts["task_RollbackAndNotify"]),
        _node("task_TechnicalRemediation", "userTask", "Technical remediation", "Lane_Technical", 1985, 918, 190, 80, form_key="remediationForm", candidate_groups="Technical Stewards"),
        _node("task_NotifyCompletion", "scriptTask", "Queue completion notification", "Lane_Automation", 2580, 748, 190, 80, script=scripts["task_NotifyCompletion"]),
        _node("task_NotifyRejection", "scriptTask", "Queue rejection notification", "Lane_Automation", 1310, 858, 190, 80, script=scripts["task_NotifyRejection"]),
        _node("end_Approved", "endEvent", "Approved and implemented", "Lane_Requester", 2820, 130, 36, 36),
        _node("end_Rejected", "endEvent", "Rejected", "Lane_Requester", 1545, 130, 36, 36),
    ]


def _node(
    node_id: str,
    tag: str,
    name: str,
    lane: str,
    x: int,
    y: int,
    width: int,
    height: int,
    **kwargs: Any,
) -> dict[str, Any]:
    return {"id": node_id, "tag": tag, "name": name, "lane": lane, "x": x, "y": y, "w": width, "h": height, **kwargs}


def _flows() -> list[tuple[str, str, str, str, str]]:
    return [
        ("flow_StartToRequest", "start_Request", "task_RequestDataAccess", "Start", ""),
        ("flow_RequestToValidate", "task_RequestDataAccess", "task_ValidateRequestContext", "Submit", ""),
        ("flow_ValidateToComplete", "task_ValidateRequestContext", "gw_RequestComplete", "Validated", ""),
        ("flow_CompleteToTriage", "gw_RequestComplete", "task_StewardTriage", "Complete", "${validationPassed == true}"),
        ("flow_IncompleteToRework", "gw_RequestComplete", "task_ReworkRequest", "Incomplete", "${validationPassed != true}"),
        ("flow_ReworkToValidate", "task_ReworkRequest", "task_ValidateRequestContext", "Resubmit", ""),
        ("flow_TriageToDecision", "task_StewardTriage", "gw_TriageDecision", "Triage submitted", ""),
        ("flow_TriageApproveToRisk", "gw_TriageDecision", "gw_RiskRouting", "Approve", "${triageDecision == 'approve'}"),
        ("flow_TriageToRework", "gw_TriageDecision", "task_ReworkRequest", "Rework", "${triageDecision == 'rework'}"),
        ("flow_TriageReject", "gw_TriageDecision", "task_NotifyRejection", "Reject", "${triageDecision == 'reject'}"),
        ("flow_RiskToBusiness", "gw_RiskRouting", "task_BusinessApproval", "Standard risk", "${riskRating == 'standard'}"),
        ("flow_RiskToSecurity", "gw_RiskRouting", "task_SecurityReview", "High or restricted risk", "${riskRating == 'high' || riskRating == 'restricted'}"),
        ("flow_BusinessToDecision", "task_BusinessApproval", "gw_BusinessDecision", "Decision", ""),
        ("flow_BusinessApprove", "gw_BusinessDecision", "gw_PolicyException", "Approve", "${businessOwnerDecision == 'approve'}"),
        ("flow_BusinessReject", "gw_BusinessDecision", "task_NotifyRejection", "Reject", "${businessOwnerDecision == 'reject'}"),
        ("flow_BusinessToRework", "gw_BusinessDecision", "task_ReworkRequest", "Rework", "${businessOwnerDecision == 'rework'}"),
        ("flow_SecurityToDecision", "task_SecurityReview", "gw_SecurityDecision", "Decision", ""),
        ("flow_SecurityApprove", "gw_SecurityDecision", "gw_PolicyException", "Approve", "${securityDecision == 'approve'}"),
        ("flow_SecurityReject", "gw_SecurityDecision", "task_NotifyRejection", "Reject", "${securityDecision == 'reject'}"),
        ("flow_SecurityToRework", "gw_SecurityDecision", "task_ReworkRequest", "Rework", "${securityDecision == 'rework'}"),
        ("flow_PolicyExceptionRequired", "gw_PolicyException", "task_OpenPolicyException", "Exception required", "${policyExceptionRequired == true}"),
        ("flow_NoPolicyException", "gw_PolicyException", "task_CreateRelationAndResponsibility", "No exception", "${policyExceptionRequired != true}"),
        ("flow_ExceptionToRelation", "task_OpenPolicyException", "task_CreateRelationAndResponsibility", "Record created", ""),
        ("flow_RelationToApiCheck", "task_CreateRelationAndResponsibility", "gw_RelationApiOk", "API result", ""),
        ("flow_ApiSuccess", "gw_RelationApiOk", "task_UpdateAssetStatus", "Success", "${relationApiSucceeded == true}"),
        ("flow_ApiFailure", "gw_RelationApiOk", "task_RollbackAndNotify", "Failure", "${relationApiSucceeded != true}"),
        ("flow_FailureToRemediation", "task_RollbackAndNotify", "task_TechnicalRemediation", "Remediate", ""),
        ("flow_RemediationToRelation", "task_TechnicalRemediation", "task_CreateRelationAndResponsibility", "Retry", ""),
        ("flow_StatusToNotify", "task_UpdateAssetStatus", "task_NotifyCompletion", "Status updated", ""),
        ("flow_NotifyToApprovedEnd", "task_NotifyCompletion", "end_Approved", "Done", ""),
        ("flow_RejectNotifyToEnd", "task_NotifyRejection", "end_Rejected", "Done", ""),
    ]


def _lanes() -> list[tuple[str, str, int, int, int, int]]:
    return [
        ("Lane_Requester", "Requester", 90, 95, 2860, 130),
        ("Lane_Steward", "Data Steward", 90, 225, 2860, 150),
        ("Lane_Business", "Business Owner", 90, 375, 2860, 150),
        ("Lane_Security", "Security & Privacy", 90, 525, 2860, 160),
        ("Lane_Automation", "Collibra Automation", 90, 685, 2860, 220),
        ("Lane_Technical", "Technical Steward", 90, 905, 2860, 150),
    ]


def _build_bpmn_xml(
    nodes: list[dict[str, Any]],
    flows: list[tuple[str, str, str, str, str]],
    lanes: list[tuple[str, str, int, int, int, int]],
) -> str:
    node_by_id = {node["id"]: node for node in nodes}
    incoming = {node["id"]: [] for node in nodes}
    outgoing = {node["id"]: [] for node in nodes}
    for flow_id, source, target, _, _ in flows:
        outgoing[source].append(flow_id)
        incoming[target].append(flow_id)

    lane_refs = {lane_id: [] for lane_id, *_ in lanes}
    for node in nodes:
        lane_refs[node["lane"]].append(node["id"])

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:flowable="http://flowable.org/bpmn" xmlns:dsc="https://dsc.local/collibra/workflows/designer" id="Definitions_ComplexDataProductAccess" targetNamespace="https://dsc.local/collibra/workflows/complex-data-product-access">',
        '  <bpmn:collaboration id="Collaboration_DataProductAccessGovernance">',
        f'    <bpmn:participant id="Pool_CollibraGovernance" name="Collibra Data Product Access Governance" processRef="{PROCESS_ID}" />',
        "  </bpmn:collaboration>",
        f'  <bpmn:process id="{PROCESS_ID}" name="{PROCESS_NAME}" isExecutable="true">',
        "    <bpmn:documentation>Complex governed data product access workflow with requester rework, steward triage, business approval, security/privacy review, policy exception creation, Collibra Java API automation, technical remediation loop, and completion/rejection notifications.</bpmn:documentation>",
        f'    <bpmn:laneSet id="{PROCESS_ID}_lanes">',
    ]
    for lane_id, lane_name, *_ in lanes:
        parts.append(f'      <bpmn:lane id="{lane_id}" name="{escape(lane_name)}">')
        for ref in lane_refs[lane_id]:
            parts.append(f"        <bpmn:flowNodeRef>{ref}</bpmn:flowNodeRef>")
        parts.append("      </bpmn:lane>")
    parts.append("    </bpmn:laneSet>")
    parts.extend(_node_xml(node, incoming[node["id"]], outgoing[node["id"]]) for node in nodes)
    parts.extend(_flow_xml(flow) for flow in flows)
    parts.append("  </bpmn:process>")
    parts.append(f'  <bpmndi:BPMNDiagram id="{PROCESS_ID}_diagram">')
    parts.append(f'    <bpmndi:BPMNPlane id="{PROCESS_ID}_plane" bpmnElement="Collaboration_DataProductAccessGovernance">')
    parts.append('      <bpmndi:BPMNShape id="Pool_CollibraGovernance_di" bpmnElement="Pool_CollibraGovernance" isHorizontal="true">')
    parts.append('        <dc:Bounds x="60" y="95" width="2890" height="960" />')
    parts.append("      </bpmndi:BPMNShape>")
    for lane_id, _, x, y, width, height in lanes:
        parts.append(f'      <bpmndi:BPMNShape id="{lane_id}_di" bpmnElement="{lane_id}" isHorizontal="true">')
        parts.append(f'        <dc:Bounds x="{x}" y="{y}" width="{width}" height="{height}" />')
        parts.append("      </bpmndi:BPMNShape>")
    for node in nodes:
        parts.append(f'      <bpmndi:BPMNShape id="{node["id"]}_di" bpmnElement="{node["id"]}">')
        parts.append(f'        <dc:Bounds x="{node["x"]}" y="{node["y"]}" width="{node["w"]}" height="{node["h"]}" />')
        parts.append("      </bpmndi:BPMNShape>")
    parts.extend(_edge_xml(flow, node_by_id) for flow in flows)
    parts.append("    </bpmndi:BPMNPlane>")
    parts.append("  </bpmndi:BPMNDiagram>")
    parts.append("</bpmn:definitions>")
    return "\n".join(parts) + "\n"


def _node_xml(node: dict[str, Any], incoming: list[str], outgoing: list[str]) -> str:
    attrs = {"id": node["id"], "name": node["name"]}
    if node.get("default"):
        attrs["default"] = node["default"]
    if node["tag"] == "scriptTask":
        attrs["scriptFormat"] = "groovy"
    if node.get("form_key") or node.get("formKey"):
        attrs["flowable:formKey"] = node.get("form_key") or node.get("formKey")
    if node.get("candidate_groups") or node.get("candidateGroups"):
        attrs["flowable:candidateGroups"] = node.get("candidate_groups") or node.get("candidateGroups")
    lines = [f'    <bpmn:{node["tag"]} {_attrs(attrs)}>']
    lines.append(f'      <bpmn:documentation>{escape("Lane: " + node["lane"] + "; generated by DSC Collibra Workflow Agent.")}</bpmn:documentation>')
    for flow_id in incoming:
        lines.append(f"      <bpmn:incoming>{flow_id}</bpmn:incoming>")
    for flow_id in outgoing:
        lines.append(f"      <bpmn:outgoing>{flow_id}</bpmn:outgoing>")
    if node["tag"] == "scriptTask":
        lines.append("      <bpmn:script><![CDATA[" + str(node.get("script", "")).rstrip() + "]]></bpmn:script>")
    lines.append(f'    </bpmn:{node["tag"]}>')
    return "\n".join(lines)


def _flow_xml(flow: tuple[str, str, str, str, str]) -> str:
    flow_id, source, target, name, condition = flow
    attrs = {"id": flow_id, "name": name, "sourceRef": source, "targetRef": target}
    lines = [f"    <bpmn:sequenceFlow {_attrs(attrs)}>"]
    if condition:
        lines.append('      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression"><![CDATA[' + condition + "]]></bpmn:conditionExpression>")
    lines.append("    </bpmn:sequenceFlow>")
    return "\n".join(lines)


def _edge_xml(flow: tuple[str, str, str, str, str], node_by_id: dict[str, dict[str, Any]]) -> str:
    flow_id, source, target, _, _ = flow
    source_node = node_by_id[source]
    target_node = node_by_id[target]
    x1, y1 = _center_right(source_node)
    x2, y2 = _center_left(target_node)
    points = [(x1, y1)]
    if x2 < x1:
        mid_y = max(y1, y2) + 70
        points.extend([(x1 + 45, y1), (x1 + 45, mid_y), (x2 - 45, mid_y), (x2 - 45, y2)])
    elif abs(y2 - y1) > 100:
        mid_x = (x1 + x2) // 2
        points.extend([(mid_x, y1), (mid_x, y2)])
    points.append((x2, y2))
    lines = [f'      <bpmndi:BPMNEdge id="{flow_id}_di" bpmnElement="{flow_id}">']
    for x, y in points:
        lines.append(f'        <di:waypoint x="{x}" y="{y}" />')
    lines.append("      </bpmndi:BPMNEdge>")
    return "\n".join(lines)


def _center_right(node: dict[str, Any]) -> tuple[int, int]:
    return int(node["x"] + node["w"]), int(node["y"] + node["h"] // 2)


def _center_left(node: dict[str, Any]) -> tuple[int, int]:
    return int(node["x"]), int(node["y"] + node["h"] // 2)


def _attrs(attrs: dict[str, Any]) -> str:
    return " ".join(f'{key}="{escape(str(value), quote=True)}"' for key, value in attrs.items() if value not in (None, ""))


def _app_model(
    generated_at: str,
    forms: dict[str, dict[str, Any]],
    scripts: dict[str, str],
    nodes: list[dict[str, Any]],
    flows: list[tuple[str, str, str, str, str]],
) -> dict[str, Any]:
    element_properties: dict[str, dict[str, Any]] = {}
    for node in nodes:
        props = {"id": node["id"], "name": node["name"], "type": f'bpmn:{node["tag"]}', "lane": node["lane"]}
        form_key = node.get("form_key") or node.get("formKey")
        if form_key:
            props["formKey"] = form_key
        candidate_groups = node.get("candidate_groups") or node.get("candidateGroups")
        if candidate_groups:
            props["candidateGroups"] = candidate_groups
        if node["tag"] == "scriptTask":
            props["scriptFormat"] = "groovy"
        element_properties[node["id"]] = props
    for flow_id, source, target, name, condition in flows:
        element_properties[flow_id] = {
            "id": flow_id,
            "name": name,
            "type": "bpmn:sequenceFlow",
            "sourceRef": source,
            "targetRef": target,
            "condition": condition,
            "flowType": "conditional" if condition else "normal",
        }
    return {
        "appName": PROCESS_NAME,
        "process": f"{PROCESS_ID}.bpmn",
        "generator": "DSC Collibra Workflow Automation Agent",
        "generatedAt": generated_at,
        "metadata": {
            "name": PROCESS_NAME,
            "format": "COLLIBRA_WORKFLOW_PACKAGE_WITH_DSC_SIDECAR",
            "version": "1.0.0",
            "description": "Generated production candidate package for a complex Collibra governed data product access use case.",
            "footer": "karthik.v",
        },
        "childModels": [
            {"type": "bpmn", "path": f"{PROCESS_ID}.bpmn"},
            *[{"type": "form", "key": key, "path": f"forms/{key}.form"} for key in forms],
            *[{"type": "groovy", "elementId": key, "path": f"scripts/{key}.groovy"} for key in scripts],
        ],
        "forms": forms,
        "scripts": {
            key: {
                "groovy": code,
                "elementId": key,
                "elementType": "bpmn:ScriptTask",
                "scriptFormat": "groovy",
                "source": f"scripts/{key}.groovy",
            }
            for key, code in scripts.items()
        },
        "elementProperties": element_properties,
        "uuidMappings": {
            "policyExceptionAttributeTypeId": "00000000-0000-0000-0000-000000000101",
            "consumerRelationTypeId": "00000000-0000-0000-0000-000000000102",
            "consumerRoleId": "00000000-0000-0000-0000-000000000103",
            "approvedStatusId": "00000000-0000-0000-0000-000000000104",
        },
        "validationRules": [
            "All script tasks must pass Collibra Groovy standards lint and Groovy shell compilation when configured.",
            "Every user task with a flowable:formKey must have a matching .form model.",
            "Every conditional reroute sequence flow must preserve its JUEL condition in BPMN XML.",
            "Exported package must re-import without losing BPMN, scripts, forms, or element properties.",
        ],
    }


def _scenario_overview(generated_at: str) -> str:
    return f"""# {PROCESS_NAME}

Generated: {generated_at}

This production-candidate scenario models a complex Collibra data product access workflow with multiple reroutes:

- requester intake and requester rework loop
- steward triage approve/rework/reject
- risk-based routing to business owner or security/privacy review
- business and security approval/rework/reject paths
- optional policy exception creation
- Collibra Java API relation/responsibility/status automation
- technical remediation loop when an API task fails
- completion and rejection notification tasks

Primary user-test scenarios are included in `scenario-test-cases.md`.
"""


def _scenario_test_cases() -> str:
    return """Scenario: Standard-risk happy path
Start with a complete dataAccessRequestForm, standard risk, steward approve, business owner approve, no policy exception, Collibra relation API succeeds.
Expected: Workflow reaches Approved and implemented, queues completion notification, and updates asset status.

Scenario: Requester rework path
Start with missing business purpose or invalid asset UUID so validationPassed is false.
Expected: Workflow reroutes to Requester rework, resubmits to validation, then continues to steward triage.

Scenario: High-risk policy exception path
Submit high risk request, steward approve, security approve with policyExceptionRequired true.
Expected: Workflow creates policy exception, then creates relation/responsibility, updates status, and completes.

Scenario: Business rejection path
Submit standard-risk request, steward approve, business owner reject.
Expected: Workflow queues rejection notification and reaches Rejected end event.

Scenario: Collibra API failure remediation path
Submit approved request but relation API throws an exception.
Expected: Workflow records API failure, routes to Technical remediation, retries relation/responsibility creation, then continues after success.
"""


if __name__ == "__main__":
    print(json.dumps(generate_complex_data_product_access_package().as_dict(), indent=2))
