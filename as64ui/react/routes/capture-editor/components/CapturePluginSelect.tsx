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
  Field,
  Listbox,
  ListboxButton,
  ListboxOption,
  ListboxOptions,
} from "@headlessui/react";
import clsx from "clsx";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { FaCheck, FaChevronDown } from "react-icons/fa6";

interface CapturePluginSelectProps {
  selected: string;
  setSelected: Dispatch<SetStateAction<string>>;
}

export const CapturePluginSelect = ({
  selected,
  setSelected,
}: CapturePluginSelectProps) => {
  const [capturePlugins, setCapturePlugins] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const plugins = await window.api.rpc("plugin_manager.capture_plugins");
      const currentPlugin = await window.api.rpc(
        "plugin_manager.current_capture_plugin"
      );
      setSelected(currentPlugin);
      setCapturePlugins(plugins);
    };

    fetchData();
  }, []);

  const setLoaded = async (plugin: string) => {
    await window.api.rpc("plugin_manager.set_loaded", plugin, true);
  };

  return (
    <Field className="w-full">
      <Listbox
        value={selected}
        onChange={(opt) => {
          setSelected(opt);
          setLoaded(opt);
        }}
      >
        <ListboxButton
          onMouseDown={(e) => e.stopPropagation()}
          onPointerDown={(e) => e.stopPropagation()}
          onTouchStart={(e) => e.stopPropagation()}
          className={clsx(
            "relative block w-full h-10 rounded-md bg-transparent border border-white/15 py-1.5 pr-8 pl-3 text-left text-sm/6 text-white",
            "focus:outline-none data-[focus]:outline-2 data-[focus]:-outline-offset-2 data-[focus]:outline-white/25"
          )}
        >
          {selected}
          <FaChevronDown
            size={10}
            className="group pointer-events-none absolute top-3.5 right-2.5 fill-white/60"
            aria-hidden="true"
          />
        </ListboxButton>
        <ListboxOptions
          anchor="bottom"
          transition
          className={clsx(
            "w-[var(--button-width)] rounded-xl border border-white/5 bg-white/5 backdrop-blur-md p-1 [--anchor-gap:var(--spacing-1)] focus:outline-none",
            "transition duration-100 ease-in data-[leave]:data-[closed]:opacity-0"
          )}
        >
          {capturePlugins.map((plugin) => (
            <ListboxOption
              key={plugin}
              value={plugin}
              onMouseDown={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
              onTouchStart={(e) => e.stopPropagation()}
              className="group flex cursor-default items-center gap-2 rounded-lg py-1.5 px-3 select-none data-[focus]:bg-white/10"
            >
              <FaCheck className="invisible size-4 fill-white group-data-[selected]:visible" />
              <div className="text-sm/6 text-white">{plugin}</div>
            </ListboxOption>
          ))}
        </ListboxOptions>
      </Listbox>
    </Field>
  );
};
