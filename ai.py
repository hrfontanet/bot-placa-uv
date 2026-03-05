import os
import json
from openai import OpenAI

# Exponemos el client para que bot.py lo use
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpretar_mensaje(mensaje: str):
    # Ajusté el prompt para que extraiga el tipo de placa específico (ej: marmol, tiza, gris)
    prompt = f"""
    Sos un asistente que analiza mensajes de clientes para una empresa de placas UV.
    Extraé la información en JSON:
    - intencion: (consulta, compra, saludo, otro)
    - producto: (el tipo de placa o color mencionado, ej: 'marmol', 'piedra', 'gris', 'tiza'. Si no especifica, pone 'placa')
    - m2: número de metros cuadrados (solo el número), sino null

    Mensaje: "{mensaje}"
    Respondé SOLO JSON válido.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Respondé únicamente en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        contenido = response.choices[0].message.content.strip()
        if contenido.startswith("```"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()

        data = json.loads(contenido)
        return {
            "intencion": data.get("intencion"),
            "producto": data.get("producto"),
            "m2": data.get("m2")
        }

    except Exception as e:
        return {"error": "Error interpretando", "detalle": str(e)}

# Esta función la usa bot.py para el lenguaje natural
def redactar_respuesta_humana(datos_calculo: dict, mensaje_usuario: str):
    prompt = f"""
    Sos un experto vendedor de placas UV. Estilo profesional, humano y servicial.
    
    Datos para la respuesta:
    {datos_calculo}
    
    Mensaje original del usuario: "{mensaje_usuario}"
    
    Instrucciones:
    - No parezcas un bot. Usá lenguaje natural.
    - Explicá el 10% de desperdicio de forma amigable.
    - Incluí links si están presentes.
    - Cerrá con una pregunta para avanzar con la venta.
    - No escribas cuentas matemáticas, da los resultados finales.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Sos un vendedor experto de revestimientos."},
                  {"role": "user", "content": prompt}],
        temperature=0.7 
    )
    return response.choices[0].message.content.strip()
