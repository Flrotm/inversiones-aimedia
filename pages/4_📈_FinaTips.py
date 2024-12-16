import streamlit as st
import openai
import toml
from openai import OpenAI
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="FinaTips",
    page_icon="📈",
)

openai.api_key = toml.load(".streamlit/secrets.toml")["opeanaikey"]
client = OpenAI(api_key=openai.api_key)

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
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Generador de Post de Tips Financieros")

user_input = st.text_input("Ingresa el tema o tip financiero:")
if st.button("Generar Post"):
    if not user_input.strip():
        st.error("Por favor, ingresa un tip financiero.")
    else:
        with st.spinner('Generando post...'):
            # Define prompt
            prompt = """Eres un asistente de marketing en Inversiones.io (una compañia de financiamiento colaborativo) y necesitas generar contenido para redes sociales.
            Crea un post atractivo para redes sociales sobre el siguiente tema: """ + user_input + """

Instrucciones:
- Genera un título de máximo 6 palabras. Escribelo directamente, sin seguirlo de dos puntos.
- Genera tres párrafos separados, cada uno con aproximadamente 20 palabras.
- Hazlo claro, profesional y sin emojis.

Output:
{title}
{paragraph1}
{paragraph2}
{paragraph3}
"""

            # Generate content
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "assistant", "content": prompt}],
                    model="gpt-4o-2024-08-06"
                )
                print(response)
                st.session_state['options'] = response.choices[0].message.content
                st.session_state['edit_mode'] = False
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
# Display Generated Post
if 'options' in st.session_state:
    st.subheader("Post generado:")
    st.write(st.session_state['options'])
    
    # Edit Mode
    if st.button("Editar Post"):
        st.session_state['edit_mode'] = True
    if st.session_state.get('edit_mode', False):
        edited_text = st.text_area("Edita tu post:", value=st.session_state['options'], key="edit_post", height=300)
        if st.button("Guardar Edición"):
            st.session_state['options'] = edited_text
            st.session_state['edit_mode'] = False


    if st.button("Descargar Post como CSV"):
        # Extract lines and clean the output
        lines = st.session_state['options'].strip().split('\n')
        print(lines)



        # Prepare the data for the CSV
        data = {
            'Title1': [lines[0]],
            'Content1': [lines[2]],
            'Content2': [lines[4]],
            'Content3': [lines[6]]
        }
        print(data)

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV format
        current_date = datetime.now().strftime("%Y-%m-%d")
        csv = df.to_csv(index=False, encoding='utf-8-sig')

        # Provide a download button for the CSV
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name=f'post_tip_{current_date}.csv',
            mime='text/csv'
        )

