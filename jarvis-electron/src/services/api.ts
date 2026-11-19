import {
  BackendHealth,
  SIMsConfig,
  CallResult,
  BalanceResult,
  SystemStatus,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:31415'
const API_KEY_STORAGE_KEY = 'jarvis_llm_api_key'

function loadApiKey(): string {
  try {
    return localStorage.getItem(API_KEY_STORAGE_KEY) || ''
  } catch {
    return ''
  }
}

interface VoiceProcessResult {
  success: boolean
  response: string
  raw?: Record<string, unknown>
}

interface VoiceStatus {
  integration_status: string
  is_listening: boolean
  is_speaking: boolean
  metrics?: Record<string, unknown>
  error?: string
}

export class JarvisAPI {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`
    const apiKey = loadApiKey()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`
    }
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // ── Health & Status ────────────────────────────────────────────────────────

  async health(): Promise<BackendHealth> {
    return this.request<BackendHealth>('/health')
  }

  async sims(): Promise<SIMsConfig> {
    return this.request<SIMsConfig>('/sims')
  }

  async status(): Promise<SystemStatus> {
    return this.request<SystemStatus>('/status')
  }

  async checkConnection(): Promise<boolean> {
    try {
      await this.health()
      return true
    } catch {
      return false
    }
  }

  // ── Telephony ──────────────────────────────────────────────────────────────

  async call(target: string, sim?: string): Promise<CallResult> {
    const params = new URLSearchParams({ target })
    if (sim) params.append('sim', sim)
    return this.request<CallResult>(`/call?${params}`, { method: 'POST' })
  }

  async hangup(): Promise<{ status: string; output: string }> {
    return this.request(`/calls/hangup`, { method: 'POST' })
  }

  // ── USSD / Balance ─────────────────────────────────────────────────────────

  async balance(simId: string = 'SIM1'): Promise<BalanceResult> {
    const params = new URLSearchParams({ sim_id: simId })
    return this.request<BalanceResult>(`/ussd/balance?${params}`, { method: 'POST' })
  }

  // ── Voice Commands ─────────────────────────────────────────────────────────

  /** Send a text command through the voice command processor and get a response. */
  async processVoiceCommand(text: string, tools?: any[]): Promise<VoiceProcessResult> {
    return this.request<VoiceProcessResult>('/voice/process', {
      method: 'POST',
      body: JSON.stringify({ text, tools }),
    })
  }

  /** Start continuous microphone listening mode. */
  async startVoiceListening(): Promise<{ status: string }> {
    return this.request('/voice/listen/start', { method: 'POST' })
  }

  /** Stop continuous microphone listening mode. */
  async stopVoiceListening(): Promise<{ status: string }> {
    return this.request('/voice/listen/stop', { method: 'POST' })
  }

  /** Get current voice engine status. */
  async getVoiceStatus(): Promise<VoiceStatus> {
    return this.request<VoiceStatus>('/voice/status')
  }

  /** Get recent voice command history. */
  async getVoiceHistory(limit = 20): Promise<{ history: unknown[] }> {
    return this.request(`/voice/history?limit=${limit}`)
  }

  /** Get available voice command help. */
  async getVoiceHelp(): Promise<{ help: string[]; error?: string }> {
    return this.request('/voice/help')
  }
}

export const api = new JarvisAPI()