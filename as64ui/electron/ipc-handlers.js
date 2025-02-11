/*
 * AutoSplit64
 *
 * Copyright (C) 2025 Kainev
 *
 * This project is currently not open source and is under active development.
 * You may view the code, but it is not licensed for distribution, modification, or use at this time.
 *
 * For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license
 */

const { ipcMain, dialog, app } = require("electron");
const fs = require("fs");
const log = require("./logger");
const { sendMessage, sendRequest } = require("./pipe");
const windowManager = require("./window-manager");

function setupFileHandling() {
  ipcMain.handle("dialog:openFile", async (options = {}) => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
      ...options,
      properties: ["openFile"],
    });
    if (canceled) {
      return null;
    } else {
      const filePath = filePaths[0];
      const data = fs.readFileSync(filePath, "utf-8");
      return { filePath, data };
    }
  });

  ipcMain.handle("file:read", async (event, filePath) => {
    return new Promise((resolve, reject) => {
      fs.readFile(filePath, "utf-8", (err, data) => {
        if (err) {
          console.error("Error reading file:", err);
          reject(err);
        } else {
          resolve(data);
        }
      });
    });
  });

  ipcMain.handle("dialog:saveFile", async (event, filePath, content, title) => {
    if (filePath) {
      log.debug("Saving file to existing path:", filePath);
      fs.writeFileSync(filePath, content, "utf-8");
      return filePath;
    } else {
      try {
        const { canceled, filePath: newPath } = await dialog.showSaveDialog({
          defaultPath: `${title}.toml`,
          filters: [{ name: "TOML", extensions: ["toml"] }],
        });
        if (canceled || !newPath) {
          return { success: false };
        }
        fs.writeFileSync(newPath, content, "utf-8");
        return { success: true, path: newPath };
      } catch (error) {
        log.error("Error overwriting file:", error);
        return { success: false, error };
      }
    }
  });
}

function setupWindowHandling() {
  ipcMain.on("resize-window", (event, { width, height }) => {
    if (windowManager.mainWindow) {
      const currentBounds = windowManager.mainWindow.getBounds();
      windowManager.mainWindow.setBounds({
        width,
        height,
        x: currentBounds.x,
        y: currentBounds.y,
      });
    }
  });

  ipcMain.handle("open-new-window", (event, options) => {
    windowManager.createSecondaryWindow(options);
  });

  ipcMain.handle("close-window", (event, key) => {
    windowManager.closeSecondaryWindow(key);
  });
}

function setupCommunicationHandling() {
  ipcMain.on("send-message", (event, message) => {
    log.debug("IPC received send-message:", message);
    sendMessage(message);
  });

  ipcMain.handle("send-request", async (event, message) => {
    try {
      const result = await sendRequest(message);
      return result;
    } catch (err) {
      log.error("Error handling send-request:", err);
      throw err;
    }
  });
}

function setupPathHandling() {
  const appDir = app.getPath("exe");

  ipcMain.handle("get-app-dir", () => {
    return appDir;
  });
}

function setupIPC() {
  setupCommunicationHandling();
  setupWindowHandling();
  setupFileHandling();
  setupPathHandling();
}

module.exports = {
  setupIPC,
};
