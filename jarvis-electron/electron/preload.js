"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
electron_1.contextBridge.exposeInMainWorld('jarvisAPI', {
    invoke: (channel, ...args) => electron_1.ipcRenderer.invoke(channel, ...args),
    on: (channel, func) => {
        const subscription = (_event, ...args) => func(...args);
        electron_1.ipcRenderer.on(channel, subscription);
        return () => electron_1.ipcRenderer.removeListener(channel, subscription);
    },
    send: (channel, ...args) => electron_1.ipcRenderer.send(channel, ...args),
});

// Backend management helpers
electron_1.contextBridge.exposeInMainWorld('jarvisBackend', {
    launchBackend: () => electron_1.ipcRenderer.invoke('backend:launch'),
    stopBackend: () => electron_1.ipcRenderer.invoke('backend:stop'),
    isRunning: () => electron_1.ipcRenderer.invoke('backend:is-running'),
    onStatusChange: (callback) => {
        const handler = (_event, status) => callback(status);
        electron_1.ipcRenderer.on('backend:status', handler);
        return () => electron_1.ipcRenderer.removeListener('backend:status', handler);
    },
});
