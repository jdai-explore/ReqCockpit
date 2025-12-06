import { invoke } from '@tauri-apps/api/tauri';

export interface Project {
  name: string;
  path: string;
}

export const api = {
  listRecentProjects: async (): Promise<Project[]> => {
    try {
      const result = await invoke<string>('list_recent_projects');
      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to list recent projects:', error);
      return [];
    }
  },

  createProject: async (name: string, path: string): Promise<string> => {
    try {
      return await invoke<string>('create_project', { name, path });
    } catch (error) {
      console.error('Failed to create project:', error);
      throw error;
    }
  },
};
