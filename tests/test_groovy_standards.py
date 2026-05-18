from src.agents.standards import CollibraGroovyStandards


def test_lint_rejects_generic_imports() -> None:
    report = CollibraGroovyStandards().lint(
        "import com.collibra.dgc.core.api.dto.instance.asset.*\nexecution.getVariable('x')"
    )

    assert not report.passed
    assert any(issue.code == "generic_import" for issue in report.issues)


def test_lint_accepts_java_style_import_semicolon() -> None:
    report = CollibraGroovyStandards().lint(
        "import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest;\n"
        "execution.setVariable('x', ChangeAssetRequest)"
    )

    assert report.passed
    assert not any(issue.code == "missing_imports" for issue in report.issues)


def test_lint_rejects_fake_uuid_imports() -> None:
    report = CollibraGroovyStandards().lint(
        "import com.collibra.dgc.core.api.uuid.UUID\n"
        "execution.setVariable('assetId', '123')"
    )

    assert not report.passed
    assert any(issue.code == "invalid_uuid_import" for issue in report.issues)


def test_lint_rejects_java_class_wrappers_for_script_tasks() -> None:
    report = CollibraGroovyStandards().lint(
        "public class GeneratedTask {\n"
        "  public static void main(String[] args) { execution.setVariable('x', true) }\n"
        "}"
    )

    assert not report.passed
    assert any(issue.code == "java_class_wrapper" for issue in report.issues)


def test_lint_warns_on_unused_java_uuid_import() -> None:
    report = CollibraGroovyStandards().lint(
        "import java.util.UUID\n"
        "execution.setVariable('x', true)"
    )

    assert report.passed
    assert any(issue.code == "unused_uuid_import" and issue.severity == "warning" for issue in report.issues)
