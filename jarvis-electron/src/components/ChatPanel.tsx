import { useState } from 'react'
import { useJarvisStore } from '../store'
import { api } from '../services/api'

export default function ChatPanel() {
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const {
    conversations,
    addConversation,
    setHologramState,
    setIsListening,
    setIsSpeaking,
    setIsWorking,
  } = useJarvisStore()

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isSending) return

    const userMessage = input
    setInput('')
    setIsSending(true)

    // Add user message
    const userMsg = {
      id: `msg_${Date.now()}`,
      role: 'user' as const,
      content: userMessage,
      timestamp: Date.now(),
    }
    addConversation(userMsg)

    // Set thinking state
    setHologramState('THINKING')
    setIsWorking(true)

    try {
      // Route known cellular commands through their dedicated endpoints for reliability
      const lower = userMessage.toLowerCase()

      if ((lower.includes('call') || lower.includes('dial') || lower.includes('phone')) && /\d{7,15}/.test(userMessage)) {
        const match = userMessage.match(/[\+]?[\d\-\s]{7,15}/)
        const target = match?.[0]
        if (target) {
          const result = await api.call(target)
          const assistantMsg = {
            id: `msg_${Date.now() + 1}`,
            role: 'assistant' as const,
            content: `Call initiated to ${target}. ${result.output || 'Dial command sent to device.'}`,
            timestamp: Date.now(),
          }
          addConversation(assistantMsg)
          setHologramState('WORKING')
          setIsSpeaking(true)
          setTimeout(() => { setIsSpeaking(false); setHologramState('IDLE') }, 2000)
          return
        }
      }

      if (lower.includes('balance') || lower.includes('credit') || lower.includes('check balance')) {
        const simMatch = userMessage.match(/SIM\s*(\d)/i)
        const simId = simMatch ? `SIM${simMatch[1]}` : 'SIM1'
        const result = await api.balance(simId)
        const assistantMsg = {
          id: `msg_${Date.now() + 1}`,
          role: 'assistant' as const,
          content: `Balance check for ${result.sim} (${result.network}): ${result.message}`,
          timestamp: Date.now(),
        }
        addConversation(assistantMsg)
        setHologramState('WORKING')
        setIsSpeaking(true)
        setTimeout(() => { setIsSpeaking(false); setHologramState('IDLE') }, 2000)
        return
      }

      if (lower.includes('hangup') || lower.includes('end call') || lower.includes('stop call')) {
        const result = await api.hangup()
        const assistantMsg = {
          id: `msg_${Date.now() + 1}`,
          role: 'assistant' as const,
          content: `Call terminated. ${result.output || 'Hang-up signal sent.'}`,
          timestamp: Date.now(),
        }
        addConversation(assistantMsg)
        setHologramState('IDLE')
        return
      }

      if (lower.includes('status') || lower.includes('system status')) {
        const status = await api.status()
        const assistantMsg = {
          id: `msg_${Date.now() + 1}`,
          role: 'assistant' as const,
          content: `System status — call state: ${status.call_state}, ADB connected: ${status.adb_connected ? 'yes' : 'no'}`,
          timestamp: Date.now(),
        }
        addConversation(assistantMsg)
        return
      }

      // Fallback: send through the voice command processor for natural-language handling
      const voiceResult = await api.processVoiceCommand(userMessage)
      const assistantMsg = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant' as const,
        content: voiceResult.success ? voiceResult.response : `I didn't understand: "${userMessage}". Try "help" for commands.`,
        timestamp: Date.now(),
      }
      addConversation(assistantMsg)
      setHologramState('IDLE')
      setIsWorking(false)
    } catch (err: any) {
      const errorMsg = {
        id: `msg_${Date.now() + 1}`,
        role: 'system' as const,
        content: `Error: ${err.message || 'Backend request failed'}`,
        timestamp: Date.now(),
      }
      addConversation(errorMsg)
      setHologramState('ERROR')
      setIsWorking(false)
    } finally {
      setIsSending(false)
      setIsListening(false)
      setIsSpeaking(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-black/30 rounded-2xl border border-white/10 overflow-hidden">
      <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-black/20">
        <h3 className="text-sm font-semibold text-white">Conversation</h3>
        <div className="flex items-center gap-2 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span className="text-gray-400">Backend Connected</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 relative">
        {conversations.length === 0 && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3 text-xl">💬</div>
            <p>Start a conversation with Jarvis</p>
          </div>
        )}

        <div className="animate-fade-in space-y-4">
          {conversations.map((msg) => (
            <div
              key={msg.id}
              className={`max-w-[80%] animate-slide-in ${
                msg.role === 'user' ? 'ml-auto text-right' : 'mr-auto text-left'
              }`}
            >
              <div
                className={`inline-block px-4 py-3 rounded-2xl ${
                  msg.role === 'user'
                    ? 'bg-emerald-500/20 border border-emerald-500/30 text-white'
                    : msg.role === 'system'
                    ? 'bg-white/5 border border-white/10 text-gray-400'
                    : 'bg-white/8 border border-white/10 text-white'
                }`}
              >
                <p className="text-sm leading-relaxed">{msg.content}</p>
                <span className="block mt-1 text-[10px] text-gray-500">{new Date(msg.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="h-14 border-t border-white/10 px-6 py-4 flex items-center gap-3 bg-black/20">
        <form onSubmit={handleSend} className="flex-1 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message to Jarvis..."
            className="w-full bg-white/5 border border-white/10 rounded-full px-5 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all"
            disabled={isSending}
          />
          {isSending && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="w-3 h-3 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin"></div>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}