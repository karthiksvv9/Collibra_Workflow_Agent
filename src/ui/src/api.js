const jsonHeaders = { 'Content-Type': 'application/json' };
const API_BASE = import.meta.env.VITE_API_BASE || '';

function apiPath(path) {
  return `${API_BASE}${path}`;
}

export async function importWorkflow(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(apiPath('/api/workflow/import'), { method: 'POST', body: form });
  return checkedJson(res);
}

export async function exportWorkflow(payload) {
  const res = await fetch(apiPath('/api/workflow/export'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = payload.packageName || 'collibra-workflow-agent.zip';
  a.click();
  URL.revokeObjectURL(url);
}

export async function generateCode(payload) {
  const res = await fetch(apiPath('/api/agent/generate-code'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function designWorkflow(payload) {
  const res = await fetch(apiPath('/api/agent/design'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function runAutonomousAgent(payload) {
  const res = await fetch(apiPath('/api/agent/autonomous-run'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function compileGroovy(payload) {
  const res = await fetch(apiPath('/api/compile/groovy'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function simulateWorkflow(payload) {
  const res = await fetch(apiPath('/api/run/simulate'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function generateDocumentation(payload) {
  const res = await fetch(apiPath('/api/workflow/documentation'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function testWorkflowPackage(payload) {
  const res = await fetch(apiPath('/api/workflow/test-package'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function runWorkflowTestCases(payload) {
  const res = await fetch(apiPath('/api/workflow/test-cases'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function uploadRagFiles(files) {
  const form = new FormData();
  Array.from(files).forEach(f => form.append('files', f));
  const res = await fetch(apiPath('/api/rag/upload'), { method: 'POST', body: form });
  return checkedJson(res);
}

export async function ingestFiles(files) {
  const form = new FormData();
  Array.from(files).forEach(f => form.append('files', f));
  const res = await fetch(apiPath('/api/rag/ingest'), { method: 'POST', body: form });
  return checkedJson(res);
}

export async function generateRagIndex() {
  const res = await fetch(apiPath('/api/rag/index'), { method: 'POST' });
  return checkedJson(res);
}

export async function reindexRag() {
  const res = await fetch(apiPath('/api/rag/reindex'), { method: 'POST' });
  return checkedJson(res);
}

export async function getRagStatus() {
  const res = await fetch(apiPath('/api/rag/status'));
  return checkedJson(res);
}

export async function downloadRagTemplate() {
  const res = await fetch(apiPath('/api/rag/template'));
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'Collibra_Relation_UUID_Template.xlsx';
  a.click();
  URL.revokeObjectURL(url);
}

export async function ragChat(payload) {
  const res = await fetch(apiPath('/api/rag/chat'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

export async function ragQuery(payload) {
  const res = await fetch(apiPath('/api/rag/query'), { method: 'POST', headers: jsonHeaders, body: JSON.stringify(payload) });
  return checkedJson(res);
}

async function checkedJson(res) {
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
