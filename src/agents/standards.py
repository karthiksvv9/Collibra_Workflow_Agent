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

    def lint(self, script: str) -> GroovyStandardsReport:
        issues: list[StandardsIssue] = []
        if "com.collibra.dgc.core.api" in script:
            imports = self.IMPORT_RE.findall(script)
            if not imports:
                issues.append(StandardsIssue("missing_imports", "Collibra API classes are referenced without explicit imports."))
        if self.GENERIC_IMPORT_RE.search(script):
            issues.append(StandardsIssue("generic_import", "Use explicit imports instead of package wildcard imports."))
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
