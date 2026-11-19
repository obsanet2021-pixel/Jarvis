import { useJarvisStore } from '../store'

const NAV_ITEMS = [
  { id: 'home', label: 'Overview', icon: '◈', kbd: '01' },
  { id: 'activity', label: 'Activity', icon: '⌁', kbd: '02' },
  { id: 'tasks', label: 'Directives', icon: '▤', kbd: '03' },
  { id: 'devices', label: 'Hardware', icon: '⌘', kbd: '04' },
  { id: 'memory', label: 'Memory', icon: '◉', kbd: '05' },
  { id: 'conversations', label: 'Conversations', icon: '◆', kbd: '06' },
  { id: 'agents', label: 'Agents', icon: '◇', kbd: '07' },
  { id: 'integrations', label: 'Integrations', icon: '⧫', kbd: '08' },
  { id: 'settings', label: 'Settings', icon: '◎', kbd: '09' },
  { id: 'mobile-bridge', label: 'Mobile Bridge', icon: '☎', kbd: '10' },
]

export default function Sidebar() {
  const activeSection = useJarvisStore((s) => s.activeSection)
  const setActiveSection = useJarvisStore((s) => s.setActiveSection)

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div>
          <b>J.A.R.V.I.S.</b>
          <small>PERSONAL INTELLIGENCE</small>
        </div>
      </div>

      <div className="nav-label">WORKSPACE</div>

      <nav id="nav">
        {NAV_ITEMS.map((item) => {
          const isActive = activeSection === item.id
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              data-page={item.id}
              onClick={() => setActiveSection(item.id)}
            >
              <i>{item.icon}</i>
              {item.label}
              <kbd>{item.kbd}</kbd>
            </button>
          )
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="connection">
          <span className="pulse"></span>
          <div>
            <b>CORE LINK ACTIVE</b>
            <small>Encrypted local session</small>
          </div>
        </div>
        <div className="version">
          JARVIS INTERFACE <span>v1.0.0</span>
        </div>
      </div>
    </aside>
  )
}
