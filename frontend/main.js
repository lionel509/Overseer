const { app, BrowserWindow } = require('electron');

function createWindow () {
  const win = new BrowserWindow({
    minWidth: 950,
    minHeight: 800,
    width: 950, 
    height: 800,
    webPreferences: {
      nodeIntegration: true
    }
  })

  win.loadURL('http://localhost:5173')
}

app.whenReady().then(createWindow)