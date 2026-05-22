from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from fastapi.testclient import TestClient

from src.agents.workflow_agent import CollibraWorkflowAgent
from src.api.server import app
from src.workflow.bpmn import BpmnModel, BpmnNode, SequenceFlow


def test_workbench_import_extracts_collibra_scripts_forms_and_properties() -> None:
    client = TestClient(app)
    package = _sample_collibra_zip()

    response = client.post(
        "/api/workflow/import",
        files={"file": ("sampleCollibraApp.zip", package, "application/zip")},
    )

    assert response.status_code == 200
    payload = response.json()
    app_model = payload["appModel"]

    assert payload["chosenBpmn"] == "sampleWorkflow.bpmn"
    assert "approveScript" in app_model["scripts"]
    assert "execution.setVariable('approved', true)" in app_model["scripts"]["approveScript"]["groovy"]
    assert "approvalForm" in payload["forms"]
    assert payload["forms"]["approvalForm"]["fields"][0]["id"] == "approvalDecision"
    assert app_model["elementProperties"]["reviewTask"]["formKey"] == "approvalForm"
    assert app_model["importDiagnostics"]["embeddedScripts"] == 1

    test_response = client.post(
        "/api/workflow/test-package",
        json={"bpmnXml": payload["bpmnXml"], "appModel": app_model, "forms": payload["forms"]},
    )
    assert test_response.status_code == 200
    assert test_response.json()["ok"] is True


def test_autonomous_agent_canvas_mode_exports_imported_workflow() -> None:
    client = TestClient(app)
    package = _sample_collibra_zip()

    import_response = client.post(
        "/api/workflow/import",
        files={"file": ("sampleCollibraApp.zip", package, "application/zip")},
    )
    assert import_response.status_code == 200
    imported = import_response.json()

    response = client.post(
        "/api/agent/autonomous-run",
        json={
            "mode": "canvas",
            "prompt": "Production-check this imported Collibra workflow and preserve its form and script task.",
            "bpmnXml": imported["bpmnXml"],
            "appModel": imported["appModel"],
            "forms": imported["forms"],
            "userTestCases": "Scenario: imported sample workflow\nExpected: package quality and generated business tests pass.",
            "packageName": "pytest_autonomous_imported_sample",
            "maxIterations": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["quality"]["summary"]["blockingIssues"] == 0
    assert payload["cases"]["summary"]["failedCases"] == 0
    assert "_with_timestamp_" not in Path(payload["zipPath"]).name
    assert re.search(r"_\d{8}_\d{6}\.zip$", Path(payload["zipPath"]).name)
    assert len(Path(payload["zipPath"]).name) <= 70
    with zipfile.ZipFile(payload["zipPath"]) as package:
        names = package.namelist()
    assert sum(name.lower().endswith(".app") for name in names) == 1
    assert not any(name.lower().endswith((".json", ".groovy", ".md")) for name in names)


def test_autonomous_prompt_mode_falls_back_when_forced_ai_key_is_missing(monkeypatch) -> None:
    for key in ("OPENAI_API_KEY", "AI_GATEWAY_API_KEY", "CLAUDE_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    client = TestClient(app)

    response = client.post(
        "/api/agent/autonomous-run",
        json={
            "mode": "prompt",
            "prompt": (
                "Create a production Collibra governed access workflow with requester intake, steward triage, "
                "business approval, risk review, rework reroutes, call activity to downstream provisioning workflow, "
                "API failure remediation, documentation and test evidence."
            ),
            "userTestCases": "Scenario: Happy path\nExpected: Workflow exports without blocking issues.",
            "forceAi": True,
            "packageName": "pytest_autonomous_prompt_fallback",
            "maxIterations": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["status"] == "passed"
    assert payload["quality"]["summary"]["blockingIssues"] == 0
    assert payload["cases"]["summary"]["failedCases"] == 0
    assert any(item["step"] == "ai_design_preference" for item in payload["trace"])
    with zipfile.ZipFile(payload["zipPath"]) as package:
        names = package.namelist()
    assert sum(name.lower().endswith(".app") for name in names) == 1


def test_import_rejects_unsafe_zip_member_paths() -> None:
    client = TestClient(app)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("../escape.bpmn", "<definitions />")
    buffer.seek(0)

    response = client.post(
        "/api/workflow/import",
        files={"file": ("unsafe.zip", buffer.getvalue(), "application/zip")},
    )

    assert response.status_code == 400
    assert "Unsafe ZIP member path" in response.text


def test_workbench_export_is_flat_ootb_style_zip() -> None:
    client = TestClient(app)
    imported = client.post(
        "/api/workflow/import",
        files={"file": ("sampleCollibraApp.zip", _sample_collibra_zip(), "application/zip")},
    ).json()

    response = client.post(
        "/api/workflow/export",
        json={
            "bpmnXml": imported["bpmnXml"],
            "appModel": imported["appModel"],
            "forms": imported["forms"],
            "packageName": "flatExport.zip",
        },
    )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        names = package.namelist()
    assert all("/" not in name and "\\" not in name for name in names)
    assert sum(name.lower().endswith(".app") for name in names) == 1
    assert "flatExport.bpmn" in names
    assert "flatExport.app" in names
    assert "form-approvalForm.form" in names
    assert not any(name.lower().endswith(".json") for name in names)
    assert not any(name.lower().endswith(".groovy") for name in names)
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        manifest = json.loads(package.read("flatExport.app").decode("utf-8"))
    assert manifest["key"] == "sampleApp"
    assert manifest["extension"]["design"]["childModels"] == [
        {"key": "approvalForm", "type": "form"},
        {"key": "sampleWorkflow", "type": "bpmn"},
    ]


def test_workbench_export_embeds_non_empty_script_and_removes_empty_conditions() -> None:
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" targetNamespace="http://www.collibra.com/test">
  <bpmn:process id="scriptExportWorkflow" isExecutable="true">
    <bpmn:startEvent id="start" />
    <bpmn:scriptTask id="scriptTaskA" name="Script A" scriptFormat="groovy"><bpmn:script /></bpmn:scriptTask>
    <bpmn:endEvent id="end" />
    <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="scriptTaskA" />
    <bpmn:sequenceFlow id="flow2" sourceRef="scriptTaskA" targetRef="end"><bpmn:conditionExpression xsi:type="tFormalExpression" /></bpmn:sequenceFlow>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="scriptExportWorkflow" /></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/export",
        json={
            "bpmnXml": bpmn,
            "appModel": {
                "scripts": {
                    "scriptTaskA": {
                        "groovy": "// #importFile NONE\nexecution.setVariable('scriptTaskACompleted', true)"
                    }
                },
                "elementProperties": {},
            },
            "forms": {},
            "packageName": "scriptExport.zip",
        },
    )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        exported_bpmn = package.read("scriptExport.bpmn").decode("utf-8")
    assert "<script />" not in exported_bpmn
    assert "scriptTaskACompleted" in exported_bpmn
    assert "autoStoreVariables=\"false\"" in exported_bpmn
    assert "conditionExpression" not in exported_bpmn


def test_workbench_export_namespaces_existing_condition_expression_for_bpmnjs() -> None:
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" targetNamespace="http://www.collibra.com/test">
  <bpmn:process id="conditionExportWorkflow" isExecutable="true">
    <bpmn:startEvent id="start" />
    <bpmn:exclusiveGateway id="gateway" />
    <bpmn:endEvent id="end" />
    <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="gateway" />
    <bpmn:sequenceFlow id="flow2" sourceRef="gateway" targetRef="end"><bpmn:conditionExpression xsi:type="tFormalExpression">${approved == true}</bpmn:conditionExpression></bpmn:sequenceFlow>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="conditionExportWorkflow" /></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/export",
        json={
            "bpmnXml": bpmn,
            "appModel": {"scripts": {}, "elementProperties": {}},
            "forms": {},
            "packageName": "conditionExport.zip",
        },
    )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        exported_bpmn = package.read("conditionExport.bpmn").decode("utf-8")
    assert 'xsi:type="bpmn:tFormalExpression"' in exported_bpmn
    assert 'xsi:type="tFormalExpression"' not in exported_bpmn


def test_bpmn_model_di_waypoints_dock_to_shape_boundaries() -> None:
    model = BpmnModel(
        process_id="dockedWorkflow",
        name="Docked Workflow",
        nodes=[
            BpmnNode(id="start", type="startEvent", name="Start", x=100, y=100),
            BpmnNode(id="review", type="userTask", name="Review", x=220, y=78),
            BpmnNode(id="end", type="endEvent", name="End", x=410, y=100),
        ],
        flows=[
            SequenceFlow(id="flow1", source_ref="start", target_ref="review"),
            SequenceFlow(id="flow2", source_ref="review", target_ref="end"),
        ],
    )

    root = ET.fromstring(model.to_xml().encode("utf-8"))

    assert _waypoints_for(root, "flow1") == [(136, 118), (220, 118)]
    assert _waypoints_for(root, "flow2") == [(348, 118), (410, 118)]


def test_workbench_export_repairs_stale_di_waypoints_from_uploaded_bpmn() -> None:
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" targetNamespace="http://www.collibra.com/test">
  <bpmn:process id="staleWaypointWorkflow" isExecutable="true">
    <bpmn:startEvent id="start" />
    <bpmn:userTask id="review" name="Review" />
    <bpmn:endEvent id="end" />
    <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="review" />
    <bpmn:sequenceFlow id="flow2" sourceRef="review" targetRef="end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="staleWaypointWorkflow">
    <bpmndi:BPMNShape id="start_di" bpmnElement="start"><dc:Bounds x="100" y="100" width="36" height="36" /></bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="review_di" bpmnElement="review"><dc:Bounds x="220" y="78" width="128" height="80" /></bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="end_di" bpmnElement="end"><dc:Bounds x="410" y="100" width="36" height="36" /></bpmndi:BPMNShape>
    <bpmndi:BPMNEdge id="flow1_di" bpmnElement="flow1"><di:waypoint x="200" y="140" /><di:waypoint x="210" y="160" /></bpmndi:BPMNEdge>
    <bpmndi:BPMNEdge id="flow2_di" bpmnElement="flow2"><di:waypoint x="390" y="90" /><di:waypoint x="395" y="92" /></bpmndi:BPMNEdge>
  </bpmndi:BPMNPlane></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/export",
        json={"bpmnXml": bpmn, "appModel": {"scripts": {}, "elementProperties": {}}, "forms": {}, "packageName": "dockedExport.zip"},
    )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        exported_root = ET.fromstring(package.read("dockedExport.bpmn"))

    assert _waypoints_for(exported_root, "flow1") == [(136, 118), (220, 118)]
    assert _waypoints_for(exported_root, "flow2") == [(348, 118), (410, 118)]


def test_workbench_export_uses_collibra_manifest_and_app_model_forms_when_forms_payload_is_empty() -> None:
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" targetNamespace="http://www.collibra.com/test">
  <bpmn:process id="generatedProcess" name="Generated Process" isExecutable="true">
    <bpmn:startEvent id="start" />
    <bpmn:userTask id="review" name="Review" />
    <bpmn:endEvent id="end" />
    <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="review" />
    <bpmn:sequenceFlow id="flow2" sourceRef="review" targetRef="end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="generatedProcess" /></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/export",
        json={
            "bpmnXml": bpmn,
            "appModel": {
                "metadata": {"name": "Generated Process"},
                "forms": {
                    "reviewForm": {
                        "key": "reviewForm",
                        "name": "Review Form",
                        "fields": [{"id": "decision", "label": "Decision", "type": "choice", "required": True, "default": None}],
                    }
                },
            },
            "forms": {},
            "packageName": "generatedProcess.zip",
        },
    )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        names = package.namelist()
        app_manifest = json.loads(package.read("generatedProcess.app").decode("utf-8"))
        form_json = package.read("form-reviewForm.form").decode("utf-8")

    assert not any(name.endswith(".dsc-sidecar.json") for name in names)
    assert not any(name.lower().endswith((".json", ".groovy", ".md")) for name in names)
    assert app_manifest["extension"]["design"]["childModels"] == [
        {"key": "reviewForm", "type": "form"},
        {"key": "generatedProcess", "type": "bpmn"},
    ]
    assert '"default": null' not in form_json
    assert '"value": ""' in form_json


def test_rag_chat_returns_business_fallback_instead_of_500() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/rag/chat",
        json={"question": "What is a Collibra script task and how should a business user think about it?", "limit": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["answer"], str)
    assert payload["answer"].strip()


def test_workbench_documentation_includes_imported_forms_and_writes_html() -> None:
    client = TestClient(app)
    imported = client.post(
        "/api/workflow/import",
        files={"file": ("sampleCollibraApp.zip", _sample_collibra_zip(), "application/zip")},
    ).json()

    response = client.post(
        "/api/workflow/documentation",
        json={
            "bpmnXml": imported["bpmnXml"],
            "appModel": imported["appModel"],
            "forms": imported["forms"],
            "prompt": "Document the imported approval workflow for Confluence.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "approvalForm" in payload["markdown"]
    assert payload["path"].endswith("_doc.md")
    assert payload["htmlPath"].endswith("_doc.html")
    assert "approvalForm" in Path(payload["path"]).read_text(encoding="utf-8")
    assert "<html>" in Path(payload["htmlPath"]).read_text(encoding="utf-8")


def test_prompt_design_accepts_form_field_label_payload() -> None:
    agent = CollibraWorkflowAgent.__new__(CollibraWorkflowAgent)
    package = agent._package_from_design(
        {
            "process_id": "labelFormWorkflow",
            "name": "Label Form Workflow",
            "lanes": ["Requester", "Collibra Automation", "Data Steward"],
            "nodes": [
                {"id": "start", "type": "startEvent", "name": "Start", "lane": "Requester", "formKey": "requestForm"},
                {"id": "script", "type": "scriptTask", "name": "Groovy", "lane": "Collibra Automation", "script": "execution.setVariable('ok', true)"},
                {"id": "end", "type": "endEvent", "name": "End", "lane": "Requester"},
            ],
            "flows": [
                {"id": "flow1", "sourceRef": "start", "targetRef": "script"},
                {"id": "flow2", "sourceRef": "script", "targetRef": "end"},
            ],
            "forms": [
                {
                    "key": "requestForm",
                    "name": "Request Form",
                    "fields": [{"id": "approvalDecision", "label": "Approval decision", "type": "dropdown", "required": True}],
                }
            ],
        }
    )

    assert package.forms[0].fields[0].name == "Approval decision"
    assert package.forms[0].fields[0].label == "Approval decision"
    assert package.process.pools
    assert package.validate() == []


def test_prompt_design_auto_connects_partially_orphaned_ai_nodes() -> None:
    agent = CollibraWorkflowAgent.__new__(CollibraWorkflowAgent)
    package = agent._package_from_design(
        {
            "process_id": "orphanRepairWorkflow",
            "name": "Orphan Repair Workflow",
            "lanes": ["Requester", "Data Steward", "Collibra Automation"],
            "nodes": [
                {"id": "start", "type": "startEvent", "name": "Start", "lane": "Requester", "x": 100, "y": 100},
                {"id": "review", "type": "userTask", "name": "Review", "lane": "Data Steward", "x": 300, "y": 270},
                {
                    "id": "orphanScript",
                    "type": "scriptTask",
                    "name": "AI forgot to connect this",
                    "lane": "Collibra Automation",
                    "script": "execution.setVariable('orphanHandled', true)",
                    "x": 500,
                    "y": 440,
                },
                {"id": "end", "type": "endEvent", "name": "End", "lane": "Requester", "x": 740, "y": 100},
            ],
            "flows": [
                {"id": "flow_start_review", "sourceRef": "start", "targetRef": "review"},
                {"id": "flow_review_end", "sourceRef": "review", "targetRef": "end"},
            ],
            "forms": [],
        }
    )

    flow_pairs = {(flow.source_ref, flow.target_ref) for flow in package.process.flows}
    assert ("review", "orphanScript") in flow_pairs
    assert ("orphanScript", "end") in flow_pairs
    assert package.validate() == []


def test_compile_endpoint_auto_repairs_uuid_style_using_org_standards() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/compile/groovy",
        json={
            "elementId": "task_NormalizeAsset",
            "element": {"id": "task_NormalizeAsset", "type": "scriptTask", "name": "Normalize asset UUID"},
            "prompt": "Repair this Collibra script using organization standards.",
            "autoRepair": True,
            "maxRepairIterations": 2,
            "appModel": {
                "scripts": {
                    "previousTask": {
                        "groovy": "// #importFile NONE\n"
                        "def previousAssetId = string2Uuid(execution.getVariable('assetId') as String)\n"
                        "execution.setVariable('previousAssetId', previousAssetId.toString())"
                    }
                }
            },
            "code": "import java.util.UUID\n"
            "UUID assetId = UUID.fromString(execution.getVariable('assetId') as String)\n"
            "execution.setVariable('assetIdNormalized', assetId.toString())",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["repaired"] is True
    assert "string2Uuid" in payload["groovy"]
    assert "UUID.fromString" not in payload["groovy"]
    assert "import java.util.UUID" not in payload["groovy"]
    assert payload["status"] in {"passed", "skipped"}
    assert payload["repairAttempts"]


def test_generate_code_returns_org_profile_plan_and_compile_result() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/agent/generate-code",
        json={
            "element": {"id": "task_CreateRelation", "type": "scriptTask", "name": "Create relation"},
            "prompt": "Create relation Groovy using source asset UUID, target asset UUID and relation type from RAG.",
            "compileAndRepair": True,
            "appModel": {
                "scripts": {
                    "existingRelation": {
                        "groovy": "// #importFile NONE\n"
                        "import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest\n"
                        "relationApi.addRelation(AddRelationRequest.builder().sourceId(string2Uuid(sourceAssetId)).targetId(string2Uuid(targetAssetId)).build())\n"
                        "execution.setVariable('relationCreated', true)"
                    }
                }
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "implementationPlan" in payload
    assert "Organization-aware Groovy profile" in payload["organizationProfile"]
    assert "string2Uuid" in payload["groovy"]
    assert "import java.util.UUID" not in payload["groovy"]
    assert payload["compileStatus"] in {"passed", "skipped"}


def test_workbench_export_can_timestamp_package_name() -> None:
    client = TestClient(app)
    imported = client.post(
        "/api/workflow/import",
        files={"file": ("sampleCollibraApp.zip", _sample_collibra_zip(), "application/zip")},
    ).json()

    response = client.post(
        "/api/workflow/export",
        json={
            "bpmnXml": imported["bpmnXml"],
            "appModel": imported["appModel"],
            "forms": imported["forms"],
            "packageName": "timestampedExport.zip",
            "withTimestamp": True,
        },
    )

    assert response.status_code == 200
    disposition = response.headers["content-disposition"]
    assert "with_timestamp" not in disposition
    assert re.search(r'timestampedExport_\d{8}_\d{6}\.zip', disposition)
    with zipfile.ZipFile(io.BytesIO(response.content)) as package:
        names = package.namelist()
    assert any(re.match(r"timestampedExport_\d{8}_\d{6}\.bpmn", name) for name in names)


def test_autocorrect_generates_sequence_flow_code_and_prompt_defined_call_activity() -> None:
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" targetNamespace="http://www.collibra.com/test">
  <bpmn:collaboration id="collab"><bpmn:participant id="pool" name="Collibra Workflow" processRef="callerRepairWorkflow" /></bpmn:collaboration>
  <bpmn:process id="callerRepairWorkflow" name="Caller Repair Workflow" isExecutable="true">
    <bpmn:laneSet id="lanes">
      <bpmn:lane id="lane_requester" name="Requester"><bpmn:flowNodeRef>start</bpmn:flowNodeRef><bpmn:flowNodeRef>review</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="lane_system" name="Collibra Automation"><bpmn:flowNodeRef>script</bpmn:flowNodeRef><bpmn:flowNodeRef>callProvisioning</bpmn:flowNodeRef><bpmn:flowNodeRef>end</bpmn:flowNodeRef></bpmn:lane>
    </bpmn:laneSet>
    <bpmn:startEvent id="start" name="Start" />
    <bpmn:userTask id="review" name="Approval Review" />
    <bpmn:scriptTask id="script" name="Prepare payload" scriptFormat="groovy"><bpmn:script /></bpmn:scriptTask>
    <bpmn:exclusiveGateway id="route" name="Approved?" />
    <bpmn:callActivity id="callProvisioning" name="Call provisioning workflow" />
    <bpmn:endEvent id="end" name="Complete" />
    <bpmn:endEvent id="rejected" name="Rejected" />
    <bpmn:sequenceFlow id="flow_start_review" sourceRef="start" targetRef="review" />
    <bpmn:sequenceFlow id="flow_review_script" sourceRef="review" targetRef="script" />
    <bpmn:sequenceFlow id="flow_script_route" sourceRef="script" targetRef="route" />
    <bpmn:sequenceFlow id="flow_approved" name="Approved" sourceRef="route" targetRef="callProvisioning" />
    <bpmn:sequenceFlow id="flow_rejected" name="Rejected" sourceRef="route" targetRef="rejected" />
    <bpmn:sequenceFlow id="flow_call_end" sourceRef="callProvisioning" targetRef="end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="collab" /></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/autocorrect",
        json={
            "bpmnXml": bpmn,
            "appModel": {"metadata": {"name": "Caller Repair Workflow"}, "scripts": {}, "elementProperties": {}},
            "forms": {},
            "prompt": "Autocorrect and use FinanceApprovalWorkflow.zip as the caller activity source.",
            "packageName": "pytest_autocorrect_repair.zip",
            "maxIterations": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["metrics"]["passPercent"] == 100
    assert "_with_timestamp_" not in Path(payload["zipPath"]).name
    assert re.search(r"_\d{8}_\d{6}\.zip$", Path(payload["zipPath"]).name)
    assert len(Path(payload["zipPath"]).name) <= 70
    assert "transitionListenerGroovy" in payload["bpmnXml"]
    assert 'calledElement="FinanceApprovalWorkflow"' in payload["bpmnXml"]
    assert "listenerCode" in payload["appModel"]["elementProperties"]["flow_approved"]
    assert payload["appModel"]["elementProperties"]["callProvisioning"]["calledWorkflowSource"] == "FinanceApprovalWorkflow.zip"
    assert "execution.setVariable" in payload["appModel"]["scripts"]["script"]["groovy"]
    with zipfile.ZipFile(payload["zipPath"]) as package:
        names = package.namelist()
        app_manifest = json.loads(package.read(next(name for name in names if name.endswith(".app"))).decode("utf-8"))
    assert sum(name.lower().endswith(".bpmn") for name in names) == 1
    assert {"key": "FinanceApprovalWorkflow", "type": "bpmn"} not in app_manifest["extension"]["design"]["childModels"]
    related = [Path(path) for path in payload["relatedPackagePaths"]]
    assert len(related) == 1
    assert related[0].exists()
    assert len(related[0].name) <= 90
    with zipfile.ZipFile(related[0]) as package:
        child_names = package.namelist()
        child_manifest = json.loads(package.read(next(name for name in child_names if name.endswith(".app"))).decode("utf-8"))
    assert "FinanceApprovalWorkflow.bpmn" in child_names
    assert child_manifest["extension"]["design"]["childModels"][-1] == {"key": "FinanceApprovalWorkflow", "type": "bpmn"}


def test_autocorrect_stitches_user_specified_ootb_subworkflow_zip() -> None:
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" targetNamespace="http://www.collibra.com/test">
  <bpmn:process id="parentWithOotbChild" name="Parent With OOTB Child" isExecutable="true">
    <bpmn:startEvent id="start" />
    <bpmn:callActivity id="voteSubprocess" name="Run voting subprocess" />
    <bpmn:endEvent id="end" />
    <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="voteSubprocess" />
    <bpmn:sequenceFlow id="flow2" sourceRef="voteSubprocess" targetRef="end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="parentWithOotbChild" /></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/autocorrect",
        json={
            "bpmnXml": bpmn,
            "appModel": {"metadata": {"name": "Parent With OOTB Child"}, "scripts": {}, "elementProperties": {}},
            "forms": {},
            "prompt": "Use VotingSubProcessApp.zip as the caller activity and stitch all required parameters.",
            "packageName": "pytest_ootb_stitch.zip",
            "maxIterations": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert 'calledElement="votingSubProcess"' in payload["bpmnXml"]
    props = payload["appModel"]["elementProperties"]["voteSubprocess"]
    assert props["calledWorkflowSource"] == "VotingSubProcessApp.zip"
    assert props["inputs"]
    assert props["outputs"]
    assert "votingSubProcess" in payload["appModel"]["calledWorkflows"]
    with zipfile.ZipFile(payload["zipPath"]) as package:
        names = package.namelist()
        app_manifest = json.loads(package.read(next(name for name in names if name.endswith(".app"))).decode("utf-8"))
    assert sum(name.lower().endswith(".bpmn") for name in names) == 1
    assert "votingSubProcess.bpmn" not in names
    assert {"key": "votingSubProcess", "type": "bpmn"} not in app_manifest["extension"]["design"]["childModels"]
    related = [Path(path) for path in payload["relatedPackagePaths"]]
    assert len(related) == 1
    assert related[0].exists()
    with zipfile.ZipFile(related[0]) as package:
        child_names = package.namelist()
        child_manifest = json.loads(package.read(next(name for name in child_names if name.endswith(".app"))).decode("utf-8"))
    assert "votingSubProcess.bpmn" in child_names
    assert any(name == "form-votingSubProcessVoteForm.form" for name in child_names)
    assert {"key": "votingSubProcess", "type": "bpmn"} in child_manifest["extension"]["design"]["childModels"]


def test_autocorrect_generates_requested_called_workflow_when_no_source_exists(monkeypatch) -> None:
    def fail_ai_design(*args, **kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr("src.api.server.agent.design_from_prompt", fail_ai_design)
    client = TestClient(app)
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" targetNamespace="http://www.collibra.com/test">
  <bpmn:process id="parentDynamicChild" name="Parent Dynamic Child" isExecutable="true">
    <bpmn:startEvent id="start" />
    <bpmn:userTask id="review" name="Review" />
    <bpmn:endEvent id="end" />
    <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="review" />
    <bpmn:sequenceFlow id="flow2" sourceRef="review" targetRef="end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="parentDynamicChild" /></bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    response = client.post(
        "/api/workflow/autocorrect",
        json={
            "bpmnXml": bpmn,
            "appModel": {"metadata": {"name": "Parent Dynamic Child"}, "scripts": {}, "elementProperties": {}},
            "forms": {},
            "prompt": "Generate called workflow named DynamicProvisioning for downstream provisioning approval and use it as a caller activity.",
            "packageName": "pytest_generated_child.zip",
            "maxIterations": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert 'calledElement="DynamicProvisioning"' in payload["bpmnXml"]
    assert payload["appModel"]["calledWorkflows"]["DynamicProvisioning"]["generated"] is True
    with zipfile.ZipFile(payload["zipPath"]) as package:
        names = package.namelist()
    assert sum(name.lower().endswith(".bpmn") for name in names) == 1
    assert "DynamicProvisioning.bpmn" not in names
    related = [Path(path) for path in payload["relatedPackagePaths"]]
    assert len(related) == 1
    assert related[0].exists()
    with zipfile.ZipFile(related[0]) as package:
        child_names = package.namelist()
    assert "DynamicProvisioning.bpmn" in child_names
    assert any(name.startswith("form-DynamicProvisioning") and name.endswith(".form") for name in child_names)


def _sample_collibra_zip() -> bytes:
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:flowable="http://flowable.org/bpmn" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:omgdc="http://www.omg.org/spec/DD/20100524/DC" targetNamespace="http://www.collibra.com/apiv2">
  <process id="sampleWorkflow" name="Sample Workflow" isExecutable="true">
    <startEvent id="start" name="Start" />
    <userTask id="reviewTask" name="Review" flowable:formKey="approvalForm" flowable:candidateGroups="role(steward)" />
    <scriptTask id="approveScript" name="Approve Script" scriptFormat="groovy" flowable:autoStoreVariables="false">
      <script><![CDATA[execution.setVariable('approved', true)]]></script>
    </scriptTask>
    <endEvent id="end" name="End" />
    <sequenceFlow id="flow1" sourceRef="start" targetRef="reviewTask" />
    <sequenceFlow id="flow2" sourceRef="reviewTask" targetRef="approveScript" />
    <sequenceFlow id="flow3" sourceRef="approveScript" targetRef="end" />
  </process>
  <bpmndi:BPMNDiagram id="diagram"><bpmndi:BPMNPlane id="plane" bpmnElement="sampleWorkflow">
    <bpmndi:BPMNShape id="start_di" bpmnElement="start"><omgdc:Bounds x="100" y="100" width="36" height="36" /></bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="reviewTask_di" bpmnElement="reviewTask"><omgdc:Bounds x="180" y="80" width="120" height="80" /></bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="approveScript_di" bpmnElement="approveScript"><omgdc:Bounds x="350" y="80" width="120" height="80" /></bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="end_di" bpmnElement="end"><omgdc:Bounds x="520" y="100" width="36" height="36" /></bpmndi:BPMNShape>
  </bpmndi:BPMNPlane></bpmndi:BPMNDiagram>
</definitions>"""
    form = {
        "rows": [
            {
                "cols": [
                    {
                        "id": "approvalDecision",
                        "label": "Approval decision",
                        "type": "dropdown",
                        "isRequired": True,
                        "visible": True,
                        "enabled": True,
                    }
                ]
            }
        ],
        "metadata": {"key": "approvalForm", "name": "Approval Form", "modelType": "form", "version": "1"},
    }
    app_json = {
        "key": "sampleApp",
        "name": "Sample App",
        "extension": {"design": {"childModels": [{"key": "approvalForm", "type": "form"}, {"key": "sampleWorkflow", "type": "bpmn"}]}},
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("sampleApp.app", json.dumps(app_json))
        package.writestr("form-approvalForm.form", json.dumps(form))
        package.writestr("sampleWorkflow.bpmn", bpmn)
    buffer.seek(0)
    return buffer.getvalue()


def _waypoints_for(root: ET.Element, flow_id: str) -> list[tuple[int, int]]:
    for edge in root.iter():
        if _local(edge.tag) != "BPMNEdge" or edge.attrib.get("bpmnElement") != flow_id:
            continue
        points: list[tuple[int, int]] = []
        for child in edge:
            if _local(child.tag) == "waypoint":
                points.append((int(float(child.attrib["x"])), int(float(child.attrib["y"]))))
        return points
    raise AssertionError(f"No BPMNEdge found for {flow_id}.")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag.split(":", 1)[-1]
