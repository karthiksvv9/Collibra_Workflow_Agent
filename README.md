# DSC Collibra Workflow Automation Agent

Production workbench for designing, importing, repairing, testing, documenting, and exporting Collibra BPMN workflow packages. The platform combines a local relation-aware RAG engine, a FastAPI automation backend, a bpmn-js React canvas, Groovy standards validation, Collibra form/app parsing, and repeatable package quality loops.

Footer credit in the browser workbench: `karthik.v`.

## Current Production Scenario

The generated end-to-end validation scenario is:

`Complex Data Product Access Governance`

It is stored at:

- Package ZIP: `output/complex-data-product-access-governance-production.zip`
- Working folder: `output/complex-data-product-access-governance`
- BPMN: `output/complex-data-product-access-governance/complexDataProductAccessGovernance.bpmn`
- App sidecar: `output/complex-data-product-access-governance/complexDataProductAccessGovernance.app`
- Forms: `output/complex-data-product-access-governance/forms/*.form`
- Scripts: `output/complex-data-product-access-governance/scripts/*.groovy`
- Test report: `output/complex-data-product-access-governance/test-report.json`
- Workbench documentation: `output/complex-data-product-access-governance/docs/production-workbench-documentation.md`

The scenario contains 6 swimlanes, 23 BPMN elements, 31 sequence flows, 6 Collibra forms, and 7 Groovy script tasks. It covers requester rework, steward triage, business approval, security/privacy review, policy exception creation, Collibra Java API automation, API failure remediation, completion notification, and rejection reroutes.

## Prompt-Driven AI Scenario

The agent was also tested from a master prompt alone, using the prompt analysis plus local RAG fallback path. The generated workflow includes multiple forms, conditional sequence flows, requester rework reroutes, Collibra Java API Groovy script tasks, and a BPMN call activity that invokes a downstream provisioning workflow.

Prompt-driven artifacts:

- Build ZIP: `output/prompt_driven_ai_complex_workflow.zip`
- Final workbench export: `output/prompt-driven-ai-complex-workflow/prompt-driven-ai-complex-workflow-final.zip`
- Prompt: `output/prompt-driven-ai-complex-workflow/prompt.txt`
- Documentation: `output/prompt-driven-ai-complex-workflow/prompt-driven-workflow-documentation.md`
- Test evidence: `output/prompt-driven-ai-complex-workflow/test-report.json`
- Comparison with the earlier sample: `output/prompt-driven-ai-complex-workflow/comparison-with-sample.json`

Prompt-driven validation result:

- Nodes: 23
- Sequence flows: 31
- Forms: 6
- Script tasks extracted: 6
- Call activities: 1
- Missing forms: 0
- Autonomous package quality loop: passed
- AI-generated test cases: 5
- User-authored test cases: 5
- Passed cases: 10
- Failed cases: 0

## What Is Included

- Python/FastAPI backend for RAG, package import/export, Groovy validation, workflow testing, documentation, and simulation.
- React + bpmn-js workbench with native BPMN canvas behavior for pools, swimlanes, tasks, gateways, sequence flows, import, export, forms, properties, and console panels.
- Central `config.yaml` for paths, model names, custom API-gateway settings, runtime concurrency, Groovy executable/classpath, and Collibra documentation seeds.
- RAG ingestion for `.docx`, `.pdf`, `.xlsx`, `.xml`, `.bpmn`, `.bpmn20.xml`, `.app`, `.form`, `.groovy`, `.json`, `.csv`, `.txt`, and `.md`.
- Relation mapping for Excel UUID columns, relation matrices, BPMN nodes/flows, XML schemas, and Collibra app/form metadata.
- SQLite vector store using OpenAI embeddings when configured and deterministic local hashing embeddings when no API key is present.
- Collibra package importer that extracts real embedded Groovy from BPMN script tasks, parses `.form` files, reads `.app` metadata, maps sequence-flow conditions, and preserves element properties.
- Autonomous package quality loop for BPMN structure, linked forms, missing scripts, Groovy standards lint, Groovy shell compilation when installed, and deterministic repair.
- AI and user test-case runner that generates business test cases from the use case and executes them alongside user-authored scenarios.
- Clean project packaging that excludes installation media and heavy dependency folders.

## Folder Structure

```text
.
|-- config.yaml
|-- run_all.ps1
|-- requirements.txt
|-- pyproject.toml
|-- README.md
|-- docs
|   |-- collibra_workflow_research.md
|   |-- collibra_api_v2_reference.md
|   |-- workflow_designer_components.md
|   `-- rag_training
|-- jars
|   `-- licensed Collibra/Groovy dependency JARs go here
|-- output
|   |-- vector_store.sqlite3
|   |-- complex-data-product-access-governance-production.zip
|   `-- complex-data-product-access-governance
|-- src
|   |-- agents
|   |-- api
|   |-- core
|   |-- rag
|   |-- ui
|   |   |-- src
|   |   |-- package.json
|   |   `-- vite.config.js
|   `-- workflow
|-- tests
`-- .venv / node_modules are local-only and excluded from clean deliverables
```

## Architecture

### Backend

The backend starts in `src.main` and exposes API routes from `src/api/server.py`. It serves the browser UI from `src/ui`, receives package uploads, manages RAG indexing, validates BPMN, compiles/lints Groovy, simulates paths, and streams generated ZIP files.

Key modules:

- `src/core/config.py`: loads `config.yaml`, environment overrides, paths, model names, runtime worker counts, Groovy settings, and Collibra documentation URLs.
- `src/rag/engine.py`: orchestrates document loading, chunking, embeddings, vector storage, and retrieval.
- `src/rag/documents.py`: loads supported file formats.
- `src/rag/relation_mapper.py`: extracts semantic relations from Excel, XML, BPMN, form, and app artifacts.
- `src/agents/workflow_agent.py`: prompt-to-workflow generation path.
- `src/agents/groovy_compiler.py`: standards lint plus optional Groovy shell parse using `/jars`.
- `src/agents/standards.py`: Collibra Groovy standards checks.
- `src/workflow/bpmn.py`: BPMN model serialization/parsing.
- `src/workflow/package.py`: package round-trip support.
- `src/workflow/simulator.py`: local path simulation.
- `src/workflow/scenario_generator.py`: repeatable complex production scenario generator.

### UI

The production UI lives under `src/ui/src`.

Key components:

- `BpmnAgentCanvas.jsx`: bpmn-js modeler shell, import/export, selected element handling, console, and footer.
- `BlockLibrary.jsx`: BPMN blocks, gateways, events, pools, lanes, and connector tooling.
- `CollibraPropertiesPanel.jsx`: selected BPMN element metadata, form key, Groovy editor, AI code generation, and compile action.
- `FormsPanel.jsx`: parsed Collibra form preview, outcomes, fields, and properties.
- `RagPanel.jsx`: upload, train/index, search, and RAG chat.
- `RunConsole.jsx`: autonomous package tests and AI + user test-case execution.
- `DocumentationPanel.jsx`: AI/workbench documentation generation.
- `RightDock.jsx` and `FloatingPanel.jsx`: resizable/floating Eclipse-style workspace panels.
- `AutonomousAgentModal.jsx`: one-click autonomous mode for either a long prompt or the current/imported canvas.

### RAG

The RAG layer is local-first. It uses deterministic hashing embeddings by default, which keeps ingestion/test flows usable offline and on non-admin laptops. If a tenant-approved embeddings endpoint is added later, enable it in `config.yaml`.

RAG responsibilities:

- Load official Collibra workflow/API docs and organization-specific files.
- Extract chunk-level text for retrieval.
- Extract structured relations such as UUID columns, source-target asset relations, role mappings, BPMN task references, forms, sequence flows, and script-task metadata.
- Return context to the workflow/code/documentation agent so generated Groovy and BPMN properties follow local standards.

### Groovy Validation

The compile loop has two stages:

1. Static Collibra standards lint:
   - no wildcard imports
   - explicit Collibra Java API imports when Collibra classes are used
   - process variables should be read/written
   - stdout logging is warned

2. Groovy shell parse:
   - uses `groovy.executable` from `config.yaml`
   - uses `groovy.default_classpath`, normally `./jars/*`
   - if `groovy.exe` is not installed, the compiler falls back to `java` plus Apache Groovy runtime JARs in `jars`
   - Collibra API imports compile against the licensed Collibra JARs you place in `jars`
   - if neither `groovy.exe` nor Java can be found, syntax compilation is skipped after static lint

When a user clicks Compile in the canvas, the backend can now run an organization-aware repair loop. The loop retrieves RAG evidence from organization standards, previous workflow ZIPs, relation/UUID sheets, form metadata, and OOTB examples; applies deterministic Collibra fixes such as replacing `UUID.fromString(...)` with `string2Uuid(...)`; and, when an AI model key is configured, asks the selected model to repair the script using the exact compiler error. The UI shows passed, failed, or skipped status, the compiler error text, repair attempts, and automatically updates the script editor when a repaired version is produced.

The Java-only fallback uses:

```text
java -cp ./jars/* org.codehaus.groovy.tools.FileSystemCompiler
```

The required Apache Groovy runtime JARs can be refreshed with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download_groovy_jars.ps1
```

## Configuration

All tunable values belong in `config.yaml`.

Important sections:

```yaml
models:
  chat_model: gpt-5-4-2026-03-05
  embedding_model: text-embedding-3-large
  embedding_provider: hashing
  available_chat_models:
    - id: openai-gpt-4-1-nano-direct
      label: ChatGPT GPT-4.1 Nano (Direct OpenAI)
      provider: openai_chat_completions
      model: gpt-4.1-nano
      base_url: https://api.openai.com
      chat_completions_path: /v1/chat/completions
      api_key: ""   # optional private-server value; otherwise use OPENAI_API_KEY
      api_key_env: OPENAI_API_KEY
      api_key_header: Authorization
      api_key_prefix: "Bearer "
      max_output_tokens: 1000
    - id: openai-gpt-5-4
      label: OpenAI GPT-5.4
      provider: custom_chat_completions
      api_key: ""   # optional private-server value; otherwise use AI_GATEWAY_API_KEY
      api_key_env: AI_GATEWAY_API_KEY
    - id: claude-opus-4-6
      label: Claude Opus 4.6
      provider: custom_messages
      api_key: ""   # optional private-server value; otherwise use CLAUDE_API_KEY
      api_key_env: CLAUDE_API_KEY
    - id: gemini-3-1-pro
      label: Gemini 3.1 Pro Preview
      provider: gemini_generate_content
      api_key: ""   # optional private-server value; otherwise use GEMINI_API_KEY
      api_key_env: GEMINI_API_KEY

openai:
  provider: custom_chat_completions
  api_key: ""
  api_key_env: AI_GATEWAY_API_KEY
  api_key_header: X-API-Key
  api_key_prefix: ""
  base_url: https://iapi-test.proj.com/gpt/v2
  chat_completions_path: /gpt-5-4-2026-03-05/chat/completions
  embedding_enabled: false

paths:
  docs_dir: ./docs/rag_training
  rag_templates_dir: ./docs/rag_training/00_templates
  rag_user_dropzone_dir: ./docs/rag_training/01_user_dropzone
  rag_ootb_workflows_dir: ./docs/rag_training/02_ootb_workflows
  rag_official_docs_dir: ./docs/rag_training/03_collibra_official_docs
  rag_organization_standards_dir: ./docs/rag_training/04_organization_standards
  rag_generated_training_dir: ./docs/rag_training/05_generated_training
  relation_template_file: ./docs/rag_training/00_templates/Collibra_Relation_UUID_Template.xlsx
  jars_dir: ./jars
  output_dir: ./output
  vector_store: ./output/vector_store.sqlite3

runtime:
  max_workers: 10
  use_multiprocessing: true
  use_multithreading: true

groovy:
  executable: groovy
  java_executable: java
  use_embedded_jars: true
  java_options:
    - "-Xms32m"
    - "-Xmx384m"
    - "-XX:ReservedCodeCacheSize=96m"
  compile_timeout_seconds: 20
  default_classpath:
    - ./jars/*
```

Do not hard-code API keys, paths, model IDs, JAR locations, or worker settings in source files. Put them in `config.yaml` or environment variables.

## API Gateway

The UI model dropdown reads `models.available_chat_models` from `config.yaml`, and the selected model is used for RAG chat, BPMN design, Groovy generation/repair, autonomous mode and documentation. Each profile uses only its own `api_key` or environment variable, so an OpenAI key is not reused for Claude, Gemini, or a gateway profile.

There are two supported ways to provide a key:

1. Private server config:
   Edit the selected profile in `config.yaml` and paste the key into `api_key: "..."`.

2. Shell/runtime prompt:
   Leave `api_key: ""` blank and set the matching environment variable before launch, or use the non-admin launcher prompt.

The `/api/models` endpoint never returns `api_key`, even when a key is stored in a private server copy of `config.yaml`.

Direct OpenAI test model:

- Model: `gpt-4.1-nano`
- URL: `https://api.openai.com/v1/chat/completions`
- Auth header: `Authorization: Bearer <OPENAI_API_KEY>`
- Payload style: `messages`, `max_tokens`, optional JSON response format

Set the direct OpenAI key for the current PowerShell session:

```powershell
$env:OPENAI_API_KEY = "paste-openai-key-here"
```

Or prompt for it while starting the localhost server:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1 -ApiKeyEnv OPENAI_API_KEY
```

The approved chat-completions gateway profile uses this shape:

- Model: `gpt-5-4-2026-03-05`
- URL shape: `https://iapi-test.proj.com/gpt/v2/gpt-5-4-2026-03-05/chat/completions`
- Auth header: `X-API-Key`
- Payload style: `messages` plus `max_completion_tokens`

Do not commit the API key. Set it for the current PowerShell session:

```powershell
$env:AI_GATEWAY_API_KEY = "paste-approved-key-here"
```

The non-admin start script can also prompt for keys securely and pass them only to the localhost server process. Never paste real keys into Git, screenshots, `README.md`, source code, test files, or `config.yaml`.

Set `CLAUDE_API_KEY` before selecting Claude, and set `GEMINI_API_KEY` before selecting Gemini. Token usage is tracked in `output/token_usage.xlsx`; human-readable and JSONL API actions are logged under `output/action_logs/`.

Prompt examples:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1 -ApiKeyEnv AI_GATEWAY_API_KEY
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1 -ApiKeyEnv CLAUDE_API_KEY
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1 -ApiKeyEnv GEMINI_API_KEY
```

## Run Locally

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Serve -StopExisting
```

Open:

```text
http://127.0.0.1:8088/ui/index.html
```

Useful runner modes:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Setup
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Test
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Build
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Serve -NoBrowser
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode All -StopExisting
```

The user is responsible for installing Python, Node.js, Java, and licensed Collibra Java API/runtime JARs. A separate Groovy installation is optional because the compiler can run Groovy scripts through Java plus the Apache Groovy JARs in `jars`. The clean deliverable intentionally does not include installation media or dependency folders.

## Non-Technical Setup Guide

Use this section if you only want to start the tool and work in the browser.

### What You Need

- The project folder on your laptop.
- Python 3.11 or newer.
- Node.js 20 or newer.
- Java 17 or newer, or a bundled Java runtime from tools such as PyCharm/IntelliJ.
- Your approved API key for the gateway in `AI_GATEWAY_API_KEY`.
- Collibra/Groovy JAR files already placed in the `jars` folder.

Do not paste the API key into Git, README, screenshots, code, or `config.yaml`.

### Option A: Office Laptop Without Admin Permission

This is the recommended path for a locked-down corporate laptop.

1. Open the project folder in File Explorer.
2. Click the address bar at the top of File Explorer.
3. Type `powershell` and press Enter. A PowerShell window opens in the correct folder.
4. Run the requirement check:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_non_admin_requirements.ps1
```

5. If the check says Python, Node.js, npm, Java, workspace write access, and JAR folder are OK, start the tool:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1
```

6. When prompted for `AI_GATEWAY_API_KEY`, paste your approved API key and press Enter.
7. The script starts the app at:

```text
http://127.0.0.1:8088/ui/index.html
```

You can also run the simpler launcher:

```cmd
scripts\start_localhost_non_admin.cmd
```

What this script does:

- Creates a local `.venv` Python environment inside this project.
- Installs Python packages only into `.venv`, not into Windows globally.
- Installs UI packages under `src/ui/node_modules`, not globally.
- Builds the browser UI.
- Keeps the API key only in the current server process environment.
- Starts the backend on localhost only, not on the public network.

### Setting The API Key Without Admin Permission

Temporary setup for the current PowerShell window:

```powershell
$env:AI_GATEWAY_API_KEY = "paste-approved-key-here"
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1
```

User-level setup that survives restart and does not require admin:

```powershell
[Environment]::SetEnvironmentVariable("AI_GATEWAY_API_KEY", "paste-approved-key-here", "User")
```

After running that command, close PowerShell and open a new PowerShell window so Windows reloads the variable.

To remove the key later:

```powershell
[Environment]::SetEnvironmentVariable("AI_GATEWAY_API_KEY", $null, "User")
```

### Setting Java Without Admin Permission

First run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_non_admin_requirements.ps1
```

If Java is found, you do not need to change anything. The checker searches common locations, including bundled JetBrains/PyCharm Java runtimes.

If Java is not found but you know where `java.exe` is, set it temporarily:

```powershell
$env:JAVA_HOME = "C:\Path\To\Java"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
powershell -ExecutionPolicy Bypass -File .\scripts\start_localhost_non_admin.ps1
```

Example using a PyCharm bundled Java runtime:

```powershell
$env:JAVA_HOME = "C:\Program Files\JetBrains\PyCharm 2025.3.1.1\jbr"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
```

To avoid typing this every time, update `config.yaml`:

```yaml
groovy:
  java_executable: "C:/Program Files/JetBrains/PyCharm 2025.3.1.1/jbr/bin/java.exe"
```

Use forward slashes in YAML paths. They work on Windows and avoid escaping issues.

### Option B: Laptop With Admin Permission

Use this path if you are allowed to install software normally.

1. Install Python 3.11 or newer.
2. Install Node.js 20 or newer.
3. Install Java 17 or newer.
4. Optional: Install Groovy. This is not required because the app can run Groovy compilation through Java plus JARs in `jars`.
5. Open PowerShell as a normal user. Admin PowerShell is not required after installation.
6. Go to the project folder:

```powershell
cd "C:\Users\Mohith\Documents\Codex\2026-05-15\role-you-are-a-senior-principal"
```

7. Set the API key for your user:

```powershell
[Environment]::SetEnvironmentVariable("AI_GATEWAY_API_KEY", "paste-approved-key-here", "User")
```

8. Close PowerShell and open a new PowerShell window.
9. Confirm requirements:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_non_admin_requirements.ps1
```

10. Start the app:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Serve -StopExisting
```

11. Open:

```text
http://127.0.0.1:8088/ui/index.html
```

### Setting Java With Admin Permission

If Java is installed normally, set `JAVA_HOME` as a user or system environment variable.

User-level Java path:

```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-17", "User")
```

System-level Java path, only if your company allows it:

```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-17", "Machine")
```

Then add Java to `Path` through Windows Environment Variables, or set the exact Java executable in `config.yaml`:

```yaml
groovy:
  java_executable: "C:/Program Files/Eclipse Adoptium/jdk-17/bin/java.exe"
```

### Common First Run Issues

- If PowerShell blocks scripts, use `-ExecutionPolicy Bypass` exactly as shown.
- If port `8088` is already in use, run with `-StopExisting` or choose another port:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Serve -Port 8090 -StopExisting
```

- If `AI_GATEWAY_API_KEY` is missing, run the non-admin start script and paste the key when prompted.
- If Java is missing, install Java, use a bundled Java runtime, or set `groovy.java_executable` in `config.yaml`.
- If npm install fails because of corporate certificates, ask IT for the corporate root CA setup for Node.js, or run from a corporate-approved terminal profile.
- If Python package install fails because of corporate certificates, ask IT for the corporate root CA setup for Python/pip. Do not disable TLS verification for production use.

## Operating Procedure

1. Place licensed Collibra JARs under `jars`.
2. Use `docs/rag_training/00_templates/Collibra_Relation_UUID_Template.xlsx` for organization UUIDs, roles, statuses, relation type IDs, called workflow keys, and column-to-column relation mappings.
3. Add organization standards, exported Collibra workflows, forms, apps, BPMN XML, relation sheets, UUID mapping Excel files, PDFs, DOCX files, and markdown procedures under `docs/rag_training/01_user_dropzone` or the relevant training subfolder.
4. Keep Collibra OOTB packages under `docs/rag_training/02_ootb_workflows`; this repo includes the local DGC OOTB workflow ZIPs copied from `C:\Users\Mohith\Downloads\OOTB-workflows-dgc`.
5. Keep official Collibra workflow/API documentation mirrors under `docs/rag_training/03_collibra_official_docs` and `docs/rag_training/collibra_official`.
6. Confirm `config.yaml` paths, OpenAI API settings, model settings, worker counts, and Groovy/JAR classpath settings.
7. Start the workbench with `run_all.ps1`.
8. Open the RAG panel.
9. Upload additional documents if needed.
10. Click `Generate Index / Train RAG` for a full rebuild or `Incremental Reindex` after adding files.
11. Use `Autonomous Agent Mode` for a full prompt-to-package run or a full repair/test/export run on the current imported canvas.
12. Select BPMN elements to edit forms, script-task Groovy, task owners, candidate groups, and sequence-flow conditions.
13. Use `Compile selected` for targeted script validation.
14. Use `Test all` for BPMN/forms/scripts/package validation.
15. Use `Run AI + user tests` to combine generated business cases with user scenarios.
16. Use `Docs` to generate workflow implementation/test documentation.
17. Export the final package ZIP and validate it in a non-production Collibra tenant.

## API Reference

Workbench endpoints:

- `POST /api/workflow/import`: import `.zip`, `.bpmn`, `.bpmn20.xml`, `.xml`, `.form`, or `.app`; returns BPMN XML, forms, scripts, element properties, diagnostics, and warnings.
- `POST /api/workflow/export`: export current BPMN, app sidecar, forms, and scripts as ZIP.
- `POST /api/workflow/test-package`: run autonomous package quality loop across BPMN, forms, scripts, and compile/lint results.
- `POST /api/workflow/test-cases`: run package quality plus generated business test cases and user-authored test cases.
- `POST /api/workflow/documentation`: generate markdown documentation for current BPMN/app/forms.
- `POST /api/run/simulate`: simulate BPMN path with supplied variables.
- `POST /api/compile/groovy`: lint/compile one Groovy script.
- `POST /api/validate/sequence-flow`: validate condition, skip expression, and listener Groovy for a sequence flow.
- `POST /api/agent/design`: generate BPMN, forms, app model, and scripts from a prompt.
- `POST /api/agent/generate-code`: generate Groovy guidance/code for one selected BPMN element.
- `POST /api/agent/autonomous-run`: run the prompt/canvas autonomous loop: retrieve RAG, design or load BPMN, compile/lint scripts, repair deterministic issues, run generated and user test cases, create documentation, and write an export ZIP/report.
- `POST /api/ai/enhance`: generate a targeted patch for a block or sequence flow.

RAG endpoints:

- `GET /api/rag/status`: current document, chunk, relation, vector, UUID, and table counts.
- `GET /api/rag/template`: download the organization relation/UUID Excel template.
- `POST /api/rag/upload`: upload files to the RAG corpus without indexing.
- `POST /api/rag/ingest`: upload files and index immediately.
- `POST /api/rag/index`: rebuild/index local RAG corpus.
- `POST /api/rag/reindex`: incremental reindex route.
- `POST /api/rag/query`: retrieve top matching chunks.
- `POST /api/rag/chat`: return a RAG-grounded answer/context block.

Official Collibra form-builder sources mirrored into RAG include:

- [Forms](https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_forms.htm)
- [Form editor](https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_forms-editor.htm)
- [Form canvas](https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_form-canvas.htm)
- [Create a new form](https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/ta_create-forms.htm)
- [Form examples](https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Forms/to_form-examples.htm)
- [Form properties](https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowElements/ref_form-properties.htm)
- [Form components](https://developer.collibra.com/tutorials/workflow-dynamic-forms/Content/Workflows/WorkflowDesigner/Forms/to_form-components.htm)

Legacy compatibility endpoints:

- `POST /api/ingest`
- `POST /api/retrieve`
- `POST /api/workflows/build`
- `POST /api/workflows/debug`
- `POST /api/workflows/repair`
- `POST /api/workflows/simulate`
- `POST /api/documentation/generate`
- `POST /api/docs/scrape`
- `GET /api/workflows/download?path=...`

## RAG Data Rules

Keep RAG data, source code, configs, tests, and generated Collibra packages. Exclude local installation media and generated dependency folders.

Keep:

- `docs/**`
- `docs/rag_training/**`
- `output/vector_store.sqlite3`
- source code under `src/**`
- tests under `tests/**`
- generated scenario package and scenario evidence under `output/complex-data-product-access-governance*`
- `config.yaml`, `README.md`, `requirements.txt`, `pyproject.toml`, `run_all.ps1`, UI package manifests

Exclude:

- `.venv/**`
- `node_modules/**`
- `.pytest_cache/**`
- `__pycache__/**`
- `.git/**`
- `*.exe`, `*.msi`, `*.iso`, installer bundles, downloaded software media
- old ad-hoc smoke screenshots/logs unless needed for an audit

## Complex Scenario Validation

The latest generated scenario was validated through the same backend API used by the UI.

Result:

- Import: passed
- BPMN selected: `complexDataProductAccessGovernance.bpmn`
- Forms extracted: 6
- Script tasks detected: 7
- Embedded Groovy scripts extracted: 7
- User tasks detected: 6
- Sequence flows detected: 31
- Missing form definitions: 0
- Autonomous package quality loop: passed
- Blocking issues: 0
- AI-generated test cases: 5
- User-authored test cases: 5
- Passed cases: 10
- Failed cases: 0

The detailed JSON evidence is in `output/complex-data-product-access-governance/test-report.json`.

## Generate The Scenario Again

```powershell
.\.venv\Scripts\python.exe -m src.workflow.scenario_generator
```

This recreates:

- `output/complex-data-product-access-governance-production.zip`
- `output/complex-data-product-access-governance/complexDataProductAccessGovernance.bpmn`
- generated forms, scripts, app metadata, and scenario docs

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend build:

```powershell
Set-Location src\ui
npm run build
```

Current automated tests cover:

- RAG ingestion and retrieval
- ZIP workflow ingestion into RAG text/relation mapping
- Excel UUID/relation mapping
- Groovy standards linting
- Custom chat-completions gateway URL/header/payload handling
- Java-only Groovy compilation with temporary Collibra dependency stubs for missing local runtime extension JARs
- BPMN/form package round trip
- Collibra OOTB-style workflow import behavior
- unsafe ZIP member rejection
- Autonomous Agent Mode on an imported workflow
- complex generated scenario import, form extraction, script extraction, package quality loop, and AI/user test-case execution

## Security

Security notes are maintained in `docs/security-hardening.md`.

Before publishing to Git, run:

```powershell
rg -n "API_KEY|AI_GATEWAY_API_KEY|X-API-Key|sk-|secret|password|token" .
```

Expected matches should be documentation, config keys, tests, or code references only. The actual API key must not appear in any tracked file.

## Deployment Notes

For a production Collibra environment:

1. Put tenant-specific UUID mappings, role mappings, status IDs, relation type IDs, responsibility role IDs, domain/community IDs, and attribute type IDs into RAG training files and/or `config.yaml`.
2. Place Collibra Java API v2 JARs and workflow runtime JARs under `jars`.
3. Run RAG indexing after every standards or metadata update.
4. Generate or import workflow.
5. Run package quality, AI/user test cases, and documentation.
6. Export ZIP.
7. Upload to a non-production Collibra tenant.
8. Execute tenant integration testing with real API credentials and real assets.
9. Promote only after Groovy shell compilation and tenant execution both pass.

## Troubleshooting

- If Groovy compile is skipped, install Groovy and confirm `groovy.executable` in `config.yaml`.
- If Groovy compile is skipped but Java is installed, set `groovy.java_executable` to the full `java.exe` path or put Java on PATH.
- If embedded Groovy classes are missing, run `.\scripts\download_groovy_jars.ps1`.
- If Collibra imports fail during compile, add licensed Collibra Java API/runtime JARs to `jars`.
- If forms do not render after import, check `appModel.importDiagnostics.missingForms` and verify `.form` keys match `flowable:formKey`.
- If sequence flows do not route, check the selected flow condition in the properties panel and validate with `/api/validate/sequence-flow`.
- If RAG answers are weak, add more official docs, exported workflows, UUID sheets, and organization standards under `docs/rag_training`, then reindex.
- If package size is too large, create the clean deliverable ZIP described below instead of sharing the working folder.

## Clean Deliverable

The clean deliverable is generated under `output/collibra-workflow-agent-clean-production.zip`. It contains source, tests, config, README, scripts, RAG data, vector store, the validated generated sample package, the validated prompt-driven workflow package, Apache Groovy runtime JARs, and the Collibra JARs currently present in `jars`. It excludes installation media, `.venv`, `node_modules`, caches, and unrelated old output artifacts.

