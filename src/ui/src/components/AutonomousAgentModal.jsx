import React, { useMemo, useState } from 'react';
import { Bot, FileInput, PlayCircle, X } from 'lucide-react';
import { runAutonomousAgent } from '../api.js';

export default function AutonomousAgentModal({
  open,
  onClose,
  getBpmnXml,
  appModel,
  forms,
  onResult,
  addConsole,
  modelId
}) {
  const [mode, setMode] = useState('prompt');
  const [prompt, setPrompt] = useState('Create a production Collibra governed access workflow with requester intake, steward triage, business approval, risk review, rework/rejection reroutes, policy exception automation, relation/responsibility creation, call activity to downstream provisioning workflow, API failure remediation, completion notification, documentation and complete test evidence.');
  const [userTestCases, setUserTestCases] = useState('Scenario: Happy path approval and provisioning\nExpected: The workflow reaches the approved end event and exports without blocking issues.\n\nScenario: Rework path\nExpected: Missing required values route to requester rework and then back to validation.\n\nScenario: Downstream provisioning failure\nExpected: Failed provisioning routes to technical remediation and retries the call activity.');
  const [running, setRunning] = useState(false);
  const [lastSummary, setLastSummary] = useState(null);

  const title = useMemo(() => mode === 'prompt' ? 'Run From Prompt' : 'Run On Canvas / Imported Workflow', [mode]);
  if (!open) return null;

  async function run() {
    setRunning(true);
    setLastSummary(null);
    try {
      const payload = {
        mode,
        prompt,
        businessUseCase: prompt,
        userTestCases,
        modelId,
        forceAi: true,
        packageName: mode === 'prompt' ? 'autonomous_prompt_workflow' : 'autonomous_canvas_workflow',
        maxIterations: 5
      };
      if (mode !== 'prompt') {
        payload.bpmnXml = await getBpmnXml();
        payload.appModel = appModel;
        payload.forms = forms;
      }
      addConsole?.({ level: 'info', message: `Autonomous Agent Mode started: ${title}`, detail: payload });
      const result = await runAutonomousAgent(payload);
      setLastSummary(result);
      await onResult?.(result);
      addConsole?.({
        level: result.ok ? 'success' : 'error',
        message: `Autonomous Agent Mode ${result.status}`,
        detail: result
      });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'Autonomous Agent Mode failed', detail: err.message });
      setLastSummary({ ok: false, status: 'failed', error: err.message });
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="autonomous-overlay" role="dialog" aria-modal="true">
      <div className="autonomous-modal">
        <header>
          <div>
            <b><Bot size={18}/> Autonomous Agent Mode</b>
            <small>RAG retrieval, BPMN design/import analysis, Groovy compile, repair, tests, docs and export.</small>
          </div>
          <button onClick={onClose} aria-label="Close autonomous agent mode"><X size={17}/></button>
        </header>

        <div className="mode-switch">
          <button className={mode === 'prompt' ? 'active' : ''} onClick={() => setMode('prompt')}><Bot size={15}/> Prompt</button>
          <button className={mode === 'canvas' ? 'active' : ''} onClick={() => setMode('canvas')}><FileInput size={15}/> Current canvas/import</button>
        </div>

        <label>
          Business prompt / operating instruction
          <textarea value={prompt} onChange={event => setPrompt(event.target.value)} rows={8} />
        </label>

        <label>
          User test cases
          <textarea value={userTestCases} onChange={event => setUserTestCases(event.target.value)} rows={7} />
        </label>

        <div className="autonomous-note">
          <b>{title}</b>
          <span>
            {mode === 'prompt'
              ? 'The agent starts from the prompt, searches RAG, designs BPMN/forms/Groovy, compiles, tests, repairs and exports.'
              : 'The agent uses the BPMN currently on the canvas, including imported packages, and repairs/tests/exports it autonomously.'}
          </span>
        </div>

        {lastSummary && (
          <div className={`autonomous-result ${lastSummary.ok ? 'success' : 'error'}`}>
            <b>Status: {lastSummary.status || 'unknown'}</b>
            {lastSummary.zipPath && <span>ZIP: {lastSummary.zipPath}</span>}
            {lastSummary.reportPath && <span>Report: {lastSummary.reportPath}</span>}
          </div>
        )}

        <footer>
          <button onClick={onClose}>Close</button>
          <button className="primary-button" onClick={run} disabled={running || !prompt.trim()}>
            <PlayCircle size={16}/> {running ? 'Running autonomous loop...' : 'Run Autonomous Agent'}
          </button>
        </footer>
      </div>
    </div>
  );
}
