import React, { useEffect, useMemo, useState } from 'react';
import { Bot, CheckCircle2, Code2, Save, Sparkles } from 'lucide-react';
import { compileGroovy, generateCode } from '../api.js';

export default function CollibraPropertiesPanel({ selectedElement, appModel, setAppModel, getBpmnXml, addConsole, forms }) {
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
      condition: elementProps.condition || '',
      documentation: elementProps.documentation || ''
    });
  }, [elementId, elementScript.groovy, elementProps.execution, elementProps.scope, elementProps.candidateRole, elementProps.formKey, elementProps.condition, elementProps.documentation, selectedElement?.type]);

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
      const result = await compileGroovy({ code: groovy, elementId });
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
        </div>
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
      {fields.slice(0, 6).map(field => (
        <div className="mini-field-row" key={`${form.key}-${field.id}`}>
          <code>{field.id}</code>
          <span>{field.label || field.name}</span>
          <small>{field.type}{field.required ? ' required' : ''}</small>
        </div>
      ))}
      {fields.length > 6 && <small>{fields.length - 6} more field(s) in the Forms tab.</small>}
    </div>
  );
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
