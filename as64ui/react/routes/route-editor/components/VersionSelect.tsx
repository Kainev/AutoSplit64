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

import { Field, Select } from "@headlessui/react";
import clsx from "clsx";
import { FaChevronDown } from "react-icons/fa6";

export const VersionSelect = () => {
  return (
    <div className="w-full">
      <Field>
        <div className="text-xs tracking-wider text-white/50 bg-[#1F1F1F] mb-1">
          Version
        </div>

        <div className="relative">
          <Select
            className={clsx(
              "block w-full appearance-none rounded-md h-10 bg-card py-1.5 px-3 text-sm/6 text-white border border-white/15",
              "focus:outline-none data-[focus]:outline-2 data-[focus]:-outline-offset-2 data-[focus]:outline-white/25",
              "*:text-white/80 "
            )}
          >
            <option value="JP">JP</option>
            <option value="US">US</option>
          </Select>
          <FaChevronDown
            size={10}
            className="group pointer-events-none absolute top-3.5 right-3 fill-white/60"
            aria-hidden="true"
          />
        </div>
      </Field>
    </div>
  );
};
