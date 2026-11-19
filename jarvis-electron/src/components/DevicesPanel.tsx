import { useEffect, useState } from 'react'
import { useJarvisStore } from '../store'
import { api } from '../services/api'
import { DeviceStatus } from '../types'

export default function DevicesPanel() {
  const [status, setStatus] = useState<DeviceStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const { setDeviceStatus, setSims, addNotification } = useJarvisStore()

  useEffect(() => {
    const load = async () => {
      try {
        const [simRes] = await Promise.allSettled([api.sims()])
        if (simRes.status === 'fulfilled') setSims(simRes.value)
        const sims = simRes.status === 'fulfilled' ? simRes.value : null
        const deviceStatus: DeviceStatus = {
          windows: 'connected', android: 'unknown', adb: 'connected',
          sim1: !!(sims?.SIM1?.phone_number) ? 'available' : 'unavailable',
          sim2: !!(sims?.SIM2?.phone_number) ? 'available' : 'unavailable',
          backend: 'online', ai_service: 'online',
        }
        setStatus(deviceStatus)
        setDeviceStatus(deviceStatus)
      } catch (err) { console.error(err) } finally { setLoading(false) }
    }
    load()
  }, [])

  const handleCheckBalance = async (simId: string) => {
    try {
      const result = await api.balance(simId)
      addNotification({
        id: `notif_${Date.now()}`,
        type: 'success',
        title: 'Balance Check',
        message: `${simId}: ${result.message}`,
        timestamp: Date.now(),
        read: false,
      })
    } catch (err: any) {
      addNotification({
        id: `notif_${Date.now()}`,
        type: 'error',
        title: 'Balance Error',
        message: err.message || 'Failed to check balance',
        timestamp: Date.now(),
        read: false,
      })
    }
  }

  const statusOk = (val?: string) => !!val && ['connected', 'available', 'online'].includes(val)

  return (
    <div className="workspace">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            HARDWARE STATUS
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Hardware<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Connected devices and cellular integration status.</p>
        </div>
      </div>

      <div className="device-grid grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-[14px]">
        {[
          { label: 'Windows Backend', key: 'windows' as const, icon: '⊞' },
          { label: 'Android Device', key: 'android' as const, icon: '📱' },
          { label: 'ADB Bridge', key: 'adb' as const, icon: '↕' },
          { label: 'AI Service', key: 'ai_service' as const, icon: '⌘' },
          { label: 'SIM 1', key: 'sim1' as const, icon: '💳' },
          { label: 'SIM 2', key: 'sim2' as const, icon: '💳' },
        ].map(({ label, key, icon }) => {
          const val = status?.[key]
          const ok = statusOk(val)
          return (
            <section key={key} className="panel device-card border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
              <div className="panel-top relative px-[18px] pt-[16px]">
                <span className="section-index text-[8px] text-[#648c9d] block">{icon}</span>
                <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">{label}</h2>
              </div>
              <div className="p-[14px_18px]">
                <div className={`text-[10px] tracking-[.1em] ${ok ? 'text-[var(--green)]' : 'text-[#ff8a8a]'}`} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span className="dot" style={{ background: ok ? 'var(--green)' : '#ff8a8a', boxShadow: `0 0 7px ${ok ? 'var(--green)' : '#ff8a8a'}` }}></span>
                  {(val || 'unknown').toUpperCase()}
                </div>
              </div>
              {key.startsWith('sim') && (
                <div className="mx-[18px] pb-[14px] border-t border-[var(--line)] pt-[10px]">
                  <button onClick={() => handleCheckBalance(key.toUpperCase())} className="text-btn uppercase">CHECK BALANCE</button>
                </div>
              )}
            </section>
          )
        })}
      </div>

      {loading && (
        <div className="mt-[14px] panel p-[40px] border border-[var(--line)] text-center text-[var(--muted)] text-[10px] tracking-[.1em]">
          <div className="w-[24px] h-[24px] border-2 border-[var(--cyan)] border-t-transparent animate-spin rounded-full mx-auto mb-3"></div>
          SCANNING DEVICES...
        </div>
      )}
    </div>
  )
}
