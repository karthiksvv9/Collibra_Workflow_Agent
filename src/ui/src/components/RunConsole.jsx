import React, { useState } from 'react';
import { PlayCircle, Trash2 } from 'lucide-react';
import { runWorkflowTestCases } from '../api.js';

export default function RunConsole({ entries, onClear, getBpmnXml, appModel, forms, addConsole }) {
  const [businessUseCase, setBusinessUseCase] = useState('Validate the imported Collibra workflow business process end to end: happy path, rejection/default paths, form validation, Groovy execution, API failure handling and export readiness.');
  const [userTestCases, setUserTestCases] = useState('Scenario: Required form validation\nOpen each user/form task and verify required fields are rendered before completion.\nExpected: Missing required values are reported before task completion.\n\nScenario: Approval happy path\nComplete requester and approver tasks with valid values.\nExpected: Workflow reaches the successful end event.');
  const [busy, setBusy] = useState(false);

  async function runCases() {
    if (!getBpmnXml) return;
    setBusy(true);
    try {
      const bpmnXml = await getBpmnXml();
      const result = await runWorkflowTestCases({ bpmnXml, appModel, forms, businessUseCase, userTestCases, maxIterations: 3 });
      addConsole?.({
        level: result.ok ? 'success' : 'error',
        message: `AI + user test cases ${result.status}`,
        detail: result
      });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'AI + user test cases failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="run-console">
      <section className="test-case-runner">
        <div className="panel-section-head">
          <div>
            <b>AI + User Test Cases</b>
            <small>Runs generated business test cases plus the user scenarios below against BPMN, forms and Groovy.</small>
          </div>
        </div>
        <label>Business use case for AI-generated tests
          <textarea value={businessUseCase} onChange={e => setBusinessUseCase(e.target.value)} />
        </label>
        <label>User test cases
          <textarea value={userTestCases} onChange={e => setUserTestCases(e.target.value)} />
        </label>
        <button className="primary-button" onClick={runCases} disabled={busy || !getBpmnXml}>
          <PlayCircle size={15}/> {busy ? 'Running...' : 'Run AI + user tests'}
        </button>
      </section>

      <div className="panel-section-head">
        <div>
          <b>Console Output</b>
          <small>Import, RAG, AI, simulation and compile logs</small>
        </div>
        {onClear && <button onClick={onClear}><Trash2 size={14}/> Clear</button>}
      </div>
      {entries.length === 0 && <div className="empty-panel">No logs yet. Import BPMN, build RAG, generate Groovy, compile, simulate, or export.</div>}
      {entries.map((entry, idx) => (
        <details key={idx} open={idx === entries.length - 1} className={`console-entry ${entry.level || 'info'}`}>
          <summary>{entry.at || new Date().toLocaleTimeString()} - {entry.message}</summary>
          <pre>{typeof entry.detail === 'string' ? entry.detail : JSON.stringify(entry.detail, null, 2)}</pre>
        </details>
      ))}
    </div>
  );
}
