// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

String assetId = execution.getVariable("assetIdNormalized") as String
def approvedStatusId = string2Uuid(execution.getVariable("approvedStatusId") as String)
assetApi.changeAsset(ChangeAssetRequest.builder()
    .id(string2Uuid(assetId))
    .statusId(approvedStatusId)
    .build())
execution.setVariable("assetStatusUpdated", true)
execution.setVariable("finalDecision", "approved")
