export default function SettingsPanel() {
  return (
    <div className="h-full flex flex-col bg-black/30 rounded-2xl border border-white/10 overflow-hidden">
      <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-black/20">
        <h3 className="text-sm font-semibold text-white">Settings</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        <div className="bg-black/20 rounded-xl border border-white/10 p-6">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-6">Voice Interface</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-300">Speech-to-Text</span>
                <p className="text-xs text-gray-500">Convert voice commands to text</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-emerald-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-300">Text-to-Speech</span>
                <p className="text-xs text-gray-500">Convert Jarvis responses to voice</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-emerald-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-black/20 rounded-xl border border-white/10 p-6">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-6">Appearance</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-300">Hologram Effects</span>
                <p className="text-xs text-gray-500">Enable holographic glow and pulse effects</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-emerald-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-black/20 rounded-xl border border-white/10 p-6">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-6">Backend Configuration</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
              <span className="text-sm text-gray-300">API Endpoint</span>
              <span className="text-xs font-mono text-emerald-400">http://localhost:8000</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
              <span className="text-sm text-gray-300">WebSocket</span>
              <span className="text-xs font-mono text-gray-400">ws://localhost:8000</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}