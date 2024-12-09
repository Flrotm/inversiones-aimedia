import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

st.write("# Bienvenido al generador de contenido de Inversiones.io👋")

st.sidebar.success("Selecciona una herramienta")

st.markdown(
"""    

## Descripción
Inversiones.io ha desarrollado una plataforma de generación de contenido automatizado para redes sociales, enfocada en el equipo de marketing. Utilizando IA generativa, esta herramienta crea posts estructurados para diferentes redes, ahorrando tiempo y garantizando la coherencia en la comunicación.


## Herramientas Disponibles

1. **[Versión 1: Generador de Post para Redes Sociales](PostV1)**
   - **Objetivo**: Crear posts para diferentes plataformas sociales.
   - **Redes Compatibles**: Meta, LinkedIn y TikTok.
   - **Características**: Generación de posts con tono ajustado según la red social. Los posts de Meta son más amigables, LinkedIn es profesional, y TikTok genera guiones en lugar de texto.
   - **Flujo de Uso**:
     1. Seleccionar la red social.
     2. Introducir el contenido o tema de la publicación.
     3. (Opcional) agregar un enlace.
     4. Obtener un artículo de negocios para inspiración.
     5. Generar y revisar el post final.

2. **[Versión 2: Generador de Post con Noticias](PostNews)**
   - **Objetivo**: Automatizar la creación de contenido basado en noticias diarias.
   - **Fuentes de Noticias**: NewsAPI (titulares de negocios globales), Gestión (Economía) y El Comercio (Titulares).
   - **Características**: Permite seleccionar noticias por sección, generar resúmenes y descargar el contenido estructurado en CSV para subirlo a Canva.
   - **Flujo de Uso**:
     1. Seleccionar una noticia de cada sección.
     2. Generar el post.
     3. (Opcional) Editar el contenido antes de descargar.
     4. Descargar en formato CSV.
     5. Subir a Canva para diseñar el post final usando la función "Data Autofill".

3. **[Versión 3: Nuevos Templates! (Finatips y Howtos)](FinaTips)**
   - **Objetivo**: Ampliar la funcionalidad ofreciendo dos nuevos tipos de plantillas.
   - **Nuevos Templates**:
     - **Finatips**: Genera un post con un título y 3 párrafos sobre un tema financiero específico.
     - **How-To**: Genera un post tipo guía con un título en forma de pregunta, y 5 pasos con títulos  y descripciones detalladas .
   - **Flujo de Uso**:
     1. Seleccionar el tipo de template (Finatips o How-To).
     2. Introducir el tema.
     3. Generar el post.
     4. (Opcional) Editar el contenido.
     5. Descargar el post en CSV para subirlo a Canva u otras plataformas.

> **Nota**: Explora cada herramienta en la barra lateral para comenzar. ¡Generar contenido nunca ha sido tan fácil y rápido!

---

### Recursos Adicionales
Para aprender más sobre INVESRIONES.IO, visita nuestro sitio web oficial:
- [Inversiones.io](https://inversiones.io)

# Para cualquier comentario contactar a fuccellim@gmail.com
"""
)
