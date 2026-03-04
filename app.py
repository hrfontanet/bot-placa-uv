import streamlit as st
from bot import procesar_mensaje

st.title("Prueba de Bot de Ventas")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribí algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del bot usando tu lógica
    respuesta = procesar_mensaje("user_streamlit", prompt)

    with st.chat_message("assistant"):
        st.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
