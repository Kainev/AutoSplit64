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

import { useSearchParams } from "react-router-dom";
import { WindowBar } from "../../components/WindowBar";
import { useEffect, useState } from "react";
import { FaTriangleExclamation, FaX } from "react-icons/fa6";

export const ErrorDialog = () => {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState(null);

  useEffect(() => {
    const data = searchParams.get("data");
    if (data) {
      try {
        const parsedData = JSON.parse(decodeURIComponent(data));
        setMessage(parsedData);
      } catch (error) {
        console.error("Error parsing data:", error);
      }
    }
  }, [searchParams]);

  const onClose = () => {
    window.close();
  };

  return (
    <main className="w-screen h-screen flex flex-col">
      <WindowBar title="Error" />
      <section className="px-8 py-4 flex flex-col flex-1 overflow-y-hidden">
        {message && (
          <div className="text-white/75 w-full h-full inline-flex justify-center items-center text-sm gap-4">
            <FaTriangleExclamation size={72} className="text-red-500 grow-0" />
            {message}
          </div>
        )}

        <div className="ml-auto">
          <button
            onClick={onClose}
            className="text-white/50 inline-flex items-center justify-center gap-2 font-medium tracking-wide grow bg-white/5 hover:bg-white/10 active:scale-95 transition-all py-3 px-6 rounded-md  shrink-0 "
          >
            <FaX size={12} />
            <span className="text-xs">Close</span>
          </button>
        </div>
      </section>
    </main>
  );
};
