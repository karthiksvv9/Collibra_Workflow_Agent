from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from src.workflow.bpmn import BpmnModel, parse_bpmn_file
from src.workflow.form import FormModel


@dataclass(slots=True)
class WorkflowPackage:
    process: BpmnModel
    forms: list[FormModel] = field(default_factory=list)
    app_name: str = "Generated Collibra Workflow"

    def validate(self) -> list[str]:
        errors = self.process.validate()
        for form in self.forms:
            errors.extend(form.validate())
        form_keys = {form.key for form in self.forms}
        for node in self.process.nodes:
            if node.form_key and node.form_key not in form_keys:
                errors.append(f"User task {node.id} references missing form {node.form_key}.")
        return errors

    def export_zip(self, output_path: str | Path) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "appName": self.app_name,
            "process": f"{self.process.process_id}.bpmn",
            "forms": [f"{form.key}.form" for form in self.forms],
            "generator": "DSC Collibra Workflow Automation Agent",
        }
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(manifest["process"], self.process.to_xml())
            for form in self.forms:
                archive.writestr(f"{form.key}.form", form.to_json())
            archive.writestr(f"{self.process.process_id}.app", json.dumps(manifest, indent=2, sort_keys=True))
        return output

    @classmethod
    def import_file(cls, path: str | Path) -> "WorkflowPackage":
        input_path = Path(path)
        if input_path.suffix.lower() == ".bpmn":
            return cls(process=parse_bpmn_file(input_path), forms=[], app_name=input_path.stem)
        if input_path.suffix.lower() != ".zip":
            raise ValueError("WorkflowPackage.import_file supports .bpmn and .zip files.")
        forms: list[FormModel] = []
        process: BpmnModel | None = None
        app_name = input_path.stem
        with zipfile.ZipFile(input_path) as archive:
            for name in archive.namelist():
                suffix = Path(name).suffix.lower()
                text = archive.read(name).decode("utf-8", errors="ignore")
                if suffix == ".bpmn":
                    process = BpmnModel.from_xml(text)
                elif suffix == ".form":
                    forms.append(FormModel.from_json(text))
                elif suffix == ".app":
                    try:
                        manifest = json.loads(text)
                        app_name = manifest.get("appName", app_name)
                    except json.JSONDecodeError:
                        pass
        if process is None:
            raise ValueError("No .bpmn process found in ZIP package.")
        return cls(process=process, forms=forms, app_name=app_name)

