# Webex Python & Google ADK Integration Template

Plantilla base y esqueleto de referencia para la integración entre el SDK de **Cisco Webex en Python** y agentes inteligentes desarrollados con **Google Agent Development Kit (ADK)** y modelos **Gemini**.

## 📌 Estado Actual del Proyecto

El repositorio funciona como un **template desacoplado y reutilizable** que ilustra la progresión desde llamadas directas a la API de Webex hasta un bot conversacional con capacidades de herramientas (tools) impulsado por IA:
- **Paso 1 (SDK Usuario)**: Conexión mediante Access Token de usuario (`webex_test.py`).
- **Paso 2 (SDK Bot)**: Envío de mensajes directos y servidor de recepción mediante polling interactivo (`bot_test.py`, `bot_server.py`).
- **Paso 3 (Agente ADK)**: Integración del bot con un agente de Google ADK que ejecuta herramientas determinísticas (`adk_integration.py`).

## 🛠️ Estructura del Repositorio

```text
webex_python/
├── .env.example          # Plantilla de variables de entorno y tokens
├── .gitignore            # Exclusión de archivos sensibles y entornos virtuales
├── README.md             # Guía técnica integral del proyecto
├── requirements.txt      # Dependencias (webexteamssdk, google-genai, python-dotenv)
├── webex_test.py         # Paso 1: Pruebas con token de usuario
├── bot_test.py           # Paso 2A: Envío de mensajes directos con bot token
├── bot_server.py         # Paso 2B: Servidor interactivo de bot mediante polling
└── adk_integration.py    # Paso 3: Orquestación del bot con agente Google ADK y herramientas
```

## ⚙️ Requisitos e Instalación

### Prerrequisitos
- **Python 3.10+** instalado.
- **Cuenta de Cisco Webex** para pruebas de usuario.
- **Bot de Webex creado** en [Webex for Developers](https://developer.webex.com/my-apps) para obtener el Bot Token.
- **Google AI Studio API Key** para los modelos Gemini.

### Instalación

1. Clonar el repositorio y navegar a la carpeta:
   ```bash
   git clone https://github.com/fnrivarola95/webex_python.git
   cd webex_python
   ```

2. Crear y activar el entorno virtual:
   ```powershell
   python -m venv venv
   .env\Scripts\Activate
   ```

3. Instalar las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno en `.env`:
   ```powershell
   copy .env.example .env
   ```
   Completar los siguientes valores:
   ```ini
   GOOGLE_API_KEY=AIzaSy...
   WEBEX_BOT_TOKEN=M2QzN...
   WEBEX_ACCESS_TOKEN=tu_user_token_personal_opcional
   ```

## 🧪 Procedimientos de Pruebas

Para validar el ciclo completo de integración, ejecutar los scripts en secuencia:

### Prueba 1: Conectividad con Token de Usuario
Valida la creación y lectura de salas de Webex:
```powershell
python webex_test.py
```

### Prueba 2: Envío de Mensaje Directo (Bot)
Envía un mensaje 1:1 a un correo corporativo específico para validar que el bot tiene permisos de mensajería:
```powershell
python bot_test.py
```

### Prueba 3: Servidor de Polling Interactivo
Inicia el bot en modo escucha por long-polling. Responde automáticamente en cualquier espacio o mensaje directo donde se mencione al bot:
```powershell
python bot_server.py
```

### Prueba 4: Flujo Completo con Agente Google ADK
Ejecuta la orquestación donde el mensaje del usuario es interpretado por el modelo Gemini, dispara una herramienta (`get_server_status`), y formula la respuesta contextual:
```powershell
python adk_integration.py
```

## 🚧 Pendientes de Desarrollo y Cómo Llevarlos a Cabo

1. **Migración de Polling a Webhooks (FastAPI + Asincronismo)**:
   - *Objetivo*: Reemplazar el bucle de long-polling de `bot_server.py` por un endpoint HTTPS reactivo (`POST /webex/webhook`), reduciendo la latencia de respuesta y el consumo de CPU.
   - *Procedimiento*:
     - Implementar un servidor FastAPI ligero (`src/webhook_server.py`).
     - Registrar el webhook en Webex API (`POST https://webexapis.com/v1/webhooks`) apuntando al dominio público (vía ngrok en desarrollo o Cloud Run en producción).
     - Validar la firma criptográfica del header `X-Spark-Signature` para autenticar las llamadas de Cisco.

2. **Memoria Conversacional y Gestión de Sesiones Multi-Usuario**:
   - *Objetivo*: Permitir conversaciones hiladas multi-turno donde el bot recuerde el contexto previo de cada usuario.
   - *Procedimiento*:
     - Almacenar el estado conversacional en memoria indexado por `personEmail` o `roomId` (usando `InMemorySessionService` o SQLite local para persistencia).
     - Pasar el `session_id` al Runner de Google ADK en cada turno.

3. **Tarjetas Interactivas (Adaptive Cards)**:
   - *Objetivo*: Responder con tarjetas visuales enriquecidas con botones, listas desplegables y formularios interactivos en lugar de texto plano o markdown simple.
   - *Procedimiento*:
     - Diseñar el payload JSON de la tarjeta con el diseñador de [Adaptive Cards para Webex](https://adaptivecards.io/designer/).
     - Enviar la tarjeta usando `webex.messages.create(roomId=..., text="...", attachments=[...])`.
     - Manejar el evento `attachmentActions` en el webhook para procesar las respuestas de los botones.

4. **Contenerización y Despliegue en Cloud Run / Docker**:
   - *Objetivo*: Disponer del bot como un microservicio cloud de alta disponibilidad disponible 24/7.
   - *Procedimiento*:
     - Crear un `Dockerfile` multi-stage ligero basado en `python:3.11-slim`.
     - Inyectar los tokens mediante Secret Manager.
     - Desplegar en Google Cloud Run configurando el webhook público permanente.
