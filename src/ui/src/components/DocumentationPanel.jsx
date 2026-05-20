import React, { useState } from 'react';
import { BookOpen, Copy, FileText, Sparkles } from 'lucide-react';
import { generateDocumentation } from '../api.js';

export default function DocumentationPanel({ appModel, forms, getBpmnXml, addConsole, modelId }) {
  const [prompt, setPrompt] = useState('Generate complete production documentation for this Collibra workflow: purpose, BPMN flow, pools, lanes, forms, Groovy scripts, sequence-flow rules, RAG assumptions, test cases, deployment notes and rollback plan.');
  const [markdown, setMarkdown] = useState('');
  const [path, setPath] = useState('');
  const [htmlPath, setHtmlPath] = useState('');
  const [busy, setBusy] = useState(false);

  async function generate() {
    setBusy(true);
    try {
      const bpmnXml = await getBpmnXml();
      const mergedForms = { ...(appModel?.forms || {}), ...(forms || {}) };
      const result = await generateDocumentation({ bpmnXml, appModel, forms: mergedForms, prompt, modelId });
      setMarkdown(result.markdown || '');
      setPath(result.path || '');
      setHtmlPath(result.htmlPath || '');
      addConsole?.({ level: 'success', message: 'Documentation generated', detail: result });
    } catch (err) {
      addConsole?.({ level: 'error', message: 'Documentation generation failed', detail: err.message });
    } finally {
      setBusy(false);
    }
  }

  async function copyMarkdown() {
    try {
      await navigator.clipboard.writeText(markdown);
      addConsole?.({ level: 'info', message: 'Documentation copied to clipboard', detail: `${markdown.length} characters` });
    } catch (err) {
      addConsole?.({ level: 'warn', message: 'Clipboard copy failed', detail: err.message });
    }
  }

  return (
    <div className="documentation-panel">
      <div className="rag-hero">
        <b><BookOpen size={15}/> AI Documentation</b>
        <span>Creates a production handoff document from the current BPMN XML, sidecar app metadata, forms, scripts, RAG status and Collibra-oriented test plan.</span>
      </div>

      <section className="rag-card">
        <label>Documentation instruction
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)} />
        </label>
        <div className="button-row">
          <button className="primary-button" onClick={generate} disabled={busy}>
            <Sparkles size={15}/> {busy ? 'Generating...' : 'Generate documentation'}
          </button>
          <button onClick={copyMarkdown} disabled={!markdown}>
            <Copy size={15}/> Copy markdown
          </button>
        </div>
        {path && <small>Markdown saved to {path}</small>}
        {htmlPath && <small>Confluence-ready HTML saved to {htmlPath}</small>}
      </section>

      <section className="property-card code-card">
        <div className="panel-section-head">
          <div>
            <b>Generated Markdown</b>
            <small>Export-ready workflow documentation for design, implementation, tests and deployment.</small>
          </div>
          <FileText size={16}/>
        </div>
        <textarea
          className="doc-output-box"
          value={markdown}
          onChange={e => setMarkdown(e.target.value)}
          placeholder="Generated documentation will appear here."
          spellCheck={false}
        />
      </section>
    </div>
  );
}
