import React from 'react';
import MasterImportWizard from './components/MasterImportWizard';
import SupplierImportWizard from './components/SupplierImportWizard';
import CockpitGrid from './components/CockpitGrid';
import DashboardPage from './components/DashboardPage';

function App() {
  return (
    <div className="App">
      <DashboardPage />
      <MasterImportWizard />
      <SupplierImportWizard />
      <CockpitGrid />
    </div>
  );
}

export default App;
