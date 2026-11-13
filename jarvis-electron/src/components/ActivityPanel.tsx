import { useJarvisStore } from '../store'
import { Notification } from '../types'

export default function ActivityPanel() {
  const { notifications, markNotificationRead, clearNotifications } = useJarvisStore()

  return (
    <div className="h-full flex flex-col bg-black/30 rounded-2xl border border-white/10 overflow-hidden">
      <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-black/20">
        <h3 className="text-sm font-semibold text-white">Activity & Notifications</h3>
        <button
          onClick={clearNotifications}
          className="text-[10px] text-gray-500 hover:text-white transition-colors uppercase tracking-wider"
          disabled={notifications.length === 0}
        >
          Clear All
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-3">
        {notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-center text-gray-500">
            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3 text-xl">📭</div>
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          <div className="space-y-3">
            {notifications.map((notif) => (
              <div
                key={notif.id}
                className={`flex items-start gap-3 p-3 rounded-lg border ${
                  notif.read ? 'border-white/5 bg-white/5' : 'border-white/10 bg-white/3'
                }`}
              >
                <div className={`w-8 h-8 rounded flex shrink-0 items-center justify-center flex-shrink-0 ${
                  notif.type === 'error'
                    ? 'bg-red-500/20 text-red-400'
                    : notif.type === 'warning'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : notif.type === 'success'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-cyan-500/20 text-cyan-400'
                }`}>
                  {notif.type === 'error' ? '⚠️' : notif.type === 'warning' ? '⚡' : notif.type === 'success' ? '✅' : 'ℹ️'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-white">{notif.title}</span>
                    <span className="text-[10px] text-gray-500">{new Date(notif.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">{notif.message}</p>
                </div>
                <button
                  onClick={() => markNotificationRead(notif.id)}
                  className="text-[10px] text-gray-500 hover:text-white transition-colors"
                >
                  {notif.read ? 'Read' : 'Mark Read'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}