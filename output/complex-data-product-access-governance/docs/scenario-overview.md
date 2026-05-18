# Complex Data Product Access Governance

Generated: 2026-05-17T03:55:39.043798+00:00

This production-candidate scenario models a complex Collibra data product access workflow with multiple reroutes:

- requester intake and requester rework loop
- steward triage approve/rework/reject
- risk-based routing to business owner or security/privacy review
- business and security approval/rework/reject paths
- optional policy exception creation
- Collibra Java API relation/responsibility/status automation
- technical remediation loop when an API task fails
- completion and rejection notification tasks

Primary user-test scenarios are included in `scenario-test-cases.md`.
