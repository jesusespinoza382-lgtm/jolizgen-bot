from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os

# ─── CREDENCIALES TWILIO ────────────────────────────────────────────────────────
ACCOUNT_SID = "AC89e58a75f65b87ca205789062f3aae8d"
AUTH_TOKEN  = "b8e1e527c350748a8054402aa784f349"
TWILIO_WHATSAPP = "whatsapp:+17372212163"   # número Twilio sandbox
ASESOR_WHATSAPP = "whatsapp:+584245927492"  # tu número Jolizgen

client = Client(ACCOUNT_SID, AUTH_TOKEN)
app = Flask(__name__)

# ─── ESTADO DE SESIÓN EN MEMORIA ───────────────────────────────────────────────
sessions = {}

# ─── CONTENIDO DEL BOT ─────────────────────────────────────────────────────────
FOOTER = (
    "\n\n📍 San Felipe, Yaracuy | 📞 +58-424-592-7492"
    "\n🌐 www.jolizgen.com | ✉️ info@jolizgen.com"
    "\n✅ 26 años | Equipos calibrados 2026 | Laboratorio móvil"
)

MENU_PRINCIPAL = (
    "👋 ¡Bienvenido a *JOLIZGEN INGENIERÍA*!\n"
    "Empresa líder en control de calidad de obras civiles.\n\n"
    "¿En qué podemos ayudarte hoy?\n\n"
    "1️⃣ ⛏️ Estudios de Suelos\n"
    "2️⃣ 🛣️ Asfalto\n"
    "3️⃣ 🏗️ Concreto\n"
    "4️⃣ 🏭 Construcción Civil\n"
    "5️⃣ 👨‍💼 Hablar con un Asesor\n\n"
    "_Escribe el número de tu opción._"
    + FOOTER
)

SERVICIOS = {
    "1": {
        "titulo": "⛏️ *ESTUDIOS DE SUELOS*",
        "descripcion": (
            "Realizamos ensayos geotécnicos de alta precisión:\n\n"
            "• Perforaciones SPT (Standard Penetration Test)\n"
            "• Calicatas y muestreo inalterado\n"
            "• Granulometría, límites de Atterberg\n"
            "• Compactación Proctor (estándar y modificado)\n"
            "• CBR de laboratorio y campo\n"
            "• Consolidación y corte directo\n"
            "• Informes geotécnicos para proyectos civiles\n\n"
            "¿Qué deseas hacer?\n\n"
            "A) 📅 Agendar consulta\n"
            "B) ℹ️ Más información\n"
            "C) 👨‍💼 Hablar con asesor\n"
            "M) 🔙 Volver al menú"
        ),
    },
    "2": {
        "titulo": "🛣️ *CONTROL DE CALIDAD EN ASFALTO*",
        "descripcion": (
            "Garantizamos la calidad de tus pavimentos:\n\n"
            "• Extracción y análisis de núcleos asfálticos\n"
            "• Ensayo Marshall (estabilidad y flujo)\n"
            "• Determinación de contenido de asfalto\n"
            "• Granulometría de mezcla asfáltica\n"
            "• Densidad in-situ (método nuclear y arena)\n"
            "• Evaluación de carpetas asfálticas existentes\n"
            "• Informes de control de calidad vial\n\n"
            "¿Qué deseas hacer?\n\n"
            "A) 📅 Agendar consulta\n"
            "B) ℹ️ Más información\n"
            "C) 👨‍💼 Hablar con asesor\n"
            "M) 🔙 Volver al menú"
        ),
    },
    "3": {
        "titulo": "🏗️ *CONTROL DE CALIDAD EN CONCRETO*",
        "descripcion": (
            "Aseguramos la resistencia de tus estructuras:\n\n"
            "• Muestreo y elaboración de cilindros de concreto\n"
            "• Ensayo de resistencia a la compresión (f'c)\n"
            "• Slump (asentamiento) en obra\n"
            "• Control de mezcla y dosificación\n"
            "• Análisis de agregados (fino y grueso)\n"
            "• Diseño de mezcla de concreto\n"
            "• Supervisión de vaciados estructurales\n\n"
            "¿Qué deseas hacer?\n\n"
            "A) 📅 Agendar consulta\n"
            "B) ℹ️ Más información\n"
            "C) 👨‍💼 Hablar con asesor\n"
            "M) 🔙 Volver al menú"
        ),
    },
    "4": {
        "titulo": "🏭 *CONSTRUCCIÓN CIVIL*",
        "descripcion": (
            "Servicios integrales para tu proyecto:\n\n"
            "• Inspección y supervisión técnica de obras\n"
            "• Control de calidad en fundaciones\n"
            "• Verificación de especificaciones estructurales\n"
            "• Reportes técnicos y memorias descriptivas\n"
            "• Asesoría en proyectos de infraestructura\n"
            "• Certificaciones de calidad para entes públicos\n\n"
            "¿Qué deseas hacer?\n\n"
            "A) 📅 Agendar consulta\n"
            "B) ℹ️ Más información\n"
            "C) 👨‍💼 Hablar con asesor\n"
            "M) 🔙 Volver al menú"
        ),
    },
}

INFO_EXTRA = {
    "1": (
        "ℹ️ *Más sobre Estudios de Suelos:*\n\n"
        "Nuestro laboratorio móvil llega a tu obra en cualquier punto del país. "
        "Los informes geotécnicos cumplen con las normas COVENIN y ASTM, "
        "aceptados por el Colegio de Ingenieros de Venezuela (CIV) y entes gubernamentales.\n\n"
        "⏱️ Tiempo de entrega: 5 a 10 días hábiles según alcance.\n\n"
        "¿Deseas agendar ahora?\n\n"
        "A) 📅 Sí, agendar consulta\n"
        "C) 👨‍💼 Hablar con asesor\n"
        "M) 🔙 Volver al menú"
    ),
    "2": (
        "ℹ️ *Más sobre Control de Asfalto:*\n\n"
        "Trabajamos con equipos calibrados y certificados en 2026. "
        "Ideal para obras viales, urbanismos y proyectos de infraestructura pública. "
        "Emitimos certificados de calidad reconocidos por el MINFRA.\n\n"
        "⏱️ Resultados de laboratorio: 3 a 7 días hábiles.\n\n"
        "¿Deseas agendar ahora?\n\n"
        "A) 📅 Sí, agendar consulta\n"
        "C) 👨‍💼 Hablar con asesor\n"
        "M) 🔙 Volver al menú"
    ),
    "3": (
        "ℹ️ *Más sobre Control de Concreto:*\n\n"
        "Supervisamos vaciados en tiempo real. "
        "Contamos con prensa de rotura de cilindros calibrada. "
        "Informes aceptados por ingenieros inspectores y entes contratantes.\n\n"
        "⏱️ Resultados: a los 7, 14 y 28 días de rotura.\n\n"
        "¿Deseas agendar ahora?\n\n"
        "A) 📅 Sí, agendar consulta\n"
        "C) 👨‍💼 Hablar con asesor\n"
        "M) 🔙 Volver al menú"
    ),
    "4": (
        "ℹ️ *Más sobre Construcción Civil:*\n\n"
        "Jolizgen tiene 26 años de trayectoria en Venezuela. "
        "Hemos participado en obras de infraestructura vial, edificaciones, "
        "urbanismos y proyectos gubernamentales en todo el país.\n\n"
        "📋 Disponemos de personal técnico certificado e ingenieros especialistas.\n\n"
        "¿Deseas agendar ahora?\n\n"
        "A) 📅 Sí, agendar consulta\n"
        "C) 👨‍💼 Hablar con asesor\n"
        "M) 🔙 Volver al menú"
    ),
}

MSG_ASESOR = (
    "👨‍💼 *Te conectamos con un asesor de Jolizgen*\n\n"
    "Un ingeniero especialista te atenderá personalmente.\n\n"
    "📞 Llama o escribe directamente:\n"
    "*+58-424-592-7492*\n\n"
    "⏰ Horario: Lunes a Viernes 8:00 AM – 5:00 PM\n\n"
    "¿Deseas hacer algo más?\n"
    "M) 🔙 Volver al menú"
    + FOOTER
)

MSG_AGENDAR = (
    "📅 *AGENDAR CONSULTA CON JOLIZGEN*\n\n"
    "Para agendar tu consulta técnica gratuita, por favor envíanos:\n\n"
    "1. 👤 Tu nombre completo\n"
    "2. 🏗️ Nombre o descripción de tu proyecto\n"
    "3. 📍 Ubicación de la obra\n"
    "4. 📆 Fecha y hora preferida\n\n"
    "_Responde con esa información y un asesor te confirmará la cita._\n\n"
    "M) 🔙 Volver al menú"
    + FOOTER
)

MSG_DATOS_RECIBIDOS = (
    "✅ *¡Datos recibidos!*\n\n"
    "Un asesor de Jolizgen revisará tu solicitud y te contactará "
    "en un máximo de *2 horas hábiles* para confirmar tu cita.\n\n"
    "¡Gracias por confiar en Jolizgen Ingeniería! 🏗️\n\n"
    "M) 🔙 Volver al menú"
    + FOOTER
)

MSG_DEFAULT = (
    "🤖 No entendí tu mensaje.\n\n"
    "Escribe *MENU* o *M* para ver el menú principal, "
    "o el número de la opción que deseas."
    + FOOTER
)


# ─── NOTIFICACIÓN AL ASESOR ────────────────────────────────────────────────────
def notificar_asesor(numero_cliente, datos):
    try:
        client.messages.create(
            from_=TWILIO_WHATSAPP,
            to=ASESOR_WHATSAPP,
            body=(
                f"🔔 *NUEVA SOLICITUD DE CITA - JOLIZGEN*\n\n"
                f"📱 Cliente: {numero_cliente}\n"
                f"📋 Datos:\n{datos}\n\n"
                f"Respóndele directamente a este número."
            )
        )
    except Exception as e:
        print(f"Error notificando asesor: {e}")


# ─── LÓGICA PRINCIPAL ──────────────────────────────────────────────────────────
def procesar_mensaje(numero, texto):
    texto = texto.strip().upper()
    estado = sessions.get(numero, {"paso": "menu"})

    respuesta = ""

    # Comandos globales
    if texto in ["MENU", "M", "INICIO", "HOLA", "HELLO", "HI", "START", "0"]:
        sessions[numero] = {"paso": "menu"}
        return MENU_PRINCIPAL

    # Estado: menú principal → seleccionar servicio
    if estado["paso"] == "menu":
        if texto in SERVICIOS:
            sessions[numero] = {"paso": "servicio", "servicio": texto}
            s = SERVICIOS[texto]
            return f"{s['titulo']}\n\n{s['descripcion']}" + FOOTER
        else:
            return MENU_PRINCIPAL

    # Estado: dentro de un servicio
    if estado["paso"] == "servicio":
        servicio = estado.get("servicio", "1")

        if texto == "A":  # Agendar
            sessions[numero] = {"paso": "agendar", "servicio": servicio}
            return MSG_AGENDAR

        elif texto == "B":  # Más información
            return INFO_EXTRA.get(servicio, MSG_DEFAULT) + FOOTER

        elif texto == "C":  # Asesor
            sessions[numero] = {"paso": "menu"}
            return MSG_ASESOR

        elif texto in SERVICIOS:  # Cambiar de servicio
            sessions[numero] = {"paso": "servicio", "servicio": texto}
            s = SERVICIOS[texto]
            return f"{s['titulo']}\n\n{s['descripcion']}" + FOOTER

        else:
            s = SERVICIOS[servicio]
            return f"Por favor elige A, B, C o M.\n\n{s['titulo']}\n\n{s['descripcion']}" + FOOTER

    # Estado: agendando
    if estado["paso"] == "agendar":
        # Si el usuario envió sus datos (cualquier texto largo)
        if len(texto) > 10:
            sessions[numero] = {"paso": "menu"}
            notificar_asesor(numero, texto)  # ← avisa a tu WhatsApp
            return MSG_DATOS_RECIBIDOS
        elif texto == "M":
            sessions[numero] = {"paso": "menu"}
            return MENU_PRINCIPAL
        else:
            return MSG_AGENDAR

    return MENU_PRINCIPAL


# ─── WEBHOOK TWILIO ─────────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    numero = request.form.get("From", "")
    texto = request.form.get("Body", "")

    respuesta_texto = procesar_mensaje(numero, texto)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(respuesta_texto)
    return str(resp)


@app.route("/", methods=["GET"])
def home():
    return "✅ Bot WhatsApp Jolizgen activo.", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
