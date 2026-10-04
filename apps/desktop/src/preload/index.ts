/**
 * Arayüze yalnızca ihtiyaç duyduğu dar API'yi açar (contextIsolation açık, Node kapalı).
 */
import { contextBridge, ipcRenderer } from 'electron';
import { IPC, type SitWiseApi } from '../shared/ipc';

const api: SitWiseApi = {
  getSettings: () => ipcRenderer.invoke(IPC.getSettings),
  setAutoStart: (enabled) => ipcRenderer.invoke(IPC.setAutoStart, enabled),
  setPaused: (paused) => ipcRenderer.invoke(IPC.setPaused, paused),
  onPausedChanged: (listener) => {
    const handler = (_e: Electron.IpcRendererEvent, paused: boolean): void => listener(paused);
    ipcRenderer.on(IPC.pausedChanged, handler);
    return () => ipcRenderer.removeListener(IPC.pausedChanged, handler);
  },
};

contextBridge.exposeInMainWorld('sitwise', api);
