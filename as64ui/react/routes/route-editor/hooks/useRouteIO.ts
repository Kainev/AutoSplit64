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

import { v4 as uuidv4 } from "uuid";

import { useRouteStore, Split } from "../store";

// @ts-ignore
import { parseToml, stringifyToml } from "../../../helpers/tomlHelper.js";

interface RouteData {
  __route__: boolean;
  logic_plugin: string;
  title: string;
  initial_star: number;
  version: "JP" | "US";
  category: string;
  SPLIT: Record<string, Split>;
}

const useRouteIO = () => {
  const {
    title,
    initial_star,
    version,
    category,
    splits,
    filePath,
    setSplits,
    setTitle,
    setInitialStar,
    setVersion,
    setCategory,
    setFilePath,
    clear,
  } = useRouteStore();

  const openRoute = async () => {
    try {
      const result = await window.api.openFile();

      if (result) {
        const routeData = parseToml(result.data);

        if (!routeData) return;

        setTitle(routeData.title || "");
        setInitialStar(routeData.initial_star || 0);
        setVersion(routeData.version || "JP");
        setCategory(routeData.category || "");

        if (routeData.SPLIT) {
          const splitsArray: Split[] = Object.values(routeData.SPLIT);
          setSplits(splitsArray);
        }
        setFilePath(result.filePath);

        await window.api.rpc("config.set", "route", "path", result.filePath);
        await window.api.rpc("config.save");
      }
    } catch (error) {
      console.error("Failed to load route:", error);
    }
  };

  const translateLSS = async () => {
    const result = await window.api.openFile();

    if (result) {
      const { data, filePath } = result;

      const route = await window.api.rpc("route.translate_lss", filePath);

      clear();
      setTitle(route.title);
      setInitialStar(route.initial_star);
      setCategory(route.category);
      setVersion(route.version);

      const splits = route.splits.map((split: Split) => ({
        ...split,
        id: split.id || uuidv4(),
      }));
      setSplits(splits);
    }
  };

  const loadRoute = async (path: string) => {
    try {
      const data = await window.api.readFile(path);
      if (!data) return;
      const routeData = parseToml(data);
      if (!routeData) return;
      setTitle(routeData.title || "");
      setInitialStar(routeData.initial_star || 0);
      setVersion(routeData.version || "JP");
      setCategory(routeData.category || "");
      if (routeData.SPLIT) {
        const splitsArray: Split[] = Object.values(routeData.SPLIT);
        setSplits(splitsArray);
      }
      setFilePath(path);
    } catch (error) {
      console.error("Failed to load route from path:", error);
    }
  };

  const saveRoute = async () => {
    try {
      const routeData: RouteData = {
        __route__: true,
        logic_plugin: "RTA",
        title,
        initial_star,
        version,
        category,
        SPLIT: splits.reduce((acc, split, index) => {
          acc[`split_${index + 1}`] = split;
          return acc;
        }, {} as Record<string, Split>),
      };

      await window.api.saveFile(filePath, stringifyToml(routeData), title);
    } catch (error) {
      console.error("Failed to save route:", error);
    }
  };

  const saveRouteAs = async () => {
    try {
      const routeData: RouteData = {
        __route__: true,
        logic_plugin: "RTA",
        title,
        initial_star,
        version,
        category,
        SPLIT: splits.reduce((acc, split, index) => {
          acc[`split_${index + 1}`] = split;
          return acc;
        }, {} as Record<string, Split>),
      };

      await window.api.saveFile("", stringifyToml(routeData), title);
    } catch (error) {
      console.error("Failed to save route:", error);
    }
  };

  return { openRoute, loadRoute, saveRoute, saveRouteAs, translateLSS };
};

export default useRouteIO;
