import streamlit as st
from image_location_processer import location_processor

st.title("Simple Location Processor Example")

# Define your fields with their properties
field_definitions = {
    "RED": {"classification": "abc"},
    "GREEN": {"classification": "def"},
    "BLUE": {"classification": "ghi"}
}

# Initialize session state for annotations
if 'annotations' not in st.session_state:
    st.session_state['annotations'] = field_definitions.copy()

# Display current annotations
st.sidebar.header("Current Annotations")
st.sidebar.json(st.session_state['annotations'])

# Image path (you can change this to your image)
image_path = "image/deer.jpg"

st.header("Annotation Tool")
st.write("Draw bounding boxes for each field. Field names are preserved in the output!")

# Call location_processor - automatically handles both initial state and rebuilding
result = location_processor(
    image_path=image_path,
    field_definitions=st.session_state['annotations'],
    line_width=3,
    use_space=True,
    key="main_annotation"
)

# Update annotations when user completes
if result is not None:
    st.session_state['annotations'] = result
    st.success("Annotations updated!")
    st.balloons()

# Show the output format
with st.expander("Output Format Explanation"):
    st.markdown("""
    ### Input Format:
    ```python
    {
        "RED": {"classification": "abc"},
        "GREEN": {"classification": "def"}
    }
    ```
    
    ### Output Format:
    ```python
    {
        "RED": {
            "classification": "abc",  # Original fields preserved!
            "label_id": 0,
            "bbox": {"x": 100, "y": 200, "width": 150, "height": 100}
        },
        "GREEN": {
            "classification": "def",
            "label_id": 1,
            "bbox": {"x": 300, "y": 400, "width": 150, "height": 100}
        }
    }
    ```
    
    **Key Features:**
    - ✨ Single parameter: Just pass `field_definitions` (works for both initial and saved state)
    - 🔄 Auto-detect: Automatically rebuilds state if bbox/label_id exist
    - 📝 Preserve fields: All your field names stay the same in output
    - 📦 Dictionary bbox: Easy to work with `bbox.x`, `bbox.y`, etc.
    """)

# Show result in a nice format
if st.session_state['annotations'] != field_definitions:
    st.header("Result JSON")
    st.json(st.session_state['annotations'])
