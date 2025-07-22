import { app, BrowserWindow, screen, ipcMain, shell, globalShortcut } from 'electron';
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

const toggleWindow = () => {
  if (!mainWindow) {
    createWindow();
    return;
  }

  if (mainWindow.isVisible()) {
    mainWindow.hide();
  } else {
    // Center the window before showing
    const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
    mainWindow.setPosition(
      Math.floor((screenWidth - 800) / 2),
      Math.floor((screenHeight - 400) / 2)
    );
    mainWindow.show();
    mainWindow.focus();
  }
};

const createWindow = (): void => {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 800,
    height: 400,
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
    show: false, // Start hidden, show on shortcut
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false, // Remove window shadow
  });

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
};

// This method will be called when Electron has finished initialization
app.on('ready', () => {
  createWindow();

  // Register global shortcut (Command+Option+Space on macOS, Ctrl+Alt+Space on others)
  const shortcut = process.platform === 'darwin' ? 'Command+Control+Space' : 'Ctrl+Alt+Space';
  const registered = globalShortcut.register(shortcut, () => {
    toggleWindow();
  });

  if (!registered) {
    console.log('Shortcut registration failed');
  }
});

// IPC event handlers
ipcMain.handle('search-query', async (event, query: string, fileType: string) => {
  // This handler receives search queries from the renderer
  console.log('Search query received:', query, 'File type:', fileType);
  
  try {
    // Make API call to webhook.site for testing
    const response = await fetch(`http://localhost:4000/files?search=${query}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    console.log('API response:', data);
    return { success: true, data };
  } catch (error) {
    console.error('API call failed:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
});

// Handler to open file location
ipcMain.handle('open-file-location', async (event, filePath: string) => {
  try {
    // Show the file in its folder
    shell.showItemInFolder(filePath);
  } catch (error) {
    console.error('Failed to open file location:', error);
  }
});

// Handler to open file
ipcMain.handle('open-file', async (event, filePath: string) => {
  try {
    // Open the file with default application
    shell.openPath(filePath);
  } catch (error) {
    console.error('Failed to open file:', error);
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

// Clean up shortcuts when quitting
app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
