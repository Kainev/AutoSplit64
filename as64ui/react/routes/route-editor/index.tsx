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

import { RouteOverview } from "./components/RouteOverview";
import SplitList from "./components/SplitList";
import { SideMenu } from "./components/SideMenu";
import { WindowBar } from "./components/WindowBar";
import { useEffect } from "react";

import useRouteIO from "./hooks/useRouteIO";

export const RouteEditor = () => {
  const { loadRoute } = useRouteIO();

  useEffect(() => {
    const fetch = async () => {
      const routePath = await window.api.rpc("config.get", "route", "path");
      loadRoute(routePath);
    };

    fetch();
  }, []);

  return (
    <main className="w-screen h-screen flex flex-col">
      <WindowBar />
      <section className="flex flex-1 overflow-y-hidden">
        <SideMenu />

        <div className="flex flex-col flex-1 items-center my-4 w-full overflow-y-hidden rounded-lg">
          <div className="px-4 w-full border-b border-white/15 pb-4">
            <RouteOverview />
          </div>
          <div className="flex-1 w-full overflow-y-auto modern-scrollbar pl-4 pt-4">
            <SplitList />
          </div>
        </div>
      </section>
    </main>
  );
};
