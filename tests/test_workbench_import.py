from __future__ import annotations

import io
import json
import zipfile

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
