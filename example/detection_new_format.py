import streamlit as st
from glob import glob
from image_location_processer import location_processor

# Define field definitions (input format)
field_definitions = {
    "RED": {"classification": "abc"},
    "GREEN": {"classification": "def"},
    "BLUE": {"classification": "ghi"}
}

image_path_list = glob('image/*.jpg')

if not image_path_list:
    st.error("No images found in 'image' directory")
    st.stop()

if 'annotations' not in st.session_state:
    annotations = {}
    for img in image_path_list:
        # Initialize with field definitions (can pass existing output to rebuild)
        annotations[img] = field_definitions.copy()
    st.session_state['annotations'] = annotations.copy()

num_page = st.slider('page', 0, len(image_path_list)-1, 0, key='slider')
target_image_path = image_path_list[num_page]

st.write(f"Current image: {target_image_path}")

# Call location_processor with field definitions (automatically handles rebuilding if bbox exists)
result = location_processor(
    image_path=target_image_path,
    field_definitions=st.session_state['annotations'].get(target_image_path, field_definitions),
    line_width=5,
    use_space=True,
    key=target_image_path
)

if result is not None:
    # Update annotations with result
    # Result format: {"RED": {"classification": "abc", "label_id": 0, "bbox": {"x": ..., "y": ..., "width": ..., "height": ...}}, ...}
    st.session_state['annotations'][target_image_path] = result

# Display current annotations
st.write("Current annotations:")
st.json(st.session_state['annotations'][target_image_path])
