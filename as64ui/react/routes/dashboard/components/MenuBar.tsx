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
  FaGear,
  FaEllipsis,
  FaCamera,
  FaPlug,
  FaRoute,
  FaRulerCombined,
  FaChevronDown,
} from "react-icons/fa6";

interface MenuBarProps {
  onCollapse: () => void;
}

const buttonClass =
  "inline-flex flex-col items-center justify-center non-draggable group first:mt-0 mt-8 disabled:opacity-50 disabled:pointer-events-none";

const iconClass = "text-white/30 group-hover:text-white/50 transition-colors";

const textClass =
  "text-xs text-white/50 group-hover:text-white/70 mt-1 transition-colors select-none";

export const MenuBar = ({ onCollapse }: MenuBarProps) => {
  const openRouteWindow = () => {
    window.api.openNewWindow({
      key: "RouteEditor",
      title: "Route Editor",
      route: "/route",
      width: 960,
      height: 805,
    });
  };

  const openCaptureWindow = () => {
    window.api.openNewWindow({
      key: "CaptureEditor",
      title: "Capture Editor",
      route: "/capture",
      width: 1440,
      height: 720,
    });
  };

  const openCalibrationWindow = () => {
    window.api.openNewWindow({
      key: "CalibrationWindow",
      title: "Calibration",
      route: "/calibration",
      width: 312,
      height: 200,
      autoCloseOnBlur: true,
      position: "cursor",
      resizable: false,
    });
  };

  return (
    <aside className="rounded-lg flex flex-col items-center bg-[#1F1F1F] w-20 overflow-clip tracking-wide py-4 mb-2">
      <button className={buttonClass} onClick={openRouteWindow}>
        <FaRoute size={24} className={iconClass} />
        <span className={textClass}>Route</span>
      </button>

      <button onClick={openCaptureWindow} className={buttonClass}>
        <FaCamera size={24} className={iconClass} />
        <span className={textClass}>Capture</span>
      </button>

      <button className={buttonClass} onClick={openCalibrationWindow}>
        <FaRulerCombined size={24} className={iconClass} />
        <span className={textClass}>Calibrate</span>
      </button>

      <button className={buttonClass} disabled>
        <FaPlug size={24} className={iconClass} />
        <span className={textClass}>Plugins</span>
      </button>

      <button className={buttonClass} disabled>
        <FaEllipsis size={24} className={iconClass} />
        <span className={textClass}>More</span>
      </button>

      <button className={buttonClass} disabled>
        <FaGear size={24} className={iconClass} />
        <span className={textClass}>Settings</span>
      </button>

      <button
        onClick={onCollapse}
        className="inline-flex flex-col items-center justify-center mt-4 non-draggable"
      >
        <FaChevronDown size={12} className="text-white/30" />
      </button>
    </aside>
  );
};
