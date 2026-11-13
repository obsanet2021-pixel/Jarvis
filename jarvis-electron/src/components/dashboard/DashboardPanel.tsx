import React from 'react'
import { useJarvisStore } from '../store'

export default function DashboardPanel() {
  const { deviceStatus, sims } = useJarvisStore()

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SystemOverviewPanel deviceStatus={deviceStatus} sims={sims} />
        <QuickActionsPanel />
      </div>
    </div>
  )
}

function SystemOverviewPanel({ deviceStatus, sims }: any) {
  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">System Overview</h3>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center py-2 border-b border-gray-800">
          <span className="text-gray-300">Backend</span>
          <span className="font-medium text-green-400">Online</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-800">
          <span className="text-gray-300">Android Link</span>
          <span className="text-yellow-400">Standby</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-800">
          <span className="text-gray-300">Voice Interface</span>
          <span className="text-green-400">Ready</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-800">
          <span className="text-gray-300">SIM 1</span>
          <span className="font-medium text-green-400">Available</span>
        </div>
        
        <div className="flex justify-between items-center py-2">
          <span className="text-gray-300">SIM 2</span>
          <span className="font-medium text-green-400">Available</span>
        </div>
      </div>
    </div>
  )
}

function QuickActionsPanel() {
  const actions = [
    'Check SIM balance',
    'Start conversation', 
    'View device status'
  ]

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
      
      <div className="space-y-3">
        {actions.map((action, index) => (
          <div key={index} className="py-3 border-b border-gray-800">
            <button className="w-full text-left text-gray-300 hover:text-white transition-colors">
              {action}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}