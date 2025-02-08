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
  getPlugins: async () => {
    return await ipcRenderer.invoke("get-plugins");
  },

  getPluginsBasePath: async () => {
    return await ipcRenderer.invoke("get-plugins-base-path");
  },

  rpc(procName, ...args) {
    return ipcRenderer.invoke("send-request", {
      rpc: procName,
      args,
    });
  },

  sendMessage: (message) => ipcRenderer.send("send-message", message),
  sendRequest: (message) => ipcRenderer.invoke("send-request", message),

  openFile: () => ipcRenderer.invoke("dialog:openFile"),
  saveFile: (defaultPath, content, title = "") =>
    ipcRenderer.invoke("dialog:saveFile", defaultPath, content, title),

  openNewWindow: (options) => ipcRenderer.invoke("open-new-window", options),
  closeWindow: (key) => ipcRenderer.invoke("close-window", key),

  resizeWindow: (width, height) =>
    ipcRenderer.send("resize-window", { width, height }),
});
