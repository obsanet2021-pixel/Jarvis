import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('jarvisAPI', {
  invoke: (channel: string, ...args: any[]) => ipcRenderer.invoke(channel, ...args),
  on: (channel: string, func: (...args: any[]) => void) => {
    const subscription = (_event: any, ...args: any[]) => func(...args)
    ipcRenderer.on(channel, subscription)
    return () => ipcRenderer.removeListener(channel, subscription)
  },
  send: (channel: string, ...args: any[]) => ipcRenderer.send(channel, ...args),
})

// KARION bridge — Firestore + E2EE operations via secure main process
contextBridge.exposeInMainWorld('karionAPI', {
  invoke: (channel: string, ...args: any[]) => ipcRenderer.invoke(`karion:${channel}`, ...args),
  state: (): Promise<{ ok: boolean; data: { connected: boolean; pairing?: { uid: string; deviceName: string }; lastError: string | null } }> =>
    ipcRenderer.invoke('karion:state').then((res) => ({ ok: true, data: res })),
})