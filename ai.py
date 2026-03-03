import os
import json
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class MensajeInterpretado(BaseModel):
    intencion: str
    producto: str
    m2: Optional[float] = None


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

        validado = MensajeInterpretado(**data)

        return validado.model_dump()

    except ValidationError as ve:
        return {
            "error": "Error de validación",
            "detalle": ve.errors()
        }

    except Exception as e:
        return {
            "error": "Error interno",
            "detalle": str(e)
        }
