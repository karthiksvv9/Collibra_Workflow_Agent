import React, { useEffect, useMemo, useState } from 'react';
import { Bot, CheckCircle2, Code2, ExternalLink, Save, Sparkles } from 'lucide-react';
import { compileGroovy, generateCode } from '../api.js';

export default function CollibraPropertiesPanel({ selectedElement, appModel, setAppModel, getBpmnXml, addConsole, forms, modelId, modeler }) {
  const elementId = selectedElement?.id;
  const elementScript = useMemo(() => appModel?.scripts?.[elementId] || {}, [appModel, elementId]);
  const elementProps = useMemo(() => appModel?.elementProperties?.[elementId] || {}, [appModel, elementId]);
  const allForms = useMemo(() => ({ ...(appModel?.forms || {}), ...(forms || {}) }), [appModel?.forms, forms]);
  const [prompt, setPrompt] = useState('Generate production Collibra Groovy for this BPMN element. Use Collibra Java API v2 style imports, organization UUID mappings from RAG, defensive null checks, execution variables, comments, and compile-safe code.');
  const [groovy, setGroovy] = useState('');
  const [props, setProps] = useState({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setGroovy(typeof elementScript === 'string' ? elementScript : elementScript.groovy || '');
    setProps({
      execution: elementProps.execution || defaultExecution(selectedElement?.type),
      scope: elementProps.scope || 'asset',
      candidateRole: elementProps.candidateRole || '',
      formKey: elementProps.formKey || flowableAttr(selectedElement, 'formKey') || '',
      calledElement: elementProps.calledElement || selectedElement?.businessObject?.calledElement || flowableAttr(selectedElement, 'calledElement') || '',
      condition: elementProps.condition || '',
      documentation: elementProps.documentation || ''
    });
  }, [elementId, elementScript.groovy, elementProps.execution, elementProps.scope, elementProps.candidateRole, elementProps.formKey, elementProps.calledElement, elementProps.condition, elementProps.documentation, selectedElement?.type]);

  if (!selectedElement) {
    return (
      <div className="properties-panel">
        <div className="empty-panel">
          <b>No BPMN element selected</b>
          <p>Select a task, gateway, sequence flow, pool, lane, event or subprocess on the canvas. Then you can generate Groovy, add conditions, map forms, save metadata and compile.</p>
        </div>
      </div>
    );
  }

  const bo = selectedElement.businessObject || {};
  const canCompile = Boolean(groovy.trim());
  const linkedForm = props.formKey ? allForms[props.formKey] : null;

  function updateProp(key, value) {
    setProps(prev => ({ ...prev, [key]: value }));
  }

  function save() {
    applyBpmnProperties(modeler, selectedElement, props);
    setAppModel(prev => ({
      ...prev,
      scripts: {
        ...(prev.scripts || {}),
        [elementId]: {
          ...(prev.scripts?.[elementId] || {}),
          groovy,
          elementId,
          elementType: selectedElement.type,
          elementName: bo.name || '',
          updatedAt: new Date().toISOString()
        }
      },
      elementProperties: {
        ...(prev.elementProperties || {}),
        [elementId]: {
          ...props,
          elementId,
          elementType: selectedElement.type,
          elementName: bo.name || '',
          updatedAt: new Date().toISOString()
        }
      }
    }));
    addConsole?.({ level: 'success', message: `Saved Collibra metadata for ${elementId}`, detail: { props, groovyBytes: groovy.length } });
  }

  async function askAi() {
    setBusy(true);
    try {
      const bpmnXml = await getBpmnXml();
      const result = await generateCode({
        bpmnXml,
        element: toElementPayload(selectedElement),
        prompt,
        appModel,
        modelId,
        compileAndRepair: true
      });
      const code = result.groovy || result.raw || '';
      setGroovy(code);
      setAppModel(prev => ({
        ...prev,
        scripts: {
          ...(prev.scripts || {}),
          [elementId]: {
            groovy: code,
            summary: result.summary || '',
            reasoning: result.reasoning || [],
            tests: result.tests || [],
            warnings: result.warnings || [],
            compileResults: result.compileResults || [],
            elementType: selectedElement.type,
            elementName: bo.name || '',
            updatedAt: new Date().toISOString()
          }
        }
      }));
      addConsole?.({ level: result.compileStatus === 'passed' ? 'success' : 'info', message: `AI generated Groovy for ${elementId}`, detail: result });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'AI Groovy generation failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  async function compile() {
    setBusy(true);
    try {
      const result = await compileGroovy({ code: groovy, elementId, modelId });
      addConsole?.({ level: result.ok ? 'success' : 'error', message: `Compile ${result.ok ? 'passed' : 'failed'} for ${elementId}`, detail: result });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'Groovy compile failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="properties-panel">
      <div className="property-hero">
        <div>
          <b>{bo.name || elementId}</b>
          <small>{selectedElement.type}</small>
        </div>
        <span className="status-pill"><CheckCircle2 size={13}/> selected</span>
      </div>

      <div className="property-card compact-grid">
        <div className="prop-row"><span>ID</span><code>{elementId}</code></div>
        <div className="prop-row"><span>Type</span><code>{selectedElement.type}</code></div>
      </div>

      <section className="property-card">
        <div className="panel-section-head">
          <div>
            <b>Collibra execution settings</b>
            <small>Stored in exported .app sidecar and used by the AI prompt.</small>
          </div>
        </div>
        <div className="form-grid-two">
          <label>Execution type
            <select value={props.execution || ''} onChange={e => updateProp('execution', e.target.value)}>
              <option value="user-form">User task / form</option>
              <option value="service-groovy">Service Groovy</option>
              <option value="script-groovy">Script Groovy</option>
              <option value="gateway-condition">Gateway / condition</option>
              <option value="notification">Notification</option>
              <option value="container">Pool / lane / subprocess</option>
            </select>
          </label>
          <label>Scope
            <select value={props.scope || ''} onChange={e => updateProp('scope', e.target.value)}>
              <option value="global">Global</option>
              <option value="asset">Asset</option>
              <option value="domain">Domain</option>
              <option value="community">Community</option>
              <option value="responsibility">Responsibility</option>
            </select>
          </label>
          <label>Candidate role UUID/name
            <input value={props.candidateRole || ''} onChange={e => updateProp('candidateRole', e.target.value)} placeholder="Role UUID or name from RAG" />
          </label>
          <label>Form key
            <select value={props.formKey || ''} onChange={e => updateProp('formKey', e.target.value)}>
              <option value="">No linked form</option>
              {Object.keys(allForms).sort().map(key => <option key={key} value={key}>{key}</option>)}
            </select>
          </label>
          {selectedElement.type === 'bpmn:CallActivity' && (
            <label>Called workflow key
              <input value={props.calledElement || ''} onChange={e => updateProp('calledElement', e.target.value)} placeholder="Workflow key or calledElement" />
            </label>
          )}
        </div>
        {selectedElement.type === 'bpmn:CallActivity' && (
          <button className="primary-button" onClick={() => openCalledWorkflowCanvas(props.calledElement || elementId, elementId)}>
            <ExternalLink size={15}/> Open called workflow in new tab
          </button>
        )}
        {linkedForm && <LinkedFormPreview form={linkedForm} />}
        <label>Sequence-flow condition / expression
          <textarea className="condition-box" value={props.condition || ''} onChange={e => updateProp('condition', e.target.value)} placeholder='Example: ${approved == true}' />
        </label>
        <label>Documentation / organization standard
          <textarea className="condition-box" value={props.documentation || ''} onChange={e => updateProp('documentation', e.target.value)} placeholder="Describe standards, variables, SLA, approval rules or validations for this element." />
        </label>
      </section>

      <section className="property-card">
        <div className="panel-section-head">
          <div>
            <b>AI prompt for selected element</b>
            <small>Uses BPMN XML + current app model + indexed RAG context.</small>
          </div>
        </div>
        <textarea className="prompt-box" value={prompt} onChange={e => setPrompt(e.target.value)} />
        <div className="button-row sticky-actions">
          <button onClick={askAi} disabled={busy} className="primary-button"><Bot size={15}/> {busy ? 'Generating...' : 'Ask AI for this block'}</button>
          <button onClick={save}><Save size={15}/> Save</button>
          <button onClick={compile} disabled={busy || !canCompile} className={canCompile ? '' : 'disabled-button'}><Code2 size={15}/> Compile</button>
        </div>
      </section>

      <section className="property-card code-card">
        <div className="panel-section-head">
          <div>
            <b>Groovy script / condition / listener code</b>
            <small>Readable light editor. Saved scripts are exported into the package.</small>
          </div>
          <Sparkles size={16}/>
        </div>
        <textarea
          className="code-box"
          value={groovy}
          onChange={e => setGroovy(e.target.value)}
          placeholder="// Groovy for selected BPMN element will appear here.\n// Click Ask AI for this block, or paste your script and click Compile."
          spellCheck={false}
        />
      </section>
    </div>
  );
}

function LinkedFormPreview({ form }) {
  const fields = Array.isArray(form.fields) ? form.fields : [];
  const outcomes = Array.isArray(form.outcomes) ? form.outcomes : [];
  return (
    <div className="linked-form-preview">
      <div>
        <b>{form.name || form.key}</b>
        <small>{form.key} - {fields.length} fields - {outcomes.length} outcomes</small>
      </div>
      <RenderedForm form={form} />
    </div>
  );
}

function RenderedForm({ form }) {
  const fields = Array.isArray(form.fields) ? form.fields : [];
  const outcomes = Array.isArray(form.outcomes) ? form.outcomes : [];
  if (!fields.length && !outcomes.length) {
    return <small>This form has no fields or outcomes in the imported metadata.</small>;
  }
  return (
    <div className="rendered-form">
      {fields.map(field => (
        <label key={`${form.key}-${field.id}`} className="rendered-field">
          <span>{field.label || field.name || field.id}{field.required ? ' *' : ''}</span>
          {renderInput(field)}
          <small>{field.id} - {field.type}{field.value ? ` - ${field.value}` : ''}</small>
        </label>
      ))}
      {outcomes.length > 0 && (
        <div className="rendered-outcomes">
          {outcomes.map(outcome => (
            <button key={`${form.key}-${outcome.value || outcome.label}`} className={outcome.primary ? 'primary-button' : ''}>
              {outcome.label || outcome.value}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function renderInput(field) {
  const type = String(field.type || '').toLowerCase();
  const values = Array.isArray(field.values) ? field.values : Array.isArray(field.extraSettings?.values) ? field.extraSettings.values : [];
  if (type.includes('richtext') || type.includes('textarea')) {
    return <textarea placeholder={field.value || field.label || field.id} readOnly />;
  }
  if (type.includes('date')) {
    return <input type="date" readOnly />;
  }
  if (type.includes('boolean')) {
    return <input type="checkbox" readOnly />;
  }
  if (type.includes('dropdown') || type.includes('select') || values.length) {
    return (
      <select value="" onChange={() => {}}>
        <option value="">Select...</option>
        {values.map(value => {
          const optionValue = value.value || value.id || value.name || value.label || String(value);
          return <option key={optionValue} value={optionValue}>{value.label || value.name || optionValue}</option>;
        })}
      </select>
    );
  }
  if (type.includes('long') || type.includes('number') || type.includes('integer')) {
    return <input type="number" placeholder={field.value || field.id} readOnly />;
  }
  return <input placeholder={field.value || field.label || field.id} readOnly />;
}

function defaultExecution(type) {
  if (!type) return 'service-groovy';
  if (type.includes('UserTask')) return 'user-form';
  if (type.includes('ServiceTask')) return 'service-groovy';
  if (type.includes('ScriptTask')) return 'script-groovy';
  if (type.includes('Gateway') || type.includes('SequenceFlow')) return 'gateway-condition';
  if (type.includes('SendTask')) return 'notification';
  if (type.includes('Participant') || type.includes('Lane') || type.includes('SubProcess')) return 'container';
  return 'service-groovy';
}

function flowableAttr(element, key) {
  const attrs = element?.businessObject?.$attrs || {};
  return attrs[`flowable:${key}`] || attrs[key] || element?.businessObject?.[key] || '';
}

function applyBpmnProperties(modeler, element, props) {
  if (!modeler || !element) return;
  try {
    const modeling = modeler.get('modeling');
    const moddle = modeler.get('moddle');
    const update = {};
    if (element.type === 'bpmn:CallActivity' && props.calledElement) {
      update.calledElement = props.calledElement;
    }
    if (element.type === 'bpmn:SequenceFlow' && props.condition?.trim()) {
      update.conditionExpression = moddle.create('bpmn:FormalExpression', { body: props.condition.trim() });
    }
    if (Object.keys(update).length) {
      modeling.updateProperties(element, update);
    }
    if (props.formKey && element.businessObject) {
      element.businessObject.$attrs = { ...(element.businessObject.$attrs || {}), 'flowable:formKey': props.formKey };
    }
  } catch {
    // Sidecar metadata is still saved even if bpmn-js cannot apply a vendor extension live.
  }
}

function toElementPayload(element) {
  const bo = element?.businessObject || {};
  return {
    id: element?.id,
    type: element?.type,
    name: bo.name || '',
    documentation: (bo.documentation || []).map(d => d.text).join('\n'),
    incoming: (bo.incoming || []).map(f => ({ id: f.id, name: f.name, sourceRef: f.sourceRef?.id })),
    outgoing: (bo.outgoing || []).map(f => ({ id: f.id, name: f.name, targetRef: f.targetRef?.id }))
  };
}

function openCalledWorkflowCanvas(calledElement, sourceElementId) {
  const key = `called-workflow-${sourceElementId}-${Date.now()}`;
  const safeName = String(calledElement || 'calledWorkflow').replace(/[^\w.-]+/g, '_');
  window.sessionStorage.setItem(key, JSON.stringify({
    bpmnXml: calledWorkflowTemplate(safeName),
    sourceElementId,
    calledElement: safeName
  }));
  const url = new URL(window.location.href);
  url.searchParams.set('calledWorkflowSession', key);
  window.open(url.toString(), '_blank', 'noopener,noreferrer');
}

function calledWorkflowTemplate(name) {
  const processId = `${name || 'calledWorkflow'}Process`.replace(/[^\w]+/g, '_');
  return `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="${processId}_definitions" targetNamespace="http://collibra.com/workflow-agent/called">
  <bpmn:collaboration id="${processId}_collaboration">
    <bpmn:participant id="${processId}_pool" name="${name}" processRef="${processId}" />
  </bpmn:collaboration>
  <bpmn:process id="${processId}" name="${name}" isExecutable="true">
    <bpmn:laneSet id="${processId}_lanes">
      <bpmn:lane id="${processId}_lane_requester" name="Requester"><bpmn:flowNodeRef>${processId}_start</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="${processId}_lane_automation" name="Collibra Automation"><bpmn:flowNodeRef>${processId}_task</bpmn:flowNodeRef><bpmn:flowNodeRef>${processId}_end</bpmn:flowNodeRef></bpmn:lane>
    </bpmn:laneSet>
    <bpmn:startEvent id="${processId}_start" name="Start called workflow" />
    <bpmn:scriptTask id="${processId}_task" name="Called workflow Groovy task" scriptFormat="groovy"><bpmn:script><![CDATA[execution.setVariable("calledWorkflowReached", true)]]></bpmn:script></bpmn:scriptTask>
    <bpmn:endEvent id="${processId}_end" name="Called workflow done" />
    <bpmn:sequenceFlow id="${processId}_flow_1" sourceRef="${processId}_start" targetRef="${processId}_task" />
    <bpmn:sequenceFlow id="${processId}_flow_2" sourceRef="${processId}_task" targetRef="${processId}_end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="${processId}_diagram">
    <bpmndi:BPMNPlane id="${processId}_plane" bpmnElement="${processId}_collaboration">
      <bpmndi:BPMNShape id="${processId}_pool_di" bpmnElement="${processId}_pool" isHorizontal="true"><dc:Bounds x="80" y="60" width="900" height="360" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_lane_requester_di" bpmnElement="${processId}_lane_requester" isHorizontal="true"><dc:Bounds x="110" y="60" width="870" height="160" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_lane_automation_di" bpmnElement="${processId}_lane_automation" isHorizontal="true"><dc:Bounds x="110" y="220" width="870" height="200" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_start_di" bpmnElement="${processId}_start"><dc:Bounds x="190" y="122" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_task_di" bpmnElement="${processId}_task"><dc:Bounds x="340" y="280" width="180" height="82" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_end_di" bpmnElement="${processId}_end"><dc:Bounds x="650" y="303" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="${processId}_flow_1_di" bpmnElement="${processId}_flow_1"><di:waypoint x="226" y="140" /><di:waypoint x="340" y="321" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="${processId}_flow_2_di" bpmnElement="${processId}_flow_2"><di:waypoint x="520" y="321" /><di:waypoint x="650" y="321" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`;
}
