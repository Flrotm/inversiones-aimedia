import streamlit as st
import openai
import os
import requests
from bs4 import BeautifulSoup
import tiktoken  # For token estimation
from openai import OpenAI
#load from toml
import toml
# Set your OpenAI API key
openai.api_key = toml.load(".streamlit/secrets.toml")["opeanaikey"]
client = OpenAI(
    # This is the default and can be omitted
    api_key=openai.api_key,
)
st.markdown(
    """
    <style>
    /* Your existing CSS styles */
    .stButton button {
        background-color: #2076AC !important;
        color: white !important;
        border: none !important;
    }

    /* Text input and text area borders */
    .stTextInput>div>div>input, .stTextArea textarea {
        border: 2px solid #2076AC !important;
    }
    
    /* Focus state for text inputs and text areas */
    .stTextInput>div>div>input:focus, .stTextArea textarea:focus {
        border-color: #2076AC !important;
        box-shadow: 0 0 5px #2076AC !important;
    }

    /* Spinner color */
    .stSpinner > div > div {
        border-top-color: #2076AC !important;
    }

    /* Keep the main text black */
    .stMarkdown, .stText {
        color: black !important;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

def estimate_tokens(text):
    # Estimate the number of tokens used by the text
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')  # or 'gpt-4' if you're using GPT-4
    tokens = encoding.encode(text)
    return len(tokens)

def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted tags
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'noscript']):
            tag.decompose()

        # Extract text from specific tags
        texts = soup.find_all(text=True)

        # Define whitelist of tags
        whitelist = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']

        visible_texts = []
        for t in texts:
            if t.parent.name in whitelist:
                text = t.strip()
                if text:
                    visible_texts.append(text)

        # Join the texts
        text = ' '.join(visible_texts)

        # Clean up the text
        text = ' '.join(text.split())

        # Estimate tokens and limit text length
        MAX_TOKENS = 500  # Adjust based on your needs
        tokens = estimate_tokens(text)

        while tokens > MAX_TOKENS:
            # Reduce text length by truncating
            text = text[:int(len(text) * 0.9)]
            tokens = estimate_tokens(text)

        return text
    except Exception as e:
        st.error(f"Error al obtener el texto del enlace: {e}")
        return ''

def generate_prompt(platform, user_input, link_text):
    if platform == "Meta":
        with open("meta.txt", "r") as file:
            prompt = file.read()
    elif platform == "LinkedIn":
        with open("linkedin.txt", "r") as file:
            prompt = file.read()
    elif platform == "TikTok":
        with open("tiktok.txt", "r") as file:
            prompt = file.read()
    
    # Construct the prompt
    prompt += f"\n\nTema: {user_input}"
    if link_text:
        prompt += f"\n\nContenido del enlace proporcionado:\n{link_text}"
    return prompt

# Initialize session state variables
if 'platform' not in st.session_state:
    st.session_state['platform'] = None
if 'options' not in st.session_state:
    st.session_state['options'] = []
if 'selected_option' not in st.session_state:
    st.session_state['selected_option'] = ''

# Streamlit app
st.title("Inversiones.io Generador de Post")
st.subheader("Selecciona una red social y escribe el contenido que deseas incluir en la publicación.")

# Platform selection using buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Meta"):
        st.session_state['platform'] = "Meta"
with col2:
    if st.button("LinkedIn"):
        st.session_state['platform'] = "LinkedIn"
with col3:
    if st.button("TikTok"):
        st.session_state['platform'] = "TikTok"

# Display the selected platform
if st.session_state['platform']:
    st.write(f"Plataforma seleccionada: **{st.session_state['platform']}**")

# Text input
user_input = st.text_area("Introduce y describe el tema sobre el que deseas escribir:")

# Link input
link_input = st.text_input("Introduce un enlace (opcional):")

# Generate post button

# Generate post button
if st.button("Generate Post"):
    if not user_input.strip():
        st.error("Por favor, introduce un tema sobre el que escribir.")
    elif not st.session_state['platform']:
        st.error("Por favor, selecciona una plataforma.")
    else:
        with st.spinner('Generando post...'):
            link_text = ''
            if link_input.strip():
                link_text = get_text_from_url(link_input)
            prompt = generate_prompt(st.session_state['platform'], user_input, link_text)
            print(prompt)


            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "assistant",
                            "content": prompt,
                        }
                    ],
                    model="gpt-4o-2024-08-06",
                )

                # Store options in session state
                st.session_state['options'] = chat_completion.choices[0].message.content
                st.session_state['selected_option'] = ''

            except Exception as e:
                st.error(f"Ocurrio un error: {e}")


# Display the generated response
if st.session_state['options']:
    st.subheader("Post generado:")
    st.write(st.session_state['options'])
    
    