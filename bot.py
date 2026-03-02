from database import SessionLocal, Pedido, Producto

usuarios = {}

def procesar_mensaje(user_id, mensaje):

    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "catalogo"}

    estado = usuarios[user_id]

    # Mostrar catálogo
    if estado["paso"] == "catalogo":

        db = SessionLocal()
        productos = db.query(Producto).all()
        db.close()

        texto = "Elegí producto:\n"

        for producto in productos:
            texto += f"{producto.id}. {producto.nombre} - ${producto.precio_m2}/m²\n"

        estado["paso"] = "esperando_producto"
        return texto

    # Esperar selección
    if estado["paso"] == "esperando_producto":

        try:
            producto_id = int(mensaje)
        except:
            return "Elegí el número del producto."

        db = SessionLocal()
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        db.close()

        if not producto:
            return "Opción inválida. Elegí el número del producto."

        estado["producto"] = {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio_m2": producto.precio_m2
        }

        estado["paso"] = "esperando_m2"
        return "¿Cuántos m² necesitás cubrir?"

    # Esperar m2
    if estado["paso"] == "esperando_m2":

        try:
            m2 = float(mensaje)
        except:
            return "Ingresá un número válido de m²."

        precio_m2 = estado["producto"]["precio_m2"]
        subtotal = m2 * precio_m2

        estado["m2"] = m2
        estado["subtotal"] = subtotal
        estado["paso"] = "esperando_envio"

        return "¿Cómo querés recibirlo?\n1. Envío\n2. Retiro"

    # Envío
    if estado["paso"] == "esperando_envio":

        if mensaje == "1":
            costo_envio = 10000
            estado["envio"] = "Envío"
        elif mensaje == "2":
            costo_envio = 0
            estado["envio"] = "Retiro"
        else:
            return "Elegí 1 para envío o 2 para retiro."

        total_final = estado["subtotal"] + costo_envio
        estado["total_final"] = total_final
        estado["paso"] = "confirmar"

        return (
            f"\n📦 Cotización Final\n"
            f"Producto: {estado['producto']['nombre']}\n"
            f"Superficie: {estado['m2']} m²\n"
            f"Subtotal: ${estado['subtotal']}\n"
            f"{estado['envio']}: ${costo_envio}\n\n"
            f"Total Final: ${total_final}\n\n"
            "Escribí 'confirmar' o 'cancelar'."
        )

    # Confirmación
    if estado["paso"] == "confirmar":

        if mensaje.lower() == "confirmar":

            db = SessionLocal()
            nuevo_pedido = Pedido(
                user_id=user_id,
                producto=estado["producto"]["nombre"],
                total=estado["total_final"]
            )
            db.add(nuevo_pedido)
            db.commit()
            db.close()

            usuarios[user_id] = {"paso": "catalogo"}

            return "Pedido confirmado y guardado. Un asesor te contacta."

        else:
            usuarios[user_id] = {"paso": "catalogo"}
            return "Pedido cancelado."
