# Bot Webex + ADK: Guía de Uso y Arquitectura

## Qué hace cada archivo
- `bot_server.py`: Bot de Webex con polling. Lee `.env`, escucha mensajes nuevos, arma `user_id`/`session_id` por usuario y sala, llama al agente para responder y envía la respuesta a Webex.
- `adk_integration.py`: Lógica del agente (Google ADK). Carga `.env`, crea el agente con tools (Stack Overflow RSS + Infobae), gestiona sesiones con persistencia mínima (`session_store.json`) y llama a `Runner.run_async` para generar respuestas.
- `.env`: Claves/tokens (WEBEX_BOT_TOKEN, WEBEX_ACCESS_TOKEN, GOOGLE_API_KEY). Ignorado por git.
- `session_store.json`: Persiste sesiones (app_name, user_id, session_id, state) para no perder contexto mínimo entre reinicios.
- `webex_test.py` / `bot_test.py`: Scripts de prueba rápidos del SDK de Webex (usuario/bot).
- `README.md`: Resumen del proyecto y scripts principales.
- `requirements.txt`: Dependencias.
- `git_commands_guide.md.resolved`: Chuleta de comandos git.
- `bot.md`: Tus notas/guía original (no tocada).

## Comunicación `bot_server.py` <-> `adk_integration.py`
1. `bot_server.py` arranca, carga `.env`, inicia polling y marca mensajes previos como procesados (no responde historial).
2. Para cada mensaje nuevo:
   - `user_id = msg.personId`
   - `session_id = f\"{room.id}:{msg.personId}\"` (una sesión por usuario en cada sala)
   - Llama `get_agent_response(text, user_id, session_id)` de `adk_integration.py`.
3. `adk_integration.py`:
   - Asegura inicialización (agente + servicio de sesión persistente).
   - Crea/recupera sesión (persistida en `session_store.json`).
   - Ejecuta `Runner.run_async` y extrae texto de los eventos (text/parts/content).
4. `bot_server.py` envía la respuesta a Webex con `api.messages.create(...)`.

## Tools del agente
- `stackoverflow_search`: Consulta feed RSS de Stack Overflow (hasta 3 resultados). Si falla, devuelve enlaces de fallback a tags populares.
- `infobae_headlines`: Titulares recientes de Infobae (prueba varias URLs; si todas fallan, error controlado).

## Cómo correr el bot
1) Asegura `.env` con `WEBEX_BOT_TOKEN`, `WEBEX_ACCESS_TOKEN` (opcional para enviar a rooms), `GOOGLE_API_KEY`.
2) Usar el venv:
```powershell
.\pywebex\Scripts\python.exe bot_server.py
```
3) En Webex, envía un mensaje al bot; responde solo a mensajes nuevos.

## Persistencia de sesiones
- Servicio: `PersistentInMemorySessionService`.
- Ubicación: `session_store.json` junto a `adk_integration.py` (se crea al iniciar sesiones).
- Contenido: `app_name`, `user_id`, `session_id`, `state` (si existiera).
- Uso: rehace las sesiones al reinicio para mantener el mínimo estado del agente.

## Notas operativas
- Stack Overflow: puede fallar por bloqueos/SSL; si ocurre, el bot devuelve enlaces de fallback.
- Infobae: intenta varias URLs de RSS; si todas fallan, responde error controlado.
- El bot no responde a historial: primera pasada marca los mensajes existentes y luego solo responde a nuevos.
