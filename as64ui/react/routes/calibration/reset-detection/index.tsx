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

import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { WindowBar } from "../../../components/WindowBar";
import clsx from "clsx";
import { FaEquals } from "react-icons/fa6";

export const ResetDetectionDialog = () => {
  const [generated, setGenerated] = useState(false);
  const [generating, setGenerating] = useState(false);

  const [templateOneIndex, setTemplateOneIndex] = useState(0);
  const [templateTwoIndex, setTemplateTwoIndex] = useState(1);

  useEffect(() => {
    window.api.onMessage((message) => {
      if (message.event === "calibration.reset_detection.generated") {
        setGenerated(true);
        setGenerating(false);
      }
    });

    window.addEventListener("beforeunload", async (ev) => {
      console.log("STOP");
      await window.api.rpc("calibration.reset_detection.stop");
    });
  }, []);

  const onGeneratePress = async () => {
    setGenerating(true);
    await window.api.rpc("calibration.reset_detection.start");
  };

  const onCancelPress = async () => {
    setGenerating(false);
    await window.api.rpc("calibration.reset_detection.stop");
  };

  const onApplyPress = async () => {
    const success = await window.api.rpc(
      "calibration.reset_detection.apply",
      templateOneIndex,
      templateTwoIndex
    );

    if (success) {
      window.close();
    }
  };

  return (
    <main className="w-screen h-screen flex flex-col">
      <WindowBar title="Calibrate Reset Detection" />
      <section className="flex flex-col flex-1 w-full overflow-y-hidden pb-4">
        <div className="w-full border-b border-neutral-800 pb-4 relative">
          <div
            className={clsx(
              "absolute w-full h-full bg-base/80 backdrop-blur-xl z-50 flex items-center justify-center transition-opacity duration-300",
              generated && !generating && "opacity-0 pointer-events-none"
            )}
          >
            {!generating && !generated ? (
              <p className="text-white/70 tracking-wide">
                Press <strong className="font-medium">Generate</strong> with
                Super Mario 64 loaded, then{" "}
                <strong className="font-medium">reset</strong> your game.
              </p>
            ) : (
              <p className="text-white/70 tracking-wide">
                Waiting for <strong className="font-medium">reset</strong>..
              </p>
            )}
          </div>

          <TemplateDisplay
            templateOneIndex={templateOneIndex}
            templateTwoIndex={templateTwoIndex}
            setTemplateOneIndex={setTemplateOneIndex}
            setTemplateTwoIndex={setTemplateTwoIndex}
          />
        </div>
        <ButtonBar
          generated={generated}
          generating={generating}
          onGenerate={onGeneratePress}
          onApply={onApplyPress}
          onCancel={onCancelPress}
        />
      </section>
    </main>
  );
};

interface ButtonBarProps {
  generated: boolean;
  generating: boolean;
  onGenerate: () => void;
  onApply: () => void;
  onCancel: () => void;
}

const ButtonBar = ({
  generated,
  generating,
  onGenerate,
  onCancel,
  onApply,
}: ButtonBarProps) => {
  const handleGenerateOrCancel = () => {
    if (generating) {
      onCancel();
    } else {
      onGenerate();
    }
  };

  return (
    <div className="grid grid-cols-2 gap-8 mt-auto px-4">
      <button onClick={handleGenerateOrCancel} className="button">
        <span className="text-xs">{generating ? "Cancel" : "Generate"}</span>
      </button>
      <button onClick={onApply} disabled={!generated} className="button">
        <span className="text-xs">Apply</span>
      </button>
    </div>
  );
};

const generatedPaths = [
  "file://\\templates\\generated_temp_1.jpg",
  "file://\\templates\\generated_temp_2.jpg",
  "file://\\templates\\generated_temp_3.jpg",
  "file://\\templates\\generated_temp_4.jpg",
  "file://\\templates\\generated_temp_5.jpg",
];

interface TemplateDisplayProps {
  templateOneIndex: number;
  templateTwoIndex: number;
  setTemplateOneIndex: Dispatch<SetStateAction<number>>;
  setTemplateTwoIndex: Dispatch<SetStateAction<number>>;
}

const TemplateDisplay = ({
  templateOneIndex,
  templateTwoIndex,
  setTemplateOneIndex,
  setTemplateTwoIndex,
}: TemplateDisplayProps) => {
  const [renderKey, setRenderKey] = useState(0);

  const defaultOne = "file://\\templates\\default_reset_one.jpg";
  const defaultTwo = "file://\\templates\\default_reset_two.jpg";

  useEffect(() => {
    window.api.onMessage((message) => {
      if (message.event === "calibration.reset_detection.generated") {
        setRenderKey((key) => key + 1);
      }
    });
  }, []);

  return (
    <div>
      <div className="w-full flex flex-col gap-4 pt-4 px-4">
        <div className="flex w-full items-center">
          <h1 className="grow text-white/60 text-sm tracking-wide text-center pr-14">
            Select the matching image
          </h1>
          <div className="flex gap-1 w-[calc(50%-1.5rem)]">
            {generatedPaths.map((path, index) => (
              <button
                key={path}
                className={clsx(
                  "flex-1 rounded-md overflow-hidden border border-neutral-800",
                  generatedPaths[templateOneIndex] === path &&
                    "outline outline-blue-500"
                )}
                onClick={() => setTemplateOneIndex(index)}
              >
                <img
                  src={`${path}?key=${renderKey}`}
                  className="h-[29px] opacity-50"
                  alt="Thumbnail"
                />
              </button>
            ))}
          </div>
        </div>

        <div className="w-full flex gap-4 items-center">
          <div className="flex-1">
            <img
              src={defaultOne}
              alt="Desired"
              className="w-full h-auto rounded-md border border-neutral-800"
            />
          </div>

          <FaEquals size={20} className="text-white/30" />

          <div className="flex-1">
            <div className="rounded-md border border-neutral-800">
              <img
                src={`${generatedPaths[templateOneIndex]}?key=${renderKey}`}
                alt="Preview"
                className={clsx("w-full h-auto rounded-md")}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="w-full border-t border-neutral-800 mt-4" />

      <div className="w-full flex flex-col gap-4 pt-4 px-4">
        <div className="flex w-full items-center">
          <h1 className="grow text-white/60 text-sm tracking-wide text-center pr-14">
            Select the matching image
          </h1>
          <div className="flex gap-1 w-[calc(50%-1.5rem)]">
            {generatedPaths.map((path, index) => (
              <button
                key={path}
                className={clsx(
                  "flex-1 rounded-md overflow-hidden border border-neutral-800",
                  generatedPaths[templateTwoIndex] === path &&
                    "outline outline-blue-500"
                )}
                onClick={() => setTemplateTwoIndex(index)}
              >
                <img
                  src={`${path}?key=${renderKey}`}
                  className="h-[29px] opacity-50"
                  alt="Thumbnail"
                />
              </button>
            ))}
          </div>
        </div>

        <div className="w-full flex gap-4 items-center">
          <div className="flex-1">
            <img
              src={defaultTwo}
              alt="Desired"
              className="w-full h-auto rounded-md border border-neutral-800"
            />
          </div>

          <FaEquals size={20} className="text-white/30" />

          <div className="flex-1">
            <div className="rounded-md border border-neutral-800">
              <img
                src={`${generatedPaths[templateTwoIndex]}?key=${renderKey}`}
                alt="Preview"
                className={clsx("w-full h-auto rounded-md")}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
