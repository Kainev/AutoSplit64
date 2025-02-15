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

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  define: {
    global: {},
  },
  base: "./",
  root: "./as64ui/react",
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    sourcemap: false,
    minify: "esbuild",
    target: "esnext",
    rollupOptions: {
      output: {
        format: "cjs",
      },
    },
    assetsInlineLimit: 51200,
  },
  resolve: {
    alias: {
      "@": "./as64ui/react",
    },
  },
});
