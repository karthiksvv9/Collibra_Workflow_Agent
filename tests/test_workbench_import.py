from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from src.agents.workflow_agent import CollibraWorkflowAgent
from src.api.server import app


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
    assert payload["zipPath"].endswith("_autonomous_package.zip")


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
    assert "flatExport.bpmn" in names
    assert "flatExport.app" in names
    assert "approvalForm.form" in names
    assert "approveScript.groovy" in names


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
    assert payload["path"].endswith("_workbench_documentation.md")
    assert payload["htmlPath"].endswith("_workbench_documentation.html")
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
