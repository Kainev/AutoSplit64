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

const { BrowserWindow, screen } = require("electron");
const path = require("path");
const { isDev } = require("./env");
const log = require("./logger");

let splashWindow = null;
let mainWindow = null;
const secondaryWindows = {};

function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 240,
    backgroundColor: "#181818",
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
      webSecurity: !isDev,
    },
  });

  if (isDev) {
    splashWindow.loadURL("http://localhost:5173/#splash");
  } else {
    const indexHtmlPath = path.join(__dirname, "../dist/index.html");
    splashWindow.loadURL(`file://${indexHtmlPath}#splash`);
  }

  splashWindow.on("closed", () => {
    splashWindow = null;
  });

  return splashWindow;
}

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
    resizable: false,
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
 * @param {Object} options - e.g. { key: "MyWindow", route: "/editor", width: 800, height: 600, title: "Editor" }
 * @returns {BrowserWindow} The created (or focused) BrowserWindow
 */
function createSecondaryWindow(options = {}) {
  const {
    key = "secondary",
    route = "",
    autoCloseOnBlur = false,
    position = "center",
    ...browserWindowOverrides
  } = options;

  // If already open, just focus it
  if (secondaryWindows[key]) {
    secondaryWindows[key].focus();
    return secondaryWindows[key];
  }

  log.info(`Creating secondary window for key: ${key}`);

  const encodedData = encodeURIComponent(JSON.stringify(options.data));
  const params = `?data=${encodedData}`;

  const defaultOptions = {
    width: 800,
    height: 600,
    title: "AS64",
    backgroundColor: "#181818",
    titleBarStyle: "hidden",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
      webSecurity: !isDev,
    },
  };

  const titleBarOverlay = autoCloseOnBlur
    ? {}
    : {
        titleBarOverlay: {
          color: "#1F1F1F",
          symbolColor: "#5E5E5E",
          height: 47,
        },
      };

  let windowCoordinates = {};
  if (position === "cursor") {
    const { x, y } = screen.getCursorScreenPoint();
    windowCoordinates = { x, y };
  }

  const newWindow = new BrowserWindow({
    ...defaultOptions,
    ...windowCoordinates,
    ...titleBarOverlay,
    ...browserWindowOverrides,
  });

  if (isDev) {
    newWindow.loadURL(`http://localhost:5173/#${route}${params}`);
  } else {
    const indexHtmlPath = path.join(__dirname, "../dist/index.html");
    newWindow.loadURL(`file://${indexHtmlPath}#${route}${params}`);
  }

  newWindow.on("closed", () => {
    delete secondaryWindows[key];
  });

  if (autoCloseOnBlur) {
    newWindow.on("blur", () => {
      secondaryWindows[key].close();
      delete secondaryWindows[key];
    });
  }

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
  }
}

/**
 * Closes all secondary windows.
 */
function closeAllSecondaryWindows() {
  Object.keys(secondaryWindows).forEach((key) => {
    if (secondaryWindows[key]) {
      secondaryWindows[key].close();
    }
  });
}

module.exports = {
  // Splash Screen
  createSplashWindow,
  get splashWindow() {
    return splashWindow;
  },

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
