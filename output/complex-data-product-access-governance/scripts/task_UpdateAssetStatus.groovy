import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

String assetId = execution.getVariable('assetId') as String
String statusId = execution.getVariable('approvedStatusId') as String
ChangeAssetRequest request = ChangeAssetRequest.builder()
    .id(UUID.fromString(assetId))
    .statusId(UUID.fromString(statusId))
    .build()
assetApi.changeAsset(request)
execution.setVariable('assetStatusUpdated', true)
execution.setVariable('finalDecision', 'approved')
