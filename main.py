from fastapi import FastAPI
from bot import procesar_mensaje
from database import engine, Base, semilla

app = FastAPI()

@app.on_event("startup")
def startup_db():
    # El try/except acá es VIDA para que Render no te tire Status 1
    try:
        Base.metadata.create_all(bind=engine)
        semilla()
    except Exception as e:
        print(f"Ignorando error de DB en arranque: {e}")

@app.get("/")
def home(): return {"status": "ok"}

@app.post("/webhook")
async def webhook(data: dict):
    u_id = data.get("user_id")
    msg = data.get("mensaje")
    if not u_id or not msg:
        return {"respuesta": "Faltan datos"}
    return {"respuesta": procesar_mensaje(u_id, msg)}
