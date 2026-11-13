import { useEffect, useState } from 'react'
import { useJarvisStore } from './store'
import Sidebar from './components/Sidebar'
import Hologram from './components/Hologram'
import ChatPanel from './components/ChatPanel'
import DevicesPanel from './components/DevicesPanel'
import TasksPanel from './components/TasksPanel'
import ActivityPanel from './components/ActivityPanel'
import SettingsPanel from './components/SettingsPanel'
import { DeviceStatus, HologramState } from './types'
import { api } from './services/api'

const SECTION_LABELS: Record<string, string> = {
  home: 'Home',
  conversations: 'Conversations',
  tasks: 'Tasks',
  agents: 'Agents',
  memory: 'Memory',
  devices: 'Devices',
  integrations: 'Integrations',
  activity: 'Activity',
  settings: 'Settings',
}

export default function App() {
  const [mounted, setMounted] = useState(false)

  const {
    health,
    deviceStatus,
    sims,
    isListening,
    isSpeaking,
    isWorking,
    hologramState,
    setHealth,
    setDeviceStatus,
    setSims,
    setIsListening,
    setIsSpeaking,
    setIsWorking,
    setHologramState,
    setActiveSection,
    activeSection,
    notifications,
    addNotification,
  } = useJarvisStore()

  useEffect(() => {
    setMounted(true)
    initBackend()
  }, [])

  const initBackend = async () => {
    try {
      const [healthRes, simsRes] = await Promise.allSettled([api.health(), api.sims()])
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value)
      if (simsRes.status === 'fulfilled') setSims(simsRes.value)

      const deviceStatus = await detectDeviceStatus()
      setDeviceStatus(deviceStatus)
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

  const detectDeviceStatus = async (): Promise<DeviceStatus> => {
    try {
      const status = await api.status()
      const sims = await api.sims()
      const sim1Avail = !!(sims?.SIM1?.phone_number)
      const sim2Avail = !!(sims?.SIM2?.phone_number)
      return {
        windows: 'connected' as const,
        android: status.call_state ? ('connected' as const) : ('unknown' as const),
        adb: 'connected' as const,
        sim1: sim1Avail ? ('available' as const) : ('unavailable' as const),
        sim2: sim2Avail ? ('available' as const) : ('unavailable' as const),
        backend: 'online' as const,
        ai_service: 'online' as const,
      }
    } catch {
      return {
        windows: 'disconnected' as const,
        android: 'disconnected' as const,
        adb: 'disconnected' as const,
        sim1: 'unavailable' as const,
        sim2: 'unavailable' as const,
        backend: 'offline' as const,
        ai_service: 'offline' as const,
      }
    }
  }

  const hologramColors: Record<string, string> = {
    IDLE: '#4ade80',
    LISTENING: '#22d3ee',
    THINKING: '#fbbf24',
    SPEAKING: '#a78bfa',
    WORKING: '#ef4444',
    ERROR: '#f43f5e',
  }

  const sectionComponents: Record<string, React.ReactNode> = {
    home: <HomeSection />,
    conversations: <ChatPanel />,
    tasks: <TasksPanel />,
    devices: <DevicesPanel />,
    activity: <ActivityPanel />,
    settings: <SettingsPanel />,
    agents: <PlaceholderSection name="Agents" />,
    memory: <PlaceholderSection name="Memory" />,
    integrations: <PlaceholderSection name="Integrations" />,
  }

  return (
    <div id="app" className="h-full w-full overflow-hidden">
      <header className="flex items-center gap-4 px-6 border-b border-[var(--line)] bg-black/25">
        <h1 className="font-semibold text-[18px] tracking-[.02em]">Jarvis</h1>
        <small className="text-[var(--tx2)] text-[12px]">Personal AI assistant</small>
        <div className="pill ml-auto flex items-center gap-2 px-3 py-1 border border-[var(--line)] rounded-full text-[12px] text-[var(--tx2)]">
          <i className="dot w-2 h-2 rounded-full bg-[var(--c)] shadow-[0_0_10px_var(--c)] transition-all duration-600"></i>
          <span id="hs">{hologramState}</span>
        </div>
      </header>

      <Sidebar />

      <main className="min-width-0 flex flex-col overflow-hidden">
        {sectionComponents[activeSection] || <PlaceholderSection name="Home" />}
      </main>

      <aside className="border-l border-[var(--line)] p-5 overflow-auto bg-black/18">
        <SidePanel activeSection={activeSection} />
      </aside>

      <footer className="flex items-center justify-between px-6 border-t border-[var(--line)] bg-black/25 font-[var(--m)] text-[12px] text-[var(--mu)]">
        <span>Jarvis Desktop v1.0.0</span>
        <span id="bk">Backend: {deviceStatus?.backend === 'online' ? 'connected' : 'offline'}</span>
      </footer>
    </div>
  )
}

function SidePanel({ activeSection }: { activeSection: string }) {
  const { notifications, deviceStatus } = useJarvisStore()

  if (activeSection === 'home') {
    return (
      <>
        <h2 className="text-[15px] font-semibold mb-3.5">System overview</h2>
        {[
          ['Backend', deviceStatus?.backend === 'online' ? 'Online' : 'Offline', deviceStatus?.backend === 'online' ? '' : 'off'],
          ['Android link', 'Standby', 'off'],
          ['Voice interface', 'Ready', ''],
          ['SIM 1', deviceStatus?.sim1 === 'available' ? 'Available' : 'Unavailable', deviceStatus?.sim1 === 'available' ? '' : 'off'],
          ['SIM 2', deviceStatus?.sim2 === 'available' ? 'Available' : 'Unavailable', deviceStatus?.sim2 === 'available' ? '' : 'off'],
        ].map(([label, value, status], i) => (
          <div key={i} className="row flex justify-between items-center gap-2.5 py-2.5 border-b border-[var(--line)]">
            <span>{label}</span>
            <span className={`v font-[var(--m)] text-[12px] ${status === 'off' ? 'text-[var(--mu)]' : 'text-[var(--em)]'}`}>{value}</span>
          </div>
        ))}
        <h2 className="text-[15px] font-semibold mb-3.5 mt-[22px]">Quick actions</h2>
        {['Check SIM balance', 'Start conversation', 'View device status'].map((action, i) => (
          <div key={i} className="row flex justify-between items-center gap-2.5 py-2.5 border-b border-[var(--line)]">
            <button className="text-left w-full hover:text-[var(--em)] transition-colors">{action}</button>
          </div>
        ))}
      </>
    )
  }

  return (
    <>
      <h2 className="text-[15px] font-semibold mb-3.5 capitalize">{activeSection}</h2>
      <p className="text-[var(--tx2)]">Coming soon.</p>
    </>
  )
}

function HomeSection() {
  const { hologramState, setHologramState, setIsListening, setIsSpeaking } = useJarvisStore()

  const handleActivate = async () => {
    setHologramState('LISTENING')
    setIsListening(true)
    setTimeout(() => {
      setHologramState('THINKING')
      setIsListening(false)
      setTimeout(() => {
        setHologramState('SPEAKING')
        setIsSpeaking(true)
        setTimeout(() => {
          setHologramState('IDLE')
          setIsSpeaking(false)
        }, 2200)
      }, 1500)
    }, 1800)
  }

  return (
    <div className="flex-1 relative min-h-0 flex flex-col">
      <div id="stage" className="flex-1 relative min-h-0 cursor-grab">
        <Hologram state={hologramState} />
        <div id="cap" className="absolute left-6 top-5 pointer-events-none">
          <b id="cs" className="block text-[32px] font-light tracking-[.04em] text-[var(--c)] transition-colors duration-600 uppercase">{hologramState}</b>
          <span id="cm" className="font-[var(--m)] text-[12px] text-[var(--tx2)]">Hologram.glb · drag to rotate</span>
        </div>
      </div>

      <div className="ctl flex items-center justify-center gap-3 p-3.5 flex-wrap">
        <button
          id="go"
          onClick={handleActivate}
          className="px-[26px] py-[11px] rounded-full border border-[var(--c)] text-[var(--c)] bg-[var(--c)]/7 transition-all duration-300 hover:shadow-[0_0_28px_-4px_var(--c)]"
        >
          Activate voice
        </button>
        <div className="st flex gap-1">
          {['Idle', 'Listening', 'Thinking', 'Speaking', 'Working', 'Error'].map(s => (
            <button
              key={s}
              onClick={() => setHologramState(s.toUpperCase() as any)}
              className={`font-[var(--m)] text-[12px] px-2.5 py-1.5 rounded-md border transition-colors ${
                hologramState === s.toUpperCase()
                  ? 'text-[var(--tx)] border-[var(--c)]'
                  : 'text-[var(--tx2)] border-[var(--line)]'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function PlaceholderSection({ name }: { name: string }) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center p-12">
      <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-4">
        <span className="text-2xl">⚙️</span>
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{name}</h3>
      <p className="text-gray-400 text-sm max-w-md mx-auto">
        {name} section — coming soon. This area will be populated with dedicated functionality.
      </p>
    </div>
  )
}