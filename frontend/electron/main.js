const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let mainWindow;
let pythonProcess;

// Check if backend is ready
function checkBackend(retries = 30, delay = 1000) {
    return new Promise((resolve, reject) => {
        const attempt = (retriesLeft) => {
            http.get('http://127.0.0.1:8000/health', (res) => {
                if (res.statusCode === 200) {
                    console.log('✅ Backend is ready');
                    resolve(true);
                } else if (retriesLeft > 0) {
                    setTimeout(() => attempt(retriesLeft - 1), delay);
                } else {
                    reject(new Error('Backend failed to start'));
                }
            }).on('error', () => {
                if (retriesLeft > 0) {
                    setTimeout(() => attempt(retriesLeft - 1), delay);
                } else {
                    reject(new Error('Backend failed to start'));
                }
            });
        };
        attempt(retries);
    });
}

// Start Python backend
function startPythonBackend() {
    console.log('🚀 Starting Python backend...');

    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(__dirname, '../../backend/main.py');

    pythonProcess = spawn(pythonPath, [scriptPath], {
        cwd: path.join(__dirname, '../../backend'),
        stdio: 'inherit'
    });

    pythonProcess.on('error', (err) => {
        console.error('❌ Failed to start Python backend:', err);
    });

    pythonProcess.on('exit', (code) => {
        console.log(`🛑 Python backend exited with code ${code}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        backgroundColor: '#0f172a',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false
    });

    // Load the frontend
    const frontendPath = path.join(__dirname, '../out/index.html');
    mainWindow.loadFile(frontendPath);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        console.log('✅ DevSwarm window ready');
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(async () => {
    console.log('🎯 DevSwarm starting...');

    // Start backend
    startPythonBackend();

    // Wait for backend to be ready
    try {
        await checkBackend();
        // Create window after backend is ready
        createWindow();
    } catch (err) {
        console.error('❌ Error starting backend:', err);
        app.quit();
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});
