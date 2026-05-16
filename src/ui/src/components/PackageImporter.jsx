import React, { useState } from 'react';
import JSZip from 'jszip';
import { importWorkflow } from '../api.js';

export default function PackageImporter({ onImported }) {
  const [status, setStatus] = useState('');

  async function onPackage(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setStatus(`Importing ${file.name}...`);
    try {
      let result;
      try {
        result = await importWorkflow(file);
      } catch (backendErr) {
        result = await browserFallbackImport(file, backendErr);
      }
      onImported(result);
      const warning = result.warnings?.length ? ` Warnings: ${result.warnings.join('; ')}` : '';
      const chosen = result.chosenBpmn ? ` BPMN: ${result.chosenBpmn}.` : '';
      setStatus(`Loaded ${file.name}.${chosen} Members: ${(result.members || []).length}.${warning}`);
    } catch (err) {
      setStatus(`Import failed: ${err.message}`);
    } finally {
      e.target.value = '';
    }
  }

  return (
    <div className="importer">
      <label>Import workflow package</label>
      <input type="file" accept=".zip,.bpmn,.xml,.bpmn20.xml,.form,.app" onChange={onPackage} />
      <small>Loads Collibra ZIP/BPMN/bpmn20 XML. ZIP import chooses a real BPMN definition first, then app/forms/scripts.</small>
      <small>{status}</small>
    </div>
  );
}

async function browserFallbackImport(file, backendErr) {
  const name = file.name;
  const lower = name.toLowerCase();
  if (lower.endsWith('.zip')) {
    const zip = await JSZip.loadAsync(await file.arrayBuffer());
    const members = Object.keys(zip.files).filter(k => !zip.files[k].dir);
    const warnings = [`Backend import failed, used browser fallback: ${backendErr.message}`];
    const candidates = [];
    const forms = {};
    const appModel = { metadata: { name, format: 'BROWSER_FALLBACK_IMPORT' }, scripts: {}, forms: {}, uuidMappings: {}, validationRules: [], elementProperties: {} };
    for (const member of members) {
      const entry = zip.files[member];
      const data = await entry.async('string');
      const normalized = normalizeXml(data);
      const l = member.toLowerCase();
      if ((l.endsWith('.bpmn') || l.endsWith('.bpmn20.xml') || l.endsWith('.xml')) && looksLikeBpmn(normalized)) {
        const priority = l.endsWith('.bpmn') ? 0 : l.endsWith('.bpmn20.xml') ? 1 : 2;
        candidates.push({ priority, member, xml: normalized });
      } else if (l.endsWith('.form')) {
        const parsed = parseCollibraForm(normalized, member);
        forms[parsed.key] = parsed;
      } else if (l.endsWith('.groovy')) {
        appModel.scripts[basename(member)] = { groovy: data, source: member };
      } else if (l.endsWith('.app')) {
        const parsed = parseJsonOrText(normalized);
        if (parsed && typeof parsed === 'object') Object.assign(appModel, deepMerge(appModel, parsed));
      }
    }
    candidates.sort((a, b) => a.priority - b.priority || a.member.localeCompare(b.member));
    const chosen = candidates[0];
    if (chosen?.xml) {
      const extracted = extractBpmnMetadata(chosen.xml, chosen.member, forms);
      appModel.scripts = deepMerge(appModel.scripts, extracted.scripts);
      appModel.elementProperties = deepMerge(appModel.elementProperties, extracted.elementProperties);
      Object.assign(forms, extracted.forms);
      appModel.forms = deepMerge(appModel.forms, forms);
      appModel.importDiagnostics = extracted.diagnostics;
      warnings.push(...extracted.warnings);
    }
    return { bpmnXml: chosen?.xml || null, chosenBpmn: chosen?.member, appModel, forms, members, warnings };
  }
  const text = await file.text();
  if ((lower.endsWith('.bpmn') || lower.endsWith('.xml')) && looksLikeBpmn(text)) {
    return { bpmnXml: normalizeXml(text), chosenBpmn: name, appModel: { metadata: { name, format: 'BROWSER_FALLBACK_IMPORT' }, scripts: {}, forms: {}, uuidMappings: {}, validationRules: [], elementProperties: {} }, forms: {}, members: [name], warnings: [`Backend import failed, used browser fallback: ${backendErr.message}`] };
  }
  throw backendErr;
}

function looksLikeBpmn(xml) {
  const low = String(xml || '').slice(0, 16000).toLowerCase();
  return low.includes('<bpmn:definitions') || (low.includes('<definitions') && (low.includes('bpmn') || low.includes('www.omg.org/spec/bpmn')));
}

function normalizeXml(xml) {
  let data = String(xml || '').replace(/^\uFEFF/, '').trim();
  const starts = [data.indexOf('<?xml'), data.indexOf('<bpmn:definitions'), data.indexOf('<definitions')].filter(v => v >= 0).sort((a, b) => a - b);
  if (starts.length && starts[0] > 0) data = data.slice(starts[0]);
  return data.trim();
}

function parseJsonOrText(text) {
  try { return JSON.parse(text); } catch { return text; }
}

function parseCollibraForm(text, source) {
  const parsed = parseJsonOrText(text);
  if (!parsed || typeof parsed !== 'object') return { key: basename(source).replace(/^form-/, ''), name: basename(source), fields: [], outcomes: [], raw: parsed, source };
  const metadata = parsed.metadata || {};
  const key = metadata.key || parsed.key || basename(source).replace(/^form-/, '');
  const fields = [];
  (parsed.fields || []).forEach((field, index) => fields.push(normalizeField(field, index, 0, 0)));
  (parsed.rows || []).forEach((row, rowIndex) => (row.cols || []).forEach((field, colIndex) => fields.push(normalizeField(field, fields.length, rowIndex, colIndex))));
  return {
    key,
    name: metadata.name || parsed.name || key,
    description: metadata.description || parsed.description || '',
    version: metadata.version || '',
    modelType: metadata.modelType || 'form',
    palette: metadata.palette || '',
    source,
    fields,
    outcomes: (parsed.outcomes || []).map(outcome => ({ label: outcome.label || outcome.value || '', value: outcome.value || outcome.label || '', primary: Boolean(outcome.primary) })),
    rows: parsed.rows || [],
    metadata,
    raw: parsed
  };
}

function normalizeField(field, index, row, column) {
  const designInfo = field.designInfo || {};
  const id = field.id || field.key || `field_${index + 1}`;
  return {
    id,
    name: field.name || field.label || id,
    label: field.label || field.name || id,
    type: field.type || designInfo.stencilId || 'string',
    required: Boolean(field.isRequired ?? field.required),
    visible: field.visible ?? true,
    enabled: field.enabled ?? true,
    value: field.value ?? field.default,
    row,
    column,
    size: field.size,
    stencilId: designInfo.stencilId,
    extraSettings: field.extraSettings || {}
  };
}

function extractBpmnMetadata(xml, source, forms) {
  const doc = new DOMParser().parseFromString(xml, 'text/xml');
  const scripts = {};
  const elementProperties = {};
  const inlineForms = {};
  const warnings = [];
  const diagnostics = { sourceBpmn: source, scriptTasks: 0, embeddedScripts: 0, userTasks: 0, sequenceFlows: 0, formReferences: 0, inlineForms: 0, missingForms: [] };
  [...doc.querySelectorAll('*')].forEach(node => {
    const local = node.localName;
    const id = node.getAttribute('id');
    if (!id) return;
    if (local === 'scriptTask') diagnostics.scriptTasks += 1;
    if (local === 'userTask') diagnostics.userTasks += 1;
    if (local === 'sequenceFlow') diagnostics.sequenceFlows += 1;
    if (!['scriptTask', 'userTask', 'serviceTask', 'sendTask', 'receiveTask', 'manualTask', 'businessRuleTask', 'callActivity', 'subProcess', 'exclusiveGateway', 'parallelGateway', 'inclusiveGateway', 'eventBasedGateway', 'sequenceFlow', 'startEvent', 'endEvent', 'boundaryEvent', 'intermediateCatchEvent', 'intermediateThrowEvent'].includes(local)) return;
    const attrs = Object.fromEntries([...node.attributes].map(attr => [attr.localName, attr.value]));
    const formKey = attrs.formKey || node.getAttribute('flowable:formKey') || '';
    const prop = {
      elementId: id,
      elementType: `bpmn:${local.slice(0, 1).toUpperCase()}${local.slice(1)}`,
      elementName: node.getAttribute('name') || '',
      formKey,
      execution: local === 'userTask' ? 'user-form' : local === 'scriptTask' ? 'script-groovy' : local === 'sequenceFlow' || local.endsWith('Gateway') ? 'gateway-condition' : 'service-groovy',
      importedFrom: source,
      rawAttributes: attrs
    };
    if (local === 'scriptTask') {
      const script = node.getElementsByTagName('script')?.[0]?.textContent?.trim() || '';
      if (script) {
        diagnostics.embeddedScripts += 1;
        scripts[id] = { groovy: script, elementId: id, elementType: prop.elementType, elementName: prop.elementName, source, scriptFormat: attrs.scriptFormat || 'groovy', importedFrom: 'bpmn:scriptTask' };
      }
    }
    if (local === 'sequenceFlow') {
      prop.condition = node.getElementsByTagName('conditionExpression')?.[0]?.textContent?.trim() || '';
      prop.skipExpression = attrs.skipExpression || '';
    }
    const inlineFields = [...node.getElementsByTagName('flowable:formProperty'), ...node.getElementsByTagName('formProperty')].map((field, index) => normalizeField(Object.fromEntries([...field.attributes].map(attr => [attr.localName, attr.value])), index, 0, index));
    if (inlineFields.length) {
      prop.inlineFormProperties = inlineFields;
      const key = formKey && forms[formKey] ? `${id}InlineForm` : (formKey || `${id}InlineForm`);
      if (!formKey) prop.formKey = key;
      inlineForms[key] = { key, name: `${prop.elementName || id} Inline Form`, source, modelType: 'inline-form', fields: inlineFields, outcomes: inlineFields.filter(field => field.type === 'taskButton'), rows: [] };
      diagnostics.inlineForms += 1;
    }
    if (prop.formKey) {
      diagnostics.formReferences += 1;
      if (!forms[prop.formKey] && !inlineForms[prop.formKey]) diagnostics.missingForms.push({ elementId: id, formKey: prop.formKey });
    }
    elementProperties[id] = prop;
  });
  if (diagnostics.missingForms.length) warnings.push(`Missing form definitions for ${diagnostics.missingForms.slice(0, 5).map(item => `${item.elementId}->${item.formKey}`).join(', ')}.`);
  return { scripts, elementProperties, forms: inlineForms, diagnostics, warnings };
}

function basename(path) {
  return path.split('/').pop().replace(/\.[^.]+$/, '');
}

function deepMerge(left, right) {
  const result = { ...(left || {}) };
  Object.entries(right || {}).forEach(([key, value]) => {
    if (value && typeof value === 'object' && !Array.isArray(value) && result[key] && typeof result[key] === 'object' && !Array.isArray(result[key])) {
      result[key] = deepMerge(result[key], value);
    } else {
      result[key] = value;
    }
  });
  return result;
}
