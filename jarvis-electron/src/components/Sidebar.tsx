import { useJarvisStore } from '../store'
import { Link } from 'react-router-dom'

const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: '🏠' },
  { id: 'conversations', label: 'Conversations', icon: '💬' },
  { id: 'tasks', label: 'Tasks', icon: '✓' },
  { id: 'agents', label: 'Agents', icon: '🤖' },
  { id: 'memory', label: 'Memory', icon: '🧠' },
  { id: 'devices', label: 'Devices', icon: '📱' },
  { id: 'integrations', label: 'Integrations', icon: '🔗' },
  { id: 'activity', label: 'Activity', icon: '📋' },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
]

export default function Sidebar() {
  const {
    activeSection,
    setActiveSection,
  } = useJarvisStore()

  return (
    <nav id="nav" className="p-4 flex flex-col gap-0.5 overflow-auto border-r border-[var(--line)]">
      {NAV_ITEMS.map((item) => {
        const isActive = activeSection === item.id
        return (
          <button
            key={item.id}
            onClick={() => setActiveSection(item.id)}
            className={`text-left px-3 py-2 rounded-lg transition-colors border border-transparent ${
              isActive
                ? 'text-[var(--em)] bg-[var(--em)]/8 border-[var(--em)]/22'
                : 'text-[var(--tx2)] hover:bg-white/4 hover:text-[var(--tx)]'
            }`}
          >
            {item.label}
          </button>
        )
      })}
    </nav>
  )
}