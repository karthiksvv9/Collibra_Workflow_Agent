import React from 'react';
import { Trash2 } from 'lucide-react';

export default function RunConsole({ entries, onClear }) {
  return (
    <div className="run-console">
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
