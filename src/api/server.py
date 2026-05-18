from __future__ import annotations

import io
import json
import re
import time
import zipfile
from dataclasses import asdict
from pathlib import Path
from xml.etree import ElementTree as ET

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.agents.groovy_compiler import GroovyCompiler
from src.agents.llm_client import model_options_payload, request_text_completion, resolve_model_profile
from src.agents.workflow_agent import CollibraWorkflowAgent
from src.api.schemas import (
    AIEnhanceRequest,
    BuildWorkflowRequest,
    BuildWorkflowResponse,
    CompileGroovyRequest,
    DebugWorkflowRequest,
    DocumentationRequest,
    ExportWorkflowRequest,
    IngestResponse,
    RepairWorkflowRequest,
    RetrieveRequest,
    RetrieveResponse,
    SequenceFlowValidateRequest,
    SimulateRequest,
)
from src.core.action_logger import log_action
from src.core.config import settings
from src.core.logging import configure_logging
from src.core.usage_tracker import ensure_usage_workbook
from src.rag.engine import RAGEngine
from src.rag.collibra_docs import CollibraDocsMirror
from src.workflow.bpmn import BpmnModel, BpmnNode, BpmnPool, SequenceFlow
from src.workflow.form import FormModel, form_field_from_mapping
from src.workflow.package import WorkflowPackage
from src.workflow.simulator import WorkflowSimulator


MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_ZIP_MEMBERS = 400
MAX_ZIP_MEMBER_BYTES = 15 * 1024 * 1024
ALLOWED_UPLOAD_SUFFIXES = {
    ".zip",
    ".bpmn",
    ".bpmn20.xml",
    ".xml",
    ".form",
    ".app",
    ".groovy",
    ".docx",
    ".pdf",
    ".xlsx",
    ".xlsm",
    ".csv",
    ".txt",
    ".md",
    ".json",
}


configure_logging()

app = FastAPI(title=settings.app.name)
rag_engine = RAGEngine(settings)
agent = CollibraWorkflowAgent(rag_engine, config=settings)
simulator = WorkflowSimulator()
groovy_compiler = GroovyCompiler(settings.groovy)
latest_ingest_report: IngestResponse | None = None
active_model_id = (settings.models.available_chat_models[0].id if settings.models.available_chat_models else settings.models.chat_model)
ensure_usage_workbook(settings)

UI_ROOT = Path(__file__).resolve().parents[1] / "ui"
UI_DIR = UI_ROOT / "dist" if (UI_ROOT / "dist").exists() else UI_ROOT
if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=UI_DIR, html=True), name="ui")


@app.middleware("http")
async def timestamped_action_log(request: Request, call_next):
    started = time.perf_counter()
    status = "error"
    response = None
    try:
        response = await call_next(request)
        status = "ok" if response.status_code < 400 else "error"
        return response
    finally:
        if request.url.path.startswith("/api/"):
            log_action(
                f"{request.method} {request.url.path}",
                status=status,
                detail={
                    "statusCode": getattr(response, "status_code", None),
                    "durationMs": round((time.perf_counter() - started) * 1000, 2),
                },
            )


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app.name, "ui": "/ui/index.html"}


@app.get("/api/models")
def list_models() -> dict:
    return {
        "activeModelId": active_model_id,
        "models": model_options_payload(settings),
        "notes": [
            "Model profiles are configured in config.yaml.",
            "API keys are read from environment variables and are never returned by this endpoint.",
        ],
    }


@app.post("/api/models/select")
def select_model(payload: dict) -> dict:
    global active_model_id
    requested = str(payload.get("modelId") or payload.get("id") or "").strip()
    if not requested:
        raise HTTPException(status_code=400, detail="modelId is required.")
    profile = resolve_model_profile(settings, requested)
    active_model_id = profile.id
    log_action("model_selected", detail={"modelId": profile.id, "provider": profile.provider, "model": profile.model})
    return {"activeModelId": active_model_id, "model": profile.id, "provider": profile.provider}


@app.post("/api/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    global latest_ingest_report
    report = rag_engine.ingest()
    latest_ingest_report = IngestResponse(**asdict(report))
    return latest_ingest_report


@app.get("/api/rag/stats")
def rag_stats() -> dict:
    report = latest_ingest_report
    vector_count = rag_engine.store.count()
    return {
        "documents": report.documents if report else rag_engine.store.source_count(),
        "chunks": report.chunks if report else vector_count,
        "relations": report.relations if report else len(rag_engine.relation_graph.relations),
        "vector_count": vector_count,
        "warnings": report.warnings if report else [],
        "uuid_buckets": len(rag_engine.relation_graph.uuid_index),
        "bpmn_nodes": len(rag_engine.relation_graph.bpmn_nodes),
        "sequence_flows": len(rag_engine.relation_graph.sequence_flows),
        "kind_counts": rag_engine.store.kind_counts(),
    }


@app.post("/api/docs/scrape")
def scrape_official_docs() -> dict:
    target = settings.paths.rag_official_docs_dir
    mirror = CollibraDocsMirror(
        target,
        max_pages=settings.runtime.docs_scrape_max_pages,
        verify_ssl=settings.runtime.docs_scrape_verify_ssl,
    )
    report = mirror.scrape(settings.collibra.workflow_docs_seed_urls + [settings.collibra.java_api_docs_url])
    return {"pages": report.pages, "output_dir": str(report.output_dir), "files": [str(path) for path in report.files]}


@app.get("/api/designer/elements")
def designer_elements() -> dict:
    return {
        "elements": ELEMENT_CATALOG,
        "flow_types": [
            {"id": "normal", "label": "Normal sequence", "description": "Unconditional path."},
            {"id": "conditional", "label": "Conditional sequence", "description": "Requires a true JUEL expression, for example ${approvalDecision == 'approve'}."},
            {"id": "default", "label": "Default sequence", "description": "Fallback flow from an activity or gateway."},
            {"id": "skip", "label": "Skip sequence", "description": "Uses flowable:skipExpression; requires _FLOWABLE_SKIP_EXPRESSION_ENABLED=true."},
            {"id": "listener", "label": "Transition listener", "description": "Compiles listener Groovy and stores transition metadata for review."},
        ],
        "form_components": FORM_COMPONENTS,
    }


@app.post("/api/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    context = rag_engine.retrieve(request.question, limit=request.limit)
    return RetrieveResponse(
        context=context.render(),
        sources=[
            {
                "source_path": result.chunk.source_path,
                "kind": result.chunk.kind,
                "score": result.score,
                "metadata": result.chunk.metadata,
            }
            for result in context.results
        ],
    )


@app.post("/api/workflows/build", response_model=BuildWorkflowResponse)
def build_workflow(request: BuildWorkflowRequest) -> BuildWorkflowResponse:
    result = agent.build(request.master_prompt, request.output_name, model_id=active_model_id)
    package = result.package
    return BuildWorkflowResponse(
        zip_path=str(result.output_zip),
        bpmn_xml=package.process.to_xml(),
        process=asdict(package.process),
        forms=[asdict(form) for form in package.forms],
        validation_errors=package.validate(),
        compile_results={
            key: {
                "ok": value.ok,
                "stdout": value.stdout,
                "stderr": value.stderr,
                "skipped": value.skipped,
                "standards": [asdict(issue) for issue in value.standards],
            }
            for key, value in result.compile_results.items()
        },
        simulation=asdict(result.simulation),
        assumptions=result.assumptions,
    )


@app.post("/api/workflows/import")
async def import_workflow(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".zip", ".bpmn"}:
        raise HTTPException(status_code=400, detail="Only .zip and .bpmn imports are supported.")
    target = settings.paths.output_dir / f"imported_{Path(file.filename or 'workflow').name}"
    raw = await _read_upload_limited(file)
    target.write_bytes(raw)
    package = WorkflowPackage.import_file(target)
    return {
        "process": asdict(package.process),
        "forms": [asdict(form) for form in package.forms],
        "validation_errors": package.validate(),
    }


@app.post("/api/workflows/export")
def export_workflow(request: ExportWorkflowRequest) -> dict:
    try:
        package = WorkflowPackage(
            process=_model_from_payload(request.process),
            forms=_forms_from_payload(request.forms),
            app_name=request.app_name,
        )
        errors = package.validate()
        if errors:
            return {"zip_path": "", "bpmn_xml": package.process.to_xml(), "validation_errors": errors}
        safe_name = "".join(char if char.isalnum() or char in "._-" else "_" for char in request.output_name).strip("_")
        output = settings.paths.output_dir / f"{safe_name or 'designer_workflow'}.zip"
        package.export_zip(output)
        return {
            "zip_path": str(output),
            "bpmn_xml": package.process.to_xml(),
            "validation_errors": [],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/workflows/download")
def download(path: str) -> FileResponse:
    output = Path(path)
    if not output.exists() or settings.paths.output_dir not in output.resolve().parents:
        raise HTTPException(status_code=404, detail="Package not found.")
    return FileResponse(output, filename=output.name)


@app.post("/api/workflow/import")
async def import_workflow_workbench(file: UploadFile = File(...)) -> dict:
    raw = await _read_upload_limited(file)
    filename = file.filename or "workflow"
    suffix = Path(filename).suffix.lower()
    app_model = _empty_app_model(filename)
    forms: dict = {}
    members: list[str] = []
    warnings: list[str] = []
    candidates: list[tuple[int, str, str]] = []

    if suffix == ".zip":
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as package:
                members = _validated_zip_member_names(package)
                for member in members:
                    data = package.read(member)
                    text = _decode_text(data)
                    lower = member.lower()
                    if lower.endswith((".bpmn", ".bpmn20.xml", ".xml")) and _looks_like_bpmn(text):
                        priority = 0 if lower.endswith(".bpmn") else 1 if lower.endswith(".bpmn20.xml") else 2
                        candidates.append((priority, member, _sanitize_bpmn_xml(text)))
                    elif lower.endswith(".form"):
                        form_key, form_payload = _parse_collibra_form(text, member)
                        forms[form_key] = form_payload
                    elif lower.endswith(".app"):
                        parsed = _parse_json_or_text(text)
                        if isinstance(parsed, dict):
                            app_model = _deep_merge(app_model, parsed)
                        else:
                            app_model.setdefault("rawApps", {})[member] = parsed
                    elif lower.endswith(".groovy"):
                        app_model.setdefault("scripts", {})[_basename(member)] = {"groovy": text, "source": member}
        except zipfile.BadZipFile as exc:
            raise HTTPException(status_code=400, detail=f"Invalid ZIP package: {exc}") from exc
    elif suffix in {".bpmn", ".xml"} or filename.lower().endswith(".bpmn20.xml"):
        text = _decode_text(raw)
        if not _looks_like_bpmn(text):
            raise HTTPException(status_code=400, detail="Uploaded XML is not a BPMN definitions document.")
        members = [filename]
        candidates.append((0, filename, _sanitize_bpmn_xml(text)))
    elif suffix in {".form", ".app"}:
        text = _decode_text(raw)
        members = [filename]
        if suffix == ".form":
            form_key, form_payload = _parse_collibra_form(text, filename)
            forms[form_key] = form_payload
        else:
            parsed = _parse_json_or_text(text)
            if isinstance(parsed, dict):
                app_model = _deep_merge(app_model, parsed)
            else:
                app_model.setdefault("rawApps", {})[filename] = parsed
        warnings.append("No BPMN diagram was found in the uploaded file.")
    else:
        raise HTTPException(status_code=400, detail="Upload a .zip, .bpmn, .bpmn20.xml, .xml, .form, or .app file.")

    candidates.sort(key=lambda item: (item[0], item[1]))
    chosen = candidates[0] if candidates else None
    if chosen:
        extracted = _extract_bpmn_package_metadata(chosen[2], chosen[1], forms)
        app_model["scripts"] = _deep_merge(app_model.get("scripts") or {}, extracted["scripts"])
        app_model["elementProperties"] = _deep_merge(app_model.get("elementProperties") or {}, extracted["elementProperties"])
        forms = _deep_merge(forms, extracted["forms"])
        existing_forms = app_model.get("forms") or {}
        if not isinstance(existing_forms, dict):
            app_model["manifestForms"] = existing_forms
            existing_forms = {}
        app_model["forms"] = _deep_merge(existing_forms, forms)
        app_model["importDiagnostics"] = extracted["diagnostics"]
        warnings.extend(extracted["warnings"])
    elif forms:
        existing_forms = app_model.get("forms") or {}
        if not isinstance(existing_forms, dict):
            app_model["manifestForms"] = existing_forms
            existing_forms = {}
        app_model["forms"] = _deep_merge(existing_forms, forms)
    return {
        "bpmnXml": chosen[2] if chosen else None,
        "chosenBpmn": chosen[1] if chosen else None,
        "appModel": app_model,
        "forms": forms,
        "members": members,
        "warnings": warnings,
    }


@app.post("/api/workflow/export")
def export_workflow_workbench(payload: dict) -> StreamingResponse:
    bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml")
    if not bpmn_xml:
        raise HTTPException(status_code=400, detail="bpmnXml is required.")
    package_name = _safe_filename(payload.get("packageName") or "collibra-workflow-agent.zip")
    if not package_name.lower().endswith(".zip"):
        package_name = f"{package_name}.zip"
    app_model = payload.get("appModel") or {}
    forms = payload.get("forms") or {}
    base_name = _safe_filename(Path(package_name).stem or "workflow")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr(f"{base_name}.bpmn", bpmn_xml)
        package.writestr(f"{base_name}.app", json.dumps(app_model, indent=2, sort_keys=True))
        for key, value in (forms.items() if isinstance(forms, dict) else []):
            package.writestr(f"{_safe_filename(str(key))}.form", value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True))
        for element_id, script_info in (app_model.get("scripts") or {}).items():
            groovy = script_info.get("groovy", "") if isinstance(script_info, dict) else str(script_info)
            if groovy.strip():
                package.writestr(f"{_safe_filename(str(element_id))}.groovy", groovy)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{package_name}"'},
    )


@app.post("/api/run/simulate")
def simulate_workbench(payload: dict) -> dict:
    bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml")
    if not bpmn_xml:
        raise HTTPException(status_code=400, detail="bpmnXml is required.")
    try:
        model = BpmnModel.from_xml(bpmn_xml)
        result = simulator.simulate(model, [], payload.get("formValues") or payload.get("variables") or {})
        return _simulation_payload(model, result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/agent/design")
def design_workflow_workbench(payload: dict) -> dict:
    prompt = payload.get("prompt") or payload.get("master_prompt") or "Create a Collibra governance workflow."
    try:
        result = agent.build(prompt, "agent_generated_workflow", model_id=_selected_model_id(payload))
        return {
            "bpmnXml": result.package.process.to_xml(),
            "appModel": {
                "metadata": {"name": result.package.process.name, "format": "DSC_SIDE_CAR_APP_V1"},
                "scripts": {
                    node.id: {"groovy": node.script, "elementType": node.type, "elementName": node.name}
                    for node in result.package.process.nodes
                    if node.script
                },
                "forms": {form.key: asdict(form) for form in result.package.forms},
                "uuidMappings": {},
                "validationRules": result.package.validate(),
            },
            "summary": "\n".join(result.assumptions) or "Workflow generated.",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/agent/generate-code")
def generate_code_workbench(payload: dict) -> dict:
    element = payload.get("element") or {}
    prompt = payload.get("prompt") or "Generate Collibra Groovy for the selected BPMN element."
    context = rag_engine.retrieve(prompt, limit=6).render()
    groovy = _ai_or_compat_groovy(element, prompt, context, _selected_model_id(payload))
    compile_result = groovy_compiler.compile_script(groovy) if groovy.strip() else None
    return {
        "groovy": groovy,
        "summary": f"Generated Collibra code guidance for {element.get('id', 'selected element')}.",
        "reasoning": [
            "Used the selected BPMN element metadata.",
            "Included local RAG context from Collibra documentation and uploaded project files.",
            "Kept output compile-oriented with defensive execution-variable handling.",
        ],
        "tests": ["Compile selected Groovy.", "Run workflow simulation.", "Export ZIP and validate in a Collibra test tenant."],
        "warnings": [] if (compile_result and compile_result.ok) else ["Groovy compiler may be unavailable or returned lint warnings."],
        "compileStatus": "passed" if (compile_result and compile_result.ok) else "not-run",
        "compileResults": [_compile_result_dict(compile_result)] if compile_result else [],
        "context": context[:3000],
    }


@app.post("/api/agent/autonomous-run")
def autonomous_agent_run(payload: dict) -> dict:
    mode = str(payload.get("mode") or "prompt").lower()
    prompt = str(payload.get("prompt") or payload.get("businessUseCase") or "").strip()
    max_iterations = max(1, min(8, int(payload.get("maxIterations") or 5)))
    output_name = _safe_filename(payload.get("packageName") or payload.get("outputName") or "autonomous_collibra_workflow")
    if output_name.lower().endswith(".zip"):
        output_name = output_name[:-4]

    rag_query = " ".join(
        filter(
            None,
            [
                prompt,
                "Collibra workflow BPMN forms Groovy Java API v2 relation UUID roles organization standards OOTB workflow",
            ],
        )
    )
    rag_context = rag_engine.retrieve(rag_query, limit=14)
    trace: list[dict] = [
        {
            "step": "rag_retrieval",
            "status": "completed",
            "sources": [_search_result_payload(result) for result in rag_context.results[:10]],
            "relations": len(rag_context.relation_graph.relations),
        }
    ]

    if mode == "prompt":
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt is required for autonomous prompt mode.")
        build_result = agent.build(prompt, f"{output_name}_draft", model_id=_selected_model_id(payload))
        model = build_result.package.process
        forms = _forms_dict_from_package(build_result.package)
        app_model = _app_model_from_package(build_result.package, rag_context.render())
        trace.append(
            {
                "step": "design_from_prompt",
                "status": "completed",
                "nodes": len(model.nodes),
                "flows": len(model.flows),
                "forms": len(forms),
                "scripts": len(app_model.get("scripts") or {}),
            }
        )
    elif mode in {"canvas", "import", "imported"}:
        bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml") or ""
        if not str(bpmn_xml).strip():
            raise HTTPException(status_code=400, detail="bpmnXml is required for autonomous canvas/import mode.")
        try:
            model = BpmnModel.from_xml(_sanitize_bpmn_xml(str(bpmn_xml)))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse BPMN XML: {exc}") from exc
        forms = dict(_workbench_form_items(payload.get("forms") or (payload.get("appModel") or {}).get("forms") or {}))
        app_model = payload.get("appModel") or {}
        trace.append(
            {
                "step": "load_canvas_or_import",
                "status": "completed",
                "nodes": len(model.nodes),
                "flows": len(model.flows),
                "forms": len(forms),
                "scripts": len(app_model.get("scripts") or {}),
            }
        )
    else:
        raise HTTPException(status_code=400, detail="mode must be prompt, canvas, or import.")

    user_test_cases = str(payload.get("userTestCases") or "")
    business_use_case = prompt or str(payload.get("businessUseCase") or f"Validate {model.name} end to end.")
    final_quality: dict = {}
    final_cases: dict = {}
    for iteration in range(1, max_iterations + 1):
        final_quality = _run_package_quality_loop(model, app_model, forms, max_iterations=1)
        app_model = final_quality.get("repairedAppModel") or app_model
        generated_cases = _generate_business_test_cases(model, app_model, forms, business_use_case)
        parsed_user_cases = _parse_user_test_cases(user_test_cases)
        case_results = _execute_business_test_cases(
            model,
            app_model,
            forms,
            generated_cases + parsed_user_cases,
            final_quality,
        )
        failed_cases = [case for case in case_results if case["status"] != "passed"]
        passed_case_count = len([case for case in case_results if case["status"] == "passed"])
        case_pass_percent = round((passed_case_count / max(1, len(case_results))) * 100, 2)
        case_status = "passed" if final_quality["ok"] and not failed_cases else "failed"
        final_cases = {
            "ok": final_quality["ok"] and not failed_cases,
            "status": case_status,
            "summaryText": (
                f"Autonomous Agent Mode {case_status}. Case pass rate {case_pass_percent}% "
                f"({passed_case_count}/{len(case_results)} cases). Package pass rate "
                f"{final_quality.get('metrics', {}).get('passPercent', 0)}%."
            ),
            "metrics": {
                "casePassPercent": case_pass_percent,
                "packagePassPercent": final_quality.get("metrics", {}).get("passPercent", 0),
            },
            "businessUseCase": business_use_case,
            "packageResult": final_quality,
            "generatedCases": generated_cases,
            "userCases": parsed_user_cases,
            "caseResults": case_results,
            "summary": {
                "generatedCases": len(generated_cases),
                "userCases": len(parsed_user_cases),
                "passedCases": len([case for case in case_results if case["status"] == "passed"]),
                "failedCases": len(failed_cases),
                "packageOk": final_quality["ok"],
            },
        }
        trace.append(
            {
                "step": "compile_test_repair",
                "iteration": iteration,
                "packageStatus": final_quality["status"],
                "blockingIssues": len(final_quality.get("blockingIssues") or []),
                "failedCases": len(failed_cases),
            }
        )
        if final_cases["ok"]:
            break

    bpmn_xml = model.to_xml()
    markdown = _workbench_documentation_markdown(
        model,
        app_model,
        forms,
        (
            "Autonomous Agent Mode documentation. Include prompt analysis, RAG evidence, organization mappings, "
            "BPMN design, forms, Groovy scripts, sequence-flow conditions, compilation, repairs and test cases.\n\n"
            + business_use_case
        ),
    )
    settings.paths.output_dir.mkdir(parents=True, exist_ok=True)
    doc_path = settings.paths.output_dir / f"{output_name}_autonomous_documentation.md"
    report_path = settings.paths.output_dir / f"{output_name}_autonomous_report.json"
    zip_path = settings.paths.output_dir / f"{output_name}_autonomous_package.zip"
    doc_path.write_text(markdown, encoding="utf-8")
    _write_workbench_zip(zip_path, bpmn_xml, app_model, forms, doc_path, report_path)
    report = {
        "mode": mode,
        "ok": bool(final_cases.get("ok")),
        "status": final_cases.get("status", "failed"),
        "trace": trace,
        "quality": final_quality,
        "cases": final_cases,
        "documentationPath": str(doc_path),
        "zipPath": str(zip_path),
        "ragContextPreview": rag_context.render()[:6000],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_workbench_zip(zip_path, bpmn_xml, app_model, forms, doc_path, report_path)
    return {
        "ok": report["ok"],
        "status": report["status"],
        "mode": mode,
        "bpmnXml": bpmn_xml,
        "appModel": app_model,
        "forms": forms,
        "quality": final_quality,
        "cases": final_cases,
        "documentation": {"path": str(doc_path), "markdown": markdown},
        "zipPath": str(zip_path),
        "downloadUrl": f"/api/workflows/download?path={zip_path}",
        "reportPath": str(report_path),
        "trace": trace,
    }


@app.get("/api/rag/status")
def rag_status_workbench() -> dict:
    stats = rag_stats()
    return _workbench_rag_status(stats)


@app.get("/api/rag/template")
def download_rag_relation_template() -> FileResponse:
    template = settings.paths.relation_template_file
    if not template.exists():
        raise HTTPException(status_code=404, detail="Relation UUID Excel template was not found.")
    return FileResponse(
        template,
        filename=template.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.post("/api/rag/index")
def rag_index_workbench() -> dict:
    ingest()
    return {"status": _workbench_rag_status(rag_stats())}


@app.post("/api/rag/reindex")
def rag_reindex_workbench() -> dict:
    ingest()
    return {"status": _workbench_rag_status(rag_stats())}


@app.post("/api/rag/upload")
async def rag_upload_workbench(files: list[UploadFile] = File(...)) -> dict:
    saved = await _save_rag_uploads(files)
    return {"saved": [str(path) for path in saved], "status": _workbench_rag_status(rag_stats())}


@app.post("/api/rag/ingest")
async def rag_ingest_workbench(files: list[UploadFile] = File(...)) -> dict:
    await _save_rag_uploads(files)
    ingest()
    return {"status": _workbench_rag_status(rag_stats())}


@app.post("/api/rag/query")
def rag_query_workbench(payload: dict) -> dict:
    question = payload.get("question") or payload.get("query") or ""
    limit = int(payload.get("top_k") or payload.get("limit") or 8)
    context = rag_engine.retrieve(question, limit=limit)
    return {"results": [_search_result_payload(result) for result in context.results]}


@app.post("/api/rag/chat")
def rag_chat_workbench(payload: dict) -> dict:
    question = payload.get("question") or ""
    limit = int(payload.get("top_k") or payload.get("limit") or 8)
    context = rag_engine.retrieve(question, limit=limit)
    results = [_search_result_payload(result) for result in context.results]
    if results:
        answer = _business_rag_answer(question, context.render(), results, _selected_model_id(payload))
    else:
        answer = "No RAG results were found. Upload documents and generate the index, then ask again."
    return {"answer": answer, "results": results}


@app.post("/api/workflows/simulate")
def simulate(request: SimulateRequest) -> dict:
    try:
        model = BpmnModel.from_xml(request.bpmn_xml)
        forms = [
            FormModel(
                key=form["key"],
                name=form.get("name", form["key"]),
                fields=[form_field_from_mapping(field) for field in form.get("fields", []) if isinstance(field, dict)],
            )
            for form in request.forms
        ]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = simulator.simulate(model, forms, request.variables)
    return _simulation_payload(model, result)


@app.post("/api/workflows/debug")
def debug_workflow(request: DebugWorkflowRequest) -> dict:
    package = WorkflowPackage(
        process=_model_from_payload(request.process),
        forms=_forms_from_payload(request.forms),
        app_name=request.process.get("name", "Imported Workflow"),
    )
    issues = [{"severity": "error", "area": "bpmn", "message": error} for error in package.validate()]
    compile_results = {}
    for node in package.process.nodes:
        if node.type == "scriptTask" and node.script.strip():
            result = groovy_compiler.compile_script(node.script)
            compile_results[node.id] = _compile_result_dict(result)
            if not result.ok:
                issues.append({"severity": "error", "area": "groovy", "element_id": node.id, "message": result.stderr or "Groovy lint failed."})
            elif result.skipped:
                issues.append({"severity": "warning", "area": "groovy", "element_id": node.id, "message": result.stderr})
    for flow in package.process.flows:
        validation = validate_sequence_flow(SequenceFlowValidateRequest(flow=asdict(flow)))
        if not validation["ok"]:
            for error in validation["errors"]:
                issues.append({"severity": "error", "area": "sequenceFlow", "element_id": flow.id, "message": error})
    simulation = simulator.simulate(package.process, package.forms, request.variables)
    for error in simulation.errors:
        issues.append({"severity": "error", "area": "simulation", "message": error})
    rag_context = rag_engine.retrieve("Collibra workflow debug BPMN Groovy sequence flow forms", limit=5).render()
    return {
        "ok": not any(issue["severity"] == "error" for issue in issues),
        "issues": issues,
        "compile_results": compile_results,
        "simulation": asdict(simulation),
        "rag_context": rag_context[:4000],
    }


@app.post("/api/workflows/repair")
def repair_workflow(request: RepairWorkflowRequest) -> dict:
    model = _model_from_payload(request.process)
    forms = _forms_from_payload(request.forms)
    if not any(node.type == "startEvent" for node in model.nodes):
        model.nodes.insert(0, BpmnNode(id="start", type="startEvent", name="Start", lane=model.lanes[0] if model.lanes else None, x=80, y=120))
    if not any(node.type == "endEvent" for node in model.nodes):
        model.nodes.append(BpmnNode(id="end", type="endEvent", name="End", lane=model.lanes[0] if model.lanes else None, x=980, y=120))
    node_ids = {node.id for node in model.nodes}
    model.flows = [flow for flow in model.flows if flow.source_ref in node_ids and flow.target_ref in node_ids]
    for flow in model.flows:
        if flow.flow_type == "conditional" and not flow.condition:
            flow.condition = "${approvalDecision == 'approve'}"
        if flow.flow_type == "default":
            flow.is_default = True
        if flow.flow_type == "skip" and not flow.skip_expression:
            flow.skip_expression = "${skipFlow == true}"
    for node in model.nodes:
        if node.type == "scriptTask" and node.script and "import " not in node.script:
            node.script = "import java.util.UUID\n\n" + node.script
    package = WorkflowPackage(process=model, forms=forms, app_name=model.name)
    return {
        "process": asdict(package.process),
        "forms": [asdict(form) for form in package.forms],
        "validation_errors": package.validate(),
        "message": "Applied deterministic repair pass. Use Debug again to verify remaining issues.",
    }


@app.post("/api/documentation/generate")
def generate_documentation(request: DocumentationRequest) -> dict:
    model = _model_from_payload(request.process)
    forms = _forms_from_payload(request.forms)
    markdown = _documentation_markdown(model, forms, request.prompt)
    output_path = settings.paths.output_dir / f"{model.process_id}_documentation.md"
    output_path.write_text(markdown, encoding="utf-8")
    return {"markdown": markdown, "path": str(output_path)}


@app.post("/api/workflow/documentation")
def generate_workbench_documentation(payload: dict) -> dict:
    bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml") or ""
    if not bpmn_xml.strip():
        raise HTTPException(status_code=400, detail="bpmnXml is required.")
    try:
        model = BpmnModel.from_xml(_sanitize_bpmn_xml(bpmn_xml))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse BPMN XML: {exc}") from exc
    app_model = payload.get("appModel") or {}
    forms = payload.get("forms") or app_model.get("forms") or {}
    prompt = payload.get("prompt") or ""
    markdown = _workbench_documentation_markdown(model, app_model, forms, prompt)
    ai_doc = _ai_documentation_narrative(markdown, prompt, _selected_model_id(payload))
    if ai_doc:
        markdown = f"{markdown}\n\n## AI Business Narrative\n\n{ai_doc}\n"
    settings.paths.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.paths.output_dir / f"{_safe_filename(model.process_id)}_workbench_documentation.md"
    output_path.write_text(markdown, encoding="utf-8")
    return {
        "markdown": markdown,
        "path": str(output_path),
        "summary": {
            "processId": model.process_id,
            "nodes": len(model.nodes),
            "flows": len(model.flows),
            "lanes": len(model.lanes),
            "scripts": len((app_model.get("scripts") or {})),
        },
    }


@app.post("/api/workflow/test-package")
def test_workbench_package(payload: dict) -> dict:
    bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml") or ""
    if not bpmn_xml.strip():
        raise HTTPException(status_code=400, detail="bpmnXml is required.")
    app_model = payload.get("appModel") or {}
    forms = payload.get("forms") or app_model.get("forms") or {}
    try:
        model = BpmnModel.from_xml(_sanitize_bpmn_xml(bpmn_xml))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse BPMN XML: {exc}") from exc
    return _run_package_quality_loop(model, app_model, forms, int(payload.get("maxIterations") or 3))


@app.post("/api/workflow/test-cases")
def test_workbench_cases(payload: dict) -> dict:
    bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml") or ""
    if not bpmn_xml.strip():
        raise HTTPException(status_code=400, detail="bpmnXml is required.")
    app_model = payload.get("appModel") or {}
    forms = payload.get("forms") or app_model.get("forms") or {}
    business_use_case = payload.get("businessUseCase") or payload.get("prompt") or ""
    user_test_cases = payload.get("userTestCases") or ""
    try:
        model = BpmnModel.from_xml(_sanitize_bpmn_xml(bpmn_xml))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse BPMN XML: {exc}") from exc
    package_result = _run_package_quality_loop(model, app_model, forms, int(payload.get("maxIterations") or 3))
    generated_cases = _generate_business_test_cases(model, app_model, forms, business_use_case)
    user_cases = _parse_user_test_cases(user_test_cases)
    case_results = _execute_business_test_cases(model, app_model, forms, generated_cases + user_cases, package_result)
    blocking = [result for result in case_results if result["status"] != "passed"]
    total_cases = max(1, len(case_results))
    passed_cases = len([result for result in case_results if result["status"] == "passed"])
    pass_percent = round((passed_cases / total_cases) * 100, 2)
    status = "passed" if package_result["ok"] and not blocking else "failed"
    return {
        "ok": package_result["ok"] and not blocking,
        "status": status,
        "summaryText": (
            f"AI and user test cases {status}. Case pass rate {pass_percent}% "
            f"({passed_cases}/{len(case_results)} cases). Package pass rate "
            f"{package_result.get('metrics', {}).get('passPercent', 0)}%."
        ),
        "metrics": {
            "casePassPercent": pass_percent,
            "totalCases": len(case_results),
            "passedCases": passed_cases,
            "failedCases": len(blocking),
            "packagePassPercent": package_result.get("metrics", {}).get("passPercent", 0),
        },
        "businessUseCase": business_use_case,
        "packageResult": package_result,
        "generatedCases": generated_cases,
        "userCases": user_cases,
        "caseResults": case_results,
        "summary": {
            "generatedCases": len(generated_cases),
            "userCases": len(user_cases),
            "passedCases": len([result for result in case_results if result["status"] == "passed"]),
            "failedCases": len(blocking),
            "packageOk": package_result["ok"],
        },
    }


@app.post("/api/compile/groovy")
def compile_groovy(request: CompileGroovyRequest) -> dict:
    return _compile_result_dict(groovy_compiler.compile_script(request.code or request.script))


@app.post("/api/validate/sequence-flow")
def validate_sequence_flow(request: SequenceFlowValidateRequest) -> dict:
    flow = _flow_from_payload(request.flow)
    errors: list[str] = []
    if flow.flow_type == "conditional" and not flow.condition:
        errors.append("Conditional sequence flow requires a condition expression.")
    if flow.flow_type == "skip" and not flow.skip_expression:
        errors.append("Skip sequence flow requires a skip expression.")
    for label, expression in (("condition", flow.condition), ("skip expression", flow.skip_expression)):
        if expression and not (expression.strip().startswith("${") and expression.strip().endswith("}")):
            errors.append(f"{label} must be wrapped as a JUEL expression, for example ${{approvalDecision == 'approve'}}.")
    listener_result = None
    if flow.listener_code:
        listener_result = _compile_result_dict(groovy_compiler.compile_script(flow.listener_code))
        if not listener_result["ok"]:
            errors.append("Transition listener Groovy failed compile/lint validation.")
    return {"ok": not errors, "errors": errors, "listener_compile": listener_result}


@app.post("/api/ai/enhance")
def ai_enhance(request: AIEnhanceRequest) -> dict:
    context = rag_engine.retrieve(request.instruction, limit=6).render()
    if request.target_type == "sequenceFlow":
        return {
            "message": "Generated sequence-flow guidance from Collibra docs and local RAG context.",
            "patch": _sequence_flow_patch(request.instruction, request.target),
            "context": context[:4000],
        }
    return {
        "message": "Generated block guidance from Collibra docs and local RAG context.",
        "patch": _block_patch(request.instruction, request.target),
        "context": context[:4000],
    }


def _model_from_payload(data: dict) -> BpmnModel:
    return BpmnModel(
        process_id=data.get("process_id") or data.get("id") or "designerWorkflow",
        name=data.get("name") or "Designer Workflow",
        pools=[
            BpmnPool(
                id=pool.get("id", "pool_main"),
                name=pool.get("name", "Collibra Workflow"),
                process_ref=pool.get("process_ref") or pool.get("processRef"),
                x=int(pool.get("x", 40)),
                y=int(pool.get("y", 40)),
                width=int(pool.get("width", 1240)),
                height=int(pool.get("height", 520)),
            )
            for pool in data.get("pools", [])
        ],
        lanes=list(data.get("lanes") or ["Requester", "Data Steward", "Collibra Automation"]),
        nodes=[_node_from_payload(node) for node in data.get("nodes", [])],
        flows=[_flow_from_payload(flow) for flow in data.get("flows", [])],
        documentation=data.get("documentation", ""),
        executable=bool(data.get("executable", True)),
    )


def _forms_dict_from_package(package: WorkflowPackage) -> dict[str, dict]:
    return {form.key: asdict(form) for form in package.forms}


def _app_model_from_package(package: WorkflowPackage, rag_context: str = "") -> dict:
    model = package.process
    scripts = {
        node.id: {
            "groovy": node.script,
            "elementId": node.id,
            "elementType": f"bpmn:{node.type[:1].upper()}{node.type[1:]}",
            "elementName": node.name,
            "scriptFormat": "groovy",
            "source": "autonomous-agent",
        }
        for node in model.nodes
        if node.script.strip()
    }
    element_properties: dict[str, dict] = {}
    for node in model.nodes:
        props = {
            "elementId": node.id,
            "elementType": f"bpmn:{node.type[:1].upper()}{node.type[1:]}",
            "elementName": node.name,
            "lane": node.lane,
            "documentation": node.documentation,
            **(node.properties or {}),
        }
        if node.form_key:
            props["formKey"] = node.form_key
        if node.candidate_users:
            props["candidateUsers"] = node.candidate_users
        if node.candidate_groups:
            props["candidateGroups"] = node.candidate_groups
        if node.type == "scriptTask":
            props["scriptFormat"] = "groovy"
        element_properties[node.id] = props
    for flow in model.flows:
        element_properties[flow.id] = {
            "elementId": flow.id,
            "elementType": "bpmn:SequenceFlow",
            "elementName": flow.name,
            "sourceRef": flow.source_ref,
            "targetRef": flow.target_ref,
            "condition": flow.condition,
            "skipExpression": flow.skip_expression,
            "flowType": flow.flow_type,
            "isDefault": flow.is_default,
            "listenerCode": flow.listener_code,
        }
    return {
        "metadata": {
            "name": model.name,
            "format": "DSC_AUTONOMOUS_AGENT_APP_V1",
            "processId": model.process_id,
            "generator": "DSC Collibra Workflow Automation Agent",
        },
        "scripts": scripts,
        "forms": _forms_dict_from_package(package),
        "elementProperties": element_properties,
        "uuidMappings": {},
        "ragContextPreview": rag_context[:4000],
        "validationRules": package.validate(),
    }


def _write_workbench_zip(
    output_path: Path,
    bpmn_xml: str,
    app_model: dict,
    forms: dict | list,
    documentation_path: Path | None = None,
    report_path: Path | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    form_items = _workbench_form_items(forms)
    base_name = _safe_filename(output_path.stem.replace("_autonomous_package", "").replace("_package", "") or "workflow")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr(f"{base_name}.bpmn", bpmn_xml)
        package.writestr(f"{base_name}.app", json.dumps(app_model, indent=2, sort_keys=True))
        for key, value in form_items:
            package.writestr(f"{_safe_filename(str(key))}.form", json.dumps(value, indent=2, sort_keys=True))
        for element_id, script_info in (app_model.get("scripts") or {}).items():
            groovy = script_info.get("groovy", "") if isinstance(script_info, dict) else str(script_info)
            if groovy.strip():
                package.writestr(f"{_safe_filename(str(element_id))}.groovy", groovy)
        if documentation_path and documentation_path.exists():
            package.writestr(documentation_path.name, documentation_path.read_text(encoding="utf-8"))
        if report_path and report_path.exists():
            package.writestr("test-report.json", report_path.read_text(encoding="utf-8"))
    return output_path


def _node_from_payload(data: dict) -> BpmnNode:
    return BpmnNode(
        id=data["id"],
        type=data.get("type", "userTask"),
        name=data.get("name", data["id"]),
        lane=data.get("lane"),
        documentation=data.get("documentation", ""),
        script=data.get("script", ""),
        form_key=data.get("form_key") or data.get("formKey"),
        candidate_users=data.get("candidate_users") or data.get("candidateUsers"),
        candidate_groups=data.get("candidate_groups") or data.get("candidateGroups"),
        properties=data.get("properties", {}),
        x=int(data.get("x", data.get("position", {}).get("x", 120))),
        y=int(data.get("y", data.get("position", {}).get("y", 120))),
    )


def _flow_from_payload(data: dict) -> SequenceFlow:
    return SequenceFlow(
        id=data["id"],
        source_ref=data.get("source_ref") or data.get("sourceRef") or data.get("source", ""),
        target_ref=data.get("target_ref") or data.get("targetRef") or data.get("target", ""),
        name=data.get("name", ""),
        condition=data.get("condition", ""),
        skip_expression=data.get("skip_expression") or data.get("skipExpression", ""),
        flow_type=data.get("flow_type") or data.get("flowType", "normal"),
        is_default=bool(data.get("is_default") or data.get("isDefault", False)),
        documentation=data.get("documentation", ""),
        listener_code=data.get("listener_code") or data.get("listenerCode", ""),
        properties=data.get("properties", {}),
    )


def _forms_from_payload(forms: list[dict]) -> list[FormModel]:
    return [
        FormModel(
            key=form["key"],
            name=form.get("name", form["key"]),
            fields=[form_field_from_mapping(field) for field in form.get("fields", []) if isinstance(field, dict)],
        )
        for form in forms
    ]


def _compile_result_dict(result) -> dict:
    return {
        "ok": result.ok,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "skipped": result.skipped,
        "standards": [asdict(issue) for issue in result.standards],
    }


def _documentation_markdown(model: BpmnModel, forms: list[FormModel], prompt: str) -> str:
    context = rag_engine.retrieve(prompt or model.name, limit=6).render()
    lines = [
        f"# {model.name}",
        "",
        "Generated by DSC Collibra Workflow Automation Agent.",
        "",
        "## Purpose",
        "",
        prompt or model.documentation or "Collibra workflow package documentation.",
        "",
        "## Pools And Lanes",
        "",
    ]
    for pool in model.pools or [BpmnPool(id=f"{model.process_id}_pool", name=model.name)]:
        lines.append(f"- Pool `{pool.id}`: {pool.name}")
    for lane in model.lanes:
        lines.append(f"- Lane: {lane}")
    lines.extend(["", "## BPMN Blocks", ""])
    for node in model.nodes:
        lines.append(f"- `{node.id}` ({node.type}) - {node.name}; lane: {node.lane or 'n/a'}")
    lines.extend(["", "## Sequence Flows", ""])
    for flow in model.flows:
        detail = flow.condition or flow.skip_expression or ("default" if flow.is_default else "normal")
        lines.append(f"- `{flow.id}`: `{flow.source_ref}` -> `{flow.target_ref}`; type: {flow.flow_type}; rule: {detail}")
    lines.extend(["", "## Forms", ""])
    for form in forms:
        lines.append(f"- `{form.key}`: {form.name} ({len(form.fields)} fields)")
    lines.extend(["", "## Test Plan", ""])
    lines.extend([
        "- Validate BPMN structure and missing references.",
        "- Compile every script task and transition listener with Collibra JARs on classpath.",
        "- Simulate approval, rejection, missing required form fields, and API failure paths.",
        "- Upload first to a non-production Collibra tenant and verify package manifest compatibility.",
        "",
        "## Retrieved RAG Context",
        "",
        context[:3000],
    ])
    return "\n".join(lines)


def _workbench_documentation_markdown(model: BpmnModel, app_model: dict, forms: dict | list, prompt: str) -> str:
    scripts = app_model.get("scripts") or {}
    element_properties = app_model.get("elementProperties") or {}
    metadata = app_model.get("metadata") or {}
    context = rag_engine.retrieve(prompt or model.name, limit=8).render()
    form_items = _workbench_form_items(forms)
    script_ids = set(scripts)
    documented_ids = set(element_properties)
    lines = [
        f"# {model.name}",
        "",
        "Generated by DSC Collibra Workflow Automation Agent.",
        "",
        "## Executive Summary",
        "",
        prompt or model.documentation or "Production Collibra workflow documentation generated from the current BPMN canvas.",
        "",
        "## Package Metadata",
        "",
        f"- Process ID: `{model.process_id}`",
        f"- Executable: `{model.executable}`",
        f"- Sidecar format: `{metadata.get('format', 'DSC_SIDE_CAR_APP_V1')}`",
        f"- Package name: `{metadata.get('name', model.name)}`",
        f"- BPMN nodes: {len(model.nodes)}",
        f"- Sequence flows: {len(model.flows)}",
        f"- Pools: {len(model.pools or [])}",
        f"- Lanes: {len(model.lanes or [])}",
        f"- Saved scripts: {len(scripts)}",
        "",
        "## Pools And Swimlanes",
        "",
    ]
    for pool in model.pools or [BpmnPool(id=f"{model.process_id}_pool", name=model.name)]:
        lines.append(f"- Pool `{pool.id}`: {pool.name}")
    for lane in model.lanes:
        lane_nodes = [node for node in model.nodes if node.lane == lane]
        lines.append(f"- Lane `{lane}`: {len(lane_nodes)} BPMN block(s)")

    lines.extend(["", "## BPMN Block Inventory", ""])
    for node in model.nodes:
        props = element_properties.get(node.id) or {}
        script_state = "script saved" if node.id in script_ids else "no script saved"
        doc_state = "metadata saved" if node.id in documented_ids else "metadata pending"
        lines.append(
            f"- `{node.id}` ({node.type}) - {node.name or 'unnamed'}; lane: {node.lane or 'n/a'}; "
            f"execution: {props.get('execution', 'n/a')}; {script_state}; {doc_state}"
        )

    lines.extend(["", "## Sequence Flow Rules", ""])
    for flow in model.flows:
        props = element_properties.get(flow.id) or {}
        rule = props.get("condition") or flow.condition or flow.skip_expression or ("default" if flow.is_default else "normal")
        lines.append(
            f"- `{flow.id}`: `{flow.source_ref}` -> `{flow.target_ref}`; name: {flow.name or 'n/a'}; "
            f"type: {flow.flow_type}; rule: `{rule}`"
        )

    lines.extend(["", "## Forms And App Sidecar", ""])
    if form_items:
        for key, form in form_items:
            fields = form.get("fields") if isinstance(form, dict) else []
            lines.append(f"- `{key}`: {form.get('name', key) if isinstance(form, dict) else key}; fields: {len(fields or [])}")
    else:
        lines.append("- No forms saved in the sidecar yet.")

    lines.extend(["", "## Groovy Implementation Notes", ""])
    if scripts:
        for element_id, script in scripts.items():
            if isinstance(script, dict):
                groovy = script.get("groovy") or ""
                summary = script.get("summary") or ""
                warnings = script.get("warnings") or []
            else:
                groovy = str(script)
                summary = ""
                warnings = []
            lines.append(f"- `{element_id}`: {len(groovy)} Groovy characters; summary: {summary or 'n/a'}; warnings: {len(warnings or [])}")
    else:
        lines.append("- No Groovy scripts have been generated or pasted yet.")

    lines.extend(
        [
            "",
            "## Autonomous Test Plan",
            "",
            "- Compile every generated Groovy script and every sequence-flow listener before export.",
            "- Run the happy path from requester form through steward approval, asset update and notification.",
            "- Run rejection paths from each approval gateway and verify the workflow reaches the expected end event.",
            "- Run missing required form fields, invalid UUID values, missing role assignment and absent asset relation mappings.",
            "- Run Collibra API failure handling for asset, domain, community and responsibility lookups.",
            "- Re-import the exported ZIP and verify BPMN, .app, .form and Groovy script round-trip integrity.",
            "- Upload to a non-production Collibra tenant before production deployment.",
            "",
            "## Deployment Checklist",
            "",
            "- Confirm all UUIDs, role names, relation type IDs and domain/community IDs come from the indexed organization knowledge base.",
            "- Confirm Java API imports match the Collibra Java API v2 documentation and local JAR classpath.",
            "- Confirm mail tasks, user tasks and service/script tasks use the organization's standard execution variables.",
            "- Keep the exported ZIP, generated documentation and compile logs together as the deployment evidence package.",
            "",
            "## Retrieved RAG Context",
            "",
            context[:4000],
        ]
    )
    return "\n".join(lines)


def _workbench_form_items(forms: dict | list) -> list[tuple[str, dict]]:
    if isinstance(forms, dict):
        return [(str(key), value if isinstance(value, dict) else {"name": str(key), "value": value}) for key, value in forms.items()]
    if isinstance(forms, list):
        result: list[tuple[str, dict]] = []
        for idx, form in enumerate(forms, start=1):
            if isinstance(form, dict):
                key = str(form.get("key") or form.get("id") or f"form_{idx}")
                result.append((key, form))
            else:
                result.append((f"form_{idx}", {"name": f"Form {idx}", "value": form}))
        return result
    return []


def _parse_collibra_form(text: str, source: str) -> tuple[str, dict | str]:
    parsed = _parse_json_or_text(text)
    if not isinstance(parsed, dict):
        return _basename(source).removeprefix("form-"), parsed
    normalized = _normalize_collibra_form(parsed, source)
    return normalized["key"], normalized


def _normalize_collibra_form(data: dict, source: str) -> dict:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    fallback_key = _basename(source).removeprefix("form-")
    key = str(metadata.get("key") or data.get("key") or fallback_key)
    name = str(metadata.get("name") or data.get("name") or key)
    fields = _flatten_collibra_form_fields(data)
    outcomes = [
        {
            "label": str(outcome.get("label") or outcome.get("name") or outcome.get("value") or ""),
            "value": str(outcome.get("value") or outcome.get("id") or outcome.get("label") or ""),
            "primary": bool(outcome.get("primary", False)),
            "visible": outcome.get("visible", ""),
            "enabled": outcome.get("enabled", ""),
        }
        for outcome in data.get("outcomes", [])
        if isinstance(outcome, dict)
    ]
    return {
        "key": key,
        "name": name,
        "description": metadata.get("description") or data.get("description") or "",
        "version": metadata.get("version") or data.get("version") or "",
        "modelType": metadata.get("modelType") or data.get("modelType") or "form",
        "palette": metadata.get("palette") or data.get("palette") or "",
        "source": source,
        "fields": fields,
        "outcomes": outcomes,
        "rows": data.get("rows", []),
        "metadata": metadata,
        "raw": data,
    }


def _flatten_collibra_form_fields(data: dict) -> list[dict]:
    fields: list[dict] = []
    if isinstance(data.get("fields"), list):
        for index, field in enumerate(data["fields"]):
            if isinstance(field, dict):
                fields.append(_normalize_form_field(field, index, 0, 0))
    for row_index, row in enumerate(data.get("rows", []) or []):
        if not isinstance(row, dict):
            continue
        for col_index, col in enumerate(row.get("cols", []) or []):
            if isinstance(col, dict):
                fields.append(_normalize_form_field(col, len(fields), row_index, col_index))
    return fields


def _normalize_form_field(field: dict, index: int, row_index: int, col_index: int) -> dict:
    design_info = field.get("designInfo") if isinstance(field.get("designInfo"), dict) else {}
    extra_settings = field.get("extraSettings") if isinstance(field.get("extraSettings"), dict) else {}
    field_id = str(field.get("id") or field.get("key") or f"field_{index + 1}")
    return {
        "id": field_id,
        "name": str(field.get("name") or field.get("label") or field_id),
        "label": str(field.get("label") or field.get("name") or field_id),
        "type": str(field.get("type") or design_info.get("stencilId") or "string"),
        "required": bool(field.get("isRequired", field.get("required", False))),
        "visible": field.get("visible", True),
        "enabled": field.get("enabled", True),
        "writable": field.get("writable", field.get("enabled", True)),
        "readable": field.get("readable", field.get("visible", True)),
        "value": field.get("value", field.get("default")),
        "size": field.get("size"),
        "row": row_index,
        "column": col_index,
        "stencilId": design_info.get("stencilId"),
        "stencilSuperIds": design_info.get("stencilSuperIds", []),
        "extraSettings": extra_settings,
    }


def _extract_bpmn_package_metadata(bpmn_xml: str, source_name: str, known_forms: dict) -> dict:
    scripts: dict = {}
    element_properties: dict = {}
    inline_forms: dict = {}
    warnings: list[str] = []
    diagnostics = {
        "sourceBpmn": source_name,
        "scriptTasks": 0,
        "embeddedScripts": 0,
        "userTasks": 0,
        "sequenceFlows": 0,
        "formReferences": 0,
        "inlineForms": 0,
        "missingForms": [],
    }
    try:
        root = ET.fromstring(_sanitize_bpmn_xml(bpmn_xml))
    except ET.ParseError as exc:
        return {
            "scripts": scripts,
            "elementProperties": element_properties,
            "forms": inline_forms,
            "warnings": [f"Could not parse BPMN for script/form extraction: {exc}"],
            "diagnostics": diagnostics,
        }

    for node in root.iter():
        local = _xml_local(node.tag)
        element_id = node.attrib.get("id")
        if not element_id:
            continue
        if local == "scriptTask":
            diagnostics["scriptTasks"] += 1
        if local == "userTask":
            diagnostics["userTasks"] += 1
        if local == "sequenceFlow":
            diagnostics["sequenceFlows"] += 1

        if not _is_bpmn_element_for_sidecar(local):
            continue

        attrs = _attrs_by_local_name(node)
        property_payload = {
            "elementId": element_id,
            "elementType": _bpmn_js_type(local),
            "elementName": node.attrib.get("name", ""),
            "documentation": _first_child_text(node, "documentation"),
            "importedFrom": source_name,
            "rawAttributes": _prefixed_attrs(node),
        }
        property_payload.update(_collibra_execution_defaults(local))
        for key in (
            "formKey",
            "candidateUsers",
            "candidateGroups",
            "assignee",
            "owner",
            "dueDate",
            "priority",
            "category",
            "taskIdVariableName",
            "autoStoreVariables",
            "async",
            "exclusive",
            "delegateExpression",
            "expression",
            "class",
            "type",
            "triggerable",
            "skipExpression",
            "formFieldValidation",
        ):
            if key in attrs:
                property_payload[key] = attrs[key]

        if local == "scriptTask":
            script = _clean_embedded_script(_first_child_text(node, "script"))
            if script:
                diagnostics["embeddedScripts"] += 1
                scripts[element_id] = {
                    "groovy": script,
                    "elementId": element_id,
                    "elementType": _bpmn_js_type(local),
                    "elementName": node.attrib.get("name", ""),
                    "source": source_name,
                    "scriptFormat": attrs.get("scriptFormat", "groovy"),
                    "importedFrom": "bpmn:scriptTask",
                }
                property_payload["scriptFormat"] = attrs.get("scriptFormat", "groovy")

        if local == "sequenceFlow":
            condition = _first_child_text(node, "conditionExpression")
            listener_code = _first_child_text(node, "transitionListenerGroovy")
            property_payload["condition"] = condition
            property_payload["skipExpression"] = attrs.get("skipExpression", "")
            property_payload["flowType"] = (
                "conditional" if condition else "skip" if attrs.get("skipExpression") else "listener" if listener_code else "normal"
            )
            if listener_code:
                property_payload["listenerCode"] = listener_code

        inline_fields = _inline_form_properties(node)
        if inline_fields:
            property_payload["inlineFormProperties"] = inline_fields
            existing_form_key = property_payload.get("formKey")
            form_key = f"{element_id}InlineForm" if existing_form_key and existing_form_key in known_forms else (existing_form_key or f"{element_id}InlineForm")
            if not existing_form_key:
                property_payload["formKey"] = form_key
            inline_forms[form_key] = {
                "key": form_key,
                "name": f"{node.attrib.get('name') or element_id} Inline Form",
                "description": "Inline flowable:formProperty definitions extracted from BPMN.",
                "modelType": "inline-form",
                "source": source_name,
                "ownerElementId": element_id,
                "fields": inline_fields,
                "outcomes": [field for field in inline_fields if field.get("type") == "taskButton"],
                "rows": [],
                "metadata": {"key": form_key, "name": f"{node.attrib.get('name') or element_id} Inline Form"},
            }
            diagnostics["inlineForms"] += 1

        if property_payload.get("formKey"):
            diagnostics["formReferences"] += 1
            form_key = property_payload["formKey"]
            if form_key not in known_forms and form_key not in inline_forms:
                diagnostics["missingForms"].append({"elementId": element_id, "formKey": form_key})

        element_properties[element_id] = property_payload

    if diagnostics["missingForms"]:
        missing = ", ".join(f"{item['elementId']}->{item['formKey']}" for item in diagnostics["missingForms"][:8])
        warnings.append(f"Missing form definitions for {missing}.")
    return {
        "scripts": scripts,
        "elementProperties": element_properties,
        "forms": inline_forms,
        "warnings": warnings,
        "diagnostics": diagnostics,
    }


def _run_package_quality_loop(model: BpmnModel, app_model: dict, forms: dict | list, max_iterations: int) -> dict:
    scripts = app_model.get("scripts") or {}
    element_properties = app_model.get("elementProperties") or {}
    form_map = dict(_workbench_form_items(forms))
    iterations: list[dict] = []
    repaired_scripts = dict(scripts)
    for iteration in range(1, max(1, max_iterations) + 1):
        compile_results = {}
        changed = False
        for element_id, script_info in repaired_scripts.items():
            groovy = script_info.get("groovy", "") if isinstance(script_info, dict) else str(script_info)
            result = groovy_compiler.compile_script(groovy)
            if not result.ok:
                repaired = _deterministic_groovy_repair(groovy)
                if repaired != groovy:
                    changed = True
                    if isinstance(script_info, dict):
                        repaired_scripts[element_id] = {**script_info, "groovy": repaired, "repairedAtIteration": iteration}
                    else:
                        repaired_scripts[element_id] = {"groovy": repaired, "repairedAtIteration": iteration}
                    result = groovy_compiler.compile_script(repaired)
            compile_results[element_id] = _compile_result_dict(result)
        structural_errors = model.validate()
        form_issues = _validate_workbench_forms(form_map, element_properties)
        missing_script_issues = _missing_script_issues(model, repaired_scripts)
        errors = structural_errors + [issue for issue in form_issues if issue["severity"] == "error"]
        errors += [
            _compile_failure_message(element_id, issue)
            for element_id, issue in compile_results.items()
            if not issue.get("ok")
        ]
        iterations.append(
            {
                "iteration": iteration,
                "changed": changed,
                "structuralErrors": structural_errors,
                "formIssues": form_issues,
                "missingScriptIssues": missing_script_issues,
                "compileResults": compile_results,
            }
        )
        if not changed:
            break
    final_iteration = iterations[-1] if iterations else {}
    final_compile = final_iteration.get("compileResults", {})
    blocking = []
    blocking.extend(final_iteration.get("structuralErrors", []))
    blocking.extend(issue["message"] for issue in final_iteration.get("formIssues", []) if issue["severity"] == "error")
    blocking.extend(_compile_failure_message(element_id, result) for element_id, result in final_compile.items() if not result.get("ok"))
    total_checks = max(1, len(model.nodes) + len(model.flows) + len(form_map) + max(1, len(repaired_scripts)))
    passed_checks = max(0, total_checks - len(blocking))
    pass_percent = round((passed_checks / total_checks) * 100, 2)
    status = "passed" if not blocking else "failed"
    summary_text = (
        f"Autonomous package test {status}. Pass rate {pass_percent}% "
        f"({passed_checks}/{total_checks} checks). Iterations: {len(iterations)}. "
        f"{'Blocking issues: ' + '; '.join(blocking[:6]) if blocking else 'No blocking BPMN, form, sequence-flow or Groovy issues remain.'}"
    )
    return {
        "ok": not blocking,
        "status": status,
        "message": summary_text,
        "summaryText": summary_text,
        "metrics": {
            "totalChecks": total_checks,
            "passedChecks": passed_checks,
            "failedChecks": len(blocking),
            "passPercent": pass_percent,
        },
        "summary": {
            "processId": model.process_id,
            "nodes": len(model.nodes),
            "flows": len(model.flows),
            "forms": len(form_map),
            "scripts": len(repaired_scripts),
            "iterations": len(iterations),
            "blockingIssues": len(blocking),
            "passPercent": pass_percent,
        },
        "blockingIssues": blocking,
        "iterations": iterations,
        "repairedAppModel": {**app_model, "scripts": repaired_scripts},
    }


def _generate_business_test_cases(model: BpmnModel, app_model: dict, forms: dict | list, business_use_case: str) -> list[dict]:
    form_map = dict(_workbench_form_items(forms))
    scripts = app_model.get("scripts") or {}
    element_properties = app_model.get("elementProperties") or {}
    cases: list[dict] = [
        {
            "id": "ai_happy_path",
            "source": "ai-business",
            "name": f"Happy path - {model.name}",
            "objective": business_use_case or "Validate the primary successful workflow path.",
            "steps": [
                "Start the workflow.",
                "Complete every required start/user form field with valid values.",
                "Take the approval or completion path through all required service/script tasks.",
                "Verify the workflow reaches an expected end event.",
            ],
            "expected": [
                "BPMN structure is valid.",
                "All referenced forms are available.",
                "All extracted Groovy scripts pass the autonomous compile/lint loop.",
            ],
            "requires": ["bpmn", "forms", "scripts"],
        }
    ]
    if any(flow.flow_type in {"conditional", "default"} or flow.condition for flow in model.flows):
        cases.append(
            {
                "id": "ai_gateway_paths",
                "source": "ai-business",
                "name": "Gateway and alternate-path coverage",
                "objective": "Validate approval, rejection, fallback and conditional sequence-flow behavior.",
                "steps": [
                    "Exercise each named conditional sequence flow.",
                    "Exercise default or otherwise paths where available.",
                    "Confirm every path has a target and reaches a terminal or follow-up task.",
                ],
                "expected": ["No missing source/target references.", "Conditional expressions are preserved in BPMN metadata."],
                "requires": ["bpmn"],
            }
        )
    if form_map:
        cases.append(
            {
                "id": "ai_required_forms",
                "source": "ai-business",
                "name": "Required form field validation",
                "objective": "Validate that imported Collibra forms expose required fields, labels, field IDs and outcomes.",
                "steps": [
                    "Open each form task from the BPMN canvas.",
                    "Render linked form fields.",
                    "Submit with valid values and verify task completion metadata.",
                    "Submit with missing required values and verify validation prevents completion.",
                ],
                "expected": ["Every form task references an imported or inline form.", "Required fields are visible in the rendered form preview."],
                "requires": ["forms"],
            }
        )
    if scripts:
        cases.append(
            {
                "id": "ai_script_compile",
                "source": "ai-business",
                "name": "Groovy script compile and standards validation",
                "objective": "Validate all imported and generated Groovy scripts before export.",
                "steps": [
                    "Extract scripts from BPMN script tasks and sidecar Groovy files.",
                    "Run static Collibra workflow standards checks.",
                    "Run Groovy shell compilation when Groovy is configured.",
                    "Apply deterministic repair and rerun until no blocking issues remain.",
                ],
                "expected": ["Every script task has extracted Groovy.", "No blocking compile or standards issues remain."],
                "requires": ["scripts"],
            }
        )
    if element_properties:
        cases.append(
            {
                "id": "ai_import_roundtrip",
                "source": "ai-business",
                "name": "Import/export package fidelity",
                "objective": "Validate imported Collibra metadata survives export and re-import.",
                "steps": [
                    "Import the Collibra ZIP.",
                    "Verify BPMN, forms, app metadata and scripts appear in the workbench.",
                    "Export the package.",
                    "Re-import exported package and compare BPMN/forms/scripts counts.",
                ],
                "expected": ["The package can be exported without losing scripts, forms or element properties."],
                "requires": ["bpmn", "forms", "scripts"],
            }
        )
    return cases


def _parse_user_test_cases(text: str) -> list[dict]:
    lines = [line.strip(" -\t") for line in str(text or "").splitlines() if line.strip(" -\t")]
    cases: list[dict] = []
    current: dict | None = None
    for line in lines:
        lowered = line.lower()
        is_new = lowered.startswith(("test:", "case:", "scenario:", "tc")) or (line[:2].isdigit() and "." in line[:4])
        if is_new or current is None:
            if current:
                cases.append(current)
            name = line.split(":", 1)[1].strip() if ":" in line else line
            current = {
                "id": f"user_case_{len(cases) + 1}",
                "source": "user",
                "name": name or f"User test case {len(cases) + 1}",
                "objective": name or line,
                "steps": [],
                "expected": [],
                "requires": ["bpmn"],
            }
            continue
        if lowered.startswith(("expect", "expected", "then", "verify")):
            current["expected"].append(line)
        else:
            current["steps"].append(line)
    if current:
        cases.append(current)
    return cases


def _execute_business_test_cases(
    model: BpmnModel,
    app_model: dict,
    forms: dict | list,
    cases: list[dict],
    package_result: dict,
) -> list[dict]:
    form_map = dict(_workbench_form_items(forms))
    scripts = app_model.get("scripts") or {}
    element_properties = app_model.get("elementProperties") or {}
    form_refs = {
        element_id: props.get("formKey")
        for element_id, props in element_properties.items()
        if isinstance(props, dict) and props.get("formKey")
    }
    results: list[dict] = []
    for case in cases:
        failures: list[str] = []
        warnings: list[str] = []
        requires = set(case.get("requires") or [])
        if "bpmn" in requires and model.validate():
            failures.extend(model.validate())
        if "forms" in requires:
            missing_forms = [f"{element_id}->{form_key}" for element_id, form_key in form_refs.items() if form_key not in form_map]
            if missing_forms:
                failures.append("Missing linked forms: " + ", ".join(missing_forms[:8]))
            required_fields = [
                f"{key}.{field.get('id')}"
                for key, form in form_map.items()
                for field in (form.get("fields") or [])
                if field.get("required")
            ]
            if not required_fields:
                warnings.append("No required fields were found in imported forms.")
        if "scripts" in requires:
            script_task_ids = [node.id for node in model.nodes if node.type == "scriptTask"]
            missing_scripts = [node_id for node_id in script_task_ids if node_id not in scripts]
            if missing_scripts:
                failures.append("Missing Groovy for script tasks: " + ", ".join(missing_scripts[:8]))
            if not package_result.get("ok"):
                failures.extend(package_result.get("blockingIssues") or ["Package quality loop failed."])
        if case.get("source") == "user" and not (case.get("steps") or case.get("expected")):
            warnings.append("User test has no explicit steps or expectations; treated as a named scenario.")
        results.append(
            {
                "id": case.get("id"),
                "name": case.get("name"),
                "source": case.get("source"),
                "status": "failed" if failures else "passed",
                "failures": failures,
                "warnings": warnings,
                "executedChecks": sorted(requires),
            }
        )
    return results


def _validate_workbench_forms(forms: dict[str, dict], element_properties: dict) -> list[dict]:
    issues: list[dict] = []
    for key, form in forms.items():
        fields = form.get("fields") if isinstance(form, dict) else []
        seen: set[str] = set()
        for field in fields or []:
            field_id = str(field.get("id") or "")
            if not field_id:
                issues.append({"severity": "error", "message": f"Form {key} contains a field without an id."})
            if field_id in seen:
                issues.append({"severity": "error", "message": f"Form {key} has duplicate field id {field_id}."})
            seen.add(field_id)
    for element_id, props in (element_properties or {}).items():
        form_key = props.get("formKey") if isinstance(props, dict) else None
        if form_key and form_key not in forms:
            issues.append({"severity": "error", "message": f"Element {element_id} references missing form {form_key}."})
    return issues


def _compile_failure_message(element_id: str, result: dict) -> str:
    standards = result.get("standards") or []
    standard_text = "; ".join(issue.get("message", "") for issue in standards if issue.get("severity") == "error")
    detail = result.get("stderr") or result.get("stdout") or standard_text or "compile failed"
    return f"{element_id}: {detail}"


def _missing_script_issues(model: BpmnModel, scripts: dict) -> list[dict]:
    issues: list[dict] = []
    for node in model.nodes:
        if node.type == "scriptTask" and node.id not in scripts and not node.script.strip():
            issues.append({"severity": "warning", "message": f"Script task {node.id} has no extracted Groovy script."})
    return issues


def _deterministic_groovy_repair(script: str) -> str:
    repaired = str(script or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if repaired.startswith("// #importFile NONE"):
        repaired = "\n".join(repaired.splitlines()[1:]).lstrip()
    return repaired


def _inline_form_properties(node: ET.Element) -> list[dict]:
    fields: list[dict] = []
    for prop in node.iter():
        if _xml_local(prop.tag) != "formProperty":
            continue
        attrs = _attrs_by_local_name(prop)
        field_id = attrs.get("id") or f"formProperty_{len(fields) + 1}"
        fields.append(
            {
                "id": field_id,
                "name": attrs.get("name") or field_id,
                "label": attrs.get("name") or field_id,
                "type": attrs.get("type") or "string",
                "required": attrs.get("required", "false") == "true",
                "readable": attrs.get("readable", "true") != "false",
                "writable": attrs.get("writable", "true") != "false",
                "value": attrs.get("default") or attrs.get("value"),
                "expression": attrs.get("expression"),
                "variable": attrs.get("variable"),
            }
        )
    return fields


def _first_child_text(node: ET.Element, local_name: str) -> str:
    for child in node:
        if _xml_local(child.tag) == local_name:
            return "".join(child.itertext()).strip()
    return ""


def _attrs_by_local_name(node: ET.Element) -> dict[str, str]:
    return {_xml_local(key): value for key, value in node.attrib.items()}


def _prefixed_attrs(node: ET.Element) -> dict[str, str]:
    return {_xml_prefixed_name(key): value for key, value in node.attrib.items()}


def _xml_local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag.split(":", 1)[-1]


def _xml_prefixed_name(tag: str) -> str:
    if tag.startswith("{http://flowable.org/bpmn}"):
        return "flowable:" + _xml_local(tag)
    if tag.startswith("{http://www.omg.org/spec/BPMN/20100524/MODEL}"):
        return "bpmn:" + _xml_local(tag)
    if tag.startswith("{http://flowable.org/design}"):
        return "design:" + _xml_local(tag)
    return _xml_local(tag)


def _clean_embedded_script(script: str) -> str:
    return str(script or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def _is_bpmn_element_for_sidecar(local: str) -> bool:
    return local in {
        "startEvent",
        "endEvent",
        "intermediateCatchEvent",
        "intermediateThrowEvent",
        "boundaryEvent",
        "userTask",
        "scriptTask",
        "serviceTask",
        "sendTask",
        "receiveTask",
        "manualTask",
        "businessRuleTask",
        "callActivity",
        "subProcess",
        "exclusiveGateway",
        "parallelGateway",
        "inclusiveGateway",
        "eventBasedGateway",
        "sequenceFlow",
        "participant",
        "lane",
    }


def _bpmn_js_type(local: str) -> str:
    parts = {
        "startEvent": "StartEvent",
        "endEvent": "EndEvent",
        "intermediateCatchEvent": "IntermediateCatchEvent",
        "intermediateThrowEvent": "IntermediateThrowEvent",
        "boundaryEvent": "BoundaryEvent",
        "userTask": "UserTask",
        "scriptTask": "ScriptTask",
        "serviceTask": "ServiceTask",
        "sendTask": "SendTask",
        "receiveTask": "ReceiveTask",
        "manualTask": "ManualTask",
        "businessRuleTask": "BusinessRuleTask",
        "callActivity": "CallActivity",
        "subProcess": "SubProcess",
        "exclusiveGateway": "ExclusiveGateway",
        "parallelGateway": "ParallelGateway",
        "inclusiveGateway": "InclusiveGateway",
        "eventBasedGateway": "EventBasedGateway",
        "sequenceFlow": "SequenceFlow",
        "participant": "Participant",
        "lane": "Lane",
    }
    return f"bpmn:{parts.get(local, local[:1].upper() + local[1:])}"


def _collibra_execution_defaults(local: str) -> dict:
    if local == "userTask":
        return {"execution": "user-form", "scope": "asset"}
    if local == "scriptTask":
        return {"execution": "script-groovy", "scope": "asset"}
    if local == "serviceTask":
        return {"execution": "service-groovy", "scope": "asset"}
    if local == "sendTask":
        return {"execution": "notification", "scope": "global"}
    if local.endswith("Gateway") or local == "sequenceFlow":
        return {"execution": "gateway-condition", "scope": "global"}
    if local in {"participant", "lane", "subProcess"}:
        return {"execution": "container", "scope": "global"}
    return {"execution": "service-groovy", "scope": "asset"}


def _sequence_flow_patch(instruction: str, target: dict) -> dict:
    lowered = instruction.lower()
    patch: dict = {"documentation": instruction}
    if "reject" in lowered or "decline" in lowered:
        patch.update({"flow_type": "conditional", "condition": "${approvalDecision != 'approve'}", "name": "Reject"})
    elif "approve" in lowered or "approved" in lowered:
        patch.update({"flow_type": "conditional", "condition": "${approvalDecision == 'approve'}", "name": "Approve"})
    elif "default" in lowered or "otherwise" in lowered:
        patch.update({"flow_type": "default", "is_default": True, "name": target.get("name") or "Otherwise"})
    elif "skip" in lowered:
        patch.update({"flow_type": "skip", "skip_expression": "${skipFlow == true}"})
    else:
        patch.update({"flow_type": target.get("flow_type", "normal")})
    return patch


def _block_patch(instruction: str, target: dict) -> dict:
    lowered = instruction.lower()
    if target.get("type") == "scriptTask" or "groovy" in lowered:
        return {
            "documentation": instruction,
            "script": "import java.util.UUID\n\nString assetId = execution.getVariable(\"assetId\") as String\nif (assetId?.trim()) {\n    execution.setVariable(\"assetIdNormalized\", UUID.fromString(assetId.trim()).toString())\n}\n",
        }
    return {"documentation": instruction}


def _empty_app_model(name: str) -> dict:
    return {
        "metadata": {"name": name, "format": "DSC_SIDE_CAR_APP_V1"},
        "scripts": {},
        "forms": {},
        "uuidMappings": {},
        "validationRules": [],
        "elementProperties": {},
    }


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _looks_like_bpmn(xml: str) -> bool:
    sample = str(xml or "")[:16000].lower()
    return "<bpmn:definitions" in sample or ("<definitions" in sample and ("bpmn" in sample or "www.omg.org/spec/bpmn" in sample))


def _sanitize_bpmn_xml(xml: str) -> str:
    clean = str(xml or "").lstrip("\ufeff").strip()
    starts = [clean.find("<?xml"), clean.find("<bpmn:definitions"), clean.find("<definitions")]
    starts = sorted(index for index in starts if index >= 0)
    if starts and starts[0] > 0:
        clean = clean[starts[0] :]
    return clean.strip()


def _parse_json_or_text(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _basename(path: str) -> str:
    return Path(path.replace("\\", "/")).name.rsplit(".", 1)[0]


def _deep_merge(left: dict, right: dict) -> dict:
    result = dict(left or {})
    for key, value in (right or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _safe_filename(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in "._-" else "_" for char in str(value)).strip("_")
    return safe or "workflow"


def _pydantic_dict(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


async def _save_rag_uploads(files: list[UploadFile]) -> list[Path]:
    upload_dir = settings.paths.docs_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for file in files:
        filename = _safe_filename(file.filename or "upload")
        if not _allowed_upload_name(filename):
            raise HTTPException(status_code=400, detail=f"Unsupported upload type: {filename}")
        target = upload_dir / filename
        target.write_bytes(await _read_upload_limited(file))
        saved.append(target)
    return saved


async def _read_upload_limited(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Upload exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
        )
    return data


def _allowed_upload_name(filename: str) -> bool:
    lower = filename.lower()
    return any(lower.endswith(suffix) for suffix in ALLOWED_UPLOAD_SUFFIXES)


def _validated_zip_member_names(package: zipfile.ZipFile) -> list[str]:
    names: list[str] = []
    for info in package.infolist():
        name = info.filename.replace("\\", "/")
        if not name or name.endswith("/"):
            continue
        if name.startswith("/") or ".." in Path(name).parts:
            raise HTTPException(status_code=400, detail=f"Unsafe ZIP member path: {info.filename}")
        if info.file_size > MAX_ZIP_MEMBER_BYTES:
            raise HTTPException(status_code=413, detail=f"ZIP member is too large: {info.filename}")
        names.append(info.filename)
        if len(names) > MAX_ZIP_MEMBERS:
            raise HTTPException(status_code=413, detail="ZIP contains too many files.")
    return names


def _workbench_rag_status(stats: dict) -> dict:
    kind_counts = stats.get("kind_counts") or {}
    return {
        "recordCount": stats.get("chunks") or stats.get("vector_count") or 0,
        "sourceFileCount": stats.get("documents") or 0,
        "uuidCount": stats.get("uuid_buckets") or 0,
        "tableCount": kind_counts.get("xlsx", 0) + kind_counts.get("xls", 0) + kind_counts.get("csv", 0),
        "elementCount": (stats.get("bpmn_nodes") or 0) + (stats.get("sequence_flows") or 0),
        "relations": stats.get("relations") or 0,
        "warnings": stats.get("warnings") or [],
    }


def _search_result_payload(result) -> dict:
    return {
        "fileName": Path(result.chunk.source_path).name,
        "sourcePath": result.chunk.source_path,
        "kind": result.chunk.kind,
        "score": result.score,
        "text": result.chunk.text,
        "metadata": result.chunk.metadata,
    }


def _selected_model_id(payload: dict | None = None) -> str:
    requested = ""
    if isinstance(payload, dict):
        requested = str(payload.get("modelId") or payload.get("model_id") or payload.get("model") or "").strip()
    return requested or active_model_id


def _simulation_payload(model: BpmnModel, result) -> dict:
    payload = asdict(result)
    total_nodes = max(1, len(model.nodes))
    completed = len([step for step in result.steps if step.status == "completed"])
    waiting = len([step for step in result.steps if step.status == "waiting"])
    errored = len(result.errors)
    percent = round(min(100.0, (completed / total_nodes) * 100), 2)
    status = "failed" if errored else "waiting" if waiting else "passed" if percent >= 100 or result.steps else "not-run"
    final_step = result.steps[-1].name if result.steps else "No step executed"
    summary_text = (
        f"Simulation {status}. Completed {completed} of {len(model.nodes)} BPMN blocks "
        f"({percent}%). Final observed step: {final_step}. "
        f"{'Errors: ' + '; '.join(result.errors[:5]) if result.errors else 'No blocking simulation errors were found.'}"
    )
    payload.update(
        {
            "status": status,
            "summaryText": summary_text,
            "metrics": {
                "totalBlocks": len(model.nodes),
                "completedBlocks": completed,
                "waitingBlocks": waiting,
                "errorCount": errored,
                "completionPercent": percent,
            },
        }
    )
    return payload


def _ai_or_compat_groovy(element: dict, prompt: str, context: str, model_id: str) -> str:
    request = f"""You are generating Collibra Workflow Designer Groovy, not Java.
Return only compile-safe Groovy code for the selected BPMN element.

Element:
{json.dumps(element, indent=2, default=str)}

User instruction:
{prompt}

Retrieved RAG and organization context:
{context[:8000]}

Rules:
- Use Groovy syntax and explicit imports.
- Use Collibra Java API v2 DTO builder classes only when grounded by context or obvious package names.
- For sequence flows, return Groovy/listener guidance as code comments plus a JUEL condition example.
- Never output markdown fences.
"""
    text = request_text_completion(settings, request, model_id=model_id, action="groovy_generation")
    code = _strip_code_fence(text or "")
    return code if code.strip() else _compat_groovy(element, prompt, context)


def _business_rag_answer(question: str, context: str, results: list[dict], model_id: str) -> str:
    prompt = f"""Use the retrieved Collibra workflow knowledge to answer for a business user.
Explain what the evidence means, the practical workflow impact, and any risks or next steps.
Do not merely paste search chunks.

Question:
{question}

Retrieved evidence:
{context[:9000]}

Sources:
{json.dumps([{ "file": r.get("fileName"), "score": r.get("score") } for r in results[:8]], indent=2)}
"""
    answer = request_text_completion(settings, prompt, model_id=model_id, action="rag_business_answer")
    if answer and answer.strip():
        return answer.strip()
    source_lines = "\n".join(f"- {result.get('fileName')}: score {float(result.get('score') or 0):.3f}" for result in results[:6])
    return (
        "Here is the business interpretation from the local RAG evidence.\n\n"
        f"The most relevant documents point to: {question}. Review the sources below first, then use the retrieved "
        "BPMN, form, UUID, role and Groovy details as organization-specific design constraints.\n\n"
        f"Sources:\n{source_lines}\n\n"
        f"Evidence excerpt:\n{context[:3500]}"
    )


def _ai_documentation_narrative(markdown: str, instruction: str, model_id: str) -> str:
    prompt = f"""Improve this Collibra workflow documentation for business and platform users.
Keep it concise, deployment-oriented, and explain the purpose, route logic, forms, Groovy, tests, risks and operating procedure.

User instruction:
{instruction}

Draft documentation:
{markdown[:10000]}
"""
    answer = request_text_completion(settings, prompt, model_id=model_id, action="workflow_documentation")
    return (answer or "").strip()


def _strip_code_fence(text: str) -> str:
    value = str(text or "").strip()
    match = re.search(r"```(?:groovy|java|text)?\s*(.*?)```", value, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return value


def _compat_groovy(element: dict, prompt: str, context: str) -> str:
    element_type = str(element.get("type", ""))
    element_id = element.get("id", "selectedElement")
    if "SequenceFlow" in element_type or "Gateway" in element_type:
        return """// Condition/listener guidance for this BPMN element.
// Use this as a sequence-flow condition when appropriate:
// ${approvalDecision == 'approve'}

def approvalDecision = execution.getVariable('approvalDecision')
execution.setVariable('lastEvaluatedFlow', '%s')
return approvalDecision != null
""" % element_id
    return """import java.util.UUID

// Generated for BPMN element: %s
// Prompt: %s
// Retrieved Collibra context is available in the AI console response.

String assetId = execution.getVariable('assetId') as String
if (assetId?.trim()) {
    execution.setVariable('assetIdNormalized', UUID.fromString(assetId.trim()).toString())
}

execution.setVariable('collibraWorkflowStep', '%s')
""" % (element_id, prompt[:300].replace("\n", " "), element_id)


ELEMENT_CATALOG = [
    {"id": "startEvent", "type": "startEvent", "label": "Start Event", "category": "Events"},
    {"id": "timerCatchEvent", "type": "intermediateCatchEvent", "label": "Timer Catch", "category": "Events", "properties": {"eventDefinition": "timer"}},
    {"id": "messageCatchEvent", "type": "intermediateCatchEvent", "label": "Message Catch", "category": "Events", "properties": {"eventDefinition": "message"}},
    {"id": "signalThrowEvent", "type": "intermediateThrowEvent", "label": "Signal Throw", "category": "Events", "properties": {"eventDefinition": "signal"}},
    {"id": "errorBoundaryEvent", "type": "boundaryEvent", "label": "Error Boundary", "category": "Events", "properties": {"eventDefinition": "error"}},
    {"id": "endEvent", "type": "endEvent", "label": "End Event", "category": "Events"},
    {"id": "userTask", "type": "userTask", "label": "User Task", "category": "Tasks"},
    {"id": "scriptTask", "type": "scriptTask", "label": "Script Task", "category": "Tasks", "properties": {"scriptLanguage": "groovy"}},
    {"id": "serviceTask", "type": "serviceTask", "label": "Service Task", "category": "Tasks"},
    {"id": "collibraApiTask", "type": "serviceTask", "label": "Collibra API Task", "category": "Tasks", "properties": {"type": "collibra-api"}},
    {"id": "emailTask", "type": "sendTask", "label": "Email Task", "category": "Tasks", "properties": {"type": "email"}},
    {"id": "manualTask", "type": "manualTask", "label": "Manual Task", "category": "Tasks"},
    {"id": "businessRuleTask", "type": "businessRuleTask", "label": "Business Rule", "category": "Tasks"},
    {"id": "receiveTask", "type": "receiveTask", "label": "Receive Task", "category": "Tasks"},
    {"id": "exclusiveGateway", "type": "exclusiveGateway", "label": "Exclusive Gateway", "category": "Gateways"},
    {"id": "parallelGateway", "type": "parallelGateway", "label": "Parallel Gateway", "category": "Gateways"},
    {"id": "inclusiveGateway", "type": "inclusiveGateway", "label": "Inclusive Gateway", "category": "Gateways"},
    {"id": "eventBasedGateway", "type": "eventBasedGateway", "label": "Event Gateway", "category": "Gateways"},
    {"id": "subProcess", "type": "subProcess", "label": "Subprocess", "category": "Structures"},
    {"id": "callActivity", "type": "callActivity", "label": "Call Activity", "category": "Structures"},
    {"id": "textAnnotation", "type": "textAnnotation", "label": "Text Annotation", "category": "Artifacts"},
    {"id": "sequenceFlow", "type": "sequenceFlow", "label": "Sequence Flow", "category": "Connectors"},
    {"id": "conditionalFlow", "type": "sequenceFlow", "label": "Conditional Flow", "category": "Connectors", "properties": {"flow_type": "conditional", "condition": "${approvalDecision == 'approve'}"}},
    {"id": "defaultFlow", "type": "sequenceFlow", "label": "Default Flow", "category": "Connectors", "properties": {"flow_type": "default", "is_default": True}},
]


FORM_COMPONENTS = [
    "Text",
    "Multiline Text",
    "Rich Text",
    "Date",
    "File Upload",
    "Asset Type",
    "Domain Type",
    "Attribute Type",
    "Relation Type",
    "User",
    "Group",
    "Role",
    "Asset",
    "Domain",
    "Community",
    "Role In Community",
    "Radio Buttons",
    "Checkbox",
    "Checkbox Group",
    "Select Single",
    "Select Multiple",
    "Subform",
]
