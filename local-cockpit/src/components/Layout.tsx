import { NavLink, Outlet } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';

const Layout = () => {
  const { currentProject } = useAppStore();

  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-gray-800 text-white p-4">
        <h1 className="text-2xl font-bold mb-4">Local Cockpit</h1>
        <nav>
          <ul>
            <li>
              <NavLink to="/" end className={({ isActive }) => isActive ? "font-bold text-blue-300" : ""}>Projects</NavLink>
            </li>
            {currentProject && (
              <>
                <li>
                  <NavLink to={`/project/${encodeURIComponent(currentProject.path)}/dashboard`} className={({ isActive }) => isActive ? "font-bold text-blue-300" : ""}>Dashboard</NavLink>
                </li>
                <li>
                  <NavLink to={`/project/${encodeURIComponent(currentProject.path)}/cockpit`} className={({ isActive }) => isActive ? "font-bold text-blue-300" : ""}>Cockpit</NavLink>
                </li>
              </>
            )}
          </ul>
        </nav>
      </aside>
      <main className="flex-1 p-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
