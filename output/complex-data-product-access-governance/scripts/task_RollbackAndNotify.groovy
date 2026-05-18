import java.util.UUID

String requestId = execution.getVariable('requestId') as String
String apiMessage = (execution.getVariable('relationApiMessage') ?: 'Unknown API error') as String
execution.setVariable('remediationRequired', true)
execution.setVariable('remediationSummary', 'Request ' + requestId + ' requires technical remediation: ' + apiMessage)
execution.setVariable('finalDecision', 'technical-remediation')
