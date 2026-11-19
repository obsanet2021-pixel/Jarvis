import { useJarvisStore } from '../store'
import { Task, ApprovalRequest } from '../types'

export default function TasksPanel() {
  const { tasks, approvals, addTask, addApproval, removeApproval } = useJarvisStore()

  return (
    <div className="workspace">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            SYSTEM DIRECTIVES
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Tasks<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Manage system tasks, active processes, and pending approvals.</p>
        </div>
      </div>

      <div className="overview-grid grid grid-cols-1 lg:grid-cols-2 gap-[14px]">
        <section className="panel border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">01 / QUEUE</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Active tasks</h2>
            </div>
            <span className="tiny-label text-[7px] text-[#547785]">PROCESSOR LOAD</span>
          </div>
          <div className="full-list p-[12px_18px_14px]">
            {tasks.length > 0 ? (
              tasks.map((task) => (
                <div key={task.id} className="task-full">
                  <div className={`task-label ${task.status === 'completed' ? 'done' : ''}`}>{task.name}</div>
                  <div className="w-[80px] h-[3px] bg-[#183241] rounded-full overflow-hidden ml-auto">
                    <div className="h-full bg-[var(--cyan)]" style={{ width: `${task.progress}%` }}></div>
                  </div>
                  <span className="priority text-[7px] tracking-[.1em] text-[#678897] uppercase ml-[15px]">{task.status}</span>
                </div>
              ))
            ) : (
              <div className="py-[30px] text-center text-[10px] text-[var(--muted)] tracking-[.1em]">NO ACTIVE TASKS</div>
            )}
          </div>
        </section>

        <section className="panel border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">02 / SECURITY</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Pending approvals</h2>
            </div>
          </div>
          <div className="full-list p-[12px_18px_14px]">
            {approvals.length > 0 ? (
              approvals.map((approval) => (
                <div key={approval.id} className="full-row">
                  <div className="kind">{approval.risk_level.toUpperCase()}</div>
                  <div className="desc">{approval.action}</div>
                  <button className="text-btn" onClick={() => removeApproval(approval.id)}>APPROVE</button>
                  <button className="text-btn text-[#ff8a8a]" onClick={() => removeApproval(approval.id)}>DENY</button>
                </div>
              ))
            ) : (
              <div className="py-[30px] text-center text-[10px] text-[var(--muted)] tracking-[.1em]">NO PENDING APPROVALS</div>
            )}
          </div>
        </section>
      </div>

      <section className="panel mt-[14px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)]">
        <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">03 / ACTIONS</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Quick controls</h2>
        </div>
        <div className="add-task">
          <button onClick={() => {
            addTask({ id: `t_${Date.now()}`, name: 'System Check', status: 'running', progress: 0, created_at: Date.now(), updated_at: Date.now() })
          }}>CHECK SYSTEMS</button>
          <button onClick={() => {
             addApproval({ id: `a_${Date.now()}`, action: 'Manual Override', description: 'User triggered manual override', risk_level: 'high', created_at: Date.now() })
          }}>TRIGGER OVERRIDE</button>
        </div>
      </section>
    </div>
  )
}
