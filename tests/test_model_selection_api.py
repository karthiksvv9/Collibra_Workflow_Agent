from fastapi.testclient import TestClient

from src.agents.llm_client import LLMRequestError
from src.api import server as api_server


def test_model_selection_rejects_unknown_model_id() -> None:
    client = TestClient(api_server.app)

    response = client.post("/api/models/select", json={"modelId": "not-a-configured-model"})

    assert response.status_code == 400
    assert "Unknown model profile" in response.text


def test_model_selection_validates_provider_before_switching(monkeypatch) -> None:
    client = TestClient(api_server.app)
    previous_model_id = api_server.active_model_id

    def failing_completion(*args, **kwargs):
        raise LLMRequestError("Provider HTTP 401: invalid_api_key for sk-test-secret")

    monkeypatch.setattr(api_server, "request_text_completion", failing_completion)

    response = client.post("/api/models/select", json={"modelId": "claude-opus-4-6"})

    assert response.status_code == 400
    assert "failed API validation" in response.text
    assert "sk-test-secret" not in response.text
    assert "sk-***" in response.text
    assert api_server.active_model_id == previous_model_id


def test_design_force_ai_requires_selected_model_success(monkeypatch) -> None:
    client = TestClient(api_server.app)
    captured = {}

    def failing_build(master_prompt, output_name=None, model_id=None, require_ai=False):
        captured["model_id"] = model_id
        captured["require_ai"] = require_ai
        raise ValueError("AI workflow design did not return a valid JSON BPMN design.")

    monkeypatch.setattr(api_server.agent, "build", failing_build)

    response = client.post(
        "/api/agent/design",
        json={"prompt": "Create a Collibra approval workflow.", "modelId": "claude-opus-4-6", "forceAi": True},
    )

    assert response.status_code == 400
    assert captured == {"model_id": "claude-opus-4-6", "require_ai": True}


def test_design_prefer_ai_can_keep_fallback_behavior(monkeypatch) -> None:
    client = TestClient(api_server.app)
    captured = {}

    def failing_build(master_prompt, output_name=None, model_id=None, require_ai=False):
        captured["model_id"] = model_id
        captured["require_ai"] = require_ai
        raise ValueError("fallback test stops after require flag capture")

    monkeypatch.setattr(api_server.agent, "build", failing_build)

    response = client.post(
        "/api/agent/design",
        json={
            "prompt": "Create a Collibra approval workflow.",
            "modelId": "claude-opus-4-6",
            "forceAi": True,
            "preferAi": True,
        },
    )

    assert response.status_code == 400
    assert captured == {"model_id": "claude-opus-4-6", "require_ai": False}
