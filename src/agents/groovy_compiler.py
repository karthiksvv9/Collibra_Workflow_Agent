from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from src.agents.standards import CollibraGroovyStandards, StandardsIssue
from src.core.config import GroovyConfig, PROJECT_ROOT, settings


@dataclass(slots=True)
class CompileResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""
    command: list[str] = field(default_factory=list)
    standards: list[StandardsIssue] = field(default_factory=list)
    skipped: bool = False


class GroovyCompiler:
    def __init__(self, config: GroovyConfig | None = None) -> None:
        self.config = config or settings.groovy
        self.standards = CollibraGroovyStandards()

    def compile_script(self, script: str, classpath: list[str] | None = None) -> CompileResult:
        lint = self.standards.lint(script)
        if not lint.passed:
            return CompileResult(ok=False, standards=lint.issues)

        executable = shutil.which(self.config.executable)
        if executable is None:
            return CompileResult(
                ok=lint.passed,
                stderr="Groovy executable not found; syntax compilation skipped after static standards lint.",
                standards=lint.issues,
                skipped=True,
            )

        cp = self._classpath(classpath or self.config.default_classpath)
        with tempfile.TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "candidate.groovy"
            script_path.write_text(script, encoding="utf-8")
            command = [
                executable,
                "-cp",
                cp,
                "-e",
                "new GroovyShell(this.class.classLoader).parse(new File(args[0])); println('OK')",
                str(script_path),
            ]
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.config.compile_timeout_seconds,
                check=False,
            )
        return CompileResult(
            ok=completed.returncode == 0 and lint.passed,
            stdout=completed.stdout,
            stderr=completed.stderr,
            command=command,
            standards=lint.issues,
        )

    def _classpath(self, entries: list[str]) -> str:
        resolved: list[str] = []
        for entry in entries:
            path = Path(entry)
            if not path.is_absolute():
                path = PROJECT_ROOT / path
            resolved.append(str(path))
        return ";".join(resolved)

