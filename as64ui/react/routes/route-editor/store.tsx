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

import { create } from "zustand";

export interface Split {
  id: string;
  title: string;
  split_type: string;
  star_count?: number;
  fade_out?: number;
  fade_in?: number;
  x_cam?: number;
}

interface RouteStore {
  modified: boolean;

  filePath: string;
  title: string;
  initial_star: number;
  version: "JP" | "US";
  category: string;

  splits: Split[];

  setSplits: (splits: Split[]) => void;

  updateSplit: (id: string, data: Partial<Split>) => void;
  moveSplit: (activeId: string, overId: string) => void;

  addSplit: (split: Split) => void;
  remove: (id: string) => void;

  clear: () => void;

  setFilePath: (filePath: string) => void;
  setTitle: (title: string) => void;
  setInitialStar: (count: number) => void;
  setVersion: (version: "JP" | "US") => void;
  setCategory: (category: string) => void;
}

export const useRouteStore = create<RouteStore>((set) => ({
  modified: false,

  filePath: "",
  title: "",
  initial_star: 0,
  version: "JP",
  category: "",
  splits: [],

  setSplits: (splits) => set({ splits }),

  updateSplit: (id, data) =>
    set((state) => ({
      splits: state.splits.map((split) =>
        split.id === id ? { ...split, ...data } : split
      ),
      modified: true,
    })),

  moveSplit: (activeId, overId) =>
    set((state) => {
      const activeIndex = state.splits.findIndex(
        (split) => split.id === activeId
      );
      const overIndex = state.splits.findIndex((split) => split.id === overId);

      if (activeIndex === -1 || overIndex === -1) return {};

      const updatedSplits = arrayMove(state.splits, activeIndex, overIndex);
      return {
        splits: updatedSplits,
        modified: true,
      };
    }),

  addSplit: (split) =>
    set((state) => ({
      splits: [...state.splits, split],
      modified: true,
    })),

  remove: (id) => {
    set((state) => ({
      splits: state.splits.filter((split) => split.id !== id),
      modified: true,
    }));
  },

  clear: () =>
    set({
      splits: [],
      title: "",
      initial_star: 0,
      version: "JP",
      category: "",
      filePath: "",
      modified: false,
    }),

  setFilePath: (filePath) => set({ filePath }),

  setTitle: (title) => set({ title }),

  setInitialStar: (count) => set({ initial_star: count }),

  setVersion: (version) => set({ version }),

  setCategory: (category) => set({ category }),
}));

const arrayMove = <T,>(array: T[], from: number, to: number): T[] => {
  const newArray = array.slice();
  const [movedItem] = newArray.splice(from, 1);
  newArray.splice(to, 0, movedItem);
  return newArray;
};
