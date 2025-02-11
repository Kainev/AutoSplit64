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

import { Input } from "../../../components/Input";
import { useRouteStore } from "../store";
import { CategorySelect } from "./CategorySelect";
import { VersionSelect } from "./VersionSelect";

export const RouteOverview = () => {
  const { title, initial_star, setTitle, setInitialStar } = useRouteStore();

  return (
    <div className="bg-[#1F1F1F] flex gap-4 p-5 rounded-lg h-min w-full">
      <div className="grow">
        <Input value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>

      <div className="w-16">
        <Input
          type="number"
          label="Initial Star"
          value={initial_star}
          onChange={(e) => setInitialStar(parseInt(e.target.value))}
        />
      </div>

      <div className="w-16">
        <VersionSelect />
      </div>

      <div>
        <CategorySelect />
      </div>
    </div>
  );
};
