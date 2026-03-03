import os
import json
from openai import OpenAI

# Inicializa cliente usando variable de entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpretar_mensaje(mensaje: str):
    try:
        prompt = f"""
Sos un asistente que analiza mensajes de clientes de una empresa que vende placas UV.

Extraé la siguiente información en formato JSON:
- intencion: (consulta, compra, saludo, otro)
- producto: (placas, instalación, otro)
- m2: número de metros cuadrados si se menciona, sino null

Mensaje del cliente:
"{mensaje}"

Respondé SOLO el JSON válido.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Respondé únicamente en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        contenido = response.choices[0].message.content.strip()

        # Limpieza por si el modelo devuelve ```json
        if contenido.startswith("```"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()

        return json.loads(contenido)

    except Exception as e:
        return {
            "error": "Error interpretando mensaje",
            "detalle": str(e)
        }
