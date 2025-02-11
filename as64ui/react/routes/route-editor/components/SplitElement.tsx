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

import React from "react";
import { useRouteStore, Split } from "../store";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Input } from "../../../components/Input";
import { SplitTypeSelect } from "./SplitTypeSelect";

interface SortableItemProps {
  id: string;
}

const SortableItem = ({ id }: SortableItemProps) => {
  const { splits, remove } = useRouteStore();
  const split = splits.find((s) => s.id === id);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  if (!split) return null; // Handle undefined split

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.3 : 1,
  };

  const SplitComponent =
    SplitTypeComponents[split.split_type] || SplitTypeComponents.DEFAULT;

  return (
    <li
      ref={setNodeRef}
      style={style}
      className={`flex items-center bg-[#1F1F1F] p-4 rounded shadow hover:bg-white/5 transition ${
        isDragging ? "bg-white/20" : ""
      }`}
      {...attributes}
      {...listeners}
    >
      <div className="flex items-center space-x-4 w-full">
        <span className="font-semibold text-white/80 w-6">
          {splits.indexOf(split) + 1}
        </span>

        <SplitComponent split={split} />

        {/* Remove Split Button */}
        <button
          onMouseDown={(e) => e.stopPropagation()}
          onTouchStart={(e) => e.stopPropagation()}
          onPointerDown={(e) => e.stopPropagation()}
          onClick={() => remove(id)}
          className="ml-auto text-red-500 hover:text-red-700 focus:outline-none"
          title="Remove Split"
        >
          &times;
        </button>
      </div>
    </li>
  );
};

export default SortableItem;

interface SplitElementProps {
  split: Split;
}

const StarSplit = ({ split }: SplitElementProps) => {
  const { updateSplit } = useRouteStore();

  return (
    <div className="flex gap-4 grow -translate-y-2">
      <Input
        label="Title"
        containerProps={{ className: "grow" }}
        value={split.title || ""}
        onChange={(e) => updateSplit(split.id, { title: e.target.value })}
      />
      <SplitTypeSelect split={split} />
      <Input
        type="number"
        label="Star Count"
        containerProps={{ className: "w-20" }}
        value={split.star_count}
        onChange={(e) =>
          updateSplit(split.id, { star_count: parseInt(e.target.value) })
        }
      />
    </div>
  );
};

const CustomSplit = ({ split }: SplitElementProps) => {
  const { updateSplit } = useRouteStore();

  return (
    <div className="grow">
      <div className="flex gap-4 grow -translate-y-2">
        <Input
          label="Title"
          containerProps={{ className: "grow" }}
          value={split.title || ""}
          onChange={(e) => updateSplit(split.id, { title: e.target.value })}
        />
        <SplitTypeSelect split={split} />
        <Input
          type="number"
          label="Star Count"
          containerProps={{ className: "w-20" }}
          value={split.star_count}
          onChange={(e) =>
            updateSplit(split.id, { star_count: parseInt(e.target.value) })
          }
        />
      </div>
      <div className="flex gap-4 grow">
        <Input
          type="number"
          label="Fade-out"
          containerProps={{ className: "ml-auto w-20" }}
          value={split.fade_out || null}
          onChange={(e) =>
            updateSplit(split.id, { fade_out: parseInt(e.target.value) })
          }
        />
        <Input
          type="number"
          label="Fade-in"
          containerProps={{ className: "w-20" }}
          value={split.fade_in || null}
          onChange={(e) =>
            updateSplit(split.id, { fade_in: parseInt(e.target.value) })
          }
        />
        <Input
          type="number"
          label="X-Cam"
          containerProps={{ className: "w-20" }}
          value={split.x_cam || null}
          onChange={(e) =>
            updateSplit(split.id, { x_cam: parseInt(e.target.value) })
          }
        />
      </div>
    </div>
  );
};

const NoStarSplit = ({ split }: SplitElementProps) => {
  const { updateSplit } = useRouteStore();

  return (
    <div className="flex gap-4 grow -translate-y-2 pr-24">
      <Input
        label="Title"
        containerProps={{ className: "grow" }}
        value={split.title || ""}
        onChange={(e) => updateSplit(split.id, { title: e.target.value })}
      />
      <SplitTypeSelect split={split} />
    </div>
  );
};

export const SplitTypeComponents: Record<string, React.FC> = {
  LBLJ: NoStarSplit,
  Star: StarSplit,
  Bowser: NoStarSplit,
  Mips: NoStarSplit,
  Custom: CustomSplit,
  DEFAULT: StarSplit,
};
