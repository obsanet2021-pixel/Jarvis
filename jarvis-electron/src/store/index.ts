import { create } from 'zustand';
import { JarvisState, PersistedSettings } from '../types';

const DEFAULT_SETTINGS: PersistedSettings = { voiceSTT: true };

interface JarvisStore extends JarvisState {
  setHologramState: (state: any) => void;
  setIsListening: (v: boolean) => void;
  setIsSpeaking: (v: boolean) => void;
  setIsWorking: (v: boolean) => void;
  setCurrentTask: (task: any) => void;
  setDeviceStatus: (status: any) => void;
  setSims: (sims: any) => void;
  setHealth: (health: any) => void;
  addConversation: (msg: any) => void;
  setConversations: (msgs: any) => void;
  setTasks: (tasks: any) => void;
  addTask: (task: any) => void;
  updateTask: (id: string, updates: any) => void;
  setApprovals: (approvals: any) => void;
  addApproval: (approval: any) => void;
  removeApproval: (id: string) => void;
  addNotification: (notif: any) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  setSidebarOpen: (v: boolean) => void;
  setActiveSection: (section: string) => void;
  setSettings: (s: Partial<PersistedSettings>) => void;
  reset: () => void;
}

const initialState: JarvisState = {
  hologramState: 'IDLE',
  isListening: false,
  isSpeaking: false,
  isWorking: false,
  currentTask: null,
  deviceStatus: null,
  sims: null,
  health: null,
  conversations: [],
  tasks: [],
  approvals: [],
  notifications: [],
  sidebarOpen: true,
  activeSection: 'home',
  settings: DEFAULT_SETTINGS,
  voiceSTT: DEFAULT_SETTINGS.voiceSTT,
};

export const useJarvisStore = create<JarvisStore>((set) => ({
  ...initialState,

  setHologramState: (state) => set({ hologramState: state }),
  setIsListening: (v) => set({ isListening: v }),
  setIsSpeaking: (v) => set({ isSpeaking: v }),
  setIsWorking: (v) => set({ isWorking: v }),
  setCurrentTask: (task) => set({ currentTask: task }),
  setDeviceStatus: (status) => set({ deviceStatus: status }),
  setSims: (sims) => set({ sims }),
  setHealth: (health) => set({ health }),
  addConversation: (msg) => set((s) => ({ conversations: [...s.conversations, msg] })), // eslint-disable-line @typescript-eslint/no-explicit-any
  setConversations: (msgs) => set({ conversations: msgs }),
  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((s) => ({ tasks: [...s.tasks, task] })),
  updateTask: (id, updates) => set((s) => ({
    tasks: s.tasks.map((t) => (t.id === id ? { ...t, ...updates } : t)),
  })),
  setApprovals: (approvals) => set({ approvals }),
  addApproval: (approval) => set((s) => ({ approvals: [...s.approvals, approval] })),
  removeApproval: (id) => set((s) => ({ approvals: s.approvals.filter((a) => a.id !== id) })),
  addNotification: (notif) => set((s) => ({ notifications: [...s.notifications, notif] })),
  markNotificationRead: (id) => set((s) => ({
    notifications: s.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
  })),
  clearNotifications: () => set({ notifications: [] }),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
  setActiveSection: (section) => set({ activeSection: section }),
  setSettings: (s) => set((state) => ({
    ...state,
    settings: { ...state.settings, ...s },
    voiceSTT: s.voiceSTT !== undefined ? s.voiceSTT : state.voiceSTT,
  })),
  reset: () => set(initialState),
}));