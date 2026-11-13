import { create } from 'zustand';
import { JarvisState, HologramState, ConversationMessage, Task, ApprovalRequest, Notification, DeviceStatus } from '../types';

interface JarvisStore extends JarvisState {
  setHologramState: (state: HologramState) => void;
  setIsListening: (v: boolean) => void;
  setIsSpeaking: (v: boolean) => void;
  setIsWorking: (v: boolean) => void;
  setCurrentTask: (task: Task | null) => void;
  setDeviceStatus: (status: DeviceStatus | null) => void;
  setSims: (sims: any) => void;
  setHealth: (health: any) => void;
  addConversation: (msg: ConversationMessage) => void;
  setConversations: (msgs: ConversationMessage[]) => void;
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  setApprovals: (approvals: ApprovalRequest[]) => void;
  addApproval: (approval: ApprovalRequest) => void;
  removeApproval: (id: string) => void;
  addNotification: (notif: Notification) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  setSidebarOpen: (v: boolean) => void;
  setActiveSection: (section: string) => void;
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
  addConversation: (msg) => set((s) => ({ conversations: [...s.conversations, msg] })),
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
  reset: () => set(initialState),
}));