# Importing required packages
import openai
import streamlit as st
import base64
import os
import requests

# Defining Web cam image details
image_paths = {
    "Web cam # 1": "images/example.jpg",
}

# Extracting OpenAI environment variables
API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def compose_payload(image_path):
    # Encoding image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

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

# Creating button for each Web cam in the first column
for image_name, image_path in image_paths.items():
    # If the cam button is clicked, load the image and display it in the second column
    if col1.button(image_name):
        image_placeholder.image(image=image_path, caption=image_name, use_container_width=True)
        current_image = image_path
        current_image_name = image_name
        st.session_state.camera = image_name
        analyze_button = False
    # If the analysis button is clicked, preserve the last selected image
    elif st.session_state.camera == image_name:
        image_placeholder.image(image=image_path, caption=image_name, use_container_width=True)
        current_image = image_path
        current_image_name = image_name
        st.session_state.camera = image_name

# Creating analysis button in the first column
if col1.button("Analyze"):
    analyze_button = True

# If the analysis button is clicked, use GPT-4V to analyze the image
if analyze_button and current_image is not None:
    my_bar = st.progress(50, text="Processing your image. Please wait...")
    result = prompt_image(OPENAI_API_KEY, current_image)
    my_bar.progress(100)
    result_placeholder.text(
        f"Image analysis results for {current_image_name}:\n{result}"
    )
    inventory = result
    