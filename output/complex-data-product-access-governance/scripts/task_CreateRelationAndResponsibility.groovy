import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

String assetId = execution.getVariable('assetId') as String
String consumerAssetId = execution.getVariable('consumerAssetId') as String
String requesterId = execution.getVariable('requesterId') as String
UUID relationTypeId = UUID.fromString(execution.getVariable('consumerRelationTypeId') as String)
UUID roleId = UUID.fromString(execution.getVariable('consumerRoleId') as String)
try {
    if (consumerAssetId?.trim()) {
        relationApi.addRelation(AddRelationRequest.builder()
            .sourceId(UUID.fromString(assetId))
            .targetId(UUID.fromString(consumerAssetId))
            .typeId(relationTypeId)
            .build())
    }
    responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
        .resourceId(UUID.fromString(assetId))
        .roleId(roleId)
        .ownerId(UUID.fromString(requesterId))
        .build())
    execution.setVariable('relationApiSucceeded', true)
    execution.setVariable('relationApiMessage', 'Relation and responsibility created.')
} catch (Exception ex) {
    execution.setVariable('relationApiSucceeded', false)
    execution.setVariable('relationApiMessage', ex.getMessage())
}
