import java.util.UUID

String requestId = execution.getVariable('requestId') as String
String reason = (execution.getVariable('rejectionReason') ?: execution.getVariable('triageNotes') ?: execution.getVariable('approvalNotes') ?: 'Request rejected by governance review.') as String
execution.setVariable('finalDecision', 'rejected')
execution.setVariable('notificationSubject', 'Collibra data product access request ' + requestId + ' rejected')
execution.setVariable('notificationBody', reason)
execution.setVariable('notificationQueued', true)
