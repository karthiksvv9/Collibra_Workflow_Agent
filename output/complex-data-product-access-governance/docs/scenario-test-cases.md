Scenario: Standard-risk happy path
Start with a complete dataAccessRequestForm, standard risk, steward approve, business owner approve, no policy exception, Collibra relation API succeeds.
Expected: Workflow reaches Approved and implemented, queues completion notification, and updates asset status.

Scenario: Requester rework path
Start with missing business purpose or invalid asset UUID so validationPassed is false.
Expected: Workflow reroutes to Requester rework, resubmits to validation, then continues to steward triage.

Scenario: High-risk policy exception path
Submit high risk request, steward approve, security approve with policyExceptionRequired true.
Expected: Workflow creates policy exception, then creates relation/responsibility, updates status, and completes.

Scenario: Business rejection path
Submit standard-risk request, steward approve, business owner reject.
Expected: Workflow queues rejection notification and reaches Rejected end event.

Scenario: Collibra API failure remediation path
Submit approved request but relation API throws an exception.
Expected: Workflow records API failure, routes to Technical remediation, retries relation/responsibility creation, then continues after success.
