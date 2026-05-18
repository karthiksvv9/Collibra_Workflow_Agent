# RAG Training Folder Layout

Place organization-specific knowledge in this folder and click **Generate Index / Train RAG** or **Incremental Reindex** in the UI.

## Folders

- `00_templates`: Excel templates for UUIDs, relation mappings, workflow variables, roles, statuses and called workflow keys.
- `01_user_dropzone`: user-managed files: `.xlsx`, `.docx`, `.pdf`, `.xml`, `.bpmn`, `.form`, `.app`, `.zip`, `.md`, `.json`.
- `02_ootb_workflows`: Collibra out-of-the-box workflow ZIP/BPMN/form/app examples copied from `C:\Users\Mohith\Downloads\OOTB-workflows-dgc`.
- `03_collibra_official_docs`: scraped/curated Collibra workflow and Java API documentation notes.
- `04_organization_standards`: local naming standards, Groovy standards, approval matrices, role rules and deployment procedures.
- `05_generated_training`: generated scenario packages, known-good workflow outputs and reusable test evidence.

Use `00_templates/Collibra_Relation_UUID_Template.xlsx` as the organization metadata template. The RAG relation mapper reads UUID mappings, source-target asset relations, relation type IDs, role mappings and workflow keys from that workbook shape.

## Incremental Training

Add files to any folder, then use **Incremental Reindex** in the UI. The vector store upserts chunks by source file and keeps the latest content available for autonomous workflow generation.
