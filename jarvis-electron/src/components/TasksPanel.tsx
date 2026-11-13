import { useJarvisStore } from '../store'
import { Task, ApprovalRequest } from '../types'

export default function TasksPanel() {
  const { tasks, approvals, addTask, addApproval, removeApproval, setTasks } = useJarvisStore()

  // Initialize some sample real tasks if empty
  // (These are UI state only; real tasks would come from backend in future phases)

  return (
    <div className="h-full flex flex-col bg-black/30 rounded-2xl border border-white/10 overflow-hidden">
      <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-black/20">
        <h3 className="text-sm font-semibold text-white">Tasks & Approvals</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-black/20 rounded-xl border border-white/10 p-5">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-4">Active Tasks</h4>
            <div className="space-y-3">
              {tasks.length > 0 ? (
                tasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between py-2">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-2 h-2 rounded-full ${task.status === 'completed' ? 'bg-emerald-500' : task.status === 'running' ? 'bg-cyan-400 animate-pulse' : 'bg-gray-600'}`}
                      ></div>
                      <span className="text-sm text-gray-300 truncate">{task.name}</span>
                    </div>
                    <div className="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-emerald-500 rounded-full transition-all duration-300`}
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-gray-500 capitalize">{task.status}</span>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500 text-sm">
                  No active tasks.
                </div>
              )}
            </div>
          </div>

          <div className="bg-black/20 rounded-xl border border-white/10 p-5">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-4">Pending Approvals</h4>
            <div className="space-y-3">
              {approvals.length > 0 ? (
                approvals.map((approval) => (
                  <div key={approval.id} className="py-3 border-b border-white/5 last:border-0">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-white">{approval.action}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full ${
                          approval.risk_level === 'high' ? 'bg-red-500/20 text-red-400' :
                          approval.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-emerald-500/20 text-emerald-400'
                        }`}
                      >
                        {approval.risk_level}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mb-3">{approval.description}</p>
                    <div className="flex gap-2">
                      <button
                        className="flex-1 px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded text-xs text-emerald-400 font-medium transition-colors"
                        onClick={() => removeApproval(approval.id)}
                      >
                        Approve
                      </button>
                      <button
                        className="flex-1 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded text-xs text-gray-400 font-medium transition-colors hover:text-red-400"
                        onClick={() => removeApproval(approval.id)}
                      >
                        Deny
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500 text-sm">
                  No pending approvals.
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="bg-black/20 rounded-xl border border-white/10 p-5">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-4">Quick Task Actions</h4>
          <div className="grid grid-cols-2 gap-3">
            <button
              className="px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-colors text-left"
              onClick={() => {
                const newTask: Task = {
                  id: `task_${Date.now()}`,
                  name: 'Cellular Balance Check',
                  status: 'running',
                  progress: 0,
                  created_at: Date.now(),
                  updated_at: Date.now(),
                }
                addTask(newTask)
              }}
            >
              📱 Check All Balances
            </button>
            <button
              className="px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-colors text-left"
              onClick={() => {
                const newTask: Task = {
                  id: `task_${Date.now() + 1}`,
                  name: 'Device Status Sync',
                  status: 'pending',
                  progress: 0,
                  created_at: Date.now(),
                  updated_at: Date.now(),
                }
                addTask(newTask)
              }}
            >
              🔄 Sync Devices
            </button>
            <button
              className="px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-colors text-left"
              onClick={() => {
                const newTask: Task = {
                  id: `task_${Date.now() + 2}`,
                  name: 'USSD Query',
                  status: 'pending',
                  progress: 0,
                  created_at: Date.now(),
                  updated_at: Date.now(),
                }
                addTask(newTask)
              }}
            >
              📊 Run USSD Query
            </button>
            <button
              className="px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-colors text-left"
              onClick={() => {
                const newApproval: ApprovalRequest = {
                  id: `approval_${Date.now()}`,
                  action: 'Outgoing Call',
                  description: 'Jarvis requests permission to initiate an outgoing cellular call.',
                  risk_level: 'medium',
                  created_at: Date.now(),
                }
                addApproval(newApproval)
              }}
            >
              📞 Request Call Approval
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}