import { useState, useEffect } from 'react'
import { useJarvisStore } from '../store'

export default function KarionPanel() {
  const [tasks, setTasks] = useState<any[]>([])
  const [focusSessions, setFocusSessions] = useState<any[]>([])
  const [callRequests, setCallRequests] = useState<any[]>([])
  const [karionState, setKarionState] = useState<{ connected: boolean; pairing?: any; lastError?: string | null }>({ connected: false })
  const [loading, setLoading] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [agentScript, setAgentScript] = useState('Call recipient and state that urgent task verification is required.')
  const [ussdCode, setUssdCode] = useState('')
  const [statusMsg, setStatusMsg] = useState('')

  const checkKarion = async () => {
    if (window.karionAPI) {
      try {
        const state = (await window.karionAPI.state()).data
        setKarionState(state)
        if (state.connected && state.pairing) {
          const uid = state.pairing.uid
          const [tRes, fRes, cRes] = await Promise.all([
            window.karionAPI.invoke('tasks', uid),
            window.karionAPI.invoke('focus-sessions', uid),
            window.karionAPI.invoke('call-requests', uid),
          ])
          if (tRes.ok) setTasks(tRes.data)
          if (fRes.ok) setFocusSessions(fRes.data)
          if (cRes.ok) setCallRequests(cRes.data)
        }
      } catch (e: any) {
        setKarionState({ connected: false, lastError: e.message })
      }
    }
  }

  useEffect(() => {
    checkKarion()
    const interval = setInterval(checkKarion, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleDispatch = async (command: string) => {
    if (!karionState.pairing) return
    setLoading(true)
    setStatusMsg('')
    try {
      const uid = karionState.pairing.uid
      const res = await window.karionAPI?.invoke('dispatch-call', uid, command, phoneNumber, agentScript, ussdCode || undefined)
      if (res?.ok) {
        setStatusMsg(`✓ Call request dispatched successfully (${command})`)
        checkKarion()
      } else {
        setStatusMsg(`Error: ${res?.error || 'Failed to dispatch'}`)
      }
    } catch (e: any) {
      setStatusMsg(`Error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleHangUp = async () => {
    if (!karionState.pairing) return
    setLoading(true)
    try {
      const uid = karionState.pairing.uid
      const res = await window.karionAPI?.invoke('hang-up', uid)
      if (res?.ok) {
        setStatusMsg('✓ Hang up command sent')
        checkKarion()
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCheckBalance = async () => {
    if (!karionState.pairing) return
    setLoading(true)
    try {
      const uid = karionState.pairing.uid
      const res = await window.karionAPI?.invoke('check-balance', uid, ussdCode || '*123#')
      if (res?.ok) {
        setStatusMsg('✓ Balance check request dispatched')
        checkKarion()
      }
    } finally {
      setLoading(false)
    }
  }

  const handleApproveTask = async (taskId: string) => {
    if (!karionState.pairing) return
    try {
      const uid = karionState.pairing.uid
      const res = await window.karionAPI?.invoke('approve-task', uid, taskId, 'Workstation-PC')
      if (res?.ok) {
        setStatusMsg('✓ Task verified & approved from PC')
        checkKarion()
      }
    } catch (e: any) {
      setStatusMsg(`Error approving task: ${e.message}`)
    }
  }

  const handleToggleFocusLock = async (armed: boolean) => {
    if (!karionState.pairing) return
    try {
      const uid = karionState.pairing.uid
      const res = await window.karionAPI?.invoke('set-focus-lock', uid, armed)
      if (res?.ok) {
        setStatusMsg(`✓ Focus lock ${armed ? 'armed' : 'disarmed'}`)
        checkKarion()
      }
    } catch (e: any) {
      setStatusMsg(`Error setting focus lock: ${e.message}`)
    }
  }

  const uid = karionState.pairing?.uid || 'Not paired'
  const deviceName = karionState.pairing?.deviceName || 'None'

  return (
    <div className="workspace overflow-y-auto">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            KARION MOBILE PROTOCOL BRIDGE
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Mobile Bridge<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Android phone dialer control, agent script dispatch, and E2EE task synchronization.</p>
        </div>
      </div>

      <div className="overview-grid grid grid-cols-1 lg:grid-cols-3 gap-[14px]">
        {/* Connection Status Card */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">01 / LINK</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Bridge connection</h2>
          </div>
          <div className="p-[14px_18px] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-[#b8d4dc]">Status</span>
              <span className={`text-[10px] font-mono px-[8px] py-[2px] border ${karionState.connected ? 'border-[var(--green)] text-[var(--green)] bg-[rgba(123,242,193,0.08)]' : 'border-[#ff8a8a] text-[#ff8a8a] bg-[rgba(255,138,138,0.08)]'}`}>
                {karionState.connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-[#b8d4dc]">Operator UID</span>
              <span className="text-[10px] font-mono text-[var(--cyan)] truncate max-w-[180px]" title={uid}>{uid}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-[#b8d4dc]">Device Name</span>
              <span className="text-[10px] font-mono text-[#e4f6fa]">{deviceName}</span>
            </div>
            {karionState.lastError && (
              <div className="text-[9px] text-[#ff8a8a] bg-[rgba(255,138,138,0.06)] p-[6px] border border-[rgba(255,138,138,0.2)]">
                Error: {karionState.lastError}
              </div>
            )}
            <div className="text-[9px] text-[#577584] pt-[4px]">
              Pairing keys and Firestore service credentials are configured in Settings.
            </div>
          </div>
        </section>

        {/* Phone Dialer & Agent Script Control */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)] lg:col-span-2">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">02 / CALLS</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Android phone & agent control</h2>
          </div>
          <div className="p-[14px_18px] space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] text-[#b8d4dc] block mb-[4px]">Phone Number</label>
                <input
                  type="text"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+1 (555) 019-2834"
                  className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[6px] text-[10px] text-[var(--ice)] font-mono outline-none focus:border-[var(--cyan)]"
                />
              </div>
              <div>
                <label className="text-[10px] text-[#b8d4dc] block mb-[4px]">USSD / Quick Code</label>
                <input
                  type="text"
                  value={ussdCode}
                  onChange={(e) => setUssdCode(e.target.value)}
                  placeholder="*123#"
                  className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[6px] text-[10px] text-[var(--ice)] font-mono outline-none focus:border-[var(--cyan)]"
                />
              </div>
            </div>
            <div>
              <label className="text-[10px] text-[#b8d4dc] block mb-[4px]">Voice Agent Script (Context Prompt)</label>
              <textarea
                value={agentScript}
                onChange={(e) => setAgentScript(e.target.value)}
                rows={2}
                className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[6px] text-[10px] text-[var(--ice)] font-mono outline-none focus:border-[var(--cyan)] resize-none"
              />
            </div>
            <div className="flex flex-wrap gap-2 pt-[2px]">
              <button
                onClick={() => handleDispatch('INITIATE_CALL')}
                disabled={loading || !phoneNumber || !karionState.connected}
                className="px-[12px] py-[7px] bg-[rgba(112,169,187,0.15)] border border-[var(--cyan)] text-[var(--cyan)] text-[10px] tracking-[.08em] hover:bg-[var(--cyan)] hover:text-[#04111a] transition-colors disabled:opacity-40"
              >
                DIAL CALL
              </button>
              <button
                onClick={() => handleDispatch('VOICE_AGENT_TURN')}
                disabled={loading || !phoneNumber || !karionState.connected}
                className="px-[12px] py-[7px] bg-[rgba(112,169,187,0.15)] border border-[var(--cyan)] text-[var(--cyan)] text-[10px] tracking-[.08em] hover:bg-[var(--cyan)] hover:text-[#04111a] transition-colors disabled:opacity-40"
              >
                DISPATCH AGENT SCRIPT
              </button>
              <button
                onClick={handleCheckBalance}
                disabled={loading || !karionState.connected}
                className="px-[12px] py-[7px] bg-[rgba(123,242,193,0.1)] border border-[var(--green)] text-[var(--green)] text-[10px] tracking-[.08em] hover:bg-[var(--green)] hover:text-[#04111a] transition-colors disabled:opacity-40"
              >
                CHECK BALANCE
              </button>
              <button
                onClick={handleHangUp}
                disabled={loading || !karionState.connected}
                className="px-[12px] py-[7px] bg-[rgba(255,138,138,0.1)] border border-[#ff8a8a] text-[#ff8a8a] text-[10px] tracking-[.08em] hover:bg-[#ff8a8a] hover:text-[#04111a] transition-colors disabled:opacity-40"
              >
                HANG UP
              </button>
            </div>
            {statusMsg && (
              <div className="text-[10px] text-[var(--cyan)] font-mono bg-[rgba(112,169,187,0.06)] p-[8px] border border-[rgba(112,169,187,0.2)]">
                {statusMsg}
              </div>
            )}
          </div>
        </section>

        {/* Synced Android Tasks with PC Verify */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)] lg:col-span-2">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">03 / TASKS</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Encrypted android tasks</h2>
          </div>
          <div className="p-[14px_18px]">
            {tasks.length === 0 ? (
              <div className="text-[10px] text-[#577584] py-[16px] text-center font-mono">
                {karionState.connected ? 'No synced tasks found in Firestore.' : 'Connect & pair in Settings to view Android tasks.'}
              </div>
            ) : (
              <div className="space-y-[8px] max-h-[280px] overflow-y-auto">
                {tasks.map((t) => (
                  <div key={t.id} className="flex items-center justify-between bg-[rgba(7,20,31,0.6)] border border-[#1b4356] p-[10px_12px]">
                    <div>
                      <div className="flex items-center gap-[8px]">
                        <span className="text-[11px] text-[#e4f6fa] font-medium">{t.title}</span>
                        <span className={`text-[8px] px-[6px] py-[1px] font-mono uppercase ${t.pcApproved ? 'bg-[rgba(123,242,193,0.1)] text-[var(--green)] border border-[rgba(123,242,193,0.3)]' : 'bg-[rgba(255,200,100,0.1)] text-[#ffc864] border border-[rgba(255,200,100,0.3)]'}`}>
                          {t.pcApproved ? 'PC_VERIFIED' : (t.syncStatus || 'PENDING')}
                        </span>
                      </div>
                      <div className="text-[9px] text-[#8aa8b6] mt-[2px]">{t.description || 'Encrypted task payload'}</div>
                    </div>
                    <div>
                      {!t.pcApproved && (
                        <button
                          onClick={() => handleApproveTask(t.id)}
                          className="px-[10px] py-[4px] bg-[var(--cyan)] text-[#04111a] text-[9px] font-mono uppercase tracking-[.06px] hover:bg-[var(--ice)] transition-colors"
                        >
                          PC VERIFY
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Focus Sessions & Strict Lock Control */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">04 / FOCUS</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Focus & strict lock</h2>
          </div>
          <div className="p-[14px_18px] space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[11px] text-[#b8d4dc]">Strict Focus Lock</div>
                <div className="text-[9px] text-[#577584]">Prevent Android app switching during active sessions</div>
              </div>
              <button
                onClick={() => handleToggleFocusLock(true)}
                className="px-[10px] py-[5px] bg-[rgba(112,169,187,0.15)] border border-[var(--cyan)] text-[var(--cyan)] text-[9px] font-mono hover:bg-[var(--cyan)] hover:text-[#04111a]"
              >
                ARM LOCK
              </button>
            </div>
            <div className="border-t border-[#1b4356] pt-[10px]">
              <div className="text-[10px] text-[#8aa8b6] mb-[6px]">Recent Focus Sessions ({focusSessions.length})</div>
              {focusSessions.length === 0 ? (
                <div className="text-[9px] text-[#577584]">No active focus sessions recorded.</div>
              ) : (
                <div className="space-y-[6px] max-h-[160px] overflow-y-auto">
                  {focusSessions.map((fs) => (
                    <div key={fs.id} className="flex items-center justify-between text-[9px] bg-[rgba(7,20,31,0.5)] p-[6px_8px] border border-[#1b4356]">
                      <span className="text-[#e4f6fa] font-mono">{fs.label || 'Focus Session'}</span>
                      <span className="text-[var(--cyan)] font-mono">{fs.status}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
