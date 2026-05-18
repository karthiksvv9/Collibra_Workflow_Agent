from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from src.core.config import Settings, settings


@dataclass(slots=True)
class OotbGroovyProfile:
    examples: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)

    def render_for_prompt(self, instruction: str, limit: int = 6000) -> str:
        snippets = select_ootb_snippets(instruction, self.examples, max_items=5)
        lines = [
            "Collibra OOTB Groovy style observed from indexed workflow ZIPs:",
            "- Scripts are Groovy snippets executed by Flowable/Collibra, not Java classes.",
            "- Most scripts start with `// #importFile NONE`.",
            "- Collibra UUIDs are data values. Use Collibra helpers such as `string2Uuid(variableOrText)` when converting UUID strings.",
            "- Do not import a generic UUID package or stamp `import java.util.UUID` into every block.",
            "- Use injected workflow services such as `assetApi`, `relationApi`, `responsibilityApi`, `userApi`, `mail`, `users`, `loggerApi`, `execution`, `item`, `domain` when relevant.",
            "- Import explicit Collibra DTO classes only when the script uses their builders.",
            "",
            "Relevant OOTB snippets:",
        ]
        for index, snippet in enumerate(snippets, start=1):
            lines.append(f"\nExample {index}:\n{snippet[:1200]}")
        rendered = "\n".join(lines)
        return rendered[:limit]


_PROFILE_CACHE: OotbGroovyProfile | None = None


def load_ootb_groovy_profile(config: Settings = settings) -> OotbGroovyProfile:
    global _PROFILE_CACHE
    if _PROFILE_CACHE is not None:
        return _PROFILE_CACHE
    examples: list[str] = []
    source_files: list[str] = []
    for folder in [config.paths.rag_ootb_workflows_dir, config.paths.docs_dir]:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".zip", ".bpmn", ".xml", ".groovy"}:
                continue
            for script in _scripts_from_path(path):
                clean = _clean_script(script)
                if clean and clean not in examples:
                    examples.append(clean)
                    source_files.append(str(path))
    imports = sorted({match.group(1) for script in examples for match in re.finditer(r"(?m)^\s*import\s+([\w.]+)\s*;?\s*$", script)})
    _PROFILE_CACHE = OotbGroovyProfile(examples=examples, imports=imports, source_files=source_files)
    return _PROFILE_CACHE


def select_ootb_snippets(instruction: str, examples: list[str], max_items: int = 4) -> list[str]:
    query = str(instruction or "").lower()
    weighted: list[tuple[int, str]] = []
    for script in examples:
        lower = script.lower()
        score = 0
        for token in _query_tokens(query):
            if token in lower:
                score += 3
        for keyword, terms in _TOPIC_TERMS.items():
            if keyword in query and any(term in lower for term in terms):
                score += 8
        if score:
            weighted.append((score, script))
    weighted.sort(key=lambda item: (-item[0], len(item[1])))
    selected = [script for _, script in weighted[:max_items]]
    if len(selected) < max_items:
        for script in examples:
            if script not in selected:
                selected.append(script)
            if len(selected) >= max_items:
                break
    return selected


def _scripts_from_path(path: Path) -> list[str]:
    if path.suffix.lower() == ".zip":
        scripts: list[str] = []
        try:
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if Path(name).suffix.lower() in {".bpmn", ".xml", ".groovy"}:
                        raw = archive.read(name).decode("utf-8", errors="ignore")
                        scripts.extend(_scripts_from_text(raw, Path(name).suffix.lower()))
        except zipfile.BadZipFile:
            return []
        return scripts
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return _scripts_from_text(raw, path.suffix.lower())


def _scripts_from_text(text: str, suffix: str) -> list[str]:
    if suffix == ".groovy":
        return [text]
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return re.findall(r"<(?:\w+:)?script[^>]*><!\[CDATA\[(.*?)\]\]></(?:\w+:)?script>", text, re.DOTALL)
    scripts: list[str] = []
    for node in root.iter():
        if _local(node.tag) == "script":
            value = "".join(node.itertext()).strip()
            if value:
                scripts.append(value)
    return scripts


def _clean_script(script: str) -> str:
    clean = str(script or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean


def _query_tokens(query: str) -> list[str]:
    return [token for token in re.findall(r"[a-z][a-z0-9_]{3,}", query.lower()) if token not in _STOP_WORDS]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag.split(":", 1)[-1]


_STOP_WORDS = {
    "collibra",
    "workflow",
    "groovy",
    "script",
    "task",
    "generate",
    "selected",
    "block",
    "with",
    "from",
    "this",
    "that",
}

_TOPIC_TERMS = {
    "mail": ["mail.sendmails", "users.getuserids"],
    "email": ["mail.sendmails", "users.getuserids"],
    "notify": ["mail.sendmails", "loggerapi.warn"],
    "notification": ["mail.sendmails", "loggerapi.warn"],
    "asset": ["assetapi", "changeassetrequest", "addassetrequest"],
    "status": ["changeassetrequest", "statusid"],
    "relation": ["relationapi", "addrelationrequest", "findrelationsrequest"],
    "responsibility": ["responsibilityapi", "addresponsibilityrequest", "findresponsibilitiesrequest"],
    "owner": ["responsibilityapi", "findusersrequest", "owner_role"],
    "issue": ["issueapi", "addissuerequest", "moveissuerequest"],
    "comment": ["commentapi", "addcommentrequest"],
    "approval": ["form_", "approved", "rejected", "decision"],
    "vote": ["voting", "voter", "earlycomplete"],
}
