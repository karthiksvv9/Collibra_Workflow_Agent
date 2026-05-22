import React, { useEffect, useRef, useState } from 'react';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import { Bot, Code2, Database, Download, EyeOff, FileText, Maximize, Play, RefreshCw, Rocket, Search, ShieldCheck, Terminal, Wrench } from 'lucide-react';
import { autocorrectWorkflow, compileGroovy, exportWorkflow, getModelProfiles, selectModelProfile, simulateWorkflow, testWorkflowPackage } from '../api.js';
import { syncAllLaneMembership, syncLaneMembership } from '../bpmnLaneSync.js';
import BlockLibrary from './BlockLibrary.jsx';
import PackageImporter from './PackageImporter.jsx';
import RightDock from './RightDock.jsx';
import AutonomousAgentModal from './AutonomousAgentModal.jsx';

const STARTER_BPMN = `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://collibra.com/workflow-agent">
  <bpmn:collaboration id="Collaboration_1">
    <bpmn:participant id="Participant_Collibra" name="Collibra Governance Workflow" processRef="Process_1" />
  </bpmn:collaboration>
  <bpmn:process id="Process_1" name="New Collibra Workflow" isExecutable="true">
    <bpmn:laneSet id="LaneSet_1">
      <bpmn:lane id="Lane_Requester" name="Requester"><bpmn:flowNodeRef>StartEvent_1</bpmn:flowNodeRef><bpmn:flowNodeRef>UserTask_RequestForm</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="Lane_Steward" name="Data Steward"><bpmn:flowNodeRef>UserTask_Review</bpmn:flowNodeRef><bpmn:flowNodeRef>Gateway_Approved</bpmn:flowNodeRef><bpmn:flowNodeRef>EndEvent_Rejected</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="Lane_System" name="Collibra Automation"><bpmn:flowNodeRef>ServiceTask_UpdateAsset</bpmn:flowNodeRef><bpmn:flowNodeRef>SendTask_Notify</bpmn:flowNodeRef><bpmn:flowNodeRef>EndEvent_1</bpmn:flowNodeRef></bpmn:lane>
    </bpmn:laneSet>
    <bpmn:startEvent id="StartEvent_1" name="Start"><bpmn:outgoing>Flow_1</bpmn:outgoing></bpmn:startEvent>
    <bpmn:userTask id="UserTask_RequestForm" name="Requester Form"><bpmn:incoming>Flow_1</bpmn:incoming><bpmn:outgoing>Flow_2</bpmn:outgoing></bpmn:userTask>
    <bpmn:userTask id="UserTask_Review" name="Steward Review"><bpmn:incoming>Flow_2</bpmn:incoming><bpmn:outgoing>Flow_3</bpmn:outgoing></bpmn:userTask>
    <bpmn:exclusiveGateway id="Gateway_Approved" name="Approved?"><bpmn:incoming>Flow_3</bpmn:incoming><bpmn:outgoing>Flow_4</bpmn:outgoing><bpmn:outgoing>Flow_Reject</bpmn:outgoing></bpmn:exclusiveGateway>
    <bpmn:serviceTask id="ServiceTask_UpdateAsset" name="Update Collibra Asset"><bpmn:incoming>Flow_4</bpmn:incoming><bpmn:outgoing>Flow_5</bpmn:outgoing></bpmn:serviceTask>
    <bpmn:sendTask id="SendTask_Notify" name="Notify Requester"><bpmn:incoming>Flow_5</bpmn:incoming><bpmn:outgoing>Flow_6</bpmn:outgoing></bpmn:sendTask>
    <bpmn:endEvent id="EndEvent_1" name="Done"><bpmn:incoming>Flow_6</bpmn:incoming></bpmn:endEvent>
    <bpmn:endEvent id="EndEvent_Rejected" name="Rejected"><bpmn:incoming>Flow_Reject</bpmn:incoming></bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="UserTask_RequestForm" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="UserTask_RequestForm" targetRef="UserTask_Review" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="UserTask_Review" targetRef="Gateway_Approved" />
    <bpmn:sequenceFlow id="Flow_4" name="Approved" sourceRef="Gateway_Approved" targetRef="ServiceTask_UpdateAsset" />
    <bpmn:sequenceFlow id="Flow_Reject" name="Rejected" sourceRef="Gateway_Approved" targetRef="EndEvent_Rejected" />
    <bpmn:sequenceFlow id="Flow_5" sourceRef="ServiceTask_UpdateAsset" targetRef="SendTask_Notify" />
    <bpmn:sequenceFlow id="Flow_6" sourceRef="SendTask_Notify" targetRef="EndEvent_1" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_1">
      <bpmndi:BPMNShape id="Participant_Collibra_di" bpmnElement="Participant_Collibra" isHorizontal="true"><dc:Bounds x="90" y="60" width="1220" height="520" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Lane_Requester_di" bpmnElement="Lane_Requester" isHorizontal="true"><dc:Bounds x="120" y="60" width="1190" height="150" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Lane_Steward_di" bpmnElement="Lane_Steward" isHorizontal="true"><dc:Bounds x="120" y="210" width="1190" height="170" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Lane_System_di" bpmnElement="Lane_System" isHorizontal="true"><dc:Bounds x="120" y="380" width="1190" height="200" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1"><dc:Bounds x="190" y="117" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="UserTask_RequestForm_di" bpmnElement="UserTask_RequestForm"><dc:Bounds x="300" y="95" width="150" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="UserTask_Review_di" bpmnElement="UserTask_Review"><dc:Bounds x="300" y="255" width="150" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_Approved_di" bpmnElement="Gateway_Approved" isMarkerVisible="true"><dc:Bounds x="560" y="270" width="50" height="50" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="ServiceTask_UpdateAsset_di" bpmnElement="ServiceTask_UpdateAsset"><dc:Bounds x="740" y="440" width="180" height="82" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="SendTask_Notify_di" bpmnElement="SendTask_Notify"><dc:Bounds x="990" y="440" width="150" height="82" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1"><dc:Bounds x="1230" y="463" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_Rejected_di" bpmnElement="EndEvent_Rejected"><dc:Bounds x="760" y="277" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1"><di:waypoint x="226" y="135" /><di:waypoint x="300" y="135" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2"><di:waypoint x="375" y="175" /><di:waypoint x="375" y="255" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3"><di:waypoint x="450" y="295" /><di:waypoint x="560" y="295" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4"><di:waypoint x="585" y="320" /><di:waypoint x="585" y="481" /><di:waypoint x="740" y="481" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_Reject_di" bpmnElement="Flow_Reject"><di:waypoint x="610" y="295" /><di:waypoint x="760" y="295" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_5_di" bpmnElement="Flow_5"><di:waypoint x="920" y="481" /><di:waypoint x="990" y="481" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_6_di" bpmnElement="Flow_6"><di:waypoint x="1140" y="481" /><di:waypoint x="1230" y="481" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`;

export default function BpmnAgentCanvas({ appModel, setAppModel, forms, setForms }) {
  const canvasRef = useRef(null);
  const modelerRef = useRef(null);
  const overlayIdsRef = useRef(new Map());
  const modelToastTimerRef = useRef(null);
  const [modelerReady, setModelerReady] = useState(false);
  const [selectedElement, setSelectedElement] = useState(null);
  const [consoleEntries, setConsoleEntries] = useState([]);
  const [packageName, setPackageName] = useState('generated-collibra-workflow.zip');
  const [importSummary, setImportSummary] = useState('Ready');
  const [rightTab, setRightTab] = useState('properties');
  const [hideHandles, setHideHandles] = useState(true);
  const [autonomousOpen, setAutonomousOpen] = useState(false);
  const [models, setModels] = useState([]);
  const [activeModelId, setActiveModelId] = useState('');
  const [modelNotice, setModelNotice] = useState(null);
  const [connectionSource, setConnectionSource] = useState(null);

  useEffect(() => {
    const modeler = new BpmnModeler({
      container: canvasRef.current,
      keyboard: { bindTo: document },
      moveCanvas: { enabled: true }
    });
    modelerRef.current = modeler;
    modeler.importXML(STARTER_BPMN)
      .then(async ({ warnings }) => {
        await loadCalledWorkflowFromSession(modeler);
        syncAllLaneMembership(modeler);
        modeler.get('canvas').zoom('fit-viewport');
        setModelerReady(true);
        addConsole({ level: warnings?.length ? 'warn' : 'success', message: 'bpmn-js canvas initialized', detail: warnings?.length ? warnings : 'Starter Collibra workflow loaded.' });
      })
      .catch(err => addConsole({ level: 'error', message: 'Starter BPMN failed', detail: err.message }));
    const eventBus = modeler.get('eventBus');
    eventBus.on('selection.changed', e => {
      setSelectedElement(e.newSelection?.[0] || null);
      if (e.newSelection?.[0]) setRightTab('properties');
    });
    eventBus.on('shape.move.end', e => syncLaneMembership(modeler, e.shape));
    eventBus.on('shape.create.end', e => syncLaneMembership(modeler, e.shape));
    eventBus.on('commandStack.connection.create.executed', e => applySequenceFlowType(modeler, e.context?.connection));
    eventBus.on('element.click', e => connectArmedElement(modeler, e.element));
    eventBus.on('commandStack.changed', () => refreshScriptBadges());
    return () => {
      if (modelToastTimerRef.current) window.clearTimeout(modelToastTimerRef.current);
      modeler.destroy();
    };
  }, []);

  useEffect(() => {
    getModelProfiles()
      .then(result => {
        setModels(result.models || []);
        setActiveModelId(result.activeModelId || result.models?.[0]?.id || '');
      })
      .catch(err => addConsole({ level: 'warn', message: 'Model profiles could not be loaded', detail: err.message }));
  }, []);

  useEffect(() => {
    refreshScriptBadges();
  }, [appModel?.scripts, modelerReady]);

  function addConsole(entry) {
    setConsoleEntries(prev => [...prev.slice(-120), { ...entry, at: new Date().toLocaleTimeString() }]);
  }

  function clearConsole() {
    setConsoleEntries([]);
  }

  function showModelNotice(level, message) {
    if (modelToastTimerRef.current) window.clearTimeout(modelToastTimerRef.current);
    setModelNotice({ level, message });
    modelToastTimerRef.current = window.setTimeout(() => setModelNotice(null), 4200);
  }

  function refreshScriptBadges() {
    const modeler = modelerRef.current;
    if (!modelerReady || !modeler) return;
    try {
      const overlays = modeler.get('overlays');
      overlayIdsRef.current.forEach(id => overlays.remove(id));
      overlayIdsRef.current.clear();
      Object.keys(appModel?.scripts || {}).forEach(elementId => {
        const overlayId = overlays.add(elementId, 'script-badge', {
          position: { top: -8, right: -8 },
          html: '<div class="script-badge">AI</div>'
        });
        overlayIdsRef.current.set(elementId, overlayId);
      });
    } catch {
      // Element may not be visible after an import. Safe to ignore and refresh later.
    }
  }

  async function importBpmnXml(xml, sourceName = 'imported BPMN') {
    const clean = sanitizeBpmnXml(xml);
    if (!clean || !looksLikeBpmn(clean)) {
      throw new Error('No BPMN definitions were found. The file may be a form/app XML rather than a BPMN definition. Upload the whole ZIP or a real .bpmn/.bpmn20.xml file.');
    }
    try {
      const result = await modelerRef.current.importXML(clean);
      syncAllLaneMembership(modelerRef.current);
      modelerRef.current.get('canvas').zoom('fit-viewport');
      setSelectedElement(null);
      setImportSummary(`Loaded ${sourceName}`);
      addConsole({ level: result?.warnings?.length ? 'warn' : 'success', message: 'BPMN loaded into canvas', detail: { sourceName, bytes: clean.length, warnings: result?.warnings || [] } });
    } catch (err) {
      const warningText = (err.warnings || []).map(w => w.message || String(w)).join('\n');
      addConsole({ level: 'error', message: 'bpmn-js parse/import failed', detail: { error: err.message, warnings: warningText } });
      throw err;
    }
  }

  async function getBpmnXml() {
    const { xml } = await modelerRef.current.saveXML({ format: true });
    return xml;
  }

  async function onImported(result) {
    try {
      if (result.bpmnXml) await importBpmnXml(result.bpmnXml, result.chosenBpmn || result.appModel?.metadata?.bpmnSource || 'package BPMN');
      if (result.appModel) {
        setAppModel(prev => deepMerge(prev, {
          ...result.appModel,
          scripts: { ...(prev.scripts || {}), ...(result.appModel.scripts || {}) },
          forms: { ...(prev.forms || {}), ...(result.forms || {}), ...(result.appModel.forms || {}) },
          elementProperties: { ...(prev.elementProperties || {}), ...(result.appModel.elementProperties || {}) }
        }));
      }
      if (result.forms) setForms(prev => ({ ...prev, ...result.forms }));
      const msg = `Members: ${(result.members || []).length}. ${result.chosenBpmn ? `BPMN: ${result.chosenBpmn}. ` : ''}${result.warnings?.length ? `Warnings: ${result.warnings.join('; ')}` : ''}`;
      setImportSummary(msg);
      addConsole({ level: result.warnings?.length ? 'warn' : 'info', message: 'Package imported', detail: result });
    } catch (err) {
      setImportSummary(`Import read package but could not render BPMN: ${err.message}`);
      addConsole({ level: 'error', message: 'Import finished but BPMN could not render', detail: err.message });
    }
  }

  async function doExport() {
    try {
      const bpmnXml = await getBpmnXml();
      const exportName = withTimestampName(packageName?.trim() || 'generated-collibra-workflow.zip');
      await exportWorkflow({ bpmnXml, appModel, forms, packageName: exportName, withTimestamp: true, modelId: activeModelId });
      setPackageName(exportName);
      addConsole({ level: 'success', message: 'Package exported', detail: exportName });
      setRightTab('console');
    } catch (err) {
      addConsole({ level: 'error', message: 'Export failed', detail: err.message });
      setRightTab('console');
    }
  }

  async function simulate() {
    try {
      const bpmnXml = await getBpmnXml();
      const result = await simulateWorkflow({ bpmnXml, appModel, formValues: {}, modelId: activeModelId });
      addConsole({ level: result.status === 'failed' ? 'error' : 'info', message: result.summaryText || 'Simulation completed', detail: result });
      setRightTab('console');
    } catch (err) {
      addConsole({ level: 'error', message: 'Simulation failed', detail: err.message });
      setRightTab('console');
    }
  }

  async function testPackage() {
    try {
      const bpmnXml = await getBpmnXml();
      const result = await testWorkflowPackage({ bpmnXml, appModel, forms, maxIterations: 3, modelId: activeModelId });
      if (result.repairedAppModel) {
        setAppModel(prev => deepMerge(prev, result.repairedAppModel));
      }
      addConsole({
        level: result.ok ? 'success' : 'error',
        message: result.summaryText || `Autonomous package test ${result.status || (result.ok ? 'passed' : 'failed')}`,
        detail: result
      });
      setRightTab('console');
    } catch (err) {
      addConsole({ level: 'error', message: 'Autonomous package test failed', detail: err.message });
      setRightTab('console');
    }
  }

  async function autocorrectAll() {
    try {
      const bpmnXml = await getBpmnXml();
      const exportName = withTimestampName(packageName?.trim() || 'autocorrected-collibra-workflow.zip');
      setRightTab('console');
      addConsole({
        level: 'info',
        message: 'Autocorrect started',
        detail: 'Checking BPMN structure, sequence-flow Groovy, script-task Groovy, forms, package export, and business-test readiness.'
      });
      const autocorrectPrompt = appModel?.metadata?.businessUseCase || appModel?.metadata?.prompt || importSummary || 'Autocorrect the current Collibra workflow and resolve all production-readiness issues.';
      const result = await autocorrectWorkflow({
        bpmnXml,
        appModel,
        forms,
        prompt: autocorrectPrompt,
        packageName: exportName,
        maxIterations: 6,
        modelId: activeModelId
      });
      if (result.bpmnXml) {
        await importBpmnXml(result.bpmnXml, 'autocorrected workflow');
      }
      if (result.appModel) {
        setAppModel(prev => deepMerge(prev, {
          ...result.appModel,
          scripts: { ...(prev.scripts || {}), ...(result.appModel.scripts || {}) },
          forms: { ...(prev.forms || {}), ...(result.forms || {}), ...(result.appModel.forms || {}) },
          elementProperties: { ...(prev.elementProperties || {}), ...(result.appModel.elementProperties || {}) }
        }));
      }
      if (result.forms) setForms(prev => ({ ...prev, ...result.forms }));
      if (result.zipPath) setPackageName(result.zipPath.split(/[\\/]/).pop() || exportName);
      addConsole({
        level: result.ok ? 'success' : 'error',
        message: result.summaryText || `Autocorrect ${result.status || (result.ok ? 'passed' : 'failed')}`,
        detail: result
      });
    } catch (err) {
      addConsole({ level: 'error', message: 'Autocorrect failed', detail: err.message });
      setRightTab('console');
    }
  }

  async function compileSelected() {
    if (!selectedElement) {
      addConsole({ level: 'warn', message: 'Compile skipped', detail: 'Select a BPMN element first.' });
      setRightTab('console');
      return;
    }
    const groovy = appModel?.scripts?.[selectedElement.id]?.groovy || '';
    if (!groovy.trim()) {
      addConsole({ level: 'warn', message: 'No Groovy found for selected element', detail: 'Open Properties and click Ask AI for this block or paste Groovy code first.' });
      setRightTab('properties');
      return;
    }
    try {
      const result = await compileGroovy({
        code: groovy,
        elementId: selectedElement.id,
        element: {
          id: selectedElement.id,
          type: selectedElement.type,
          name: selectedElement.businessObject?.name || selectedElement.id
        },
        prompt: `Compile and repair Groovy for ${selectedElement.businessObject?.name || selectedElement.id} using organization RAG standards and previous workflow code.`,
        appModel,
        modelId: activeModelId,
        autoRepair: true,
        maxRepairIterations: 4
      });
      if (result.repaired && result.repairedCode) {
        setAppModel(prev => ({
          ...prev,
          scripts: {
            ...(prev.scripts || {}),
            [selectedElement.id]: {
              ...(prev.scripts?.[selectedElement.id] || {}),
              groovy: result.repairedCode,
              compileResults: [result],
              repairAttempts: result.repairAttempts || [],
              updatedAt: new Date().toISOString()
            }
          }
        }));
      }
      const level = result.status === 'passed' ? 'success' : result.status === 'skipped' ? 'warn' : 'error';
      addConsole({ level, message: `Compile ${result.status || (result.ok ? 'passed' : 'failed')} for ${selectedElement.id}${result.repaired ? ' after auto-repair' : ''}`, detail: result });
      setRightTab('console');
    } catch (err) {
      addConsole({ level: 'error', message: 'Compile failed', detail: err.message });
      setRightTab('console');
    }
  }

  async function onAutonomousResult(result) {
    if (result.bpmnXml) {
      await importBpmnXml(result.bpmnXml, 'autonomous agent output');
    }
    if (result.appModel) {
      setAppModel(prev => deepMerge(prev, {
        ...result.appModel,
        scripts: { ...(prev.scripts || {}), ...(result.appModel.scripts || {}) },
        forms: { ...(prev.forms || {}), ...(result.forms || {}), ...(result.appModel.forms || {}) },
        elementProperties: { ...(prev.elementProperties || {}), ...(result.appModel.elementProperties || {}) }
      }));
    }
    if (result.forms) setForms(prev => ({ ...prev, ...result.forms }));
    if (result.zipPath) setPackageName(result.zipPath.split(/[\\/]/).pop() || packageName);
    setImportSummary(`Autonomous Agent Mode ${result.status}. ZIP: ${result.zipPath || 'not exported'}`);
    setRightTab('console');
  }

  async function reloadStarter() {
    await importBpmnXml(STARTER_BPMN, 'starter workflow');
  }

  function fitCanvas() {
    modelerRef.current?.get('canvas')?.zoom('fit-viewport');
  }

  async function changeModel(event) {
    const modelId = event.target.value;
    const previousModelId = activeModelId;
    setActiveModelId(modelId);
    try {
      const result = await selectModelProfile(modelId);
      setActiveModelId(result.activeModelId || modelId);
      addConsole({ level: 'info', message: `AI model selected: ${result.model}`, detail: result });
      const label = models.find(model => model.id === modelId)?.label || result.model || modelId;
      showModelNotice('success', `Model selected: ${label}. All AI actions will use this profile.`);
    } catch (err) {
      setActiveModelId(previousModelId);
      addConsole({ level: 'error', message: 'AI model selection failed', detail: err.message });
      showModelNotice('error', `Model selection failed: ${err.message}`);
    }
  }

  function armConnection(source, flowType) {
    if (!modelerRef.current || !source) return;
    modelerRef.current.__dscConnectionSource = source;
    modelerRef.current.__dscNextSequenceFlowType = flowType || 'normal';
    setConnectionSource({ id: source.id, flowType: flowType || 'normal' });
    setImportSummary(`Connection armed from ${source.id}. Click the target BPMN block.`);
  }

  function connectArmedElement(modeler, target) {
    const source = modeler?.__dscConnectionSource;
    if (!source || !target || source.id === target.id || !isConnectableFlowNode(source) || !isConnectableFlowNode(target)) return;
    try {
      const connection = modeler.get('modeling').connect(source, target);
      applySequenceFlowType(modeler, connection);
      modeler.__dscConnectionSource = null;
      setConnectionSource(null);
      setSelectedElement(connection || target);
      addConsole({
        level: 'info',
        message: 'Sequence flow connected',
        detail: { source: source.id, target: target.id, flowType: modeler.__dscNextSequenceFlowType || 'normal' }
      });
    } catch (err) {
      addConsole({ level: 'error', message: 'Sequence flow connection failed', detail: err.message });
    }
  }

  return (
    <div className={`agent-workbench ${hideHandles ? 'hide-edit-handles' : ''}`}>
      <header className="topbar">
        <div className="brand-block">
          <strong>DSC Collibra Workflow Agent</strong>
          <small>Production BPMN designer + RAG training + Groovy generation + compile/export</small>
        </div>
        <div className="top-actions">
          <select className="model-select" value={activeModelId} onChange={changeModel} aria-label="AI model">
            {models.length === 0 && <option value="">Loading models...</option>}
            {models.map(model => <option key={model.id} value={model.id}>{model.label || model.id}</option>)}
          </select>
          <button onClick={() => setRightTab('rag')} className="accent-button"><Database size={16}/> RAG / Train</button>
          <button onClick={() => setRightTab('agent')}><Bot size={16}/> Generate BPMN</button>
          <button onClick={() => setAutonomousOpen(true)} className="accent-button"><Rocket size={16}/> Autonomous Agent Mode</button>
          <button onClick={compileSelected}><Code2 size={16}/> Compile selected</button>
          <button onClick={simulate}><Play size={16}/> Run simulation</button>
          <button onClick={testPackage}><ShieldCheck size={16}/> Test all</button>
          <button onClick={autocorrectAll} className="accent-button"><Wrench size={16}/> Autocorrect</button>
          <button onClick={() => setRightTab('docs')}><FileText size={16}/> Docs</button>
          <button onClick={doExport} className="primary-button"><Download size={16}/> Export ZIP</button>
        </div>
      </header>
      {modelNotice && <div className={`model-toast ${modelNotice.level}`}>{modelNotice.message}</div>}

      <aside className="toolbox">
        <div className="toolbox-head">
          <strong>Workflow Toolbox</strong>
          <span><ShieldCheck size={13}/> bpmn-js + Collibra</span>
        </div>
        <div className="quick-toolbar">
          <button onClick={fitCanvas}><Maximize size={14}/> Fit</button>
          <button onClick={reloadStarter}><RefreshCw size={14}/> Reset</button>
          <button onClick={() => setHideHandles(v => !v)}><EyeOff size={14}/> {hideHandles ? 'Handles off' : 'Handles on'}</button>
          <button onClick={() => setRightTab('console')}><Terminal size={14}/> Logs</button>
          <button onClick={() => setRightTab('rag')}><Search size={14}/> RAG</button>
        </div>
        <PackageImporter onImported={onImported} />
        <small className="import-summary">{importSummary}</small>
        <BlockLibrary
          modeler={modelerReady ? modelerRef.current : null}
          selectedElement={selectedElement}
          addConsole={addConsole}
          onConnectionArmed={armConnection}
        />
      </aside>

      <main className="canvas-wrap">
        <div className="canvas-toolbar">
          <span>{connectionSource ? `Connection armed from ${connectionSource.id}; click target block (${connectionSource.flowType}).` : selectedElement ? `Selected: ${selectedElement.id} - ${selectedElement.type}` : 'Select a BPMN element to edit Collibra properties and Groovy.'}</span>
          <span>Native bpmn-js canvas enabled: zoom, pan, connect, append, lanes, pools, import/export.</span>
        </div>
        <div className="canvas" ref={canvasRef} />
      </main>

      <RightDock
        activeTab={rightTab}
        setActiveTab={setRightTab}
        selectedElement={selectedElement}
        appModel={appModel}
        setAppModel={setAppModel}
        getBpmnXml={getBpmnXml}
        importBpmnXml={importBpmnXml}
        addConsole={addConsole}
        consoleEntries={consoleEntries}
        clearConsole={clearConsole}
        forms={forms}
        modelId={activeModelId}
        modeler={modelerReady ? modelerRef.current : null}
      />
      <AutonomousAgentModal
        open={autonomousOpen}
        onClose={() => setAutonomousOpen(false)}
        getBpmnXml={getBpmnXml}
        appModel={appModel}
        forms={forms}
        onResult={onAutonomousResult}
        addConsole={addConsole}
        modelId={activeModelId}
      />
      <footer className="app-footer">karthik.v</footer>
    </div>
  );
}

function looksLikeBpmn(xml) {
  const low = String(xml || '').slice(0, 16000).toLowerCase();
  return low.includes('<bpmn:definitions') || (low.includes('<definitions') && (low.includes('bpmn') || low.includes('www.omg.org/spec/bpmn')));
}

function sanitizeBpmnXml(xml) {
  if (!xml || typeof xml !== 'string') return '';
  let clean = xml.replace(/^\uFEFF/, '').trim();
  const xmlStart = clean.indexOf('<?xml');
  const bpmnStart = clean.indexOf('<bpmn:definitions');
  const defsStart = clean.indexOf('<definitions');
  const starts = [xmlStart, bpmnStart, defsStart].filter(v => v >= 0).sort((a, b) => a - b);
  if (starts.length && starts[0] > 0) clean = clean.slice(starts[0]);
  return clean;
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

function timestampSuffix() {
  const value = new Date();
  const pad = number => String(number).padStart(2, '0');
  return `${value.getFullYear()}${pad(value.getMonth() + 1)}${pad(value.getDate())}_${pad(value.getHours())}${pad(value.getMinutes())}${pad(value.getSeconds())}`;
}

function withTimestampName(name) {
  const fallback = 'generated-collibra-workflow.zip';
  const rawName = String(name || fallback).trim() || fallback;
  const stem = rawName
    .replace(/\.zip$/i, '')
    .replace(/_with_timestamp_\d{8}_\d{6}.*$/i, '')
    .replace(/_\d{8}_\d{6}.*$/i, '');
  const suffix = `_${timestampSuffix()}`;
  return `${compactNamePart(stem || 'workflow', 62 - suffix.length)}${suffix}.zip`;
}

function compactNamePart(value, maxLength = 36) {
  const safe = String(value || 'workflow').replace(/[^A-Za-z0-9._-]+/g, '_').replace(/^_+|_+$/g, '') || 'workflow';
  if (safe.length <= maxLength) return safe;
  let hash = 0;
  for (let index = 0; index < safe.length; index += 1) {
    hash = ((hash << 5) - hash + safe.charCodeAt(index)) | 0;
  }
  const digest = Math.abs(hash).toString(16).slice(0, 6).padStart(6, '0');
  return `${safe.slice(0, Math.max(8, maxLength - 7)).replace(/[._-]+$/g, '')}_${digest}`;
}

function isConnectableFlowNode(element) {
  return element?.businessObject?.$instanceOf?.('bpmn:FlowNode') || [
    'bpmn:Task', 'bpmn:UserTask', 'bpmn:ServiceTask', 'bpmn:ScriptTask', 'bpmn:BusinessRuleTask',
    'bpmn:SendTask', 'bpmn:ReceiveTask', 'bpmn:ManualTask', 'bpmn:CallActivity',
    'bpmn:StartEvent', 'bpmn:IntermediateCatchEvent', 'bpmn:IntermediateThrowEvent', 'bpmn:EndEvent',
    'bpmn:ExclusiveGateway', 'bpmn:ParallelGateway', 'bpmn:InclusiveGateway', 'bpmn:EventBasedGateway',
    'bpmn:SubProcess'
  ].includes(element?.type);
}

function applySequenceFlowType(modeler, connection) {
  if (!connection || connection.type !== 'bpmn:SequenceFlow') return;
  const flowType = modeler.__dscNextSequenceFlowType || 'normal';
  if (flowType === 'normal') return;
  try {
    const modeling = modeler.get('modeling');
    const moddle = modeler.get('moddle');
    if (flowType === 'conditional') {
      modeling.updateProperties(connection, {
        name: connection.businessObject.name || 'Conditional',
        conditionExpression: moddle.create('bpmn:FormalExpression', { body: '${approvalDecision == "approve"}' })
      });
    } else if (flowType === 'default') {
      modeling.updateProperties(connection, { name: connection.businessObject.name || 'Default' });
      if (connection.source) {
        modeling.updateProperties(connection.source, { default: connection.businessObject });
      }
    } else if (flowType === 'skip') {
      modeling.updateProperties(connection, {
        name: connection.businessObject.name || 'Skip',
        conditionExpression: moddle.create('bpmn:FormalExpression', { body: '${skipFlow == true}' })
      });
    }
  } catch {
    // The connection itself is already valid. If metadata decoration fails, keep the user's sequence flow.
  }
}

async function loadCalledWorkflowFromSession(modeler) {
  const params = new URLSearchParams(window.location.search);
  const key = params.get('calledWorkflowSession');
  if (!key) return;
  try {
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return;
    const payload = JSON.parse(raw);
    if (payload?.bpmnXml) {
      await modeler.importXML(payload.bpmnXml);
    }
  } catch {
    // Keep the starter workflow if the session payload cannot be parsed.
  }
}
