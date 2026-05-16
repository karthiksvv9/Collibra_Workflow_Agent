import React, { useState } from 'react';
import { designWorkflow } from '../api.js';

export default function ReasoningChat({ appModel, setAppModel, importBpmnXml, addConsole }) {
  const [messages, setMessages] = useState([{ role: 'agent', text: 'Describe a Collibra workflow use case. I can generate a BPMN file, forms, and element scripts using the current RAG index.' }]);
  const [text, setText] = useState('Generate a BPMN workflow for data governance asset approval with requester form, steward review, business owner approval, update asset status, rejection path, and notification task.');
  const [busy, setBusy] = useState(false);

  async function send() {
    const userText = text.trim();
    if (!userText) return;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setText('');
    setBusy(true);
    try {
      const result = await designWorkflow({ prompt: userText, appModel });
      if (result.bpmnXml) await importBpmnXml(result.bpmnXml);
      if (result.appModel) {
        setAppModel(prev => ({
          ...prev,
          ...result.appModel,
          scripts: { ...(prev.scripts || {}), ...(result.appModel.scripts || {}) },
          forms: { ...(prev.forms || {}), ...(result.appModel.forms || {}) },
          uuidMappings: { ...(prev.uuidMappings || {}), ...(result.appModel.uuidMappings || {}) }
        }));
      }
      setMessages(prev => [...prev, { role: 'agent', text: result.summary || 'BPMN generated. Review the canvas, properties, forms, and generated package model.' }]);
      addConsole({ level: 'info', message: 'BPMN/workflow generation completed', detail: result });
    } catch (err) {
      setMessages(prev => [...prev, { role: 'agent', text: `Design failed: ${err.message}` }]);
      addConsole({ level: 'error', message: 'BPMN/workflow generation failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-log">
        {messages.map((m, i) => <div key={i} className={`chat-msg ${m.role}`}>{m.text}</div>)}
      </div>
      <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Ask AI to generate or modify BPMN..." />
      <button onClick={send} disabled={busy}>{busy ? 'Generating BPMN...' : 'Generate / Modify BPMN'}</button>
    </div>
  );
}
