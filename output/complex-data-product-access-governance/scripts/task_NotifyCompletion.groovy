import java.util.UUID

String requestId = execution.getVariable('requestId') as String
String finalDecision = (execution.getVariable('finalDecision') ?: 'approved') as String
String recipient = (execution.getVariable('requesterEmail') ?: execution.getVariable('requesterId') ?: 'requester') as String
execution.setVariable('notificationRecipient', recipient)
execution.setVariable('notificationSubject', 'Collibra data product access request ' + requestId + ' ' + finalDecision)
execution.setVariable('notificationQueued', true)
