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

import "./index.css";

import { HashRouter, Routes, Route } from "react-router-dom";
import { Dashboard } from "./routes/dashboard";
import { RouteEditor } from "./routes/route-editor";
import { CaptureEditor } from "./routes/capture-editor";
import { ErrorDialog } from "./routes/error-dialog";
import { SplashScreen } from "./routes/splash-screen";
import { CalibrationDialog } from "./routes/calibration";
import { ResetDetectionDialog } from "./routes/calibration/reset-detection";

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/route" element={<RouteEditor />} />
        <Route path="/capture" element={<CaptureEditor />} />
        <Route path="/error" element={<ErrorDialog />} />
        <Route path="/splash" element={<SplashScreen />} />
        <Route path="/calibration" element={<CalibrationDialog />} />
        <Route path="/reset-detection" element={<ResetDetectionDialog />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
