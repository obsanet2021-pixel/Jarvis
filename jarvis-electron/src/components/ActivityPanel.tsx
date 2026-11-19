import { useEffect, useState } from 'react'
import { useJarvisStore } from '../store'
import { Notification } from '../types'

export default function ActivityPanel() {
  const { notifications, markNotificationRead, clearNotifications, addNotification } = useJarvisStore()

  return (
    <div className="workspace">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            EVENT STREAM
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Activity<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">System logs and notification events in real-time.</p>
        </div>
      </div>

      <section className="panel min-h-[400px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
        <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
          <div>
            <span className="section-index text-[8px] text-[#648c9d] block">01 / LOGS</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Notification stream</h2>
          </div>
          <button onClick={clearNotifications} disabled={notifications.length === 0} className="text-btn border-0 bg-transparent cursor-pointer disabled:opacity-30 disabled:cursor-default">CLEAR ALL ↗</button>
        </div>

        <div className="activity-list p-[12px_18px_14px] max-h-[520px] overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="py-[40px] text-center text-[10px] text-[var(--muted)] tracking-[.1em]">NO RECENT ACTIVITY</div>
          ) : (
            [...notifications].reverse().map((notif) => {
              const typeColors: Record<string, string> = { error: '#ff8a8a', warning: '#ffb86a', success: '#7bf2c1', info: '#63e6ff' }
              const typeIcons: Record<string, string> = { error: '⚠', warning: '⚡', success: '✓', info: 'ℹ' }
              const color = typeColors[notif.type] || '#63e6ff'
              return (
                <div key={notif.id} className={`activity-row flex items-start gap-[10px] py-[10px] border-b border-[#17303d] text-[10px]`}>
                  <span className="w-[22px] h-[22px] rounded-full grid place-items-center text-[10px] shrink-0" style={{ background: `${color}22`, color }}>{typeIcons[notif.type]}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-[2px]">
                      <span className="font-medium" style={{ color: '#b8d4dc' }}>{notif.title}</span>
                      <span className="text-[#5f8595] font-display">{new Date(notif.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-[#678897] leading-[1.5]">{notif.message}</p>
                  </div>
                  {!notif.read && (
                    <button onClick={() => markNotificationRead(notif.id)} className="text-btn shrink-0 ml-[5px]">READ</button>
                  )}
                </div>
              )
            })
          )}
        </div>
      </section>
    </div>
  )
}
