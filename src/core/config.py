from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _deep_get(data: dict[str, Any], path: str, default: Any) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        return _minimal_yaml(text)
    loaded = yaml.safe_load(text)
    return loaded or {}


def _minimal_yaml(text: str) -> dict[str, Any]:
    """Small fallback for the shipped config shape when PyYAML is unavailable."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            if isinstance(parent, list):
                parent.append(_coerce_scalar(line[2:].strip()))
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value:
            if isinstance(parent, dict):
                parent[key] = _coerce_scalar(value)
            continue
        container: dict[str, Any] | list[Any] = {}
        if isinstance(parent, dict):
            parent[key] = container
            stack.append((indent, container))
    return root


def _coerce_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(value)
    except ValueError:
        return value


@dataclass(frozen=True)
class ModelConfig:
    chat_model: str = "gpt-5-4-2026"
    embedding_model: str = "text-embedding-3-large"
    temperature: float = 0.1
    max_output_tokens: int = 8192
    request_timeout_seconds: int = 90


@dataclass(frozen=True)
class PathConfig:
    docs_dir: Path = PROJECT_ROOT / "docs" / "rag_training"
    jars_dir: Path = PROJECT_ROOT / "jars"
    output_dir: Path = PROJECT_ROOT / "output"
    vector_store: Path = PROJECT_ROOT / "output" / "vector_store.sqlite3"
    research_notes: Path = PROJECT_ROOT / "docs" / "collibra_workflow_research.md"


@dataclass(frozen=True)
class RuntimeConfig:
    max_workers: int = 10
    ingestion_batch_size: int = 24
    chunk_size: int = 1400
    chunk_overlap: int = 220
    relation_sample_rows: int = 100
    use_multiprocessing: bool = True
    use_multithreading: bool = True
    docs_scrape_max_pages: int = 80
    docs_scrape_verify_ssl: bool = True


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str = ""
    organization: str = ""
    project: str = ""
    base_url: str = ""


@dataclass(frozen=True)
class GroovyConfig:
    executable: str = "groovy"
    compile_timeout_seconds: int = 20
    default_classpath: list[str] = field(default_factory=lambda: ["./jars/*"])


@dataclass(frozen=True)
class CollibraConfig:
    java_api_docs_url: str = "https://developer.collibra.com/apis/java/javav2/allpackages-index.html"
    workflow_docs_seed_urls: list[str] = field(default_factory=list)
    uuid_columns: list[str] = field(default_factory=list)
    role_columns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QualityConfig:
    require_bpmn_start_and_end: bool = True
    require_script_imports: bool = True
    reject_generic_groovy_imports: bool = True
    max_self_heal_iterations: int = 5


@dataclass(frozen=True)
class AppConfig:
    name: str = "DSC Collibra Workflow Automation Agent"
    environment: str = "local"
    host: str = "127.0.0.1"
    port: int = 8088


@dataclass(frozen=True)
class Settings:
    app: AppConfig
    models: ModelConfig
    openai: OpenAIConfig
    paths: PathConfig
    runtime: RuntimeConfig
    groovy: GroovyConfig
    collibra: CollibraConfig
    quality: QualityConfig


def resolve_path(value: str | Path, base: Path = PROJECT_ROOT) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def load_settings(config_path: str | Path | None = None) -> Settings:
    path = resolve_path(config_path or PROJECT_ROOT / "config.yaml")
    data = _load_yaml(path)

    app = AppConfig(
        name=_deep_get(data, "app.name", AppConfig.name),
        environment=_deep_get(data, "app.environment", AppConfig.environment),
        host=_deep_get(data, "app.host", AppConfig.host),
        port=int(_deep_get(data, "app.port", AppConfig.port)),
    )
    models = ModelConfig(
        chat_model=_deep_get(data, "models.chat_model", ModelConfig.chat_model),
        embedding_model=_deep_get(data, "models.embedding_model", ModelConfig.embedding_model),
        temperature=float(_deep_get(data, "models.temperature", ModelConfig.temperature)),
        max_output_tokens=int(_deep_get(data, "models.max_output_tokens", ModelConfig.max_output_tokens)),
        request_timeout_seconds=int(
            _deep_get(data, "models.request_timeout_seconds", ModelConfig.request_timeout_seconds)
        ),
    )
    paths = PathConfig(
        docs_dir=resolve_path(_deep_get(data, "paths.docs_dir", "./docs/rag_training")),
        jars_dir=resolve_path(_deep_get(data, "paths.jars_dir", "./jars")),
        output_dir=resolve_path(_deep_get(data, "paths.output_dir", "./output")),
        vector_store=resolve_path(_deep_get(data, "paths.vector_store", "./output/vector_store.sqlite3")),
        research_notes=resolve_path(
            _deep_get(data, "paths.research_notes", "./docs/collibra_workflow_research.md")
        ),
    )
    runtime = RuntimeConfig(
        max_workers=int(_deep_get(data, "runtime.max_workers", RuntimeConfig.max_workers)),
        ingestion_batch_size=int(_deep_get(data, "runtime.ingestion_batch_size", RuntimeConfig.ingestion_batch_size)),
        chunk_size=int(_deep_get(data, "runtime.chunk_size", RuntimeConfig.chunk_size)),
        chunk_overlap=int(_deep_get(data, "runtime.chunk_overlap", RuntimeConfig.chunk_overlap)),
        relation_sample_rows=int(_deep_get(data, "runtime.relation_sample_rows", RuntimeConfig.relation_sample_rows)),
        use_multiprocessing=bool(_deep_get(data, "runtime.use_multiprocessing", RuntimeConfig.use_multiprocessing)),
        use_multithreading=bool(_deep_get(data, "runtime.use_multithreading", RuntimeConfig.use_multithreading)),
        docs_scrape_max_pages=int(_deep_get(data, "runtime.docs_scrape_max_pages", RuntimeConfig.docs_scrape_max_pages)),
        docs_scrape_verify_ssl=bool(
            _deep_get(data, "runtime.docs_scrape_verify_ssl", RuntimeConfig.docs_scrape_verify_ssl)
        ),
    )
    openai = OpenAIConfig(
        api_key=_deep_get(data, "openai.api_key", OpenAIConfig.api_key),
        organization=_deep_get(data, "openai.organization", OpenAIConfig.organization),
        project=_deep_get(data, "openai.project", OpenAIConfig.project),
        base_url=_deep_get(data, "openai.base_url", OpenAIConfig.base_url),
    )
    groovy = GroovyConfig(
        executable=_deep_get(data, "groovy.executable", GroovyConfig.executable),
        compile_timeout_seconds=int(
            _deep_get(data, "groovy.compile_timeout_seconds", GroovyConfig.compile_timeout_seconds)
        ),
        default_classpath=list(_deep_get(data, "groovy.default_classpath", ["./jars/*"])),
    )
    organization = _deep_get(data, "collibra.organization", {})
    collibra = CollibraConfig(
        java_api_docs_url=_deep_get(data, "collibra.java_api_docs_url", CollibraConfig.java_api_docs_url),
        workflow_docs_seed_urls=list(_deep_get(data, "collibra.workflow_docs_seed_urls", [])),
        uuid_columns=list(organization.get("uuid_columns", [])) if isinstance(organization, dict) else [],
        role_columns=list(organization.get("role_columns", [])) if isinstance(organization, dict) else [],
    )
    quality = QualityConfig(
        require_bpmn_start_and_end=bool(
            _deep_get(data, "quality.require_bpmn_start_and_end", QualityConfig.require_bpmn_start_and_end)
        ),
        require_script_imports=bool(_deep_get(data, "quality.require_script_imports", QualityConfig.require_script_imports)),
        reject_generic_groovy_imports=bool(
            _deep_get(data, "quality.reject_generic_groovy_imports", QualityConfig.reject_generic_groovy_imports)
        ),
        max_self_heal_iterations=int(
            _deep_get(data, "quality.max_self_heal_iterations", QualityConfig.max_self_heal_iterations)
        ),
    )
    for folder in (paths.docs_dir, paths.jars_dir, paths.output_dir):
        folder.mkdir(parents=True, exist_ok=True)
    return Settings(
        app=app,
        models=models,
        openai=openai,
        paths=paths,
        runtime=runtime,
        groovy=groovy,
        collibra=collibra,
        quality=quality,
    )


settings = load_settings()
