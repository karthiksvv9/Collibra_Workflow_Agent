import java.util.UUID

String requestId = (execution.getVariable("requestId") ?: UUID.randomUUID().toString()) as String
String requesterId = (execution.getVariable("requesterId") ?: "") as String
String assetId = (execution.getVariable("assetId") ?: "") as String
String purpose = (execution.getVariable("businessPurpose") ?: "") as String
String workflowKey = (execution.getVariable("provisioningWorkflowKey") ?: "") as String
Boolean complete = requesterId.trim() && assetId.trim() && purpose.trim().length() > 15 && workflowKey.trim()
execution.setVariable("requestId", requestId)
execution.setVariable("requesterIdNormalized", requesterId.trim())
execution.setVariable("assetIdNormalized", assetId.trim())
execution.setVariable("businessPurposeNormalized", purpose.trim())
execution.setVariable("validationPassed", complete)
execution.setVariable("validationMessage", complete ? "Request is complete." : "Requester, asset, purpose and provisioning workflow key are required.")