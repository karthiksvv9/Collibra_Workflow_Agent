from src.agents.groovy_compiler import GroovyCompiler
from src.core.config import GroovyConfig


def test_compiler_accepts_missing_collibra_runtime_classes_with_local_stubs() -> None:
    script = """
import com.collibra.catalog.api.component.businessmodel.dto.FindDataElementsRequest
import static com.collibra.catalog.core.businessmodel.paging.PagingHelper.paginateAll

FindDataElementsRequest.Builder builder = FindDataElementsRequest.builder().assetId('asset-id')
def request = builder.build()
def values = paginateAll(null, request)
try {
    execution.setVariable('valuesFound', values != null)
} catch (com.collibra.common.api.exception.ApiEntityNotFoundException e) {
    execution.setVariable('valuesFound', false)
}
"""

    result = GroovyCompiler().compile_script(script)

    if result.skipped:
        assert result.ok is False
        assert "not a deployable success state" in result.stderr
    else:
        assert result.ok is True
        assert "temporary Collibra dependency stubs" in result.stdout


def test_compiler_skipped_runtime_is_not_success() -> None:
    compiler = GroovyCompiler(
        GroovyConfig(
            executable="definitely-missing-groovy",
            java_executable="definitely-missing-java",
            use_embedded_jars=False,
        )
    )

    result = compiler.compile_script("// #importFile NONE\nexecution.setVariable('validated', true)")

    assert result.skipped is True
    assert result.ok is False
    assert "not a deployable success state" in result.stderr
