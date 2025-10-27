import os
import streamlit.components.v1 as components
from streamlit.components.v1.components import CustomComponent
from typing import List
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
import numpy as np
import matplotlib.pyplot as plt
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
    _component_func = components.declare_component("location_processor", path=build_path)
else:
    _component_func = components.declare_component("location_processor", url="http://localhost:3000")

def get_colormap(label_names, colormap_name='gist_rainbow'):
    colormap = {} 
    cmap = plt.get_cmap(colormap_name)
    for idx, l in enumerate(label_names):
        rgb = [int(d) for d in np.array(cmap(float(idx)/len(label_names)))*255][:3]
        colormap[l] = ('#%02x%02x%02x' % tuple(rgb))
    return colormap

#'''
#bboxes:
#[[x,y,w,h],[x,y,w,h]]
#labels:
#[0,3]
#'''
def detection(image_path, field_definitions, height=512, width=512, line_width=5.0, use_space=False, key=None) -> CustomComponent:
    """
    Detects bounding boxes for given field definitions.
    
    Args:
        image_path: Path to the image
        field_definitions: Dictionary mapping field names to their definitions.
                         Can be either:
                         - Initial definitions: {"RED": {"classification": "abc"}, ...}
                         - Previous output with bboxes: {"RED": {"classification": "abc", "bbox": {...}, "label_id": 0}, ...}
        height: Maximum height for display
        width: Maximum width for display
        line_width: Width of bounding box lines
        use_space: Enable Space key for completion
        key: Optional unique key for the widget
        
    Returns:
        Dictionary mapping field names to their data including bbox info.
        Preserves all original fields and adds bbox and label_id.
        e.g., {"RED": {"classification": "abc", "label_id": 0, "bbox": {"x": ..., "y": ..., "width": ..., "height": ...}}, ...}
    """
    image = Image.open(image_path)
    original_image_size = image.size
    image.thumbnail(size=(width, height))
    resized_image_size = image.size
    scale = original_image_size[0]/resized_image_size[0]
    
    # Support both old and new Streamlit API
    if USE_LAYOUT_CONFIG:
        layout_config = LayoutConfig(width=image.size[0], height=image.size[1])
        image_url = image_to_url(image, layout_config, True, "RGB", "PNG", f"detection-{md5(image.tobytes()).hexdigest()}-{key}")
    else:
        image_url = image_to_url(image, image.size[0], True, "RGB", "PNG", f"detection-{md5(image.tobytes()).hexdigest()}-{key}")

    # Extract label_list from field_definitions
    label_list = list(field_definitions.keys())
    color_map = get_colormap(label_list, colormap_name='gist_rainbow')
    
    # Detect if this is previous output (has bbox/label_id) or initial definition
    # Check if any field has bbox or label_id
    has_bboxes = any(
        isinstance(value, dict) and ('bbox' in value or 'label_id' in value)
        for value in field_definitions.values()
    )
    
    # Prepare initial bbox_info if bboxes exist in the input
    bbox_info = []
    if has_bboxes:
        for i, field_name in enumerate(label_list):
            field_data = field_definitions.get(field_name, {})
            if isinstance(field_data, dict) and 'bbox' in field_data:
                bbox = field_data['bbox']
                # Convert from new format (dict with x,y,width,height) to old format (list)
                if isinstance(bbox, dict):
                    bbox_list = [bbox.get('x', 0) / scale, bbox.get('y', 0) / scale, 
                               bbox.get('width', 0) / scale, bbox.get('height', 0) / scale]
                else:
                    # Support old format for backward compatibility
                    bbox_list = [b/scale for b in bbox]
                bbox_info.append({
                    'bbox': bbox_list,
                    'label_id': field_data.get('label_id', i),
                    'label': field_name
                })
    
    component_value = _component_func(image_url=image_url, image_size=image.size, label_list=label_list, bbox_info=bbox_info, color_map=color_map, line_width=line_width, use_space=use_space, key=key)
    
    if component_value is not None:
        # Convert from old format to new format
        result = {}
        for item in component_value:
            # Scale back to original image coordinates
            scaled_bbox = [b * scale for b in item['bbox']]
            label = item['label']
            label_id = item['label_id']
            
            # Get the original field definition to preserve other fields
            # Filter out bbox and label_id to avoid duplication
            field_data = {
                k: v for k, v in field_definitions[label].items() 
                if k not in ['bbox', 'label_id']
            }
            
            # Add bbox and label_id to the result (overwrite any existing)
            result[label] = {
                **field_data,  # Include original field definitions first
                'bbox': {
                    'x': scaled_bbox[0],
                    'y': scaled_bbox[1],
                    'width': scaled_bbox[2],
                    'height': scaled_bbox[3]
                },
                'label_id': label_id
            }
        
        return result
    
    return None

if not IS_RELEASE:
    from glob import glob
    import pandas as pd
    label_list = ['deer', 'human', 'dog', 'penguin', 'framingo', 'teddy bear']
    image_path_list = glob('image/*.jpg')
    if 'result_dict' not in st.session_state:
        result_dict = {}
        for img in image_path_list:
            # Initialize with field definitions
            result_dict[img] = {
                'deer': {'classification': 'mammal'},
                'human': {'classification': 'mammal'},
                'dog': {'classification': 'mammal'},
                'penguin': {'classification': 'bird'},
                'framingo': {'classification': 'bird'},
                'teddy bear': {'classification': 'toy'}
            }
        st.session_state['result_dict'] = result_dict.copy()

    num_page = st.slider('page', 0, len(image_path_list)-1, 0, key='slider')
    target_image_path = image_path_list[num_page]

    new_labels = detection(image_path=target_image_path, 
                      field_definitions=st.session_state['result_dict'][target_image_path],
                      line_width=5, use_space=True, key=target_image_path)
    if new_labels is not None:
        st.session_state['result_dict'][target_image_path] = new_labels
    st.json(st.session_state['result_dict'])