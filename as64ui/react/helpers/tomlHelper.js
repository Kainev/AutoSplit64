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

import toml from "toml";
import tomlify from "tomlify-j0.4";

export const parseToml = (tomlString) => {
  try {
    return toml.parse(tomlString);
  } catch (error) {
    console.error("Error parsing TOML:", error);
    return null;
  }
};

export const stringifyToml = (obj) => {
  try {
    return tomlify.toToml(obj, { space: 2 });
  } catch (error) {
    console.error("Error stringifying TOML:", error);
    return "";
  }
};
