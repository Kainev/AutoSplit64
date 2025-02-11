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

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  // Paths
  getAppDir: async () => {
    return await ipcRenderer.invoke("get-app-dir");
  },

  // Back-End Communication
  rpc(procName, ...args) {
    return ipcRenderer.invoke("send-request", {
      rpc: procName,
      args,
    });
  },

  onMessage: (callback) => {
    ipcRenderer.on("message", (event, data) => {
      callback(data);
    });
  },

  // File Handling
  openFile: (options) => ipcRenderer.invoke("dialog:openFile", options),

  saveFile: (defaultPath, content, title = "") =>
    ipcRenderer.invoke("dialog:saveFile", defaultPath, content, title),

  readFile: async (filePath) => {
    return await ipcRenderer.invoke("file:read", filePath);
  },

  // Window Handling
  openNewWindow: (options) => ipcRenderer.invoke("open-new-window", options),

  closeWindow: (key) => ipcRenderer.invoke("close-window", key),

  resizeWindow: (width, height) =>
    ipcRenderer.send("resize-window", { width, height }),
});
