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

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./as64ui/react/**/*.{js,ts,jsx,tsx}", "./as64ui/react/index.html"],
  theme: {
    extend: {
      colors: {
        base: "#181818",
        card: "#1F1F1F",
      },
    },
  },
  plugins: [],
};
