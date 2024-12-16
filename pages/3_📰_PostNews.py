import streamlit as st
import openai
import os
import requests
from bs4 import BeautifulSoup
import tiktoken  # For token estimation
import random
import toml
from openai import OpenAI
from datetime import datetime
import json
import pandas as pd

st.set_page_config(
    page_title="PostNews",
    page_icon="📰",
)



# Set your OpenAI API key
openai.api_key = toml.load(".streamlit/secrets.toml")["opeanaikey"]
newsapi_key = toml.load(".streamlit/secrets.toml")["newsapikey"]
client = OpenAI(
    api_key=openai.api_key,
)

st.markdown(
    """
    <style>
    .stButton button {
        background-color: #2076AC !important;
        color: white !important;
        border: none !important;
    }
    
    .stTextInput>div>div>input, .stTextArea textarea {
        border: 2px solid #2076AC !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea textarea:focus {
        border-color: #2076AC !important;
        box-shadow: 0 0 5px #2076AC !important;
    }

    .stSpinner > div > div {
        border-top-color: #2076AC !important;
    }

    .stMarkdown, .stText {
        color: black !important;
    }
    .stRadio > label {
        margin-bottom: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def estimate_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    tokens = encoding.encode(text)
    return len(tokens)

def fetch_rss_feed(feed_url):
    try:
        response = requests.get(feed_url)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.findAll('item')
        today = datetime.now().date()
        headlines = []
        for item in items:
            pub_date = item.pubDate.text if item.pubDate else None
            if pub_date:
                pub_date_parsed = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").date()
                if pub_date_parsed == today:
                    headlines.append({"title": item.title.text, "link": item.link.text, "description": item.description.text})
        return headlines
    except Exception as e:
        st.error(f"Error al obtener RSS Feed: {e}")
        return []

def fetch_business_headlines():
    url = ('https://newsapi.org/v2/top-headlines?'
           'category=business&'
           'apiKey=' + newsapi_key)
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles')
        if articles:
            headlines = []
            for article in articles:
                headlines.append({"title": article.get('title', ''), "link": article.get('url', ''), "description": article.get('description', '')})
            return headlines
        else:
            st.error("No se encontraron artículos de negocios.")
            return []
    except Exception as e:
        st.error(f"Error al obtener el artículo de negocios: {e}")
        return []

# Collect headlines from all sources
world_headlines = fetch_business_headlines()
gestion_headlines = fetch_rss_feed("https://gestion.pe/arc/outboundfeeds/rss/category/economia/?outputType=xml")
elcomercio_headlines = fetch_rss_feed("https://elcomercio.pe/arc/outboundfeeds/rss/category/economia/?outputType=xml")

# Limit to 10 headlines from each source
world_headlines = world_headlines[:10]
gestion_headlines = gestion_headlines[:10]
elcomercio_headlines = elcomercio_headlines[:10]

# Streamlit app
st.title("Inversiones.io Generador de Post")

# Function to display headlines with expandable descriptions in containers
def display_headlines_with_containers(header, headlines, key_prefix):
    today = datetime.now().strftime("%d/%m/%Y")
    st.header(f"{header} ({today})")
    selected_indexes = []
    with st.container():
        for i, headline in enumerate(headlines):
            col1, col2 = st.columns([1, 6])

            with col1:
                if st.checkbox("", key=f"{key_prefix}_news_{i}"):
                    selected_indexes.append(i)

            with col2:
                expander = st.expander(headline['title'])
                expander.write(headline.get('description', 'No hay descripción disponible.'))

    return selected_indexes

# Display headlines for each section
selected_world = display_headlines_with_containers("Noticias de MUNDO", world_headlines, "world")
selected_gestion = display_headlines_with_containers("Noticias de PERÚ - Gestion", gestion_headlines, "gestion")
selected_elcomercio = display_headlines_with_containers("Noticias de PERÚ - El Comercio", elcomercio_headlines, "elcomercio")

# Generate post button
if st.button("Generar Post"):
    selected_options = []

    # Gather selected news from all sections
    if selected_world:
        selected_options += [world_headlines[i] for i in selected_world]
    if selected_gestion:
        selected_options += [gestion_headlines[i] for i in selected_gestion]
    if selected_elcomercio:
        selected_options += [elcomercio_headlines[i] for i in selected_elcomercio]

    # Limit to 3 selected options to match expected output
    selected_options = selected_options[:3]

    if not selected_options:
        st.error("Por favor, selecciona una noticia para generar un post.")
    else:
        with st.spinner('Generando post...'):
            # Use simplified prompt to generate the post
            template_prompt = """
            Eres un asistente de marketing en Inversiones.io (una compañia de financiamiento colaborativo) y necesitas generar contenido para redes sociales.
            Resume estas noticias, con la idea de generar un post para 
redes sociales, haz el post lo más atractivo posible. No uses emojis ni le pongas comillas al titulo.Los titulos como maximo 6 palabras y las descripciones 40, pero presentalo de manera interesante y mas descriptiva que el input.
El output debe ser 
Mundo
{title1}
{content1}
Peru
{title2}
{content2}
Peru
{title3}
{content3}"""

            # Construct the content for the prompt
            content = ""
            for option in selected_options:
                content += f"{option['title']}\n{option['description']}\n"

            prompt = template_prompt + "\n" + content

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
                st.error(f"Ocurrió un error: {e}")
# Display the generated response
if st.session_state.get('options'):
    st.subheader("Post generado:")
    st.write(st.session_state['options'])
    # Print post lines for debugging
    post_lines = st.session_state['options'].split('\n')
    if st.button("Editar Post"):
        st.session_state['edit_mode'] = True

    if st.session_state.get('edit_mode', False):
        edited_text = st.text_area("Edita tu post:", value=st.session_state['options'], key="edit_post", height=300)
        if st.button("Guardar Edición"):
            st.session_state['options'] = edited_text
            st.session_state['edit_mode'] = False

    if st.button("Descargar Post como CSV"):
        # Create a CSV file with columns Title1, Content1, Title2, Content2, Title3, Content3}
        post_lines = st.session_state['options'].split('\n')
        titles = []
        contents = []
        for line in post_lines:
            word_count = len(line.split())
            if 2 <= word_count <= 6:
                titles.append(line)
            elif 10 <= word_count <= 30:
                contents.append(line)

        # Ensure there are exactly 3 titles and 3 contents
        while len(titles) < 3:
            titles.append('')
        while len(contents) < 3:
            contents.append('')

        data = {
            'Title1': [titles[0]],
            'Content1': [contents[0]],
            'Title2': [titles[1]],
            'Content2': [contents[1]],
            'Title3': [titles[2]],
            'Content3': [contents[2]]
        }
        df = pd.DataFrame(data)
        # Get current date to include in filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(label="Descargar CSV", data=csv, file_name=f'post_generado_{current_date}.csv', mime='text/csv')
