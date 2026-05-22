import React, { useEffect, useMemo, useState } from 'react';
import { Bot, CheckCircle2, Code2, ExternalLink, Save, Sparkles } from 'lucide-react';
import { compileGroovy, generateCode } from '../api.js';

export default function CollibraPropertiesPanel({ selectedElement, appModel, setAppModel, getBpmnXml, addConsole, forms, modelId, modeler }) {
  const elementId = selectedElement?.id;
  const elementScript = useMemo(() => appModel?.scripts?.[elementId] || {}, [appModel, elementId]);
  const elementProps = useMemo(() => appModel?.elementProperties?.[elementId] || {}, [appModel, elementId]);
  const allForms = useMemo(() => ({ ...(appModel?.forms || {}), ...(forms || {}) }), [appModel?.forms, forms]);
  const [prompt, setPrompt] = useState('Generate production Collibra Workflow Designer Groovy for this BPMN element. Use Collibra Java API v2 DTO imports only when required, organization identifiers and UUID values from RAG, string2Uuid(...) for UUID conversion, defensive null checks, execution variables, comments, and compile-safe snippet code.');
  const [groovy, setGroovy] = useState('');
  const [props, setProps] = useState({});
  const [busy, setBusy] = useState(false);
  const [compileFeedback, setCompileFeedback] = useState(null);

  useEffect(() => {
    setGroovy(typeof elementScript === 'string' ? elementScript : elementScript.groovy || '');
    setCompileFeedback(null);
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
        compileAndRepair: true,
        forceAi: true
      });
      const code = result.groovy || result.raw || '';
      setGroovy(code);
      setCompileFeedback(result);
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
      const level = result.compileStatus === 'passed' ? 'success' : result.compileStatus === 'failed' ? 'error' : result.compileStatus === 'skipped' ? 'warn' : 'info';
      addConsole?.({ level, message: `AI generated Groovy for ${elementId}`, detail: result });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'AI Groovy generation failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  async function compile() {
    setBusy(true);
    try {
      const result = await compileGroovy({
        code: groovy,
        elementId,
        element: toElementPayload(selectedElement),
        prompt,
        appModel,
        modelId,
        autoRepair: true,
        maxRepairIterations: 4
      });
      const repairedCode = result.repairedCode || result.groovy || '';
      if (result.repaired && repairedCode && repairedCode !== groovy) {
        setGroovy(repairedCode);
        setAppModel(prev => ({
          ...prev,
          scripts: {
            ...(prev.scripts || {}),
            [elementId]: {
              ...(prev.scripts?.[elementId] || {}),
              groovy: repairedCode,
              compileResults: [result],
              repairAttempts: result.repairAttempts || [],
              elementType: selectedElement.type,
              elementName: bo.name || '',
              updatedAt: new Date().toISOString()
            }
          }
        }));
      }
      setCompileFeedback(result);
      const level = result.status === 'passed' ? 'success' : result.status === 'skipped' ? 'warn' : 'error';
      const suffix = result.repaired ? ' after auto-repair' : '';
      addConsole?.({ level, message: `Compile ${result.status || (result.ok ? 'passed' : 'failed')} for ${elementId}${suffix}`, detail: result });
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
          <button className="primary-button" onClick={() => openCalledWorkflowCanvas(props.calledElement || elementId, elementId, bo.name || elementId, `${props.documentation || ''}\n${prompt || ''}`)}>
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
        {compileFeedback && <CompileFeedback result={compileFeedback} />}
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

function CompileFeedback({ result }) {
  const status = result.compileStatus || result.status || (result.ok ? 'passed' : 'failed');
  const attempts = Array.isArray(result.repairAttempts) ? result.repairAttempts : [];
  const errors = result.errorText || result.stderr || '';
  const warnings = Array.isArray(result.warnings) ? result.warnings : [];
  return (
    <div className={`compile-feedback ${status}`}>
      <div>
        <b>Compile {status}</b>
        <small>{result.summaryText || (result.repaired ? 'Auto-repair updated the Groovy and recompiled it.' : 'Compile result is ready.')}</small>
      </div>
      {result.repaired && <span className="compile-chip">auto-repaired</span>}
      {attempts.length > 0 && <span className="compile-chip">{attempts.length} attempt(s)</span>}
      {warnings.length > 0 && <pre>{warnings.join('\n')}</pre>}
      {errors && <pre>{errors}</pre>}
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

function openCalledWorkflowCanvas(calledElement, sourceElementId, sourceName = '', context = '') {
  const key = `called-workflow-${sourceElementId}-${Date.now()}`;
  const profile = calledWorkflowProfile(calledElement, sourceElementId, sourceName, context);
  window.sessionStorage.setItem(key, JSON.stringify({
    bpmnXml: calledWorkflowTemplate(profile),
    sourceElementId,
    calledElement: profile.key,
    calledWorkflowProfile: profile
  }));
  const url = new URL(window.location.href);
  url.searchParams.set('calledWorkflowSession', key);
  window.open(url.toString(), '_blank', 'noopener,noreferrer');
}

function calledWorkflowProfile(calledElement, sourceElementId, sourceName = '', context = '') {
  const text = `${calledElement || ''} ${sourceElementId || ''} ${sourceName || ''} ${context || ''}`.toLowerCase();
  const key = safeBpmnId(String(calledElement || sourceElementId || 'calledWorkflow').replace(/\$\{|\}/g, ''));
  const profiles = [
    {
      tokens: ['privacy', 'pii', 'personal data', 'gdpr', 'data protection'],
      label: 'Privacy Assessment',
      lane: 'Privacy Automation',
      receive: 'Receive privacy assessment request',
      execute: 'Assess privacy controls',
      returnTask: 'Return privacy assessment result',
      statusValue: 'privacy_assessed'
    },
    {
      tokens: ['obsolete', 'deletion', 'delete', 'retire', 'archive'],
      label: 'Asset Obsolescence',
      lane: 'Deletion Automation',
      receive: 'Receive obsolescence request',
      execute: 'Validate deletion dependencies',
      returnTask: 'Return deletion readiness result',
      statusValue: 'deletion_ready'
    },
    {
      tokens: ['quality', 'data quality', 'dq', 'certification', 'certify'],
      label: 'Data Quality Certification',
      lane: 'Quality Automation',
      receive: 'Receive certification request',
      execute: 'Run quality certification checks',
      returnTask: 'Return certification result',
      statusValue: 'quality_certified'
    },
    {
      tokens: ['relation', 'responsibility', 'ownership', 'stewardship', 'assignment'],
      label: 'Stewardship Assignment',
      lane: 'Stewardship Automation',
      receive: 'Receive stewardship request',
      execute: 'Create relation and responsibility',
      returnTask: 'Return stewardship assignment result',
      statusValue: 'stewardship_assigned'
    },
    {
      tokens: ['risk', 'security', 'exception', 'control', 'compliance'],
      label: 'Risk Control',
      lane: 'Risk Automation',
      receive: 'Receive risk control request',
      execute: 'Validate risk controls',
      returnTask: 'Return risk decision result',
      statusValue: 'risk_control_approved'
    },
    {
      tokens: ['provision', 'access', 'entitlement', 'permission'],
      label: 'Access Provisioning',
      lane: 'Provisioning Automation',
      receive: 'Receive provisioning request',
      execute: 'Execute governed provisioning',
      returnTask: 'Return provisioning result',
      statusValue: 'provisioned'
    }
  ];
  const selected = profiles.find(profile => profile.tokens.some(token => text.includes(token))) || profiles[profiles.length - 1];
  return {
    ...selected,
    key,
    name: `${selected.label} - ${key}`,
    sourceElementId: sourceElementId || '',
    sourceName: sourceName || ''
  };
}

function calledWorkflowTemplate(profile) {
  const processId = safeBpmnId(`${profile.key || 'calledWorkflow'}Process`);
  const script = calledWorkflowGroovy(profile);
  return `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="${processId}_definitions" targetNamespace="http://collibra.com/workflow-agent/called">
  <bpmn:collaboration id="${processId}_collaboration">
    <bpmn:participant id="${processId}_pool" name="${xmlAttr(profile.name)}" processRef="${processId}" />
  </bpmn:collaboration>
  <bpmn:process id="${processId}" name="${xmlAttr(profile.name)}" isExecutable="true">
    <bpmn:laneSet id="${processId}_lanes">
      <bpmn:lane id="${processId}_lane_parent" name="Calling Workflow"><bpmn:flowNodeRef>${processId}_start</bpmn:flowNodeRef><bpmn:flowNodeRef>${processId}_receive</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="${processId}_lane_automation" name="${xmlAttr(profile.lane)}"><bpmn:flowNodeRef>${processId}_execute</bpmn:flowNodeRef><bpmn:flowNodeRef>${processId}_return</bpmn:flowNodeRef><bpmn:flowNodeRef>${processId}_end</bpmn:flowNodeRef></bpmn:lane>
    </bpmn:laneSet>
    <bpmn:startEvent id="${processId}_start" name="Start ${xmlAttr(profile.label)}" />
    <bpmn:userTask id="${processId}_receive" name="${xmlAttr(profile.receive)}" />
    <bpmn:scriptTask id="${processId}_execute" name="${xmlAttr(profile.execute)}" scriptFormat="groovy"><bpmn:script><![CDATA[${cdata(script)}]]></bpmn:script></bpmn:scriptTask>
    <bpmn:scriptTask id="${processId}_return" name="${xmlAttr(profile.returnTask)}" scriptFormat="groovy"><bpmn:script><![CDATA[execution.setVariable("provisioningStatus", "success")
execution.setVariable("calledWorkflowStatus", "${cdata(profile.statusValue)}")
execution.setVariable("calledWorkflowKey", "${cdata(profile.key)}")]]></bpmn:script></bpmn:scriptTask>
    <bpmn:endEvent id="${processId}_end" name="${xmlAttr(profile.label)} complete" />
    <bpmn:sequenceFlow id="${processId}_flow_1" sourceRef="${processId}_start" targetRef="${processId}_receive" />
    <bpmn:sequenceFlow id="${processId}_flow_2" sourceRef="${processId}_receive" targetRef="${processId}_execute" />
    <bpmn:sequenceFlow id="${processId}_flow_3" sourceRef="${processId}_execute" targetRef="${processId}_return" />
    <bpmn:sequenceFlow id="${processId}_flow_4" sourceRef="${processId}_return" targetRef="${processId}_end" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="${processId}_diagram">
    <bpmndi:BPMNPlane id="${processId}_plane" bpmnElement="${processId}_collaboration">
      <bpmndi:BPMNShape id="${processId}_pool_di" bpmnElement="${processId}_pool" isHorizontal="true"><dc:Bounds x="80" y="60" width="1120" height="420" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_lane_parent_di" bpmnElement="${processId}_lane_parent" isHorizontal="true"><dc:Bounds x="110" y="60" width="1090" height="180" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_lane_automation_di" bpmnElement="${processId}_lane_automation" isHorizontal="true"><dc:Bounds x="110" y="240" width="1090" height="240" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_start_di" bpmnElement="${processId}_start"><dc:Bounds x="190" y="132" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_receive_di" bpmnElement="${processId}_receive"><dc:Bounds x="300" y="110" width="180" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_execute_di" bpmnElement="${processId}_execute"><dc:Bounds x="560" y="312" width="210" height="86" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_return_di" bpmnElement="${processId}_return"><dc:Bounds x="840" y="312" width="210" height="86" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="${processId}_end_di" bpmnElement="${processId}_end"><dc:Bounds x="1110" y="337" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="${processId}_flow_1_di" bpmnElement="${processId}_flow_1"><di:waypoint x="226" y="150" /><di:waypoint x="300" y="150" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="${processId}_flow_2_di" bpmnElement="${processId}_flow_2"><di:waypoint x="480" y="150" /><di:waypoint x="560" y="355" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="${processId}_flow_3_di" bpmnElement="${processId}_flow_3"><di:waypoint x="770" y="355" /><di:waypoint x="840" y="355" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="${processId}_flow_4_di" bpmnElement="${processId}_flow_4"><di:waypoint x="1050" y="355" /><di:waypoint x="1110" y="355" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`;
}

function calledWorkflowGroovy(profile) {
  return `String requestId = (execution.getVariable("requestId") ?: java.util.UUID.randomUUID().toString()) as String
execution.setVariable("requestId", requestId)
execution.setVariable("calledWorkflowKey", "${cdata(profile.key)}")
execution.setVariable("calledWorkflowName", "${cdata(profile.name)}")
execution.setVariable("calledWorkflowSourceElementId", "${cdata(profile.sourceElementId)}")
execution.setVariable("calledWorkflowSourceName", "${cdata(profile.sourceName)}")
execution.setVariable("calledWorkflowStatus", "${cdata(profile.statusValue)}")
execution.setVariable("provisioningStatus", "success")`;
}

function safeBpmnId(value) {
  let cleaned = String(value || 'calledWorkflow').replace(/[^A-Za-z0-9_]+/g, '_').replace(/^_+|_+$/g, '');
  if (!cleaned) cleaned = 'calledWorkflow';
  if (/^[0-9]/.test(cleaned)) cleaned = `id_${cleaned}`;
  return cleaned;
}

function xmlAttr(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function cdata(value) {
  return String(value || '').replaceAll(']]>', ']]]]><![CDATA[>');
}
