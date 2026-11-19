import { useState, useEffect } from 'react'
import { useJarvisStore } from '../store'

// Reflects what socials.js defines — mirrors parent project's APPS list
const SOCIAL_APPS = [
  { slug: 'twitter',   label: 'Twitter / X',   nativePrefix: ['TWITTER_', 'X_'] },
  { slug: 'linkedin',  label: 'LinkedIn',       nativePrefix: ['LINKEDIN_'] },
  { slug: 'facebook',  label: 'Facebook',       nativePrefix: ['FACEBOOK_'] },
  { slug: 'instagram', label: 'Instagram',      nativePrefix: ['INSTAGRAM_'] },
]

type ConnState = 'disconnected' | 'connecting' | 'connected' | 'error'

interface AccountHandle {
  id: string
  handle: string
  displayName: string
}

export default function AgentsPanel() {
  const { addNotification } = useJarvisStore()
  const STORAGE_KEY = 'jarvis_composio_key'

  const [composioKey, setComposioKey] = useState('')
  const [apiKeyVisible, setApiKeyVisible] = useState(false)
  const [connStates, setConnStates] = useState<Record<string, ConnState>>({})
  const [isConnecting, setIsConnecting] = useState(false)

  // Modal state for account selection during OAuth flow
  const [showAccountModal, setShowAccountModal] = useState(false)
  const [modalSlug, setModalSlug] = useState('')
  const [accounts, setAccounts] = useState<AccountHandle[]>([])

  // Restore stored key and connection states on mount (fixes dead useState initializer)
  useEffect(() => {
    try {
      const storedKey = localStorage.getItem(STORAGE_KEY) ?? ''
      if (storedKey) setComposioKey(storedKey)
      const storedConns = localStorage.getItem('jarvis_conn_states')
      if (storedConns) setConnStates(JSON.parse(storedConns))
    } catch {}
  }, [])

  // Persist connection states whenever they change
  useEffect(() => {
    if (Object.keys(connStates).length > 0) {
      localStorage.setItem('jarvis_conn_states', JSON.stringify(connStates))
    }
  }, [connStates])

  const handleConnect = async (slug: string) => {
    const key = composioKey.trim()
    if (!key) {
      addNotification({
        id: `notif_${Date.now()}`,
        type: 'error',
        title: 'Missing API Key',
        message: 'Set your Composio key in Settings → Auth first.',
        timestamp: Date.now(),
        read: false,
      })
      return
    }
    // Open account-selection dialog so user binds a specific account handle
    const mockAccounts: AccountHandle[] = [
      { id: `${slug}_1`, handle: `@${slug.replace('_', '')}_user`, displayName: `${slug.charAt(0).toUpperCase() + slug.slice(1)} User` },
      { id: `${slug}_2`, handle: `@${slug}_secondary`, displayName: `${slug.charAt(0).toUpperCase() + slug.slice(1)} Secondary` },
    ]
    setAccounts(mockAccounts)
    setModalSlug(slug)
    setShowAccountModal(true)
  }

  const confirmAccountSelection = async () => {
    if (!modalSlug || accounts.length === 0) return
    setIsConnecting(true)
    setConnStates((prev) => ({ ...prev, [modalSlug]: 'connecting' }))
    // Real flow: POST to Composio OAuth endpoint here; demo simulates success
    await new Promise((r) => setTimeout(r, 900 + Math.random() * 500))
    const ok = true
    setConnStates((prev) => ({ ...prev, [modalSlug]: ok ? 'connected' : 'error' }))
    setIsConnecting(false)
    setShowAccountModal(false)

    if (ok) {
      addNotification({
        id: `notif_${Date.now()}`,
        type: 'success',
        title: `${modalSlug} Connected`,
        message: `Successfully authorized ${modalSlug}. Tool queries enabled.`,
        timestamp: Date.now(),
        read: false,
      })
    } else {
      addNotification({
        id: `notif_${Date.now()}`,
        type: 'error',
        title: `${modalSlug} Failed`,
        message: 'OAuth handshake failed. Check your Composio credentials.',
        timestamp: Date.now(),
        read: false,
      })
    }
  }

  const handleSaveKey = () => {
    localStorage.setItem(STORAGE_KEY, composioKey.trim())
    addNotification({
      id: `notif_${Date.now()}`,
      type: 'success',
      title: 'Key Saved',
      message: 'Composio API key persisted to local storage.',
      timestamp: Date.now(),
      read: false,
    })
  }

  const handleDisconnect = (slug: string) => {
    setConnStates((prev) => ({ ...prev, [slug]: 'disconnected' }))
    addNotification({
      id: `notif_${Date.now()}`,
      type: 'info',
      title: `${slug} Disconnected`,
      message: `Removed authorization for ${slug}.`,
      timestamp: Date.now(),
      read: false,
    })
  }

  const connectedCount = Object.values(connStates).filter((s) => s === 'connected').length

  return (
    <div className="workspace overflow-y-auto">
      {/* Account Selection Modal */}
      {showAccountModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowAccountModal(false)}>
          <div
            className="panel border border-[var(--line)] bg-gradient-to-br from-[rgba(11,28,42,0.97)] to-[rgba(6,17,27,0.97)] w-[400px] max-w-[90vw]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="panel-top px-[18px] pt-[16px] mb-0">
              <span className="section-index text-[8px] text-[#648c9d] block">OAUTH FLOW</span>
              <h3 className="font-display font-medium text-[16px] tracking-[.035em] text-[#d9f3f9] mt-[4px]">
                Select {modalSlug.toUpperCase()} Account
              </h3>
              <p className="text-[9px] text-[#577584] mt-[2px]">Choose the account to authorize for read-only access.</p>
            </div>
            <div className="p-[14px_18px] space-y-3">
              {accounts.map((acct) => (
                <button
                  key={acct.id}
                  onClick={confirmAccountSelection}
                  className="w-full flex items-center gap-[10px] px-[12px] py-[10px] border border-[#276077] rounded hover:border-[var(--cyan)] transition-colors text-left cursor-pointer"
                >
                  <div className="w-[28px] h-[28px] rounded-full bg-[rgba(99,230,255,0.1)] border border-[rgba(99,230,255,0.3)] grid place-items-center text-[var(--cyan)] text-[11px] shrink-0">
                    {acct.handle[0].toUpperCase()}
                  </div>
                  <div>
                    <div className="text-[11px] text-[#d9f3f9]">{acct.displayName}</div>
                    <div className="text-[9px] text-[#577584]">{acct.handle}</div>
                  </div>
                </button>
              ))}
            </div>
            <div className="flex items-center justify-between px-[18px] pb-[14px]">
              <button
                onClick={() => setShowAccountModal(false)}
                className="text-btn border-0 bg-transparent cursor-pointer text-[#ff8a8a]"
              >
                Cancel
              </button>
              <button
                onClick={confirmAccountSelection}
                disabled={isConnecting}
                className="px-[12px] py-[6px] bg-[var(--cyan)] text-[#04111a] text-[10px] font-medium cursor-pointer hover:shadow-[0_0_12px_rgba(99,230,255,0.4)] transition-shadow disabled:opacity-40"
              >
                {isConnecting ? 'AUTHENTICATING…' : 'CONFIRM'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            AGENT INTEGRATIONS
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Agents<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Social media agents powered by Composio — connect accounts to enable read-only queries. <span className="text-[var(--cyan)]">{connectedCount}/4 linked</span></p>
        </div>
      </div>

      {/* Key entry */}
      <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)] mb-[14px]">
        <div className="panel-top relative px-[18px] pt-[16px]">
          <span className="section-index text-[8px] text-[#648c9d] block">01 / COMPOSIO</span>
          <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">API Key</h2>
        </div>
        <div className="p-[14px_18px] flex items-center gap-[10px]">
          <input
            type={apiKeyVisible ? 'text' : 'password'}
            value={composioKey}
            onChange={(e) => setComposioKey(e.target.value)}
            placeholder="app_xxxxxxxx..."
            className="flex-1 bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[12px] py-[8px] text-[11px] font-mono text-[var(--ice)] placeholder-[#607e8c] outline-none focus:border-[var(--cyan)] transition-colors"
          />
          <button
            onClick={() => setApiKeyVisible((v) => !v)}
            className="px-[10px] py-[8px] border border-[#276077] text-[#607e8c] text-[9px] cursor-pointer hover:text-[var(--cyan)] hover:border-[var(--cyan)] transition-colors"
          >
            {apiKeyVisible ? 'HIDE' : 'SHOW'}
          </button>
          <button
            onClick={handleSaveKey}
            className="px-[12px] py-[8px] bg-[var(--cyan)] text-[#04111a] text-[10px] font-medium cursor-pointer hover:shadow-[0_0_12px_rgba(99,230,255,0.4)] transition-shadow"
          >
            SAVE
          </button>
        </div>
        <div className="mx-[18px] mb-[12px] text-[8px] text-[#577584]">
          Get your key at <span className="text-[var(--cyan)] underline">app.composio.dev → Settings → API Keys</span>. Stores locally only.
        </div>
      </section>

      {/* Agent cards */}
      <div className="device-grid grid grid-cols-1 md:grid-cols-2 gap-[14px]">
        {SOCIAL_APPS.map(({ slug, label, nativePrefix }) => {
          const state = connStates[slug] ?? 'disconnected'
          const dotColor =
            state === 'connected' ? 'var(--green)'
            : state === 'connecting' ? 'var(--amber, #f0c060)'
            : state === 'error' ? '#ff8a8a'
            : '#577584'
          const stateLabel =
            state === 'connected' ? 'CONNECTED'
            : state === 'connecting' ? 'AUTHENTICATING…'
            : state === 'error' ? 'FAILED'
            : 'DISCONNECTED'
          return (
            <section key={slug} className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
              <div className="panel-top relative px-[18px] pt-[16px]">
                <span className="section-index text-[8px] text-[#648c9d] block">{label.toUpperCase()}</span>
                <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">{label}</h2>
              </div>
              <div className="p-[14px_18px] space-y-3">
                <div className="flex items-center gap-[8px] text-[10px]">
                  <span className="dot inline-block w-[6px] h-[6px] rounded-full" style={{ background: dotColor, boxShadow: `0 0 6px ${dotColor}` }} />
                  <span className="tracking-[.1em]" style={{ color: dotColor }}>{stateLabel}</span>
                </div>
                <div className="text-[9px] text-[#577584]">
                  Read-only tools: {nativePrefix.map((p) => p.replace('_', '')).join(', ')}
                </div>
                <div className="pt-[4px] flex gap-[8px]">
                  <button
                    onClick={() => handleConnect(slug)}
                    disabled={isConnecting}
                    className="text-btn border-0 bg-transparent cursor-pointer disabled:opacity-40"
                  >
                    {state === 'connected' ? 'RECONNECT' : 'CONNECT ACCOUNT'}
                  </button>
                  {state === 'connected' && (
                    <button
                      onClick={() => handleDisconnect(slug)}
                      className="text-btn border-0 bg-transparent cursor-pointer text-[#ff8a8a]"
                    >
                      DISCONNECT
                    </button>
                  )}
                </div>
              </div>
            </section>
          )
        })}
      </div>

      <div className="mt-[14px] panel border border-[var(--line)] p-[14px_18px] text-[9px] text-[#577584]">
        Note: Social platforms require OAuth app registration on their developer portals. Composio handles the exchange once credentials are configured at{' '}
        <span className="text-[var(--cyan)]">app.composio.dev</span>. Queries are read-only by design.
      </div>
    </div>
  )
}
