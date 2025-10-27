# Changes to location_processor

## Overview
The `location_processor` function has been updated to use a dictionary-based input/output format with support for rebuilding state from previous outputs.

## Input Format

### Old Format (deprecated)
```python
location_processor(
    image_path="path/to/image.jpg",
    label_list=["RED", "GREEN", "BLUE"],
    bboxes=[[0, 0, 100, 100], [50, 50, 150, 150]],
    labels=[0, 1],
    ...
)
```

### New Format
```python
# Define field definitions with additional metadata
field_definitions = {
    "RED": {"classification": "abc"},
    "GREEN": {"classification": "def"},
    "BLUE": {"classification": "ghi"}
}

# Call with field definitions
# The function automatically detects if bbox/label_id exist and rebuilds state
result = location_processor(
    image_path="path/to/image.jpg",
    field_definitions=field_definitions,  # Pass previous output or initial definitions
    ...
)
```

## Output Format

### Old Format
```python
[
    {
        "bbox": [552.44, 567.32, 178.63, 198.48],
        "label_id": 0,
        "label": "RED"
    },
    {
        "bbox": [1288.47, 406.88, 196.83, 342.38],
        "label_id": 1,
        "label": "GREEN"
    }
]
```

### New Format
```python
{
    "RED": {
        "classification": "abc",  # Original field names are preserved
        "label_id": 0,
        "bbox": {
            "x": 552.44,
            "y": 567.32,
            "width": 178.63,
            "height": 198.48
        }
    },
    "GREEN": {
        "classification": "def",
        "label_id": 1,
        "bbox": {
            "x": 1288.47,
            "y": 406.88,
            "width": 196.83,
            "height": 342.38
        }
    }
}
```

## Key Features

### 1. Dictionary-based Structure
- Input and output now use dictionaries keyed by field name
- More intuitive and easier to work with programmatically

### 2. Field Metadata Preservation
- Additional fields in `field_definitions` are preserved in the output
- Example: If you have `{"RED": {"classification": "abc", "type": "color"}}`, both fields are preserved

### 3. Rebuild Support
- Simply pass your previous output back as `field_definitions` to rebuild the component state
- Automatically detects if bbox/label_id exist in the input and handles both cases

### 4. Bounding Box Format
- Output bboxes are now dictionaries with `x`, `y`, `width`, `height` keys
- More readable and easier to work with than arrays

## Example Usage

```python
import streamlit as st
from image_location_processer import location_processor

# Define field definitions
field_definitions = {
    "RED": {"classification": "primary"},
    "GREEN": {"classification": "secondary"},
    "BLUE": {"classification": "tertiary"}
}

# Initialize session state
if 'annotations' not in st.session_state:
    st.session_state['annotations'] = {}

# Annotate an image
# Automatically handles both initial state and rebuilding from previous output
result = location_processor(
    image_path="example.jpg",
    field_definitions=st.session_state['annotations'].get("example.jpg", field_definitions),
    key="example"
)

# Save result
if result is not None:
    st.session_state['annotations']["example.jpg"] = result
    st.json(result)
```

## Migration Guide

To migrate existing code:

1. Replace `label_list` with `field_definitions` dictionary
2. Remove `bboxes` and `labels` parameters (use `existing_output` instead)
3. Update code to handle dictionary output format
4. Convert bbox arrays `[x, y, w, h]` to dictionaries `{"x": x, "y": y, "width": w, "height": h}`

## See Also

- `example/detection_new_format.py` - Complete example using the new format
