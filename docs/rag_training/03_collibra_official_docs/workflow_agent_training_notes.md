# Collibra Workflow Agent Training Notes

Sources:

- https://developer.collibra.com/workflows/workflow-documentation
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/DesignWorkflows/to_creating-workflows.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/DesignWorkflows/to_using-workflow-designer.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_forms.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Process/ref_activities_script_task.htm
- https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/dto/instance/relation/AddRelationRequest.html
- https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/dto/instance/asset/AddAssetRequest.html
- https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/component/instance/RelationApi.html

## Workflow Design Rules

Collibra workflows are BPMN 2.0 processes deployed as workflow definitions. Workflow Designer apps group the process model and related forms. A production-ready package should preserve the BPMN process, user forms, app metadata, scripts, sequence-flow conditions and deployment variables.

Use pools and lanes to separate requesters, stewards, owners, compliance teams, automation tasks and called workflows. Use start/end events for lifecycle boundaries, user tasks for human review, script tasks for Groovy logic, service/API tasks for automation, gateways for branching, and call activities when a process invokes another workflow.

## Forms

Forms collect input on start events and user tasks. Form field IDs should be stable process variable names. Required fields must match sequence-flow and Groovy expectations. The RAG relation template provides workflow variables, UUID references and relation mappings that generated forms and scripts can use.

## Script Tasks

Script tasks run Groovy. Each script task is independent, so every script must include explicit imports for all Java and Collibra classes it uses. Avoid wildcard imports. Do not rely on methods declared in earlier script tasks. Collibra workflow API variables such as `assetApi`, `relationApi`, `responsibilityApi` and `attributeApi` are available in the workflow context when the corresponding API exists in the tenant/runtime.

## Java API v2 Patterns

Use Java API v2 builder DTOs where possible. Examples:

- `com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest`
- `com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest`
- `com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest`
- `com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest`
- `com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest`

For relations, map source asset UUID, target asset UUID and relation type UUID/public ID from the organization relation workbook. For assets, map domain, asset type, status and display names from organization metadata. For responsibilities, map role IDs and user/group IDs from the workbook.

## Autonomous Agent Expectations

An autonomous run should retrieve relevant RAG chunks before design, inspect organization UUID/relation mappings, generate or repair BPMN, create forms, embed Groovy scripts, compile every script with Java and `/jars/*`, generate business and user tests, apply repairs, export a ZIP and write documentation/test evidence.
