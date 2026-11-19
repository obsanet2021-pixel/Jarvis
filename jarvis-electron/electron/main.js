"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path_1 = __importDefault(require("path"));
const child_process_1 = require("child_process");
let mainWindow = null;
let backendProcess = null;
function createWindow() {
    mainWindow = new electron_1.BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: 'Jarvis - Holographic AI Assistant',
        titleBarStyle: 'hiddenInset',
        trafficLightPosition: { x: 16, y: 16 },
        webPreferences: {
            preload: path_1.default.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
    });
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
        mainWindow.loadURL('http://localhost:5174');
        mainWindow.webContents.openDevTools();
    }
    else {
        mainWindow.loadFile(path_1.default.join(__dirname, '../dist/index.html'));
    }
    mainWindow.webContents.on('console-message', (_event, level, message, line, sourceId) => {
        console.log(`[renderer:${level}] ${message} (${sourceId}:${line})`);
    });
    mainWindow.webContents.on('did-fail-load', (_event, code, description, url) => {
        console.error(`[did-fail-load] ${code} ${description} ${url}`);
    });
    mainWindow.webContents.on('render-process-gone', (_event, details) => {
        console.error(`[render-process-gone] ${JSON.stringify(details)}`);
    });
    mainWindow.webContents.on('did-finish-load', () => {
        mainWindow.webContents.executeJavaScript(`({
            rootChildren: document.getElementById('root')?.childElementCount ?? -1,
            hasAppGrid: !!document.getElementById('app'),
            canvases: document.querySelectorAll('canvas').length,
            text: (document.body.innerText || '').slice(0, 80),
        })`).then((info) => console.log('[dom]', JSON.stringify(info)));
    });
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}
electron_1.app.whenReady().then(() => {
    createWindow();
    electron_1.app.on('activate', () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0)
            createWindow();
    });
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin')
        electron_1.app.quit();
});
electron_1.ipcMain.handle('ping', () => 'pong');
electron_1.ipcMain.handle('api-keys-updated', (_event, keys) => {
    console.log('[IPC] API keys updated:', Object.keys(keys));
    return { success: true };
});
electron_1.ipcMain.handle('backend:launch', async () => {
    if (backendProcess) {
        console.log('[IPC] Backend already running');
        return { success: true, message: 'Backend already running' };
    }
    try {
        const projectRoot = path_1.default.join(__dirname, '..');
        const scriptPath = path_1.default.join(projectRoot, 'api', 'main.py');
        backendProcess = child_process_1.spawn('python', [scriptPath], {
            cwd: projectRoot,
            detached: false,
            stdio: 'ignore',
        });
        backendProcess.on('error', (err) => {
            console.error('[IPC] Failed to start backend:', err.message);
            backendProcess = null;
        });
        backendProcess.unref();
        mainWindow?.webContents.send('backend:status', 'running');
        console.log('[IPC] Backend process started');
        return { success: true, message: 'Backend launched successfully' };
    } catch (err) {
        console.error('[IPC] Backend launch error:', err);
        return { success: false, message: err.message };
    }
});
electron_1.ipcMain.handle('backend:stop', () => {
    if (backendProcess) {
        backendProcess.kill();
        backendProcess = null;
        mainWindow?.webContents.send('backend:status', 'stopped');
        console.log('[IPC] Backend process stopped');
        return { success: true, message: 'Backend stopped' };
    }
    return { success: false, message: 'Backend not running' };
});
electron_1.ipcMain.handle('backend:is-running', () => {
    const isRunning = backendProcess !== null && !backendProcess.killed;
    return { running: isRunning };
});
