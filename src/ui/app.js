const state = {
  process: null,
  forms: [],
  selectedId: null,
  lastZipPath: null,
  bpmnXml: "",
};

const canvas = document.getElementById("canvas");
const flowLayer = document.getElementById("flowLayer");
const chatLog = document.getElementById("chatLog");
const runLog = document.getElementById("runLog");

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((tab) => tab.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(`${button.dataset.tab}Tab`).classList.add("active");
  });
});

document.querySelectorAll(".tool").forEach((button) => {
  button.addEventListener("click", () => addNode(button.dataset.type));
});

document.getElementById("buildBtn").addEventListener("click", buildWorkflow);
document.getElementById("simulateBtn").addEventListener("click", simulateWorkflow);
document.getElementById("ingestBtn").addEventListener("click", ingestCorpus);
document.getElementById("exportBtn").addEventListener("click", exportPackage);
document.getElementById("applyPropsBtn").addEventListener("click", applyProperties);
document.getElementById("askBtn").addEventListener("click", askAboutBlock);
document.getElementById("importFile").addEventListener("change", importWorkflow);

function seed() {
  state.process = {
    process_id: "draftWorkflow",
    name: "Draft Workflow",
    lanes: ["Requester", "Data Steward", "Collibra Automation"],
    nodes: [
      { id: "start", type: "startEvent", name: "Start", lane: "Requester", x: 80, y: 90 },
      { id: "review", type: "userTask", name: "Review", lane: "Data Steward", x: 300, y: 235 },
      { id: "end", type: "endEvent", name: "Done", lane: "Requester", x: 560, y: 90 },
    ],
    flows: [
      { id: "flow_start_review", source_ref: "start", target_ref: "review", name: "" },
      { id: "flow_review_end", source_ref: "review", target_ref: "end", name: "" },
    ],
  };
  render();
}

async function ingestCorpus() {
  addMessage("System", "Ingesting local RAG corpus...");
  const response = await fetch("/api/ingest", { method: "POST" });
  const data = await response.json();
  addMessage("RAG", `${data.documents} documents, ${data.chunks} chunks, ${data.relations} relations, ${data.vector_count} vectors.`);
}

async function buildWorkflow() {
  const masterPrompt = document.getElementById("masterPrompt").value.trim();
  addMessage("Agent", "Designing, compiling, simulating, and packaging...");
  const response = await fetch("/api/workflows/build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ master_prompt: masterPrompt, output_name: "generated_collibra_workflow" }),
  });
  if (!response.ok) {
    addMessage("Error", await response.text());
    return;
  }
  const data = await response.json();
  state.lastZipPath = data.zip_path;
  state.bpmnXml = data.bpmn_xml;
  state.forms = data.forms || [];
  parseBpmn(data.bpmn_xml);
  renderRun(data.simulation);
  addMessage("Agent", `Package ready: ${data.zip_path}`);
}

async function importWorkflow(event) {
  const file = event.target.files[0];
  if (!file) return;
  const body = new FormData();
  body.append("file", file);
  const response = await fetch("/api/workflows/import", { method: "POST", body });
  if (!response.ok) {
    addMessage("Import", await response.text());
    return;
  }
  const data = await response.json();
  state.process = data.process;
  state.forms = data.forms;
  render();
  addMessage("Import", `${file.name} loaded with ${data.validation_errors.length} validation issue(s).`);
}

async function simulateWorkflow() {
  const bpmnXml = state.bpmnXml || serializeDraftNotice();
  const response = await fetch("/api/workflows/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bpmn_xml: bpmnXml, forms: state.forms, variables: {} }),
  });
  if (!response.ok) {
    addMessage("Run", "Build or import a BPMN package before running a full simulation.");
    return;
  }
  renderRun(await response.json());
}

function exportPackage() {
  if (!state.lastZipPath) {
    addMessage("Export", "Build a workflow first.");
    return;
  }
  window.location.href = `/api/workflows/download?path=${encodeURIComponent(state.lastZipPath)}`;
}

function addNode(type) {
  if (!state.process) seed();
  const count = state.process.nodes.length + 1;
  const id = `${type}_${count}`;
  state.process.nodes.push({
    id,
    type,
    name: type.replace(/([A-Z])/g, " $1").trim(),
    lane: state.process.lanes[0],
    x: 160 + count * 34,
    y: 120 + count * 22,
    script: "",
  });
  state.selectedId = id;
  render();
}

function render() {
  canvas.innerHTML = "";
  flowLayer.innerHTML = "";
  if (!state.process) return;
  const lanes = state.process.lanes?.length ? state.process.lanes : ["Workflow"];
  lanes.forEach((lane, index) => {
    const laneEl = document.createElement("div");
    laneEl.className = "lane";
    laneEl.style.top = `${index * 150 + 18}px`;
    laneEl.innerHTML = `<span class="lane-label">${escapeHtml(lane)}</span>`;
    canvas.appendChild(laneEl);
  });
  state.process.nodes.forEach((node) => {
    const element = document.createElement("button");
    element.className = `node ${node.type || ""}${state.selectedId === node.id ? " selected" : ""}`;
    element.style.left = `${node.x || 120}px`;
    element.style.top = `${node.y || 120}px`;
    element.innerHTML = `<span>${escapeHtml(node.name || node.id)}</span>`;
    element.addEventListener("click", () => selectNode(node.id));
    makeDraggable(element, node);
    canvas.appendChild(element);
  });
  drawFlows();
  if (state.selectedId) loadProperties();
}

function drawFlows() {
  const flows = state.process.flows || state.process.sequence_flows || [];
  const nodes = Object.fromEntries(state.process.nodes.map((node) => [node.id, node]));
  flowLayer.setAttribute("width", "1280");
  flowLayer.setAttribute("height", "760");
  flows.forEach((flow) => {
    const source = nodes[flow.source_ref || flow.sourceRef];
    const target = nodes[flow.target_ref || flow.targetRef];
    if (!source || !target) return;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const sx = (source.x || 0) + 120;
    const sy = (source.y || 0) + 38;
    const tx = target.x || 0;
    const ty = (target.y || 0) + 38;
    line.setAttribute("d", `M ${sx} ${sy} C ${sx + 70} ${sy}, ${tx - 70} ${ty}, ${tx} ${ty}`);
    line.setAttribute("fill", "none");
    line.setAttribute("stroke", "#5c6b70");
    line.setAttribute("stroke-width", "2");
    flowLayer.appendChild(line);
  });
}

function selectNode(id) {
  state.selectedId = id;
  render();
}

function loadProperties() {
  const node = selectedNode();
  if (!node) return;
  document.getElementById("propId").value = node.id || "";
  document.getElementById("propName").value = node.name || "";
  document.getElementById("propType").value = node.type || "";
  document.getElementById("propLane").value = node.lane || "";
  document.getElementById("propForm").value = node.form_key || "";
  document.getElementById("propScript").value = node.script || "";
}

function applyProperties() {
  const node = selectedNode();
  if (!node) return;
  node.id = document.getElementById("propId").value.trim() || node.id;
  node.name = document.getElementById("propName").value.trim();
  node.lane = document.getElementById("propLane").value.trim();
  node.form_key = document.getElementById("propForm").value.trim();
  node.script = document.getElementById("propScript").value;
  render();
}

function askAboutBlock() {
  const node = selectedNode();
  const prompt = document.getElementById("blockPrompt").value.trim();
  if (!node || !prompt) return;
  addMessage("You", `${node.id}: ${prompt}`);
  addMessage("Agent", "Targeted block enhancement is queued for the backend enhancement loop; current draft keeps your selected block editable.");
}

function makeDraggable(element, node) {
  let drag = null;
  element.addEventListener("pointerdown", (event) => {
    drag = { x: event.clientX, y: event.clientY, nodeX: node.x || 0, nodeY: node.y || 0 };
    element.setPointerCapture(event.pointerId);
  });
  element.addEventListener("pointermove", (event) => {
    if (!drag) return;
    node.x = Math.max(20, drag.nodeX + event.clientX - drag.x);
    node.y = Math.max(20, drag.nodeY + event.clientY - drag.y);
    element.style.left = `${node.x}px`;
    element.style.top = `${node.y}px`;
    drawFlows();
  });
  element.addEventListener("pointerup", () => {
    drag = null;
  });
}

function parseBpmn(xml) {
  const documentXml = new DOMParser().parseFromString(xml, "application/xml");
  const process = documentXml.getElementsByTagNameNS("*", "process")[0];
  const lanes = [...documentXml.getElementsByTagNameNS("*", "lane")].map((lane) => lane.getAttribute("name") || lane.getAttribute("id"));
  const nodeTags = ["startEvent", "endEvent", "userTask", "scriptTask", "serviceTask", "exclusiveGateway", "parallelGateway", "subProcess", "callActivity"];
  const positions = {};
  [...documentXml.getElementsByTagNameNS("*", "BPMNShape")].forEach((shape) => {
    const id = shape.getAttribute("bpmnElement");
    const bounds = shape.getElementsByTagNameNS("*", "Bounds")[0];
    if (id && bounds) positions[id] = { x: Number(bounds.getAttribute("x")), y: Number(bounds.getAttribute("y")) };
  });
  const nodes = [];
  nodeTags.forEach((tag) => {
    [...documentXml.getElementsByTagNameNS("*", tag)].forEach((element) => {
      const id = element.getAttribute("id");
      const script = element.getElementsByTagNameNS("*", "script")[0]?.textContent || "";
      nodes.push({
        id,
        type: tag,
        name: element.getAttribute("name") || id,
        x: positions[id]?.x || 120,
        y: positions[id]?.y || 120,
        script,
        form_key: element.getAttribute("flowable:formKey") || element.getAttribute("formKey") || "",
      });
    });
  });
  const flows = [...documentXml.getElementsByTagNameNS("*", "sequenceFlow")].map((flow) => ({
    id: flow.getAttribute("id"),
    source_ref: flow.getAttribute("sourceRef"),
    target_ref: flow.getAttribute("targetRef"),
    name: flow.getAttribute("name") || "",
  }));
  state.process = {
    process_id: process?.getAttribute("id") || "importedWorkflow",
    name: process?.getAttribute("name") || "Imported Workflow",
    lanes,
    nodes,
    flows,
  };
  render();
}

function renderRun(simulation) {
  runLog.innerHTML = "";
  const steps = simulation.steps || [];
  steps.forEach((step) => {
    const div = document.createElement("div");
    div.className = "run-step";
    div.innerHTML = `<strong>${escapeHtml(step.name || step.node_id)}</strong>${escapeHtml(step.node_type)} · ${escapeHtml(step.status)}<br>${escapeHtml(step.detail || "")}`;
    runLog.appendChild(div);
  });
  (simulation.errors || []).forEach((error) => {
    const div = document.createElement("div");
    div.className = "run-step";
    div.innerHTML = `<strong>Error</strong>${escapeHtml(error)}`;
    runLog.appendChild(div);
  });
}

function addMessage(who, text) {
  const div = document.createElement("div");
  div.className = "message";
  div.innerHTML = `<strong>${escapeHtml(who)}</strong>${escapeHtml(text)}`;
  chatLog.prepend(div);
}

function selectedNode() {
  return state.process?.nodes.find((node) => node.id === state.selectedId);
}

function serializeDraftNotice() {
  return state.bpmnXml || "";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

seed();
