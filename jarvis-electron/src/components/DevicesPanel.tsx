import { useEffect, useState } from 'react'
import { useJarvisStore } from '../store'
import { api } from '../services/api'
import { DeviceStatus } from '../types'

export default function DevicesPanel() {
  const [status, setStatus] = useState<DeviceStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const { setDeviceStatus, setSims } = useJarvisStore()

  useEffect(() => {
    const load = async () => {
      try {
        const [simRes] = await Promise.allSettled([api.sims()])
        if (simRes.status === 'fulfilled') {
          setSims(simRes.value)
        }

        const sims = simRes.status === 'fulfilled' ? simRes.value : null
        const sim1Avail = !!(sims?.SIM1?.phone_number)
        const sim2Avail = !!(sims?.SIM2?.phone_number)

        const deviceStatus: DeviceStatus = {
          windows: 'connected',
          android: 'unknown',
          adb: 'connected',
          sim1: sim1Avail ? 'available' : 'unavailable',
          sim2: sim2Avail ? 'available' : 'unavailable',
          backend: 'online',
          ai_service: 'online',
        }

        setStatus(deviceStatus)
        setDeviceStatus(deviceStatus)
      } catch (err) {
        console.error('Failed to load device status:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const statusColors: Record<string, string> = {
    connected: 'text-emerald-400',
    disconnected: 'text-red-400',
    unknown: 'text-gray-400',
    available: 'text-emerald-400',
    unavailable: 'text-gray-400',
    online: 'text-emerald-400',
    offline: 'text-red-400',
  }

  const handleCheckBalance = async (simId: string) => {
    try {
      const result = await api.balance(simId)
      alert(`Balance for ${simId}: ${result.message}`)
    } catch (err: any) {
      alert(`Error: ${err.message || 'Failed to check balance'}`)
    }
  }

  const handleInitiateCall = async () => {
    const target = prompt('Enter phone number to call:')
    if (target) {
      try {
        await api.call(target)
        alert(`Call initiated to ${target}`)
      } catch (err: any) {
        alert(`Error: ${err.message || 'Failed to initiate call'}`)
      }
    }
  }

  const handleHangup = async () => {
    try {
      await api.hangup()
      alert('Call terminated')
    } catch (err: any) {
      alert(`Error: ${err.message || 'Failed to hang up'}`)
    }
  }

  return (
    <div className="h-full flex flex-col bg-black/30 rounded-2xl border border-white/10 overflow-hidden">
      <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-black/20">
        <h3 className="text-sm font-semibold text-white">Device Status</h3>
        <button
          onClick={() => window.location.reload()}
          className="w-8 h-8 rounded bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors text-xs"
        >
          ↻
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-40 text-gray-400">
            <div className="w-6 h-6 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin mb-2"></div>
            <p>Loading device status...</p>
          </div>
        ) : (
          <>
            <div className="bg-black/20 rounded-xl border border-white/10 p-5">
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-4">Connection Status</h4>
              <div className="space-y-3">
                {[
                  { label: 'Windows Backend', key: 'windows' },
                  { label: 'Android Device', key: 'android' },
                  { label: 'ADB Bridge', key: 'adb' },
                  { label: 'AI Service', key: 'ai_service' },
                ].map((item) => {
                  const val = status?.[item.key as keyof DeviceStatus]
                  return (
                    <div
                      key={item.key}
                      className="flex items-center justify-between py-1.5 border-b border-white/5 last:border-0"
                    >
                      <span className="text-sm text-gray-300">{item.label}</span>
                      <span className={`text-xs font-mono ${statusColors[val || 'unknown']}`}>
                        {val ? val.charAt(0).toUpperCase() + val.slice(1) : 'Unknown'}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="bg-black/20 rounded-xl border border-white/10 p-5">
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-4">SIM Cards</h4>
              <div className="space-y-4">
                {[1, 2].map((n) => {
                  const key = `sim${n}` as keyof DeviceStatus
                  const simData = {
                    phone_number: null,
                    network: null,
                    ussd_code: null,
                    sub_id: null,
                  }
                  const isAvailable = status?.[key] === 'available'
                  return (
                    <div
                      key={key}
                      className={`flex items-center justify-between py-3 px-3 rounded-lg border ${
                        isAvailable ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div className={`w-2.5 h-2.5 rounded-full ${isAvailable ? 'bg-emerald-500' : 'bg-gray-600'}`}></div>
                        <div>
                          <div className="text-sm font-medium text-white">SIM {n}</div>
                          <div className="text-xs text-gray-400">
                            {simData.phone_number || 'Not configured'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-mono capitalize ${isAvailable ? 'text-emerald-400' : 'text-gray-500'}`}>
                          {isAvailable ? 'Available' : 'Unavailable'}
                        </span>
                        <button
                          onClick={() => handleCheckBalance(`SIM${n}`)}
                          className="w-8 h-8 rounded bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-emerald-400 transition-colors text-xs"
                        >
                          💰
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={handleInitiateCall}
                  className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-colors"
                >
                  📞 Initiate Call
                </button>
                <button
                  onClick={handleHangup}
                  className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-red-400 transition-colors"
                >
                  📴 Hang Up
                </button>
              </div>
            </div>

            <div className="bg-black/20 rounded-xl border border-white/10 p-5">
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-4">USSD Balance</h4>
              <p className="text-xs text-gray-500 mb-3">
                Check SIM balance using the configured USSD codes (*804# / *704#)
              </p>
              <div className="space-y-3">
                {[1, 2].map((n) => (
                  <button
                    key={n}
                    onClick={() => handleCheckBalance(`SIM${n}`)}
                    className={`w-full flex items-center justify-between px-4 py-2.5 rounded-lg text-sm transition-colors ${
                      status?.[`sim${n}` as keyof DeviceStatus] === 'available'
                        ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20'
                        : 'bg-white/5 border border-white/10 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    <span>Check SIM {n} Balance</span>
                    <span className="text-xs">{`*${n === 1 ? '804' : '704'}#`}</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}