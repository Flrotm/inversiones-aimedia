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
newsapi_key = toml.load(".streamlit/secrets.toml")["newsapikey"]
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
import streamlit as st
import requests
from bs4 import BeautifulSoup
import tiktoken
import random

def estimate_tokens(text):
    # Estimate the number of tokens used by the text
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')  # or 'gpt-4' if you're using GPT-4
    tokens = encoding.encode(text)
    return len(tokens)

def get_text_from_url(url):
    # Your existing implementation...
    pass  # Replace with your code

def fetch_business_article():
    api_key = newsapi_key
    url = ('https://newsapi.org/v2/top-headlines?'
       'category=business&'
       'apiKey='+api_key)
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles')
        if articles:
            #choose a ranfom article
            try:
                num = random.randint(0, len(articles)-1)
                article = articles[num]
            except:
                article = articles[0]
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            article_text = f"{title}\n\n{description}\n\n{content}"
            return article_text
        else:
            st.error("No se encontraron artículos de negocios.")
            return ''
    except Exception as e:
        st.error(f"Error al obtener el artículo de negocios: {e}")
        return ''

def generate_prompt(platform, user_input, link_text, article_text=''):
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
    if article_text:
        prompt += f"\n\nContenido del artículo de negocios:\n{article_text}"
    return prompt

# Initialize session state variables
if 'platform' not in st.session_state:
    st.session_state['platform'] = None
if 'options' not in st.session_state:
    st.session_state['options'] = []
if 'selected_option' not in st.session_state:
    st.session_state['selected_option'] = ''
if 'article_text' not in st.session_state:
    st.session_state['article_text'] = ''

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

# Fetch business article button
if st.button("Obtener artículo de negocios"):
    with st.spinner('Obteniendo artículo de negocios...'):
        article_text = fetch_business_article()
        if article_text:
            st.session_state['article_text'] = article_text
            st.write("Artículo obtenido:")
            st.write(article_text)
        else:
            st.session_state['article_text'] = ''

# Generate post button
if st.button("Generar Post"):
    article_text = st.session_state.get('article_text', '')
    if not user_input.strip() and not article_text.strip():
        st.error("Por favor, introduce un tema sobre el que escribir.")
    elif not st.session_state['platform']:
        st.error("Por favor, selecciona una plataforma.")
    else:
        with st.spinner('Generando post...'):
            link_text = ''
            if link_input.strip():
                link_text = get_text_from_url(link_input)
            article_text = st.session_state.get('article_text', '')
            prompt = generate_prompt(st.session_state['platform'], user_input, link_text, article_text)
            print(prompt)

            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "assistant",
                            "content": prompt,
                        }
                    ],
                    model="gpt-4",
                )

                # Store options in session state
                st.session_state['options'] = chat_completion.choices[0].message.content
                st.session_state['selected_option'] = ''

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

# Display the generated response
if st.session_state['options']:
    st.subheader("Post generado:")
    st.write(st.session_state['options'])
