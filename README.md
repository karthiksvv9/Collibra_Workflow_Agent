# DSC Collibra Workflow Automation Agent

Production-shaped platform for designing, validating, simulating, and packaging Collibra BPMN workflows with a relation-aware RAG engine and Groovy self-healing loop.

## What Is Included

- Python backend with FastAPI endpoints and static browser canvas.
- Centralized `config.yaml` for models, paths, concurrency, Groovy, and Collibra documentation seeds.
- RAG ingestion for `.docx`, `.pdf`, `.xlsx`, `.xml`, `.bpmn`, `.app`, `.form`, `.json`, `.txt`, and `.md`.
- Excel/XML/BPMN relation mapping for UUIDs, source-target relations, asset ownership, BPMN nodes, and sequence flows.
- SQLite vector store with OpenAI embeddings when `OPENAI_API_KEY` is set and deterministic local embeddings otherwise.
- Agentic workflow builder that designs BPMN, forms, Groovy scripts, package manifests, and local simulations.
- Groovy compile loop that uses `/jars` classpath and validates explicit Collibra Java API v2 imports.
- React Flow designer with connectable BPMN blocks, selectable/editable sequence flows, Collibra-specific task templates, import/export support for `.bpmn` and generated `.zip` packages.
- Resizable/floating workbench panels, pool/lane editing, debug/AI-fix loop for imported workflows, and AI-generated workflow documentation.
- Explicit connector tools: `Sequence Flow`, `Conditional Flow`, and `Default Flow`. Pick a connector, click the source block, then click the target block to create an editable BPMN sequence flow.

## Folder Structure

```text
.
├── config.yaml
├── docs
│   ├── collibra_workflow_research.md
│   └── rag_training
├── jars
├── output
├── src
│   ├── agents
│   ├── api
│   ├── core
│   ├── rag
│   ├── ui              # React/Vite workflow designer
│   └── workflow
└── tests
```

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="sk-..."
python -m src.main
```

Open `http://127.0.0.1:8088/ui/index.html`.

If `OPENAI_API_KEY` is not set, the platform still runs with deterministic local embeddings and heuristic workflow generation.

## One-Button Orchestrator

Use the PowerShell runner to set up, test, smoke-build, and serve the platform:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

Useful modes:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Setup
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Test
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Build
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode Serve -NoBrowser
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -Mode All -StopExisting
```

## Production Setup Checklist

1. Place licensed Collibra Java API v2 and workflow runtime JARs in `/jars`.
2. Add organization workflow standards, exported workflows, Excel UUID maps, relation matrices, `.form`, `.app`, `.bpmn`, PDFs, and DOCX files under `/docs/rag_training`.
3. Confirm `config.yaml` values:
   - `models.chat_model: gpt-5-4-2026`
   - `models.embedding_model: text-embedding-3-large`
   - `openai.api_key`
   - `paths.*`
   - `runtime.max_workers`
   - `runtime.use_multiprocessing`
   - `runtime.use_multithreading`
   - `groovy.default_classpath`
4. Start the server and click `Ingest`.
5. Build a workflow from a master prompt.
6. Review Groovy compile results and simulation.
7. Upload generated ZIP to a non-production Collibra tenant for tenant-specific package validation.

## API

- `POST /api/ingest`: parse local RAG corpus and update vectors.
- `POST /api/retrieve`: retrieve RAG context plus relation graph evidence.
- `POST /api/workflows/build`: design, compile, simulate, and export a workflow package.
- `POST /api/workflows/import`: import `.zip` or `.bpmn` onto the canvas.
- `POST /api/workflows/debug`: validate imported/current workflow BPMN, forms, scripts, sequence flows, and simulation.
- `POST /api/workflows/repair`: apply a RAG-aware deterministic repair pass for debug findings.
- `POST /api/workflows/simulate`: run local BPMN path simulation.
- `POST /api/documentation/generate`: generate Markdown implementation/test documentation.
- `POST /api/docs/scrape`: mirror official Collibra workflow/API docs into the local RAG corpus.
- `GET /api/workflows/download?path=...`: download generated ZIP from `/output`.

## Tests

```powershell
pytest
cd src\ui
npm run build
```

Current test coverage verifies:

- Excel UUID/relation extraction from `.xlsx`.
- BPMN/form ZIP package round trip.
- RAG ingestion and retrieval with local hashing embeddings.
- Groovy standards linting.

## Collibra Research

See [docs/collibra_workflow_research.md](docs/collibra_workflow_research.md) for source-grounded notes on Workflow Designer apps, BPMN, forms, script tasks, service/API tasks, and Java API v2 classes.
