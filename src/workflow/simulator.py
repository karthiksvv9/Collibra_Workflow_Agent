from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.workflow.bpmn import BpmnModel
from src.workflow.form import FormModel


@dataclass(slots=True)
class SimulationStep:
    node_id: str
    node_type: str
    name: str
    status: str
    detail: str


@dataclass(slots=True)
class SimulationResult:
    steps: list[SimulationStep] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class WorkflowSimulator:
    def simulate(
        self,
        model: BpmnModel,
        forms: list[FormModel] | None = None,
        variables: dict[str, Any] | None = None,
        max_steps: int = 100,
    ) -> SimulationResult:
        forms_by_key = {form.key: form for form in (forms or [])}
        state = dict(variables or {})
        result = SimulationResult(variables=state)
        errors = model.validate()
        if errors:
            result.errors.extend(errors)
            return result
        current = next(node for node in model.nodes if node.type == "startEvent")
        visited = 0
        while visited < max_steps:
            visited += 1
            detail = ""
            status = "completed"
            if current.type == "userTask" and current.form_key:
                form = forms_by_key.get(current.form_key)
                if form:
                    missing = [field.id for field in form.fields if field.required and field.id not in state]
                    status = "waiting" if missing else "completed"
                    detail = f"Form {form.name}; missing required: {', '.join(missing) or 'none'}"
                    for field in form.fields:
                        state.setdefault(field.id, field.default)
                else:
                    status = "error"
                    detail = f"Missing form {current.form_key}"
                    result.errors.append(detail)
            elif current.type == "scriptTask":
                detail = "Groovy script would execute in Collibra workflow context."
            elif current.type == "serviceTask":
                detail = "Service/API task would execute asynchronously when configured."
            result.steps.append(
                SimulationStep(
                    node_id=current.id,
                    node_type=current.type,
                    name=current.name,
                    status=status,
                    detail=detail,
                )
            )
            if current.type == "endEvent" or status in {"error", "waiting"}:
                return result
            outgoing = [flow for flow in model.flows if flow.source_ref == current.id]
            if not outgoing:
                result.errors.append(f"No outgoing sequence flow from {current.id}.")
                return result
            chosen = _choose_flow(outgoing, state)
            next_node = model.find_node(chosen.target_ref)
            if next_node is None:
                result.errors.append(f"Sequence flow {chosen.id} points to missing node {chosen.target_ref}.")
                return result
            current = next_node
        result.errors.append(f"Simulation exceeded max_steps={max_steps}; possible cycle.")
        return result


def _choose_flow(flows, state):
    for flow in flows:
        if not flow.condition:
            return flow
        if _condition_matches(flow.condition, state):
            return flow
    return flows[0]


def _condition_matches(condition: str, state: dict[str, Any]) -> bool:
    expression = condition.strip()
    if expression.startswith("${") and expression.endswith("}"):
        expression = expression[2:-1]
    for operator in ("==", "!="):
        if operator in expression:
            left, right = [part.strip().strip("'\"") for part in expression.split(operator, 1)]
            actual = state.get(left)
            return (str(actual) == right) if operator == "==" else (str(actual) != right)
    return bool(state.get(expression))
