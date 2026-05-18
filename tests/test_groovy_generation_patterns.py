from src.agents.groovy_compiler import CompileResult
from src.agents.workflow_agent import APPLY_METADATA_SCRIPT, VALIDATE_SCRIPT, _compile_failure_summaries, _complex_prompt_scripts
from src.api.server import _compat_groovy, _looks_like_collibra_groovy_snippet


def test_deterministic_workflow_templates_use_ootb_uuid_conversion() -> None:
    scripts = [VALIDATE_SCRIPT, APPLY_METADATA_SCRIPT, *_complex_prompt_scripts().values()]

    for script in scripts:
        assert "UUID.fromString" not in script
        assert "import java.util.UUID" not in script
        assert script.lstrip().startswith("// #importFile NONE")


def test_compat_generation_never_imports_uuid_package_for_generic_blocks() -> None:
    groovy = _compat_groovy(
        {"id": "task_CheckAccess", "type": "scriptTask", "name": "Check access"},
        "Generate code that validates an asset UUID and relation UUID",
        "",
    )

    assert groovy.lstrip().startswith("// #importFile NONE")
    assert "UUID.fromString" not in groovy
    assert "import java.util.UUID" not in groovy
    assert "import uuid" not in groovy.lower()


def test_compat_generation_uses_string2uuid_for_collibra_relations() -> None:
    groovy = _compat_groovy(
        {"id": "task_CreateRelation", "type": "scriptTask", "name": "Create relation"},
        "Create relation between source and target assets",
        "",
    )

    assert "AddRelationRequest" in groovy
    assert "string2Uuid" in groovy
    assert "UUID.fromString" not in groovy
    assert "import java.util.UUID" not in groovy


def test_ai_snippet_filter_rejects_java_uuid_style_output() -> None:
    assert not _looks_like_collibra_groovy_snippet(
        "import java.util.UUID\nUUID assetId = UUID.fromString(execution.getVariable('assetId') as String)"
    )
    assert not _looks_like_collibra_groovy_snippet(
        "public class GeneratedTask { public static void main(String[] args) {} }"
    )
    assert not _looks_like_collibra_groovy_snippet(
        "import com.collibra.dgc.core.api.uuid.UUID\nexecution.setVariable('x', true)"
    )


def test_agent_build_failure_summary_marks_skipped_compile_as_blocking() -> None:
    failures = _compile_failure_summaries(
        {
            "task_Script": CompileResult(
                ok=False,
                skipped=True,
                stderr="Groovy executable not found; syntax compilation skipped.",
            )
        }
    )

    assert failures
    assert "task_Script" in failures[0]
    assert "skipped" in failures[0]
