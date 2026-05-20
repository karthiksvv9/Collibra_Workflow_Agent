from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.dom import minidom
from xml.etree import ElementTree as ET


BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
DI_NS = "http://www.omg.org/spec/DD/20100524/DI"
FLOWABLE_NS = "http://flowable.org/bpmn"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
DSC_NS = "https://dsc.local/collibra/workflows/designer"

ET.register_namespace("bpmn", BPMN_NS)
ET.register_namespace("bpmndi", BPMNDI_NS)
ET.register_namespace("dc", DC_NS)
ET.register_namespace("di", DI_NS)
ET.register_namespace("flowable", FLOWABLE_NS)
ET.register_namespace("xsi", XSI_NS)
ET.register_namespace("dsc", DSC_NS)


@dataclass(slots=True)
class BpmnNode:
    id: str
    type: str
    name: str
    lane: str | None = None
    documentation: str = ""
    script: str = ""
    form_key: str | None = None
    candidate_users: str | None = None
    candidate_groups: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    x: int = 120
    y: int = 120


@dataclass(slots=True)
class SequenceFlow:
    id: str
    source_ref: str
    target_ref: str
    name: str = ""
    condition: str = ""
    skip_expression: str = ""
    flow_type: str = "normal"
    is_default: bool = False
    documentation: str = ""
    listener_code: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BpmnPool:
    id: str
    name: str
    process_ref: str | None = None
    x: int = 40
    y: int = 40
    width: int = 1240
    height: int = 520


@dataclass(slots=True)
class BpmnModel:
    process_id: str
    name: str
    pools: list[BpmnPool] = field(default_factory=list)
    lanes: list[str] = field(default_factory=list)
    nodes: list[BpmnNode] = field(default_factory=list)
    flows: list[SequenceFlow] = field(default_factory=list)
    documentation: str = ""
    executable: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        node_ids = {node.id for node in self.nodes}
        if not any(node.type == "startEvent" for node in self.nodes):
            errors.append("BPMN model must include a startEvent.")
        if not any(node.type == "endEvent" for node in self.nodes):
            errors.append("BPMN model must include an endEvent.")
        for flow in self.flows:
            if flow.source_ref not in node_ids:
                errors.append(f"Sequence flow {flow.id} has unknown sourceRef {flow.source_ref}.")
            if flow.target_ref not in node_ids:
                errors.append(f"Sequence flow {flow.id} has unknown targetRef {flow.target_ref}.")
            for label, expression in (("condition", flow.condition), ("skip expression", flow.skip_expression)):
                if expression and not _looks_like_expression(expression):
                    errors.append(
                        f"Sequence flow {flow.id} {label} should be a Flowable/JUEL expression like ${{approved == true}}."
                    )
        if not errors and self.nodes:
            start_ids = [node.id for node in self.nodes if node.type == "startEvent"]
            end_ids = {node.id for node in self.nodes if node.type == "endEvent"}
            if start_ids and end_ids and not _has_path_to_end(start_ids, end_ids, self.flows):
                errors.append("BPMN model must contain at least one complete path from a startEvent to an endEvent.")
            errors.extend(_flow_node_connectivity_errors(self.nodes, self.flows))
        return errors

    def to_xml(self) -> str:
        definitions = ET.Element(
            _q(BPMN_NS, "definitions"),
            {
                "id": f"{self.process_id}_definitions",
                "targetNamespace": "https://dsc.local/collibra/workflows",
            },
        )
        pools = self.pools or [BpmnPool(id=f"{self.process_id}_pool", name=self.name, process_ref=self.process_id)]
        if pools:
            collaboration = ET.SubElement(
                definitions,
                _q(BPMN_NS, "collaboration"),
                {"id": f"{self.process_id}_collaboration"},
            )
            for pool in pools:
                ET.SubElement(
                    collaboration,
                    _q(BPMN_NS, "participant"),
                    {
                        "id": pool.id,
                        "name": pool.name,
                        "processRef": pool.process_ref or self.process_id,
                    },
                )
        process = ET.SubElement(
            definitions,
            _q(BPMN_NS, "process"),
            {"id": self.process_id, "name": self.name, "isExecutable": str(self.executable).lower()},
        )
        if self.documentation:
            doc = ET.SubElement(process, _q(BPMN_NS, "documentation"))
            doc.text = self.documentation

        if self.lanes:
            lane_set = ET.SubElement(process, _q(BPMN_NS, "laneSet"), {"id": f"{self.process_id}_lanes"})
            for lane in self.lanes:
                lane_el = ET.SubElement(lane_set, _q(BPMN_NS, "lane"), {"id": _id("lane", lane), "name": lane})
                for node in self.nodes:
                    if node.lane == lane:
                        ref = ET.SubElement(lane_el, _q(BPMN_NS, "flowNodeRef"))
                        ref.text = node.id

        for node in self.nodes:
            self._append_node(process, node)
        for flow in self.flows:
            attrs = {"id": flow.id, "sourceRef": flow.source_ref, "targetRef": flow.target_ref}
            if flow.name:
                attrs["name"] = flow.name
            if flow.skip_expression:
                attrs[_q(FLOWABLE_NS, "skipExpression")] = flow.skip_expression
            flow_el = ET.SubElement(process, _q(BPMN_NS, "sequenceFlow"), attrs)
            if flow.documentation:
                doc = ET.SubElement(flow_el, _q(BPMN_NS, "documentation"))
                doc.text = flow.documentation
            if flow.listener_code or flow.properties.get("listenerExpression"):
                extension_elements = ET.SubElement(flow_el, _q(BPMN_NS, "extensionElements"))
                if flow.properties.get("listenerExpression"):
                    ET.SubElement(
                        extension_elements,
                        _q(FLOWABLE_NS, "executionListener"),
                        {"event": "take", "expression": str(flow.properties["listenerExpression"])},
                    )
                if flow.listener_code:
                    listener = ET.SubElement(extension_elements, _q(DSC_NS, "transitionListenerGroovy"))
                    listener.text = flow.listener_code
            if flow.condition:
                condition = ET.SubElement(
                    flow_el,
                    _q(BPMN_NS, "conditionExpression"),
                    {_q(XSI_NS, "type"): "bpmn:tFormalExpression"},
                )
                condition.text = flow.condition

        self._append_diagram(definitions)
        raw = ET.tostring(definitions, encoding="utf-8")
        return minidom.parseString(raw).toprettyxml(indent="  ")

    def _append_node(self, process: ET.Element, node: BpmnNode) -> None:
        tag = NODE_TAGS.get(node.type)
        if tag is None:
            raise ValueError(f"Unsupported BPMN node type: {node.type}")
        attrs = {"id": node.id}
        if node.name:
            attrs["name"] = node.name
        default_flow = next((flow.id for flow in self.flows if flow.source_ref == node.id and flow.is_default), None)
        if default_flow:
            attrs["default"] = default_flow
        if node.type == "scriptTask":
            attrs["scriptFormat"] = "groovy"
            attrs[_q(FLOWABLE_NS, "autoStoreVariables")] = "false"
        if node.type in {"userTask", "startEvent"}:
            if node.form_key:
                attrs[_q(FLOWABLE_NS, "formKey")] = node.form_key
        if node.type == "userTask":
            if node.candidate_users:
                attrs[_q(FLOWABLE_NS, "candidateUsers")] = node.candidate_users
            if node.candidate_groups:
                attrs[_q(FLOWABLE_NS, "candidateGroups")] = node.candidate_groups
        if node.type == "serviceTask":
            for key in ("expression", "delegateExpression", "class", "type"):
                if key in node.properties:
                    attrs[_q(FLOWABLE_NS, key)] = str(node.properties[key])
        if node.type == "callActivity":
            if node.properties.get("calledElement"):
                attrs["calledElement"] = str(node.properties["calledElement"])
            for key in ("calledElementType", "inheritVariables", "businessKey", "sameDeployment", "fallbackToDefaultTenant"):
                if key in node.properties:
                    attrs[_q(FLOWABLE_NS, key)] = str(node.properties[key])
        if node.properties.get("skipExpression"):
            attrs[_q(FLOWABLE_NS, "skipExpression")] = str(node.properties["skipExpression"])
        element = ET.SubElement(process, _q(BPMN_NS, tag), attrs)
        if node.documentation:
            doc = ET.SubElement(element, _q(BPMN_NS, "documentation"))
            doc.text = node.documentation
        if node.type == "scriptTask":
            script = ET.SubElement(element, _q(BPMN_NS, "script"))
            script.text = node.script.strip() or _default_script_text(node.id)

    def _append_diagram(self, definitions: ET.Element) -> None:
        diagram = ET.SubElement(definitions, _q(BPMNDI_NS, "BPMNDiagram"), {"id": f"{self.process_id}_diagram"})
        plane_element = f"{self.process_id}_collaboration"
        plane = ET.SubElement(
            diagram,
            _q(BPMNDI_NS, "BPMNPlane"),
            {"id": f"{self.process_id}_plane", "bpmnElement": plane_element},
        )
        pools = self.pools or [BpmnPool(id=f"{self.process_id}_pool", name=self.name, process_ref=self.process_id)]
        lane_height = 170
        for pool in pools:
            pool_width = max(pool.width, max([node.x for node in self.nodes] or [900]) + 260)
            pool_height = max(pool.height, 80 + max(1, len(self.lanes)) * lane_height)
            shape = ET.SubElement(
                plane,
                _q(BPMNDI_NS, "BPMNShape"),
                {"id": f"{pool.id}_di", "bpmnElement": pool.id, "isHorizontal": "true"},
            )
            ET.SubElement(
                shape,
                _q(DC_NS, "Bounds"),
                {
                    "x": str(pool.x),
                    "y": str(pool.y),
                    "width": str(pool_width),
                    "height": str(pool_height),
                },
            )
            for index, lane in enumerate(self.lanes):
                lane_id = _id("lane", lane)
                lane_shape = ET.SubElement(
                    plane,
                    _q(BPMNDI_NS, "BPMNShape"),
                    {"id": f"{lane_id}_di", "bpmnElement": lane_id, "isHorizontal": "true"},
                )
                ET.SubElement(
                    lane_shape,
                    _q(DC_NS, "Bounds"),
                    {
                        "x": str(pool.x + 30),
                        "y": str(pool.y + index * lane_height),
                        "width": str(max(100, pool_width - 30)),
                        "height": str(lane_height),
                    },
                )
        for node in self.nodes:
            shape = ET.SubElement(
                plane,
                _q(BPMNDI_NS, "BPMNShape"),
                {"id": f"{node.id}_di", "bpmnElement": node.id},
            )
            width, height = _dimensions(node.type)
            ET.SubElement(
                shape,
                _q(DC_NS, "Bounds"),
                {"x": str(node.x), "y": str(node.y), "width": str(width), "height": str(height)},
            )
        for flow in self.flows:
            edge = ET.SubElement(
                plane,
                _q(BPMNDI_NS, "BPMNEdge"),
                {"id": f"{flow.id}_di", "bpmnElement": flow.id},
            )
            source = self.find_node(flow.source_ref)
            target = self.find_node(flow.target_ref)
            if source and target:
                source_width, source_height = _dimensions(source.type)
                target_width, target_height = _dimensions(target.type)
                for x, y in diagram_waypoints(
                    (source.x, source.y, source_width, source_height),
                    (target.x, target.y, target_width, target_height),
                ):
                    ET.SubElement(edge, _q(DI_NS, "waypoint"), {"x": str(x), "y": str(y)})

    def find_node(self, node_id: str) -> BpmnNode | None:
        return next((node for node in self.nodes if node.id == node_id), None)

    @classmethod
    def from_xml(cls, xml_text: str) -> "BpmnModel":
        root = ET.fromstring(xml_text)
        process = next((node for node in root.iter() if _local(node.tag) == "process"), None)
        if process is None:
            raise ValueError("No BPMN process element found.")
        model = cls(
            process_id=process.attrib["id"],
            name=process.attrib.get("name", process.attrib["id"]),
            documentation=_first_doc(process),
            executable=process.attrib.get("isExecutable", "true") == "true",
        )
        model.pools = _pools(root, model.process_id, model.name)
        lane_lookup: dict[str, str] = {}
        for lane in process.iter():
            if _local(lane.tag) != "lane":
                continue
            lane_name = lane.attrib.get("name", lane.attrib.get("id", "Lane"))
            model.lanes.append(lane_name)
            for ref in lane:
                if _local(ref.tag) == "flowNodeRef" and ref.text:
                    lane_lookup[ref.text] = lane_name
        positions = _positions(root)
        default_flow_ids = {node.attrib.get("default", "") for node in process if node.attrib.get("default")}
        for node in process:
            tag = _local(node.tag)
            if tag in REVERSE_NODE_TAGS:
                node_id = node.attrib["id"]
                x, y = positions.get(node_id, (120 + len(model.nodes) * 170, 120))
                model.nodes.append(
                    BpmnNode(
                        id=node_id,
                        type=REVERSE_NODE_TAGS[tag],
                        name=node.attrib.get("name", ""),
                        lane=lane_lookup.get(node_id),
                        documentation=_first_doc(node),
                        script=_script(node),
                        form_key=node.attrib.get(_q(FLOWABLE_NS, "formKey")),
                        candidate_users=node.attrib.get(_q(FLOWABLE_NS, "candidateUsers")),
                        candidate_groups=node.attrib.get(_q(FLOWABLE_NS, "candidateGroups")),
                        properties={
                            _local(key): value
                            for key, value in node.attrib.items()
                            if (key.startswith("{") or _local(key) in {"calledElement"})
                            and _local(key)
                            not in {"formKey", "candidateUsers", "candidateGroups"}
                        },
                        x=x,
                        y=y,
                    )
                )
            if tag == "sequenceFlow":
                model.flows.append(
                    SequenceFlow(
                        id=node.attrib["id"],
                        source_ref=node.attrib.get("sourceRef", ""),
                        target_ref=node.attrib.get("targetRef", ""),
                        name=node.attrib.get("name", ""),
                        condition=_condition(node),
                        skip_expression=node.attrib.get(_q(FLOWABLE_NS, "skipExpression"), ""),
                        flow_type=_flow_type(node, default_flow_ids),
                        is_default=node.attrib["id"] in default_flow_ids,
                        documentation=_first_doc(node),
                        listener_code=_listener_code(node),
                        properties=_flow_properties(node),
                    )
                )
        return model


NODE_TAGS = {
    "startEvent": "startEvent",
    "endEvent": "endEvent",
    "userTask": "userTask",
    "scriptTask": "scriptTask",
    "serviceTask": "serviceTask",
    "manualTask": "manualTask",
    "businessRuleTask": "businessRuleTask",
    "sendTask": "sendTask",
    "receiveTask": "receiveTask",
    "exclusiveGateway": "exclusiveGateway",
    "parallelGateway": "parallelGateway",
    "inclusiveGateway": "inclusiveGateway",
    "eventBasedGateway": "eventBasedGateway",
    "subProcess": "subProcess",
    "callActivity": "callActivity",
    "intermediateCatchEvent": "intermediateCatchEvent",
    "intermediateThrowEvent": "intermediateThrowEvent",
    "boundaryEvent": "boundaryEvent",
    "textAnnotation": "textAnnotation",
}
REVERSE_NODE_TAGS = {value: key for key, value in NODE_TAGS.items()}


def parse_bpmn_file(path: str | Path) -> BpmnModel:
    return BpmnModel.from_xml(Path(path).read_text(encoding="utf-8"))


def write_bpmn_file(model: BpmnModel, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(model.to_xml(), encoding="utf-8")
    return output_path


def _q(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _first_doc(node: ET.Element) -> str:
    for child in node:
        if _local(child.tag) == "documentation":
            return " ".join(child.itertext()).strip()
    return ""


def _script(node: ET.Element) -> str:
    for child in node:
        if _local(child.tag) == "script":
            return child.text or ""
    return ""


def _default_script_text(element_id: str) -> str:
    variable = "".join(char if char.isalnum() else "_" for char in str(element_id or "scriptTask"))
    return f"// #importFile NONE\nexecution.setVariable('{variable}Completed', true)"


def _condition(node: ET.Element) -> str:
    for child in node:
        if _local(child.tag) == "conditionExpression":
            return child.text or ""
    return ""


def _listener_code(node: ET.Element) -> str:
    for child in node.iter():
        if child.tag == _q(DSC_NS, "transitionListenerGroovy"):
            return child.text or ""
    return ""


def _flow_properties(node: ET.Element) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    for child in node.iter():
        if child.tag == _q(FLOWABLE_NS, "executionListener"):
            for key, value in child.attrib.items():
                properties[f"listener{key[:1].upper()}{key[1:]}"] = value
    return properties


def _flow_type(node: ET.Element, default_flow_ids: set[str]) -> str:
    if node.attrib.get("id", "") in default_flow_ids:
        return "default"
    if _condition(node):
        return "conditional"
    if node.attrib.get(_q(FLOWABLE_NS, "skipExpression")):
        return "skip"
    if _listener_code(node) or _flow_properties(node):
        return "listener"
    return "normal"


def _positions(root: ET.Element) -> dict[str, tuple[int, int]]:
    positions: dict[str, tuple[int, int]] = {}
    for shape in root.iter():
        if _local(shape.tag) != "BPMNShape":
            continue
        bpmn_id = shape.attrib.get("bpmnElement")
        for child in shape:
            if _local(child.tag) == "Bounds" and bpmn_id:
                positions[bpmn_id] = (int(float(child.attrib.get("x", 120))), int(float(child.attrib.get("y", 120))))
    return positions


def _pools(root: ET.Element, process_id: str, process_name: str) -> list[BpmnPool]:
    bounds = _pool_bounds(root)
    pools: list[BpmnPool] = []
    for node in root.iter():
        if _local(node.tag) != "participant":
            continue
        pool_id = node.attrib.get("id", f"{process_id}_pool")
        x, y, width, height = bounds.get(pool_id, (40, 40, 1240, 520))
        pools.append(
            BpmnPool(
                id=pool_id,
                name=node.attrib.get("name", process_name),
                process_ref=node.attrib.get("processRef", process_id),
                x=x,
                y=y,
                width=width,
                height=height,
            )
        )
    return pools


def _pool_bounds(root: ET.Element) -> dict[str, tuple[int, int, int, int]]:
    result: dict[str, tuple[int, int, int, int]] = {}
    for shape in root.iter():
        if _local(shape.tag) != "BPMNShape":
            continue
        bpmn_id = shape.attrib.get("bpmnElement")
        for child in shape:
            if _local(child.tag) == "Bounds" and bpmn_id:
                result[bpmn_id] = (
                    int(float(child.attrib.get("x", 40))),
                    int(float(child.attrib.get("y", 40))),
                    int(float(child.attrib.get("width", 1240))),
                    int(float(child.attrib.get("height", 520))),
                )
    return result


def _dimensions(node_type: str) -> tuple[int, int]:
    if node_type in {"startEvent", "endEvent"}:
        return 36, 36
    if node_type.endswith("Gateway"):
        return 50, 50
    if node_type in {"intermediateCatchEvent", "intermediateThrowEvent", "boundaryEvent"}:
        return 36, 36
    if node_type == "textAnnotation":
        return 140, 60
    return 128, 80


def diagram_waypoints(
    source_bounds: tuple[int | float, int | float, int | float, int | float],
    target_bounds: tuple[int | float, int | float, int | float, int | float],
) -> list[tuple[int, int]]:
    """Return orthogonal BPMN DI waypoints docked to shape borders."""
    source_x, source_y, source_width, source_height = [float(value) for value in source_bounds]
    target_x, target_y, target_width, target_height = [float(value) for value in target_bounds]
    source_center_x = source_x + source_width / 2
    source_center_y = source_y + source_height / 2
    target_center_x = target_x + target_width / 2
    target_center_y = target_y + target_height / 2
    delta_x = target_center_x - source_center_x
    delta_y = target_center_y - source_center_y

    if abs(delta_x) >= abs(delta_y):
        if delta_x >= 0:
            start = (source_x + source_width, source_center_y)
            end = (target_x, target_center_y)
        else:
            start = (source_x, source_center_y)
            end = (target_x + target_width, target_center_y)
        if abs(start[1] - end[1]) > 1:
            midpoint_x = (start[0] + end[0]) / 2
            return _clean_waypoints([start, (midpoint_x, start[1]), (midpoint_x, end[1]), end])
        return _clean_waypoints([start, end])

    if delta_y >= 0:
        start = (source_center_x, source_y + source_height)
        end = (target_center_x, target_y)
    else:
        start = (source_center_x, source_y)
        end = (target_center_x, target_y + target_height)
    if abs(start[0] - end[0]) > 1:
        midpoint_y = (start[1] + end[1]) / 2
        return _clean_waypoints([start, (start[0], midpoint_y), (end[0], midpoint_y), end])
    return _clean_waypoints([start, end])


def _clean_waypoints(points: list[tuple[float, float]]) -> list[tuple[int, int]]:
    rounded = [(int(round(x)), int(round(y))) for x, y in points]
    deduped: list[tuple[int, int]] = []
    for point in rounded:
        if not deduped or deduped[-1] != point:
            deduped.append(point)
    changed = True
    while changed and len(deduped) > 2:
        changed = False
        next_points: list[tuple[int, int]] = [deduped[0]]
        for index in range(1, len(deduped) - 1):
            previous = next_points[-1]
            current = deduped[index]
            following = deduped[index + 1]
            if (previous[0] == current[0] == following[0]) or (previous[1] == current[1] == following[1]):
                changed = True
                continue
            next_points.append(current)
        next_points.append(deduped[-1])
        deduped = next_points
    return deduped if len(deduped) >= 2 else rounded[:2]


def _id(prefix: str, label: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]+", "_", label.strip()).strip("_")
    return f"{prefix}_{value or 'default'}"


def _looks_like_expression(expression: str) -> bool:
    value = expression.strip()
    return value.startswith("${") and value.endswith("}")


def _has_path_to_end(start_ids: list[str], end_ids: set[str], flows: list[SequenceFlow]) -> bool:
    adjacency: dict[str, list[str]] = {}
    for flow in flows:
        adjacency.setdefault(flow.source_ref, []).append(flow.target_ref)
    visited: set[str] = set()
    stack = list(start_ids)
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        if node_id in end_ids:
            return True
        visited.add(node_id)
        stack.extend(adjacency.get(node_id, []))
    return False


def _flow_node_connectivity_errors(nodes: list[BpmnNode], flows: list[SequenceFlow]) -> list[str]:
    incoming: dict[str, int] = {}
    outgoing: dict[str, int] = {}
    for flow in flows:
        outgoing[flow.source_ref] = outgoing.get(flow.source_ref, 0) + 1
        incoming[flow.target_ref] = incoming.get(flow.target_ref, 0) + 1
    errors: list[str] = []
    for node in nodes:
        if node.type in {"textAnnotation", "boundaryEvent"}:
            continue
        if node.type != "startEvent" and incoming.get(node.id, 0) == 0:
            errors.append(f"BPMN node {node.id} ({node.type}) has no incoming sequence flow.")
        if node.type != "endEvent" and outgoing.get(node.id, 0) == 0:
            errors.append(f"BPMN node {node.id} ({node.type}) has no outgoing sequence flow.")
    return errors
