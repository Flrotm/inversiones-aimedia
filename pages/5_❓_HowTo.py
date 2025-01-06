import streamlit as st
import openai
import toml
from openai import OpenAI
from datetime import datetime
import pandas as pd
import json
st.set_page_config(page_title="How-To Generator", page_icon="❓")

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
    .stRadio > label {
        margin-bottom: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Generador de Post: Cómo Hacerlo")

topic = st.text_input("Ingresa el tema:", "")

if st.button("Generar Post"):
    if not topic.strip():
        st.error("Por favor, ingresa un tema.")
    else:
        with st.spinner('Generando post...'):
            # Prompt to create a question title (max 5 words), and 5 steps each with a title (max 5 words)
            # and a description (max 20 words)
            prompt = """Eres un asistente de marketing en Inversiones.io (una compañia de financiamiento colaborativo) y necesitas generar contenido para redes sociales
Crea un título de pregunta y luego 5 pasos para enseñar "cómo" hacer algo sobre el siguiente tema: ¿? """ + topic + """ 
El título de la pregunta (máximo 5 palabras).
Cada título de paso (máximo 5 palabras).
Cada descripción de paso dando intrucciones detalladas (máximo 30 palabras).
No uses comillas ni emojis.
El output debe tener el formato:
{
    "QuestionTitle": {},
    "Step1Title": {},
    "Step1Description": {},
    "Step2Title": {},
    "Step2Description": {},
    "Step3Title": {},
    "Step3Description": {},
    "Step4Title": {},
    "Step4Description": {},
    "Step5Title": {},
    "Step5Description": {}
}

            """

            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "assistant", "content": prompt}],
                    model="gpt-4o-2024-08-06",
                )
                st.session_state['howto'] = chat_completion.choices[0].message.content
                st.session_state['edit_mode'] = False
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")


if st.session_state.get('howto'):
    st.subheader("Post generado:")

    # Display the post in a nicely formatted way
    try:
        json_data = json.loads(st.session_state['howto'])
        print(json_data)
        st.write(f"**Question:** {json_data.get('QuestionTitle', '')}")
        for i in range(1, 6):
            step_title = json_data.get(f"Step{i}Title", '')
            step_desc = json_data.get(f"Step{i}Description", '')
            st.write(f"**Step {i}: {step_title}**")
            st.write(step_desc)
    except Exception as e:
        st.error(f"Error al mostrar el post: {e}")

    if st.button("Editar Post"):
        st.session_state['edit_mode'] = True

    if st.session_state.get('edit_mode', False):
        edited_text = st.text_area("Edita tu post (en formato JSON):", value=st.session_state['howto'], key="edit_post", height=300)
        if st.button("Guardar Edición"):
            st.session_state['howto'] = edited_text
            st.session_state['edit_mode'] = False

    if st.button("Descargar Post como CSV"):
        try:
            json_data = json.loads(st.session_state['howto'])
            data = {
                'QuestionTitle': [json_data.get('QuestionTitle', '')],
                'Step1Title': [json_data.get('Step1Title', '')],
                'Step1Description': [json_data.get('Step1Description', '')],
                'Step2Title': [json_data.get('Step2Title', '')],
                'Step2Description': [json_data.get('Step2Description', '')],
                'Step3Title': [json_data.get('Step3Title', '')],
                'Step3Description': [json_data.get('Step3Description', '')],
                'Step4Title': [json_data.get('Step4Title', '')],
                'Step4Description': [json_data.get('Step4Description', '')],
                'Step5Title': [json_data.get('Step5Title', '')],
                'Step5Description': [json_data.get('Step5Description', '')],
            }
            print(data)

            df = pd.DataFrame(data)
            current_date = datetime.now().strftime("%Y-%m-%d")
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="Descargar CSV", data=csv, file_name=f'post_howto_{current_date}.csv', mime='text/csv')
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el JSON: {e}")

#link to canvas design
link = "https://www.canva.com/design/DAGbX0ZkSk4/VKrL4qrSmvRGE-8Qjo4m6Q/edit?utm_content=DAGbX0ZkSk4&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton"
st.markdown(f"Si deseas ver el diseño en Canva, haz click [aquí]({link}).")