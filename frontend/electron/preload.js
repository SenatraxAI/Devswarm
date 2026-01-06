const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // Add any Electron-specific APIs here
    getVersion: () => process.versions.electron,
});
