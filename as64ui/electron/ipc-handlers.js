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
const path = require("path");
const fs = require("fs");
const log = require("./logger");
const { sendMessage, sendRequest } = require("./pipe");
const { isDev } = require("./env");
const { createSecondaryWindow, mainWindow } = require("./window-manager");

function setupIPC() {
  const pluginsDir = isDev
    ? path.resolve(__dirname, process.env.PLUGINS_DEV_PATH || "../../plugins")
    : path.join(
        app.getPath("exe"),
        process.env.PLUGINS_PROD_PATH || "../plugins"
      );

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

  ipcMain.handle("get-plugins", () => {
    log.debug(`IPC: 'get-plugins' called. Checking directory: ${pluginsDir}`);
    try {
      if (!fs.existsSync(pluginsDir)) {
        log.info("Plugins directory does not exist.");
        return [];
      }
      const pluginList = fs.readdirSync(pluginsDir).filter((pluginName) => {
        const pluginPath = path.join(
          pluginsDir,
          pluginName,
          `${pluginName}.mjs`
        );
        return fs.existsSync(pluginPath);
      });
      log.debug("Found plugins:", pluginList);
      return pluginList;
    } catch (err) {
      log.error(`Error reading plugins directory '${pluginsDir}':`, err);
      return [];
    }
  });

  ipcMain.handle("get-plugins-base-path", () => {
    return pluginsDir;
  });

  ipcMain.on("resize-window", (event, { width, height }) => {
    if (mainWindow) {
      const currentBounds = mainWindow.getBounds();
      mainWindow.setBounds({
        width,
        height,
        x: currentBounds.x,
        y: currentBounds.y,
      });
    }
  });

  ipcMain.handle("open-new-window", (event, options) => {
    return createSecondaryWindow(options);
  });

  ipcMain.handle("close-window", (event, key) => {
    closeSecondaryWindow(key);
  });

  ipcMain.handle("dialog:openFile", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
      filters: [{ name: "TOML Files", extensions: ["toml"] }],
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

module.exports = {
  setupIPC,
};
