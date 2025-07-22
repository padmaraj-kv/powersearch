import { app, BrowserWindow, screen, ipcMain } from 'electron';
import path from 'node:path';
// @ts-ignore - electron-squirrel-startup doesn't have types but returns a simple boolean
import started from 'electron-squirrel-startup';

// Declare Vite-injected variables
declare const MAIN_WINDOW_VITE_DEV_SERVER_URL: string | undefined;
declare const MAIN_WINDOW_VITE_NAME: string;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

let mainWindow: BrowserWindow | null = null;

const createWindow = (): void => {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 800,
    height: 400, // Increased for debugging
    frame: false,
    transparent: true,
    backgroundColor: '#00000000', // Fully transparent background
    resizable: false,
    movable: false,
    // vibrancy: 'under-window', // Re-enabled for better glass effect on macOS
    x: Math.floor((screenWidth - 800) / 2), // Center horizontally
    y: Math.floor((screenHeight - 400) / 2), // Center vertically
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      backgroundThrottling: false, // Prevent throttling when window is hidden
    },
    show: true, // Show by default since no shortcut
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false, // Remove window shadow
  });

  // Ensure window stays transparent
  mainWindow.setBackgroundColor('#00000000');
  
  // Load the app
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
  }

  // Hide window when it loses focus
  mainWindow.on('blur', () => {
    if (mainWindow && mainWindow.isVisible()) {
      mainWindow.hide();
    }
  });

  // Show window when clicked on dock/taskbar
  mainWindow.on('show', () => {
    if (mainWindow) {
      mainWindow.focus();
    }
  });
  
  // Remove detached devtools as it might interfere with transparency
  // mainWindow.webContents.openDevTools({ mode: 'detach' });

  // Remove automatic DevTools opening
  // if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
  // }
};

// This method will be called when Electron has finished initialization
app.on('ready', () => {
  createWindow();
});

// IPC event handlers
ipcMain.handle('search-query', async (event, query: string, fileType: string) => {
  // This handler receives search queries from the renderer
  console.log('Search query received:', query, 'File type:', fileType);
  
  try {
    // Make API call to webhook.site for testing
    const response = await fetch('https://webhook.site/6c743397-0ee2-4982-a42c-e0649599063c', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        query,
        fileType 
      }),
    });
    
    const data = await response.text(); // webhook.site returns text, not JSON
    return { success: true, data };
  } catch (error) {
    console.error('API call failed:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else if (mainWindow) {
    // Show the existing window if it's hidden
    mainWindow.show();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
