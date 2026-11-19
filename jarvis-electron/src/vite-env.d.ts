/// <reference types="vite/client" />

export interface JarvisBackendAPI {
  launchBackend: () => Promise<{ success: boolean; pid?: number; error?: string }>
  stopBackend: () => Promise<{ success: boolean }>
  isRunning: () => Promise<{ running: boolean }>
  onStatusChange: (callback: (status: string) => void) => () => void
}

export interface JarvisKARIONAPI {
  invoke: (channel: string, ...args: any[]) => Promise<any>
  state: () => Promise<{ ok: boolean; data: { connected: boolean; pairing?: { uid: string; deviceName: string }; lastError: string | null } }>
}

declare global {
  interface Window {
    jarvisBackend?: JarvisBackendAPI
    jarvisAPI?: {
      invoke: (channel: string, ...args: any[]) => Promise<any>
      on: (channel: string, func: (...args: any[]) => void) => () => void
      send: (channel: string, ...args: any[]) => void
    }
    karionAPI?: JarvisKARIONAPI
  }
}
