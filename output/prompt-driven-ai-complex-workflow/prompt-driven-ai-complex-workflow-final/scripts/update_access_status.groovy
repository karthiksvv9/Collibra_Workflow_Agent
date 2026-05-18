import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

String assetId = execution.getVariable("assetIdNormalized") as String
UUID approvedStatusId = UUID.fromString(execution.getVariable("approvedStatusId") as String)
assetApi.changeAsset(ChangeAssetRequest.builder()
    .id(UUID.fromString(assetId))
    .statusId(approvedStatusId)
    .build())
execution.setVariable("assetStatusUpdated", true)
execution.setVariable("finalDecision", "approved")