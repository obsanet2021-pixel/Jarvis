import { useEffect, useState } from 'react'
import { useJarvisStore } from '../../store'
import Hologram from '../Hologram'
import { HologramState } from '../../types'

export default function HomeDashboardPanel() {
  const { deviceStatus, hologramState, setHologramState, setIsListening, setIsSpeaking } = useJarvisStore()
  const [time, setTime] = useState('')
  const [date, setDate] = useState('')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString('en-US', { hour12: false }))
      setDate(now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase())
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

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

  const getStatusColor = (status?: string) => {
    if (!status) return 'text-[var(--mu)]'
    return status === 'online' || status === 'connected' || status === 'available' ? 'text-[var(--green)]' : 'text-red-400'
  }

  return (
    <div className="workspace">
      <div className="hero-head flex items-end justify-between mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            YOUR INTELLIGENCE, AT A GLANCE
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Good morning<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">All systems are operational. Here's your current overview.</p>
        </div>
        <div className="clock-wrap text-right pb-[3px]">
          <div id="clock" className="font-display font-normal text-[27px] tracking-[.08em] text-[#e5fbff]">{time}</div>
          <span className="text-[8px] tracking-[.16em] text-[var(--muted)] block">{date}</span>
        </div>
      </div>

      <div className="overview-grid grid grid-cols-[minmax(0,1.55fr)_minmax(290px,_0.9fr)] gap-[14px]">
        <section className="panel model-panel row-span-2 relative min-w-0 border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] shadow-[0_12px_40px_rgba(0,0,0,0),inset_0_1px_rgba(182,243,255,0.03)] overflow-hidden">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">01 / HOLOGRAPHIC PROJECTION</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Hologram interface</h2>
            </div>
            <div className="live-chip text-[8px] tracking-[.12em] text-[var(--green)] border border-[rgba(123,242,193,0.21)] px-[8px] py-[5px] flex items-center gap-[7px]">
              <span className="pulse inline-block w-[5px] h-[5px] rounded-full bg-[var(--green)] shadow-[0_0_9px_var(--green)] animate-pulse"></span>
              LIVE RENDER
            </div>
          </div>

          <div id="modelStage" className="h-[435px] relative overflow-hidden bg-gradient-to-b from-[rgba(8,89,119,0.26)] via-transparent to-transparent before:absolute before:inset-0 before:z-[1] before:pointer-events-none before:bg-[linear-gradient(90deg,transparent_49.8%,rgba(83,201,232,0.04)_50%,transparent_50.2%),linear-gradient(0deg,transparent_49.8%,rgba(83,201,232,0.04)_50%,transparent_50.2%)] after:absolute after:inset-[12px] after:border after:border-[rgba(99,230,255,0.07)] after:clip-path-[polygon(0_0,18px_0,18px_1px,1px_1px,1px_18px,0_18px,0_0,100%_0,100%_18px,calc(100%-1px)_18px,calc(100%-1px)_1px,calc(100%-18px)_1px,calc(100%-18px)_0)]">
            <Hologram state={hologramState} />

            <div className="model-caption absolute bottom-[14px] left-[18px] right-[18px] z-[2] flex justify-between text-[#6792a1] text-[8px] tracking-[.16em]">
              <span>FIG. 01</span>
              <span>HOLOGRAPHIC AVATAR · 3D</span>
            </div>

            <div className="model-tools absolute right-[15px] bottom-[12px] flex gap-[5px] z-[3]">
              <button title="Toggle rotation" className="tool-btn w-[29px] h-[27px] border border-[#326478] bg-[rgba(7,27,41,0.86)] text-[#8ebbc9] cursor-pointer hover:text-[var(--cyan)] hover:border-[var(--cyan)] hover:shadow-[0_0_10px_rgba(99,230,255,0.13)] transition-all">↻</button>
              <button title="Reset view" className="tool-btn w-[29px] h-[27px] border border-[#326478] bg-[rgba(7,27,41,0.86)] text-[#8ebbc9] cursor-pointer hover:text-[var(--cyan)] hover:border-[var(--cyan)] hover:shadow-[0_0_10px_rgba(99,230,255,0.13)] transition-all">⌖</button>
              <button title="Load another model" className="tool-btn w-[29px] h-[27px] border border-[#326478] bg-[rgba(7,27,41,0.86)] text-[#8ebbc9] cursor-pointer hover:text-[var(--cyan)] hover:border-[var(--cyan)] hover:shadow-[0_0_10px_rgba(99,230,255,0.13)] transition-all">＋</button>
            </div>
          </div>

          <div className="model-footer h-[57px] border-t border-[var(--line)] flex items-center justify-between px-[18px]">
            <div>
              <small className="text-[8px] tracking-[.12em] text-[var(--muted)] block">PROJECTION STATUS</small>
              <b className="text-[9px] tracking-[.08em] text-[#a7cbd5] block mt-[5px]"><span className="dot inline-block w-[5px] h-[5px] bg-[var(--green)] rounded-full shadow-[0_0_7px_var(--green)] mr-[5px] align-middle"></span>STABLE / 60 FPS TARGET</b>
            </div>
            <div className="intensity w-[45%]">
              <label htmlFor="intensity" className="text-[8px] tracking-[.12em] text-[var(--muted)] flex justify-between">
                HOLOGRAM INTENSITY
                <span className="text-[var(--cyan)]" id="intensityValue">78%</span>
              </label>
              <input type="range" id="intensity" min="20" max="120" value="78" className="w-full h-[3px] accent-[var(--cyan)] cursor-pointer" />
            </div>
          </div>
        </section>

        <div className="right-stack flex flex-col gap-[14px]">
          <section className="panel greeting-panel min-h-[182px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] shadow-[0_12px_40px_rgba(0,0,0,0),inset_0_1px_rgba(182,243,255,0.03)] overflow-hidden before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
            <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
              <div>
                <span className="section-index text-[8px] text-[#648c9d] block">02 / ASSISTANT</span>
                <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">At your service.</h2>
              </div>
              <div className="assistant-orb w-[35px] h-[35px] border border-[rgba(73,217,245,0.42)] rounded-full grid place-items-center shadow-[0_0_18px_rgba(50,216,255,0.16)]">
                <span className="w-[13px] h-[13px] rounded-full bg-[var(--cyan)] shadow-[0_0_14px_4px_rgba(74,223,255,0.4)] inline-block"></span>
              </div>
            </div>
            <p className="assistant-copy text-[11px] leading-[1.7] text-[#9bbac6] px-[18px] py-[12px] max-w-[440px]">
              Good morning. All systems are operational. Current status shows optimal performance across all subsystems.
            </p>
            <div className="assistant-meta border-t border-[var(--line)] mx-[18px] py-[9px] flex justify-between text-[7px] tracking-[.1em] text-[#64818e]">
              <span className="text-[#86c9d6]"><i className="dot inline-block w-[5px] h-[5px] bg-[var(--green)] rounded-full shadow-[0_0_7px_var(--green)] mr-[5px] align-middle"></i> LISTENING FOR COMMAND</span>
              <span>KARION CORE</span>
            </div>
          </section>

          <section className="panel power-panel min-h-[224px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] shadow-[0_12px_40px_rgba(0,0,0,0),inset_0_1px_rgba(182,243,255,0.03)] overflow-hidden before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
            <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
              <div>
                <span className="section-index text-[8px] text-[#648c9d] block">03 / ENERGY RESERVE</span>
                <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Power systems</h2>
              </div>
              <span className="tiny-label text-[7px] text-[#547785]">MAIN REACTOR</span>
            </div>
            <div className="power-readout h-[128px] relative flex items-center pl-[23px]">
              <strong className="font-display font-medium text-[59px] leading-[0.9] text-[#e4fbff] text-shadow-[0_0_18px_rgba(89,221,255,0.25)]">100</strong>
              <span className="font-display font-medium text-[21px] text-[var(--cyan)] ml-[4px]">%</span>
              <div className="power-ring absolute right-[24px] w-[102px] h-[102px]">
                <svg viewBox="0 0 100 100" className="w-full h-full transform rotate-[-90deg]">
                  <circle className="ring-track fill-none stroke-[#173748]" strokeWidth="2" cx="50" cy="50" r="43" />
                  <circle className="ring-progress fill-none stroke-[var(--cyan)]" strokeWidth="2" cx="50" cy="50" r="43" strokeDasharray="270.2" strokeDashoffset="0" style={{filter: 'drop-shadow(0 0 4px rgba(99,230,255,0.5))'}} />
                </svg>
                <div className="ring-core absolute inset-0 grid place-items-center text-[#6da4b4] font-display font-medium text-[10px] tracking-[.2em]">ARC</div>
              </div>
            </div>
            <div className="power-bottom border-t border-[var(--line)] mx-[18px] py-[10px] flex justify-between text-[8px] tracking-[.1em] text-[#82a5b2]">
              <span><i className="dot inline-block w-[5px] h-[5px] bg-[var(--green)] rounded-full shadow-[0_0_7px_var(--green)] mr-[5px] align-middle"></i> OUTPUT NOMINAL</span>
              <b className="text-[var(--green)] font-medium">STABLE</b>
            </div>
          </section>
        </div>
      </div>

      <div className="overview-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[14px] mt-[14px]">
        <section className="panel metrics-panel min-h-[160px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] shadow-[0_12px_40px_rgba(0,0,0,0),inset_0_1px_rgba(182,243,255,0.03)] overflow-hidden before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">04 / PERFORMANCE</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">System telemetry</h2>
            </div>
            <span className="tiny-label text-[7px] text-[#547785]">SIMULATED DEMO DATA</span>
          </div>
          <div className="metrics-grid p-[19px_18px_18px] grid grid-cols-4 gap-[17px]">
            {[
              { label: 'PROCESSOR', value: '24%', color: 'text-[#d9f5fb]' },
              { label: 'MEMORY', value: '48%', color: 'text-[#d9f5fb]' },
              { label: 'THERMAL', value: '42°C', color: 'text-[#d9f5fb]' },
              { label: 'NETWORK', value: '86%', color: 'text-[#d9f5fb]' },
            ].map((metric) => (
              <div key={metric.label} className="metric">
                <div className="metric-head flex justify-between items-center text-[8px] tracking-[.1em] text-[#8aaebb]">
                  <span>{metric.label}</span>
                  <b className={`font-display font-medium text-[15px] ${metric.color}`}>{metric.value}</b>
                </div>
                <div className="meter h-[3px] bg-[#183241] my-[11px_0_7px]">
                  <span className="block h-full bg-gradient-to-r from-[#258ba8] to-[var(--cyan)] shadow-[0_0_8px_rgba(99,230,255,0.44)] transition-[width] duration-700" style={{width: metric.value}}></span>
                </div>
                <small className="text-[7px] tracking-[.1em] text-[#577584] block">METRIC DISPLAY</small>
              </div>
            ))}
          </div>
        </section>

        <section className="panel directives-panel min-h-[160px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] shadow-[0_12px_40px_rgba(0,0,0,0),inset_0_1px_rgba(182,243,255,0.03)] overflow-hidden before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">05 / PRIORITY QUEUE</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Active directives</h2>
            </div>
            <button className="text-btn border-0 bg-transparent text-[var(--cyan)] text-[8px] tracking-[.12em] cursor-pointer hover:text-white transition-colors">VIEW ALL ↗</button>
          </div>
          <div className="directive-list p-[12px_18px_14px] space-y-0">
            <div className="directive flex items-center gap-[10px] py-[8px] border-b border-[#17303d] text-[10px]">
              <input type="checkbox" className="check appearance-none w-[13px] h-[13px] border border-[#527a8b] bg-transparent cursor-pointer checked:bg-[var(--cyan)] checked:border-[var(--cyan)] checked:shadow-[inset_0_0_0_3px_rgba(10,27,40)]" />
              <span className="directive-name text-[#b8d4dc]">Check network connectivity</span>
              <span className="priority ml-auto text-[7px] tracking-[.1em] text-[var(--amber)]">HIGH</span>
            </div>
            <div className="directive flex items-center gap-[10px] py-[8px] border-b border-[#17303d] text-[10px]">
              <input type="checkbox" className="check appearance-none w-[13px] h-[13px] border border-[#527a8b] bg-transparent cursor-pointer checked:bg-[var(--cyan)] checked:border-[var(--cyan)] checked:shadow-[inset_0_0_0_3px_rgba(10,27,40)]" />
              <span className="directive-name text-[#b8d4dc]">Sync device permissions</span>
              <span className="priority ml-auto text-[7px] tracking-[.1em] text-[var(--amber)]">MED</span>
            </div>
          </div>
        </section>

        <section className="panel activity-panel min-h-[160px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] shadow-[0_12px_40px_rgba(0,0,0,0),inset_0_1px_rgba(182,243,255,0.03)] overflow-hidden before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">06 / EVENT STREAM</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Recent activity</h2>
            </div>
            <button className="text-btn border-0 bg-transparent text-[var(--cyan)] text-[8px] tracking-[.12em] cursor-pointer hover:text-white transition-colors">VIEW LOG ↗</button>
          </div>
          <div className="activity-list p-[12px_18px_14px] space-y-0">
            <div className="activity-row flex items-center gap-[10px] py-[8px] border-b border-[#17303d] text-[10px]">
              <span className="activity-time text-[#5f8595] font-display text-[10px] min-w-[40px]">14:32</span>
              <span className="activity-name text-[#a9c6d0]">System check complete</span>
              <span className="activity-type ml-auto text-[#5b8596] text-[7px] tracking-[.1em]">DIAGNOSTIC</span>
            </div>
            <div className="activity-row flex items-center gap-[10px] py-[8px] border-b border-[#17303d] text-[10px]">
              <span className="activity-time text-[#5f8595] font-display text-[10px] min-w-[40px]">14:15</span>
              <span className="activity-name text-[#a9c6d0]">Network ping successful</span>
              <span className="activity-type ml-auto text-[#5b8596] text-[7px] tracking-[.1em]">NETWORK</span>
            </div>
          </div>
        </section>
      </div>

      <footer className="footerline flex justify-between py-[17px] text-[7px] tracking-[.14em] text-[#405e6d]">
        <span>KARION / AUTONOMOUS INTERFACE</span>
        <span>SECURE CHANNEL <i className="dot inline-block w-[4px] h-[4px] bg-[var(--green)] rounded-full shadow-[0_0_7px_var(--green)] align-middle mr-[5px]"></i> ENCRYPTED</span>
        <span>© STARK SYSTEMS</span>
      </footer>
    </div>
  )
}
