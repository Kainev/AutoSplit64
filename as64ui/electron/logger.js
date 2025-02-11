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

const log = require("electron-log");
const { isDev } = require("./env");

log.transports.console.format = "{h}:{i}:{s} [{level}] {text}";
log.transports.file.format = "{h}:{i}:{s} [{level}] {text}";

log.transports.console.level = isDev ? "debug" : "info";
log.transports.file.level = isDev ? "debug" : "info";

module.exports = { log };
