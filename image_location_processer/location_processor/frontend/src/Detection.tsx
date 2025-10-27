import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps
} from "streamlit-component-lib"
import React, { useEffect, useState } from "react"
import { ChakraProvider, Select, Box, HStack, Center, Button, Text } from '@chakra-ui/react'
import { CheckIcon } from '@chakra-ui/icons'

import useImage from 'use-image';

import ThemeSwitcher from './ThemeSwitcher'

import BBoxCanvas from "./BBoxCanvas";

export interface PythonArgs {
  image_url: string,
  image_size: number[],
  label_list: string[],
  bbox_info: any[],
  color_map: any,
  line_width: number,
  use_space: boolean
}

const Detection = ({ args, theme }: ComponentProps) => {
  const {
    image_url,
    image_size,
    label_list,
    bbox_info,
    color_map,
    line_width,
    use_space
  }: PythonArgs = args

  const params = new URLSearchParams(window.location.search);
  const baseUrl = params.get('streamlitUrl')

  // Construct image URL
  let imageUrl: string
  if (baseUrl) {
    const url = new URL(baseUrl)
    // If baseUrl doesn't end with '/', it likely includes a page name - remove it
    const cleanPath = url.pathname.endsWith('/')
      ? url.pathname
      : url.pathname.substring(0, url.pathname.lastIndexOf('/') + 1)
    imageUrl = url.origin + cleanPath + image_url.substring(1)
  } else {
    imageUrl = image_url
  }

  const [image] = useImage(imageUrl)

  const [rectangles, setRectangles] = React.useState(
    bbox_info.map((bb, i) => {
      return {
        x: bb.bbox[0],
        y: bb.bbox[1],
        width: bb.bbox[2],
        height: bb.bbox[3],
        label: bb.label,
        stroke: color_map[bb.label],
        id: 'bbox-' + i
      }
    }));
  const [selectedId, setSelectedId] = React.useState<string | null>(null);
  const [label, setLabel] = useState(label_list[0])

  // Calculate which classes don't have bounding boxes yet
  const classesWithBoxes = rectangles.map(rect => rect.label);
  const missingClasses = label_list.filter(label => !classesWithBoxes.includes(label));

  const handleClassSelectorChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setLabel(event.target.value)
    console.log(selectedId)
    if (!(selectedId === null)) {
      const rects = rectangles.slice();
      for (let i = 0; i < rects.length; i++) {
        if (rects[i].id === selectedId) {
          rects[i].label = event.target.value;
          rects[i].stroke = color_map[rects[i].label]
        }
      }
      setRectangles(rects)
    }
  }
  const [scale, setScale] = useState(1.0)
  useEffect(() => {
    const resizeCanvas = () => {
      const scale_ratio = window.innerWidth * 0.8 / image_size[0]
      setScale(Math.min(scale_ratio, 1.0))
      Streamlit.setFrameHeight(image_size[1] * Math.min(scale_ratio, 1.0))
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas()
  }, [image_size])

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (use_space && event.key === ' ') { // 32 is the key code for Space key
        const currentBboxValue = rectangles.map((rect, i) => {
          return {
            bbox: [rect.x, rect.y, rect.width, rect.height],
            label_id: label_list.indexOf(rect.label),
            label: rect.label
          }
        })
        Streamlit.setComponentValue(currentBboxValue)
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [rectangles]); 

  return (
    <ChakraProvider>
      <ThemeSwitcher theme={theme}>
        <Center>
          <HStack width="100%" spacing={4} align="flex-start">
            <Box flex="0 0 auto" minWidth="200px" maxWidth="300px">
              <Text fontSize='sm' mb={2}>Class</Text>
              <Select value={label} onChange={handleClassSelectorChange} width="100%" mb={4}>
                {label_list.map(
                  (l) =>
                    <option value={l}>{l}</option>
                )
                }
              </Select>

              <Button 
                onClick={(e) => {
                  const currentBboxValue = rectangles.map((rect, i) => {
                    return {
                      bbox: [rect.x, rect.y, rect.width, rect.height],
                      label_id: label_list.indexOf(rect.label),
                      label: rect.label
                    }
                  })
                  Streamlit.setComponentValue(currentBboxValue)
                }} 
                width="100%" 
                mb={4}
                isDisabled={missingClasses.length > 0}
                colorScheme={missingClasses.length > 0 ? "gray" : "blue"}
                leftIcon={<CheckIcon />}
              >
                {missingClasses.length > 0 ? "Complete (Missing Fields)" : "Complete"}
              </Button>

              {/* Missing Classes Warning Box */}
              {missingClasses.length > 0 && (
                <Box
                  bg="red.50"
                  border="1px solid"
                  borderColor="red.200"
                  borderRadius="md"
                  p={3}
                  width="100%"
                >
                  <Text fontSize="sm" color="red.700" fontWeight="medium" mb={2}>
                    You've Not yet set the positions for the below fields:
                  </Text>
                  {missingClasses.map((className) => (
                    <Text key={className} fontSize="xs" color="red.600" ml={2}>
                      • {className}
                    </Text>
                  ))}
                </Box>
              )}
            </Box>
            <Box flex="1">
              <BBoxCanvas
                rectangles={rectangles}
                selectedId={selectedId}
                scale={scale}
                setSelectedId={setSelectedId}
                setRectangles={setRectangles}
                setLabel={setLabel}
                color_map={color_map}
                label={label}
                image={image}
                image_size={image_size}
                strokeWidth={line_width}
              />
            </Box>
          </HStack>
        </Center>
      </ThemeSwitcher>
    </ChakraProvider>
  )

}


export default withStreamlitConnection(Detection)
