import { create } from 'zustand';
import { api, type Project } from '../lib/api';

interface AppState {
  recentProjects: Project[];
  currentProject: Project | null;
  fetchRecentProjects: () => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  recentProjects: [],
  currentProject: null,
  fetchRecentProjects: async () => {
    const projects = await api.listRecentProjects();
    set({ recentProjects: projects });
  },
  setCurrentProject: (project) => set({ currentProject: project }),
}));
