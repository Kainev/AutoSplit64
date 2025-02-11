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

import { FaBoltLightning, FaCamera, FaCheck, FaX } from "react-icons/fa6";

import { Input } from "../../../components/Input";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { CapturePluginSelect } from "./CapturePluginSelect";
import { Select } from "../../../components/Select";

type Rect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

interface CaptureEditorProps {
  initialRect?: Rect;
  onChange?: (rect: Rect) => void;
}

const MAGNIFIER_SIZE = 161;

export const CaptureEditorComponent: React.FC<CaptureEditorProps> = ({
  initialRect = { x: 50, y: 50, width: 200, height: 100 },
  onChange = () => {},
}) => {
  const [imageKey, setImageKey] = useState(0);
  const imageUrl = `file://\\resources\\capture.jpg?key=${imageKey}`;

  useEffect(() => {
    const fetchConfig = async () => {
      const result = await window.api.rpc("config.get", "capture");
      setRect({
        x: result.region[0],
        y: result.region[1],
        width: result.region[2],
        height: result.region[3],
      });
    };
    const fetchVisibleProcesses = async () => {
      const sources = await window.api.rpc(
        "plugin_manager.available_capture_sources"
      );

      const source = await window.api.rpc("config.get", "capture", "source");

      setCurrentSource(source);
      setAvailableSources(sources);
    };

    onCapture();
    fetchConfig();
    fetchVisibleProcesses();
  }, []);

  const onApply = async () => {
    await window.api.rpc("config.set", "capture", "region", [
      rect.x,
      rect.y,
      rect.width,
      rect.height,
    ]);

    if (imgRef.current) {
      await window.api.rpc("config.set", "capture", "size", [
        imgRef.current.naturalWidth,
        imgRef.current.naturalHeight,
      ]);
    }

    await window.api.rpc("config.save");

    window.close();
  };

  const onCancel = async () => {
    await window.api.rpc("config.rollback", "CaptureEditor", "capture");
    await window.api.rpc(
      "config.rollback",
      "CaptureEditor",
      "plugins",
      "CapturePlugin"
    );
    window.close();
  };

  const handleSourceChange = async (source: string) => {
    setCurrentSource(source);
    await window.api.rpc("config.set", "capture", "source", source);
    await onCapture();
  };

  // State & Refs
  const [capturePlugin, setCapturePlugin] = useState("");
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [currentSource, setCurrentSource] = useState("");

  const [imgSize, setImgSize] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0,
  });
  const [rect, setRect] = useState<Rect>(initialRect);
  const [magnifierPos, setMagnifierPos] = useState<{
    top?: number | string;
    left?: number | string;
    bottom?: number | string;
    right?: number | string;
  } | null>(null);

  const [draggingHandle, setDraggingHandle] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const imgRef = useRef<HTMLImageElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const offsetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const magnifierCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Effects
  useEffect(() => {
    window.api.rpc("config.create_rollback", "CaptureEditor");
  }, []);

  useEffect(() => {
    onChange(rect);
  }, [rect, onChange]);

  const onImageLoad = useCallback(
    (e: React.SyntheticEvent<HTMLImageElement>) => {
      const target = e.currentTarget;
      setImgSize({
        width: target.naturalWidth,
        height: target.naturalHeight,
      });
    },
    []
  );

  const onCapture = async () => {
    try {
      await window.api.rpc("save_frame");
      setImageKey((val) => val + 1);
    } catch (err) {
      console.log("Error fetching config: " + err.message);
    }
  };

  const clamp = (val: number, min: number, max: number) =>
    Math.min(Math.max(val, min), max);

  // Convert page coords to local (image container) coords
  const getLocalCoords = (clientX: number, clientY: number) => {
    if (!containerRef.current) return { x: 0, y: 0 };
    const rect = containerRef.current.getBoundingClientRect();
    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  };

  // Start dragging/resizing
  const onPointerDown = (
    e: React.PointerEvent<HTMLDivElement>,
    handle: string
  ) => {
    e.preventDefault();
    e.stopPropagation();

    const local = getLocalCoords(e.clientX, e.clientY);

    setDraggingHandle(handle);

    switch (handle) {
      case "tl":
        setMagnifierPos({
          top: -81,
          left: -81,
        });
        break;

      case "tr":
        setMagnifierPos({ top: -81, right: -81 });
        break;

      case "bl":
        setMagnifierPos({
          bottom: -81,
          left: -81,
        });
        break;

      case "br":
        setMagnifierPos({ bottom: -81, right: -81 });
        break;

      case "l":
        setMagnifierPos({
          top: `calc(50% - ${80}px)`,
          left: -81,
        });
        break;

      case "r":
        setMagnifierPos({
          top: `calc(50% - ${80}px)`,
          right: -81,
        });
        break;

      case "t":
        setMagnifierPos({
          left: `calc(50% - ${80}px)`,
          top: -81,
        });
        break;

      case "b":
        setMagnifierPos({
          left: `calc(50% - ${80}px)`,
          bottom: -81,
        });
        break;
      default:
        break;
    }

    if (handle === "move") {
      // Offset from the pointer to the rectangle's top-left corner
      offsetRef.current = {
        x: local.x - rect.x,
        y: local.y - rect.y,
      };
    } else {
      offsetRef.current = { x: local.x, y: local.y };
    }

    setIsDragging(true);
  };

  // Dragging/resizing
  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;

    const local = getLocalCoords(e.clientX, e.clientY);
    setMousePos(local);

    if (!isDragging || !draggingHandle) return;

    const deltaX = local.x - offsetRef.current.x;
    const deltaY = local.y - offsetRef.current.y;

    let newRect = { ...rect };

    switch (draggingHandle) {
      case "move":
        // Move entire rectangle
        newRect.x = local.x - offsetRef.current.x;
        newRect.y = local.y - offsetRef.current.y;

        // Clamp to prevent leaving image container
        newRect.x = clamp(newRect.x, 0, imgSize.width - newRect.width);
        newRect.y = clamp(newRect.y, 0, imgSize.height - newRect.height);
        break;

      case "tl":
        newRect.x += deltaX;
        newRect.y += deltaY;
        newRect.width -= deltaX;
        newRect.height -= deltaY;
        break;

      case "tr":
        newRect.y += deltaY;
        newRect.width += deltaX;
        newRect.height -= deltaY;
        break;

      case "bl":
        newRect.x += deltaX;
        newRect.width -= deltaX;
        newRect.height += deltaY;
        break;

      case "br":
        newRect.width += deltaX;
        newRect.height += deltaY;
        break;

      case "l":
        newRect.x += deltaX;
        newRect.width -= deltaX;
        break;

      case "r":
        newRect.width += deltaX;
        break;

      case "t":
        newRect.y += deltaY;
        newRect.height -= deltaY;
        break;

      case "b":
        newRect.height += deltaY;
        break;
      default:
        break;
    }

    // Ensure min size
    if (newRect.width < 1) {
      newRect.width = 1;
    }
    if (newRect.height < 1) {
      newRect.height = 1;
    }

    // Clamp X/Y if corners moved beyond image boundaries
    newRect.x = clamp(newRect.x, 0, imgSize.width - newRect.width);
    newRect.y = clamp(newRect.y, 0, imgSize.height - newRect.height);

    setRect(newRect);
    if (draggingHandle !== "move") {
      offsetRef.current = { x: local.x, y: local.y };
    }
  };

  const onPointerUp = () => {
    setMagnifierPos(null);
    setIsDragging(false);
    setDraggingHandle(null);
  };

  // Magnifier
  useEffect(() => {
    const canvas = magnifierCanvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!ctx || !imgRef.current || !canvas) return;

    ctx.imageSmoothingEnabled = false;

    const zoomFactor = 12;
    const halfZoomFactor = zoomFactor / 2;
    const regionSize = MAGNIFIER_SIZE / 4;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let posX = 0;
    let posY = 0;

    switch (draggingHandle) {
      case "tl":
        posX = rect.x;
        posY = rect.y;
        break;

      case "tr":
        posX = rect.x + rect.width;
        posY = rect.y;
        break;

      case "bl":
        posX = rect.x;
        posY = rect.y + rect.height;
        break;

      case "br":
        posX = rect.x + rect.width;
        posY = rect.y + rect.height;
        break;

      case "l":
        posX = rect.x;
        posY = rect.y + rect.height / 2;
        break;

      case "r":
        posX = rect.x + rect.width;
        posY = rect.y + rect.height / 2;
        break;

      case "t":
        posX = rect.x + rect.width / 2;
        posY = rect.y;
        break;

      case "b":
        posX = rect.x + rect.width / 2;
        posY = rect.y + rect.height;
        break;

      default:
        break;
    }

    const sx = posX - regionSize / halfZoomFactor;
    const sy = posY - regionSize / halfZoomFactor;

    ctx.drawImage(
      imgRef.current,
      sx,
      sy,
      regionSize,
      regionSize,
      0,
      0,
      regionSize * zoomFactor,
      regionSize * zoomFactor
    );

    // Crosshair lines
    ctx.strokeStyle = "red";
    ctx.lineWidth = 1;

    // Vertical line
    ctx.beginPath();
    ctx.moveTo((regionSize * zoomFactor) / halfZoomFactor, 0);
    ctx.lineTo(
      (regionSize * zoomFactor) / halfZoomFactor,
      regionSize * zoomFactor
    );
    ctx.stroke();
    // Horizontal line
    ctx.beginPath();
    ctx.moveTo(0, (regionSize * zoomFactor) / halfZoomFactor);
    ctx.lineTo(
      regionSize * zoomFactor,
      (regionSize * zoomFactor) / halfZoomFactor
    );
    ctx.stroke();
  }, [mousePos, rect, draggingHandle, imgSize]);

  // Render
  const selectionHandles = [
    { name: "tl", style: { left: rect.x - 4, top: rect.y - 4 } },
    { name: "tr", style: { left: rect.x + rect.width - 5, top: rect.y - 4 } },
    { name: "bl", style: { left: rect.x - 4, top: rect.y + rect.height - 5 } },
    {
      name: "br",
      style: { left: rect.x + rect.width - 5, top: rect.y + rect.height - 5 },
    },
    {
      name: "l",
      style: { left: rect.x - 4, top: rect.y + rect.height / 2 - 4 },
    },
    {
      name: "r",
      style: {
        left: rect.x + rect.width - 5,
        top: rect.y + rect.height / 2 - 4,
      },
    },
    {
      name: "t",
      style: { left: rect.x + rect.width / 2 - 4, top: rect.y - 4 },
    },
    {
      name: "b",
      style: {
        left: rect.x + rect.width / 2 - 4,
        top: rect.y + rect.height - 5,
      },
    },
  ];

  return (
    <div className="flex overflow-hidden w-full">
      {/* Sidebar */}
      <div className="w-[19rem] border-r border-white/15 shrink-0 p-6 bg-card">
        <div className="flex mb-4 justify-between">
          <button onClick={onCapture} className="button w-[7.5rem]">
            <FaCamera />
            <span className="text-xs">Capture</span>
          </button>
          <button className="text-white/50 inline-flex items-center justify-center gap-2 font-medium tracking-wide bg-white/5 w-[7.5rem] p-3 rounded-md  text-nowrap  shrink-0">
            <FaBoltLightning />
            <span className="text-xs">Auto-Detect</span>
          </button>
        </div>
        <div className="">
          <h1 className="font-medium tracking-wide text-sm text-white/60 mb-2 border-b-0 border-white/15">
            Capture Method
          </h1>
          <CapturePluginSelect
            selected={capturePlugin}
            setSelected={setCapturePlugin}
          />

          {availableSources.length > 0 && (
            <>
              <h1 className="font-medium tracking-wide text-sm text-white/60 mb-2 border-b-0 border-white/15 mt-4">
                Source
              </h1>
              <Select
                items={availableSources}
                value={currentSource}
                onChange={handleSourceChange}
                optionsClassName="max-h-[200px] overflow-y-auto overflow-x-hidden modern-scrollbar-select"
              />
            </>
          )}
        </div>
      </div>

      {/* Image + selection container */}
      <div
        className="overflow-auto grow w-full bg-transparent modern-scrollbar flex"
        key={imageKey}
      >
        <div
          ref={containerRef}
          className="shrink-0 mx-auto"
          style={{
            position: "relative",
            border: "1px solid #ccc",
            width: imgSize.width,
            height: imgSize.height,
          }}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
        >
          <img
            src={imageUrl}
            key={imageKey}
            alt="To select"
            onLoad={onImageLoad}
            ref={imgRef}
            draggable={false}
            style={{ display: "block", userSelect: "none" }}
          />

          {/* Selection rectangle */}
          <div
            onPointerDown={(e) => onPointerDown(e, "move")}
            style={{
              position: "absolute",
              left: rect.x,
              top: rect.y,
              width: rect.width,
              height: rect.height,
              border: "1px solid #ff0000",
              cursor: "move",
              boxSizing: "border-box",
              background: "rgba(255, 0, 0, 0.1)",
            }}
          >
            <canvas
              ref={magnifierCanvasRef}
              className="pointer-events-none rounded-full"
              width={MAGNIFIER_SIZE}
              height={MAGNIFIER_SIZE}
              style={{
                visibility: magnifierPos === null ? "hidden" : "visible",
                position: "absolute",
                ...magnifierPos,
                border: "1px solid #000",
                imageRendering: "pixelated",
                width: MAGNIFIER_SIZE,
                height: MAGNIFIER_SIZE,
              }}
            />
          </div>

          {/* Handle elements */}
          {selectionHandles.map(({ name, style }) => (
            <div
              key={name}
              onPointerDown={(e) => onPointerDown(e, name)}
              style={{
                position: "absolute",
                borderRadius: "100%",
                width: 9,
                height: 9,
                background: "#ff0000",
                cursor: name + "-resize",
                ...style,
              }}
            />
          ))}
        </div>
      </div>
      {/* Sidebar */}
      <div className="w-72 border-l border-white/15 shrink-0 p-6 bg-card flex flex-col">
        <div className="">
          <h1 className="font-medium tracking-wide text-sm text-white/60 mb-2 pb-1 border-b border-white/15">
            Game Region
          </h1>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="X"
              className="text-sm text-white/90"
              containerProps={{ className: "" }}
              value={rect.x}
              onChange={(e) =>
                setRect({ ...rect, x: parseInt(e.target.value) || 0 })
              }
            />
            <Input
              label="Y"
              className="text-sm text-white/90"
              containerProps={{ className: "" }}
              value={rect.y}
              onChange={(e) =>
                setRect({ ...rect, y: parseInt(e.target.value) || 0 })
              }
            />
          </div>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <Input
              label="Width"
              className="text-sm text-white/90"
              containerProps={{ className: "" }}
              value={rect.width}
              onChange={(e) =>
                setRect({ ...rect, width: parseInt(e.target.value) || 0 })
              }
            />
            <Input
              label="Height"
              className="text-sm text-white/90"
              containerProps={{ className: "" }}
              value={rect.height}
              onChange={(e) =>
                setRect({ ...rect, height: parseInt(e.target.value) || 0 })
              }
            />
          </div>
        </div>
        <div className="flex w-full gap-4 mt-auto">
          <button
            onClick={onApply}
            className="text-white/50 inline-flex items-center justify-center gap-2 font-medium tracking-wide grow bg-white/5 hover:bg-white/10 active:scale-95 transition-all p-3 rounded-md  shrink-0 "
          >
            <FaCheck />
            <span className="text-xs">Apply</span>
          </button>
          <button
            onClick={onCancel}
            className="text-white/50 inline-flex items-center justify-center gap-2 font-medium tracking-wide grow bg-white/5 hover:bg-white/10 active:scale-95 transition-all p-3 rounded-md  shrink-0"
          >
            <FaX size={14} />
            <span className="text-xs">Cancel</span>
          </button>
        </div>
      </div>
    </div>
  );
};
