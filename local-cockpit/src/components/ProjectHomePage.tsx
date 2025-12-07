import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { api, type Project } from '../lib/api';
import { open } from '@tauri-apps/api/dialog';

const ProjectHomePage = () => {
  const { recentProjects, fetchRecentProjects, setCurrentProject } = useAppStore();
  const navigate = useNavigate();
  const [isCreateModalOpen, setCreateModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentProjects();
  }, [fetchRecentProjects]);

  const handleProjectClick = (project: Project) => {
    setCurrentProject(project);
    const projectId = encodeURIComponent(project.path);
    navigate(`/project/${projectId}/dashboard`);
  };

  const handleCreateProject = async () => {
    const selectedPath = await open({
      directory: true,
      multiple: false,
      title: 'Select Project Directory',
    });

    if (typeof selectedPath === 'string') {
      try {
        setErrorMessage(null);
        const newProjectPath = await api.createProject(newProjectName, selectedPath);
        const newProject = { name: newProjectName, path: newProjectPath };
        setCurrentProject(newProject);
        fetchRecentProjects(); // Refresh the list
        const projectId = encodeURIComponent(newProjectPath);
        navigate(`/project/${projectId}/dashboard`);
      } catch (error) {
        console.error('Failed to create project:', error);
        setErrorMessage(error instanceof Error ? error.message : String(error));
      }
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Projects</h1>
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          onClick={() => setCreateModalOpen(true)}
        >
          Create New Project
        </button>
      </div>
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Recent Projects</h2>
        <ul>
          {recentProjects.map((project) => (
            <li
              key={project.path}
              className="cursor-pointer hover:bg-gray-100 p-2 rounded"
              onClick={() => handleProjectClick(project)}
            >
              {project.name}
            </li>
          ))}
        </ul>
      </div>

      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4">Create New Project</h2>
            <input
              type="text"
              className="border p-2 w-full mb-4"
              placeholder="Project Name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
            />
            {errorMessage && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong className="font-bold">Error:</strong>
                <span className="block sm:inline"> {errorMessage}</span>
              </div>
            )}
            <div className="flex justify-end">
              <button
                className="bg-gray-300 hover:bg-gray-400 text-black font-bold py-2 px-4 rounded mr-2"
                onClick={() => setCreateModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={handleCreateProject}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectHomePage;
