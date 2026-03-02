import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpretar_mensaje(mensaje):

    prompt = f"""
    Sos un asistente comercial de placas decorativas.

    Analizá el mensaje del cliente y devolvé SOLO un JSON válido con esta estructura:

    {{
        "intencion": "cotizar | consulta | saludo | desconocido",
        "producto": "string o null",
        "m2": numero o null
    }}

    Mensaje del cliente:
    "{mensaje}"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    contenido = response.choices[0].message.content

    return contenido
