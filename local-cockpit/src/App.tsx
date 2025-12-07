import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './components/DashboardPage';
import CockpitGrid from './components/CockpitGrid';
import ProjectHomePage from './components/ProjectHomePage'; // This will be created in a later step

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ProjectHomePage />} />
          <Route path="project/:projectId/dashboard" element={<DashboardPage />} />
          <Route path="project/:projectId/cockpit" element={<CockpitGrid />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
