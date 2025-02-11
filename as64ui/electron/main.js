// /*
//  * AutoSplit64
//  *
//  * Copyright (C) 2025 Kainev
//  *
//  * This project is currently not open source and is under active development.
//  * You may view the code, but it is not licensed for distribution, modification, or use at this time.
//  *
//  * For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license
//  */

const { app } = require("electron");

const { createSplashWindow } = require("./window-manager");

const { spawnAS64, killAS64 } = require("./backend");
const { connectToAS64 } = require("./pipe");

const { setupIPC } = require("./ipc-handlers");

function onAppReady() {
  createSplashWindow();

  spawnAS64();
  setTimeout(() => connectToAS64(), 1000);

  setupIPC();
}

app.whenReady().then(onAppReady);

app.on("window-all-closed", () => {
  killAS64();
  app.quit();
});
