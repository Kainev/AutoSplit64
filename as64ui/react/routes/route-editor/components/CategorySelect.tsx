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

import { useState } from "react";
import {
  Combobox,
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import { FaCheck, FaChevronDown } from "react-icons/fa6";
import clsx from "clsx";
import { useRouteStore } from "../store";

const defaultCategories = [
  "0 Star",
  "1 Star",
  "16 Star",
  "70 Star",
  "120 Star",
];

export const CategorySelect = () => {
  const { category, setCategory } = useRouteStore();
  const [categories, setCategories] = useState(defaultCategories);
  const [query, setQuery] = useState("");

  // Filter existing categories
  const filtered =
    query === ""
      ? categories
      : categories.filter((cat) =>
          cat.toLowerCase().includes(query.toLowerCase())
        );

  // If no existing category, show a 'virtual' option
  let finalOptions = filtered;
  if (
    query !== "" &&
    !filtered.some((cat) => cat.toLowerCase() === query.toLowerCase())
  ) {
    finalOptions = [
      ...filtered,
      query, // "create new" option
    ];
  }

  const handleChange = (item: string) => {
    const exists = categories.some(
      (cat) => cat.toLowerCase() === item.toLowerCase()
    );
    if (!exists) {
      setCategories((prev) => [...prev, item]);
    }
    setCategory(item);
    setQuery("");
  };

  return (
    <div className="max-w-sm space-y-1 relative">
      <label className="block text-xs tracking-wider text-white/50 bg-[#1F1F1F]">
        Category
      </label>

      <Combobox value={category} onChange={handleChange}>
        <div className="relative">
          <ComboboxInput
            className={clsx(
              "w-full rounded-md border border-white/15 bg-card h-10 py-1.5 pl-3 pr-8 text-sm text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500"
            )}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Select or type a category"
          />

          <ComboboxButton className="group absolute inset-y-0 right-0 px-2.5">
            <FaChevronDown
              size={10}
              className="fill-white/60 group-data-[hover]:fill-white"
            />
          </ComboboxButton>
        </div>

        <ComboboxOptions
          transition
          className={clsx(
            "absolute w-full rounded-md border border-white/5 bg-white/5 backdrop-blur-md p-1 empty:invisible",
            "transition duration-100 ease-in data-[leave]:data-[closed]:opacity-0 z-50"
          )}
        >
          {finalOptions.map((cat) => (
            <ComboboxOption
              key={cat}
              value={cat}
              className={clsx(
                "group flex cursor-default select-none items-center gap-2 rounded-md px-3 py-1.5 text-sm text-white",
                "data-[focus]:bg-gray-700"
              )}
            >
              <FaCheck
                className={clsx(
                  "h-4 w-4 invisible group-data-[selected]:visible"
                )}
              />
              <span>{cat}</span>
            </ComboboxOption>
          ))}
        </ComboboxOptions>
      </Combobox>
    </div>
  );
};
