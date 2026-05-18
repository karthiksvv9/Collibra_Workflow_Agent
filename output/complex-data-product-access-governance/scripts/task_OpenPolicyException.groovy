import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest

String requestId = execution.getVariable('requestId') as String
String assetId = execution.getVariable('assetId') as String
String controls = (execution.getVariable('securityControls') ?: 'Compensating control review required') as String
UUID targetAssetId = UUID.fromString(assetId)
AddAttributeRequest attributeRequest = AddAttributeRequest.builder()
    .assetId(targetAssetId)
    .typeId(UUID.fromString(execution.getVariable('policyExceptionAttributeTypeId') as String))
    .value('Policy exception approved for request ' + requestId + ': ' + controls)
    .build()
attributeApi.addAttribute(attributeRequest)
execution.setVariable('policyExceptionCreated', true)
execution.setVariable('policyExceptionReference', requestId + '-EXCEPTION')
