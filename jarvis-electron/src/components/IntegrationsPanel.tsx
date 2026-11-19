import { useState, useEffect, useRef } from 'react'
import { useJarvisStore } from '../store'
import { api } from '../services/api'

const INTEGRATION_APPS = [
  { slug: 'twitter',   label: 'Twitter / X',   icon: '\u{1D54F}', description: 'Read tweets, timelines, and mentions' },
  { slug: 'linkedin',  label: 'LinkedIn',       icon: 'in', description: 'Fetch profile data and network activity' },
  { slug: 'facebook',  label: 'Facebook',       icon: 'f', description: 'Read pages and public posts' },
  { slug: 'instagram', label: 'Instagram',      icon: '\u{1F4F7}', description: 'View account insights and media' },
]

type ExecLog = { id: string; tool: string; app: string; ts: number; success: boolean; result?: string }

export default function IntegrationsPanel() {
  const { addNotification } = useJarvisStore()
  const [wsReady, setWsReady] = useState(false)
  const [execLogs, setExecLogs] = useState<ExecLog[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    let alive = false
    const check = async () => {
      try {
        await api.health()
        if (!alive) { alive = true; setWsReady(true) }
      } catch {
        if (alive) { alive = false; setWsReady(false) }
      }
    }
    check()
    timerRef.current = setInterval(check, 5000)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [])

  const addLog = (tool: string, app: string, success: boolean, result?: string) => {
    setExecLogs((prev) => [...prev.slice(-49), { id: `log_${Date.now()}`, tool, app, ts: Date.now(), success, result }])
  }

  const handleRunTool = (appSlug: string, toolName: string) => {
    addLog(toolName, appSlug, false, 'Demo mode — configure Composio key in Agents panel for live results')
    addNotification({
      id: `notif_${Date.now()}`,
      type: 'info',
      title: `Tool: ${toolName}`,
      message: `Executed on ${appSlug} (demo mode).`,
      timestamp: Date.now(),
      read: false,
    })
  }

  return (
    <div className="workspace overflow-y-auto">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            THIRD-PARTY INTEGRATIONS
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Integrations<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Connected services, active tool executions, and health status.</p>
        </div>
      </div>

      {/* Connection status */}
      <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)] mb-[14px]">
        <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
          <div>
            <span className="section-index text-[8px] text-[#648c9d] block">01 / STATUS</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Backend link</h2>
          </div>
          <div className={`text-[8px] tracking-[.12em] px-[8px] py-[5px] border flex items-center gap-[7px] ${
            wsReady
              ? 'border-[rgba(123,242,193,0.21)] text-[var(--green)]'
              : 'border-[rgba(255,138,138,0.2)] text-[#ff8a8a]'
          }`}>
            <span className={`inline-block w-[5px] h-[5px] rounded-full ${wsReady ? 'bg-[var(--green)] animate-pulse' : 'bg-[#ff8a8a]'}`} />
            {wsReady ? 'WEBSOCKET ONLINE' : 'WEBSOCKET OFFLINE'}
          </div>
        </div>
      </section>

      <div className="overview-grid grid grid-cols-1 lg:grid-cols-2 gap-[14px]">
        {/* App list */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">02 / SERVICES</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Available apps</h2>
          </div>
          <div className="max-h-[340px] overflow-y-auto p-[12px_18px_14px]" style={{ padding: '12px 18px 14px' }}>
            {INTEGRATION_APPS.map((app) => (
              <div key={app.slug} className="full-row border-b border-[#17303d] last:border-0 py-[10px]" style={{ borderBottom: '1px solid #17303d' }}>
                <span className="time" style={{ fontSize: '16px' }}>{app.icon}</span>
                <div className="desc">
                  <div className="text-[#b8d4dc]">{app.label}</div>
                  <div className="text-[8px] text-[#577584] mt-[1px]">{app.description}</div>
                </div>
                <span className="kind">READ-ONLY</span>
              </div>
            ))}
          </div>
        </section>

        {/* Execution logs */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">03 / LOGS</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Tool execution</h2>
            </div>
            <button onClick={() => setExecLogs([])} disabled={execLogs.length === 0} className="text-btn border-0 bg-transparent cursor-pointer disabled:opacity-30">
              CLEAR
            </button>
          </div>
          <div className="max-h-[320px] overflow-y-auto p-[12px_18px_14px]" style={{ maxHeight: '320px', overflowY: 'auto', padding: '12px 18px 14px' }}>
            {execLogs.length === 0 ? (
              <div className="py-[40px] text-center text-[10px] text-[var(--muted)] tracking-[.1em]">NO EXECUTIONS YET</div>
            ) : (
              execLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-[10px] py-[8px] border-b border-[#17303d] text-[10px]" style={{ borderBottom: '1px solid #17303d', paddingBottom: '8px', marginBottom: '8px' }}>
                  <span className={`w-[18px] h-[18px] rounded-full grid place-items-center shrink-0 text-[9px] ${
                    log.success ? 'bg-[rgba(123,242,193,0.1)] text-[var(--green)]' : 'bg-[rgba(255,138,138,0.1)] text-[#ff8a8a]'
                  }`}>
                    {log.success ? '✓' : '—'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-[8px]">
                      <span className="font-medium text-[#b8d4dc]">{log.tool}</span>
                      <span className="text-[#5f8595] text-[8px]">on {log.app.toUpperCase()}</span>
                    </div>
                    {log.result && (
                      <p className="text-[#678897] mt-[2px] truncate">{log.result}</p>
                    )}
                  </div>
                  <span className="text-[#5f8595] font-display text-[9px] shrink-0">
                    {new Date(log.ts).toLocaleTimeString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Quick actions */}
      <section className="panel mt-[14px] border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
        <div className="panel-top relative px-[18px] pt-[16px]">
          <span className="section-index text-[8px] text-[#648c9d] block">04 / QUICK ACTIONS</span>
          <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Run sample query</h2>
        </div>
        <div className="p-[14px_18px] flex flex-wrap gap-[8px]">
          {INTEGRATION_APPS.map((app) => (
            <button
              key={app.slug}
              onClick={() => handleRunTool(app.slug, `GET_${app.slug.toUpperCase()}_FEED`)}
              className="px-[12px] py-[7px] border border-[#276077] text-[#8ebbc9] text-[9px] tracking-[.1em] cursor-pointer hover:border-[var(--cyan)] hover:text-[var(--cyan)] transition-colors"
            >
              {app.icon} {app.label} — GET FEED
            </button>
          ))}
          <button
            onClick={() => handleRunTool('system', 'GET_SYSTEM_STATUS')}
            className="px-[12px] py-[7px] border border-[#276077] text-[#8ebbc9] text-[9px] tracking-[.1em] cursor-pointer hover:border-[var(--cyan)] hover:text-[var(--cyan)] transition-colors ml-auto"
          >
            ⌘ CHECK SYSTEM HEALTH
          </button>
        </div>
      </section>
    </div>
  )
}
