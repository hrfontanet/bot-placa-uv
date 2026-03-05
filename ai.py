import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def interpretar_mensaje(mensaje: str):

    prompt = f"""
Sos un asistente que analiza mensajes de clientes de una empresa que vende placas UV.

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
                {"role": "system", "content": "Respondé únicamente en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        contenido = response.choices[0].message.content.strip()

        if contenido.startswith("```"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()

        data = json.loads(contenido)

        # Validación manual simple
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

def redactar_respuesta(datos_calculo: dict, mensaje_usuario: str):
    prompt = f"""
    Sos un experto vendedor de placas UV. Tu estilo es profesional, directo y servicial.
    
    Contexto del cálculo:
    {datos_calculo}
    
    Mensaje del usuario: "{mensaje_usuario}"
    
    Instrucciones:
    - Usá lenguaje natural, no parezcas un bot.
    - Explicá que sumaste un 10% por desperdicio de forma natural.
    - Si hay un link de producto, incluyelo.
    - Terminá con una pregunta para cerrar la venta (envío o retiro, o forma de pago).
    - No uses fórmulas matemáticas, solo resultados amigables.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 # Más alto para que sea menos robótico
    )
    return response.choices[0].message.content.strip()
