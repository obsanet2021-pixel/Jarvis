import { useState, useRef, useEffect } from 'react'
import { useJarvisStore } from '../store'
import { api } from '../services/api'

export default function ChatPanel() {
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const speakTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const {
    conversations,
    addConversation,
    setHologramState,
    setIsListening,
    setIsSpeaking,
    setIsWorking,
  } = useJarvisStore()

  // Cleanup timers on unmount or before new actions
  useEffect(() => {
    return () => clearSpeakTimers()
  }, [])

  const clearSpeakTimers = () => {
    if (speakTimerRef.current) {
      clearTimeout(speakTimerRef.current)
      speakTimerRef.current = null
    }
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isSending) return

    const userMessage = input
    setInput('')
    setIsSending(true)

    const userMsg = {
      id: `msg_${Date.now()}`,
      role: 'user' as const,
      content: userMessage,
      timestamp: Date.now(),
    }
    addConversation(userMsg)

    setHologramState('THINKING')
    setIsWorking(true)

    try {
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
          speakTimerRef.current = setTimeout(() => {
            clearSpeakTimers()
            setIsSpeaking(false)
            setHologramState('IDLE')
          }, 2000)
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
        speakTimerRef.current = setTimeout(() => {
          clearSpeakTimers()
          setIsSpeaking(false)
          setHologramState('IDLE')
        }, 2000)
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
          content: `System status — call state: ${status.call_state}, backend: online`,
          timestamp: Date.now(),
        }
        addConversation(assistantMsg)
        return
      }

      const voiceResult = await api.processVoiceCommand(userMessage, [
        { name: 'place_phone_call', description: 'Dial a phone number via Android' },
        { name: 'hang_up_call', description: 'Terminate the current Android call' },
        { name: 'check_phone_balance', description: 'Check balance on Android SIM' },
        { name: 'approve_android_task', description: 'Approve an Android task from PC' },
        { name: 'toggle_phone_focus_lock', description: 'Arm or disarm Android focus lock' },
      ])
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
      const isNetworkError = !err.message?.includes('API error')
      const errorMsg = {
        id: `msg_${Date.now() + 1}`,
        role: 'system' as const,
        content: isNetworkError
          ? 'Backend unreachable — active base URL: http://127.0.0.1:31415. Check if freellmapi is running and verify Settings > API credentials.'
          : `Error: ${err.message || 'Request failed'}`,
        timestamp: Date.now(),
      }
      addConversation(errorMsg)
      setHologramState(isNetworkError ? 'ERROR' : 'IDLE')
      setIsWorking(false)
    } finally {
      setIsSending(false)
      setIsListening(false)
      setIsSpeaking(false)
    }
  }

  return (
    <div className="workspace">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            COMMUNICATIONS LOG
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Conversations<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Voice and text interaction history with J.A.R.V.I.S. core.</p>
        </div>
      </div>

      <section className="panel min-h-[600px] border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.92)] to-[rgba(6,17,27,0.92)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
        <div className="panel-top relative flex items-center justify-between px-[18px] pt-[16px] z-[2]">
          <div>
            <span className="section-index text-[8px] text-[#648c9d] block">01 / CONVERSATION STREAM</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Message log</h2>
          </div>
          <div className="live-chip text-[8px] tracking-[.12em] text-[var(--green)] border border-[rgba(123,242,193,0.21)] px-[8px] py-[5px] flex items-center gap-[7px]">
            <span className="pulse inline-block w-[5px] h-[5px] rounded-full bg-[var(--green)] shadow-[0_0_9px_var(--green)] animate-pulse"></span>
            ONLINE
          </div>
        </div>

        <div className="chat-stream p-[18px] space-y-4 max-h-[520px] overflow-y-auto">
          {conversations.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-[var(--muted)]">
              <div className="w-[45px] h-[45px] border border-[rgba(73,217,245,0.42)] rounded-full grid place-items-center mb-3">
                <span className="w-[16px] h-[16px] rounded-full bg-[var(--cyan)] shadow-[0_0_14px_4px_rgba(74,223,255,0.4)] inline-block"></span>
              </div>
              <p className="text-[10px] tracking-[.14em]">INITIALIZE CONVERSATION</p>
            </div>
          )}

          <div className="space-y-4">
            {conversations.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[75%] px-[14px] py-[10px] ${
                  msg.role === 'user'
                    ? 'bg-[rgba(99,230,255,0.08)] border border-[rgba(99,230,255,0.2)] text-[#d9f3f9]'
                    : msg.role === 'system'
                    ? 'bg-[rgba(255,100,100,0.06)] border border-[rgba(255,100,100,0.15)] text-[#ff8a8a]'
                    : 'bg-[rgba(11,28,42,0.7)] border border-[var(--line)] text-[#b8d4dc]'
                }`}>
                  <p className="text-[11px] leading-[1.6]">{msg.content}</p>
                  <span className="block mt-[5px] text-[7px] text-[#577584] tracking-[.1em]">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-[var(--line)] mx-[18px]"></div>

        <div className="p-[14px_18px_18px]">
          <form onSubmit={handleSend} className="relative flex items-center gap-[10px]">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter command or message…"
              className="flex-1 bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[14px] py-[11px] text-[11px] text-[var(--ice)] placeholder-[#607e8c] outline-none focus:border-[var(--cyan)] transition-colors"
              disabled={isSending}
            />
            {isSending && (
              <div className="absolute right-[50px] top-1/2 -translate-y-1/2">
                <div className="w-[14px] h-[14px] rounded-full border-2 border-[var(--cyan)] border-t-transparent animate-spin"></div>
              </div>
            )}
            <button
              type="submit"
              className="w-[31px] h-[31px] border-0 bg-[var(--cyan)] text-[#04111a] text-[14px] cursor-pointer hover:shadow-[0_0_15px_rgba(99,230,255,0.44)] transition-shadow"
              disabled={isSending}
            >↑</button>
          </form>
          <div className="mt-[8px] text-[7px] tracking-[.1em] text-[var(--muted)]">
            PRESS ENTER TO SEND · BACKEND INTEGRATED
          </div>
        </div>
      </section>
    </div>
  )
}
