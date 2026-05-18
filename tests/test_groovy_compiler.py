from src.agents.groovy_compiler import GroovyCompiler


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

    assert result.ok is True
    assert result.skipped or "temporary Collibra dependency stubs" in result.stdout
