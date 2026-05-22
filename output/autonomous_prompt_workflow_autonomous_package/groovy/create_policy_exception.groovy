// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest

String assetId = execution.getVariable("assetIdNormalized") as String
String requestId = execution.getVariable("requestId") as String
String controls = (execution.getVariable("securityControls") ?: "Controls must be confirmed before provisioning.") as String
def attributeTypeId = string2Uuid(execution.getVariable("policyExceptionAttributeTypeId") as String)
AddAttributeRequest request = AddAttributeRequest.builder()
    .assetId(string2Uuid(assetId))
    .typeId(attributeTypeId)
    .value("Policy exception for request " + requestId + ": " + controls)
    .build()
attributeApi.addAttribute(request)
execution.setVariable("policyExceptionCreated", true)
