// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest

String assetName = execution.getVariable("assetNameNormalized") as String
String domainIdText = execution.getVariable("domainIdNormalized") as String
String assetTypePublicId = execution.getVariable("assetTypePublicIdNormalized") as String

AddAssetRequest addAssetRequest = AddAssetRequest.builder()
    .name(assetName)
    .displayName(assetName)
    .domainId(string2Uuid(domainIdText))
    .typePublicId(assetTypePublicId)
    .build()

def asset = assetApi.addAsset(addAssetRequest)
execution.setVariable("createdAssetId", asset.getId().toString())

String sourceId = execution.getVariable("relationSourceId") as String
String targetId = execution.getVariable("relationTargetId") as String
String relationTypePublicId = execution.getVariable("relationTypePublicId") as String

if (sourceId?.trim() && targetId?.trim() && relationTypePublicId?.trim()) {
    AddRelationRequest relationRequest = AddRelationRequest.builder()
        .sourceId(string2Uuid(sourceId.trim()))
        .targetId(string2Uuid(targetId.trim()))
        .typePublicId(relationTypePublicId.trim())
        .build()
    def relation = relationApi.addRelation(relationRequest)
    execution.setVariable("createdRelationId", relation.getId().toString())
}
