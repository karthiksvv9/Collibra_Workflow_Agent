from __future__ import annotations

import io
import json
import re
import time
import zipfile
from dataclasses import asdict
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from xml.etree import ElementTree as ET

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.agents.groovy_compiler import GroovyCompiler
from src.agents.groovy_ootb import load_ootb_groovy_profile
from src.agents.llm_client import (
    LLMRequestError,
    model_api_key_configured,
    model_options_payload,
    request_text_completion,
    resolve_model_profile,
)
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
from src.workflow.bpmn import (
    DI_NS,
    DSC_NS,
    FLOWABLE_NS,
    XSI_NS,
    BpmnModel,
    BpmnNode,
    BpmnPool,
    SequenceFlow,
    diagram_waypoints,
)
from src.workflow.form import FormField, FormModel, form_field_from_mapping
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
active_model_id = resolve_model_profile(settings).id
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
            "One shared enterprise API key can be configured as models.api_key or openai.api_key in config.yaml and is never returned by this endpoint.",
        ],
    }


@app.post("/api/models/select")
def select_model(payload: dict) -> dict:
    global active_model_id
    requested = str(payload.get("modelId") or payload.get("id") or "").strip()
    if not requested:
        raise HTTPException(status_code=400, detail="modelId is required.")
    try:
        profile = resolve_model_profile(settings, requested)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not model_api_key_configured(settings, profile.id):
        raise HTTPException(
            status_code=400,
            detail=(
                f"API key is not configured for {profile.label or profile.id}. "
                "Set models.api_key once in config.yaml or set the shared openai.api_key/openai.api_key_env value, then restart."
            ),
        )
    if payload.get("validateConnection", True) is not False:
        try:
            probe = request_text_completion(
                settings,
                "Reply with OK only.",
                model_id=profile.id,
                action="model_connection_test",
                raise_on_error=True,
            )
        except (LLMRequestError, ValueError) as exc:
            log_action(
                "model_selection_failed",
                status="error",
                detail={"modelId": profile.id, "provider": profile.provider, "model": profile.model, "error": _safe_public_error(str(exc))},
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Model profile '{profile.label or profile.id}' failed API validation. "
                    f"Check the endpoint, model name and API key in config.yaml. Provider error: {_safe_public_error(str(exc))}"
                ),
            ) from exc
        if not str(probe or "").strip():
            raise HTTPException(
                status_code=400,
                detail=f"Model profile '{profile.label or profile.id}' returned an empty validation response. Check config.yaml.",
            )
    active_model_id = profile.id
    log_action("model_selected", detail={"modelId": profile.id, "provider": profile.provider, "model": profile.model, "validated": True})
    return {"activeModelId": active_model_id, "model": profile.id, "provider": profile.provider, "validated": True}


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
    result = agent.build(request.master_prompt, request.output_name, model_id=request.modelId or active_model_id)
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
        safe_name = _compact_name_part(request.output_name, 54)
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
    chosen_bpmn_xml = chosen[2] if chosen else None
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
        chosen_bpmn_xml = _embed_app_model_scripts_in_bpmn(chosen[2], app_model)
    elif forms:
        existing_forms = app_model.get("forms") or {}
        if not isinstance(existing_forms, dict):
            app_model["manifestForms"] = existing_forms
            existing_forms = {}
        app_model["forms"] = _deep_merge(existing_forms, forms)
    return {
        "bpmnXml": chosen_bpmn_xml,
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
    package_name = _safe_filename(payload.get("packageName") or "generated-collibra-workflow.zip")
    if payload.get("withTimestamp"):
        package_name = f"{_short_export_stem(package_name)}.zip"
    else:
        package_name = f"{_compact_name_part(Path(package_name).stem or 'workflow', 64)}.zip"
    app_model = payload.get("appModel") or {}
    forms = payload.get("forms") or {}
    base_name = _compact_name_part(Path(package_name).stem or "workflow", 64)
    if payload.get("withTimestamp"):
        app_model = {
            **app_model,
            "metadata": {
                **(app_model.get("metadata") if isinstance(app_model.get("metadata"), dict) else {}),
                "timestamp": _timestamp_suffix(),
            },
        }
    export_bpmn_xml = _embed_app_model_scripts_in_bpmn(bpmn_xml, app_model)
    form_items = _workbench_form_items(_merge_export_forms(forms, app_model))
    app_manifest = _collibra_app_manifest(base_name, app_model, form_items, export_bpmn_xml)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr(f"{base_name}.bpmn", export_bpmn_xml)
        package.writestr(f"{base_name}.app", json.dumps(app_manifest, indent=2, sort_keys=True))
        for key, value in form_items:
            form_payload = _collibra_form_payload(key, value)
            package.writestr(f"form-{_safe_filename(str(key))}.form", json.dumps(form_payload, indent=2, sort_keys=True))
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
        app_model = payload.get("appModel") or {}
        forms = _form_models_from_workbench_payload(payload.get("forms") or app_model.get("forms") or {})
        result = simulator.simulate(model, forms, payload.get("formValues") or payload.get("variables") or {})
        return _simulation_payload(model, result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/agent/design")
def design_workflow_workbench(payload: dict) -> dict:
    prompt = payload.get("prompt") or payload.get("master_prompt") or "Create a Collibra governance workflow."
    model_id = _selected_model_id(payload)
    force_ai = bool(payload.get("forceAi"))
    allow_fallback = bool(payload.get("preferAi") or payload.get("allowFallback"))
    strict_ai = bool(payload.get("strictAi") or payload.get("requireAi") or (force_ai and not allow_fallback))
    try:
        result = agent.build(
            prompt,
            "agent_generated_workflow",
            model_id=model_id,
            require_ai=strict_ai,
        )
        model = result.package.process
        forms = _forms_dict_from_package(result.package)
        app_model = _app_model_from_package(result.package, result.retrieved_context)
        repair_trace: list[dict] = []
        try:
            model, app_model, forms, repair_trace = _autocorrect_model_and_app(
                model,
                app_model,
                forms,
                prompt=prompt,
                model_id=model_id,
                max_iterations=3,
            )
        except Exception as repair_exc:
            repair_trace.append({"step": "design_autocorrect", "status": "skipped", "reason": _safe_public_error(str(repair_exc))})
        return {
            "bpmnXml": _embed_app_model_scripts_in_bpmn(model.to_xml(), app_model),
            "appModel": app_model,
            "forms": forms,
            "summary": (f"Workflow generated with selected model profile: {model_id}.\n" + "\n".join(result.assumptions)).strip(),
            "trace": repair_trace,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/agent/generate-code")
def generate_code_workbench(payload: dict) -> dict:
    element = payload.get("element") or {}
    prompt = payload.get("prompt") or "Generate Collibra Groovy for the selected BPMN element."
    model_id = _selected_model_id(payload)
    context, org_profile = _groovy_generation_context(element, prompt, payload)
    groovy = _ai_or_compat_groovy(element, prompt, context, model_id, org_profile, force_ai=bool(payload.get("forceAi")))
    repair_attempts: list[dict] = []
    original_groovy = groovy
    if bool(payload.get("compileAndRepair", True)):
        groovy, compile_result, repair_attempts = _compile_and_repair_groovy(
            groovy,
            element=element,
            prompt=prompt,
            context=context,
            org_profile=org_profile,
            model_id=model_id,
            max_iterations=int(payload.get("maxRepairIterations") or 3),
        )
    else:
        compile_result = groovy_compiler.compile_script(groovy) if groovy.strip() else None
    compile_status = _compile_status(compile_result)
    warnings = []
    if compile_result:
        if compile_result.skipped:
            warnings.append("Groovy compilation was skipped because no Groovy runtime was available. Treat as not deployable until compiled.")
        elif not compile_result.ok:
            warnings.append("Groovy compilation or Collibra standards lint failed. Review compile results before export.")
        elif any(issue.severity == "warning" for issue in compile_result.standards):
            warnings.append("Groovy compiled with standards warnings. Review before deployment.")
    else:
        warnings.append("No Groovy was generated for compilation.")
    return {
        "groovy": groovy,
        "summary": f"Generated Collibra code guidance for {element.get('id', 'selected element')}.",
        "reasoning": [
            "Used the selected BPMN element metadata.",
            "Retrieved organization standards, previous Groovy, UUID/relation mappings and Collibra API hints from RAG.",
            "Planned the script around the selected block purpose, org process variables and OOTB Collibra Groovy style.",
            "Compiled and repaired the script before returning it when compile-and-repair mode was enabled.",
        ],
        "implementationPlan": _groovy_implementation_plan(element, prompt, org_profile),
        "tests": ["Compile selected Groovy.", "Run workflow simulation.", "Export ZIP and validate in a Collibra test tenant."],
        "warnings": warnings,
        "compileStatus": compile_status,
        "compileResults": [_compile_result_dict(compile_result)] if compile_result else [],
        "repairAttempts": repair_attempts,
        "originalGroovy": original_groovy,
        "repaired": bool(repair_attempts and groovy != original_groovy),
        "errorText": _compile_error_text(compile_result),
        "summaryText": _compile_summary_text(compile_result),
        "organizationProfile": org_profile,
        "context": context[:3000],
    }


@app.post("/api/agent/autonomous-run")
def autonomous_agent_run(payload: dict) -> dict:
    mode = str(payload.get("mode") or "prompt").lower()
    prompt = str(payload.get("prompt") or payload.get("businessUseCase") or "").strip()
    max_iterations = max(1, min(8, int(payload.get("maxIterations") or 5)))
    output_name = _short_export_stem(payload.get("packageName") or payload.get("outputName") or "autonomous_collibra_workflow")

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
        build_result, design_trace = _autonomous_build_from_prompt(prompt, output_name, payload)
        model = build_result.package.process
        forms = _forms_dict_from_package(build_result.package)
        app_model = _app_model_from_package(build_result.package, rag_context.render())
        trace.extend(design_trace)
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
    stitched_model, stitched_app_model, stitched_forms, stitch_trace = _autocorrect_model_and_app(
        model,
        app_model,
        forms,
        prompt=business_use_case,
        model_id=_selected_model_id(payload),
        max_iterations=max_iterations,
    )
    model, app_model, forms = stitched_model, stitched_app_model, stitched_forms
    trace.extend(stitch_trace)
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
    doc_path = settings.paths.output_dir / f"{output_name}_doc.md"
    report_path = settings.paths.output_dir / f"{output_name}_report.json"
    zip_path = settings.paths.output_dir / f"{output_name}.zip"
    doc_path.write_text(markdown, encoding="utf-8")
    _write_workbench_zip(zip_path, bpmn_xml, app_model, forms, doc_path, report_path)
    related_package_paths = [str(path) for path in _called_workflow_package_paths(zip_path, app_model) if path.exists()]
    report = {
        "mode": mode,
        "ok": bool(final_cases.get("ok")),
        "status": final_cases.get("status", "failed"),
        "trace": trace,
        "quality": final_quality,
        "cases": final_cases,
        "documentationPath": str(doc_path),
        "zipPath": str(zip_path),
        "relatedPackagePaths": related_package_paths,
        "ragContextPreview": rag_context.render()[:6000],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_workbench_zip(zip_path, bpmn_xml, app_model, forms, doc_path, report_path)
    related_package_paths = [str(path) for path in _called_workflow_package_paths(zip_path, app_model) if path.exists()]
    report["relatedPackagePaths"] = related_package_paths
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
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
        "relatedPackagePaths": related_package_paths,
        "downloadUrl": f"/api/workflows/download?path={zip_path}",
        "reportPath": str(report_path),
        "trace": trace,
    }


def _autonomous_build_from_prompt(prompt: str, output_name: str, payload: dict) -> tuple[object, list[dict]]:
    model_id = _selected_model_id(payload)
    strict_ai = bool(payload.get("strictAi") or payload.get("requireAi"))
    prefer_ai = bool(payload.get("forceAi", True) or payload.get("preferAi", True))
    trace = [
        {
            "step": "ai_design_preference",
            "status": "strict" if strict_ai else "preferred" if prefer_ai else "optional",
            "modelId": model_id,
        }
    ]
    try:
        return (
            agent.build(
                prompt,
                f"{output_name}_draft",
                model_id=model_id,
                require_ai=strict_ai,
            ),
            trace,
        )
    except Exception as exc:
        if strict_ai:
            raise
        trace.append(
            {
                "step": "ai_design_fallback",
                "status": "completed",
                "reason": _safe_public_error(str(exc)),
                "message": "AI design did not complete, so autonomous mode used deterministic RAG-backed workflow generation.",
            }
        )
        return (
            agent.build(
                prompt,
                f"{output_name}_draft",
                model_id=model_id,
                require_ai=False,
            ),
            trace,
        )


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
    try:
        context = rag_engine.retrieve(question, limit=limit)
        results = [_search_result_payload(result) for result in context.results]
        if results:
            answer = _business_rag_answer(question, context.render(), results, _selected_model_id(payload))
        else:
            answer = "No RAG results were found. Upload documents and generate the index, then ask again."
    except Exception as exc:
        log_action("rag_chat", status="error", detail={"error": str(exc), "question": question[:500]})
        results = []
        answer = (
            "RAG chat could not complete this request. The local index or selected model may need attention. "
            f"Technical detail: {exc}"
        )
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
            node.script = "// #importFile NONE\n" + node.script.lstrip()
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
    doc_base = _compact_name_part(model.process_id, 42)
    output_path = settings.paths.output_dir / f"{doc_base}_doc.md"
    html_path = settings.paths.output_dir / f"{doc_base}_doc.html"
    output_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(_markdown_to_confluence_html(markdown), encoding="utf-8")
    return {
        "markdown": markdown,
        "path": str(output_path),
        "htmlPath": str(html_path),
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


@app.post("/api/workflow/autocorrect")
def autocorrect_workbench_package(payload: dict) -> dict:
    bpmn_xml = payload.get("bpmnXml") or payload.get("bpmn_xml") or ""
    if not bpmn_xml.strip():
        raise HTTPException(status_code=400, detail="bpmnXml is required.")
    app_model = payload.get("appModel") or {}
    forms = payload.get("forms") or app_model.get("forms") or {}
    prompt = str(payload.get("prompt") or payload.get("businessUseCase") or "Autocorrect the Collibra workflow to production readiness.")
    model_id = _selected_model_id(payload)
    max_iterations = max(1, min(8, int(payload.get("maxIterations") or 6)))
    timestamp = _timestamp_suffix()
    output_base = _short_export_stem(payload.get("packageName") or "autocorrected-collibra-workflow.zip", timestamp)
    try:
        model = BpmnModel.from_xml(_sanitize_bpmn_xml(bpmn_xml))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse BPMN XML: {exc}") from exc

    repaired_model, repaired_app_model, repaired_forms, repair_trace = _autocorrect_model_and_app(
        model,
        app_model,
        forms,
        prompt=prompt,
        model_id=model_id,
        max_iterations=max_iterations,
    )
    bpmn_after = repaired_model.to_xml()
    quality = _run_package_quality_loop(repaired_model, repaired_app_model, repaired_forms, max_iterations)
    repaired_app_model = quality.get("repairedAppModel") or repaired_app_model
    bpmn_after = _embed_app_model_scripts_in_bpmn(bpmn_after, repaired_app_model)
    markdown = _workbench_documentation_markdown(
        repaired_model,
        repaired_app_model,
        repaired_forms,
        f"Autocorrect evidence for production readiness.\n\n{prompt}",
    )
    settings.paths.output_dir.mkdir(parents=True, exist_ok=True)
    doc_path = settings.paths.output_dir / f"{output_base}_doc.md"
    report_path = settings.paths.output_dir / f"{output_base}_report.json"
    zip_path = settings.paths.output_dir / f"{output_base}.zip"
    doc_path.write_text(markdown, encoding="utf-8")
    _write_workbench_zip(zip_path, bpmn_after, repaired_app_model, repaired_forms, doc_path, report_path)
    related_package_paths = [str(path) for path in _called_workflow_package_paths(zip_path, repaired_app_model) if path.exists()]
    report = {
        "ok": bool(quality.get("ok")),
        "status": quality.get("status"),
        "timestamp": timestamp,
        "modelId": model_id,
        "quality": quality,
        "trace": repair_trace,
        "zipPath": str(zip_path),
        "relatedPackagePaths": related_package_paths,
        "documentationPath": str(doc_path),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_workbench_zip(zip_path, bpmn_after, repaired_app_model, repaired_forms, doc_path, report_path)
    related_package_paths = [str(path) for path in _called_workflow_package_paths(zip_path, repaired_app_model) if path.exists()]
    report["relatedPackagePaths"] = related_package_paths
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    summary_text = (
        f"Autocorrect {quality.get('status')}. Package quality is "
        f"{quality.get('metrics', {}).get('passPercent', 0)}%. "
        f"Timestamped ZIP: {zip_path.name}. "
        f"{'All blocking issues are resolved.' if quality.get('ok') else 'Remaining blockers: ' + '; '.join((quality.get('blockingIssues') or [])[:5])}"
    )
    log_action(
        "workflow_autocorrect",
        status="ok" if quality.get("ok") else "error",
        detail={"processId": repaired_model.process_id, "passPercent": quality.get("metrics", {}).get("passPercent"), "zipPath": str(zip_path)},
    )
    return {
        "ok": bool(quality.get("ok")),
        "status": quality.get("status"),
        "summaryText": summary_text,
        "metrics": quality.get("metrics", {}),
        "bpmnXml": bpmn_after,
        "appModel": repaired_app_model,
        "forms": repaired_forms,
        "quality": quality,
        "trace": repair_trace,
        "timestamp": timestamp,
        "zipPath": str(zip_path),
        "relatedPackagePaths": related_package_paths,
        "downloadUrl": f"/api/workflows/download?path={zip_path}",
        "documentation": {"path": str(doc_path), "markdown": markdown},
        "reportPath": str(report_path),
    }


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
    code = request.code or request.script or ""
    element = request.element or {"id": request.elementId or "selectedElement", "type": "scriptTask", "name": request.elementId or "Selected element"}
    context, org_profile = _groovy_generation_context(element, request.prompt or "Compile and repair selected Collibra Groovy.", {"appModel": request.appModel})
    if request.autoRepair:
        repaired_code, result, attempts = _compile_and_repair_groovy(
            code,
            element=element,
            prompt=request.prompt or "Repair selected Collibra Groovy so it compiles and follows organization standards.",
            context=context,
            org_profile=org_profile,
            model_id=_selected_model_id({"modelId": request.modelId}),
            max_iterations=request.maxRepairIterations,
        )
    else:
        repaired_code = code
        result = groovy_compiler.compile_script(code)
        attempts = []
    payload = _compile_result_dict(result)
    payload.update(
        {
            "groovy": repaired_code,
            "repairedCode": repaired_code if repaired_code != code else "",
            "originalCode": code,
            "repaired": repaired_code != code,
            "repairAttempts": attempts,
            "organizationProfile": org_profile,
            "errorText": _compile_error_text(result),
            "summaryText": _compile_summary_text(result),
        }
    )
    return payload


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
    form_items = _workbench_form_items(_merge_export_forms(forms, app_model))
    base_name = _compact_name_part(output_path.stem.replace("_autonomous_package", "").replace("_package", "") or "workflow", 64)
    export_bpmn_xml = _embed_app_model_scripts_in_bpmn(bpmn_xml, app_model)
    app_manifest = _collibra_app_manifest(base_name, app_model, form_items, export_bpmn_xml)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr(f"{base_name}.bpmn", export_bpmn_xml)
        package.writestr(f"{base_name}.app", json.dumps(app_manifest, indent=2, sort_keys=True))
        for key, value in form_items:
            package.writestr(f"form-{_safe_filename(str(key))}.form", json.dumps(_collibra_form_payload(key, value), indent=2, sort_keys=True))
    _write_workbench_artifacts(output_path, base_name, app_model, documentation_path, report_path)
    _write_called_workflow_packages(output_path, app_model)
    return output_path


def _write_workbench_artifacts(
    output_path: Path,
    base_name: str,
    app_model: dict,
    documentation_path: Path | None = None,
    report_path: Path | None = None,
) -> None:
    artifact_dir = output_path.with_suffix("")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / f"{base_name}.dsc-sidecar.json").write_text(
        json.dumps(_json_safe_export_metadata(app_model), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    scripts_dir = artifact_dir / "groovy"
    scripts_dir.mkdir(exist_ok=True)
    for element_id, script_info in (app_model.get("scripts") or {}).items():
        groovy = script_info.get("groovy", "") if isinstance(script_info, dict) else str(script_info)
        if groovy.strip():
            (scripts_dir / f"{_compact_name_part(str(element_id), 48)}.groovy").write_text(groovy.rstrip() + "\n", encoding="utf-8")
    if documentation_path and documentation_path.exists():
        target = artifact_dir / documentation_path.name
        if documentation_path.resolve() != target.resolve():
            target.write_text(documentation_path.read_text(encoding="utf-8"), encoding="utf-8")
    if report_path and report_path.exists():
        target = artifact_dir / report_path.name
        if report_path.resolve() != target.resolve():
            target.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")


def _write_called_workflow_packages(parent_output_path: Path, app_model: dict) -> list[Path]:
    written: list[Path] = []
    for workflow in _called_workflow_items(app_model):
        process_key = _safe_model_key(workflow.get("processKey") or workflow.get("key") or "calledWorkflow")
        output_path = _called_workflow_package_path(parent_output_path, process_key)
        child_app_model = workflow.get("appModel") if isinstance(workflow.get("appModel"), dict) else {}
        child_forms = _workbench_form_items(workflow.get("forms") or child_app_model.get("forms") or {})
        child_bpmn = _embed_app_model_scripts_in_bpmn(str(workflow.get("bpmnXml") or ""), child_app_model)
        if not child_bpmn.strip():
            continue
        child_manifest = _collibra_app_manifest(
            process_key,
            {
                **child_app_model,
                "metadata": {
                    **(child_app_model.get("metadata") if isinstance(child_app_model.get("metadata"), dict) else {}),
                    "key": child_app_model.get("key") or f"{process_key}App",
                    "name": child_app_model.get("name") or workflow.get("name") or f"{process_key} App",
                },
            },
            child_forms,
            child_bpmn,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as package:
            package.writestr(f"{process_key}.bpmn", child_bpmn)
            package.writestr(f"{process_key}.app", json.dumps(child_manifest, indent=2, sort_keys=True))
            for key, value in child_forms:
                package.writestr(f"form-{_safe_filename(str(key))}.form", json.dumps(_collibra_form_payload(key, value), indent=2, sort_keys=True))
        written.append(output_path)
    return written


def _called_workflow_package_paths(parent_output_path: Path, app_model: dict) -> list[Path]:
    return [
        _called_workflow_package_path(parent_output_path, _safe_model_key(workflow.get("processKey") or workflow.get("key") or "calledWorkflow"))
        for workflow in _called_workflow_items(app_model)
    ]


def _called_workflow_package_path(parent_output_path: Path, process_key: str) -> Path:
    parent_stem = _compact_name_part(parent_output_path.stem, 40)
    child_key = _compact_name_part(process_key, 28)
    return parent_output_path.with_name(f"{parent_stem}_child_{child_key}.zip")


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
    condition = _normalize_juel_expression(data.get("condition", ""))
    skip_expression = _normalize_juel_expression(data.get("skip_expression") or data.get("skipExpression", ""))
    return SequenceFlow(
        id=data["id"],
        source_ref=data.get("source_ref") or data.get("sourceRef") or data.get("source", ""),
        target_ref=data.get("target_ref") or data.get("targetRef") or data.get("target", ""),
        name=data.get("name", ""),
        condition=condition,
        skip_expression=skip_expression,
        flow_type=data.get("flow_type") or data.get("flowType") or ("conditional" if condition else "normal"),
        is_default=bool(data.get("is_default") or data.get("isDefault", False)),
        documentation=data.get("documentation", ""),
        listener_code=data.get("listener_code") or data.get("listenerCode", ""),
        properties=data.get("properties", {}),
    )


def _normalize_juel_expression(value) -> str:
    expression = str(value or "").strip()
    if not expression:
        return ""
    if expression.startswith("${") and expression.endswith("}"):
        return expression
    if expression.lower() in {"true", "false"}:
        return "${" + expression.lower() + "}"
    if any(operator in expression for operator in ("==", "!=", ">=", "<=", ">", "<", "&&", "||")):
        return "${" + expression + "}"
    return expression


def _forms_from_payload(forms: list[dict]) -> list[FormModel]:
    return [
        FormModel(
            key=form["key"],
            name=form.get("name", form["key"]),
            fields=[form_field_from_mapping(field) for field in form.get("fields", []) if isinstance(field, dict)],
        )
        for form in forms
    ]


def _form_models_from_workbench_payload(forms: dict | list) -> list[FormModel]:
    models: list[FormModel] = []
    for key, form in _workbench_form_items(forms):
        if not isinstance(form, dict):
            continue
        form_key = str(form.get("key") or key)
        fields = form.get("fields")
        if not isinstance(fields, list) or not fields:
            fields = _flatten_collibra_form_fields(form)
        models.append(
            FormModel(
                key=form_key,
                name=str(form.get("name") or form_key),
                fields=[form_field_from_mapping(field) for field in fields if isinstance(field, dict)],
            )
        )
    return models


def _compile_result_dict(result) -> dict:
    return {
        "ok": result.ok,
        "status": _compile_status(result),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "skipped": result.skipped,
        "standards": [asdict(issue) for issue in result.standards],
        "errorText": _compile_error_text(result),
        "summaryText": _compile_summary_text(result),
    }


def _compile_status(result) -> str:
    if result is None:
        return "not-run"
    if result.ok and not result.skipped:
        return "passed"
    if result.skipped:
        return "skipped"
    return "failed"


def _compile_error_text(result) -> str:
    if result is None or result.ok:
        return ""
    standards = [issue.message for issue in result.standards if issue.severity == "error"]
    warning_text = [issue.message for issue in result.standards if issue.severity == "warning"]
    parts = [
        value.strip()
        for value in [result.stderr, result.stdout, "; ".join(standards), "; ".join(warning_text)]
        if str(value or "").strip()
    ]
    if result.skipped and not parts:
        parts.append("Groovy runtime is unavailable, so compilation was skipped. Add Groovy runtime JARs or configure groovy/java paths.")
    return "\n".join(parts).strip()


def _compile_summary_text(result) -> str:
    status = _compile_status(result)
    if status == "passed":
        warnings = [issue.message for issue in result.standards if issue.severity == "warning"]
        if warnings:
            return "Compile passed with standards warnings: " + "; ".join(warnings[:4])
        return "Compile passed. The script passed Collibra standards lint and local Groovy syntax validation."
    if status == "skipped":
        return "Compile skipped. The script was linted, but no Groovy runtime was available, so this is not deployable evidence yet."
    if status == "failed":
        return "Compile failed. Review the error text; auto-repair will use RAG, previous code and organization standards to patch the Groovy."
    return "Compile was not run."


def _compile_and_repair_groovy(
    script: str,
    *,
    element: dict,
    prompt: str,
    context: str,
    org_profile: str,
    model_id: str,
    max_iterations: int = 3,
) -> tuple[str, object, list[dict]]:
    current = str(script or "")
    attempts: list[dict] = []
    max_iterations = max(1, min(6, int(max_iterations or 3)))
    result = groovy_compiler.compile_script(current) if current.strip() else None
    if result is None:
        return current, result, attempts
    attempts.append({"iteration": 0, "strategy": "initial_compile", "result": _compile_result_dict(result)})
    for iteration in range(1, max_iterations + 1):
        if result.ok and not _requires_org_style_repair(current):
            break
        if result.skipped and not any(issue.severity == "error" for issue in result.standards) and not _requires_org_style_repair(current):
            break
        deterministic = _deterministic_groovy_repair(current)
        if deterministic != current:
            current = deterministic
            result = groovy_compiler.compile_script(current)
            attempts.append({"iteration": iteration, "strategy": "deterministic_org_standards_repair", "result": _compile_result_dict(result)})
            if result.ok:
                break
        ai_repair = _ai_repair_groovy(current, result, element, prompt, context, org_profile, model_id)
        if not ai_repair or ai_repair == current or not _looks_like_collibra_groovy_snippet(ai_repair):
            continue
        ai_repair = _deterministic_groovy_repair(ai_repair)
        if ai_repair == current:
            continue
        current = ai_repair
        result = groovy_compiler.compile_script(current)
        attempts.append({"iteration": iteration, "strategy": "ai_rag_compile_error_repair", "result": _compile_result_dict(result)})
    return current, result, attempts


def _requires_org_style_repair(script: str) -> bool:
    value = str(script or "")
    lowered = value.lower()
    return (
        "uuid.fromstring" in lowered
        or re.search(r"(?m)^\s*import\s+java\.util\.UUID\s*;?\s*$", value) is not None
        or re.search(r"(?m)^\s*import\s+(?:uuid|UUID|[\w.]*\.uuid(?:\.[\w.*]+)?)\s*;?\s*$", value, re.IGNORECASE) is not None
        or re.search(r"(?m)^\s*(?:public\s+)?class\s+\w+\b|public\s+static\s+void\s+main\s*\(", value) is not None
    )


def _ai_repair_groovy(script: str, result, element: dict, prompt: str, context: str, org_profile: str, model_id: str) -> str:
    if result is None:
        return ""
    repair_prompt = f"""You are repairing Collibra Workflow Designer Groovy.
Return only the repaired Groovy snippet. No markdown fences, no explanations.

Selected BPMN element:
{json.dumps(element, indent=2, default=str)}

Business/user instruction:
{prompt}

Compiler and standards error:
{_compile_error_text(result)}

Organization/RAG coding profile:
{org_profile}

Retrieved evidence and previous code:
{context[:9000]}

Current Groovy:
{script[:12000]}

Rules:
- Keep the script as a Groovy snippet for Collibra/Flowable, not a Java class.
- Use previous organization code patterns, variable names, role names, relation mappings and DTO imports from RAG when present.
- UUIDs are values, not packages. Do not import UUID packages. Use string2Uuid(...) for UUID conversion.
- Start script tasks with // #importFile NONE.
- Only use explicit Collibra DTO imports that are needed by this script.
- Preserve required business behavior and add defensive null checks around execution variables.
"""
    repaired = request_text_completion(settings, repair_prompt, model_id=model_id, action="groovy_compile_repair")
    return _strip_code_fence(repaired or "")


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


def _merge_export_forms(forms: dict | list, app_model: dict) -> dict | list:
    app_forms = app_model.get("forms") if isinstance(app_model, dict) else {}
    if isinstance(forms, dict) and isinstance(app_forms, dict):
        return _deep_merge(app_forms, forms)
    if isinstance(forms, dict) and forms:
        return forms
    if isinstance(app_forms, dict) and app_forms:
        return app_forms
    if isinstance(forms, list) and forms:
        return forms
    if isinstance(app_forms, list) and app_forms:
        return app_forms
    return forms


def _called_workflow_items(app_model: dict) -> list[dict]:
    if not isinstance(app_model, dict):
        return []
    raw = app_model.get("calledWorkflows") or app_model.get("childWorkflows") or {}
    if isinstance(raw, dict):
        values = raw.values()
    elif isinstance(raw, list):
        values = raw
    else:
        values = []
    workflows: list[dict] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, dict):
            continue
        process_key = _safe_model_key(value.get("processKey") or value.get("key") or _process_key_from_bpmn(str(value.get("bpmnXml") or ""), "calledWorkflow"))
        if process_key in seen:
            continue
        bpmn_xml = str(value.get("bpmnXml") or "").strip()
        if not bpmn_xml:
            continue
        workflows.append({**value, "processKey": process_key, "key": process_key})
        seen.add(process_key)
    return workflows


def _merge_called_workflow_forms(form_items: list[tuple[str, dict]], called_workflows: list[dict]) -> list[tuple[str, dict]]:
    merged: dict[str, dict] = {str(key): value for key, value in form_items}
    for workflow in called_workflows:
        for key, value in _workbench_form_items(workflow.get("forms") or (workflow.get("appModel") or {}).get("forms") or {}):
            merged.setdefault(str(key), value)
    return list(merged.items())


def _collibra_app_manifest(
    base_name: str,
    app_model: dict,
    form_items: list[tuple[str, dict]],
    bpmn_xml: str,
) -> dict:
    metadata = app_model.get("metadata") if isinstance(app_model.get("metadata"), dict) else {}
    process_key = _process_key_from_bpmn(bpmn_xml, base_name)
    app_key = _safe_model_key(metadata.get("key") or app_model.get("key") or f"{process_key}App")
    app_name = str(metadata.get("name") or app_model.get("name") or app_key)
    child_models = []
    seen_models: set[tuple[str, str]] = set()
    for key, _ in form_items:
        item = (_safe_model_key(key), "form")
        if item not in seen_models:
            child_models.append({"key": item[0], "type": item[1]})
            seen_models.add(item)
    item = (_safe_model_key(process_key), "bpmn")
    if item not in seen_models:
        child_models.append({"key": item[0], "type": item[1]})
        seen_models.add(item)
    return {
        "key": app_key,
        "name": app_name,
        "description": str(metadata.get("description") if metadata.get("description") is not None else app_model.get("description") or ""),
        "theme": str(metadata.get("theme") or app_model.get("theme") or "theme-1"),
        "icon": str(metadata.get("icon") or app_model.get("icon") or "glyphicon-asterisk"),
        "usersAccess": metadata.get("usersAccess", app_model.get("usersAccess")),
        "groupsAccess": metadata.get("groupsAccess", app_model.get("groupsAccess")),
        "flowApp": bool(metadata.get("flowApp", app_model.get("flowApp", False))),
        "url": metadata.get("url", app_model.get("url")),
        "paletteDefinitionCategory": str(metadata.get("paletteDefinitionCategory") or app_model.get("paletteDefinitionCategory") or "core"),
        "extension": {"design": {"childModels": child_models}},
    }


def _process_key_from_bpmn(bpmn_xml: str, fallback: str) -> str:
    try:
        root = ET.fromstring(_sanitize_bpmn_xml(bpmn_xml).encode("utf-8"))
        process = next((node for node in root.iter() if _xml_local(node.tag) == "process"), None)
        if process is not None and process.attrib.get("id"):
            return _safe_model_key(process.attrib["id"])
    except Exception:
        pass
    return _safe_model_key(fallback)


def _collibra_form_payload(key: str, value: dict) -> dict:
    form_key = _safe_model_key(value.get("key") or key)
    raw = value.get("raw") if isinstance(value.get("raw"), dict) else None
    if raw and (raw.get("rows") or raw.get("outcomes") or raw.get("metadata")):
        payload = _json_safe_export_metadata(raw)
        payload.setdefault("metadata", {})
        if isinstance(payload["metadata"], dict):
            payload["metadata"]["key"] = form_key
            payload["metadata"].setdefault("name", str(value.get("name") or form_key))
            payload["metadata"].setdefault("description", "")
            payload["metadata"].setdefault("version", "1")
            payload["metadata"].setdefault("modelType", "form")
            payload["metadata"].setdefault("flowableDesignVersion", 3110)
            payload["metadata"].setdefault("palette", "flowable-core-form-palette")
        return payload

    fields = value.get("fields") if isinstance(value.get("fields"), list) else _flatten_collibra_form_fields(value)
    rows = value.get("rows") if isinstance(value.get("rows"), list) and value.get("rows") else []
    if not rows:
        rows = [{"cols": [_collibra_form_col(field, index) for index, field in enumerate(fields or []) if isinstance(field, dict)]}]
    outcomes = value.get("outcomes") if isinstance(value.get("outcomes"), list) else []
    payload = {
        "outcomes": [_collibra_outcome(outcome) for outcome in outcomes if isinstance(outcome, dict)],
        "rows": rows,
        "metadata": {
            "key": form_key,
            "name": str(value.get("name") or form_key),
            "description": str(value.get("description") or ""),
            "version": str(value.get("version") or "1"),
            "modelType": "form",
            "flowableDesignVersion": int(value.get("flowableDesignVersion") or 3110),
            "palette": str(value.get("palette") or "flowable-core-form-palette"),
        },
    }
    return _json_safe_export_metadata(payload)


def _collibra_form_col(field: dict, index: int) -> dict:
    field_id = str(field.get("id") or field.get("key") or f"field_{index + 1}")
    label = str(field.get("label") or field.get("name") or field_id)
    field_type = _collibra_form_type(str(field.get("type") or field.get("stencilId") or "string"))
    extra_settings = field.get("extraSettings") if isinstance(field.get("extraSettings"), dict) else {}
    values = field.get("values")
    if values and isinstance(values, list):
        extra_settings = {**extra_settings, "values": values}
    return {
        "designInfo": {"stencilSuperIds": ["Component"], "stencilId": field_type},
        "value": str(field.get("value") or field.get("default") or ""),
        "ignore": bool(field.get("ignore", False)),
        "visible": bool(field.get("visible", field.get("readable", True))),
        "enabled": bool(field.get("enabled", field.get("writable", True))),
        "isRequired": bool(field.get("required", field.get("isRequired", False))),
        "size": int(field.get("size") or 12),
        "label": label,
        "id": field_id,
        "type": field_type,
        "extraSettings": extra_settings,
    }


def _collibra_form_type(value: str) -> str:
    lowered = value.strip().lower()
    mapping = {
        "str": "text",
        "string": "text",
        "text": "text",
        "textarea": "multi-line-text",
        "multiline": "multi-line-text",
        "multi-line-text": "multi-line-text",
        "boolean": "boolean",
        "bool": "boolean",
        "choice": "dropdown",
        "enum": "dropdown",
        "select": "dropdown",
        "dropdown": "dropdown",
        "date": "date",
        "datetime": "datetime",
        "number": "integer",
        "int": "integer",
        "integer": "integer",
        "richtext": "richText",
        "rich-text": "richText",
        "richtxt": "richText",
    }
    return mapping.get(lowered, value or "text")


def _collibra_outcome(outcome: dict) -> dict:
    value = str(outcome.get("value") or outcome.get("id") or outcome.get("label") or "")
    label = str(outcome.get("label") or outcome.get("name") or value)
    return {
        "label": label,
        "value": value,
        "visible": str(outcome.get("visible") or ""),
        "enabled": str(outcome.get("enabled") or ""),
        "navigationUrl": str(outcome.get("navigationUrl") or ""),
        "ignorePayload": bool(outcome.get("ignorePayload", False)),
        "ignoreValidation": bool(outcome.get("ignoreValidation", False)),
        "primary": bool(outcome.get("primary", False)),
    }


def _json_safe_export_metadata(value):
    if value is None:
        return ""
    if isinstance(value, dict):
        return {str(key): _json_safe_export_metadata(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe_export_metadata(item) for item in value]
    return value


def _safe_model_key(value: str) -> str:
    raw = re.sub(r"[^A-Za-z0-9_]+", "_", str(value or "model")).strip("_")
    if not raw:
        raw = "model"
    if raw[0].isdigit():
        raw = f"model_{raw}"
    return raw


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
            "calledElement",
            "calledElementType",
            "inheritVariables",
            "sameDeployment",
            "fallbackToDefaultTenant",
            "businessKey",
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

        if local == "callActivity":
            inputs, outputs = _call_activity_io_mappings(node)
            if inputs:
                property_payload["inputs"] = inputs
            if outputs:
                property_payload["outputs"] = outputs

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
    repaired_element_properties = dict(element_properties)
    for iteration in range(1, max(1, max_iterations) + 1):
        compile_results = {}
        listener_compile_results = {}
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
        for flow in model.flows:
            props = repaired_element_properties.get(flow.id) if isinstance(repaired_element_properties.get(flow.id), dict) else {}
            listener_code = str((props or {}).get("listenerCode") or flow.listener_code or "").strip()
            if not listener_code:
                continue
            result = groovy_compiler.compile_script(listener_code)
            if not result.ok:
                repaired = _deterministic_groovy_repair(listener_code)
                if repaired != listener_code:
                    changed = True
                    listener_code = repaired
                    props = {**props, "listenerCode": listener_code, "repairedAtIteration": iteration}
                    repaired_element_properties[flow.id] = props
                    flow.listener_code = listener_code
                    result = groovy_compiler.compile_script(listener_code)
            listener_compile_results[flow.id] = _compile_result_dict(result)
        structural_errors = model.validate()
        called_workflow_results = _validate_called_workflows(app_model)
        form_issues = _validate_workbench_forms(form_map, repaired_element_properties)
        missing_script_issues = _missing_script_issues(model, repaired_scripts)
        errors = structural_errors + [issue for issue in form_issues if issue["severity"] == "error"]
        errors += [
            f"Called workflow {result['processKey']}: {error}"
            for result in called_workflow_results
            for error in result.get("errors", [])
        ]
        errors += [
            _compile_failure_message(element_id, issue)
            for element_id, issue in compile_results.items()
            if not issue.get("ok")
        ]
        errors += [
            _compile_failure_message(flow_id, issue)
            for flow_id, issue in listener_compile_results.items()
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
                "listenerCompileResults": listener_compile_results,
                "calledWorkflowResults": called_workflow_results,
            }
        )
        if not changed:
            break
    final_iteration = iterations[-1] if iterations else {}
    final_compile = final_iteration.get("compileResults", {})
    final_listener_compile = final_iteration.get("listenerCompileResults", {})
    blocking = []
    blocking.extend(final_iteration.get("structuralErrors", []))
    blocking.extend(
        f"Called workflow {result['processKey']}: {error}"
        for result in final_iteration.get("calledWorkflowResults", [])
        for error in result.get("errors", [])
    )
    blocking.extend(issue["message"] for issue in final_iteration.get("formIssues", []) if issue["severity"] == "error")
    blocking.extend(_compile_failure_message(element_id, result) for element_id, result in final_compile.items() if not result.get("ok"))
    blocking.extend(_compile_failure_message(flow_id, result) for flow_id, result in final_listener_compile.items() if not result.get("ok"))
    total_checks = max(
        1,
        len(model.nodes)
        + len(model.flows)
        + len(form_map)
        + max(1, len(repaired_scripts))
        + len(final_listener_compile)
        + sum(max(1, result.get("checks", 1)) for result in final_iteration.get("calledWorkflowResults", [])),
    )
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
            "calledWorkflows": len(_called_workflow_items(app_model)),
            "iterations": len(iterations),
            "blockingIssues": len(blocking),
            "passPercent": pass_percent,
        },
        "blockingIssues": blocking,
        "iterations": iterations,
        "repairedAppModel": {**app_model, "scripts": repaired_scripts, "elementProperties": repaired_element_properties},
    }


def _validate_called_workflows(app_model: dict) -> list[dict]:
    results: list[dict] = []
    for workflow in _called_workflow_items(app_model):
        process_key = _safe_model_key(workflow.get("processKey") or workflow.get("key") or "calledWorkflow")
        errors: list[str] = []
        checks = 1
        bpmn_xml = str(workflow.get("bpmnXml") or "")
        try:
            child_model = BpmnModel.from_xml(_sanitize_bpmn_xml(bpmn_xml))
            structural_errors = child_model.validate()
            errors.extend(structural_errors)
            checks += len(child_model.nodes) + len(child_model.flows)
        except Exception as exc:
            errors.append(f"Could not parse child BPMN: {_safe_public_error(str(exc))}")
            child_model = None
        child_app_model = workflow.get("appModel") if isinstance(workflow.get("appModel"), dict) else {}
        for element_id, script_info in (child_app_model.get("scripts") or {}).items():
            groovy = script_info.get("groovy", "") if isinstance(script_info, dict) else str(script_info)
            if not str(groovy).strip():
                continue
            result = groovy_compiler.compile_script(str(groovy))
            checks += 1
            if not result.ok:
                errors.append(_compile_failure_message(f"{process_key}.{element_id}", _compile_result_dict(result)))
        for flow_id, props in (child_app_model.get("elementProperties") or {}).items():
            if not isinstance(props, dict) or not str(props.get("listenerCode") or "").strip():
                continue
            result = groovy_compiler.compile_script(str(props.get("listenerCode")))
            checks += 1
            if not result.ok:
                errors.append(_compile_failure_message(f"{process_key}.{flow_id}", _compile_result_dict(result)))
        results.append(
            {
                "processKey": process_key,
                "ok": not errors,
                "checks": checks,
                "nodes": len(child_model.nodes) if child_model else 0,
                "flows": len(child_model.flows) if child_model else 0,
                "errors": errors,
            }
        )
    return results


def _autocorrect_model_and_app(
    model: BpmnModel,
    app_model: dict,
    forms: dict | list,
    *,
    prompt: str,
    model_id: str,
    max_iterations: int,
) -> tuple[BpmnModel, dict, dict, list[dict]]:
    repaired_app_model = json.loads(json.dumps(app_model or {}, default=str))
    repaired_forms = dict(_workbench_form_items(forms))
    repaired_app_model.setdefault("scripts", {})
    repaired_app_model.setdefault("elementProperties", {})
    repaired_app_model.setdefault("metadata", {})
    repaired_app_model["metadata"]["timestamp"] = _timestamp_suffix()
    trace: list[dict] = []
    rag_context = rag_engine.retrieve(
        prompt
        + "\ncalled activity caller workflow subprocess package zip bpmn source existing OOTB workflow Groovy sequence flow condition listener",
        limit=12,
    ).render()
    _ensure_call_activity_stitching(model, repaired_app_model, repaired_forms, prompt, rag_context, model_id, max_iterations, trace)
    _repair_sequence_flow_metadata(model, repaired_app_model, prompt, rag_context, trace)
    _repair_script_tasks(model, repaired_app_model, prompt, rag_context, model_id, max_iterations, trace)
    return model, repaired_app_model, repaired_forms, trace


def _ensure_call_activity_stitching(
    model: BpmnModel,
    app_model: dict,
    forms: dict,
    prompt: str,
    rag_context: str,
    model_id: str,
    max_iterations: int,
    trace: list[dict],
) -> None:
    reference = _workflow_reference_from_prompt(prompt, rag_context)
    generated_requested = _prompt_requests_generated_called_workflow(prompt)
    if not any(node.type == "callActivity" for node in model.nodes) and (reference or generated_requested):
        created = _insert_call_activity_before_end(model, reference["calledElement"] if reference else _called_workflow_key_from_prompt(prompt))
        trace.append({"step": "call_activity_insert", "status": "completed" if created else "skipped"})
    call_nodes = [node for node in model.nodes if node.type == "callActivity"]
    if not call_nodes:
        return
    app_model.setdefault("calledWorkflows", {})
    app_model.setdefault("elementProperties", {})
    for index, node in enumerate(call_nodes):
        node_reference = reference or _workflow_reference_from_node(node)
        if generated_requested or not node_reference:
            node_reference = node_reference or {
                "sourceName": f"generated:{_called_workflow_key_from_prompt(prompt, index)}",
                "calledElement": _called_workflow_key_from_prompt(prompt, index),
            }
        payload, stitch_trace = _resolve_called_workflow_payload(node_reference, prompt, rag_context, model_id, max_iterations)
        trace.extend(stitch_trace)
        if not payload:
            if node_reference:
                _apply_called_element_without_payload(node, app_model, node_reference, trace)
            continue
        process_key = _safe_model_key(payload["processKey"])
        payload["processKey"] = process_key
        app_model["calledWorkflows"][process_key] = payload
        contract = _called_workflow_parameter_contract(model, app_model, forms, payload)
        node.properties = {
            **(node.properties or {}),
            "calledElement": process_key,
            "calledElementType": "key",
            "inheritVariables": "true",
            "sameDeployment": "true",
            "fallbackToDefaultTenant": "true",
        }
        props = app_model["elementProperties"].get(node.id, {}) if isinstance(app_model["elementProperties"].get(node.id), dict) else {}
        app_model["elementProperties"][node.id] = {
            **props,
            "calledElement": process_key,
            "calledElementType": "key",
            "inheritVariables": "true",
            "sameDeployment": "true",
            "fallbackToDefaultTenant": "true",
            "calledWorkflowSource": payload.get("sourceName") or node_reference.get("sourceName", ""),
            "calledWorkflowGenerated": bool(payload.get("generated")),
            "calledWorkflowParameters": contract,
            "inputs": contract["inputs"],
            "outputs": contract["outputs"],
            "documentation": (
                str(props.get("documentation") or node.documentation or "").strip()
                + f"\nStitched to workflow `{process_key}` from `{payload.get('sourceName', 'generated child workflow')}`. "
                + f"Mapped {len(contract['inputs'])} input parameter(s) and {len(contract['outputs'])} output parameter(s)."
            ).strip(),
            "updatedAt": datetime.now().isoformat(timespec="seconds"),
        }
        trace.append(
            {
                "step": "call_activity_stitch",
                "status": "completed",
                "elementId": node.id,
                "calledElement": process_key,
                "source": payload.get("sourceName"),
                "generated": bool(payload.get("generated")),
                "inputs": len(contract["inputs"]),
                "outputs": len(contract["outputs"]),
                "warnings": contract.get("warnings", []),
            }
        )


def _apply_called_element_without_payload(node: BpmnNode, app_model: dict, reference: dict, trace: list[dict]) -> None:
    process_key = _safe_model_key(reference.get("calledElement") or "calledWorkflow")
    node.properties = {**(node.properties or {}), "calledElement": process_key, "calledElementType": "key", "inheritVariables": "true"}
    props = app_model.setdefault("elementProperties", {}).get(node.id, {})
    if not isinstance(props, dict):
        props = {}
    app_model["elementProperties"][node.id] = {
        **props,
        "calledElement": process_key,
        "calledElementType": "key",
        "inheritVariables": "true",
        "calledWorkflowSource": reference.get("sourceName", ""),
        "stitchStatus": "referenced-only-source-not-found",
    }
    trace.append({"step": "call_activity_stitch", "status": "referenced_only", "calledElement": process_key, "source": reference.get("sourceName")})


def _resolve_called_workflow_payload(
    reference: dict,
    prompt: str,
    rag_context: str,
    model_id: str,
    max_iterations: int,
) -> tuple[dict | None, list[dict]]:
    trace: list[dict] = []
    source_name = str(reference.get("sourceName") or "")
    source_path = None if source_name.startswith("prompt:") or source_name.startswith("generated:") else _find_workflow_source_file(source_name)
    if source_path:
        try:
            payload = _called_workflow_from_file(source_path, reference.get("calledElement"))
            trace.append({"step": "called_workflow_source_load", "status": "completed", "source": str(source_path), "processKey": payload["processKey"]})
            return payload, trace
        except Exception as exc:
            trace.append({"step": "called_workflow_source_load", "status": "failed", "source": str(source_path), "error": _safe_public_error(str(exc))})
    allow_ai_generation = _prompt_requests_generated_called_workflow(prompt) or source_name.startswith("generated:")
    if allow_ai_generation or source_name.startswith("prompt:") or not source_path:
        payload = _generate_called_workflow_payload(reference, prompt, rag_context, model_id, max_iterations, allow_ai=allow_ai_generation)
        trace.append({"step": "called_workflow_generate", "status": "completed", "processKey": payload["processKey"], "source": payload["sourceName"]})
        return payload, trace
    return None, trace


def _called_workflow_from_file(path: Path, preferred_key: str | None = None) -> dict:
    app_model = _empty_app_model(path.name)
    forms: dict = {}
    candidates: list[tuple[int, str, str]] = []
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as package:
            members = _validated_zip_member_names(package)
            for member in members:
                text = _decode_text(package.read(member))
                lower = member.lower()
                if lower.endswith((".bpmn", ".bpmn20.xml", ".xml")) and _looks_like_bpmn(text):
                    process_key = _process_key_from_bpmn(text, Path(member).stem)
                    score = 0 if preferred_key and process_key.lower() == str(preferred_key).lower() else 2
                    candidates.append((score, member, _sanitize_bpmn_xml(text)))
                elif lower.endswith(".form"):
                    form_key, form_payload = _parse_collibra_form(text, member)
                    forms[form_key] = form_payload
                elif lower.endswith(".app"):
                    parsed = _parse_json_or_text(text)
                    if isinstance(parsed, dict):
                        app_model = _deep_merge(app_model, parsed)
                elif lower.endswith(".groovy"):
                    app_model.setdefault("scripts", {})[_basename(member)] = {"groovy": text, "source": member}
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _looks_like_bpmn(text):
            candidates.append((0, path.name, _sanitize_bpmn_xml(text)))
    if not candidates:
        raise ValueError(f"No BPMN child workflow found in {path.name}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    source_member = candidates[0][1]
    bpmn_xml = candidates[0][2]
    extracted = _extract_bpmn_package_metadata(bpmn_xml, source_member, forms)
    app_model["scripts"] = _deep_merge(app_model.get("scripts") or {}, extracted["scripts"])
    app_model["elementProperties"] = _deep_merge(app_model.get("elementProperties") or {}, extracted["elementProperties"])
    forms = _deep_merge(forms, extracted["forms"])
    existing_forms = app_model.get("forms") or {}
    if not isinstance(existing_forms, dict):
        app_model["manifestForms"] = existing_forms
        existing_forms = {}
    app_model["forms"] = _deep_merge(existing_forms, forms)
    process_key = _process_key_from_bpmn(bpmn_xml, Path(source_member).stem)
    return {
        "key": process_key,
        "processKey": process_key,
        "name": process_key,
        "sourceName": path.name,
        "sourceMember": source_member,
        "bpmnXml": _embed_app_model_scripts_in_bpmn(bpmn_xml, app_model),
        "forms": forms,
        "appModel": app_model,
        "generated": False,
        "parameterProfile": _workflow_parameter_profile(bpmn_xml, app_model, forms),
    }


def _generate_called_workflow_payload(reference: dict, prompt: str, rag_context: str, model_id: str, max_iterations: int, allow_ai: bool = True) -> dict:
    process_key = _safe_model_key(reference.get("calledElement") or _called_workflow_key_from_prompt(prompt))
    child_prompt = (
        f"Design a standalone Collibra child workflow with process id {process_key}. "
        "This workflow will be invoked by a parent BPMN callActivity. Do not include another call activity unless the user explicitly requests nested orchestration. "
        "Include pools, lanes, forms, Groovy script tasks, sequence-flow conditions, input variables, output variables, and failure/rework paths. "
        f"Parent request:\n{prompt}"
    )
    try:
        if not allow_ai:
            raise RuntimeError("AI generation disabled for deterministic missing-source stitch.")
        package = agent.design_from_prompt(child_prompt, model_id=model_id)
    except Exception:
        package = _generated_called_workflow_fallback(process_key, prompt)
    package.process.process_id = process_key
    package.process.name = package.process.name or process_key
    package.process.nodes = [node for node in package.process.nodes if node.type != "callActivity"]
    package.process.flows = _repair_child_flow_continuity(package.process.nodes, package.process.flows)
    app_model = _app_model_from_package(package, rag_context)
    forms = _forms_dict_from_package(package)
    child_trace: list[dict] = []
    _repair_sequence_flow_metadata(package.process, app_model, child_prompt, rag_context, child_trace)
    _repair_script_tasks(package.process, app_model, child_prompt, rag_context, model_id, max(1, min(3, max_iterations)), child_trace)
    quality = _run_package_quality_loop(package.process, app_model, forms, max_iterations=max(1, min(3, max_iterations)))
    app_model = quality.get("repairedAppModel") or app_model
    bpmn_xml = _embed_app_model_scripts_in_bpmn(package.process.to_xml(), app_model)
    return {
        "key": process_key,
        "processKey": process_key,
        "name": package.process.name,
        "sourceName": reference.get("sourceName") or f"generated:{process_key}",
        "bpmnXml": bpmn_xml,
        "forms": forms,
        "appModel": app_model,
        "generated": True,
        "quality": quality,
        "parameterProfile": _workflow_parameter_profile(bpmn_xml, app_model, forms),
    }


def _generated_called_workflow_fallback(process_key: str, prompt: str) -> WorkflowPackage:
    form_key = f"{process_key}DecisionForm"
    normalized = _safe_model_key(_summarise_prompt_for_key(prompt) or process_key)
    form = FormModel(
        key=form_key,
        name=f"{process_key} Decision Form",
        fields=[
            FormField(id="decisionInfo", name="Decision information", type="textarea", required=False),
            FormField(
                id="approvalDecision",
                name="Approval decision",
                type="dropdown",
                required=True,
                values=[
                    {"id": "approve", "name": "Approve"},
                    {"id": "reject", "name": "Reject"},
                    {"id": "rework", "name": "Rework"},
                ],
            ),
        ],
    )
    nodes = [
        BpmnNode("childStart", "startEvent", "Start child workflow", "Requester", form_key=form_key, x=140, y=120),
        BpmnNode("childReview", "userTask", f"Review {normalized}", "Data Steward", candidate_groups="${stewardGroup}", form_key=form_key, x=340, y=260),
        BpmnNode("childRoute", "exclusiveGateway", "Decision route", "Data Steward", x=570, y=275),
        BpmnNode(
            "childApply",
            "scriptTask",
            "Apply child decision",
            "Collibra Automation",
            script="// #importFile NONE\nexecution.setVariable('childWorkflowStatus', 'approved')\nexecution.setVariable('childWorkflowCompleted', true)",
            x=760,
            y=430,
        ),
        BpmnNode("childRejected", "endEvent", "Rejected", "Data Steward", x=790, y=275),
        BpmnNode("childEnd", "endEvent", "Completed", "Collibra Automation", x=1010, y=452),
    ]
    flows = [
        SequenceFlow("childFlow_start_review", "childStart", "childReview"),
        SequenceFlow("childFlow_review_route", "childReview", "childRoute"),
        SequenceFlow("childFlow_approved", "childRoute", "childApply", name="Approved", condition="${approvalDecision == 'approve'}", flow_type="conditional"),
        SequenceFlow("childFlow_rejected", "childRoute", "childRejected", name="Rejected", condition="${approvalDecision != 'approve'}", flow_type="conditional"),
        SequenceFlow("childFlow_apply_end", "childApply", "childEnd"),
    ]
    return WorkflowPackage(
        process=BpmnModel(
            process_id=process_key,
            name=f"{process_key} Called Workflow",
            pools=[BpmnPool(id=f"{process_key}_pool", name=f"{process_key} Called Workflow", process_ref=process_key, width=1220, height=560)],
            lanes=["Requester", "Data Steward", "Collibra Automation"],
            nodes=nodes,
            flows=flows,
            documentation=f"Generated child workflow for parent prompt: {prompt[:600]}",
        ),
        forms=[form],
        app_name=f"{process_key} Called Workflow",
    )


def _repair_child_flow_continuity(nodes: list[BpmnNode], flows: list[SequenceFlow]) -> list[SequenceFlow]:
    node_ids = {node.id for node in nodes}
    valid_flows = [flow for flow in flows if flow.source_ref in node_ids and flow.target_ref in node_ids and flow.source_ref != flow.target_ref]
    start = next((node for node in nodes if node.type == "startEvent"), None)
    end = next((node for node in nodes if node.type == "endEvent"), None)
    if not start or not end:
        return valid_flows
    outgoing = {flow.source_ref for flow in valid_flows}
    incoming = {flow.target_ref for flow in valid_flows}
    ordered = sorted(nodes, key=lambda node: (node.x, node.y, node.id))
    for source, target in zip(ordered, ordered[1:]):
        if source.type == "endEvent" or target.type == "startEvent":
            continue
        if source.id not in outgoing or target.id not in incoming:
            flow_id = _safe_model_key(f"flow_{source.id}_{target.id}")
            if not any(flow.id == flow_id for flow in valid_flows):
                valid_flows.append(SequenceFlow(flow_id, source.id, target.id))
                outgoing.add(source.id)
                incoming.add(target.id)
    if start.id not in outgoing:
        target = next((node for node in ordered if node.id != start.id), end)
        valid_flows.append(SequenceFlow(_safe_model_key(f"flow_{start.id}_{target.id}"), start.id, target.id))
    if end.id not in incoming:
        source = next((node for node in reversed(ordered) if node.id != end.id and node.type != "endEvent"), start)
        valid_flows.append(SequenceFlow(_safe_model_key(f"flow_{source.id}_{end.id}"), source.id, end.id))
    return valid_flows


def _insert_call_activity_before_end(model: BpmnModel, called_key: str) -> bool:
    end_node = next((node for node in model.nodes if node.type == "endEvent"), None)
    if end_node is None:
        return False
    incoming_flow = next((flow for flow in model.flows if flow.target_ref == end_node.id), None)
    source_id = incoming_flow.source_ref if incoming_flow else next((node.id for node in model.nodes if node.type == "startEvent"), "")
    if not source_id:
        return False
    call_id = _safe_model_key(f"call_{called_key}")
    if any(node.id == call_id for node in model.nodes):
        return False
    source_node = next((node for node in model.nodes if node.id == source_id), end_node)
    lane = "Collibra Automation" if "Collibra Automation" in model.lanes else (source_node.lane or (model.lanes[-1] if model.lanes else None))
    model.nodes.append(
        BpmnNode(
            id=call_id,
            type="callActivity",
            name=f"Call {called_key}",
            lane=lane,
            documentation="Inserted by Autocorrect to invoke the requested child workflow.",
            properties={"calledElement": _safe_model_key(called_key), "calledElementType": "key", "inheritVariables": "true"},
            x=max(source_node.x + 220, end_node.x - 180),
            y=source_node.y,
        )
    )
    if incoming_flow:
        model.flows = [flow for flow in model.flows if flow.id != incoming_flow.id]
    model.flows.append(SequenceFlow(_safe_model_key(f"flow_{source_id}_{call_id}"), source_id, call_id))
    model.flows.append(SequenceFlow(_safe_model_key(f"flow_{call_id}_{end_node.id}"), call_id, end_node.id))
    return True


def _find_workflow_source_file(source_name: str) -> Path | None:
    raw = str(source_name or "").strip().strip("'\"")
    if not raw:
        return None
    direct = Path(raw)
    if direct.exists() and direct.is_file():
        return direct
    candidates = [
        settings.paths.rag_user_dropzone_dir,
        settings.paths.rag_ootb_workflows_dir,
        settings.paths.rag_generated_training_dir,
        settings.paths.docs_dir,
    ]
    wanted = raw.replace("\\", "/").split("/")[-1].lower()
    wanted_stem = re.sub(r"\.(?:zip|bpmn|bpmn20\.xml)$", "", wanted, flags=re.IGNORECASE)
    for folder in candidates:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".zip", ".bpmn", ".xml"}:
                continue
            name = path.name.lower()
            stem = re.sub(r"\.(?:zip|bpmn|bpmn20\.xml)$", "", name, flags=re.IGNORECASE)
            if name == wanted or stem == wanted_stem:
                return path
    return None


def _workflow_reference_from_node(node: BpmnNode) -> dict | None:
    called = str((node.properties or {}).get("calledElement") or "").strip()
    if not called:
        return None
    return {"sourceName": f"prompt:{called}", "calledElement": _safe_model_key(called)}


def _prompt_requests_generated_called_workflow(prompt: str) -> bool:
    text = str(prompt or "").lower()
    return any(
        phrase in text
        for phrase in (
            "generate caller workflow",
            "generate called workflow",
            "generate subworkflow",
            "generate sub workflow",
            "create caller workflow",
            "create called workflow",
            "create subworkflow",
            "design caller workflow",
            "design called workflow",
            "design subworkflow",
            "also generate caller",
            "also generate called",
        )
    )


def _called_workflow_key_from_prompt(prompt: str, index: int = 0) -> str:
    reference = _workflow_reference_from_prompt(prompt, "")
    if reference:
        return _safe_model_key(reference.get("calledElement") or "calledWorkflow")
    summary = _summarise_prompt_for_key(prompt)
    suffix = "" if index == 0 else str(index + 1)
    return _safe_model_key(f"{summary or 'called'}SubWorkflow{suffix}")


def _summarise_prompt_for_key(prompt: str) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z0-9]+", str(prompt or ""))[:5]
    return "".join(word[:1].upper() + word[1:] for word in words) or "Called"


def _called_workflow_parameter_contract(model: BpmnModel, app_model: dict, forms: dict, payload: dict) -> dict:
    profile = payload.get("parameterProfile") if isinstance(payload.get("parameterProfile"), dict) else {}
    required_inputs = sorted(set(profile.get("inputVariables") or []))
    produced_outputs = sorted(set(profile.get("outputVariables") or []))
    main_profile = _workflow_parameter_profile(model.to_xml(), app_model, forms)
    available = set(main_profile.get("availableVariables") or [])
    inputs: list[dict] = []
    warnings: list[str] = []
    for variable in required_inputs:
        if not _safe_variable_name(variable):
            continue
        if variable in available:
            inputs.append({"source": variable, "target": variable})
        else:
            inputs.append({"sourceExpression": f"${{{variable}}}", "target": variable})
            warnings.append(f"Input `{variable}` is required by the called workflow but was not found in the parent forms/scripts; mapped by expression for runtime resolution.")
    outputs = [{"source": variable, "target": variable} for variable in produced_outputs if _safe_variable_name(variable)]
    if not inputs:
        inputs = [{"source": "businessItemId", "target": "businessItemId"}]
    if not outputs:
        outputs = [{"source": "childWorkflowStatus", "target": "childWorkflowStatus"}]
    return {
        "inputs": inputs,
        "outputs": outputs,
        "requiredInputs": required_inputs,
        "producedOutputs": produced_outputs,
        "availableParentVariables": sorted(available),
        "formKeys": sorted(set(profile.get("formKeys") or [])),
        "warnings": warnings,
    }


def _workflow_parameter_profile(bpmn_xml: str, app_model: dict, forms: dict | list) -> dict:
    text_parts = [str(bpmn_xml or "")]
    for script_info in (app_model.get("scripts") or {}).values() if isinstance(app_model, dict) else []:
        if isinstance(script_info, dict):
            text_parts.append(str(script_info.get("groovy") or ""))
        else:
            text_parts.append(str(script_info))
    element_props = app_model.get("elementProperties") if isinstance(app_model, dict) else {}
    if isinstance(element_props, dict):
        text_parts.append(json.dumps(element_props, default=str))
    form_items = _workbench_form_items(forms)
    form_fields: set[str] = set()
    form_keys: set[str] = set()
    for key, form in form_items:
        form_keys.add(str(key))
        for field in _flatten_collibra_form_fields(form):
            field_id = str(field.get("id") or field.get("key") or "").strip()
            if field_id:
                form_fields.add(field_id)
    combined = "\n".join(text_parts)
    input_variables = _variables_read_from_text(combined) | form_fields
    output_variables = _variables_written_from_text(combined)
    return {
        "inputVariables": sorted(input_variables - output_variables),
        "outputVariables": sorted(output_variables),
        "availableVariables": sorted(input_variables | output_variables | form_fields),
        "formKeys": sorted(form_keys),
        "formFields": sorted(form_fields),
    }


def _variables_read_from_text(text: str) -> set[str]:
    variables = set(re.findall(r"getVariable\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", text or ""))
    for expression in re.findall(r"\$\{([^}]+)\}", text or ""):
        for token in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", expression):
            if token not in {"true", "false", "null", "and", "or", "not", "execution"}:
                variables.add(token)
    return {variable for variable in variables if _safe_variable_name(variable)}


def _variables_written_from_text(text: str) -> set[str]:
    variables = set(re.findall(r"setVariable\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", text or ""))
    return {variable for variable in variables if _safe_variable_name(variable)}


def _safe_variable_name(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,80}", str(value or "")))


def _repair_script_tasks(
    model: BpmnModel,
    app_model: dict,
    prompt: str,
    rag_context: str,
    model_id: str,
    max_iterations: int,
    trace: list[dict],
) -> None:
    scripts = app_model.setdefault("scripts", {})
    for node in model.nodes:
        if node.type != "scriptTask":
            continue
        script_info = scripts.get(node.id)
        existing = script_info.get("groovy", "") if isinstance(script_info, dict) else str(script_info or "")
        groovy = existing.strip() or node.script.strip()
        generated = False
        if not groovy:
            groovy = _compat_groovy({"id": node.id, "type": "bpmn:ScriptTask", "name": node.name}, prompt, rag_context)
            generated = True
        repaired, result, attempts = _compile_and_repair_groovy(
            groovy,
            element={"id": node.id, "type": "bpmn:ScriptTask", "name": node.name},
            prompt=f"Autocorrect Groovy for script task {node.name or node.id}. {prompt}",
            context=rag_context,
            org_profile=_organization_code_profile(rag_context, app_model, node.id),
            model_id=model_id,
            max_iterations=max_iterations,
        )
        node.script = repaired
        scripts[node.id] = {
            **(script_info if isinstance(script_info, dict) else {}),
            "groovy": repaired,
            "elementType": "scriptTask",
            "elementName": node.name,
            "autocorrected": True,
            "generatedByAutocorrect": generated,
            "compileResults": [_compile_result_dict(result)] if result else [],
            "repairAttempts": attempts,
            "updatedAt": datetime.now().isoformat(timespec="seconds"),
        }
        trace.append(
            {
                "step": "script_task_autocorrect",
                "elementId": node.id,
                "generated": generated,
                "status": _compile_status(result),
                "attempts": len(attempts),
            }
        )


def _repair_sequence_flow_metadata(model: BpmnModel, app_model: dict, prompt: str, rag_context: str, trace: list[dict]) -> None:
    element_properties = app_model.setdefault("elementProperties", {})
    outgoing: dict[str, list[SequenceFlow]] = {}
    for flow in model.flows:
        outgoing.setdefault(flow.source_ref, []).append(flow)
    node_by_id = {node.id: node for node in model.nodes}
    for source_id, flows in outgoing.items():
        source = node_by_id.get(source_id)
        has_default = any(flow.is_default for flow in flows)
        for index, flow in enumerate(flows):
            props = element_properties.get(flow.id, {}) if isinstance(element_properties.get(flow.id), dict) else {}
            inferred_condition, flow_type, is_default = _infer_sequence_flow_rule(flow, source, index, len(flows), has_default)
            if not flow.condition and inferred_condition:
                flow.condition = inferred_condition
            if flow_type:
                flow.flow_type = flow_type
            if is_default:
                flow.is_default = True
                has_default = True
            listener_code = str(props.get("listenerCode") or flow.listener_code or "").strip()
            generated_listener = False
            if not listener_code:
                listener_code = _sequence_flow_listener_code(flow, source, node_by_id.get(flow.target_ref), prompt, rag_context)
                generated_listener = True
            flow.listener_code = listener_code
            element_properties[flow.id] = {
                **props,
                "execution": "gateway-condition",
                "scope": "global",
                "flowType": flow.flow_type,
                "condition": flow.condition or props.get("condition") or "",
                "isDefault": flow.is_default,
                "listenerCode": listener_code,
                "documentation": props.get("documentation") or f"Autocorrected sequence flow from {flow.source_ref} to {flow.target_ref}.",
                "updatedAt": datetime.now().isoformat(timespec="seconds"),
            }
            trace.append(
                {
                    "step": "sequence_flow_autocorrect",
                    "elementId": flow.id,
                    "flowType": flow.flow_type,
                    "condition": flow.condition,
                    "listenerGenerated": generated_listener,
                }
            )


def _infer_sequence_flow_rule(
    flow: SequenceFlow,
    source: BpmnNode | None,
    index: int,
    sibling_count: int,
    has_default: bool,
) -> tuple[str, str | None, bool]:
    label = f"{flow.id} {flow.name} {flow.target_ref}".lower()
    if flow.condition:
        return flow.condition, "conditional", False
    if flow.is_default or flow.flow_type == "default":
        return "", "default", True
    if "reject" in label or "decline" in label or "denied" in label:
        return "${approvalDecision != 'approve'}", "conditional", False
    if "approve" in label or "approved" in label:
        return "${approvalDecision == 'approve'}", "conditional", False
    if "rework" in label or "reroute" in label:
        return "${approvalDecision == 'rework'}", "conditional", False
    if "fail" in label or "error" in label or "remediation" in label:
        return "${provisioningStatus != 'success'}", "conditional", False
    if "success" in label or "complete" in label or "done" in label or "provisioned" in label:
        return "${provisioningStatus == 'success'}", "conditional", False
    if source and source.type.endswith("Gateway") and sibling_count > 1 and index == sibling_count - 1 and not has_default:
        return "", "default", True
    if flow.flow_type in {"conditional", "skip"}:
        return "${routeApproved == true}", "conditional", False
    return "", flow.flow_type or "normal", False


def _sequence_flow_listener_code(flow: SequenceFlow, source: BpmnNode | None, target: BpmnNode | None, prompt: str, rag_context: str) -> str:
    variable = _groovy_var(flow.id)
    source_name = (source.name if source else flow.source_ref) or flow.source_ref
    target_name = (target.name if target else flow.target_ref) or flow.target_ref
    return f"""// #importFile NONE

// Autogenerated transition listener for sequence flow {flow.id}.
// Source: {source_name}
// Target: {target_name}
execution.setVariable("lastSequenceFlowId", "{flow.id}")
execution.setVariable("{variable}Taken", true)
execution.setVariable("{variable}SourceRef", "{flow.source_ref}")
execution.setVariable("{variable}TargetRef", "{flow.target_ref}")
"""


def _workflow_reference_from_prompt(prompt: str, rag_context: str) -> dict | None:
    explicit = _workflow_file_mentions(prompt)
    prompt_mentions_source = any(token in prompt.lower() for token in ("caller activity", "call activity", "called workflow", "subworkflow", "sub workflow", "use workflow", "use zip", "from rag", "source folder"))
    if explicit:
        source = Path(str(explicit[0]).strip().strip("'\"")).name
        stem = re.sub(r"\.(?:zip|bpmn|bpmn20\.xml)$", "", source, flags=re.IGNORECASE)
        return {"sourceName": source, "calledElement": _safe_model_key(stem)}
    named = re.findall(
        r"(?:called workflow|call activity|subworkflow|sub workflow|caller workflow)\s+(?:named|called|key|to|as)\s+['\"]?([A-Za-z][A-Za-z0-9_-]{2,80})",
        prompt,
        flags=re.IGNORECASE,
    )
    if named:
        called_element = _safe_model_key(named[0])
        return {"sourceName": f"prompt:{called_element}", "calledElement": called_element}
    if not prompt_mentions_source:
        return None
    candidates = re.findall(r"source=([^\s]+(?:\.zip|\.bpmn|\.bpmn20\.xml))", rag_context, flags=re.IGNORECASE)
    if not candidates:
        candidates = _workflow_file_mentions(rag_context)
    if not candidates:
        return None
    source = Path(str(candidates[0]).strip().strip("'\"")).name
    stem = re.sub(r"\.(?:zip|bpmn|bpmn20\.xml)$", "", source, flags=re.IGNORECASE)
    return {"sourceName": source, "calledElement": _safe_model_key(stem)}


def _workflow_file_mentions(text: str) -> list[str]:
    quoted = re.findall(r"['\"]([^'\"]+\.(?:zip|bpmn|bpmn20\.xml))['\"]", text or "", flags=re.IGNORECASE)
    bare = re.findall(r"(?<![A-Za-z0-9_.()\\/-])([A-Za-z0-9_.()\\/-]+\.(?:zip|bpmn|bpmn20\.xml))", text or "", flags=re.IGNORECASE)
    return quoted + bare


def _timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _short_export_stem(value: str | None, timestamp: str | None = None, max_length: int = 62) -> str:
    ts = timestamp or _timestamp_suffix()
    raw = Path(str(value or "workflow")).stem
    raw = re.sub(r"_with_timestamp_\d{8}_\d{6}.*$", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"_\d{8}_\d{6}.*$", "", raw, flags=re.IGNORECASE)
    suffix = f"_{ts}"
    core_max = max(12, max_length - len(suffix))
    return f"{_compact_name_part(raw or 'workflow', core_max)}{suffix}"


def _compact_name_part(value: str | None, max_length: int = 48) -> str:
    safe = _safe_filename(value or "workflow")
    if len(safe) <= max_length:
        return safe
    digest = sha1(safe.encode("utf-8", errors="ignore")).hexdigest()[:7]
    keep = max(8, max_length - len(digest) - 1)
    return f"{safe[:keep].rstrip('._-')}_{digest}"


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
    repaired = _strip_code_fence(repaired)
    repaired = re.sub(r"(?m)^\s*import\s+[\w.]+\.\*\s*;?\s*\n?", "", repaired)
    repaired = re.sub(r"(?m)^\s*import\s+(?:uuid|UUID|[\w.]*\.uuid(?:\.[\w.*]+)?)\s*;?\s*\n?", "", repaired, flags=re.IGNORECASE)
    repaired = re.sub(r"(?m)^\s*import\s+java\.util\.UUID\s*;?\s*\n?", "", repaired)
    repaired = repaired.replace("UUID.randomUUID()", "java.util.UUID.randomUUID()")
    repaired = re.sub(r"\bUUID\.fromString\s*\(", "string2Uuid(", repaired)
    repaired = re.sub(r"\bUUID\s+([A-Za-z_]\w*)\s*=", r"def \1 =", repaired)
    repaired = re.sub(r"(?m)^\s*(?:public\s+)?class\s+\w+\s*\{\s*", "", repaired)
    repaired = re.sub(r"(?m)^\s*public\s+static\s+void\s+main\s*\([^)]*\)\s*\{\s*", "", repaired)
    repaired = repaired.rstrip()
    if repaired and not repaired.lstrip().startswith("// #importFile NONE"):
        repaired = "// #importFile NONE\n" + repaired.lstrip()
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
            "script": "// #importFile NONE\n\ndef assetId = execution.getVariable(\"assetId\")\nexecution.setVariable(\"assetIdPresent\", assetId != null && assetId.toString().trim())\n",
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


def _embed_app_model_scripts_in_bpmn(bpmn_xml: str, app_model: dict) -> str:
    clean = _sanitize_bpmn_xml(bpmn_xml)
    if not clean:
        return clean
    _register_bpmn_namespaces()
    try:
        root = ET.fromstring(clean.encode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse BPMN XML for export: {exc}") from exc
    scripts = app_model.get("scripts") or {}
    element_properties = app_model.get("elementProperties") or {}
    changed = False
    for node in root.iter():
        local = _xml_local(node.tag)
        if local == "scriptTask":
            element_id = node.attrib.get("id", "scriptTask")
            node.attrib["scriptFormat"] = "groovy"
            node.attrib[_qname_for_namespace(FLOWABLE_NS, "autoStoreVariables")] = "false"
            script_el = next((child for child in node if _xml_local(child.tag) == "script"), None)
            existing_script = "".join(script_el.itertext()).strip() if script_el is not None else ""
            groovy = _script_from_app_model(scripts, element_id) or existing_script or _minimal_collibra_script(element_id)
            if script_el is None:
                script_el = ET.SubElement(node, _qname_for_existing(node.tag, "script"))
            if not str(script_el.text or "").strip() or groovy.strip():
                script_el.text = groovy.rstrip() + "\n"
                changed = True
        elif local == "sequenceFlow":
            if _normalize_sequence_flow_condition(node, element_properties):
                changed = True
            if _normalize_sequence_flow_listener(node, element_properties):
                changed = True
        elif local == "callActivity":
            if _normalize_call_activity_stitching(node, element_properties):
                changed = True
    if _normalize_bpmn_di_waypoints(root):
        changed = True
    if not changed:
        return clean
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def _register_bpmn_namespaces() -> None:
    namespaces = {
        "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
        "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
        "dc": "http://www.omg.org/spec/DD/20100524/DC",
        "di": "http://www.omg.org/spec/DD/20100524/DI",
        "flowable": "http://flowable.org/bpmn",
        "camunda": "http://camunda.org/schema/1.0/bpmn",
        "dsc": DSC_NS,
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)


def _qname_for_existing(tag: str, local_name: str) -> str:
    if tag.startswith("{"):
        namespace = tag[1:].split("}", 1)[0]
        return f"{{{namespace}}}{local_name}"
    return local_name


def _qname_for_namespace(namespace: str, local_name: str) -> str:
    return f"{{{namespace}}}{local_name}"


def _normalize_sequence_flow_condition(flow: ET.Element, element_properties: dict) -> bool:
    changed = False
    flow_id = flow.attrib.get("id", "")
    props = element_properties.get(flow_id) if isinstance(element_properties, dict) else {}
    prop_condition = ""
    if isinstance(props, dict):
        prop_condition = str(props.get("condition") or props.get("expression") or "").strip()
    condition_el = next((child for child in flow if _xml_local(child.tag) == "conditionExpression"), None)
    if condition_el is None:
        if prop_condition:
            condition_el = ET.SubElement(
                flow,
                _qname_for_existing(flow.tag, "conditionExpression"),
                {_qname_for_namespace(XSI_NS, "type"): "bpmn:tFormalExpression"},
            )
            condition_el.text = prop_condition
            return True
        return False
    xsi_type = _qname_for_namespace(XSI_NS, "type")
    if condition_el.attrib.get(xsi_type) != "bpmn:tFormalExpression":
        condition_el.attrib[xsi_type] = "bpmn:tFormalExpression"
        changed = True
    current = "".join(condition_el.itertext()).strip()
    if current:
        condition_el.text = current
        return changed
    if prop_condition:
        condition_el.text = prop_condition
        return True
    flow.remove(condition_el)
    return True


def _normalize_sequence_flow_listener(flow: ET.Element, element_properties: dict) -> bool:
    flow_id = flow.attrib.get("id", "")
    props = element_properties.get(flow_id) if isinstance(element_properties, dict) else {}
    if not isinstance(props, dict):
        return False
    listener_code = str(props.get("listenerCode") or props.get("listener_code") or "").strip()
    if not listener_code:
        return False
    changed = False
    extension_el = next((child for child in flow if _xml_local(child.tag) == "extensionElements"), None)
    if extension_el is None:
        extension_el = ET.Element(_qname_for_existing(flow.tag, "extensionElements"))
        children = list(flow)
        condition_index = next(
            (index for index, child in enumerate(children) if _xml_local(child.tag) == "conditionExpression"),
            len(children),
        )
        flow.insert(condition_index, extension_el)
        changed = True
    listener_el = next((child for child in extension_el if _xml_local(child.tag) == "transitionListenerGroovy"), None)
    if listener_el is None:
        listener_el = ET.SubElement(extension_el, _qname_for_namespace(DSC_NS, "transitionListenerGroovy"))
        changed = True
    normalized = listener_code.rstrip() + "\n"
    if listener_el.text != normalized:
        listener_el.text = normalized
        changed = True
    return changed


def _normalize_call_activity_stitching(node: ET.Element, element_properties: dict) -> bool:
    element_id = node.attrib.get("id", "")
    props = element_properties.get(element_id) if isinstance(element_properties, dict) else {}
    if not isinstance(props, dict):
        return False
    changed = False
    called_element = str(props.get("calledElement") or "").strip()
    if called_element and node.attrib.get("calledElement") != called_element:
        node.attrib["calledElement"] = called_element
        changed = True
    for prop_key, attr_name in (
        ("calledElementType", "calledElementType"),
        ("inheritVariables", "inheritVariables"),
        ("sameDeployment", "sameDeployment"),
        ("fallbackToDefaultTenant", "fallbackToDefaultTenant"),
        ("businessKey", "businessKey"),
    ):
        if prop_key in props and props[prop_key] not in (None, ""):
            value = str(props[prop_key]).lower() if isinstance(props[prop_key], bool) else str(props[prop_key])
            qname = _qname_for_namespace(FLOWABLE_NS, attr_name)
            if node.attrib.get(qname) != value:
                node.attrib[qname] = value
                changed = True
    inputs = props.get("inputs") or props.get("inputParameters") or []
    outputs = props.get("outputs") or props.get("outputParameters") or []
    if not isinstance(inputs, list):
        inputs = []
    if not isinstance(outputs, list):
        outputs = []
    if not inputs and not outputs:
        return changed
    extension_el = next((child for child in node if _xml_local(child.tag) == "extensionElements"), None)
    if extension_el is None:
        extension_el = ET.Element(_qname_for_existing(node.tag, "extensionElements"))
        node.insert(0, extension_el)
        changed = True
    for child in list(extension_el):
        if child.tag in {_qname_for_namespace(FLOWABLE_NS, "in"), _qname_for_namespace(FLOWABLE_NS, "out")}:
            extension_el.remove(child)
            changed = True
    for mapping in inputs:
        if not isinstance(mapping, dict) or not mapping.get("target"):
            continue
        attrs = {"target": str(mapping["target"])}
        if mapping.get("sourceExpression"):
            attrs["sourceExpression"] = str(mapping["sourceExpression"])
        elif mapping.get("source"):
            attrs["source"] = str(mapping["source"])
        else:
            attrs["source"] = str(mapping["target"])
        ET.SubElement(extension_el, _qname_for_namespace(FLOWABLE_NS, "in"), attrs)
        changed = True
    for mapping in outputs:
        if not isinstance(mapping, dict) or not mapping.get("source"):
            continue
        attrs = {"source": str(mapping["source"]), "target": str(mapping.get("target") or mapping["source"])}
        ET.SubElement(extension_el, _qname_for_namespace(FLOWABLE_NS, "out"), attrs)
        changed = True
    return changed


def _call_activity_io_mappings(node: ET.Element) -> tuple[list[dict], list[dict]]:
    inputs: list[dict] = []
    outputs: list[dict] = []
    for child in node.iter():
        if child.tag == _qname_for_namespace(FLOWABLE_NS, "in"):
            mapping = {
                "target": child.attrib.get("target", ""),
                "source": child.attrib.get("source", ""),
                "sourceExpression": child.attrib.get("sourceExpression", ""),
            }
            inputs.append({key: value for key, value in mapping.items() if value})
        elif child.tag == _qname_for_namespace(FLOWABLE_NS, "out"):
            mapping = {
                "source": child.attrib.get("source", ""),
                "target": child.attrib.get("target", ""),
            }
            outputs.append({key: value for key, value in mapping.items() if value})
    return inputs, outputs


def _normalize_bpmn_di_waypoints(root: ET.Element) -> bool:
    shape_bounds = _bpmn_shape_bounds(root)
    if not shape_bounds:
        return False
    flow_refs = _bpmn_sequence_flow_refs(root)
    if not flow_refs:
        return False
    changed = False
    for edge in root.iter():
        if _xml_local(edge.tag) != "BPMNEdge":
            continue
        flow_id = edge.attrib.get("bpmnElement", "")
        refs = flow_refs.get(flow_id)
        if not refs:
            continue
        source_ref, target_ref = refs
        source_bounds = shape_bounds.get(source_ref)
        target_bounds = shape_bounds.get(target_ref)
        if not source_bounds or not target_bounds:
            continue
        waypoints = diagram_waypoints(source_bounds, target_bounds)
        current = _edge_waypoints(edge)
        if current == waypoints:
            continue
        for child in list(edge):
            if _xml_local(child.tag) == "waypoint":
                edge.remove(child)
        for index, (x, y) in enumerate(waypoints):
            edge.insert(index, ET.Element(_qname_for_namespace(DI_NS, "waypoint"), {"x": str(x), "y": str(y)}))
        changed = True
    return changed


def _bpmn_shape_bounds(root: ET.Element) -> dict[str, tuple[int, int, int, int]]:
    bounds: dict[str, tuple[int, int, int, int]] = {}
    for shape in root.iter():
        if _xml_local(shape.tag) != "BPMNShape":
            continue
        bpmn_id = shape.attrib.get("bpmnElement")
        if not bpmn_id:
            continue
        for child in shape:
            if _xml_local(child.tag) != "Bounds":
                continue
            bounds[bpmn_id] = (
                _round_xml_number(child.attrib.get("x"), 0),
                _round_xml_number(child.attrib.get("y"), 0),
                _round_xml_number(child.attrib.get("width"), 120),
                _round_xml_number(child.attrib.get("height"), 80),
            )
            break
    return bounds


def _bpmn_sequence_flow_refs(root: ET.Element) -> dict[str, tuple[str, str]]:
    refs: dict[str, tuple[str, str]] = {}
    for node in root.iter():
        if _xml_local(node.tag) != "sequenceFlow":
            continue
        flow_id = node.attrib.get("id", "")
        source_ref = node.attrib.get("sourceRef", "")
        target_ref = node.attrib.get("targetRef", "")
        if flow_id and source_ref and target_ref:
            refs[flow_id] = (source_ref, target_ref)
    return refs


def _edge_waypoints(edge: ET.Element) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    for child in edge:
        if _xml_local(child.tag) == "waypoint":
            points.append((_round_xml_number(child.attrib.get("x"), 0), _round_xml_number(child.attrib.get("y"), 0)))
    return points


def _round_xml_number(value: str | None, fallback: int) -> int:
    try:
        return int(round(float(value))) if value is not None else fallback
    except (TypeError, ValueError):
        return fallback


def _script_from_app_model(scripts: dict, element_id: str) -> str:
    value = scripts.get(element_id) if isinstance(scripts, dict) else None
    if isinstance(value, dict):
        return str(value.get("groovy") or "")
    if value is not None:
        return str(value)
    return ""


def _minimal_collibra_script(element_id: str) -> str:
    variable = _safe_filename(str(element_id)).replace("-", "_")
    return f"// #importFile NONE\nexecution.setVariable('{variable}Completed', true)"


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


def _safe_public_error(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"sk-[^\s,'\")]+", "sk-***", text)
    text = re.sub(r"Bearer\s+[^\s,'\")]+", "Bearer ***", text)
    text = re.sub(r"(?i)(api[_ -]?key\s*(?:is|=|:)?\s*)[^\s,'\")]+", r"\1***", text)
    return text[:1000]


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


def _groovy_generation_context(element: dict, prompt: str, payload: dict | None = None) -> tuple[str, str]:
    payload = payload or {}
    element_id = str(element.get("id") or payload.get("elementId") or "selectedElement")
    app_model = payload.get("appModel") or {}
    element_properties = app_model.get("elementProperties") or {}
    selected_properties = element_properties.get(element_id) or {}
    script_excerpt = _nearby_script_excerpts(app_model.get("scripts") or {}, element_id)
    form_keys = ", ".join(sorted((app_model.get("forms") or {}).keys())[:12])
    query = "\n".join(
        [
            str(prompt or ""),
            f"BPMN element {element_id} {element.get('type', '')} {element.get('name', '')}",
            f"Element properties {json.dumps(selected_properties, default=str)[:1000]}",
            "organization standards previous Groovy code Collibra OOTB workflow UUID role relation assetApi relationApi responsibilityApi Java API v2",
            script_excerpt[:2500],
            f"Available form keys: {form_keys}",
        ]
    )
    retrieval = rag_engine.retrieve(query, limit=12)
    context = retrieval.render()
    org_profile = _organization_code_profile(context, app_model, element_id)
    return context, org_profile


def _nearby_script_excerpts(scripts: dict, selected_element_id: str) -> str:
    excerpts: list[str] = []
    for key, value in list((scripts or {}).items())[:8]:
        groovy = value.get("groovy", "") if isinstance(value, dict) else str(value or "")
        if not groovy.strip():
            continue
        label = "selected" if key == selected_element_id else "existing"
        excerpts.append(f"## {label} script {key}\n{groovy[:1400]}")
    return "\n\n".join(excerpts)


def _organization_code_profile(context: str, app_model: dict, selected_element_id: str) -> str:
    script_text = _nearby_script_excerpts(app_model.get("scripts") or {}, selected_element_id)
    combined = f"{context}\n\n{script_text}"
    imports = sorted(set(re.findall(r"(?m)^\s*import\s+(com\.collibra[\w.]+|java\.[\w.]+)\s*;?\s*$", combined)))[:18]
    get_vars = sorted(set(re.findall(r"execution\.getVariable\(['\"]([^'\"]+)['\"]\)", combined)))[:30]
    set_vars = sorted(set(re.findall(r"execution\.setVariable\(['\"]([^'\"]+)['\"]", combined)))[:30]
    api_calls = sorted(set(re.findall(r"\b(assetApi|relationApi|responsibilityApi|attributeApi|userApi|loggerApi|mail|users)\.[A-Za-z_]\w+", combined)))[:30]
    source_files = []
    for match in re.finditer(r"source=([^\s]+)", context):
        name = Path(match.group(1).replace("\\", "/")).name
        if name and name not in source_files:
            source_files.append(name)
        if len(source_files) >= 10:
            break
    uuid_lines = []
    for line in combined.splitlines():
        lowered = line.lower()
        if any(token in lowered for token in ("uuid", "role", "relation type", "asset type", "workflow key")):
            cleaned = line.strip()
            if cleaned and cleaned not in uuid_lines:
                uuid_lines.append(cleaned[:240])
        if len(uuid_lines) >= 12:
            break
    return "\n".join(
        [
            "Organization-aware Groovy profile derived from RAG and current package:",
            f"- RAG/previous-code sources: {', '.join(source_files) if source_files else 'No named sources found in current retrieval.'}",
            f"- Reusable explicit imports: {', '.join(imports) if imports else 'Use only imports required by this block.'}",
            f"- Observed input variables: {', '.join(get_vars) if get_vars else 'None found; derive from prompt/form fields.'}",
            f"- Observed output variables: {', '.join(set_vars) if set_vars else 'None found; set clear execution variables for downstream blocks.'}",
            f"- Observed Collibra APIs/helpers: {', '.join(api_calls) if api_calls else 'Use injected Collibra workflow APIs when grounded by task purpose.'}",
            "- UUID/relation/role hints:",
            *[f"  - {line}" for line in uuid_lines[:12]],
        ]
    ).strip()


def _groovy_implementation_plan(element: dict, prompt: str, org_profile: str) -> list[str]:
    element_label = f"{element.get('id', 'selected element')} ({element.get('type', 'BPMN element')})"
    return [
        f"Analyze the selected BPMN block {element_label} and the user instruction.",
        "Retrieve RAG evidence for organization standards, previous workflow scripts, UUID/relation mappings, forms and API classes.",
        "Choose only the Collibra APIs, process variables and DTO imports supported by the retrieved evidence and the block purpose.",
        "Write a Collibra Workflow Designer Groovy snippet using string2Uuid(...) for UUID values and defensive execution-variable checks.",
        "Compile/lint locally, repair deterministic standards issues, then use AI repair with compiler errors and RAG context if needed.",
    ]


def _ai_or_compat_groovy(element: dict, prompt: str, context: str, model_id: str, org_profile: str = "", force_ai: bool = False) -> str:
    ootb_style = load_ootb_groovy_profile(settings).render_for_prompt(f"{element.get('name', '')} {element.get('type', '')} {prompt}")
    request = f"""You are generating Collibra Workflow Designer Groovy, not Java.
Return only compile-safe Groovy code for the selected BPMN element.

Element:
{json.dumps(element, indent=2, default=str)}

User instruction:
{prompt}

Retrieved RAG and organization context:
{context[:8000]}

Organization-specific code profile:
{org_profile}

{ootb_style}

Rules:
- Use Groovy snippet syntax and explicit imports. Do not return a Java class, `public static void main`, or markdown fences.
- Use Collibra Java API v2 DTO builder classes only when grounded by context or obvious package names.
- For sequence flows, return Groovy/listener guidance as code comments plus a JUEL condition example.
- UUIDs in Collibra are data identifiers, not packages. Use `string2Uuid(variableOrUuidText)` as seen in OOTB workflows.
- Do not use `UUID.fromString(...)` in generated workflow snippets. Do not add `import java.util.UUID`.
- Never import `uuid`, `UUID`, or any made-up Collibra UUID package.
- Start generated script tasks with `// #importFile NONE`.
- Before writing code, internally devise a small implementation plan using RAG/previous code; return only the final Groovy.
- Tailor variable names, forms, roles, UUID placeholders and relation logic to the retrieved organization profile.
- Never output markdown fences.
"""
    text = request_text_completion(settings, request, model_id=model_id, action="groovy_generation")
    code = _strip_code_fence(text or "")
    if code.strip() and _looks_like_collibra_groovy_snippet(code):
        return code
    if force_ai:
        raise HTTPException(
            status_code=400,
            detail="AI Groovy generation failed or returned invalid code. Check the selected model/API key and try again.",
        )
    return _compat_groovy(element, prompt, context)


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
    try:
        answer = request_text_completion(settings, prompt, model_id=model_id, action="workflow_documentation")
        return (answer or "").strip()
    except Exception:
        return ""


def _markdown_to_confluence_html(markdown: str) -> str:
    import html

    lines = []
    in_list = False
    for raw in str(markdown or "").splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            lines.append(f"<li>{html.escape(line[2:].strip())}</li>")
        elif not line.strip():
            if in_list:
                lines.append("</ul>")
                in_list = False
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        lines.append("</ul>")
    return "<!doctype html><html><body>\n" + "\n".join(lines) + "\n</body></html>\n"


def _strip_code_fence(text: str) -> str:
    value = str(text or "").strip()
    match = re.search(r"```(?:groovy|java|text)?\s*(.*?)```", value, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return value


def _looks_like_collibra_groovy_snippet(code: str) -> bool:
    lowered = str(code or "").lower()
    if re.search(r"(?m)^\s*(public\s+)?class\s+\w+", code):
        return False
    if "public static void main" in lowered:
        return False
    if "uuid.fromstring" in lowered or re.search(r"(?m)^\s*import\s+java\.util\.uuid\s*;?\s*$", lowered):
        return False
    if re.search(r"(?m)^\s*import\s+(?!java\.util\.uuid\b)(?:uuid|.*\.uuid|.*\.uuid\.\*)\s*;?\s*$", lowered):
        return False
    return True


def _compat_groovy(element: dict, prompt: str, context: str) -> str:
    element_type = str(element.get("type", ""))
    element_id = element.get("id", "selectedElement")
    label = (str(element.get("name") or "") + " " + str(prompt or "") + " " + element_type).lower()
    if "SequenceFlow" in element_type or "Gateway" in element_type:
        return """// Condition/listener guidance for this BPMN element.
// Use this as a sequence-flow condition when appropriate:
// ${approvalDecision == 'approve'}

def approvalDecision = execution.getVariable('approvalDecision')
execution.setVariable('lastEvaluatedFlow', '%s')
return approvalDecision != null
""" % element_id
    if any(token in label for token in ("mail", "email", "notify", "notification", "sendtask")):
        return """// #importFile NONE
def recipients = users.getUserIds("user(${startUser})")
if (recipients.isEmpty()) {
    loggerApi.warn("No users to send a mail to, no mail will be sent")
} else {
    mail.sendMails(recipients, "workflow-notification", null, execution)
}
execution.setVariable("%sCompleted", true)
""" % _groovy_var(element_id)
    if "relation" in label:
        return """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest

def sourceAssetId = execution.getVariable("sourceAssetId") ?: execution.getVariable("assetId")
def targetAssetId = execution.getVariable("targetAssetId")
def relationTypeId = execution.getVariable("relationTypeId")

if (sourceAssetId && targetAssetId && relationTypeId) {
    relationApi.addRelation(AddRelationRequest.builder()
        .sourceId(string2Uuid(sourceAssetId.toString()))
        .targetId(string2Uuid(targetAssetId.toString()))
        .typeId(string2Uuid(relationTypeId.toString()))
        .build())
    execution.setVariable("%sCompleted", true)
} else {
    loggerApi.warn("Relation creation skipped because source, target, or relation type is missing")
    execution.setVariable("%sCompleted", false)
}
""" % (_groovy_var(element_id), _groovy_var(element_id))
    if any(token in label for token in ("responsibility", "owner", "steward role", "assign")):
        return """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest

def ownerId = execution.getVariable("ownerId") ?: execution.getVariable("requesterId")
def roleId = execution.getVariable("roleId")
def resourceId = execution.getVariable("assetId") ?: item.id

if (ownerId && roleId && resourceId) {
    responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
        .ownerId(string2Uuid(ownerId.toString()))
        .resourceId(resourceId instanceof String ? string2Uuid(resourceId) : resourceId)
        .roleId(string2Uuid(roleId.toString()))
        .resourceType(item.type)
        .build())
    execution.setVariable("%sCompleted", true)
} else {
    loggerApi.warn("Responsibility assignment skipped because owner, role, or resource is missing")
    execution.setVariable("%sCompleted", false)
}
""" % (_groovy_var(element_id), _groovy_var(element_id))
    if any(token in label for token in ("asset status", "status", "approve", "reject", "change asset", "update asset")):
        return """// #importFile NONE
import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest

def statusId = execution.getVariable("targetStatusId") ?: execution.getVariable("approvedStatusId")
def assetId = execution.getVariable("assetId") ?: item.id

if (statusId && assetId) {
    assetApi.changeAsset(ChangeAssetRequest.builder()
        .id(assetId instanceof String ? string2Uuid(assetId) : assetId)
        .statusId(string2Uuid(statusId.toString()))
        .build())
    execution.setVariable("%sCompleted", true)
} else {
    loggerApi.warn("Asset status update skipped because asset or status id is missing")
    execution.setVariable("%sCompleted", false)
}
""" % (_groovy_var(element_id), _groovy_var(element_id))
    if any(token in label for token in ("validate", "required", "request", "form")):
        return """// #importFile NONE
def missingFields = []
["assetId", "businessJustification"].each { fieldName ->
    def value = execution.getVariable(fieldName)
    if (value == null || value.toString().trim().isEmpty()) {
        missingFields.add(fieldName)
    }
}
execution.setVariable("validationPassed", missingFields.isEmpty())
execution.setVariable("validationMessage", missingFields.isEmpty() ? "Request is complete" : "Missing required fields: " + missingFields.join(", "))
"""
    return """// #importFile NONE

// Generated for BPMN element: %s
// Prompt: %s
// Retrieved Collibra context is available in the AI console response. UUID values must come from forms, config, or RAG mappings.

execution.setVariable('%sCompleted', true)
loggerApi.info('Completed workflow step %s')
""" % (element_id, prompt[:300].replace("\n", " "), _groovy_var(element_id), element_id)


def _groovy_var(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", str(value or "step")).strip("_")
    if not clean:
        clean = "step"
    if clean[0].isdigit():
        clean = "step_" + clean
    return clean[:80]


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
