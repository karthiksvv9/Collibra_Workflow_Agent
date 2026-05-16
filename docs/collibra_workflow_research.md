# Collibra Workflow Research Notes

Research date: 2026-05-15

## Primary Sources

- Collibra Workflow overview: https://developer.collibra.com/workflows/workflow-documentation
- Script task reference: https://developer.collibra.com/tutorials/workflow-dynamic-forms/Content/Workflows/WorkflowDesigner/Process/ref_activities_script_task.htm
- Creating workflows and model keys: https://developer.collibra.com/workflows/202402/Content/Workflows/DesignWorkflows/to_creating-workflows.htm
- Designing workflows and Flowable engine: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/DesignWorkflows/to_using-workflow-designer.htm
- Workflow apps/import packaging: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Apps/to_apps.htm
- App import ZIP behavior: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Apps/ta_import-app.htm
- Collibra API task: https://developer.collibra.com/workflows/202402/Content/Workflows/WorkflowDesigner/Process/ref_activities-collibra-api-task.htm
- Service task: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Process/ref_activities_service_task.htm
- Sequence flows: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Process/ref_artifacts_sequence.htm
- Forms: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_forms.htm
- Form property types: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowElements/ref_form-property-types.htm
- Java API v2 package index: https://developer.collibra.com/apis/java/javav2/allpackages-index.html
- AssetApi: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/component/instance/AssetApi.html
- AddAssetRequest: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/dto/instance/asset/AddAssetRequest.html
- RelationApi: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/component/instance/RelationApi.html
- AddRelationRequest: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/dto/instance/relation/AddRelationRequest.html
- WorkflowInstanceApi: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/component/workflow/WorkflowInstanceApi.html

## Workflow Model

Collibra workflows are BPMN 2.0 processes running on Flowable. A workflow app groups one process model and optional forms. The app can be exported/imported as a ZIP; current Workflow Designer imports one process with one or more forms. The process key maps to the BPMN `<process id="...">`; keeping the same key creates a new version, while changing it creates a separate workflow definition.

Recommended modeling pattern:

- One process pool for the workflow.
- One lane per stakeholder or system responsibility. Lanes are visual aids, but they help governance review and ownership.
- One start event and at least one end event.
- User tasks for human review, approval, and data entry.
- Script tasks for Groovy logic that uses Collibra Java API v2 beans already present in workflow context.
- Collibra API tasks for same-environment REST API calls where Java API coverage is insufficient.
- Gateways for explicit routing, especially approval/rejection and error-handling paths.

## Script Task Standards

Script tasks execute Groovy and are independent compilation units. Each script must include its own explicit imports. Avoid wildcard imports because they slow resolution and hide dependency usage. Do not define methods in one script task for later script tasks, because Collibra/Flowable compiles and caches scripts independently.

Workflow script context exposes instantiated API beans such as `assetApi`, `communityTypeApi`, and `fileApi`. The generator therefore emits Java API v2 builder DTO imports and references API beans directly.

Examples encoded in this platform:

- `com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest`
- `com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest`
- `java.util.UUID`
- `execution.getVariable(...)` and `execution.setVariable(...)` for process variables.

## Java API v2 Grounding

The Java API v2 package index contains component, DTO, and model packages for assets, attributes, relations, roles, users, workflows, metadata types, and more. Relevant signatures observed:

- `AssetApi.addAsset(AddAssetRequest)` creates an asset.
- `AssetApi.findAssets(FindAssetsRequest)` searches assets.
- `AddAssetRequest.builder()` supports `name`, `displayName`, `domainId`, `typeId`, `typePublicId`, and related properties.
- `RelationApi.addRelation(AddRelationRequest)` creates source-target relations.
- `AddRelationRequest.builder()` supports `sourceId`, `targetId`, `typeId`, and `typePublicId`.
- `WorkflowInstanceApi.startWorkflowInstances(StartWorkflowInstancesRequest)` starts workflows.

The RAG corpus and `/jars` folder are treated as higher-priority than heuristics when resolving imports and method signatures.

## Forms And Variables

Workflow Designer uses JSON-based form definitions for forms, while older form properties remain for configuration variables/backwards compatibility. Form property IDs become workflow variable names and must avoid special characters. Supported/default types include string, long, boolean, date, enum, and custom types such as textarea, checkbox, dynamic enum, file upload, asset, and role/user-style dropdowns.

Generation rules:

- Keep variable IDs stable and code-friendly.
- Use form references for user tasks.
- Use form properties primarily for configuration variables.
- Use `execution.getVariable("fieldId")` in script tasks.
- Include required/default values for deployment-time configuration.

## Collibra API Task Behavior

Collibra API tasks call same-environment Collibra REST APIs and handle authentication. They are asynchronous. Response status codes, including 4xx/5xx, are treated as successful unless configured. For reliable workflows, use "Handle status codes" with boundary error events instead of only failing status codes, because asynchronous failure can halt progress.

The platform models this as a task type but defaults to Groovy script tasks for Java API v2 operations because local JAR compilation can validate imports and DTO usage.

## Sequence Flow Behavior

Sequence flows connect BPMN elements and define routing. A flow has one source, one target, a display name, optional documentation, optional condition expression, optional skip expression, and optional execution listener behavior. Conditions should be explicit JUEL/Flowable expressions such as `${approvalDecision == 'approve'}`. For gateway-driven routing, use named outgoing paths and a default path for "otherwise" cases, because default flows are easier to audit than implicit fall-through behavior.

The React designer treats sequence flows as selectable first-class elements. Users can edit:

- Normal flow metadata.
- Conditional flow expressions.
- Default flow behavior.
- Skip expressions.
- Transition listener Groovy snippets, compiled through the same Groovy validation endpoint as script-task code.

## RAG Relation Mapping Requirements

Organization-specific workflows depend on local metadata maps. The ingestion pipeline must therefore extract more than free text:

- Excel headers and row values.
- UUID-like values, keyed by normalized column names.
- Source/target/relation-type columns into semantic relation triples.
- Asset/role ownership columns into responsibility triples.
- BPMN node IDs, lanes, sequence flows, scripts, and form keys.
- XML schema IDs and element relationships.
- `.form` and `.app` JSON manifest keys.

These extracted relations are included beside vector retrieval so the agent can reason with exact UUIDs, relation type public IDs, asset type public IDs, roles, and process topology.

## Deployment Package Assumption

The generated ZIP contains:

- `<processKey>.bpmn`
- one or more `<formKey>.form`
- `<processKey>.app` manifest

Collibra package requirements have changed across Workflow Designer versions; before production upload, validate the package in a non-production Collibra environment and adjust the manifest naming/metadata if your tenant expects a version-specific layout.
