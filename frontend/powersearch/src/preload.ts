import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  searchQuery: (query: string, fileType: string) => ipcRenderer.invoke('search-query', query, fileType),
  openFileLocation: (filePath: string) => ipcRenderer.invoke('open-file-location', filePath),
  openFile: (filePath: string) => ipcRenderer.invoke('open-file', filePath),
  // Platform detection
  platform: process.platform,
});

// Type definitions for the exposed API
declare global {
  interface Window {
    electronAPI: {
      searchQuery: (query: string, fileType: string) => Promise<{ success: boolean; data?: any; error?: string }>;
      openFileLocation: (filePath: string) => Promise<void>;
      openFile: (filePath: string) => Promise<void>;
      platform: string;
    };
  }
}
