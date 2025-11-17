import React from "react"
import { Layer, Stage, Image } from 'react-konva';
import Line from './Line'

export interface LineCanvasProps {
  lines: any[],
  selectedId: string | null,
  setSelectedId: any,
  scale: number,
  image_size: number[],
  image: any,
  strokeWidth: number
}

const LineCanvas = (props: LineCanvasProps) => {
  const {
    lines,
    selectedId,
    setSelectedId,
    scale,
    image_size,
    image,
    strokeWidth
  }: LineCanvasProps = props

  const checkDeselect = (e: any) => {
    // Deselect if clicking on the stage (not on a line)
    if (e.target === e.target.getStage()) {
      setSelectedId(null);
    }
  };

  return (
    <Stage 
      width={image_size[0] * scale} 
      height={image_size[1] * scale}
      onMouseDown={checkDeselect}
    >
      <Layer>
        <Image image={image} scaleX={scale} scaleY={scale} />
      </Layer>
      <Layer>
        {lines.map((line, i) => {
          return (
            <Line
              key={line.id}
              lineProps={line}
              scale={scale}
              strokeWidth={strokeWidth}
              isSelected={line.id === selectedId}
              onClick={() => {
                setSelectedId(line.id);
              }}
            />
          );
        })}
      </Layer>
    </Stage>
  );
};

export default LineCanvas;

