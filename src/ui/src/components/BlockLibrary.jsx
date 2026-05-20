import React, { useState } from 'react';
import { GitBranch, Link2, Maximize, Plus, SquareStack, Undo2, Redo2 } from 'lucide-react';
import { preferredCreateParent, preferredCreatePosition, syncLaneMembership } from '../bpmnLaneSync.js';

const GROUPS = [
  {
    title: 'Events',
    items: [
      { type: 'bpmn:StartEvent', label: 'Start Event' },
      { type: 'bpmn:IntermediateCatchEvent', label: 'Intermediate Catch' },
      { type: 'bpmn:IntermediateThrowEvent', label: 'Intermediate Throw' },
      { type: 'bpmn:BoundaryEvent', label: 'Boundary Event' },
      { type: 'bpmn:EndEvent', label: 'End Event' }
    ]
  },
  {
    title: 'Collibra Tasks',
    items: [
      { type: 'bpmn:Task', label: 'Generic Task' },
      { type: 'bpmn:UserTask', label: 'User Review / Form Task' },
      { type: 'bpmn:ServiceTask', label: 'Collibra Java API Service' },
      { type: 'bpmn:ScriptTask', label: 'Groovy Script Task' },
      { type: 'bpmn:BusinessRuleTask', label: 'Policy / Rule Task' },
      { type: 'bpmn:SendTask', label: 'Notification / Mail Task' },
      { type: 'bpmn:ReceiveTask', label: 'Receive Signal Task' },
      { type: 'bpmn:ManualTask', label: 'Manual Governance Task' },
      { type: 'bpmn:CallActivity', label: 'Call Sub Workflow' }
    ]
  },
  {
    title: 'Gateways',
    items: [
      { type: 'bpmn:ExclusiveGateway', label: 'Exclusive Gateway' },
      { type: 'bpmn:ParallelGateway', label: 'Parallel Gateway' },
      { type: 'bpmn:InclusiveGateway', label: 'Inclusive Gateway' },
      { type: 'bpmn:EventBasedGateway', label: 'Event Based Gateway' }
    ]
  },
  {
    title: 'Data & Artifacts',
    items: [
      { type: 'bpmn:DataObjectReference', label: 'Data Object' },
      { type: 'bpmn:DataStoreReference', label: 'Data Store' },
      { type: 'bpmn:TextAnnotation', label: 'Text Annotation' }
    ]
  },
  {
    title: 'Containers',
    items: [
      { type: 'bpmn:SubProcess', label: 'Expanded Sub Process', attrs: { triggeredByEvent: false } },
      { type: 'bpmn:Participant', label: 'Pool / Participant' },
      { type: 'bpmn:Group', label: 'Visual Group' }
    ]
  }
];

const DEFAULT_SIZE = {
  'bpmn:StartEvent': [36, 36],
  'bpmn:IntermediateCatchEvent': [36, 36],
  'bpmn:IntermediateThrowEvent': [36, 36],
  'bpmn:BoundaryEvent': [36, 36],
  'bpmn:EndEvent': [36, 36],
  'bpmn:ExclusiveGateway': [50, 50],
  'bpmn:ParallelGateway': [50, 50],
  'bpmn:InclusiveGateway': [50, 50],
  'bpmn:EventBasedGateway': [50, 50],
  'bpmn:DataObjectReference': [36, 50],
  'bpmn:DataStoreReference': [50, 50],
  'bpmn:TextAnnotation': [120, 70],
  'bpmn:SubProcess': [320, 190],
  'bpmn:Participant': [720, 300],
  'bpmn:Group': [320, 180]
};

function sizeFor(type) {
  return DEFAULT_SIZE[type] || [160, 86];
}

export default function BlockLibrary({ modeler, selectedElement, addConsole, onConnectionArmed }) {
  const [flowType, setFlowType] = useState('normal');

  function createOrAppend(item) {
    if (!modeler) return;
    try {
      const elementFactory = modeler.get('elementFactory');
      const modeling = modeler.get('modeling');
      const moddle = modeler.get('moddle');
      const [width, height] = sizeFor(item.type);
      const attrs = { name: item.label, ...(item.attrs || {}) };

      if (item.type === 'bpmn:Participant') {
        attrs.processRef = moddle.create('bpmn:Process', { id: `Process_${Date.now()}`, isExecutable: true });
      }
      if (item.type === 'bpmn:ScriptTask') {
        attrs.scriptFormat = 'groovy';
      }
      if (item.type === 'bpmn:DataObjectReference') {
        attrs.dataObjectRef = moddle.create('bpmn:DataObject', { id: `DataObject_${Date.now()}`, name: item.label });
      }

      const businessObject = moddle.create(item.type, attrs);
      const shape = item.type === 'bpmn:Participant' && elementFactory.createParticipantShape
        ? elementFactory.createParticipantShape({ type: item.type, businessObject, width, height })
        : elementFactory.createShape({ type: item.type, businessObject, width, height });

      const canAppend = selectedElement && isFlowNode(selectedElement) && isAppendable(item.type);
      if (canAppend) {
        const autoPlace = safeGet(modeler, 'autoPlace');
        if (autoPlace?.append) {
          autoPlace.append(selectedElement, shape);
          addConsole?.({ level: 'info', message: `Appended ${item.label}`, detail: { after: selectedElement.id, type: item.type } });
          return;
        }
      }

      const position = preferredCreatePosition(modeler, selectedElement);
      const parent = preferredCreateParent(modeler, selectedElement, item.type);
      const created = modeling.createShape(shape, position, parent);
      syncLaneMembership(modeler, created || shape);
      addConsole?.({ level: 'info', message: `Added ${item.label}`, detail: { type: item.type, position } });
    } catch (err) {
      addConsole?.({ level: 'error', message: `Could not add ${item.label}`, detail: err.message });
    }
  }

  function startConnect(event) {
    if (!modeler || !selectedElement) return;
    try {
      event.preventDefault();
      event.stopPropagation();
      modeler.__dscNextSequenceFlowType = flowType;
      modeler.__dscConnectionSource = selectedElement;
      onConnectionArmed?.(selectedElement, flowType);
      addConsole?.({ level: 'info', message: 'Connection source armed', detail: { source: selectedElement.id, flowType, nextStep: 'Click the target BPMN block on the canvas.' } });
    } catch (err) {
      try {
        modeler.__dscNextSequenceFlowType = flowType;
        modeler.get('globalConnect').start(event.nativeEvent || event);
        addConsole?.({ level: 'info', message: 'Global connection mode started', detail: { flowType } });
      } catch (fallbackErr) {
        addConsole?.({ level: 'error', message: 'Connection mode failed', detail: `${err.message}; ${fallbackErr.message}` });
      }
    }
  }

  function addLane() {
    if (!modeler || !selectedElement) return;
    try {
      const modeling = modeler.get('modeling');
      const target = selectedElement.type === 'bpmn:Participant' || selectedElement.type === 'bpmn:Lane'
        ? selectedElement
        : selectedElement.parent;
      if (!target || !['bpmn:Participant', 'bpmn:Lane'].includes(target.type)) {
        throw new Error('Select a pool or lane first.');
      }
      modeling.addLane(target, 'bottom');
      addConsole?.({ level: 'info', message: 'Lane added', detail: target.id });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'Could not add lane', detail: err.message });
    }
  }

  function fit() {
    if (!modeler) return;
    modeler.get('canvas').zoom('fit-viewport');
  }

  function undo() {
    safeGet(modeler, 'commandStack')?.undo();
  }

  function redo() {
    safeGet(modeler, 'commandStack')?.redo();
  }

  return (
    <div className="block-library">
      <div className="library-actions">
        <button onClick={fit}><Maximize size={14}/> Fit</button>
        <button onClick={undo}><Undo2 size={14}/> Undo</button>
        <button onClick={redo}><Redo2 size={14}/> Redo</button>
        <select value={flowType} onChange={event => setFlowType(event.target.value)} title="Sequence flow type">
          <option value="normal">Normal</option>
          <option value="conditional">Conditional</option>
          <option value="default">Default</option>
          <option value="skip">Skip</option>
        </select>
        <button onMouseDown={startConnect} disabled={!selectedElement}><Link2 size={14}/> Connect</button>
        <button onClick={addLane} disabled={!selectedElement}><SquareStack size={14}/> Add Lane</button>
      </div>
      {GROUPS.map(group => (
        <section key={group.title} className="block-group">
          <h4><GitBranch size={14}/> {group.title}</h4>
          <div className="block-grid">
            {group.items.map(item => (
              <button key={item.type + item.label} onClick={() => createOrAppend(item)} title={item.type}><Plus size={13}/> {item.label}</button>
            ))}
          </div>
        </section>
      ))}
      <small>Tip: select a block first, then click a task/gateway to append with sequence flow. Use the native bpmn-js context pad for delete, replace, append, and connect.</small>
    </div>
  );
}

function isFlowNode(element) {
  return element?.businessObject?.$instanceOf?.('bpmn:FlowNode') || [
    'bpmn:Task', 'bpmn:UserTask', 'bpmn:ServiceTask', 'bpmn:ScriptTask', 'bpmn:BusinessRuleTask',
    'bpmn:SendTask', 'bpmn:ReceiveTask', 'bpmn:ManualTask', 'bpmn:CallActivity',
    'bpmn:StartEvent', 'bpmn:IntermediateCatchEvent', 'bpmn:IntermediateThrowEvent', 'bpmn:EndEvent',
    'bpmn:ExclusiveGateway', 'bpmn:ParallelGateway', 'bpmn:InclusiveGateway', 'bpmn:EventBasedGateway',
    'bpmn:SubProcess'
  ].includes(element?.type);
}

function isAppendable(type) {
  return !['bpmn:Participant', 'bpmn:Lane', 'bpmn:Group', 'bpmn:DataObjectReference', 'bpmn:DataStoreReference', 'bpmn:TextAnnotation', 'bpmn:BoundaryEvent'].includes(type);
}

function safeGet(modeler, service) {
  try {
    return modeler?.get(service);
  } catch {
    return null;
  }
}
