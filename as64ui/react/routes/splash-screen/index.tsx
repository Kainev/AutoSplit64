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

import logo_128 from "../../assets/logo_128.png";

export const SplashScreen = () => {
  return (
    <div className="flex flex-col h-screen bg-card py-6 px-8">
      <div className="flex justify-center gap-12">
        <img src={logo_128} alt="AutoSplit64 Logo" width={128} height={128} />

        <div className="flex flex-col items-end mt-12">
          <p className="text-4xl tracking-wider text-neutral-400">
            AutoSplit64
          </p>
          <p className="text-sm text-neutral-400 tracking-wide font-medium">
            By Synozure
          </p>
        </div>
      </div>
      <div className="flex justify-between mt-auto">
        <p className="text-sm tracking-wide text-neutral-400">v1.0.0-alpha.1</p>
        <p className="text-sm text-neutral-400 tracking-wide">Initializing..</p>
      </div>
    </div>
  );
};
