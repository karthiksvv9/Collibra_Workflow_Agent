// #importFile NONE

String requestId = execution.getVariable("requestId") as String
String recipient = (execution.getVariable("requesterEmail") ?: execution.getVariable("requesterIdNormalized") ?: "requester") as String
execution.setVariable("notificationRecipient", recipient)
execution.setVariable("notificationSubject", "Collibra governed access request " + requestId + " approved and provisioned")
execution.setVariable("notificationQueued", true)
