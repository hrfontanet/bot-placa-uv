from database import SessionLocal, Pedido

usuarios = {}

def procesar_mensaje(user_id, mensaje):

    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "inicio"}

    estado = usuarios[user_id]

    if estado["paso"] == "inicio":
        estado["paso"] = "esperando_m2"
        return "¿Cuántos m² necesitás cubrir?"

    if estado["paso"] == "esperando_m2":
        try:
            m2 = float(mensaje)
        except:
            return "Por favor ingresá un número válido."

        precio_m2 = 20000
        total = m2 * precio_m2

        estado["paso"] = "confirmar"
        estado["total"] = total
        estado["m2"] = m2

        return f"Total: ${total}. Escribí 'confirmar' para seguir."

    if estado["paso"] == "confirmar":
        if mensaje.lower() == "confirmar":

            db = SessionLocal()
            nuevo_pedido = Pedido(
                user_id=user_id,
                producto="Placa UV",
                total=estado["total"]
            )
            db.add(nuevo_pedido)
            db.commit()
            db.close()

            estado["paso"] = "inicio"

            return "Pedido confirmado y guardado. Un asesor te contacta."
        else:
            estado["paso"] = "inicio"
            return "Pedido cancelado."
