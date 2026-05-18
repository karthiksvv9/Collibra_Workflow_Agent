from pathlib import Path

from fastapi.testclient import TestClient

from src.api.server import app
from src.workflow.scenario_generator import generate_complex_data_product_access_package


def test_complex_scenario_package_imports_and_passes_quality_loop(tmp_path: Path) -> None:
    generated = generate_complex_data_product_access_package(tmp_path)
    client = TestClient(app)

    with generated.zip_path.open("rb") as package:
        import_response = client.post(
            "/api/workflow/import",
            files={"file": (generated.zip_path.name, package, "application/zip")},
        )

    assert import_response.status_code == 200
    imported = import_response.json()
    diagnostics = imported["appModel"]["importDiagnostics"]
    assert diagnostics["scriptTasks"] == 7
    assert diagnostics["embeddedScripts"] == 7
    assert diagnostics["userTasks"] == 6
    assert diagnostics["sequenceFlows"] == 31
    assert diagnostics["missingForms"] == []
    assert len(imported["forms"]) == 6
    assert len(imported["appModel"]["scripts"]) == 7

    payload = {
        "bpmnXml": imported["bpmnXml"],
        "appModel": imported["appModel"],
        "forms": imported["forms"],
        "maxIterations": 4,
    }
    quality_response = client.post("/api/workflow/test-package", json=payload)
    assert quality_response.status_code == 200
    quality = quality_response.json()
    assert quality["ok"] is True
    assert quality["summary"]["blockingIssues"] == 0

    case_response = client.post(
        "/api/workflow/test-cases",
        json={
            **payload,
            "businessUseCase": (
                "Complex governed data product access workflow with requester rework, steward triage, "
                "business approval, security review, policy exception automation, and API remediation."
            ),
            "userTestCases": (generated.output_dir / "docs" / "scenario-test-cases.md").read_text(encoding="utf-8"),
        },
    )
    assert case_response.status_code == 200
    case_result = case_response.json()
    assert case_result["ok"] is True
    assert case_result["summary"]["failedCases"] == 0
