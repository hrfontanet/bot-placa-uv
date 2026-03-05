from fastapi import FastAPI
from bot import procesar_mensaje
from database import engine, Base, semilla

app = FastAPI()

@app.on_event("startup")
def startup_db():
    # Esto se ejecuta DESPUÉS de que el servidor está online, evitando el Status 1
    Base.metadata.create_all(bind=engine)
    semilla()

@app.get("/")
def home():
    return {"status": "Bot Placa UV funcionando"}

@app.post("/webhook")
async def webhook(data: dict):
    user_id = data.get("user_id")
    mensaje = data.get("mensaje")
    
    if not user_id or not mensaje:
        return {"respuesta": "Faltan datos en el JSON"}

    respuesta = procesar_mensaje(user_id, mensaje)
    return {"respuesta": respuesta}
