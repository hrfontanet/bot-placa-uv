from fastapi import FastAPI
from bot import procesar_mensaje
from ai import interpretar_mensaje
from database import engine, Base, semilla # Importamos lo necesario de la DB

app = FastAPI()

# Esto es lo único que garantiza que el build NO falle
@app.on_event("startup")
def startup_db():
    Base.metadata.create_all(bind=engine)
    semilla()

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
