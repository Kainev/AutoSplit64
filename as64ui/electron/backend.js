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

const path = require("path");
const { spawn } = require("child_process");

const { dialog } = require("electron");

const { isDev } = require("./env");
const log = require("./logger");

let as64Process = null;

function spawnAS64() {
  const pythonExePath = isDev
    ? process.env.PYTHON_DEV_EXE_PATH
    : process.env.PYTHON_PROD_EXE_PATH;

  const backendScriptPath = isDev
    ? process.env.PYTHON_DEV_APP_PATH
    : process.env.PYTHON_PROD_APP_PATH;

  const resolvedPythonExePath = path.resolve(__dirname, pythonExePath);
  const resolvedBackendScriptPath = path.resolve(__dirname, backendScriptPath);

  log.info(
    `Attempting to spawn AS64 process: ${resolvedPythonExePath} ${resolvedBackendScriptPath}`
  );

  try {
    as64Process = spawn(resolvedPythonExePath, [resolvedBackendScriptPath]);

    as64Process.on("error", (err) => {
      log.error("Failed to spawn AS64 process:", err);
      dialog.showErrorBox(
        "Python Error",
        `Failed to launch AS64:\n${err.message}`
      );
    });

    if (isDev) {
      as64Process.stdout.on("data", (data) => {
        log.debug(`AS64 (stdout): ${data}`);
      });

      as64Process.stderr.on("data", (data) => {
        log.error(`AS64 (stderr): ${data}`);
      });
    }

    as64Process.on("close", (code) => {
      log.info(`AS64 process exited with code ${code}`);
      as64Process = null;
    });
  } catch (err) {
    log.error("Exception caught while spawning AS64 process:", err);
    dialog.showErrorBox(
      "Python Error",
      `Exception while starting AS64:\n${err.message}`
    );
  }
}

function killAS64() {
  if (as64Process) {
    as64Process.kill();
    as64Process = null;
  }
}

module.exports = {
  spawnAS64,
  killAS64,
  get as64Process() {
    return as64Process;
  },
};
