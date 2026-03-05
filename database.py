import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================================
# INTERPRETAR MENSAJE DEL CLIENTE
# =========================================================

def interpretar_mensaje(mensaje: str):

    prompt = f"""
Sos un asistente que analiza mensajes de clientes de una empresa que vende placas UV para revestimiento.

Extraé la siguiente información en formato JSON:

- intencion: (consulta, compra, saludo, otro)
- producto: (placas, instalación, otro)
- m2: número de metros cuadrados si se menciona, sino null

Mensaje:
"{mensaje}"

Respondé SOLO JSON válido.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Respondé únicamente JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        contenido = response.choices[0].message.content.strip()

        # limpiar markdown si aparece
        if contenido.startswith("```"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()

        data = json.loads(contenido)

        return {
            "intencion": data.get("intencion"),
            "producto": data.get("producto"),
            "m2": data.get("m2")
        }

    except Exception as e:
        return {
            "error": "Error interpretando mensaje",
            "detalle": str(e)
        }


# =========================================================
# REDACTAR RESPUESTA HUMANA DEL BOT
# =========================================================

def redactar_respuesta_humana(producto: str, m2: float, subtotal: float):

    prompt = f"""
Sos un vendedor de placas UV.

Un cliente quiere comprar:

Producto: {producto}
Superficie: {m2} m2
Subtotal: {subtotal} pesos

Redactá una respuesta corta, clara y amable explicando el presupuesto.
No inventes precios ni datos adicionales.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sos un vendedor amable y profesional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"El subtotal para {m2} m² de {producto} es ${subtotal}."
