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

const { BrowserWindow } = require("electron");
const path = require("path");
const { isDev } = require("./env");
const log = require("./logger");

let mainWindow = null;
const secondaryWindows = {};

/**
 * Creates the main BrowserWindow (single instance).
 */
function createMainWindow() {
  log.info("Creating main BrowserWindow...");

  mainWindow = new BrowserWindow({
    width: 96,
    height: 576,
    titleBarStyle: "hidden",
    backgroundColor: "#181818",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
      webSecurity: !isDev,
    },
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  return mainWindow;
}

/**
 * Creates (or focuses) a secondary window, identified by a unique key.
 *
 * @param {Object} options - e.g. { key: "myWindow", route: "/editor", width: 800, height: 600, title: "Editor" }
 * @returns {BrowserWindow} The created (or focused) BrowserWindow
 */
function createSecondaryWindow(options = {}) {
  const {
    key = "secondary", // unique identifier for this window
    route = "",
    width = 800,
    height = 600,
    title = "New Window",
  } = options;

  // If already open, just focus it
  if (secondaryWindows[key]) {
    secondaryWindows[key].focus();
    return secondaryWindows[key];
  }

  log.info(`Creating secondary window for key: ${key}`);

  const newWindow = new BrowserWindow({
    width,
    height,
    titleBarStyle: "hidden",
    titleBarOverlay: {
      color: "#1F1F1F",
      symbolColor: "#5E5E5E",
      height: 47,
    },
    title,
    backgroundColor: "#181818",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
      webSecurity: !isDev,
    },
  });

  if (isDev) {
    newWindow.loadURL(`http://localhost:5173/#${route}`);
    newWindow.webContents.openDevTools();
  } else {
    const distPath = path.join(__dirname, "../dist/index.html");
    newWindow.loadURL(`file://${distPath}#${route}`);
  }

  newWindow.on("closed", () => {
    delete secondaryWindows[key];
  });

  secondaryWindows[key] = newWindow;
  return newWindow;
}

/**
 * Closes a specific secondary window by key (if it exists).
 * @param {string} key - The key used to create the window
 */
function closeSecondaryWindow(key) {
  if (secondaryWindows[key]) {
    secondaryWindows[key].close();
    // The "closed" event will remove it from the registry
  }
}

/**
 * Closes all secondary windows (optional utility if needed).
 */
function closeAllSecondaryWindows() {
  Object.keys(secondaryWindows).forEach((key) => {
    if (secondaryWindows[key]) {
      secondaryWindows[key].close();
    }
  });
}

module.exports = {
  // Main window
  createMainWindow,
  get mainWindow() {
    return mainWindow;
  },

  // Secondary windows
  createSecondaryWindow,
  closeSecondaryWindow,
  closeAllSecondaryWindows,

  get secondaryWindows() {
    return secondaryWindows;
  },
};
