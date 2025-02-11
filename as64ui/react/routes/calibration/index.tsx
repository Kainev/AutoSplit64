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

import sm64Logo from "../../assets/sm64_logo_96.png";
import cameraIcon from "../../assets/camera_96.png";

export const CalibrationDialog = () => {
  const onResetClick = async () => {
    window.api.openNewWindow({
      key: "ResetDetection",
      title: "Calibrate Reset Detection",
      route: "/reset-detection",
      resizable: false,
      maximizable: false,
      minimizable: false,
      width: 650,
      height: 596,
    });
  };

  return (
    <main className="w-screen h-screen flex flex-col">
      {/* <WindowBar title="Calibration Menu" /> */}
      <section className="p-4 flex flex-col flex-1 w-full overflow-y-hidden gap-4">
        <button
          onClick={onResetClick}
          className="w-full bg-card hover:bg-white/5 rounded-md p-4 flex items-center gap-4 h-24"
        >
          <img
            src={sm64Logo}
            alt="Reset Detection"
            className="w-12 object-contain opacity-75"
          />
          <span className="ml-4 tracking-wide text-white/80">
            Reset Detection
          </span>
        </button>

        <button
          className="w-full bg-card rounded-md p-4 flex items-center gap-4 h-24 disabled:opacity-25"
          disabled
        >
          <div className="w-12 inline-flex items-center justify-center">
            <img
              src={cameraIcon}
              alt="Camera Detection"
              className="w-10 object-contain"
            />
          </div>
          <span className="ml-4 tracking-wide text-white/80">
            Camera Detection
          </span>
        </button>
      </section>
    </main>
  );
};
