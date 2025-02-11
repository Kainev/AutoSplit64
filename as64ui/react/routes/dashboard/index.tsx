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

import React, { useEffect, useState } from "react";

import { BsPlay, BsStop } from "react-icons/bs";

import { FaChevronUp } from "react-icons/fa6";

import { MenuBar } from "./components/MenuBar";
import clsx from "clsx";

export const Dashboard: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [status, setStatus] = useState("Stopped");

  const [route, setRoute] = useState(null);

  useEffect(() => {
    const loadRoute = async (routePath: string) => {
      const route = await window.api.rpc("route.load", routePath);
      setRoute(route);
    };

    const loadRouteFromConfig = async () => {
      const routePath = await window.api.rpc("config.get", "route", "path");
      loadRoute(routePath);
    };

    window.api.onMessage((message) => {
      if (message.event === "config.update" && message.data[0] === "route") {
        loadRoute(message.data[2]);
      } else if (message.event === "status") {
        setStatus(message.data);
      } else if (message.event === "error") {
        window.api.openNewWindow({
          key: "ErrorDialog",
          title: "Error Dialog",
          route: "/error",
          width: 450,
          height: 200,
          data: message.data,
        });
      }
    });

    loadRouteFromConfig();
  }, []);

  const onCollapse = () => {
    setCollapsed(true);
    window.api.resizeWindow(96, 87);
  };

  const onExpand = () => {
    setCollapsed(false);
    window.api.resizeWindow(96, 576);
  };

  const handleRunningPress = async () => {
    if (status === "Running") {
      await window.api.rpc("as64.stop");
    } else {
      await window.api.rpc("as64.start");
    }
  };

  return (
    <main
      className={clsx(
        "bg-[#181818] h-screen w-screen draggable overflow-clip",
        collapsed ? "p-0" : "p-2"
      )}
    >
      {!collapsed && <MenuBar onCollapse={onCollapse} />}

      {collapsed && (
        <button
          onClick={onExpand}
          className="w-full inline-flex items-center justify-center mt-2 non-draggable"
        >
          <FaChevronUp size={12} className="text-white/30" />
        </button>
      )}

      <div className="mt-auto w-full overflow-clip">
        <h3
          className={clsx(
            "text-center tracking-wide text-white/50 w-full text-sm py-2 transition-colors",
            status === "Running" ? "border-red-500/40" : "border-green-500/30",
            !collapsed ? "border-t rounded-t-lg border-x py-2" : "pb-2 pt-0"
          )}
        >
          {route?.title}
        </h3>
        <button
          className={clsx(
            " w-full inline-flex items-center justify-center text-white/60 text-center p-1 rounded-b-lg tracking-wide non-draggable transition-colors",
            status === "Running" ? "bg-red-500/40" : "bg-green-500/30"
          )}
          onClick={handleRunningPress}
        >
          {status === "Running" ? <BsStop size={24} /> : <BsPlay size={24} />}
        </button>
      </div>
    </main>
  );
};
