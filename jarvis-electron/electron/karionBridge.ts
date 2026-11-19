import * as admin from 'firebase-admin'
import { writeFileSync, mkdirSync, existsSync } from 'fs'
import { join } from 'path'
import { randomUUID, createHash, createDecipheriv } from 'crypto'
import { BrowserWindow, ipcMain, app } from 'electron'

// ── Types ────────────────────────────────────────────────────────────────────
interface FirebaseConfig {
  apiKey: string
  authDomain: string
  projectId: string
  storageBucket: string
  messagingSenderId: string
  appId: string
}

type CallCommandType = 'INITIATE_CALL' | 'CHECK_BALANCE' | 'HANG_UP' | 'VOICE_AGENT_TURN'
type CallExecutionState = 'QUEUED' | 'DIALING' | 'ACTIVE' | 'ENDED' | 'FAILED'
type TaskSyncStatus = 'PENDING_PC' | 'SYNCED_PC' | 'PC_IN_PROGRESS' | 'PC_VERIFIED'
type TaskWorkflowStatus = 'ACTIVE' | 'AWAITING_PC_CHECK' | 'COMPLETED_ON_PC'
type FocusSessionStatus = 'ACTIVE' | 'LOCKED' | 'COMPLETED' | 'OVERRIDDEN'

interface AgentCallRequest {
  id: string; userId: string; command: CallCommandType; phoneNumber: string
  agentScript?: string; ussdCode?: string; requestedBy: 'PC_AGENT' | 'ANDROID_CONSOLE'
  callState: CallExecutionState; transcript?: string; balanceResult?: string
}

interface SyncTask {
  id: string; userId: string; title: string; description: string
  encryptedPayload?: string; encryptionIv?: string; priority: string
  originPlatform: string; syncStatus: TaskSyncStatus; status: TaskWorkflowStatus
  pcApproved: boolean; pcApprovedBy?: string; deadlineEpochMs?: number
}

interface FocusSession {
  id: string; userId: string; label: string; durationMinutes: number
  status: FocusSessionStatus; strictLock: boolean; unfinishedTaskCount: number
  lockedTaskIds: string[]; startedEpochMs: number; endsEpochMs: number
}

interface UserPairing {
  uid: string
  deviceName: string
  e2eeKeyBase64: string // raw 32-byte AES-256 session key, base64-encoded
  pairedAt: number
}

interface KarionBridgeState {
  connected: boolean
  pairing: UserPairing | null
  lastError: string | null
}

// ── AES-256-GCM decrypt (Node equivalent of Android E2eeCryptoManager) ──────
function base64ToBuf(s: string): Buffer {
  const padded = s.replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
  while (padded.length % 4 !== 0) padded += '='
  return Buffer.from(padded, 'base64')
}

function tryDecryptTask(task: SyncTask, key: Buffer): SyncTask {
  if (!task.encryptedPayload || !task.encryptionIv) return task
  try {
    const ct = base64ToBuf(task.encryptedPayload)
    const iv = base64ToBuf(task.encryptionIv).slice(0, 12)
    const cipher = createDecipheriv('aes-256-gcm', key, iv)
    let dec = cipher.update(ct)
    dec = Buffer.concat([dec, cipher.final()])
    const obj = JSON.parse(dec.toString('utf8'))
    return { ...task, title: obj.title ?? task.title, description: obj.description ?? task.description }
  } catch {
    return task
  }
}

// ── Secure config storage in Electron userData ───────────────────────────────
function getConfigPath(): string {
  return join(app.getPath('userData'), 'karion_config.json')
}

function loadConfig(): { firebase?: FirebaseConfig; pairing?: UserPairing } {
  try {
    if (!existsSync(getConfigPath())) return {}
    return JSON.parse(require('fs').readFileSync(getConfigPath(), 'utf8'))
  } catch {
    return {}
  }
}

function saveConfig(cfg: { firebase?: FirebaseConfig; pairing?: UserPairing }): void {
  const dir = join(app.getPath('userData'), 'jarvis')
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
  writeFileSync(getConfigPath(), JSON.stringify(cfg), 'utf8')
}

// ── Singleton state ──────────────────────────────────────────────────────────
let _state: KarionBridgeState = { connected: false, pairing: null, lastError: null }
let _db: admin.firestore.Firestore | null = null
let _keyBuf: Buffer | null = null

function ensureAdmin(firebaseCfg: FirebaseConfig): admin.app.App {
  if (admin.apps.length === 0) {
    admin.initializeApp({
      credential: admin.credential.cert({
        projectId: firebaseCfg.projectId,
        privateKey: process.env.KARION_SA_KEY ?? null,
        clientEmail: process.env.KARION_SA_EMAIL ?? null,
      }),
      databaseURL: `https://${firebaseCfg.projectId}.firebaseio.com`,
    })
  }
  return admin.apps[0]
}

function getDb(firebaseCfg?: FirebaseConfig): admin.firestore.Firestore {
  if (!_db) {
    const cfg = firebaseCfg ?? loadConfig().firebase
    if (!cfg) throw new Error('Firebase config not set — pair in Settings first')
    ensureAdmin(cfg)
    _db = admin.firestore.getFirestore()
  }
  return _db
}

// ── Firestore operations ─────────────────────────────────────────────────────
async function createUserProfile(uid: string, displayName: string): Promise<void> {
  const db = getDb()
  const ref = db.collection('users').doc(uid)
  const snap = await ref.get()
  const now = admin.firestore.FieldValue.serverTimestamp()
  if (!snap.exists) {
    await ref.set({
      userId: uid, displayName, assistantName: 'Nexus',
      assistantPersona: 'Direct, high-clarity productivity strategist focused on strict deadlines.',
      pcDeviceName: 'Workstation-PC', focusLockArmed: true,
      strictModeEnabled: true, aiVoiceCredits: 500, createdAt: now, updatedAt: now,
    }, { merge: true })
  } else {
    await ref.update({ updatedAt: now })
  }
}

async function dispatchCallRequest(
  userId: string, command: CallCommandType, phoneNumber: string,
  agentScript: string = '', ussdCode?: string
): Promise<string> {
  const db = getDb()
  const docRef = db.collection('users').doc(userId).collection('call_requests').doc(randomUUID())
  await docRef.set({
    userId, command, phoneNumber: phoneNumber.slice(0, 32),
    agentScript: agentScript.slice(0, 1000),
    ...(ussdCode ? { ussdCode: ussdCode.slice(0, 32) } : {}),
    requestedBy: 'PC_AGENT', callState: 'QUEUED',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  })
  return docRef.id
}

async function hangUp(userId: string): Promise<void> {
  await dispatchCallRequest(userId, 'HANG_UP', '')
}

async function checkBalance(userId: string, phoneNumber: string = ''): Promise<string> {
  await dispatchCallRequest(userId, 'CHECK_BALANCE', phoneNumber)
  return ''
}

async function setFocusLock(userId: string, armed: boolean): Promise<void> {
  const db = getDb()
  await db.collection('users').doc(userId).update({
    focusLockArmed: armed, updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  })
}

async function approveTask(userId: string, taskId: string, agentName: string): Promise<void> {
  const db = getDb()
  await db.collection('users').doc(userId).collection('tasks').doc(taskId).update({
    pcApproved: true, pcApprovedBy: agentName.slice(0, 80) || 'Workstation-PC',
    syncStatus: 'PC_VERIFIED', status: 'COMPLETED_ON_PC',
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  })
}

async function finishFocusSession(userId: string, sessionId: string, status: FocusSessionStatus): Promise<void> {
  const db = getDb()
  await db.collection('users').doc(userId).collection('focus_sessions').doc(sessionId).update({
    status, updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  })
}

// ── Fetch helpers ────────────────────────────────────────────────────────────
async function fetchTasks(userId: string): Promise<SyncTask[]> {
  const db = getDb()
  const snap = await db.collection('users').doc(userId).collection('tasks')
    .orderBy('createdAt', 'desc').limit(50).get()
  return snap.docs.map(d => ({ ...d.data() as SyncTask, id: d.id })).map(t =>
    _keyBuf ? tryDecryptTask(t, _keyBuf) : t
  )
}

async function fetchFocusSessions(userId: string): Promise<FocusSession[]> {
  const db = getDb()
  const snap = await db.collection('users').doc(userId).collection('focus_sessions')
    .orderBy('createdAt', 'desc').limit(20).get()
  return snap.docs.map(d => ({ ...d.data() as FocusSession, id: d.id }))
}

async function fetchCallRequests(userId: string): Promise<AgentCallRequest[]> {
  const db = getDb()
  const snap = await db.collection('users').doc(userId).collection('call_requests')
    .orderBy('createdAt', 'desc').limit(20).get()
  return snap.docs.map(d => ({ ...d.data() as AgentCallRequest, id: d.id }))
}

async function fetchProfile(userId: string): Promise<any> {
  const db = getDb()
  const snap = await db.collection('users').doc(userId).get()
  return snap.exists ? { id: snap.id, ...snap.data() } : null
}

// ── Pairing ──────────────────────────────────────────────────────────────────
async function pairWithKarion(
  firebaseCfg: FirebaseConfig, uid: string, keyBase64: string,
  deviceName: string = 'Workstation-PC'
): Promise<{ status: string; fingerprint: string }> {
  const decoded = Buffer.from(keyBase64.trim(), 'base64')
  if (decoded.length !== 32) throw new Error('E2EE key must be exactly 32 bytes (256-bit AES)')
  _keyBuf = decoded
  const hash = createHash('sha256').update(decoded).digest()
  const fingerprint = Array.from(hash).slice(0, 8).map(b => b.toString(16).padStart(2, '0')).join(':')
  const pairing: UserPairing = { uid, deviceName, e2eeKeyBase64: keyBase64.trim(), pairedAt: Date.now() }
  saveConfig({ firebase: firebaseCfg, pairing })
  _state = { connected: true, pairing, lastError: null }
  try {
    await createUserProfile(uid, deviceName)
    _state.lastError = null
  } catch (e: any) {
    _state.lastError = e.message
  }
  return { status: _state.lastError ? 'error' : 'ok', fingerprint }
}

async function getCurrentState(): Promise<KarionBridgeState & { keyLength?: number }> {
  return { ..._state, ...(_keyBuf ? { keyLength: _keyBuf.length } : {}) }
}

// ── IPC handlers ─────────────────────────────────────────────────────────────
function registerHandlers(win: BrowserWindow): void {
  const handle = (channel: string, factory: (...args: any[]) => Promise<any>) => {
    ipcMain.handle(channel, async (_event, ...args) => {
      try {
        const result = await factory(...args)
        return { ok: true, data: result }
      } catch (e: any) {
        _state.lastError = e.message
        return { ok: false, error: e.message }
      }
    })
  }

  handle('karion:pair', (firebaseCfg: FirebaseConfig, uid: string, keyBase64: string, deviceName: string) =>
    pairWithKarion(firebaseCfg, uid, keyBase64, deviceName))
  handle('karion:state', () => getCurrentState())
  handle('karion:profile', (uid: string) => fetchProfile(uid))
  handle('karion:tasks', (uid: string) => fetchTasks(uid))
  handle('karion:approve-task', (uid: string, taskId: string, agentName: string) =>
    approveTask(uid, taskId, agentName))
  handle('karion:focus-sessions', (uid: string) => fetchFocusSessions(uid))
  handle('karion:set-focus-lock', (uid: string, armed: boolean) => setFocusLock(uid, armed))
  handle('karion:finish-focus-session', (uid: string, sessionId: string, status: FocusSessionStatus) =>
    finishFocusSession(uid, sessionId, status))
  handle('karion:dispatch-call', (uid: string, command: CallCommandType, phoneNumber: string,
    agentScript: string, ussdCode?: string) =>
    dispatchCallRequest(uid, command, phoneNumber, agentScript, ussdCode))
  handle('karion:hang-up', (uid: string) => hangUp(uid))
  handle('karion:check-balance', (uid: string, phoneNumber: string) => checkBalance(uid, phoneNumber))
  handle('karion:call-requests', (uid: string) => fetchCallRequests(uid))
}

export { registerHandlers, _state as karionState }
