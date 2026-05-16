import React, { useEffect, useMemo, useState } from 'react';
import { Database, FileUp, RefreshCw, Search, UploadCloud, FolderSync, ListFilter } from 'lucide-react';
import { generateRagIndex, getRagStatus, ingestFiles, ragChat, ragQuery, reindexRag, uploadRagFiles } from '../api.js';

export default function RagPanel({ addConsole }) {
  const [status, setStatus] = useState(null);
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState('Find Collibra workflow UUIDs, asset relations, BPMN tasks, form fields, app settings, Groovy standards and Java API hints from the indexed knowledge base.');
  const [searchText, setSearchText] = useState('asset relation uuid workflow form groovy');
  const [messages, setMessages] = useState([{ role: 'agent', text: 'RAG is ready. Upload Collibra ZIP/BPMN/forms/apps/docs/Excel/PDF/Word/XML files, then click Upload + Index or Generate Index / Train RAG.' }]);
  const [results, setResults] = useState([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    refreshStatus();
  }, []);

  const fileSummary = useMemo(() => {
    if (!files.length) return 'No files selected';
    if (files.length === 1) return files[0].name;
    return `${files.length} files selected: ${files.slice(0, 3).map(f => f.name).join(', ')}${files.length > 3 ? '...' : ''}`;
  }, [files]);

  async function refreshStatus() {
    try {
      const s = await getRagStatus();
      setStatus(s);
    } catch (err) {
      addConsole?.({ level: 'error', message: 'RAG status failed', detail: err.message });
    }
  }

  async function uploadOnly() {
    if (!files.length) return;
    setBusy(true);
    try {
      const result = await uploadRagFiles(files);
      addConsole?.({ level: 'info', message: 'RAG files uploaded', detail: result });
      setMessages(prev => [...prev, { role: 'agent', text: `${files.length} file(s) uploaded to /docs. Use Incremental Reindex to add only the new knowledge or Generate Index to rebuild from scratch.` }]);
      setFiles([]);
      await refreshStatus();
    } catch (err) {
      addConsole?.({ level: 'error', message: 'RAG upload failed', detail: err.message });
      setMessages(prev => [...prev, { role: 'agent', text: `Upload failed: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function uploadAndIndex() {
    if (!files.length) return;
    setBusy(true);
    try {
      const result = await ingestFiles(files);
      setStatus(result.status);
      addConsole?.({ level: 'success', message: 'RAG upload + incremental index completed', detail: result });
      setMessages(prev => [...prev, { role: 'agent', text: `Uploaded and incrementally indexed ${files.length} file(s). Chunks: ${result.status?.recordCount || 0}; UUIDs: ${result.status?.uuidCount || 0}; tables: ${result.status?.tableCount || 0}.` }]);
      setFiles([]);
    } catch (err) {
      addConsole?.({ level: 'error', message: 'RAG upload + index failed', detail: err.message });
      setMessages(prev => [...prev, { role: 'agent', text: `Upload + index failed: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function buildIndex() {
    setBusy(true);
    try {
      const result = await generateRagIndex();
      setStatus(result.status);
      addConsole?.({ level: 'success', message: 'Full RAG index/training completed', detail: result });
      setMessages(prev => [...prev, { role: 'agent', text: `Full index regenerated from /docs. Records: ${result.status?.recordCount || 0}, files: ${result.status?.sourceFileCount || 0}.` }]);
    } catch (err) {
      addConsole?.({ level: 'error', message: 'RAG full index failed', detail: err.message });
      setMessages(prev => [...prev, { role: 'agent', text: `Full index failed: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function incrementalReindex() {
    setBusy(true);
    try {
      const result = await reindexRag();
      setStatus(result.status);
      addConsole?.({ level: 'success', message: 'RAG incremental reindex completed', detail: result });
      setMessages(prev => [...prev, { role: 'agent', text: `Incremental reindex completed. Current chunks: ${result.status?.recordCount || 0}; files: ${result.status?.sourceFileCount || 0}.` }]);
    } catch (err) {
      addConsole?.({ level: 'error', message: 'RAG incremental reindex failed', detail: err.message });
      setMessages(prev => [...prev, { role: 'agent', text: `Incremental reindex failed: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function search() {
    const q = searchText.trim();
    if (!q) return;
    setBusy(true);
    try {
      const result = await ragQuery({ question: q, top_k: 12 });
      setResults(result.results || []);
      addConsole?.({ level: 'info', message: 'RAG search completed', detail: result });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'RAG search failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  async function ask() {
    const q = question.trim();
    if (!q) return;
    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setBusy(true);
    try {
      const result = await ragChat({ question: q, top_k: 10 });
      const sourceText = (result.results || []).slice(0, 6).map(r => `- ${r.fileName} (${Number(r.score || 0).toFixed(3)})`).join('\n');
      const answer = `${result.answer || 'No answer returned.'}${sourceText ? `\n\nSources:\n${sourceText}` : ''}`;
      setMessages(prev => [...prev, { role: 'agent', text: answer }]);
      addConsole?.({ level: 'info', message: 'RAG chat completed', detail: result });
    } catch (err) {
      setMessages(prev => [...prev, { role: 'agent', text: `RAG chat failed: ${err.message}` }]);
      addConsole?.({ level: 'error', message: 'RAG chat failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rag-panel">
      <div className="rag-hero">
        <b>Enterprise RAG Knowledge Base</b>
        <span>Upload and index Collibra APIs, exported workflow packages, BPMN, form/app XML, Groovy, Excel mappings, PDFs, Word docs and table-level relation sheets.</span>
      </div>

      <div className="rag-status-grid">
        <div><b>{status?.recordCount || 0}</b><span>chunks</span></div>
        <div><b>{status?.sourceFileCount || 0}</b><span>files</span></div>
        <div><b>{status?.uuidCount || 0}</b><span>UUIDs</span></div>
        <div><b>{status?.tableCount || 0}</b><span>tables</span></div>
        <div><b>{status?.elementCount || 0}</b><span>BPMN/Form elements</span></div>
      </div>

      <section className="rag-card">
        <div className="panel-section-head">
          <div>
            <b>1. Upload knowledge</b>
            <small>{fileSummary}</small>
          </div>
        </div>
        <div className="rag-actions primary-actions">
          <label className="file-button strong-file-button">
            <UploadCloud size={15} /> Select files
            <input
              type="file"
              multiple
              accept=".zip,.bpmn,.xml,.bpmn20.xml,.form,.app,.groovy,.docx,.pdf,.xlsx,.xlsm,.csv,.txt,.md,.json"
              onChange={e => setFiles(Array.from(e.target.files || []))}
            />
          </label>
          <button onClick={uploadAndIndex} disabled={busy || !files.length} className="primary-button"><FileUp size={15}/> Upload + Index</button>
          <button onClick={uploadOnly} disabled={busy || !files.length}><UploadCloud size={15}/> Upload only</button>
        </div>
      </section>

      <section className="rag-card">
        <div className="panel-section-head">
          <div>
            <b>2. Build / reindex</b>
            <small>Full rebuild resets the index. Incremental appends new or changed documents.</small>
          </div>
        </div>
        <div className="rag-actions primary-actions">
          <button onClick={buildIndex} disabled={busy} className="primary-button"><Database size={15}/> Generate Index / Train RAG</button>
          <button onClick={incrementalReindex} disabled={busy}><FolderSync size={15}/> Incremental Reindex</button>
          <button onClick={refreshStatus} disabled={busy}><RefreshCw size={15}/> Refresh Status</button>
        </div>
      </section>

      <section className="rag-card">
        <div className="panel-section-head">
          <div>
            <b>3. Search index</b>
            <small>Use this before asking AI to verify which files and UUID mappings are retrieved.</small>
          </div>
        </div>
        <div className="inline-search-row">
          <input value={searchText} onChange={e => setSearchText(e.target.value)} placeholder="Search RAG knowledge..." />
          <button onClick={search} disabled={busy || !searchText.trim()}><ListFilter size={15}/> Search</button>
        </div>
        {results.length > 0 && (
          <div className="rag-results">
            {results.slice(0, 8).map((r, i) => (
              <details key={i}>
                <summary>{r.fileName} - {Number(r.score || 0).toFixed(3)}</summary>
                <pre>{r.text}</pre>
              </details>
            ))}
          </div>
        )}
      </section>

      <section className="rag-card rag-chat-section">
        <div className="panel-section-head">
          <div>
            <b>4. Chat with RAG</b>
            <small>Ask about APIs, UUIDs, relations, forms, BPMN tasks, Groovy standards and compilation hints.</small>
          </div>
        </div>
        <div className="chat-log rag-chat-log">
          {messages.map((m, i) => <div key={i} className={`chat-msg ${m.role}`}>{m.text}</div>)}
        </div>
        <textarea value={question} onChange={e => setQuestion(e.target.value)} placeholder="Ask RAG about Collibra APIs, UUIDs, relations, forms, BPMN tasks..." />
        <button onClick={ask} disabled={busy || !question.trim()} className="primary-button"><Search size={15}/> Chat with RAG</button>
      </section>
    </div>
  );
}
