const API_BASE = 'http://localhost:8000'

import { BackendHealth, SIMsConfig, CallResult, BalanceResult, SystemStatus } from '../types'

export class JarvisAPI {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  async health(): Promise<BackendHealth> {
    return this.request<BackendHealth>('/health')
  }

  async sims(): Promise<SIMsConfig> {
    return this.request<SIMsConfig>('/sims')
  }

  async call(target: string, sim?: string): Promise<CallResult> {
    const params = new URLSearchParams({ target })
    if (sim) params.append('sim', sim)
    return this.request<CallResult>(`/call?${params}`, { method: 'POST' })
  }

  async hangup(): Promise<{ status: string; output: string }> {
    return this.request(`/calls/hangup`, { method: 'POST' })
  }

  async balance(simId: string = 'SIM1'): Promise<BalanceResult> {
    const params = new URLSearchParams({ sim_id: simId })
    return this.request<BalanceResult>(`/ussd/balance?${params}`, { method: 'POST' })
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
}

export const api = new JarvisAPI()