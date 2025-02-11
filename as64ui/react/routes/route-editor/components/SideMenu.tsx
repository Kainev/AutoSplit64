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

import {
  FaFolderOpen,
  FaFloppyDisk,
  FaBolt,
  FaCirclePlus,
} from "react-icons/fa6";
import useRouteIO from "../hooks/useRouteIO";
import { useRouteStore } from "../store";

export const SideMenu = () => {
  const { openRoute, saveRoute, saveRouteAs, translateLSS } = useRouteIO();
  const { clear } = useRouteStore();

  return (
    <aside className="flex flex-col items-center w-min overflow-clip tracking-wide px-2  border-r border-white/10 font-normal">
      <button
        onClick={clear}
        className="group inline-flex flex-col items-center justify-center non-draggable mt-2 hover:bg-neutral-500/5 w-full px-3 py-2 rounded-md active:scale-95 transition-all"
      >
        <FaCirclePlus
          size={20}
          className="text-white/30 group-hover:text-white/40 transition-colors"
        />
        <span className="text-xs text-white/50 mt-1 group-hover:text-white/60 transition-colors">
          New
        </span>
      </button>

      <button
        onClick={openRoute}
        className="group inline-flex flex-col items-center justify-center non-draggable mt-2 hover:bg-neutral-500/5 w-full px-3 py-2 rounded-md active:scale-95 transition-all"
      >
        <FaFolderOpen
          size={20}
          className="text-white/30 group-hover:text-white/40 transition-colors"
        />
        <span className="text-xs text-white/50 mt-1">Open</span>
      </button>

      <button
        onClick={saveRoute}
        className="group inline-flex flex-col items-center justify-center mt-2 hover:bg-neutral-500/5 w-full px-3 py-2 rounded-md active:scale-95 transition-all"
      >
        <FaFloppyDisk
          size={20}
          className="text-white/30 group-hover:text-white/40 transition-colors"
        />
        <span className="text-xs text-white/50 mt-1">Save</span>
      </button>

      <button
        onClick={saveRouteAs}
        className="group relative inline-flex flex-col items-center justify-center mt-2 hover:bg-neutral-500/5 w-full py-2 rounded-md active:scale-95 transition-all"
      >
        <FaFloppyDisk
          size={20}
          className="text-[#636363] relative group-hover:text-white/40 transition-colors"
        />
        <FaCirclePlus
          size={20}
          className="text-[#636363] absolute right-2 bottom-6 bg-[#1F1F1F] rounded-full border border-[#1F1F1F] group-hover:text-white/40 transition-colors"
        />
        <span className="text-xs text-white/50 mt-2">Save As</span>
      </button>

      <button
        onClick={translateLSS}
        className="group relative inline-flex flex-col items-center justify-center mt-2 hover:bg-neutral-500/5 w-full py-2 rounded-md active:scale-95 transition-all"
      >
        <FaBolt
          size={20}
          className="text-white/30 group-hover:text-white/40 transition-colors"
        />
        <span className="text-xs text-white/50 mt-1 text-center">
          Convert LSS
        </span>
      </button>
    </aside>
  );
};
