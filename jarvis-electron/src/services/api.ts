import {
  BackendHealth,
  SIMsConfig,
  CallResult,
  BalanceResult,
  SystemStatus,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
const LLM_KEY_STORAGE_KEY = 'jarvis_llm_api_key'
const AUTH_TOKEN_STORAGE_KEY = 'jarvis_auth_token'
const TOKEN_PROMPTED_KEY = 'jarvis_token_prompted'

function loadApiKey(): string {
  try {
    return localStorage.getItem(LLM_KEY_STORAGE_KEY) || ''
  } catch {
    return ''
  }
}

function loadAuthToken(): string {
  try {
    return localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || ''
  } catch {
    return ''
  }
}

/** Prompt the user for the auth token once; store it in localStorage. */
async function promptAuthToken(): Promise<string | null> {
  if (localStorage.getItem(TOKEN_PROMPTED_KEY)) return null
  const val = window.prompt(
    'JARVIS requires an authentication token.\n\nOpen http://127.0.0.1:8000/api/health or check your .env file for the value of JARVIS_API_TOKEN, then paste it below.'
  )
  if (val === null) return null // cancelled
  const trimmed = val.trim()
  if (!trimmed) return null
  localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, trimmed)
  localStorage.setItem(TOKEN_PROMPTED_KEY, '1')
  return trimmed
}

let _promptPending: Promise<string | null> | null = null

function ensureTokenPrompt(): Promise<string | null> {
  if (!_promptPending) {
    _promptPending = promptAuthToken().finally(() => { _promptPending = null })
  }
  return _promptPending
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
    let apiKey = loadApiKey()
    let authToken = loadAuthToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`
    }
    if (authToken) {
      headers['X-Jarvis-Auth'] = authToken
    }

    let response = await fetch(url, {
      ...options,
      headers,
    })

    // On 401 without a stored token, prompt once and retry
    if (!response.ok && response.status === 401 && !authToken) {
      const refreshed = await ensureTokenPrompt()
      if (!refreshed) throw new Error('Authentication token not provided')
      authToken = refreshed
      headers['X-Jarvis-Auth'] = authToken
      response = await fetch(url, {
        ...options,
        headers,
      })
    }

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  /** Create a WebSocket connection to the bridge server with auth token via query param. */
  connectWebSocket(onMessage: (data: unknown) => void, onOpen?: () => void): () => void {
    const token = loadAuthToken()
    const wsUrl = `${API_BASE.replace('http://', 'ws://').replace('https://', 'wss://')}/ws${token ? `?token=${encodeURIComponent(token)}` : ''}`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (e) => {
      try {
        onMessage(JSON.parse(e.data))
      } catch {
        onMessage(e.data)
      }
    }
    ws.onopen = () => onOpen?.()

    // Return cleanup function
    return () => ws.close()
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
