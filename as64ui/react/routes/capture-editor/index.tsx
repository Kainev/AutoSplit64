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

import { CaptureEditorComponent } from "./components/CaptureEditor";
import { WindowBar } from "./components/WindowBar";

export const CaptureEditor = () => {
  return (
    <main className="w-screen h-screen flex flex-col">
      <WindowBar />
      <section className="flex flex-1 overflow-y-hidden">
        <CaptureEditorComponent />
      </section>
    </main>
  );
};
