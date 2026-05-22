// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String consumerAssetId = (execution.getVariable("consumerAssetId") ?: "") as String
String requesterId = execution.getVariable("requesterIdNormalized") as String
def relationTypeId = string2Uuid(execution.getVariable("consumerRelationTypeId") as String)
def consumerRoleId = string2Uuid(execution.getVariable("consumerRoleId") as String)
if (consumerAssetId.trim()) {
    relationApi.addRelation(AddRelationRequest.builder()
        .sourceId(string2Uuid(assetId))
        .targetId(string2Uuid(consumerAssetId.trim()))
        .typeId(relationTypeId)
        .build())
}
responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
    .resourceId(string2Uuid(assetId))
    .roleId(consumerRoleId)
    .ownerId(string2Uuid(requesterId))
    .build())
execution.setVariable("relationAndResponsibilityCreated", true)
