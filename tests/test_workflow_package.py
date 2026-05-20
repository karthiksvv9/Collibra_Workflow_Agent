from __future__ import annotations

import json
import zipfile
from pathlib import Path

from src.workflow.bpmn import BpmnModel, BpmnNode, SequenceFlow
from src.workflow.form import FormField, FormModel
from src.workflow.package import WorkflowPackage


def test_package_round_trip_zip(tmp_path: Path) -> None:
    form = FormModel("approvalForm", "Approval", [FormField(id="approvalDecision", name="Decision", type="string")])
    model = BpmnModel(
        process_id="approvalWorkflow",
        name="Approval Workflow",
        lanes=["Requester", "Steward"],
        nodes=[
            BpmnNode("start", "startEvent", "Start", "Requester"),
            BpmnNode("review", "userTask", "Review", "Steward", form_key="approvalForm"),
            BpmnNode("end", "endEvent", "End", "Requester"),
        ],
        flows=[
            SequenceFlow("flow1", "start", "review"),
            SequenceFlow("flow2", "review", "end"),
        ],
    )
    package = WorkflowPackage(model, [form], "Approval App")

    output = package.export_zip(tmp_path / "workflow.zip")
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        manifest = json.loads(archive.read("approvalWorkflow.app").decode("utf-8"))
    assert names == ["approvalWorkflow.bpmn", "form-approvalForm.form", "approvalWorkflow.app"]
    assert manifest["key"] == "approvalWorkflowApp"
    assert manifest["extension"]["design"]["childModels"] == [
        {"key": "approvalForm", "type": "form"},
        {"key": "approvalWorkflow", "type": "bpmn"},
    ]

    imported = WorkflowPackage.import_file(output)

    assert imported.app_name == "Approval App"
    assert imported.process.process_id == "approvalWorkflow"
    assert imported.forms[0].key == "approvalForm"
    assert imported.validate() == []
