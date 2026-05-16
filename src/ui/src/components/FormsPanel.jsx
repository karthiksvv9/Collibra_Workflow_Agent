import React, { useMemo, useState } from 'react';
import { ClipboardList, Search } from 'lucide-react';

export default function FormsPanel({ forms, appModel, selectedElement }) {
  const [filter, setFilter] = useState('');
  const linkedFormKey = selectedFormKey(selectedElement, appModel);
  const items = useMemo(() => Object.entries(forms || {}).map(([key, value]) => normalizeForm(key, value)), [forms]);
  const filtered = items.filter(form => {
    const q = filter.trim().toLowerCase();
    if (!q) return true;
    return [form.key, form.name, form.source, ...form.fields.map(field => `${field.id} ${field.label} ${field.type}`)]
      .join(' ')
      .toLowerCase()
      .includes(q);
  });

  return (
    <div className="forms-panel">
      <div className="rag-hero">
        <b><ClipboardList size={15}/> Collibra Forms</b>
        <span>Shows imported `.form` files, inline `flowable:formProperty` definitions, outcomes, field IDs, required flags, visibility and extra settings.</span>
      </div>
      <div className="inline-search-row">
        <input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Search forms, fields, labels or types" />
        <button><Search size={15}/> Search</button>
      </div>
      {linkedFormKey && (
        <small className="linked-form-pill">Selected element form: {linkedFormKey}</small>
      )}
      <div className="forms-list">
        {filtered.length === 0 && <div className="empty-panel"><b>No forms found</b><p>Import a Collibra ZIP or `.form` file to inspect form metadata here.</p></div>}
        {filtered.map(form => (
          <details key={form.key} className={form.key === linkedFormKey ? 'form-card linked' : 'form-card'} open={form.key === linkedFormKey || filtered.length <= 4}>
            <summary>
              <span>{form.name}</span>
              <small>{form.key} - {form.fields.length} fields - {form.outcomes.length} outcomes{fieldPreview(form) ? ` - ${fieldPreview(form)}` : ''}</small>
            </summary>
            <div className="form-meta-grid">
              <div><span>Source</span><b>{form.source || 'n/a'}</b></div>
              <div><span>Model</span><b>{form.modelType || 'form'}</b></div>
              <div><span>Palette</span><b>{form.palette || 'n/a'}</b></div>
              <div><span>Version</span><b>{form.version || 'n/a'}</b></div>
            </div>
            {form.outcomes.length > 0 && (
              <div className="outcome-row">
                {form.outcomes.map(outcome => (
                  <span key={`${form.key}-${outcome.value || outcome.label}`}>{outcome.label || outcome.value}</span>
                ))}
              </div>
            )}
            <div className="field-table">
              <div className="field-row field-head"><span>ID</span><span>Label</span><span>Type</span><span>Required</span></div>
              {form.fields.map(field => (
                <div className="field-row" key={`${form.key}-${field.id}-${field.row}-${field.column}`}>
                  <code>{field.id}</code>
                  <span>{field.label || field.name}</span>
                  <span>{field.type}</span>
                  <span>{field.required ? 'yes' : 'no'}</span>
                </div>
              ))}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}

function selectedFormKey(selectedElement, appModel) {
  if (!selectedElement) return '';
  const props = appModel?.elementProperties?.[selectedElement.id] || {};
  const attrs = selectedElement.businessObject?.$attrs || {};
  return props.formKey || attrs['flowable:formKey'] || attrs.formKey || selectedElement.businessObject?.formKey || '';
}

function normalizeForm(key, value) {
  if (!value || typeof value !== 'object') {
    return { key, name: key, source: '', modelType: 'raw', palette: '', version: '', fields: [], outcomes: [] };
  }
  return {
    key: value.key || key,
    name: value.name || value.metadata?.name || value.key || key,
    source: value.source || '',
    modelType: value.modelType || value.metadata?.modelType || 'form',
    palette: value.palette || value.metadata?.palette || '',
    version: value.version || value.metadata?.version || '',
    fields: Array.isArray(value.fields) ? value.fields : [],
    outcomes: Array.isArray(value.outcomes) ? value.outcomes : []
  };
}

function fieldPreview(form) {
  return form.fields.slice(0, 3).map(field => field.id).filter(Boolean).join(', ');
}
