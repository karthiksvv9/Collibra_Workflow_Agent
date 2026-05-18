import java.util.UUID

String requestId = execution.getVariable("requestId") as String
String reason = (execution.getVariable("stewardNotes") ?: execution.getVariable("businessNotes") ?: "Request rejected or withdrawn.") as String
execution.setVariable("finalDecision", "rejected")
execution.setVariable("notificationSubject", "Collibra governed access request " + requestId + " rejected")
execution.setVariable("notificationBody", reason)
execution.setVariable("notificationQueued", true)