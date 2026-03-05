import math
from database import SessionLocal, Pedido, Producto
from ai import interpretar_mensaje

usuarios = {}

def procesar_mensaje(user_id: str, mensaje: str):
    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "inicio"}
    
    estado = usuarios[user_id]
    db = SessionLocal()

    try:
        # 1. IA analiza la intención
        interp = interpretar_mensaje(mensaje)
        
        # Lógica Consultiva Directa
        if estado["paso"] == "inicio" and interp.get("intencion") in ["consulta", "compra"]:
            prod_db = db.query(Producto).filter(Producto.nombre.ilike(f"%{interp['producto']}%")).first()
            
            if prod_db and interp.get("m2"):
                # CÁLCULO PROFESIONAL
                m2_reales = float(interp["m2"])
                m2_con_desperdicio = m2_reales * 1.10
                cant_placas = math.ceil(m2_con_desperdicio / prod_db.m2_por_unidad)
                total = cant_placas * prod_db.precio_unidad
                
                estado.update({
                    "paso": "confirmar",
                    "prod_id": prod_db.id,
                    "cant": cant_placas,
                    "total": total
                })

                return (f"Perfecto. Para cubrir {m2_reales}m² necesitás {cant_placas} placas "
                        f"(incluye 10% de desperdicio).\n\n"
                        f"Producto: {prod_db.nombre}\n"
                        f"Detalle: {prod_db.descripcion}\n"
                        f"Total: ${total}\n\n"
                        f"¿Confirmamos el pedido? (Escribí 'si' o 'no')")

        # 2. Confirmación
        if estado["paso"] == "confirmar":
            if "si" in mensaje.lower():
                # Guardar en base de datos profesional
                nuevo = Pedido(user_id=user_id, total=estado["total"], detalle=f"{estado['cant']} placas")
                db.add(nuevo)
                db.commit()
                usuarios[user_id] = {"paso": "inicio"}
                return "¡Pedido confirmado! Un asesor te contactará para el pago y envío."
            
        # 3. Fallback: Catálogo
        productos = db.query(Producto).all()
        txt = "¡Hola! Soy tu asistente de ventas. ¿Qué estás buscando?\n\n"
        for p in productos:
            txt += f"• {p.nombre}: ${p.precio_unidad}/unidad ({p.m2_por_unidad}m²)\n"
        return txt

    finally:
        db.close()
