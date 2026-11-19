import { useEffect, useState } from 'react'
import { useJarvisStore } from './store'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import DevicesPanel from './components/DevicesPanel'
import TasksPanel from './components/TasksPanel'
import ActivityPanel from './components/ActivityPanel'
import SettingsPanel from './components/SettingsPanel'
import HomeDashboardPanel from './components/dashboard/HomeDashboardPanel'
import AgentsPanel from './components/AgentsPanel'
import IntegrationsPanel from './components/IntegrationsPanel'
import KarionPanel from './components/KarionPanel'
import { api } from './services/api'
import './styles/global.css'

// Lazy-load Three.js hologram only when needed
let HologramComponent: any = null
const loadHologram = async () => {
  if (!HologramComponent) {
    const mod = await import('./components/Hologram')
    HologramComponent = mod.default
  }
  return HologramComponent
}

// Placeholder panels for sections not yet fully implemented
function PlaceholderSection({ name }: { name: string }) {
  return (
    <div className="panel" style={{ padding: '24px' }}>
      <div className="assistant-orb" style={{ marginBottom: '16px' }}>
        <span />
      </div>
      <h2 className="text-surface-100 mb-2" style={{ fontSize: '18px', fontFamily: 'var(--display)', fontWeight: 500, letterSpacing: '.035em' }}>{name}</h2>
      <p className="text-sm" style={{ color: '#9bbac6', maxWidth: '440px' }}>
        {name} section — coming soon. This area will be populated with dedicated functionality.
      </p>
    </div>
  )
}

// Section renderer map
const sectionComponents: Record<string, React.ReactNode> = {
  home: <HomeDashboardPanel />,
  conversations: <ChatPanel />,
  tasks: <TasksPanel />,
  devices: <DevicesPanel />,
  activity: <ActivityPanel />,
  settings: <SettingsPanel />,
  agents: <AgentsPanel />,
  memory: <PlaceholderSection name="Memory" />,
  integrations: <IntegrationsPanel />,
  'mobile-bridge': <KarionPanel />,
}

export default function App() {
  const activeSection = useJarvisStore((s) => s.activeSection)
  const { health, deviceStatus, sims, hologramState, setHealth, setDeviceStatus, setSims, setActiveSection, notifications, addNotification } = useJarvisStore()

  // Backend launch state
  const [backendRunning, setBackendRunning] = useState(false)
  const [launching, setLaunching] = useState(false)

  useEffect(() => {
    // Check if backend is running via preload bridge
    if (typeof window !== 'undefined' && (window as any).jarvisBackend) {
      ;(window as any).jarvisBackend.isRunning().then((res: { running: boolean }) => {
        setBackendRunning(res.running)
      }).catch(() => {})

      const cleanup = (window as any).jarvisBackend.onStatusChange((status: string) => {
        setBackendRunning(status === 'running')
      })
      return cleanup
    }
  }, [])

  const handleLaunchBackend = async () => {
    if (launching || !window.jarvisBackend) return
    setLaunching(true)
    try {
      await window.jarvisBackend.launchBackend()
      setBackendRunning(true)
    } catch {} finally {
      setLaunching(false)
    }
  }

  // Real-time clock
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  const formattedTime = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })

  // Boot greeting after backend initializes
  useEffect(() => {
    initBackend()
    setTimeout(async () => {
      try {
        const balance = await api.balance()
        // Balance already handled in store via USSD flow
      } catch {}
      const hour = new Date().getHours()
      const greeting = hour < 6 ? 'Good night, sir.' : hour < 12 ? 'Good morning, sir.' : hour < 18 ? 'Good afternoon, sir.' : 'Good evening, sir.'
      // Note: api.call() requires a phone target, not free text
      // Greeting sent as log for now; use ChatPanel for actual commands
      console.log('[JARVIS]', greeting)
    }, 800)
  }, [])

  const initBackend = async () => {
    try {
      const [healthRes, simsRes] = await Promise.allSettled([api.health(), api.sims()])
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value)
      if (simsRes.status === 'fulfilled') setSims(simsRes.value)
      const ds = await detectDeviceStatus()
      setDeviceStatus(ds)
    } catch (err) {
      console.error('Failed to initialize backend:', err)
      addNotification({
        id: `notif_${Date.now()}`,
        type: 'error',
        title: 'Backend Unreachable',
        message: 'Jarvis backend is not running. Start `python api/main.py` on port 8000.',
        timestamp: Date.now(),
        read: false,
      })
    }
  }

  const detectDeviceStatus = async (): Promise<any> => {
    try {
      const status = await api.status()
      const simsData = await api.sims()
      const sim1Avail = !!(simsData?.SIM1?.phone_number)
      const sim2Avail = !!(simsData?.SIM2?.phone_number)
      return {
        windows: 'connected',
        android: status.call_state ? 'connected' : 'unknown',
        adb: 'connected',
        sim1: sim1Avail ? 'available' : 'unavailable',
        sim2: sim2Avail ? 'available' : 'unavailable',
        backend: 'online',
        ai_service: 'online',
      }
    } catch {
      return {
        windows: 'disconnected',
        android: 'disconnected',
        adb: 'disconnected',
        sim1: 'unavailable',
        sim2: 'unavailable',
        backend: 'offline',
        ai_service: 'offline',
      }
    }
  }

  const sectionLabel = (activeSection.charAt(0).toUpperCase() + activeSection.slice(1))

  return (
    <>
      {/* Ambient background layers — matched source exactly */}
      <div className="ambient" />
      <div className="grain" />

      {/* Fixed sidebar — positioned by CSS, not grid */}
      <Sidebar />

      {/* Main content area */}
      <div className="main-area">
        {/* Top bar */}
        <header className="topbar">
          <p className="crumb">
            JARVIS <i>/</i> <b>{sectionLabel}</b>
          </p>
          <div className="top-actions">
            <div className="top-status">
              <span className="pulse" />
              ONLINE
            </div>
            {[
              { label: 'System', icon: '◈' },
              { label: 'Net', icon: '⌁' },
              { label: 'Log', icon: '▤' },
            ].map(({ label, icon }) => (
              <button key={label} className="icon-btn" title={label}>{icon}</button>
            ))}
            <div className="avatar">J</div>
          </div>
        </header>

        {/* Page content */}
        <div className="workspace">
          {sectionComponents[activeSection]}
        </div>

        {/* Footer line with live clock */}
        <div className="footerline">
          <span>KARION v2.2.0 — Stark Industries UI Framework</span>
          <div className="flex items-center gap-[10px]">
            {!backendRunning && (
              <button
                onClick={handleLaunchBackend}
                disabled={launching}
                className="text-[8px] tracking-[.1em] px-[6px] py-[2px] border border-[var(--cyan)] text-[var(--cyan)] hover:bg-[var(--cyan)] hover:text-[#04111a] transition-colors"
              >
                {launching ? 'LAUNCHING…' : 'LAUNCH BACKEND'}
              </button>
            )}
            <span className={`w-[6px] h-[6px] rounded-full ${backendRunning ? 'bg-[var(--green)]' : 'bg-[#ff8a8a]'}`} />
            <span id="clock">{formattedTime}</span>
          </div>
        </div>
      </div>

      {/* Command Dock — centered below viewport using source calc */}
      <CommandDock />

      {/* Toast notification container */}
      <div id="toast"></div>
    </>
  )
}

/** Bottom command input dock — matches source.calc formula exactly */
function CommandDock() {
  const { activeSection } = useJarvisStore()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const input = form.querySelector('input') as HTMLInputElement
    const value = input?.value.trim()
    if (!value) return
    api.processVoiceCommand(value).catch(() => {})
    input!.value = ''
  }

  return (
    <div className="command-dock">
      <span className="command-mark">⌘</span>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask KARION or enter a command…"
          autoComplete="off"
        />
      </form>
      <kbd>ENTER ↵</kbd>
      <button aria-label="Send command">↑</button>
    </div>
  )
}