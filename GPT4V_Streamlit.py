# Importing required packages
import openai
import streamlit as st
import base64
import os
import requests

# Defining Web cam image details
image_paths = {
    "Web cam # 1": "images/GPT4V_OutOfStock_Image1.jpg",
    # "Web cam # 2": "images/GPT4V_OutOfStock_Image2.jpg",
    "Web cam # 2": "images/shelf2.jpg",
    "Web cam # 3": "images/GPT4V_OutOfStock_Image3.jpg",
    "Web cam # 4": "images/GPT4V_OutOfStock_Image4.jpg"
}

# Extracting OpenAI environment variables
API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Defining various variables
base64_image = None
current_image = None
current_image_name = None
analyse_button = False
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
        # "model": "gpt-4-turbo",
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You analyze shelf images for stock levels and detect which shelves need restocking. "
                    "Rules:\n"
                    "1. Shelves are numbered from bottom to top (0, 1, 2, ...).\n"
                    "2. Stock levels:\n"
                    "   - Well-stocked: >80% full.\n"
                    "   - Partially stocked: 30%-80% full.\n"
                    "   - Empty: <30% full.\n"
                    "3. Respond:\n"
                    "   - For each shelf, state whether it is well stocked, partially stocked, or empty.\n"
                    "   - Do it in this format: 'Shelf 0: Well stocked Shelf 1: Partially stocked ...'"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please, check this shelf image." # Prompt
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

def parse_response(response):
    # response = response.split('Shelf ')[1:]
    # response = [item.removesuffix('\n').strip() for item in response]
    # response_dict = {item.split(': ')[0]: item.split(': ')[1] for item in response}
    # return response_dict
    reponse = response.strip().split('\n')  # Split the string by newlines and remove extra whitespace
    response_list = [shelf.split(': ')[1].strip('.').strip() for shelf in reponse]
    return response_list

# Creating sidebar with instructions
st.sidebar.header("Instructions:")
st.sidebar.markdown(
    """
    This app allows you to choose between 4 Web cam images to check different areas of your fictitious shop.
    When you click specific Web cam button, its image is shown on the right side of the app.
    
    
    There is also an additional button, called Analyse.
    When you click it, your selected Web cam's image is submitted to GPT-4-Turbo with Vision in your Azure OpenAI deployment to perform the image analysis and report its results back to the app.
    """
)

# Creating Home Page UI
st.title("Out-Of-Stock Shop Assistant")
main_container = st.container()
col1, col2 = main_container.columns([1, 3])
image_placeholder = col2.empty()
result_container = st.container()
result_placeholder = result_container.empty()

# Creating button for each Web cam in the first column
for image_name, image_path in image_paths.items():
    # If the cam button is clicked, load the image and display it in the second column
    if col1.button(image_name):
        image_placeholder.image(image=image_path, caption=image_name, use_column_width=True)
        current_image = image_path
        current_image_name = image_name
        st.session_state.camera = image_name
        analyse_button = False
    # If the analysis button is clicked, preserve the last selected image
    elif st.session_state.camera == image_name:
        image_placeholder.image(image=image_path, caption=image_name, use_column_width=True)
        current_image = image_path
        current_image_name = image_name
        st.session_state.camera = image_name

# Creating analysis button in the first column
if col1.button("Analyse"):
    analyse_button = True

# If the analysis button is clicked, use GPT-4V to analyse the image
if analyse_button and current_image is not None:
    my_bar = st.progress(50, text="Processing your image. Please wait...")
    result = prompt_image(OPENAI_API_KEY, current_image)
    my_bar.progress(100)
    result_placeholder.text(
        f"Image analysis results for {current_image_name}:\n{result}"
    )
    print(parse_response(result)) # For debugging