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
  Listbox,
  ListboxButton,
  ListboxOption,
  ListboxOptions,
} from "@headlessui/react";
import clsx from "clsx";
import { FaCheck, FaChevronDown } from "react-icons/fa6";
import { ReactNode } from "react";

interface SelectProps<T> {
  items: T[];

  value: T;
  onChange: (val: T) => void;

  optionsClassName?: string;
  buttonClassName?: string;

  renderValue?: (val: T) => ReactNode;
  renderOption?: (val: T, selected: boolean) => ReactNode;
}

export function Select<T>({
  items,
  value,
  onChange,
  optionsClassName,
  buttonClassName,
  renderValue,
  renderOption,
}: SelectProps<T>) {
  return (
    <Listbox value={value} onChange={onChange}>
      <ListboxButton
        onMouseDown={(e) => e.stopPropagation()}
        onPointerDown={(e) => e.stopPropagation()}
        onTouchStart={(e) => e.stopPropagation()}
        className={clsx(
          "relative block w-full h-10 rounded-md bg-transparent border border-white/15 py-1.5 pr-8 pl-3 text-left text-sm/6 text-white truncate",
          "focus:outline-none data-[focus]:outline-2 data-[focus]:-outline-offset-2 data-[focus]:outline-white/25",
          buttonClassName
        )}
      >
        {renderValue ? renderValue(value) : String(value)}
        <FaChevronDown
          size={10}
          className="group pointer-events-none absolute top-3.5 right-2.5 fill-white/60"
          aria-hidden="true"
        />
      </ListboxButton>

      <ListboxOptions
        className={clsx(
          "mt-1 w-full rounded-xl border border-white/5 bg-white/5 backdrop-blur-md p-1",
          "focus:outline-none transition duration-100 ease-in",
          optionsClassName
        )}
      >
        {items.map((item) => (
          <ListboxOption
            key={String(item)}
            value={item}
            onMouseDown={(e) => e.stopPropagation()}
            onPointerDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
            className="group flex cursor-default items-center gap-2 rounded-lg py-1.5 px-3 select-none data-[focus]:bg-white/10"
          >
            {({ selected }) => (
              <>
                <FaCheck
                  className={clsx(
                    "size-4 fill-white shrink-0",
                    selected ? "visible" : "invisible"
                  )}
                />

                {renderOption ? (
                  renderOption(item, selected)
                ) : (
                  <div className="text-sm/6 text-white truncate">
                    {String(item)}
                  </div>
                )}
              </>
            )}
          </ListboxOption>
        ))}
      </ListboxOptions>
    </Listbox>
  );
}
