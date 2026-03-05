from fastapi import FastAPI
from bot import procesar_mensaje
from ai import interpretar_mensaje
from database import engine, Base, semilla # Importamos las piezas de la DB

app = FastAPI()

# ESTO ES LO QUE FALTA: Crea las tablas y carga los productos al arrancar
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        semilla()
        print("Conexión a DB y Semilla exitosas")
    except Exception as e:
        print(f"Error al iniciar DB: {e}")

@app.get("/")
def home():
    return {"status": "Bot Placa UV funcionando"}

@app.post("/webhook")
def webhook(data: dict):
    # Usamos .get() para evitar errores si el JSON viene vacío
    user_id = data.get("user_id", "test_user")
    mensaje = data.get("mensaje", "")

    if not mensaje:
        return {"respuesta": "No recibí ningún mensaje."}

    respuesta = procesar_mensaje(user_id, mensaje)
    return {"respuesta": respuesta}

@app.get("/test-ai")
def test_ai(mensaje: str):
    return interpretar_mensaje(mensaje)
