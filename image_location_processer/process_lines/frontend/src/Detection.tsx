import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps
} from "streamlit-component-lib"
import React, { useEffect, useState } from "react"
import { ChakraProvider, Box, HStack, Center, Button } from '@chakra-ui/react'
import { DeleteIcon, CheckIcon } from '@chakra-ui/icons'

import useImage from 'use-image';

import ThemeSwitcher from './ThemeSwitcher'

import LineCanvas from "./LineCanvas";

export interface PythonArgs {
  image_url: string,
  image_size: number[],
  input_lines: any[],
  line_width: number,
}

const Detection = ({ args, theme }: ComponentProps) => {
  const {
    image_url,
    image_size,
    input_lines,
    line_width,
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

  // Initialize lines state from input_lines with added id
  const [lines, setLines] = React.useState(
    input_lines.map((line, i) => {
      return {
        ...line,  // Preserve all original keys
        id: 'line-' + i,
        stroke: '#FFA500'  // Bright orange for unselected
      }
    })
  );

  const [selectedId, setSelectedId] = React.useState<string | null>(null);

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

  // Handle delete button click
  const handleDelete = () => {
    if (selectedId !== null) {
      const updatedLines = lines.filter(line => line.id !== selectedId)
      setLines(updatedLines)
      setSelectedId(null)
    }
  }

  // Handle accept button click
  const handleAccept = () => {
    // Prepare output - remove internal id and stroke, keep all original keys
    const outputLines = lines.map(line => {
      const { id, stroke, ...originalLine } = line
      return originalLine
    })
    Streamlit.setComponentValue(outputLines)
  }

  return (
    <ChakraProvider>
      <ThemeSwitcher theme={theme}>
        <Center>
          <HStack width="100%" spacing={4} align="flex-start">
            <Box flex="0 0 auto" minWidth="200px" maxWidth="300px">
              <Button 
                onClick={handleDelete}
                width="100%" 
                mb={4}
                isDisabled={selectedId === null}
                colorScheme={selectedId === null ? "gray" : "red"}
                leftIcon={<DeleteIcon />}
              >
                Delete Line
              </Button>

              <Button 
                onClick={handleAccept}
                width="100%" 
                mb={4}
                colorScheme="blue"
                leftIcon={<CheckIcon />}
              >
                Accept
              </Button>
            </Box>
            <Box flex="1">
              <LineCanvas
                lines={lines}
                selectedId={selectedId}
                scale={scale}
                setSelectedId={setSelectedId}
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

