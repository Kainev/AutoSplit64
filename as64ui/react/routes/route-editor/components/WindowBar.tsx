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

import { useRouteStore } from "../store";

export const WindowBar = () => {
  const { filePath, modified } = useRouteStore();
  return (
    <div className="w-full h-12 bg-[#1F1F1F] border-b border-white/10 flex items-center pl-3 draggable shrink-0">
      <div className="font-medium tracking-wide text-xs text-white/50 text-nowrap">
        Route Editor{" "}
        {filePath && (
          <span>
            [{filePath}
            {modified && "*"}]
          </span>
        )}
      </div>
    </div>
  );
};
