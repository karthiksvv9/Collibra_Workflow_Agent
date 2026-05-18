# Collibra Form Builder Training Notes

Source set:

- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_forms.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_forms-editor.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_form-canvas.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/ta_create-forms.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_form-examples.htm
- https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowElements/ref_form-properties.htm
- https://developer.collibra.com/tutorials/workflow-dynamic-forms/Content/Workflows/WorkflowDesigner/Forms/to_form-components.htm

## Agent Rules

- Treat `.form` files as JSON-based Collibra Workflow Designer form definitions.
- Link forms to start events and user tasks through form references/form keys.
- Preserve form IDs, labels, required flags, outcomes, visibility/enabled rules, layout rows, and column widths during import/export.
- Prefer form references for new workflows. Use legacy form properties only for backwards compatibility.
- Form canvas layout is a 12-column grid. Preserve row and column placement where available.
- Collibra data-entry form components can store values as strings. Groovy scripts should convert string UUID values with Collibra workflow helper functions or `UUID.fromString` where appropriate.
- Generated test cases must validate required fields, outcomes, field IDs, linked user tasks, and sequence-flow variables that depend on form values.
