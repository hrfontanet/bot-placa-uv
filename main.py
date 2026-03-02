from fastapi import FastAPI
from bot import procesar_mensaje
from ai import interpretar_mensaje

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot Placa UV funcionando"}

@app.post("/webhook")
def webhook(data: dict):
    user_id = data.get("user_id")
    mensaje = data.get("mensaje")

    respuesta = procesar_mensaje(user_id, mensaje)

    return {"respuesta": respuesta}

@app.get("/test-ai")
def test_ai(mensaje: str):
    return interpretar_mensaje(mensaje)
