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

import clsx from "clsx";
import { ReactElement } from "react";

interface WindowBarProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  icon?: ReactElement;
  children?: React.ReactNode;
  className?: string;
}

export const WindowBar = ({
  title = "",
  icon,
  className = "",
  children,
  ...rest
}: WindowBarProps) => {
  return (
    <div
      className={clsx(
        "w-full h-12 bg-[#1F1F1F] border-b border-white/10 flex items-center pl-3 draggable shrink-0",
        className
      )}
      {...rest}
    >
      {children || (
        <div className="font-medium tracking-wide text-xs text-white/50 text-nowrap flex gap-3 items-center">
          {icon} {title}
        </div>
      )}
    </div>
  );
};
