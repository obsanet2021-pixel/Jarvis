export type HologramState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'WORKING' | 'ERROR';

export interface SIMConfig {
  phone_number: string;
  network: string | null;
  ussd_code: string | null;
  sub_id: number;
  manual_override: {
    network: string | null;
    ussd_code: string | null;
  };
}

export interface SIMsConfig {
  SIM1: SIMConfig;
  SIM2: SIMConfig;
}

export interface SystemStatus {
  status: string;
  call_state: string;
  timestamp: number;
}

export interface CallResult {
  status: string;
  target: string;
  output: string;
}

export interface BalanceResult {
  status: string;
  sim: string;
  network: string;
  code: string;
  sub_id: number;
  message: string;
}

export interface BackendHealth {
  status: string;
  timestamp: number;
  version: string;
}

export interface DeviceStatus {
  windows: 'connected' | 'disconnected' | 'unknown';
  android: 'connected' | 'disconnected' | 'unknown';
  adb: 'connected' | 'disconnected' | 'unknown';
  sim1: 'available' | 'unavailable';
  sim2: 'available' | 'unavailable';
  backend: 'online' | 'offline';
  ai_service: 'online' | 'offline';
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

export interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  created_at: number;
  updated_at: number;
  agent?: string;
}

export interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high';
  created_at: number;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
}

export interface PersistedSettings {
  voiceSTT: boolean;
}

export interface JarvisState extends PersistedSettings {
  hologramState: HologramState;
  isListening: boolean;
  isSpeaking: boolean;
  isWorking: boolean;
  currentTask: Task | null;
  deviceStatus: DeviceStatus | null;
  sims: SIMsConfig | null;
  health: BackendHealth | null;
  conversations: ConversationMessage[];
  tasks: Task[];
  approvals: ApprovalRequest[];
  notifications: Notification[];
  sidebarOpen: boolean;
  activeSection: string;
  settings: PersistedSettings;
}

export type NavSection = 'home' | 'conversations' | 'tasks' | 'agents' | 'memory' | 'devices' | 'integrations' | 'activity' | 'settings' | 'mobile-bridge';
export interface KarionState {
  connected: boolean
  pairing: { uid: string; deviceName: string } | null
}
