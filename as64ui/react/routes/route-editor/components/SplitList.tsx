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

import React, { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useRouteStore, Split } from "../store";
import SortableItem from "./SplitElement";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { DragOverlay } from "@dnd-kit/core";
import { FaPlus } from "react-icons/fa6";

const SplitList = () => {
  const { splits, moveSplit, addSplit } = useRouteStore();
  const sensors = useSensors(useSensor(PointerSensor));
  const [activeId, setActiveId] = useState<string | null>(null);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (active.id !== over?.id && over) {
      moveSplit(active.id, over.id);
    }

    setActiveId(null);
  };

  const handleDragCancel = () => {
    setActiveId(null);
  };

  const handleAdd = () => {
    addSplit({ id: uuidv4(), title: "", split_type: "Star" });
  };

  const activeSplit: Split | null = activeId
    ? splits.find((split) => split.id === activeId) || null
    : null;

  return (
    <div>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragCancel={handleDragCancel}
      >
        <SortableContext
          items={splits.map((split) => split.id)}
          strategy={verticalListSortingStrategy}
        >
          <ul className="space-y-2">
            {splits.map((split) => (
              <SortableItem key={split.id} id={split.id} />
            ))}
          </ul>
        </SortableContext>

        <DragOverlay>
          {activeSplit ? (
            <div className="bg-[#303030]/50 backdrop-blur-sm border border-neutral-700 p-4 rounded shadow-lg">
              <div className="flex items-center space-x-4">
                <span className="font-medium text-white/80">
                  {splits.indexOf(activeSplit) + 1}
                </span>
                <span className="text-white/80">{activeSplit.title}</span>
              </div>
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>
      <button
        onClick={handleAdd}
        className="h-20 border border-green-500/30 rounded-md w-full text-white/70 tracking-wide mt-2 flex items-center justify-center gap-2 hover:bg-green-500/5 transition-colors"
      >
        <FaPlus size={18} className="text-green-500/70" />
      </button>
    </div>
  );
};

export default SplitList;
