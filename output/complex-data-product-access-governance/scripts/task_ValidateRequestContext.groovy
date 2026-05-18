import java.util.UUID

String requestId = (execution.getVariable('requestId') ?: UUID.randomUUID().toString()) as String
String requester = (execution.getVariable('requesterId') ?: execution.getVariable('initiator') ?: 'unknown-requester') as String
String assetId = (execution.getVariable('assetId') ?: '') as String
String purpose = (execution.getVariable('businessPurpose') ?: '') as String
String riskRating = (execution.getVariable('riskRating') ?: 'standard') as String
Boolean complete = assetId.trim().length() > 0 && purpose.trim().length() > 15
execution.setVariable('requestId', requestId)
execution.setVariable('requesterId', requester)
execution.setVariable('riskRating', riskRating)
execution.setVariable('validationPassed', complete)
execution.setVariable('validationMessage', complete ? 'Request context is complete.' : 'Asset and business purpose are required before steward triage.')
