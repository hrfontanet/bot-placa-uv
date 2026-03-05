import math
from database import SessionLocal, Pedido, Producto
from ai import interpretar_mensaje, redactar_respuesta_humana # Importación corregida

usuarios = {}

def procesar_mensaje(user_id: str, mensaje: str):
    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "inicio"}
    
    estado = usuarios[user_id]
    db = SessionLocal()

    try:
        # 1. IA analiza la intención y extrae datos (m2, producto)
        interp = interpretar_mensaje(mensaje)
        
        # Lógica Consultiva Directa (Paso inicial)
        if estado["paso"] == "inicio" and interp.get("intencion") in ["consulta", "compra"]:
            # Buscamos producto que coincida con lo que detectó la IA
            prod_db = db.query(Producto).filter(Producto.nombre.ilike(f"%{interp.get('producto', '')}%")).first()
            
            if prod_db and interp.get("m2"):
                # CÁLCULO PROFESIONAL (Matemática exacta en Python)
                m2_reales = float(interp["m2"])
                m2_con_desperdicio = m2_reales * 1.10
                cant_placas = math.ceil(m2_con_desperdicio / prod_db.m2_por_unidad)
                total = cant_placas * prod_db.precio_unidad
                
                # Guardamos datos en el estado del usuario para la confirmación
                estado.update({
                    "paso": "confirmar",
                    "prod_id": prod_db.id,
                    "cant": cant_placas,
                    "total": total
                })

                # Datos para que la IA redacte con onda
                datos_calculo = {
                    "nombre": prod_db.nombre,
                    "m2_solicitados": m2_reales,
                    "cant_placas": cant_placas,
                    "total": total,
                    "descripcion": prod_db.descripcion,
                    "link": prod_db.link_url
                }

                # DELEGAMOS LA REDACCIÓN A LA IA (Lenguaje Natural)
                return redactar_respuesta_humana(datos_calculo, mensaje)

        # 2. Flujo de Confirmación
        if estado["paso"] == "confirmar":
            confirmaciones = ["si", "ok", "confirmar", "dale", "de una", "perfecto"]
            if any(palabra in mensaje.lower() for palabra in confirmaciones):
                # Guardamos el pedido real en Supabase
                nuevo = Pedido(
                    user_id=user_id, 
                    total=estado["total"], 
                    detalle=f"{estado['cant']} placas de {estado.get('prod_id')}"
                )
                db.add(nuevo)
                db.commit()
                usuarios[user_id] = {"paso": "inicio"}
                return "¡Espectacular! Ya registré tu pedido en el sistema. ¿Te gustaría que coordinemos el envío a tu zona o preferís retirar por nuestro depósito?"
            
            if "no" in mensaje.lower():
                usuarios[user_id] = {"paso": "inicio"}
                return "No hay problema, cancelamos la cotización. ¿Hay algún otro modelo que te interese ver o alguna duda técnica?"
            
        # 3. Fallback: Catálogo (Si la IA no entiende o falta info)
        productos = db.query(Producto).all()
        txt = "¡Hola! ¿Cómo estás? Te cuento que tenemos estas Placas UV disponibles para entrega inmediata:\n\n"
        for p in productos:
            txt += f"• {p.nombre}: ${p.precio_unidad}/unidad (Cubre {p.m2_por_unidad}m²)\n"
        txt += "\nDecime cuál te gusta y cuántos m² necesitás cubrir, así te paso el presupuesto con el 10% de desperdicio incluido."
        return txt

    finally:
        db.close()
