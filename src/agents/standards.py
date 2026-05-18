from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class StandardsIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass(slots=True)
class GroovyStandardsReport:
    issues: list[StandardsIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


class CollibraGroovyStandards:
    GENERIC_IMPORT_RE = re.compile(r"^\s*import\s+[\w.]+\.\*\s*;?\s*$", re.MULTILINE)
    IMPORT_RE = re.compile(r"^\s*import\s+([\w.]+)\s*;?\s*$", re.MULTILINE)
    INVALID_UUID_IMPORT_RE = re.compile(
        r"^\s*import\s+(?!java\.util\.UUID\b)(?:uuid|UUID|[\w.]*\.uuid(?:\.[\w.*]+)?)\s*;?\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    JAVA_CLASS_WRAPPER_RE = re.compile(r"^\s*(?:public\s+)?class\s+\w+\b|public\s+static\s+void\s+main\s*\(", re.MULTILINE)

    def lint(self, script: str) -> GroovyStandardsReport:
        issues: list[StandardsIssue] = []
        if self.JAVA_CLASS_WRAPPER_RE.search(script):
            issues.append(
                StandardsIssue(
                    "java_class_wrapper",
                    "Collibra script tasks must be Groovy snippets, not Java classes or public static main programs.",
                )
            )
        if self.INVALID_UUID_IMPORT_RE.search(script):
            issues.append(
                StandardsIssue(
                    "invalid_uuid_import",
                    "Collibra UUIDs are identifier values; do not import uuid packages. Use string2Uuid(...) when conversion is required.",
                )
            )
        if "com.collibra.dgc.core.api" in script:
            imports = self.IMPORT_RE.findall(script)
            if not imports:
                issues.append(StandardsIssue("missing_imports", "Collibra API classes are referenced without explicit imports."))
        if self.GENERIC_IMPORT_RE.search(script):
            issues.append(StandardsIssue("generic_import", "Use explicit imports instead of package wildcard imports."))
        script_without_java_uuid_import = re.sub(r"(?m)^\s*import\s+java\.util\.UUID\s*;?\s*$", "", script)
        if "import java.util.UUID" in script and not re.search(r"\b(UUID\.|UUID[ \t]+[A-Za-z_]\w*)", script_without_java_uuid_import):
            issues.append(
                StandardsIssue(
                    "unused_uuid_import",
                    "Avoid java.util.UUID imports unless the snippet actually declares UUID variables or calls UUID methods.",
                    "warning",
                )
            )
        if "execution.getVariable(" not in script and "execution.setVariable(" not in script:
            issues.append(
                StandardsIssue(
                    "no_process_variables",
                    "Script does not read or write workflow process variables; confirm this is intentional.",
                    "warning",
                )
            )
        if "println " in script or "System.out" in script:
            issues.append(StandardsIssue("stdout_logging", "Use Collibra workflow logging instead of stdout.", "warning"))
        return GroovyStandardsReport(issues)
