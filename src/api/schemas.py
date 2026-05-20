from __future__ import annotations

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    documents: int
    chunks: int
    relations: int
    vector_count: int
    warnings: list[str] = Field(default_factory=list)


class RetrieveRequest(BaseModel):
    question: str
    limit: int = 8


class RetrieveResponse(BaseModel):
    context: str
    sources: list[dict]


class BuildWorkflowRequest(BaseModel):
    master_prompt: str
    output_name: str | None = None


class BuildWorkflowResponse(BaseModel):
    zip_path: str
    bpmn_xml: str
    process: dict
    forms: list[dict]
    validation_errors: list[str]
    compile_results: dict
    simulation: dict
    assumptions: list[str]


class SimulateRequest(BaseModel):
    bpmn_xml: str
    forms: list[dict] = Field(default_factory=list)
    variables: dict = Field(default_factory=dict)


class ExportWorkflowRequest(BaseModel):
    process: dict
    forms: list[dict] = Field(default_factory=list)
    app_name: str = "Generated Collibra Workflow"
    output_name: str = "designer_workflow"


class CompileGroovyRequest(BaseModel):
    script: str = ""
    code: str | None = None
    elementId: str | None = None
    element: dict = Field(default_factory=dict)
    prompt: str = ""
    appModel: dict = Field(default_factory=dict)
    modelId: str | None = None
    autoRepair: bool = False
    maxRepairIterations: int = 3


class SequenceFlowValidateRequest(BaseModel):
    flow: dict


class AIEnhanceRequest(BaseModel):
    target_type: str
    target: dict
    instruction: str
    context: dict = Field(default_factory=dict)


class DebugWorkflowRequest(BaseModel):
    process: dict
    forms: list[dict] = Field(default_factory=list)
    variables: dict = Field(default_factory=dict)


class RepairWorkflowRequest(BaseModel):
    process: dict
    forms: list[dict] = Field(default_factory=list)
    issues: list[dict] = Field(default_factory=list)


class DocumentationRequest(BaseModel):
    process: dict
    forms: list[dict] = Field(default_factory=list)
    prompt: str = ""
