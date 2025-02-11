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

import { forwardRef, HTMLAttributes } from "react";
import {
  Field,
  Input as HeadlessInput,
  type InputProps as HeadlessInputProps,
} from "@headlessui/react";
import clsx from "clsx";

export interface CustomInputProps extends HeadlessInputProps {
  label?: string;
  className?: string;
  containerProps?: HTMLAttributes<HTMLDivElement>;
}

export const Input = forwardRef<HTMLInputElement, CustomInputProps>(
  ({ label = "Title", className, containerProps, ...props }, ref) => {
    return (
      <div
        className={clsx("w-full", containerProps?.className)}
        {...containerProps}
      >
        <Field>
          <label className="text-xs tracking-wider text-white/50 pb-1 block">
            {label}
          </label>
          <HeadlessInput
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
            onPointerDown={(e) => e.stopPropagation()}
            ref={ref}
            className={clsx(
              "block w-full h-10 rounded-md border border-white/15 bg-transparent py-1.5 px-3 text-white",
              "focus:outline-none data-[focus]:outline-2 data-[focus]:-outline-offset-2 data-[focus]:outline-blue-500",
              className
            )}
            {...props}
          />
        </Field>
      </div>
    );
  }
);

Input.displayName = "Input";
