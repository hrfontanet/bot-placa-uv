import math
from database import SessionLocal, Pedido, Producto
from ai import interpretar_mensaje, client # Asegurate de que 'client' esté exportado en ai.py

usuarios = {}

def redactar_respuesta_humana(datos_calculo: dict, mensaje_usuario: str):
    """
    Usa la IA para transformar datos fríos en una respuesta de venta natural.
    """
    prompt = f"""
    Sos un experto vendedor de placas UV y revestimientos. Tu estilo es profesional, 
    cercano, resolutivo y muy humano. No respondas como un robot.
    
    Contexto de la cotización actual:
    - Producto: {datos_calculo.get('nombre')}
    - Metros cuadrados solicitados: {datos_calculo.get('m2_solicitados')}m2
    - Cantidad de placas a vender: {datos_calculo.get('cant_placas')} (ya incluye el 10% de desperdicio)
    - Total a cobrar: ${datos_calculo.get('total')}
    - Descripción técnica: {datos_calculo.get('descripcion')}
    - Link de referencia: {datos_calculo.get('link')}

    Mensaje del usuario: "{mensaje_usuario}"

    Instrucciones de respuesta:
    1. Confirmá que entendiste las medidas.
    2. Explicá de forma natural que sumaste un 10% por recortes/desperdicio.
    3. Mencioná brevemente una característica técnica (ej: se pega con silicona).
    4. Da el precio total de forma clara.
    5. Cerrá con una pregunta para avanzar (envío, retiro o medio de pago).
    6. Si hay un link, incluyelo sutilmente.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Sos un vendedor humano de una tienda de revestimientos."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Fallback por si falla la API de OpenAI en la redacción
        return f"Perfecto, para {datos_calculo.get('m2_solicitados')}m2 necesitás {datos_calculo.get('cant_placas')} placas. El total es ${datos_calculo.get('total')}. ¿Confirmamos?"

def procesar_mensaje(user_id: str, mensaje: str):
    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "inicio"}
    
    estado = usuarios[user_id]
    db = SessionLocal()

    try:
        # 1. IA analiza la intención y extrae datos
        interp = interpretar_mensaje(mensaje)
        
        # Lógica Consultiva Directa
        if estado["paso"] == "inicio" and interp.get("intencion") in ["consulta", "compra"]:
            # Buscamos el producto en la base de datos
            prod_db = db.query(Producto).filter(Producto.nombre.ilike(f"%{interp.get('producto', '')}%")).first()
            
            if prod_db and interp.get("m2"):
                # CÁLCULO PROFESIONAL
                m2_reales = float(interp["m2"])
                m2_con_desperdicio = m2_reales * 1.10
                cant_placas = math.ceil(m2_con_desperdicio / prod_db.m2_por_unidad)
                total = cant_placas * prod_db.precio_unidad
                
                # Preparamos datos para que la IA redacte
                datos_calculo = {
                    "nombre": prod_db.nombre,
                    "m2_solicitados": m2_reales,
                    "cant_placas": cant_placas,
                    "total": total,
                    "descripcion": prod_db.descripcion,
                    "link": prod_db.link_url
                }

                estado.update({
                    "paso": "confirmar",
                    "prod_id": prod_db.id,
                    "cant": cant_placas,
                    "total": total
                })

                # DELEGAMOS LA RESPUESTA A LA IA
                return redactar_respuesta_humana(datos_calculo, mensaje)

        # 2. Confirmación
        if estado["paso"] == "confirmar":
            # Dejamos que la IA también maneje la confirmación sutilmente si querés, 
            # pero aquí mantenemos control del flujo.
            if any(palabra in mensaje.lower() for palabra in ["si", "ok", "confirmar", "dale"]):
                nuevo = Pedido(user_id=user_id, total=estado["total"], detalle=f"{estado['cant']} placas de {estado.get('prod_id')}")
                db.add(nuevo)
                db.commit()
                usuarios[user_id] = {"paso": "inicio"}
                return "¡Espectacular! Ya registré tu pedido. ¿Te gustaría que coordinemos el envío o preferís retirar por nuestro depósito?"
            
            if "no" in mensaje.lower():
                usuarios[user_id] = {"paso": "inicio"}
                return "No hay problema. ¿Hay algo más en lo que te pueda ayudar o buscás otro modelo?"
            
        # 3. Fallback: Catálogo (cuando no hay m2 o producto claro)
        productos = db.query(Producto).all()
        txt = "¡Hola! Cómo estás? Te paso nuestros modelos disponibles de Placas UV:\n\n"
        for p in productos:
            txt += f"• {p.nombre}: ${p.precio_unidad}/unidad (Cubre {p.m2_por_unidad}m²)\n"
        txt += "\nDecime cuál te gusta y cuántos m² necesitás cubrir así te asesoro."
        return txt

    finally:
        db.close()
