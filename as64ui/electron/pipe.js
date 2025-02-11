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

const net = require("net");
const log = require("./logger");
const windowManager = require("./window-manager");

const PIPE_NAME = process.env.PIPE_NAME || "\\\\.\\pipe\\AutoSplit64";
let as64Pipe = null;

const pendingRequests = {};

function generateUniqueId() {
  return Math.random().toString(36).substring(2, 15);
}

function connectToAS64() {
  log.info(`Connecting to named pipe: ${PIPE_NAME}...`);

  as64Pipe = net.connect(PIPE_NAME, () => {
    log.info("Connected to AS64 pipe.");
  });

  as64Pipe.on("data", handleData);
  as64Pipe.on("error", handlePipeError);
  as64Pipe.on("close", handlePipeClose);
}

function handlePipeError(err) {
  log.error("Pipe error:", err);
  if (as64Pipe) {
    as64Pipe.destroy();
    as64Pipe = null;
  }

  setTimeout(() => connectToAS64(), 500);
}

function handlePipeClose() {
  log.warn("Named pipe connection closed.");
  as64Pipe = null;
}

// Inbound buffer
let buffer = "";

function handleData(data) {
  buffer += data.toString("utf-8");

  const lines = buffer.split("\n");

  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    try {
      const parsedData = JSON.parse(line);
      log.debug("Parsed line:", parsedData);

      if (parsedData.replyTo) {
        handleIncomingResponse(parsedData);
      }

      if (parsedData.event && parsedData.event === "loaded") {
        if (!windowManager.mainWindow) {
          windowManager.createMainWindow();
        }

        if (windowManager.splashWindow) {
          windowManager.splashWindow.close();
        }
      }

      if (windowManager.mainWindow && windowManager.mainWindow.webContents) {
        windowManager.mainWindow.webContents.send("message", parsedData);
      }

      if (windowManager.secondaryWindows) {
        Object.keys(windowManager.secondaryWindows).forEach((key) => {
          const win = windowManager.secondaryWindows[key];
          if (win && win.webContents) {
            win.webContents.send("message", parsedData);
          }
        });
      }
    } catch (err) {
      log.error("Failed to parse JSON line:", line, err);
    }
  }

  buffer = lines[lines.length - 1];
}

function handleIncomingResponse(parsedData) {
  const { replyTo: reqId, result } = parsedData;
  if (reqId && pendingRequests[reqId]) {
    const { resolve, timer } = pendingRequests[reqId];
    clearTimeout(timer);
    resolve(result);
    delete pendingRequests[reqId];
  }
}

// no response
function sendMessage(message) {
  if (!as64Pipe) {
    log.warn("No pipe connection available to send message.");
    return;
  }
  const jsonMessage = JSON.stringify(message);
  const bodyLength = Buffer.byteLength(jsonMessage, "utf-8");
  const header = bodyLength.toString().padStart(8, "0");
  const fullMessage = header + jsonMessage;
  as64Pipe.write(fullMessage);
}

// Request/response
function sendRequest(message, timeout = 1000) {
  return new Promise((resolve, reject) => {
    if (!as64Pipe) {
      return reject(new Error("No pipe connection"));
    }
    const requestId = generateUniqueId();
    message.requestId = requestId;
    const jsonMessage = JSON.stringify(message);

    const bodyLength = Buffer.byteLength(jsonMessage, "utf-8");
    const header = bodyLength.toString().padStart(8, "0");
    const fullMessage = header + jsonMessage;

    const timer = setTimeout(() => {
      delete pendingRequests[requestId];
      reject(new Error("Request timed out"));
    }, timeout);

    pendingRequests[requestId] = { resolve, timer };
    as64Pipe.write(fullMessage);
  });
}

module.exports = {
  connectToAS64,
  sendMessage,
  sendRequest,
};
