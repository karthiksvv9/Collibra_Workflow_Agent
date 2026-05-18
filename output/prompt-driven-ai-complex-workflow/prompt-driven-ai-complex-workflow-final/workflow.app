{
  "appName": "Create A Production Collibra Governed Access And Policy",
  "elementProperties": {
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow_pool": {
      "documentation": "",
      "elementId": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow_pool",
      "elementName": "Create A Production Collibra Governed Access And Policy",
      "elementType": "bpmn:Participant",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow_pool",
        "name": "Create A Production Collibra Governed Access And Policy",
        "processRef": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow"
      },
      "scope": "global"
    },
    "business_approval": {
      "candidateGroups": "${businessOwnerRole}",
      "documentation": "Business owner approves, rejects or requests rework.",
      "elementId": "business_approval",
      "elementName": "Business owner approval",
      "elementType": "bpmn:UserTask",
      "execution": "user-form",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:candidateGroups": "${businessOwnerRole}",
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm",
        "id": "business_approval",
        "name": "Business owner approval"
      },
      "scope": "asset"
    },
    "call_provisioning_workflow": {
      "documentation": "Calls a separate Collibra/Flowable workflow to provision access after governance approval.",
      "elementId": "call_provisioning_workflow",
      "elementName": "Call downstream provisioning workflow",
      "elementType": "bpmn:CallActivity",
      "execution": "service-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "calledElement": "${provisioningWorkflowKey}",
        "flowable:businessKey": "${requestId}",
        "flowable:calledElementType": "key",
        "flowable:inheritVariables": "true",
        "id": "call_provisioning_workflow",
        "name": "Call downstream provisioning workflow"
      },
      "scope": "asset"
    },
    "create_policy_exception": {
      "documentation": "Create Collibra policy exception attribute and audit variables using Java API v2 builders.",
      "elementId": "create_policy_exception",
      "elementName": "Create policy exception metadata",
      "elementType": "bpmn:ScriptTask",
      "execution": "script-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "create_policy_exception",
        "name": "Create policy exception metadata",
        "scriptFormat": "groovy"
      },
      "scope": "asset",
      "scriptFormat": "groovy"
    },
    "create_relations": {
      "documentation": "Create relation/responsibility using organization UUID mappings retrieved from RAG.",
      "elementId": "create_relations",
      "elementName": "Create relation and responsibility",
      "elementType": "bpmn:ScriptTask",
      "execution": "script-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "create_relations",
        "name": "Create relation and responsibility",
        "scriptFormat": "groovy"
      },
      "scope": "asset",
      "scriptFormat": "groovy"
    },
    "end_approved": {
      "documentation": "",
      "elementId": "end_approved",
      "elementName": "Approved and provisioned",
      "elementType": "bpmn:EndEvent",
      "execution": "service-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "end_approved",
        "name": "Approved and provisioned"
      },
      "scope": "asset"
    },
    "end_rejected": {
      "documentation": "",
      "elementId": "end_rejected",
      "elementName": "Rejected or withdrawn",
      "elementType": "bpmn:EndEvent",
      "execution": "service-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "end_rejected",
        "name": "Rejected or withdrawn"
      },
      "scope": "asset"
    },
    "flow_business_approve": {
      "condition": "${businessDecision == 'approve'}",
      "documentation": "",
      "elementId": "flow_business_approve",
      "elementName": "Approve",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_business_approve",
        "name": "Approve",
        "sourceRef": "gateway_business_decision",
        "targetRef": "gateway_policy_exception"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_business_gateway": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_business_gateway",
      "elementName": "Decision",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_business_gateway",
        "name": "Decision",
        "sourceRef": "business_approval",
        "targetRef": "gateway_business_decision"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_business_reject": {
      "condition": "${businessDecision == 'reject'}",
      "documentation": "",
      "elementId": "flow_business_reject",
      "elementName": "Reject",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_business_reject",
        "name": "Reject",
        "sourceRef": "gateway_business_decision",
        "targetRef": "notify_rejection"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_business_rework": {
      "condition": "${businessDecision == 'rework'}",
      "documentation": "",
      "elementId": "flow_business_rework",
      "elementName": "Rework",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_business_rework",
        "name": "Rework",
        "sourceRef": "gateway_business_decision",
        "targetRef": "requester_rework"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_call_result": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_call_result",
      "elementName": "Provisioning returned",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_call_result",
        "name": "Provisioning returned",
        "sourceRef": "call_provisioning_workflow",
        "targetRef": "gateway_provisioning_result"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_complete_to_steward": {
      "condition": "${validationPassed == true}",
      "documentation": "",
      "elementId": "flow_complete_to_steward",
      "elementName": "Complete",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_complete_to_steward",
        "name": "Complete",
        "sourceRef": "gateway_request_complete",
        "targetRef": "steward_triage"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_compliance_approve": {
      "condition": "${complianceDecision == 'approve'}",
      "documentation": "",
      "elementId": "flow_compliance_approve",
      "elementName": "Approve",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_compliance_approve",
        "name": "Approve",
        "sourceRef": "gateway_compliance_decision",
        "targetRef": "gateway_policy_exception"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_compliance_gateway": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_compliance_gateway",
      "elementName": "Decision",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_compliance_gateway",
        "name": "Decision",
        "sourceRef": "risk_compliance_review",
        "targetRef": "gateway_compliance_decision"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_compliance_reject": {
      "condition": "${complianceDecision == 'reject'}",
      "documentation": "",
      "elementId": "flow_compliance_reject",
      "elementName": "Reject",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_compliance_reject",
        "name": "Reject",
        "sourceRef": "gateway_compliance_decision",
        "targetRef": "notify_rejection"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_compliance_rework": {
      "condition": "${complianceDecision == 'rework'}",
      "documentation": "",
      "elementId": "flow_compliance_rework",
      "elementName": "Rework",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_compliance_rework",
        "name": "Rework",
        "sourceRef": "gateway_compliance_decision",
        "targetRef": "requester_rework"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_exception_relations": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_exception_relations",
      "elementName": "Exception logged",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_exception_relations",
        "name": "Exception logged",
        "sourceRef": "create_policy_exception",
        "targetRef": "create_relations"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_exception_required": {
      "condition": "${policyExceptionRequired == true}",
      "documentation": "",
      "elementId": "flow_exception_required",
      "elementName": "Exception required",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_exception_required",
        "name": "Exception required",
        "sourceRef": "gateway_policy_exception",
        "targetRef": "create_policy_exception"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_incomplete_to_rework": {
      "condition": "${validationPassed != true}",
      "documentation": "",
      "elementId": "flow_incomplete_to_rework",
      "elementName": "Incomplete",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_incomplete_to_rework",
        "name": "Incomplete",
        "sourceRef": "gateway_request_complete",
        "targetRef": "requester_rework"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_no_exception": {
      "condition": "${policyExceptionRequired != true}",
      "documentation": "",
      "elementId": "flow_no_exception",
      "elementName": "No exception",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_no_exception",
        "name": "No exception",
        "sourceRef": "gateway_policy_exception",
        "targetRef": "create_relations"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_notify_reject_end": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_notify_reject_end",
      "elementName": "Done",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_notify_reject_end",
        "name": "Done",
        "sourceRef": "notify_rejection",
        "targetRef": "end_rejected"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_notify_success_end": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_notify_success_end",
      "elementName": "Done",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_notify_success_end",
        "name": "Done",
        "sourceRef": "notify_success",
        "targetRef": "end_approved"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_provision_failure": {
      "condition": "${provisioningStatus != 'success'}",
      "documentation": "",
      "elementId": "flow_provision_failure",
      "elementName": "Provisioning failed",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_provision_failure",
        "name": "Provisioning failed",
        "sourceRef": "gateway_provisioning_result",
        "targetRef": "technical_remediation"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_provision_success": {
      "condition": "${provisioningStatus == 'success'}",
      "documentation": "",
      "elementId": "flow_provision_success",
      "elementName": "Provisioned",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_provision_success",
        "name": "Provisioned",
        "sourceRef": "gateway_provisioning_result",
        "targetRef": "update_access_status"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_relations_call": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_relations_call",
      "elementName": "Invoke provisioning",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_relations_call",
        "name": "Invoke provisioning",
        "sourceRef": "create_relations",
        "targetRef": "call_provisioning_workflow"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_remediation_retry": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_remediation_retry",
      "elementName": "Retry",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_remediation_retry",
        "name": "Retry",
        "sourceRef": "technical_remediation",
        "targetRef": "call_provisioning_workflow"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_rework_validate": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_rework_validate",
      "elementName": "Resubmit",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_rework_validate",
        "name": "Resubmit",
        "sourceRef": "requester_rework",
        "targetRef": "validate_context"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_risk_compliance": {
      "condition": "${riskRating == 'high' || riskRating == 'restricted'}",
      "documentation": "",
      "elementId": "flow_risk_compliance",
      "elementName": "High risk",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_risk_compliance",
        "name": "High risk",
        "sourceRef": "gateway_risk_route",
        "targetRef": "risk_compliance_review"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_risk_standard": {
      "condition": "${riskRating == 'standard'}",
      "documentation": "",
      "elementId": "flow_risk_standard",
      "elementName": "Standard risk",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_risk_standard",
        "name": "Standard risk",
        "sourceRef": "gateway_risk_route",
        "targetRef": "business_approval"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_start_submit": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_start_submit",
      "elementName": "Start",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_start_submit",
        "name": "Start",
        "sourceRef": "start_request",
        "targetRef": "submit_request"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_status_notify": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_status_notify",
      "elementName": "Status updated",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_status_notify",
        "name": "Status updated",
        "sourceRef": "update_access_status",
        "targetRef": "notify_success"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_steward_approve": {
      "condition": "${stewardDecision == 'approve'}",
      "documentation": "",
      "elementId": "flow_steward_approve",
      "elementName": "Approve",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_steward_approve",
        "name": "Approve",
        "sourceRef": "gateway_steward_decision",
        "targetRef": "gateway_risk_route"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_steward_gateway": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_steward_gateway",
      "elementName": "Route",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_steward_gateway",
        "name": "Route",
        "sourceRef": "steward_triage",
        "targetRef": "gateway_steward_decision"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_steward_reject": {
      "condition": "${stewardDecision == 'reject'}",
      "documentation": "",
      "elementId": "flow_steward_reject",
      "elementName": "Reject",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_steward_reject",
        "name": "Reject",
        "sourceRef": "gateway_steward_decision",
        "targetRef": "notify_rejection"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_steward_rework": {
      "condition": "${stewardDecision == 'rework'}",
      "documentation": "",
      "elementId": "flow_steward_rework",
      "elementName": "Rework",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "conditional",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_steward_rework",
        "name": "Rework",
        "sourceRef": "gateway_steward_decision",
        "targetRef": "requester_rework"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_submit_validate": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_submit_validate",
      "elementName": "Submit",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_submit_validate",
        "name": "Submit",
        "sourceRef": "submit_request",
        "targetRef": "validate_context"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "flow_validate_complete_gateway": {
      "condition": "",
      "documentation": "",
      "elementId": "flow_validate_complete_gateway",
      "elementName": "Validated",
      "elementType": "bpmn:SequenceFlow",
      "execution": "gateway-condition",
      "flowType": "normal",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "flow_validate_complete_gateway",
        "name": "Validated",
        "sourceRef": "validate_context",
        "targetRef": "gateway_request_complete"
      },
      "scope": "global",
      "skipExpression": ""
    },
    "gateway_business_decision": {
      "documentation": "",
      "elementId": "gateway_business_decision",
      "elementName": "Business decision",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_business_rework",
        "id": "gateway_business_decision",
        "name": "Business decision"
      },
      "scope": "global"
    },
    "gateway_compliance_decision": {
      "documentation": "",
      "elementId": "gateway_compliance_decision",
      "elementName": "Compliance decision",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_compliance_rework",
        "id": "gateway_compliance_decision",
        "name": "Compliance decision"
      },
      "scope": "global"
    },
    "gateway_policy_exception": {
      "documentation": "",
      "elementId": "gateway_policy_exception",
      "elementName": "Policy exception?",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_no_exception",
        "id": "gateway_policy_exception",
        "name": "Policy exception?"
      },
      "scope": "global"
    },
    "gateway_provisioning_result": {
      "documentation": "",
      "elementId": "gateway_provisioning_result",
      "elementName": "Provisioning result",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_provision_failure",
        "id": "gateway_provisioning_result",
        "name": "Provisioning result"
      },
      "scope": "global"
    },
    "gateway_request_complete": {
      "documentation": "",
      "elementId": "gateway_request_complete",
      "elementName": "Request complete?",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_incomplete_to_rework",
        "id": "gateway_request_complete",
        "name": "Request complete?"
      },
      "scope": "global"
    },
    "gateway_risk_route": {
      "documentation": "",
      "elementId": "gateway_risk_route",
      "elementName": "Risk route",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_risk_standard",
        "id": "gateway_risk_route",
        "name": "Risk route"
      },
      "scope": "global"
    },
    "gateway_steward_decision": {
      "documentation": "",
      "elementId": "gateway_steward_decision",
      "elementName": "Steward decision",
      "elementType": "bpmn:ExclusiveGateway",
      "execution": "gateway-condition",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "default": "flow_steward_rework",
        "id": "gateway_steward_decision",
        "name": "Steward decision"
      },
      "scope": "global"
    },
    "lane_Business_Owner": {
      "documentation": "",
      "elementId": "lane_Business_Owner",
      "elementName": "Business Owner",
      "elementType": "bpmn:Lane",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "lane_Business_Owner",
        "name": "Business Owner"
      },
      "scope": "global"
    },
    "lane_Collibra_Automation": {
      "documentation": "",
      "elementId": "lane_Collibra_Automation",
      "elementName": "Collibra Automation",
      "elementType": "bpmn:Lane",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "lane_Collibra_Automation",
        "name": "Collibra Automation"
      },
      "scope": "global"
    },
    "lane_Data_Steward": {
      "documentation": "",
      "elementId": "lane_Data_Steward",
      "elementName": "Data Steward",
      "elementType": "bpmn:Lane",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "lane_Data_Steward",
        "name": "Data Steward"
      },
      "scope": "global"
    },
    "lane_Provisioning_Workflow": {
      "documentation": "",
      "elementId": "lane_Provisioning_Workflow",
      "elementName": "Provisioning Workflow",
      "elementType": "bpmn:Lane",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "lane_Provisioning_Workflow",
        "name": "Provisioning Workflow"
      },
      "scope": "global"
    },
    "lane_Requester": {
      "documentation": "",
      "elementId": "lane_Requester",
      "elementName": "Requester",
      "elementType": "bpmn:Lane",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "lane_Requester",
        "name": "Requester"
      },
      "scope": "global"
    },
    "lane_Risk_and_Compliance": {
      "documentation": "",
      "elementId": "lane_Risk_and_Compliance",
      "elementName": "Risk and Compliance",
      "elementType": "bpmn:Lane",
      "execution": "container",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "lane_Risk_and_Compliance",
        "name": "Risk and Compliance"
      },
      "scope": "global"
    },
    "notify_rejection": {
      "documentation": "Queue rejection notification variables for rejected and withdrawn paths.",
      "elementId": "notify_rejection",
      "elementName": "Notify rejection or withdrawal",
      "elementType": "bpmn:ScriptTask",
      "execution": "script-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "notify_rejection",
        "name": "Notify rejection or withdrawal",
        "scriptFormat": "groovy"
      },
      "scope": "asset",
      "scriptFormat": "groovy"
    },
    "notify_success": {
      "documentation": "Queue final notification variables for completion mail task or integration.",
      "elementId": "notify_success",
      "elementName": "Notify approval completion",
      "elementType": "bpmn:ScriptTask",
      "execution": "script-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "notify_success",
        "name": "Notify approval completion",
        "scriptFormat": "groovy"
      },
      "scope": "asset",
      "scriptFormat": "groovy"
    },
    "requester_rework": {
      "candidateGroups": "${requesterGroup}",
      "documentation": "Requester corrects missing purpose, UUIDs, relation details or access constraints.",
      "elementId": "requester_rework",
      "elementName": "Requester rework",
      "elementType": "bpmn:UserTask",
      "execution": "user-form",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:candidateGroups": "${requesterGroup}",
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm",
        "id": "requester_rework",
        "name": "Requester rework"
      },
      "scope": "asset"
    },
    "risk_compliance_review": {
      "candidateGroups": "${riskComplianceRole}",
      "documentation": "Compliance owner reviews high-risk access and approves policy exception where required.",
      "elementId": "risk_compliance_review",
      "elementName": "Risk and compliance review",
      "elementType": "bpmn:UserTask",
      "execution": "user-form",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:candidateGroups": "${riskComplianceRole}",
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm",
        "id": "risk_compliance_review",
        "name": "Risk and compliance review"
      },
      "scope": "asset"
    },
    "start_request": {
      "documentation": "Start event with request form for governed asset access.",
      "elementId": "start_request",
      "elementName": "Start governed access request",
      "elementType": "bpmn:StartEvent",
      "execution": "service-groovy",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm",
        "id": "start_request",
        "name": "Start governed access request"
      },
      "scope": "asset"
    },
    "steward_triage": {
      "candidateGroups": "${dataStewardRole}",
      "documentation": "Steward confirms ownership, domain, asset status, relation intent and routing decision.",
      "elementId": "steward_triage",
      "elementName": "Data steward triage",
      "elementType": "bpmn:UserTask",
      "execution": "user-form",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:candidateGroups": "${dataStewardRole}",
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm",
        "id": "steward_triage",
        "name": "Data steward triage"
      },
      "scope": "asset"
    },
    "submit_request": {
      "candidateGroups": "${requesterGroup}",
      "documentation": "Requester supplies asset, purpose, access window, relation and provisioning intent.",
      "elementId": "submit_request",
      "elementName": "Submit governed access request",
      "elementType": "bpmn:UserTask",
      "execution": "user-form",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:candidateGroups": "${requesterGroup}",
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm",
        "id": "submit_request",
        "name": "Submit governed access request"
      },
      "scope": "asset"
    },
    "technical_remediation": {
      "candidateGroups": "${technicalStewardRole}",
      "documentation": "Technical owner fixes failed provisioning and retries the called workflow.",
      "elementId": "technical_remediation",
      "elementName": "Technical remediation",
      "elementType": "bpmn:UserTask",
      "execution": "user-form",
      "formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "flowable:candidateGroups": "${technicalStewardRole}",
        "flowable:formKey": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm",
        "id": "technical_remediation",
        "name": "Technical remediation"
      },
      "scope": "asset"
    },
    "update_access_status": {
      "documentation": "Apply final Collibra status and audit attributes after downstream workflow success.",
      "elementId": "update_access_status",
      "elementName": "Update asset status and audit",
      "elementType": "bpmn:ScriptTask",
      "execution": "script-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "update_access_status",
        "name": "Update asset status and audit",
        "scriptFormat": "groovy"
      },
      "scope": "asset",
      "scriptFormat": "groovy"
    },
    "validate_context": {
      "documentation": "Normalize UUIDs and validate required organization mapping variables from RAG/config.",
      "elementId": "validate_context",
      "elementName": "Validate request and RAG mappings",
      "elementType": "bpmn:ScriptTask",
      "execution": "script-groovy",
      "importedFrom": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
      "rawAttributes": {
        "id": "validate_context",
        "name": "Validate request and RAG mappings",
        "scriptFormat": "groovy"
      },
      "scope": "asset",
      "scriptFormat": "groovy"
    }
  },
  "forms": {
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm": {
      "description": "",
      "fields": [
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "requesterId",
          "label": "Requester UUID",
          "name": "Requester UUID",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "requesterEmail",
          "label": "Requester email",
          "name": "Requester email",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "assetId",
          "label": "Asset UUID",
          "name": "Asset UUID",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "consumerAssetId",
          "label": "Consumer asset UUID",
          "name": "Consumer asset UUID",
          "readable": true,
          "required": false,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "businessPurpose",
          "label": "Business purpose",
          "name": "Business purpose",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "riskRating",
          "label": "Risk rating",
          "name": "Risk rating",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "enum",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "requestedAccessEndDate",
          "label": "Requested access end date",
          "name": "Requested access end date",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "date",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "provisioningWorkflowKey",
          "label": "Downstream provisioning workflow key",
          "name": "Downstream provisioning workflow key",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        }
      ],
      "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm",
      "metadata": {},
      "modelType": "form",
      "name": "Governed Access Request",
      "outcomes": [],
      "palette": "",
      "raw": {
        "fields": [
          {
            "default": null,
            "id": "requesterId",
            "name": "Requester UUID",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "requesterEmail",
            "name": "Requester email",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "assetId",
            "name": "Asset UUID",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "consumerAssetId",
            "name": "Consumer asset UUID",
            "readable": true,
            "required": false,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "businessPurpose",
            "name": "Business purpose",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "riskRating",
            "name": "Risk rating",
            "readable": true,
            "required": true,
            "type": "enum",
            "values": [
              {
                "id": "standard",
                "name": "Standard"
              },
              {
                "id": "high",
                "name": "High"
              },
              {
                "id": "restricted",
                "name": "Restricted"
              }
            ],
            "writable": true
          },
          {
            "default": null,
            "id": "requestedAccessEndDate",
            "name": "Requested access end date",
            "readable": true,
            "required": true,
            "type": "date",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "provisioningWorkflowKey",
            "name": "Downstream provisioning workflow key",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          }
        ],
        "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm",
        "name": "Governed Access Request"
      },
      "rows": [],
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm.form",
      "version": ""
    },
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm": {
      "description": "",
      "fields": [
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "businessDecision",
          "label": "Business decision",
          "name": "Business decision",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "enum",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "businessNotes",
          "label": "Business approval notes",
          "name": "Business approval notes",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        }
      ],
      "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm",
      "metadata": {},
      "modelType": "form",
      "name": "Business Owner Approval",
      "outcomes": [],
      "palette": "",
      "raw": {
        "fields": [
          {
            "default": null,
            "id": "businessDecision",
            "name": "Business decision",
            "readable": true,
            "required": true,
            "type": "enum",
            "values": [
              {
                "id": "approve",
                "name": "Approve"
              },
              {
                "id": "rework",
                "name": "Request rework"
              },
              {
                "id": "reject",
                "name": "Reject"
              }
            ],
            "writable": true
          },
          {
            "default": null,
            "id": "businessNotes",
            "name": "Business approval notes",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          }
        ],
        "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm",
        "name": "Business Owner Approval"
      },
      "rows": [],
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm.form",
      "version": ""
    },
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm": {
      "description": "",
      "fields": [
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "complianceDecision",
          "label": "Compliance decision",
          "name": "Compliance decision",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "enum",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "policyExceptionRequired",
          "label": "Policy exception required",
          "name": "Policy exception required",
          "readable": true,
          "required": false,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "boolean",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "securityControls",
          "label": "Security controls",
          "name": "Security controls",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        }
      ],
      "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm",
      "metadata": {},
      "modelType": "form",
      "name": "Risk and Compliance Review",
      "outcomes": [],
      "palette": "",
      "raw": {
        "fields": [
          {
            "default": null,
            "id": "complianceDecision",
            "name": "Compliance decision",
            "readable": true,
            "required": true,
            "type": "enum",
            "values": [
              {
                "id": "approve",
                "name": "Approve"
              },
              {
                "id": "rework",
                "name": "Request rework"
              },
              {
                "id": "reject",
                "name": "Reject"
              }
            ],
            "writable": true
          },
          {
            "default": null,
            "id": "policyExceptionRequired",
            "name": "Policy exception required",
            "readable": true,
            "required": false,
            "type": "boolean",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "securityControls",
            "name": "Security controls",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          }
        ],
        "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm",
        "name": "Risk and Compliance Review"
      },
      "rows": [],
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm.form",
      "version": ""
    },
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm": {
      "description": "",
      "fields": [
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "reworkSummary",
          "label": "Rework summary",
          "name": "Rework summary",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "businessPurpose",
          "label": "Updated business purpose",
          "name": "Updated business purpose",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "consumerAssetId",
          "label": "Updated consumer asset UUID",
          "name": "Updated consumer asset UUID",
          "readable": true,
          "required": false,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        }
      ],
      "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm",
      "metadata": {},
      "modelType": "form",
      "name": "Requester Rework",
      "outcomes": [],
      "palette": "",
      "raw": {
        "fields": [
          {
            "default": null,
            "id": "reworkSummary",
            "name": "Rework summary",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "businessPurpose",
            "name": "Updated business purpose",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "consumerAssetId",
            "name": "Updated consumer asset UUID",
            "readable": true,
            "required": false,
            "type": "string",
            "values": [],
            "writable": true
          }
        ],
        "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm",
        "name": "Requester Rework"
      },
      "rows": [],
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm.form",
      "version": ""
    },
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm": {
      "description": "",
      "fields": [
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "stewardDecision",
          "label": "Steward decision",
          "name": "Steward decision",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "enum",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "stewardNotes",
          "label": "Steward notes",
          "name": "Steward notes",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "riskRating",
          "label": "Confirmed risk rating",
          "name": "Confirmed risk rating",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "enum",
          "value": null,
          "visible": true,
          "writable": true
        }
      ],
      "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm",
      "metadata": {},
      "modelType": "form",
      "name": "Steward Triage",
      "outcomes": [],
      "palette": "",
      "raw": {
        "fields": [
          {
            "default": null,
            "id": "stewardDecision",
            "name": "Steward decision",
            "readable": true,
            "required": true,
            "type": "enum",
            "values": [
              {
                "id": "approve",
                "name": "Approve"
              },
              {
                "id": "rework",
                "name": "Request rework"
              },
              {
                "id": "reject",
                "name": "Reject"
              }
            ],
            "writable": true
          },
          {
            "default": null,
            "id": "stewardNotes",
            "name": "Steward notes",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "riskRating",
            "name": "Confirmed risk rating",
            "readable": true,
            "required": true,
            "type": "enum",
            "values": [],
            "writable": true
          }
        ],
        "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm",
        "name": "Steward Triage"
      },
      "rows": [],
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm.form",
      "version": ""
    },
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm": {
      "description": "",
      "fields": [
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "provisioningStatus",
          "label": "Provisioning status",
          "name": "Provisioning status",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "provisioningError",
          "label": "Provisioning error",
          "name": "Provisioning error",
          "readable": true,
          "required": false,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        },
        {
          "column": 0,
          "enabled": true,
          "extraSettings": {},
          "id": "remediationAction",
          "label": "Remediation action",
          "name": "Remediation action",
          "readable": true,
          "required": true,
          "row": 0,
          "size": null,
          "stencilId": null,
          "stencilSuperIds": [],
          "type": "string",
          "value": null,
          "visible": true,
          "writable": true
        }
      ],
      "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm",
      "metadata": {},
      "modelType": "form",
      "name": "Technical Remediation",
      "outcomes": [],
      "palette": "",
      "raw": {
        "fields": [
          {
            "default": null,
            "id": "provisioningStatus",
            "name": "Provisioning status",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "provisioningError",
            "name": "Provisioning error",
            "readable": true,
            "required": false,
            "type": "string",
            "values": [],
            "writable": true
          },
          {
            "default": null,
            "id": "remediationAction",
            "name": "Remediation action",
            "readable": true,
            "required": true,
            "type": "string",
            "values": [],
            "writable": true
          }
        ],
        "key": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm",
        "name": "Technical Remediation"
      },
      "rows": [],
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm.form",
      "version": ""
    }
  },
  "generator": "DSC Collibra Workflow Automation Agent",
  "importDiagnostics": {
    "embeddedScripts": 6,
    "formReferences": 7,
    "inlineForms": 0,
    "missingForms": [],
    "scriptTasks": 6,
    "sequenceFlows": 31,
    "sourceBpmn": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
    "userTasks": 6
  },
  "manifestForms": [
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowAccessRequestForm.form",
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowRequesterReworkForm.form",
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowStewardTriageForm.form",
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowBusinessApprovalForm.form",
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowComplianceReviewForm.form",
    "CreateAProductionCollibraGovernedAiDesignedComplexWorkflowTechnicalRemediationForm.form"
  ],
  "metadata": {
    "format": "DSC_SIDE_CAR_APP_V1",
    "name": "prompt_driven_ai_complex_workflow.zip"
  },
  "process": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn",
  "scripts": {
    "create_policy_exception": {
      "elementId": "create_policy_exception",
      "elementName": "Create policy exception metadata",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\nimport com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest\n\nString assetId = execution.getVariable(\"assetIdNormalized\") as String\nString requestId = execution.getVariable(\"requestId\") as String\nString controls = (execution.getVariable(\"securityControls\") ?: \"Controls must be confirmed before provisioning.\") as String\nUUID attributeTypeId = UUID.fromString(execution.getVariable(\"policyExceptionAttributeTypeId\") as String)\nAddAttributeRequest request = AddAttributeRequest.builder()\n    .assetId(UUID.fromString(assetId))\n    .typeId(attributeTypeId)\n    .value(\"Policy exception for request \" + requestId + \": \" + controls)\n    .build()\nattributeApi.addAttribute(request)\nexecution.setVariable(\"policyExceptionCreated\", true)",
      "importedFrom": "bpmn:scriptTask",
      "scriptFormat": "groovy",
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn"
    },
    "create_relations": {
      "elementId": "create_relations",
      "elementName": "Create relation and responsibility",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\nimport com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest\nimport com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest\n\nString assetId = execution.getVariable(\"assetIdNormalized\") as String\nString consumerAssetId = (execution.getVariable(\"consumerAssetId\") ?: \"\") as String\nString requesterId = execution.getVariable(\"requesterIdNormalized\") as String\nUUID relationTypeId = UUID.fromString(execution.getVariable(\"consumerRelationTypeId\") as String)\nUUID consumerRoleId = UUID.fromString(execution.getVariable(\"consumerRoleId\") as String)\nif (consumerAssetId.trim()) {\n    relationApi.addRelation(AddRelationRequest.builder()\n        .sourceId(UUID.fromString(assetId))\n        .targetId(UUID.fromString(consumerAssetId.trim()))\n        .typeId(relationTypeId)\n        .build())\n}\nresponsibilityApi.addResponsibility(AddResponsibilityRequest.builder()\n    .resourceId(UUID.fromString(assetId))\n    .roleId(consumerRoleId)\n    .ownerId(UUID.fromString(requesterId))\n    .build())\nexecution.setVariable(\"relationAndResponsibilityCreated\", true)",
      "importedFrom": "bpmn:scriptTask",
      "scriptFormat": "groovy",
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn"
    },
    "notify_rejection": {
      "elementId": "notify_rejection",
      "elementName": "Notify rejection or withdrawal",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = execution.getVariable(\"requestId\") as String\nString reason = (execution.getVariable(\"stewardNotes\") ?: execution.getVariable(\"businessNotes\") ?: \"Request rejected or withdrawn.\") as String\nexecution.setVariable(\"finalDecision\", \"rejected\")\nexecution.setVariable(\"notificationSubject\", \"Collibra governed access request \" + requestId + \" rejected\")\nexecution.setVariable(\"notificationBody\", reason)\nexecution.setVariable(\"notificationQueued\", true)",
      "importedFrom": "bpmn:scriptTask",
      "scriptFormat": "groovy",
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn"
    },
    "notify_success": {
      "elementId": "notify_success",
      "elementName": "Notify approval completion",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = execution.getVariable(\"requestId\") as String\nString recipient = (execution.getVariable(\"requesterEmail\") ?: execution.getVariable(\"requesterIdNormalized\") ?: \"requester\") as String\nexecution.setVariable(\"notificationRecipient\", recipient)\nexecution.setVariable(\"notificationSubject\", \"Collibra governed access request \" + requestId + \" approved and provisioned\")\nexecution.setVariable(\"notificationQueued\", true)",
      "importedFrom": "bpmn:scriptTask",
      "scriptFormat": "groovy",
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn"
    },
    "update_access_status": {
      "elementId": "update_access_status",
      "elementName": "Update asset status and audit",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\nimport com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest\n\nString assetId = execution.getVariable(\"assetIdNormalized\") as String\nUUID approvedStatusId = UUID.fromString(execution.getVariable(\"approvedStatusId\") as String)\nassetApi.changeAsset(ChangeAssetRequest.builder()\n    .id(UUID.fromString(assetId))\n    .statusId(approvedStatusId)\n    .build())\nexecution.setVariable(\"assetStatusUpdated\", true)\nexecution.setVariable(\"finalDecision\", \"approved\")",
      "importedFrom": "bpmn:scriptTask",
      "scriptFormat": "groovy",
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn"
    },
    "validate_context": {
      "elementId": "validate_context",
      "elementName": "Validate request and RAG mappings",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = (execution.getVariable(\"requestId\") ?: UUID.randomUUID().toString()) as String\nString requesterId = (execution.getVariable(\"requesterId\") ?: \"\") as String\nString assetId = (execution.getVariable(\"assetId\") ?: \"\") as String\nString purpose = (execution.getVariable(\"businessPurpose\") ?: \"\") as String\nString workflowKey = (execution.getVariable(\"provisioningWorkflowKey\") ?: \"\") as String\nBoolean complete = requesterId.trim() && assetId.trim() && purpose.trim().length() > 15 && workflowKey.trim()\nexecution.setVariable(\"requestId\", requestId)\nexecution.setVariable(\"requesterIdNormalized\", requesterId.trim())\nexecution.setVariable(\"assetIdNormalized\", assetId.trim())\nexecution.setVariable(\"businessPurposeNormalized\", purpose.trim())\nexecution.setVariable(\"validationPassed\", complete)\nexecution.setVariable(\"validationMessage\", complete ? \"Request is complete.\" : \"Requester, asset, purpose and provisioning workflow key are required.\")",
      "importedFrom": "bpmn:scriptTask",
      "scriptFormat": "groovy",
      "source": "CreateAProductionCollibraGovernedAiDesignedComplexWorkflow.bpmn"
    }
  },
  "uuidMappings": {},
  "validationRules": []
}