import React, { useState } from 'react';
import BpmnAgentCanvas from './components/BpmnAgentCanvas.jsx';

const initialAppModel = {
  metadata: { name: 'New Collibra Workflow', format: 'DSC_SIDE_CAR_APP_V1' },
  scripts: {},
  forms: {},
  uuidMappings: {},
  validationRules: [],
  elementProperties: {}
};

export default function App() {
  const [appModel, setAppModel] = useState(initialAppModel);
  const [forms, setForms] = useState({});

  return (
    <div className="app-shell">
      <BpmnAgentCanvas
        appModel={appModel}
        setAppModel={setAppModel}
        forms={forms}
        setForms={setForms}
      />
    </div>
  );
}
