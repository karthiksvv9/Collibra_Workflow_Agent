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
