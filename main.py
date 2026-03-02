from fastapi import FastAPI
from bot import procesar_mensaje

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
