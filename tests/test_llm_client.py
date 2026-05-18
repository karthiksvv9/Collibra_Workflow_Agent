from pathlib import Path

from src.agents.llm_client import request_json_design
from src.core.config import load_settings


def test_custom_chat_completion_uses_configured_gateway(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
models:
  chat_model: "gpt-5-4-2026-03-05"
  embedding_provider: "hashing"
openai:
  provider: "custom_chat_completions"
  api_key_env: "AI_GATEWAY_API_KEY"
  api_key_header: "X-API-Key"
  api_key_prefix: ""
  base_url: "https://iapi-test.proj.com/gpt/v2"
  chat_completions_path: "/gpt-5-4-2026-03-05/chat/completions"
  embedding_enabled: false
paths:
  docs_dir: "{(tmp_path / "docs").as_posix()}"
  jars_dir: "{(tmp_path / "jars").as_posix()}"
  output_dir: "{(tmp_path / "output").as_posix()}"
  vector_store: "{(tmp_path / "output" / "vectors.sqlite3").as_posix()}"
""",
        encoding="utf-8",
    )
    settings = load_settings(config_path)
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "unit-test-secret")
    captured = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"process_id":"sample","nodes":[],"flows":[],"forms":[]}'
                        }
                    }
                ]
            }

    def fake_post(url, headers, json, timeout):
        captured.update({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("src.agents.llm_client.requests.post", fake_post)

    design = request_json_design(settings, "Return JSON only")

    assert design == {"process_id": "sample", "nodes": [], "flows": [], "forms": []}
    assert captured["url"] == "https://iapi-test.proj.com/gpt/v2/gpt-5-4-2026-03-05/chat/completions"
    assert captured["headers"]["X-API-Key"] == "unit-test-secret"
    assert captured["json"]["model"] == "gpt-5-4-2026-03-05"
    assert captured["json"]["messages"][0]["content"] == "Return JSON only"
