from database import SessionLocal, Producto, Pedido
from ai import interpretar_mensaje

usuarios = {}

def procesar_mensaje(user_id: str, mensaje: str):

    print("=== BOT NUEVO EJECUTANDO ===")
    print("Mensaje recibido:", mensaje)

    mensaje = mensaje.strip()

    if user_id not in usuarios:
        usuarios[user_id] = {"paso": "catalogo"}

    estado = usuarios[user_id]

    # =========================================================
    # 1️⃣ INTELIGENCIA ARTIFICIAL
    # =========================================================

    if estado["paso"] == "catalogo":

        interpretacion = interpretar_mensaje(mensaje)

        print("Interpretación IA:", interpretacion)

        if not interpretacion.get("error"):

            if interpretacion["intencion"] in ["consulta", "compra"]:

                db = SessionLocal()
                try:
                    productos = db.query(Producto).all()
                finally:
                    db.close()

                producto_encontrado = None
                producto_ai = str(interpretacion["producto"]).lower()

                for producto in productos:

                    nombre = producto.nombre.lower()

                    if (
                        producto_ai in nombre
                        or "placa" in nombre
                        or "placas" in producto_ai
                    ):
                        producto_encontrado = producto
                        break

                if producto_encontrado:

                    estado["producto"] = {
                        "id": producto_encontrado.id,
                        "nombre": producto_encontrado.nombre,
                        "precio_m2": producto_encontrado.precio_m2
                    }

                    # SI YA VINO CON M2
                    if interpretacion["m2"]:

                        m2 = float(interpretacion["m2"])

                        subtotal = round(
                            m2 * producto_encontrado.precio_m2,
                            2
                        )

                        estado["m2"] = m2
                        estado["subtotal"] = subtotal
                        estado["paso"] = "esperando_envio"

                        return (
                            f"Perfecto.\n\n"
                            f"Producto: {producto_encontrado.nombre}\n"
                            f"Superficie: {m2} m²\n"
                            f"Subtotal: ${subtotal}\n\n"
                            f"¿Cómo querés recibirlo?\n"
                            f"1. Envío\n"
                            f"2. Retiro"
                        )

                    estado["paso"] = "esperando_m2"

                    return (
                        f"Tenemos {producto_encontrado.nombre} "
                        f"a ${producto_encontrado.precio_m2}/m².\n\n"
                        f"¿Cuántos m² necesitás?"
                    )

        # =========================================================
        # MOSTRAR CATÁLOGO
        # =========================================================

        db = SessionLocal()
        try:
            productos = db.query(Producto).all()
        finally:
            db.close()

        texto = "Elegí producto:\n\n"

        for producto in productos:
            texto += (
                f"{producto.id}. {producto.nombre} "
                f"- ${producto.precio_m2}/m²\n"
            )

        estado["paso"] = "esperando_producto"

        return texto

    # =========================================================
    # 2️⃣ SELECCIÓN DE PRODUCTO
    # =========================================================

    if estado["paso"] == "esperando_producto":

        if not mensaje.isdigit():
            return "Elegí el número del producto."

        producto_id = int(mensaje)

        db = SessionLocal()
        try:
            producto = db.query(Producto).filter(
                Producto.id == producto_id
            ).first()
        finally:
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

    # =========================================================
    # 3️⃣ INGRESO M2
    # =========================================================

    if estado["paso"] == "esperando_m2":

        try:
            m2 = float(mensaje.replace(",", "."))

            if m2 <= 0:
                return "Ingresá un número válido de m²."

        except ValueError:
            return "Ingresá un número válido de m²."

        precio_m2 = estado["producto"]["precio_m2"]

        subtotal = round(m2 * precio_m2, 2)

        estado["m2"] = m2
        estado["subtotal"] = subtotal
        estado["paso"] = "esperando_envio"

        return (
            f"Subtotal: ${subtotal}\n\n"
            f"¿Cómo querés recibirlo?\n"
            f"1. Envío\n"
            f"2. Retiro"
        )

    # =========================================================
    # 4️⃣ ENVÍO
    # =========================================================

    if estado["paso"] == "esperando_envio":

        if mensaje == "1":

            costo_envio = 10000
            estado["envio"] = "Envío"

        elif mensaje == "2":

            costo_envio = 0
            estado["envio"] = "Retiro"

        else:

            return "Elegí 1 para envío o 2 para retiro."

        total_final = round(
            estado["subtotal"] + costo_envio,
            2
        )

        estado["total_final"] = total_final
        estado["costo_envio"] = costo_envio
        estado["paso"] = "confirmar"

        return (
            f"📦 Cotización Final\n\n"
            f"Producto: {estado['producto']['nombre']}\n"
            f"Superficie: {estado['m2']} m²\n"
            f"Subtotal: ${estado['subtotal']}\n"
            f"{estado['envio']}: ${costo_envio}\n\n"
            f"Total Final: ${total_final}\n\n"
            f"Escribí 'confirmar' o 'cancelar'."
        )

    # =========================================================
    # 5️⃣ CONFIRMAR
    # =========================================================

    if estado["paso"] == "confirmar":

        if mensaje.lower() == "confirmar":

            db = SessionLocal()

            try:

                nuevo_pedido = Pedido(
                    user_id=user_id,
                    producto=estado["producto"]["nombre"],
                    total=estado["total_final"]
                )

                db.add(nuevo_pedido)
                db.commit()

            finally:

                db.close()

            usuarios[user_id] = {"paso": "catalogo"}

            return "Pedido confirmado. Un asesor te contactará."

        if mensaje.lower() == "cancelar":

            usuarios[user_id] = {"paso": "catalogo"}

            return "Pedido cancelado."

        return "Escribí 'confirmar' o 'cancelar'."
