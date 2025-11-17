import os
import streamlit.components.v1 as components
from streamlit.components.v1.components import CustomComponent
from typing import List, Union, Dict, Any
from packaging import version

import streamlit as st
try:
    from streamlit.elements.image import image_to_url
except:
    from streamlit.elements.lib.image_utils import image_to_url

# Streamlit >= 1.49.0 uses LayoutConfig, older versions use int width
STREAMLIT_VERSION = version.parse(st.__version__)
USE_LAYOUT_CONFIG = STREAMLIT_VERSION >= version.parse("1.49.0")

if USE_LAYOUT_CONFIG:
    from streamlit.elements.lib.layout_utils import LayoutConfig

from PIL import Image
from hashlib import md5

# Import IS_RELEASE directly from the package to avoid circular import
import sys
import os
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)
try:
    from image_location_processer import IS_RELEASE
finally:
    sys.path.pop(0)

if IS_RELEASE:
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(absolute_path, "frontend/build")
    _component_func = components.declare_component("process_lines", path=build_path)
else:
    _component_func = components.declare_component("process_lines", url="http://localhost:3001")

def process_identifying_lines(
    image_input: Union[str, Image.Image], 
    input_lines: List[Dict[str, Any]], 
    height: int = 512, 
    width: int = 512, 
    line_width: float = 5.0, 
    key: str = None
) -> Union[List[Dict[str, Any]], None]:
    """
    Processes identifying lines on an image. Allows selection and deletion of lines.
    
    Args:
        image_input: Path to the image file (str) or PIL Image object
        input_lines: List of dictionaries containing line definitions.
                     Each dict must have keys: x0, y0, x1, y1 (coordinates).
                     All other keys are preserved in the output.
        height: Maximum height for display
        width: Maximum width for display
        line_width: Width of lines to draw
        key: Optional unique key for the widget
        
    Returns:
        List of remaining line dictionaries (without deleted lines).
        All original keys are preserved. Returns None if Accept hasn't been pressed.
    """
    if isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        image = image_input.copy()  # Create a copy to avoid modifying the original
    
    original_image_size = image.size
    image.thumbnail(size=(width, height))
    resized_image_size = image.size
    scale = original_image_size[0] / resized_image_size[0] if resized_image_size[0] > 0 else 1.0
    
    # Support both old and new Streamlit API
    if USE_LAYOUT_CONFIG:
        layout_config = LayoutConfig(width=image.size[0], height=image.size[1])
        image_url = image_to_url(image, layout_config, True, "RGB", "PNG", f"process_lines-{md5(image.tobytes()).hexdigest()}-{key}")
    else:
        image_url = image_to_url(image, image.size[0], True, "RGB", "PNG", f"process_lines-{md5(image.tobytes()).hexdigest()}-{key}")
    
    # Prepare line_info for the component - scale coordinates to resized image
    line_info = []
    for line in input_lines:
        line_info.append({
            'x0': line.get('x0', 0) / scale,
            'y0': line.get('y0', 0) / scale,
            'x1': line.get('x1', 0) / scale,
            'y1': line.get('y1', 0) / scale,
            # Store original line dict to preserve all other keys
            '_original': line
        })
    
    component_value = _component_func(
        image_url=image_url, 
        image_size=image.size, 
        input_lines=line_info, 
        line_width=line_width, 
        key=key
    )
    
    if component_value is not None:
        # Convert back - scale coordinates to original image size and restore original keys
        result = []
        for item in component_value:
            # Get the original line dict to preserve all other keys
            original_line = item.get('_original', {})
            
            # Create result dict with all original keys (preserving non-coordinate keys)
            result_line = {k: v for k, v in original_line.items()}
            
            # Update coordinates (scaled back to original image size from the returned values)
            result_line['x0'] = item['x0'] * scale
            result_line['y0'] = item['y0'] * scale
            result_line['x1'] = item['x1'] * scale
            result_line['y1'] = item['y1'] * scale
            
            result.append(result_line)
        
        return result
    
    return None

