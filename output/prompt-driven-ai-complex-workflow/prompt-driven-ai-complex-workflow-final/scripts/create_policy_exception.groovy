import java.util.UUID
import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String requestId = execution.getVariable("requestId") as String
String controls = (execution.getVariable("securityControls") ?: "Controls must be confirmed before provisioning.") as String
UUID attributeTypeId = UUID.fromString(execution.getVariable("policyExceptionAttributeTypeId") as String)
AddAttributeRequest request = AddAttributeRequest.builder()
    .assetId(UUID.fromString(assetId))
    .typeId(attributeTypeId)
    .value("Policy exception for request " + requestId + ": " + controls)
    .build()
attributeApi.addAttribute(request)
execution.setVariable("policyExceptionCreated", true)