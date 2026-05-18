Scenario: Prompt-only standard approval path
Start a standard-risk request with requesterId, requesterEmail, assetId, businessPurpose, provisioningWorkflowKey, steward approve, business approve, policyExceptionRequired false, provisioningStatus success.
Expected: relation/responsibility script runs, call activity invokes downstream workflow, asset status update runs, success notification queued, approved end reached.

Scenario: Restricted policy exception path
Submit a restricted asset request, steward approve, compliance approve, policyExceptionRequired true, provisioningStatus success.
Expected: policy exception Groovy runs before relation/responsibility and call activity, then completion path succeeds.

Scenario: Requester rework route
Submit missing businessPurpose or provisioningWorkflowKey.
Expected: validationPassed false, route to requester rework, resubmit to validation, then steward triage.

Scenario: Business rejection route
Submit standard-risk request, steward approve, businessDecision reject.
Expected: rejection notification script queues reason and reaches rejected end.

Scenario: Downstream provisioning failure route
Submit fully approved request but set provisioningStatus failed.
Expected: workflow routes to technical remediation and retries the call activity.
