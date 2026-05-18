export function syncLaneMembership(modeler, element) {
  if (!modeler || !element || !isFlowNode(element) || element.type === 'label') return null;
  const elementRegistry = modeler.get('elementRegistry');
  const lanes = elementRegistry.filter(e => e.type === 'bpmn:Lane');
  if (!lanes.length) return null;
  const targetLane = laneAtCenter(lanes, element);
  const bo = element.businessObject;
  lanes.forEach(lane => {
    const laneBo = lane.businessObject;
    const refs = Array.isArray(laneBo.flowNodeRef) ? laneBo.flowNodeRef : [];
    laneBo.flowNodeRef = refs.filter(ref => ref && ref.id !== bo.id);
  });
  if (targetLane) {
    const laneBo = targetLane.businessObject;
    laneBo.flowNodeRef = Array.isArray(laneBo.flowNodeRef) ? laneBo.flowNodeRef : [];
    if (!laneBo.flowNodeRef.some(ref => ref && ref.id === bo.id)) {
      laneBo.flowNodeRef.push(bo);
    }
    return targetLane;
  }
  return null;
}

export function syncAllLaneMembership(modeler) {
  if (!modeler) return;
  const elementRegistry = modeler.get('elementRegistry');
  elementRegistry.filter(isFlowNode).forEach(element => syncLaneMembership(modeler, element));
}

export function preferredCreateParent(modeler, selectedElement, type) {
  const canvas = modeler.get('canvas');
  const elementRegistry = modeler.get('elementRegistry');
  const root = canvas.getRootElement();
  if (type === 'bpmn:Participant') return root;
  if (type === 'bpmn:Group' || type === 'bpmn:TextAnnotation') return selectedElement?.parent || firstParticipant(elementRegistry) || root;
  if (selectedElement?.type === 'bpmn:Participant') return selectedElement;
  if (selectedElement?.type === 'bpmn:Lane') return selectedElement.parent || firstParticipant(elementRegistry) || root;
  if (selectedElement?.parent?.type === 'bpmn:Lane') return selectedElement.parent.parent || firstParticipant(elementRegistry) || root;
  return firstParticipant(elementRegistry) || root;
}

export function preferredCreatePosition(modeler, selectedElement) {
  const canvas = modeler.get('canvas');
  const elementRegistry = modeler.get('elementRegistry');
  const lane = selectedElement?.type === 'bpmn:Lane'
    ? selectedElement
    : selectedElement?.parent?.type === 'bpmn:Lane'
      ? selectedElement.parent
      : elementRegistry.filter(e => e.type === 'bpmn:Lane')?.[0];
  if (lane) {
    return { x: lane.x + Math.min(Math.max(240, lane.width * 0.35), lane.width - 180), y: lane.y + lane.height / 2 };
  }
  const viewbox = canvas.viewbox();
  return { x: viewbox.x + viewbox.width / 2, y: viewbox.y + Math.min(viewbox.height / 2, 260) };
}

function firstParticipant(elementRegistry) {
  return elementRegistry.filter(e => e.type === 'bpmn:Participant')?.[0] || null;
}

function laneAtCenter(lanes, element) {
  const cx = element.x + (element.width || 0) / 2;
  const cy = element.y + (element.height || 0) / 2;
  return lanes.find(lane => cx >= lane.x && cx <= lane.x + lane.width && cy >= lane.y && cy <= lane.y + lane.height) || null;
}

function isFlowNode(element) {
  return Boolean(element?.businessObject?.$instanceOf?.('bpmn:FlowNode')) || [
    'bpmn:Task', 'bpmn:UserTask', 'bpmn:ServiceTask', 'bpmn:ScriptTask', 'bpmn:BusinessRuleTask',
    'bpmn:SendTask', 'bpmn:ReceiveTask', 'bpmn:ManualTask', 'bpmn:CallActivity',
    'bpmn:StartEvent', 'bpmn:IntermediateCatchEvent', 'bpmn:IntermediateThrowEvent', 'bpmn:EndEvent',
    'bpmn:ExclusiveGateway', 'bpmn:ParallelGateway', 'bpmn:InclusiveGateway', 'bpmn:EventBasedGateway',
    'bpmn:SubProcess'
  ].includes(element?.type);
}
