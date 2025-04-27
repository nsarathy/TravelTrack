const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let djangoServer = null;
let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,   // security best practice
      contextIsolation: true,   // security best practice
    },
    show: false   // only show after ready
  });

  // Load frontend built files (dist/index.html)
  mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    // mainWindow.webContents.openDevTools();  // Uncomment if you want to debug
  });

  mainWindow.on('closed', () => {
    if (djangoServer) {
      djangoServer.kill('SIGTERM');
      djangoServer = null;
    }
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Path to the bundled Django backend executable
  const djangoExePath = path.join(__dirname, 'backend', 'django-server.exe');

  // Start the Django server
  djangoServer = spawn(djangoExePath, [], {
    cwd: path.join(__dirname, 'backend')  // set working directory to backend/
  });

  // Log Django output (optional)
  djangoServer.stdout.on('data', (data) => {
    console.log(`Django: ${data.toString()}`);
  });

  djangoServer.stderr.on('data', (data) => {
    console.error(`Django Error: ${data.toString()}`);
  });

  djangoServer.on('close', (code) => {
    console.log(`Django server exited with code ${code}`);
  });

  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    if (djangoServer) {
      djangoServer.kill('SIGTERM');
      djangoServer = null;
    }
    app.quit();
  }
});
