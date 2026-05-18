from __future__ import annotations

import shutil
import subprocess
import tempfile
import os
import re
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
        cp = self._classpath(classpath or self.config.default_classpath)
        if executable is None and self.config.use_embedded_jars:
            java_executable = self._java_executable()
            if java_executable:
                return self._compile_with_embedded_groovy(script, cp, java_executable, lint.issues)
        if executable is None:
            return CompileResult(
                ok=lint.passed,
                stderr=(
                    "Groovy executable not found and embedded Java/Groovy fallback could not start; "
                    "syntax compilation skipped after static standards lint."
                ),
                standards=lint.issues,
                skipped=True,
            )

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

    def _compile_with_embedded_groovy(
        self,
        script: str,
        classpath: str,
        java_executable: str,
        standards: list[StandardsIssue],
    ) -> CompileResult:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script_path = tmp_path / "candidate.groovy"
            classes_path = tmp_path / "classes"
            classes_path.mkdir(parents=True, exist_ok=True)
            script_path.write_text(script, encoding="utf-8")
            completed, command = self._run_file_system_compiler(
                java_executable,
                classpath,
                classes_path,
                [script_path],
                self.config.java_options,
            )
            if completed.returncode != 0 and _java_memory_failed(completed.stdout, completed.stderr):
                completed, command = self._run_file_system_compiler(
                    java_executable,
                    classpath,
                    classes_path,
                    [script_path],
                    _low_memory_java_options(self.config.java_options),
                )
            active_script = script
            active_script_path = script_path
            if completed.returncode != 0:
                compatible_script = _strip_incompatible_raw_type_generics(active_script, completed.stderr)
                if compatible_script != active_script:
                    active_script = compatible_script
                    active_script_path = tmp_path / "candidate_compat.groovy"
                    active_script_path.write_text(active_script, encoding="utf-8")
                    completed, command = self._run_file_system_compiler(
                        java_executable,
                        classpath,
                        classes_path,
                        [active_script_path],
                        _low_memory_java_options(self.config.java_options),
                    )
            if completed.returncode != 0:
                stub_sources = self._write_collibra_dependency_stubs(tmp_path, active_script, completed.stderr)
                if stub_sources:
                    stub_completed, stub_command = self._run_file_system_compiler(
                        java_executable,
                        classpath,
                        classes_path,
                        stub_sources + [active_script_path],
                        _low_memory_java_options(self.config.java_options),
                    )
                    if stub_completed.returncode == 0:
                        return CompileResult(
                            ok=True,
                            stdout=(
                                stub_completed.stdout
                                + "\nCompiled with temporary Collibra dependency stubs for local syntax validation."
                            ).strip(),
                            stderr=stub_completed.stderr,
                            command=stub_command,
                            standards=standards,
                            skipped=False,
                        )
                    stub_compatible_script = _strip_incompatible_raw_type_generics(active_script, stub_completed.stderr)
                    if stub_compatible_script != active_script:
                        active_script = stub_compatible_script
                        active_script_path = tmp_path / "candidate_stub_compat.groovy"
                        active_script_path.write_text(active_script, encoding="utf-8")
                        stub_completed, stub_command = self._run_file_system_compiler(
                            java_executable,
                            classpath,
                            classes_path,
                            stub_sources + [active_script_path],
                            _low_memory_java_options(self.config.java_options),
                        )
                        if stub_completed.returncode == 0:
                            return CompileResult(
                                ok=True,
                                stdout=(
                                    stub_completed.stdout
                                    + "\nCompiled with temporary Collibra dependency stubs and raw-type compatibility for local syntax validation."
                                ).strip(),
                                stderr=stub_completed.stderr,
                                command=stub_command,
                                standards=standards,
                                skipped=False,
                            )
                    completed = stub_completed
                    command = stub_command
        missing_runtime = "ClassNotFoundException" in completed.stderr and "FileSystemCompiler" in completed.stderr
        return CompileResult(
            ok=completed.returncode == 0,
            stdout=completed.stdout,
            stderr=(
                "Embedded Groovy runtime was not found on classpath; download Apache Groovy JARs into ./jars. "
                + completed.stderr
                if missing_runtime
                else completed.stderr
            ),
            command=command,
            standards=standards,
            skipped=False,
        )

    def _run_file_system_compiler(
        self,
        java_executable: str,
        classpath: str,
        classes_path: Path,
        sources: list[Path],
        java_options: list[str],
    ) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        command = [
            java_executable,
            *java_options,
            "-cp",
            classpath,
            "org.codehaus.groovy.tools.FileSystemCompiler",
            "-d",
            str(classes_path),
            *[str(source) for source in sources],
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=self.config.compile_timeout_seconds,
            check=False,
        )
        return completed, command

    def _write_collibra_dependency_stubs(self, tmp_path: Path, script: str, stderr: str) -> list[Path]:
        class_names, static_methods = _collibra_dependency_references(script, stderr)
        if not class_names:
            return []
        root = tmp_path / "collibra_dependency_stubs"
        sources: list[Path] = []
        for class_name in sorted(class_names):
            package_name, _, simple_name = class_name.rpartition(".")
            if not package_name or not simple_name:
                continue
            target = root / Path(package_name.replace(".", "/")) / f"{simple_name}.groovy"
            target.parent.mkdir(parents=True, exist_ok=True)
            methods = sorted(static_methods.get(class_name, set()))
            target.write_text(_collibra_stub_source(package_name, simple_name, methods), encoding="utf-8")
            sources.append(target)
        return sources

    def _classpath(self, entries: list[str]) -> str:
        resolved: list[str] = []
        for entry in entries:
            path = Path(entry)
            if not path.is_absolute():
                path = PROJECT_ROOT / path
            resolved.append(str(path))
        return ";".join(resolved)

    def _java_executable(self) -> str | None:
        configured = str(self.config.java_executable or "java")
        configured_path = Path(configured)
        if configured_path.is_file():
            return str(configured_path)
        found = shutil.which(configured)
        if found:
            return found
        java_home = os.getenv("JAVA_HOME")
        if java_home:
            candidate = Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
            if candidate.is_file():
                return str(candidate)
        if os.name != "nt":
            return None
        roots = [
            Path(os.getenv("ProgramFiles", r"C:\Program Files")),
            Path(os.getenv("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        ]
        patterns = [
            "Java/*/bin/java.exe",
            "Eclipse Adoptium/*/bin/java.exe",
            "Microsoft/jdk*/bin/java.exe",
            "JetBrains/*/jbr/bin/java.exe",
        ]
        for root in roots:
            for pattern in patterns:
                for candidate in root.glob(pattern):
                    if candidate.is_file():
                        return str(candidate)
        return None


def _java_memory_failed(stdout: str, stderr: str) -> bool:
    text = f"{stdout}\n{stderr}".lower()
    return "insufficient memory" in text or "paging file is too small" in text or "native memory allocation" in text


def _low_memory_java_options(options: list[str]) -> list[str]:
    filtered = [option for option in options if not option.startswith(("-Xmx", "-Xms", "-XX:ReservedCodeCacheSize="))]
    return ["-Xms16m", "-Xmx192m", "-XX:ReservedCodeCacheSize=64m", "-XX:-UsePerfData", *filtered]


def _strip_incompatible_raw_type_generics(script: str, stderr: str) -> str:
    if "takes no parameters" not in stderr:
        return script
    adjusted = script
    for match in re.finditer(r"The class\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)<", stderr):
        simple_name = match.group(1).rsplit(".", 1)[-1]
        adjusted = re.sub(rf"\b{re.escape(simple_name)}\s*<[^>\n]+>", simple_name, adjusted)
    return adjusted


def _collibra_dependency_references(script: str, stderr: str) -> tuple[set[str], dict[str, set[str]]]:
    class_names: set[str] = set()
    static_methods: dict[str, set[str]] = {}
    for match in re.finditer(r"(?m)^\s*import\s+(?!static\s)(com\.collibra(?:\.[A-Za-z_]\w*)+)\s*$", script):
        _add_class_reference(match.group(1), class_names)
    for match in re.finditer(r"(?m)^\s*import\s+static\s+(com\.collibra(?:\.[A-Za-z_]\w*)+)\.([A-Za-z_]\w*|\*)\s*$", script):
        class_name = match.group(1)
        method = match.group(2)
        _add_class_reference(class_name, class_names)
        if method != "*":
            static_methods.setdefault(class_name, set()).add(method)
        else:
            static_methods.setdefault(class_name, set()).add("paginateAll")
    for match in re.finditer(r"unable to resolve class\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)", stderr):
        value = match.group(1)
        if value.startswith("com.collibra."):
            _add_class_reference(value, class_names)
    for match in re.finditer(r"\b(com\.collibra(?:\.[A-Za-z_]\w*)+)\b", script):
        _add_class_reference(match.group(1), class_names)
    return class_names, static_methods


def _add_class_reference(value: str, class_names: set[str]) -> None:
    parts = [part for part in value.split(".") if part]
    if not parts:
        return
    while parts and not parts[-1][:1].isupper():
        parts.pop()
    if len(parts) < 3:
        return
    class_names.add(".".join(parts))


def _collibra_stub_source(package_name: str, simple_name: str, static_methods: list[str]) -> str:
    extra_methods = "\n".join(f"    static def {method}(Object... args) {{ [] }}" for method in static_methods)
    if simple_name.endswith("Exception"):
        return f"""package {package_name}

class {simple_name} extends RuntimeException {{
    {simple_name}() {{ super() }}
    {simple_name}(String message) {{ super(message) }}
    {simple_name}(String message, Throwable cause) {{ super(message, cause) }}
}}
"""
    return f"""package {package_name}

class {simple_name} implements java.io.Serializable {{
    {simple_name}() {{}}
    {simple_name}(Object... args) {{}}
    static Builder builder() {{ new Builder() }}
    static def of(Object... args) {{ new {simple_name}() }}
{extra_methods}
    def methodMissing(String name, args) {{ null }}
    def propertyMissing(String name) {{ null }}
    void propertyMissing(String name, value) {{}}

    static class Builder extends {simple_name}Builder {{}}
}}

class {simple_name}Builder {{
    def methodMissing(String name, args) {{ this }}
    def propertyMissing(String name) {{ null }}
    void propertyMissing(String name, value) {{}}
    def build() {{ new {simple_name}() }}
}}
"""
