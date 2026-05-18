import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String consumerAssetId = (execution.getVariable("consumerAssetId") ?: "") as String
String requesterId = execution.getVariable("requesterIdNormalized") as String
UUID relationTypeId = UUID.fromString(execution.getVariable("consumerRelationTypeId") as String)
UUID consumerRoleId = UUID.fromString(execution.getVariable("consumerRoleId") as String)
if (consumerAssetId.trim()) {
    relationApi.addRelation(AddRelationRequest.builder()
        .sourceId(UUID.fromString(assetId))
        .targetId(UUID.fromString(consumerAssetId.trim()))
        .typeId(relationTypeId)
        .build())
}
responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
    .resourceId(UUID.fromString(assetId))
    .roleId(consumerRoleId)
    .ownerId(UUID.fromString(requesterId))
    .build())
execution.setVariable("relationAndResponsibilityCreated", true)