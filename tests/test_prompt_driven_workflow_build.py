from pathlib import Path

from fastapi.testclient import TestClient

from src.api.server import app


PROMPT = """
Create a production Collibra governed access workflow from this prompt alone.
The workflow must contain multiple forms, conditional approval flows, requester rework reroutes,
steward triage, business owner approval, risk/compliance review, policy exception creation,
Groovy script tasks that use Collibra Java API v2 imports, and a BPMN call activity that invokes
a downstream provisioning workflow. Include technical remediation when the called workflow fails.
"""


def test_prompt_driven_complex_workflow_builds_imports_and_tests() -> None:
    client = TestClient(app)

    build_response = client.post(
        "/api/workflows/build",
        json={"master_prompt": PROMPT, "output_name": "pytest_prompt_driven_complex_workflow"},
    )
    assert build_response.status_code == 200
    built = build_response.json()

    nodes = built["process"]["nodes"]
    flows = built["process"]["flows"]
    assert len(nodes) >= 20
    assert len(flows) >= 25
    assert len(built["forms"]) >= 5
    assert any(node["type"] == "callActivity" for node in nodes)
    assert any(node["type"] == "scriptTask" for node in nodes)
    assert any(flow.get("condition") for flow in flows)
    assert built["validation_errors"] == []

    zip_path = Path(built["zip_path"])
    with zip_path.open("rb") as package:
        import_response = client.post(
            "/api/workflow/import",
            files={"file": (zip_path.name, package, "application/zip")},
        )
    assert import_response.status_code == 200
    imported = import_response.json()
    diagnostics = imported["appModel"]["importDiagnostics"]
    assert diagnostics["scriptTasks"] >= 5
    assert diagnostics["embeddedScripts"] >= 5
    assert diagnostics["missingForms"] == []
    assert len(imported["forms"]) >= 5

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
            "businessUseCase": PROMPT,
            "userTestCases": """
Scenario: Standard approval and provisioning
Expected: The call activity is reached and the workflow reaches the approved end.

Scenario: Provisioning failure reroute
Expected: The workflow routes to technical remediation and retries the called workflow.
""",
        },
    )
    assert case_response.status_code == 200
    cases = case_response.json()
    assert cases["ok"] is True
    assert cases["summary"]["failedCases"] == 0
