import React from "react"
import { Line as KonvaLine } from 'react-konva';

export interface LineProps {
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  id: string,
  [key: string]: any,  // Allow other keys to be preserved
}

export interface LineComponentProps {
  lineProps: LineProps,
  onClick: any,
  isSelected: boolean,
  scale: number,
  strokeWidth: number
}

const Line = (props: LineComponentProps) => {
  const {
    lineProps, 
    onClick, 
    isSelected, 
    scale, 
    strokeWidth
  }: LineComponentProps = props

  // Bright orange for unselected, bright green for selected
  const strokeColor = isSelected ? '#00FF00' : '#FFA500'

  return (
    <KonvaLine
      points={[
        lineProps.x0 * scale,
        lineProps.y0 * scale,
        lineProps.x1 * scale,
        lineProps.y1 * scale
      ]}
      stroke={strokeColor}
      strokeWidth={strokeWidth}
      onClick={onClick}
      onTap={onClick}
      listening={true}
    />
  );
};

export default Line;

