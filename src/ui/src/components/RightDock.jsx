import React from 'react';
import { Bot, Braces, Database, FileText, ScrollText, TableProperties } from 'lucide-react';
import CollibraPropertiesPanel from './CollibraPropertiesPanel.jsx';
import DocumentationPanel from './DocumentationPanel.jsx';
import FormsPanel from './FormsPanel.jsx';
import RagPanel from './RagPanel.jsx';
import ReasoningChat from './ReasoningChat.jsx';
import RunConsole from './RunConsole.jsx';

const TABS = [
  { id: 'properties', label: 'Properties', icon: Braces },
  { id: 'rag', label: 'RAG / Train', icon: Database },
  { id: 'forms', label: 'Forms', icon: TableProperties },
  { id: 'agent', label: 'AI Designer', icon: Bot },
  { id: 'docs', label: 'Docs', icon: FileText },
  { id: 'console', label: 'Console', icon: ScrollText }
];

export default function RightDock({
  activeTab,
  setActiveTab,
  selectedElement,
  appModel,
  setAppModel,
  getBpmnXml,
  importBpmnXml,
  addConsole,
  consoleEntries,
  clearConsole,
  forms
}) {
  return (
    <aside className="right-dock">
      <div className="dock-titlebar">
        <div>
          <b>Agent Dock</b>
          <small>RAG, AI design, Groovy, compile and logs</small>
        </div>
      </div>
      <div className="dock-tabs" role="tablist" aria-label="Agent panels">
        {TABS.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={activeTab === tab.id ? 'active' : ''}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              aria-selected={activeTab === tab.id}
            >
              <Icon size={15} /> <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      <div className="dock-body">
        {activeTab === 'properties' && (
          <CollibraPropertiesPanel
            selectedElement={selectedElement}
            appModel={appModel}
            setAppModel={setAppModel}
            getBpmnXml={getBpmnXml}
            addConsole={addConsole}
            forms={forms}
          />
        )}
        {activeTab === 'rag' && <RagPanel addConsole={addConsole} />}
        {activeTab === 'forms' && <FormsPanel forms={{ ...(appModel?.forms || {}), ...(forms || {}) }} appModel={appModel} selectedElement={selectedElement} />}
        {activeTab === 'docs' && (
          <DocumentationPanel
            appModel={appModel}
            getBpmnXml={getBpmnXml}
            addConsole={addConsole}
          />
        )}
        {activeTab === 'agent' && (
          <ReasoningChat
            appModel={appModel}
            setAppModel={setAppModel}
            importBpmnXml={importBpmnXml}
            addConsole={addConsole}
          />
        )}
        {activeTab === 'console' && (
          <RunConsole
            entries={consoleEntries}
            onClear={clearConsole}
            getBpmnXml={getBpmnXml}
            appModel={appModel}
            forms={forms || appModel?.forms || {}}
            addConsole={addConsole}
          />
        )}
      </div>
    </aside>
  );
}
