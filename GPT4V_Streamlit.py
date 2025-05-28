'''
Runs the Traffic Monitor Assistant Streamlit app
'''

# Importing required packages
import openai
import streamlit as st
import base64
import os
import requests
from scripts.webcams import fetch_webcam_data
from scripts.saveImage import save_image
from google.cloud import storage

# Defining Web cam image details
CALTRANS_URL = "https://cwwp2.dot.ca.gov/vm/streamlist.htm"
webcam_data = fetch_webcam_data(CALTRANS_URL)
image_paths = {}
for cam in webcam_data:
    image_paths[f"{cam['nearby_place']}, {cam['cam_name']}"] = f"images/{cam['id']}.jpg"

# Extracting OpenAI environment variables
API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Get rid of whitespace
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip()
openai.api_key = OPENAI_API_KEY

# Defining various variables
base64_image = None
current_image = None
current_image_name = None
analyze_button = False
if "camera" not in st.session_state:
    st.session_state.camera = None

# Defining helper function to call OpenAI API
def compose_headers(api_key):
    if not api_key:
        raise ValueError("OPENAI API key is missing or empty")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def download_image_bytes(image_url):
    # Parse bucket name and filename
    bucket_name = "traffic-monitor-images"
    file_name = image_url.split("/")[-1]

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.download_as_bytes()

def compose_payload(image_path):
    image_bytes = download_image_bytes(image_path)
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    return {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful traffic monitor assistant."
                    "Rules:\n"
                    "1. If the image is not an image of traffic, respond with 'Invalid image, try again later.'.\n"
                    "2. Output whether traffic is 'Low traffic', 'Moderately low traffic', 'Medium traffic', 'Moderately high traffic', or 'High traffic', depending on the image and how densely packed the traffic is.\n"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please, check the traffic in this image." # Prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

def prompt_image(api_key, image_path):
    headers = compose_headers(api_key=api_key)
    payload = compose_payload(image_path=image_path)
    response = requests.post(url=API_URL, headers=headers, json=payload).json()

    if 'error' in response:
        raise ValueError(response['error']['message'])
    return response['choices'][0]['message']['content']

# Creating sidebar with instructions
st.sidebar.header("Instructions:")
st.sidebar.markdown(
    """
    This app allows you to monitor the traffic on different via Caltrans web cams.
    
    There is a button called Analyze.
    When you click it, your selected Web cam's image is submitted to GPT-4o with Vision in your OpenAI deployment to perform the image analysis and report its results back to the app.
    """
)

# Creating Home Page UI
st.title("Traffic Monitor Assistant")
main_container = st.container()
col1, col2 = main_container.columns([1, 3])
image_placeholder = col2.empty()
result_container = st.container()
result_placeholder = result_container.empty()

with col1:
    selected_camera = st.selectbox(
        "Select a Web Cam:",
        list(image_paths.keys()),
        index=list(image_paths.keys()).index(st.session_state.camera) if st.session_state.camera else 0
    )

    # Extract the cam ID from the selected image path
    selected_cam_id = os.path.basename(image_paths[selected_camera]).replace('.jpg', '')

    # Find the corresponding cam dictionary
    selected_cam_data = next((cam for cam in webcam_data if cam['id'] == selected_cam_id), None)

    # Save the image if the camera data was found
    if selected_cam_data:
        image_url = save_image(selected_cam_data)

    # Update session state camera and image paths
    current_image = image_url
    current_image_name = selected_camera
    st.session_state.camera = selected_camera

    if st.button("Analyze"):
        analyze_button = True

# Only render image in col2 *after* a selection is made and the image exists
if current_image:
    try:
        image_bytes = download_image_bytes(current_image)
        image_placeholder.image(
            image_bytes,
            caption=current_image_name,
            use_container_width=True
        )
    except Exception as e:
        image_placeholder.error(f"Could not load image: {e}")
else:
    image_placeholder.empty()

# If the analysis button is clicked, use GPT-4V to analyze the image
if analyze_button and current_image is not None:
    my_bar = st.progress(50, text="Processing your image. Please wait...")
    result = prompt_image(OPENAI_API_KEY, current_image)
    my_bar.progress(100)
    result_placeholder.text(
        f"Image analysis results for {current_image_name}:\n{result}"
    )
    inventory = result
    