import { useState, useEffect } from 'react'
import { useJarvisStore } from '../store'

const API_KEYS_STORAGE_KEY = 'jarvis_api_keys'
const LLM_CONFIG_STORAGE_KEY = 'jarvis_llm_config'
const KARION_CONFIG_STORAGE_KEY = 'jarvis_karion_pairing'

interface ApiKeys {
  openai: string
  composio: string
  stt: string
  tts: string
}

interface FirebaseConfig {
  apiKey: string
  authDomain: string
  projectId: string
  storageBucket: string
  messagingSenderId: string
  appId: string
}

interface KarionPairingConfig {
  firebaseConfig: FirebaseConfig
  operatorUid: string
  e2eeSessionKey: string
}

interface LLMBaseURLConfig {
  selectedPreset: 'freellmapi' | 'custom'
  customUrl: string
  apiKey: string
}

function loadApiKeys(): ApiKeys {
  try {
    const raw = localStorage.getItem(API_KEYS_STORAGE_KEY)
    if (raw) return JSON.parse(raw) as ApiKeys
  } catch {}
  return { openai: '', composio: '', stt: '', tts: '' }
}

function saveApiKeys(keys: ApiKeys) {
  localStorage.setItem(API_KEYS_STORAGE_KEY, JSON.stringify(keys))
  if (typeof window !== 'undefined' && (window as any).jarvisAPI) {
    ;(window as any).jarvisAPI.send('api-keys-updated', keys)
  }
}

function loadLlmConfig(): LLMBaseURLConfig {
  try {
    const raw = localStorage.getItem(LLM_CONFIG_STORAGE_KEY)
    if (raw) return JSON.parse(raw) as LLMBaseURLConfig
  } catch {}
  return {
    selectedPreset: 'freellmapi',
    customUrl: 'http://127.0.0.1:31415',
    apiKey: '',
  }
}

function saveLlmConfig(cfg: LLMBaseURLConfig) {
  localStorage.setItem(LLM_CONFIG_STORAGE_KEY, JSON.stringify(cfg))
  if (typeof window !== 'undefined' && (window as any).jarvisAPI) {
    ;(window as any).jarvisAPI.send('llm-config-updated', cfg)
  }
}

function loadKarionConfig(): KarionPairingConfig | null {
  try {
    const raw = localStorage.getItem(KARION_CONFIG_STORAGE_KEY)
    if (raw) return JSON.parse(raw) as KarionPairingConfig
  } catch {}
  return null
}

export default function SettingsPanel() {
  const initialLlm = loadLlmConfig()
  const initialKarion = loadKarionConfig()

  const [voiceSTT, setVoiceSTT] = useState(true)
  const [voiceTTS, setVoiceTTS] = useState(true)
  const [holoEffects, setHoloEffects] = useState(true)
  const [keys, setKeys] = useState<ApiKeys>(loadApiKeys)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved'>('idle')

  const [llmPreset, setLlmPreset] = useState<'freellmapi' | 'custom'>(initialLlm.selectedPreset)
  const [llmCustomUrl, setLlmCustomUrl] = useState(initialLlm.customUrl)
  const [llmApiKey, setLlmApiKey] = useState(initialLlm.apiKey)

  const [karionCfg, setKarionCfg] = useState<KarionPairingConfig | null>(initialKarion)
  const [operatorUid, setOperatorUid] = useState(initialKarion?.operatorUid ?? '')
  const [e2eeKey, setE2eeKey] = useState(initialKarion?.e2eeSessionKey ?? '')
  const [firebaseJson, setFirebaseJson] = useState(
    initialKarion?.firebaseConfig ? JSON.stringify(initialKarion.firebaseConfig, null, 2) : ''
  )
  const [karionStatus, setKarionStatus] = useState<'idle' | 'pairing' | 'paired' | 'error'>(
    initialKarion ? 'paired' : 'idle'
  )
  const [karionError, setKarionError] = useState('')

  useEffect(() => {
    const handler = () => setKeys(loadApiKeys())
    window.addEventListener('storage', handler)
    return () => window.removeEventListener('storage', handler)
  }, [])

  useEffect(() => {
    saveLlmConfig({
      selectedPreset: llmPreset,
      customUrl: llmPreset === 'freellmapi' ? 'http://127.0.0.1:31415' : llmCustomUrl,
      apiKey: llmApiKey,
    })
  }, [llmPreset, llmCustomUrl, llmApiKey])

  const handleKeyChange = (field: keyof ApiKeys, value: string) => {
    setKeys((prev) => {
      const next = { ...prev, [field]: value }
      saveApiKeys(next)
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 1500)
      return next
    })
  }

  const handleKarionPair = async () => {
    setKarionError('')
    if (!operatorUid.trim() || !e2eeKey.trim()) {
      setKarionStatus('error')
      setKarionError('Operator UID and Base64 E2EE Session Key are required.')
      return
    }

    let parsedFirebase: FirebaseConfig = {
      apiKey: '',
      authDomain: '',
      projectId: '',
      storageBucket: '',
      messagingSenderId: '',
      appId: '',
    }

    if (firebaseJson.trim()) {
      try {
        parsedFirebase = { ...parsedFirebase, ...JSON.parse(firebaseJson) }
      } catch {
        setKarionStatus('error')
        setKarionError('Invalid Firebase Config JSON.')
        return
      }
    }

    setKarionStatus('pairing')
    const nextCfg: KarionPairingConfig = {
      firebaseConfig: parsedFirebase,
      operatorUid: operatorUid.trim(),
      e2eeSessionKey: e2eeKey.trim(),
    }

    try {
      localStorage.setItem(KARION_CONFIG_STORAGE_KEY, JSON.stringify(nextCfg))
      if (typeof window !== 'undefined' && (window as any).jarvisAPI) {
        if ((window as any).jarvisAPI.invoke) {
          await (window as any).jarvisAPI.invoke('karion:pair', nextCfg)
        } else {
          ;(window as any).jarvisAPI.send('karion-pairing-updated', nextCfg)
        }
      }
      setKarionCfg(nextCfg)
      setKarionStatus('paired')
    } catch (err: any) {
      setKarionStatus('error')
      setKarionError(err?.message || 'Failed to pair KARION workstation bridge.')
    }
  }

  const keyFields: { field: keyof ApiKeys; label: string; desc: string; placeholder: string }[] = [
    { field: 'openai', label: 'OpenAI / Custom LLM', desc: 'Base URL + key for LLM inference', placeholder: 'sk-... or http://127.0.0.1:31415' },
    { field: 'composio', label: 'Composio API Key', desc: 'App-level key for social integrations', placeholder: 'app_xxx...' },
    { field: 'stt', label: 'Speech-to-Text (STT)', desc: 'Whisper / transcription endpoint key', placeholder: 'sk-whisper-...' },
    { field: 'tts', label: 'Text-to-Speech (TTS)', desc: 'Neural voice synthesis key', placeholder: 'sk-tts-...' },
  ]

  return (
    <div className="workspace overflow-y-auto">
      <div className="hero-head mb-[23px]">
        <div>
          <div className="eyebrow flex items-center gap-[9px] text-[#70a9bb]">
            <span className="eyebrow-line w-[20px] h-[1px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan)] inline-block"></span>
            SYSTEM CONFIGURATION
          </div>
          <h1 className="font-display font-medium text-[clamp(34px,4vw,49px)] leading-[1] tracking-[.015em] text-[#e4f6fa] mt-[11px] mb-[7px]">
            Settings<span className="text-[var(--cyan)]">.</span>
          </h1>
          <p className="text-[11px] text-[var(--muted)]">Interface preferences and backend connection parameters.</p>
        </div>
      </div>

      <div className="overview-grid grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-[14px] pb-[96px]">
        {/* Voice Interface */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">01 / VOICE</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Speech interface</h2>
          </div>
          <div className="p-[14px_18px] space-y-4">
            {[
              { label: 'Speech-to-Text', desc: 'Convert voice commands to text', value: voiceSTT, set: setVoiceSTT },
              { label: 'Text-to-Speech', desc: 'Convert JARVIS responses to voice', value: voiceTTS, set: setVoiceTTS },
              { label: 'Wake Word ("Hey Jarvis")', desc: 'Listen for activation phrase continuously', value: voiceSTT, set: setVoiceSTT },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <div>
                  <div className="text-[11px] text-[#b8d4dc]">{item.label}</div>
                  <div className="text-[9px] text-[#577584] mt-[2px]">{item.desc}</div>
                </div>
                <button
                  onClick={() => item.set(!item.value)}
                  className={`w-[32px] h-[17px] rounded-full relative transition-colors ${item.value ? 'bg-[var(--cyan)]' : 'bg-[#183241]'}`}
                >
                  <span className={`absolute top-[2px] w-[13px] h-[13px] rounded-full bg-white transition-all ${item.value ? 'left-[17px]' : 'left-[2px]'}`}></span>
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Appearance */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">02 / VISUAL</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">Appearance</h2>
          </div>
          <div className="p-[14px_18px] space-y-4">
            {[
              { label: 'Hologram Effects', desc: 'Enable glow and pulse animations', value: holoEffects, set: setHoloEffects },
              { label: 'Scan Lines', desc: 'CRT-style scanline overlay', value: true, set: () => {} },
              { label: 'Noise Grain', desc: 'Film grain texture overlay', value: true, set: () => {} },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <div>
                  <div className="text-[11px] text-[#b8d4dc]">{item.label}</div>
                  <div className="text-[9px] text-[#577584] mt-[2px]">{item.desc}</div>
                </div>
                <button
                  onClick={() => item.set(!item.value)}
                  className={`w-[32px] h-[17px] rounded-full relative transition-colors ${item.value ? 'bg-[var(--cyan)]' : 'bg-[#183241]'}`}
                >
                  <span className={`absolute top-[2px] w-[13px] h-[13px] rounded-full bg-white transition-all ${item.value ? 'left-[17px]' : 'left-[2px]'}`}></span>
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* LLM Base URL */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)]">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">03 / CONNECTION</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">LLM base URL</h2>
          </div>
          <div className="p-[14px_18px] space-y-4">
            <div>
              <div className="text-[10px] text-[#b8d4dc] mb-[6px]">Preset</div>
              <div className="flex gap-[8px]">
                {[
                  { id: 'freellmapi', label: 'Local FreeLLMAPI', url: 'http://127.0.0.1:31415' },
                  { id: 'custom', label: 'Custom Endpoint', url: '' },
                ].map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      setLlmPreset(p.id as 'freellmapi' | 'custom')
                      if (p.id === 'freellmapi') setLlmCustomUrl('http://127.0.0.1:31415')
                    }}
                    className={`px-[12px] py-[6px] text-[9px] tracking-[.08em] border transition-colors ${
                      llmPreset === p.id
                        ? 'bg-[var(--cyan)] text-[#04111a] border-[var(--cyan)]'
                        : 'text-[#b8d4dc] border-[#276077] hover:border-[var(--cyan)]'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[#b8d4dc] mb-[4px]">Base URL</div>
              <input
                type="text"
                value={llmPreset === 'freellmapi' ? 'http://127.0.0.1:31415' : llmCustomUrl}
                onChange={(e) => {
                  setLlmPreset('custom')
                  setLlmCustomUrl(e.target.value)
                }}
                placeholder="http://127.0.0.1:31415"
                className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[6px] text-[10px] text-[var(--ice)] font-mono outline-none focus:border-[var(--cyan)]"
              />
            </div>
            <div>
              <div className="text-[10px] text-[#b8d4dc] mb-[4px]">API Key</div>
              <input
                type="password"
                value={llmApiKey}
                onChange={(e) => setLlmApiKey(e.target.value)}
                placeholder="freellmapi-..."
                className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[6px] text-[10px] text-[var(--ice)] font-mono outline-none focus:border-[var(--cyan)]"
              />
            </div>
            <div className="text-[8px] text-[#577584] pt-[2px]">
              Active endpoint used by the JARVIS assistant chat pipeline. Local FreeLLMAPI is the default.
            </div>
          </div>
        </section>

        {/* API Keys */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)] col-span-1 md:col-span-2 xl:col-span-1">
          <div className="panel-top relative px-[18px] pt-[16px]">
            <span className="section-index text-[8px] text-[#648c9d] block">04 / AUTH</span>
            <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">API credentials</h2>
          </div>
          <div className="max-h-[360px] overflow-y-auto p-[14px_18px] space-y-4">
            {keyFields.map(({ field, label, desc, placeholder }) => (
              <div key={field}>
                <div className="text-[11px] text-[#b8d4dc] mb-[4px]">{label}</div>
                <div className="text-[9px] text-[#577584] mb-[5px]">{desc}</div>
                <input
                  type="password"
                  value={keys[field]}
                  onChange={(e) => handleKeyChange(field, e.target.value)}
                  placeholder={placeholder}
                  className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[7px] text-[10px] text-[var(--ice)] placeholder-[#607e8c] outline-none focus:border-[var(--cyan)] transition-colors font-mono"
                />
              </div>
            ))}
            <div className="text-[8px] text-[#577584] pt-[4px]">
              Stored locally in browser storage. Sent to backend on each request. Keys are never logged.
            </div>
          </div>
          {saveStatus === 'saved' && (
            <div className="mx-[18px] mb-[12px] px-[10px] py-[6px] bg-[rgba(123,242,193,0.07)] border border-[rgba(123,242,193,0.2)] text-[9px] text-[var(--green)] tracking-[.08em]">
              ✓ CREDENTIALS SAVED LOCALLY
            </div>
          )}
        </section>

        {/* KARION Mobile Pairing */}
        <section className="panel border border-[var(--line)] overflow-hidden relative before:absolute before:top-0 before:left-0 before:w-[34px] before:h-[1px] before:bg-[var(--cyan)] before:shadow-[0_0_9px_var(--cyan)] col-span-1 md:col-span-2 xl:col-span-2">
          <div className="panel-top relative px-[18px] pt-[16px] flex items-center justify-between">
            <div>
              <span className="section-index text-[8px] text-[#648c9d] block">05 / TELEPHONY &amp; SYNC</span>
              <h2 className="font-display font-medium text-[18px] tracking-[.035em] text-[#d9f3f9] mt-[4px] mb-0">
                KARION Mobile Pairing
              </h2>
            </div>
            <span
              className={`px-[8px] py-[3px] text-[8px] tracking-[.1em] border font-mono ${
                karionStatus === 'paired'
                  ? 'border-[rgba(123,242,193,0.35)] text-[var(--green)] bg-[rgba(123,242,193,0.07)]'
                  : karionStatus === 'error'
                  ? 'border-red-500/40 text-red-400 bg-red-500/10'
                  : 'border-[#276077] text-[#648c9d]'
              }`}
            >
              {karionStatus === 'paired'
                ? 'BRIDGE PAIRED'
                : karionStatus === 'pairing'
                ? 'PAIRING...'
                : karionStatus === 'error'
                ? 'PAIRING ERROR'
                : 'UNPAIRED'}
            </span>
          </div>

          <div className="p-[14px_18px] space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-[12px]">
              <div>
                <div className="text-[11px] text-[#b8d4dc] mb-[4px]">Operator UID</div>
                <div className="text-[9px] text-[#577584] mb-[5px]">Firebase Auth UID from KARION Android profile</div>
                <input
                  type="text"
                  value={operatorUid}
                  onChange={(e) => setOperatorUid(e.target.value)}
                  placeholder="uid_..."
                  className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[7px] text-[10px] text-[var(--ice)] placeholder-[#607e8c] outline-none focus:border-[var(--cyan)] font-mono"
                />
              </div>

              <div>
                <div className="text-[11px] text-[#b8d4dc] mb-[4px]">E2EE Session Key (Base64)</div>
                <div className="text-[9px] text-[#577584] mb-[5px]">256-bit AES-GCM workspace key exported from KARION</div>
                <input
                  type="password"
                  value={e2eeKey}
                  onChange={(e) => setE2eeKey(e.target.value)}
                  placeholder="Base64 AES-256-GCM key..."
                  className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[7px] text-[10px] text-[var(--ice)] placeholder-[#607e8c] outline-none focus:border-[var(--cyan)] font-mono"
                />
              </div>
            </div>

            <div>
              <div className="text-[11px] text-[#b8d4dc] mb-[4px]">Firebase Project Config (JSON)</div>
              <div className="text-[9px] text-[#577584] mb-[5px]">
                Paste your Firebase web config object to sync /users/{'{uid}'}/call_requests, tasks, and focus_sessions
              </div>
              <textarea
                rows={4}
                value={firebaseJson}
                onChange={(e) => setFirebaseJson(e.target.value)}
                placeholder={'{\n  "apiKey": "...",\n  "authDomain": "...",\n  "projectId": "..."\n}'}
                className="w-full bg-[rgba(7,20,31,0.9)] border border-[#276077] px-[10px] py-[7px] text-[10px] text-[var(--ice)] placeholder-[#607e8c] outline-none focus:border-[var(--cyan)] font-mono resize-y"
              />
            </div>

            <div className="flex items-center justify-between pt-[4px]">
              <div className="text-[8px] text-[#577584]">
                {karionCfg
                  ? `Active Operator: ${karionCfg.operatorUid}`
                  : 'Enables PC-directed VoiceAgentBridge calls and E2EE task approval.'}
              </div>
              <button
                onClick={handleKarionPair}
                disabled={karionStatus === 'pairing'}
                className="px-[16px] py-[7px] bg-[var(--cyan)] text-[#04111a] text-[9px] font-semibold tracking-[.1em] hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {karionStatus === 'paired' ? 'UPDATE PAIRING' : 'PAIR KARION BRIDGE'}
              </button>
            </div>

            {karionError && (
              <div className="px-[10px] py-[6px] bg-red-500/10 border border-red-500/30 text-[9px] text-red-400">
                {karionError}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}