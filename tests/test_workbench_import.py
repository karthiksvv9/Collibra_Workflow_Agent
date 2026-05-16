from __future__ import annotations

import io
import json
import zipfile

from fastapi.testclient import TestClient

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
