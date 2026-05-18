{
  "appName": "Complex Data Product Access Governance",
  "childModels": [
    {
      "path": "complexDataProductAccessGovernance.bpmn",
      "type": "bpmn"
    },
    {
      "key": "dataAccessRequestForm",
      "path": "forms/dataAccessRequestForm.form",
      "type": "form"
    },
    {
      "key": "reworkForm",
      "path": "forms/reworkForm.form",
      "type": "form"
    },
    {
      "key": "stewardTriageForm",
      "path": "forms/stewardTriageForm.form",
      "type": "form"
    },
    {
      "key": "businessApprovalForm",
      "path": "forms/businessApprovalForm.form",
      "type": "form"
    },
    {
      "key": "securityReviewForm",
      "path": "forms/securityReviewForm.form",
      "type": "form"
    },
    {
      "key": "remediationForm",
      "path": "forms/remediationForm.form",
      "type": "form"
    },
    {
      "elementId": "task_ValidateRequestContext",
      "path": "scripts/task_ValidateRequestContext.groovy",
      "type": "groovy"
    },
    {
      "elementId": "task_OpenPolicyException",
      "path": "scripts/task_OpenPolicyException.groovy",
      "type": "groovy"
    },
    {
      "elementId": "task_CreateRelationAndResponsibility",
      "path": "scripts/task_CreateRelationAndResponsibility.groovy",
      "type": "groovy"
    },
    {
      "elementId": "task_UpdateAssetStatus",
      "path": "scripts/task_UpdateAssetStatus.groovy",
      "type": "groovy"
    },
    {
      "elementId": "task_RollbackAndNotify",
      "path": "scripts/task_RollbackAndNotify.groovy",
      "type": "groovy"
    },
    {
      "elementId": "task_NotifyCompletion",
      "path": "scripts/task_NotifyCompletion.groovy",
      "type": "groovy"
    },
    {
      "elementId": "task_NotifyRejection",
      "path": "scripts/task_NotifyRejection.groovy",
      "type": "groovy"
    }
  ],
  "elementProperties": {
    "end_Approved": {
      "id": "end_Approved",
      "lane": "Lane_Requester",
      "name": "Approved and implemented",
      "type": "bpmn:endEvent"
    },
    "end_Rejected": {
      "id": "end_Rejected",
      "lane": "Lane_Requester",
      "name": "Rejected",
      "type": "bpmn:endEvent"
    },
    "flow_ApiFailure": {
      "condition": "${relationApiSucceeded != true}",
      "flowType": "conditional",
      "id": "flow_ApiFailure",
      "name": "Failure",
      "sourceRef": "gw_RelationApiOk",
      "targetRef": "task_RollbackAndNotify",
      "type": "bpmn:sequenceFlow"
    },
    "flow_ApiSuccess": {
      "condition": "${relationApiSucceeded == true}",
      "flowType": "conditional",
      "id": "flow_ApiSuccess",
      "name": "Success",
      "sourceRef": "gw_RelationApiOk",
      "targetRef": "task_UpdateAssetStatus",
      "type": "bpmn:sequenceFlow"
    },
    "flow_BusinessApprove": {
      "condition": "${businessOwnerDecision == 'approve'}",
      "flowType": "conditional",
      "id": "flow_BusinessApprove",
      "name": "Approve",
      "sourceRef": "gw_BusinessDecision",
      "targetRef": "gw_PolicyException",
      "type": "bpmn:sequenceFlow"
    },
    "flow_BusinessReject": {
      "condition": "${businessOwnerDecision == 'reject'}",
      "flowType": "conditional",
      "id": "flow_BusinessReject",
      "name": "Reject",
      "sourceRef": "gw_BusinessDecision",
      "targetRef": "task_NotifyRejection",
      "type": "bpmn:sequenceFlow"
    },
    "flow_BusinessToDecision": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_BusinessToDecision",
      "name": "Decision",
      "sourceRef": "task_BusinessApproval",
      "targetRef": "gw_BusinessDecision",
      "type": "bpmn:sequenceFlow"
    },
    "flow_BusinessToRework": {
      "condition": "${businessOwnerDecision == 'rework'}",
      "flowType": "conditional",
      "id": "flow_BusinessToRework",
      "name": "Rework",
      "sourceRef": "gw_BusinessDecision",
      "targetRef": "task_ReworkRequest",
      "type": "bpmn:sequenceFlow"
    },
    "flow_CompleteToTriage": {
      "condition": "${validationPassed == true}",
      "flowType": "conditional",
      "id": "flow_CompleteToTriage",
      "name": "Complete",
      "sourceRef": "gw_RequestComplete",
      "targetRef": "task_StewardTriage",
      "type": "bpmn:sequenceFlow"
    },
    "flow_ExceptionToRelation": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_ExceptionToRelation",
      "name": "Record created",
      "sourceRef": "task_OpenPolicyException",
      "targetRef": "task_CreateRelationAndResponsibility",
      "type": "bpmn:sequenceFlow"
    },
    "flow_FailureToRemediation": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_FailureToRemediation",
      "name": "Remediate",
      "sourceRef": "task_RollbackAndNotify",
      "targetRef": "task_TechnicalRemediation",
      "type": "bpmn:sequenceFlow"
    },
    "flow_IncompleteToRework": {
      "condition": "${validationPassed != true}",
      "flowType": "conditional",
      "id": "flow_IncompleteToRework",
      "name": "Incomplete",
      "sourceRef": "gw_RequestComplete",
      "targetRef": "task_ReworkRequest",
      "type": "bpmn:sequenceFlow"
    },
    "flow_NoPolicyException": {
      "condition": "${policyExceptionRequired != true}",
      "flowType": "conditional",
      "id": "flow_NoPolicyException",
      "name": "No exception",
      "sourceRef": "gw_PolicyException",
      "targetRef": "task_CreateRelationAndResponsibility",
      "type": "bpmn:sequenceFlow"
    },
    "flow_NotifyToApprovedEnd": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_NotifyToApprovedEnd",
      "name": "Done",
      "sourceRef": "task_NotifyCompletion",
      "targetRef": "end_Approved",
      "type": "bpmn:sequenceFlow"
    },
    "flow_PolicyExceptionRequired": {
      "condition": "${policyExceptionRequired == true}",
      "flowType": "conditional",
      "id": "flow_PolicyExceptionRequired",
      "name": "Exception required",
      "sourceRef": "gw_PolicyException",
      "targetRef": "task_OpenPolicyException",
      "type": "bpmn:sequenceFlow"
    },
    "flow_RejectNotifyToEnd": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_RejectNotifyToEnd",
      "name": "Done",
      "sourceRef": "task_NotifyRejection",
      "targetRef": "end_Rejected",
      "type": "bpmn:sequenceFlow"
    },
    "flow_RelationToApiCheck": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_RelationToApiCheck",
      "name": "API result",
      "sourceRef": "task_CreateRelationAndResponsibility",
      "targetRef": "gw_RelationApiOk",
      "type": "bpmn:sequenceFlow"
    },
    "flow_RemediationToRelation": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_RemediationToRelation",
      "name": "Retry",
      "sourceRef": "task_TechnicalRemediation",
      "targetRef": "task_CreateRelationAndResponsibility",
      "type": "bpmn:sequenceFlow"
    },
    "flow_RequestToValidate": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_RequestToValidate",
      "name": "Submit",
      "sourceRef": "task_RequestDataAccess",
      "targetRef": "task_ValidateRequestContext",
      "type": "bpmn:sequenceFlow"
    },
    "flow_ReworkToValidate": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_ReworkToValidate",
      "name": "Resubmit",
      "sourceRef": "task_ReworkRequest",
      "targetRef": "task_ValidateRequestContext",
      "type": "bpmn:sequenceFlow"
    },
    "flow_RiskToBusiness": {
      "condition": "${riskRating == 'standard'}",
      "flowType": "conditional",
      "id": "flow_RiskToBusiness",
      "name": "Standard risk",
      "sourceRef": "gw_RiskRouting",
      "targetRef": "task_BusinessApproval",
      "type": "bpmn:sequenceFlow"
    },
    "flow_RiskToSecurity": {
      "condition": "${riskRating == 'high' || riskRating == 'restricted'}",
      "flowType": "conditional",
      "id": "flow_RiskToSecurity",
      "name": "High or restricted risk",
      "sourceRef": "gw_RiskRouting",
      "targetRef": "task_SecurityReview",
      "type": "bpmn:sequenceFlow"
    },
    "flow_SecurityApprove": {
      "condition": "${securityDecision == 'approve'}",
      "flowType": "conditional",
      "id": "flow_SecurityApprove",
      "name": "Approve",
      "sourceRef": "gw_SecurityDecision",
      "targetRef": "gw_PolicyException",
      "type": "bpmn:sequenceFlow"
    },
    "flow_SecurityReject": {
      "condition": "${securityDecision == 'reject'}",
      "flowType": "conditional",
      "id": "flow_SecurityReject",
      "name": "Reject",
      "sourceRef": "gw_SecurityDecision",
      "targetRef": "task_NotifyRejection",
      "type": "bpmn:sequenceFlow"
    },
    "flow_SecurityToDecision": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_SecurityToDecision",
      "name": "Decision",
      "sourceRef": "task_SecurityReview",
      "targetRef": "gw_SecurityDecision",
      "type": "bpmn:sequenceFlow"
    },
    "flow_SecurityToRework": {
      "condition": "${securityDecision == 'rework'}",
      "flowType": "conditional",
      "id": "flow_SecurityToRework",
      "name": "Rework",
      "sourceRef": "gw_SecurityDecision",
      "targetRef": "task_ReworkRequest",
      "type": "bpmn:sequenceFlow"
    },
    "flow_StartToRequest": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_StartToRequest",
      "name": "Start",
      "sourceRef": "start_Request",
      "targetRef": "task_RequestDataAccess",
      "type": "bpmn:sequenceFlow"
    },
    "flow_StatusToNotify": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_StatusToNotify",
      "name": "Status updated",
      "sourceRef": "task_UpdateAssetStatus",
      "targetRef": "task_NotifyCompletion",
      "type": "bpmn:sequenceFlow"
    },
    "flow_TriageApproveToRisk": {
      "condition": "${triageDecision == 'approve'}",
      "flowType": "conditional",
      "id": "flow_TriageApproveToRisk",
      "name": "Approve",
      "sourceRef": "gw_TriageDecision",
      "targetRef": "gw_RiskRouting",
      "type": "bpmn:sequenceFlow"
    },
    "flow_TriageReject": {
      "condition": "${triageDecision == 'reject'}",
      "flowType": "conditional",
      "id": "flow_TriageReject",
      "name": "Reject",
      "sourceRef": "gw_TriageDecision",
      "targetRef": "task_NotifyRejection",
      "type": "bpmn:sequenceFlow"
    },
    "flow_TriageToDecision": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_TriageToDecision",
      "name": "Triage submitted",
      "sourceRef": "task_StewardTriage",
      "targetRef": "gw_TriageDecision",
      "type": "bpmn:sequenceFlow"
    },
    "flow_TriageToRework": {
      "condition": "${triageDecision == 'rework'}",
      "flowType": "conditional",
      "id": "flow_TriageToRework",
      "name": "Rework",
      "sourceRef": "gw_TriageDecision",
      "targetRef": "task_ReworkRequest",
      "type": "bpmn:sequenceFlow"
    },
    "flow_ValidateToComplete": {
      "condition": "",
      "flowType": "normal",
      "id": "flow_ValidateToComplete",
      "name": "Validated",
      "sourceRef": "task_ValidateRequestContext",
      "targetRef": "gw_RequestComplete",
      "type": "bpmn:sequenceFlow"
    },
    "gw_BusinessDecision": {
      "id": "gw_BusinessDecision",
      "lane": "Lane_Business",
      "name": "Business decision",
      "type": "bpmn:exclusiveGateway"
    },
    "gw_PolicyException": {
      "id": "gw_PolicyException",
      "lane": "Lane_Automation",
      "name": "Policy exception?",
      "type": "bpmn:exclusiveGateway"
    },
    "gw_RelationApiOk": {
      "id": "gw_RelationApiOk",
      "lane": "Lane_Automation",
      "name": "API success?",
      "type": "bpmn:exclusiveGateway"
    },
    "gw_RequestComplete": {
      "id": "gw_RequestComplete",
      "lane": "Lane_Automation",
      "name": "Request complete?",
      "type": "bpmn:exclusiveGateway"
    },
    "gw_RiskRouting": {
      "id": "gw_RiskRouting",
      "lane": "Lane_Automation",
      "name": "Risk routing",
      "type": "bpmn:exclusiveGateway"
    },
    "gw_SecurityDecision": {
      "id": "gw_SecurityDecision",
      "lane": "Lane_Security",
      "name": "Security decision",
      "type": "bpmn:exclusiveGateway"
    },
    "gw_TriageDecision": {
      "id": "gw_TriageDecision",
      "lane": "Lane_Steward",
      "name": "Triage decision",
      "type": "bpmn:exclusiveGateway"
    },
    "start_Request": {
      "formKey": "dataAccessRequestForm",
      "id": "start_Request",
      "lane": "Lane_Requester",
      "name": "Start request",
      "type": "bpmn:startEvent"
    },
    "task_BusinessApproval": {
      "candidateGroups": "Business Owners",
      "formKey": "businessApprovalForm",
      "id": "task_BusinessApproval",
      "lane": "Lane_Business",
      "name": "Business owner approval",
      "type": "bpmn:userTask"
    },
    "task_CreateRelationAndResponsibility": {
      "id": "task_CreateRelationAndResponsibility",
      "lane": "Lane_Automation",
      "name": "Create relation and responsibility",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    },
    "task_NotifyCompletion": {
      "id": "task_NotifyCompletion",
      "lane": "Lane_Automation",
      "name": "Queue completion notification",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    },
    "task_NotifyRejection": {
      "id": "task_NotifyRejection",
      "lane": "Lane_Automation",
      "name": "Queue rejection notification",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    },
    "task_OpenPolicyException": {
      "id": "task_OpenPolicyException",
      "lane": "Lane_Automation",
      "name": "Open policy exception record",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    },
    "task_RequestDataAccess": {
      "candidateGroups": "Data Consumers",
      "formKey": "dataAccessRequestForm",
      "id": "task_RequestDataAccess",
      "lane": "Lane_Requester",
      "name": "Submit data product access request",
      "type": "bpmn:userTask"
    },
    "task_ReworkRequest": {
      "candidateGroups": "Data Consumers",
      "formKey": "reworkForm",
      "id": "task_ReworkRequest",
      "lane": "Lane_Requester",
      "name": "Requester rework",
      "type": "bpmn:userTask"
    },
    "task_RollbackAndNotify": {
      "id": "task_RollbackAndNotify",
      "lane": "Lane_Automation",
      "name": "Record API failure and notify",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    },
    "task_SecurityReview": {
      "candidateGroups": "Privacy Owners,Security Owners",
      "formKey": "securityReviewForm",
      "id": "task_SecurityReview",
      "lane": "Lane_Security",
      "name": "Security and privacy review",
      "type": "bpmn:userTask"
    },
    "task_StewardTriage": {
      "candidateGroups": "Data Stewards",
      "formKey": "stewardTriageForm",
      "id": "task_StewardTriage",
      "lane": "Lane_Steward",
      "name": "Steward triage and route",
      "type": "bpmn:userTask"
    },
    "task_TechnicalRemediation": {
      "candidateGroups": "Technical Stewards",
      "formKey": "remediationForm",
      "id": "task_TechnicalRemediation",
      "lane": "Lane_Technical",
      "name": "Technical remediation",
      "type": "bpmn:userTask"
    },
    "task_UpdateAssetStatus": {
      "id": "task_UpdateAssetStatus",
      "lane": "Lane_Automation",
      "name": "Update asset status",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    },
    "task_ValidateRequestContext": {
      "id": "task_ValidateRequestContext",
      "lane": "Lane_Automation",
      "name": "Validate request context",
      "scriptFormat": "groovy",
      "type": "bpmn:scriptTask"
    }
  },
  "forms": {
    "businessApprovalForm": {
      "description": "Business owner approval with reject and rework reroutes.",
      "fields": [
        {
          "enabled": true,
          "id": "businessOwnerDecision",
          "label": "Business owner decision",
          "name": "Business owner decision",
          "readable": true,
          "required": true,
          "type": "dropdown",
          "values": [
            {
              "label": "Approve",
              "value": "approve"
            },
            {
              "label": "Rework",
              "value": "rework"
            },
            {
              "label": "Reject",
              "value": "reject"
            }
          ],
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "approvalNotes",
          "label": "Approval notes",
          "name": "Approval notes",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        }
      ],
      "key": "businessApprovalForm",
      "metadata": {
        "description": "Business owner approval with reject and rework reroutes.",
        "key": "businessApprovalForm",
        "modelType": "form",
        "name": "Business Owner Approval",
        "version": "1.0.0"
      },
      "name": "Business Owner Approval",
      "outcomes": [
        {
          "label": "Submit decision",
          "primary": true,
          "value": "submit_decision"
        }
      ]
    },
    "dataAccessRequestForm": {
      "description": "Requester intake form for governed data product access.",
      "fields": [
        {
          "enabled": true,
          "id": "requesterId",
          "label": "Requester UUID",
          "name": "Requester UUID",
          "readable": true,
          "required": true,
          "type": "string",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "requesterEmail",
          "label": "Requester email",
          "name": "Requester email",
          "readable": true,
          "required": true,
          "type": "string",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "assetId",
          "label": "Data product asset UUID",
          "name": "Data product asset UUID",
          "readable": true,
          "required": true,
          "type": "string",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "consumerAssetId",
          "label": "Consuming application asset UUID",
          "name": "Consuming application asset UUID",
          "readable": true,
          "required": false,
          "type": "string",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "businessPurpose",
          "label": "Business purpose",
          "name": "Business purpose",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "riskRating",
          "label": "Risk rating",
          "name": "Risk rating",
          "readable": true,
          "required": true,
          "type": "dropdown",
          "values": [
            {
              "label": "Standard",
              "value": "standard"
            },
            {
              "label": "High",
              "value": "high"
            },
            {
              "label": "Restricted",
              "value": "restricted"
            }
          ],
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "requestedAccessEndDate",
          "label": "Access end date",
          "name": "Access end date",
          "readable": true,
          "required": true,
          "type": "date",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "acceptUsagePolicy",
          "label": "Accept usage policy",
          "name": "Accept usage policy",
          "readable": true,
          "required": true,
          "type": "checkbox",
          "visible": true,
          "writable": true
        }
      ],
      "key": "dataAccessRequestForm",
      "metadata": {
        "description": "Requester intake form for governed data product access.",
        "key": "dataAccessRequestForm",
        "modelType": "form",
        "name": "Data Product Access Request",
        "version": "1.0.0"
      },
      "name": "Data Product Access Request",
      "outcomes": [
        {
          "label": "Submit",
          "primary": true,
          "value": "submit"
        },
        {
          "label": "Save draft",
          "primary": false,
          "value": "save_draft"
        }
      ]
    },
    "remediationForm": {
      "description": "Technical steward action form after Collibra API failure.",
      "fields": [
        {
          "enabled": true,
          "id": "remediationAction",
          "label": "Remediation action",
          "name": "Remediation action",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "relationApiMessage",
          "label": "API message",
          "name": "API message",
          "readable": true,
          "required": false,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "technicalRetryApproved",
          "label": "Retry approved",
          "name": "Retry approved",
          "readable": true,
          "required": true,
          "type": "checkbox",
          "visible": true,
          "writable": true
        }
      ],
      "key": "remediationForm",
      "metadata": {
        "description": "Technical steward action form after Collibra API failure.",
        "key": "remediationForm",
        "modelType": "form",
        "name": "Technical Remediation",
        "version": "1.0.0"
      },
      "name": "Technical Remediation",
      "outcomes": [
        {
          "label": "Retry automation",
          "primary": true,
          "value": "retry_automation"
        },
        {
          "label": "Cancel",
          "primary": false,
          "value": "cancel"
        }
      ]
    },
    "reworkForm": {
      "description": "Requester correction form for rerouted governance requests.",
      "fields": [
        {
          "enabled": true,
          "id": "reworkSummary",
          "label": "Rework summary",
          "name": "Rework summary",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "businessPurpose",
          "label": "Updated business purpose",
          "name": "Updated business purpose",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "consumerAssetId",
          "label": "Updated consumer asset UUID",
          "name": "Updated consumer asset UUID",
          "readable": true,
          "required": false,
          "type": "string",
          "visible": true,
          "writable": true
        }
      ],
      "key": "reworkForm",
      "metadata": {
        "description": "Requester correction form for rerouted governance requests.",
        "key": "reworkForm",
        "modelType": "form",
        "name": "Requester Rework",
        "version": "1.0.0"
      },
      "name": "Requester Rework",
      "outcomes": [
        {
          "label": "Resubmit",
          "primary": true,
          "value": "resubmit"
        },
        {
          "label": "Withdraw",
          "primary": false,
          "value": "withdraw"
        }
      ]
    },
    "securityReviewForm": {
      "description": "Security/privacy review for high-risk or restricted requests.",
      "fields": [
        {
          "enabled": true,
          "id": "securityDecision",
          "label": "Security decision",
          "name": "Security decision",
          "readable": true,
          "required": true,
          "type": "dropdown",
          "values": [
            {
              "label": "Approve",
              "value": "approve"
            },
            {
              "label": "Rework",
              "value": "rework"
            },
            {
              "label": "Reject",
              "value": "reject"
            }
          ],
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "policyExceptionRequired",
          "label": "Policy exception required",
          "name": "Policy exception required",
          "readable": true,
          "required": false,
          "type": "checkbox",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "securityControls",
          "label": "Required controls",
          "name": "Required controls",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        }
      ],
      "key": "securityReviewForm",
      "metadata": {
        "description": "Security/privacy review for high-risk or restricted requests.",
        "key": "securityReviewForm",
        "modelType": "form",
        "name": "Security and Privacy Review",
        "version": "1.0.0"
      },
      "name": "Security and Privacy Review",
      "outcomes": [
        {
          "label": "Submit review",
          "primary": true,
          "value": "submit_review"
        }
      ]
    },
    "stewardTriageForm": {
      "description": "Data steward routing and completeness decision.",
      "fields": [
        {
          "enabled": true,
          "id": "triageDecision",
          "label": "Triage decision",
          "name": "Triage decision",
          "readable": true,
          "required": true,
          "type": "dropdown",
          "values": [
            {
              "label": "Approve",
              "value": "approve"
            },
            {
              "label": "Rework",
              "value": "rework"
            },
            {
              "label": "Reject",
              "value": "reject"
            }
          ],
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "triageNotes",
          "label": "Triage notes",
          "name": "Triage notes",
          "readable": true,
          "required": true,
          "type": "multiLineText",
          "visible": true,
          "writable": true
        },
        {
          "enabled": true,
          "id": "riskRating",
          "label": "Confirmed risk rating",
          "name": "Confirmed risk rating",
          "readable": true,
          "required": true,
          "type": "dropdown",
          "values": [
            {
              "label": "Standard",
              "value": "standard"
            },
            {
              "label": "High",
              "value": "high"
            },
            {
              "label": "Restricted",
              "value": "restricted"
            }
          ],
          "visible": true,
          "writable": true
        }
      ],
      "key": "stewardTriageForm",
      "metadata": {
        "description": "Data steward routing and completeness decision.",
        "key": "stewardTriageForm",
        "modelType": "form",
        "name": "Steward Triage",
        "version": "1.0.0"
      },
      "name": "Steward Triage",
      "outcomes": [
        {
          "label": "Route",
          "primary": true,
          "value": "route"
        }
      ]
    }
  },
  "generatedAt": "2026-05-17T03:55:39.043798+00:00",
  "generator": "DSC Collibra Workflow Automation Agent",
  "metadata": {
    "description": "Generated production candidate package for a complex Collibra governed data product access use case.",
    "footer": "karthik.v",
    "format": "COLLIBRA_WORKFLOW_PACKAGE_WITH_DSC_SIDECAR",
    "name": "Complex Data Product Access Governance",
    "version": "1.0.0"
  },
  "process": "complexDataProductAccessGovernance.bpmn",
  "scripts": {
    "task_CreateRelationAndResponsibility": {
      "elementId": "task_CreateRelationAndResponsibility",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\nimport com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest\nimport com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest\n\nString assetId = execution.getVariable('assetId') as String\nString consumerAssetId = execution.getVariable('consumerAssetId') as String\nString requesterId = execution.getVariable('requesterId') as String\nUUID relationTypeId = UUID.fromString(execution.getVariable('consumerRelationTypeId') as String)\nUUID roleId = UUID.fromString(execution.getVariable('consumerRoleId') as String)\ntry {\n    if (consumerAssetId?.trim()) {\n        relationApi.addRelation(AddRelationRequest.builder()\n            .sourceId(UUID.fromString(assetId))\n            .targetId(UUID.fromString(consumerAssetId))\n            .typeId(relationTypeId)\n            .build())\n    }\n    responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()\n        .resourceId(UUID.fromString(assetId))\n        .roleId(roleId)\n        .ownerId(UUID.fromString(requesterId))\n        .build())\n    execution.setVariable('relationApiSucceeded', true)\n    execution.setVariable('relationApiMessage', 'Relation and responsibility created.')\n} catch (Exception ex) {\n    execution.setVariable('relationApiSucceeded', false)\n    execution.setVariable('relationApiMessage', ex.getMessage())\n}\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_CreateRelationAndResponsibility.groovy"
    },
    "task_NotifyCompletion": {
      "elementId": "task_NotifyCompletion",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = execution.getVariable('requestId') as String\nString finalDecision = (execution.getVariable('finalDecision') ?: 'approved') as String\nString recipient = (execution.getVariable('requesterEmail') ?: execution.getVariable('requesterId') ?: 'requester') as String\nexecution.setVariable('notificationRecipient', recipient)\nexecution.setVariable('notificationSubject', 'Collibra data product access request ' + requestId + ' ' + finalDecision)\nexecution.setVariable('notificationQueued', true)\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_NotifyCompletion.groovy"
    },
    "task_NotifyRejection": {
      "elementId": "task_NotifyRejection",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = execution.getVariable('requestId') as String\nString reason = (execution.getVariable('rejectionReason') ?: execution.getVariable('triageNotes') ?: execution.getVariable('approvalNotes') ?: 'Request rejected by governance review.') as String\nexecution.setVariable('finalDecision', 'rejected')\nexecution.setVariable('notificationSubject', 'Collibra data product access request ' + requestId + ' rejected')\nexecution.setVariable('notificationBody', reason)\nexecution.setVariable('notificationQueued', true)\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_NotifyRejection.groovy"
    },
    "task_OpenPolicyException": {
      "elementId": "task_OpenPolicyException",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\nimport com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest\n\nString requestId = execution.getVariable('requestId') as String\nString assetId = execution.getVariable('assetId') as String\nString controls = (execution.getVariable('securityControls') ?: 'Compensating control review required') as String\nUUID targetAssetId = UUID.fromString(assetId)\nAddAttributeRequest attributeRequest = AddAttributeRequest.builder()\n    .assetId(targetAssetId)\n    .typeId(UUID.fromString(execution.getVariable('policyExceptionAttributeTypeId') as String))\n    .value('Policy exception approved for request ' + requestId + ': ' + controls)\n    .build()\nattributeApi.addAttribute(attributeRequest)\nexecution.setVariable('policyExceptionCreated', true)\nexecution.setVariable('policyExceptionReference', requestId + '-EXCEPTION')\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_OpenPolicyException.groovy"
    },
    "task_RollbackAndNotify": {
      "elementId": "task_RollbackAndNotify",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = execution.getVariable('requestId') as String\nString apiMessage = (execution.getVariable('relationApiMessage') ?: 'Unknown API error') as String\nexecution.setVariable('remediationRequired', true)\nexecution.setVariable('remediationSummary', 'Request ' + requestId + ' requires technical remediation: ' + apiMessage)\nexecution.setVariable('finalDecision', 'technical-remediation')\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_RollbackAndNotify.groovy"
    },
    "task_UpdateAssetStatus": {
      "elementId": "task_UpdateAssetStatus",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\nimport com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest\n\nString assetId = execution.getVariable('assetId') as String\nString statusId = execution.getVariable('approvedStatusId') as String\nChangeAssetRequest request = ChangeAssetRequest.builder()\n    .id(UUID.fromString(assetId))\n    .statusId(UUID.fromString(statusId))\n    .build()\nassetApi.changeAsset(request)\nexecution.setVariable('assetStatusUpdated', true)\nexecution.setVariable('finalDecision', 'approved')\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_UpdateAssetStatus.groovy"
    },
    "task_ValidateRequestContext": {
      "elementId": "task_ValidateRequestContext",
      "elementType": "bpmn:ScriptTask",
      "groovy": "import java.util.UUID\n\nString requestId = (execution.getVariable('requestId') ?: UUID.randomUUID().toString()) as String\nString requester = (execution.getVariable('requesterId') ?: execution.getVariable('initiator') ?: 'unknown-requester') as String\nString assetId = (execution.getVariable('assetId') ?: '') as String\nString purpose = (execution.getVariable('businessPurpose') ?: '') as String\nString riskRating = (execution.getVariable('riskRating') ?: 'standard') as String\nBoolean complete = assetId.trim().length() > 0 && purpose.trim().length() > 15\nexecution.setVariable('requestId', requestId)\nexecution.setVariable('requesterId', requester)\nexecution.setVariable('riskRating', riskRating)\nexecution.setVariable('validationPassed', complete)\nexecution.setVariable('validationMessage', complete ? 'Request context is complete.' : 'Asset and business purpose are required before steward triage.')\n",
      "scriptFormat": "groovy",
      "source": "scripts/task_ValidateRequestContext.groovy"
    }
  },
  "uuidMappings": {
    "approvedStatusId": "00000000-0000-0000-0000-000000000104",
    "consumerRelationTypeId": "00000000-0000-0000-0000-000000000102",
    "consumerRoleId": "00000000-0000-0000-0000-000000000103",
    "policyExceptionAttributeTypeId": "00000000-0000-0000-0000-000000000101"
  },
  "validationRules": [
    "All script tasks must pass Collibra Groovy standards lint and Groovy shell compilation when configured.",
    "Every user task with a flowable:formKey must have a matching .form model.",
    "Every conditional reroute sequence flow must preserve its JUEL condition in BPMN XML.",
    "Exported package must re-import without losing BPMN, scripts, forms, or element properties."
  ]
}