# Esqueleto Webex Bot + ADK (Python)

Este esqueleto permite conectar un bot de Webex con un agente de Google ADK de forma reproducible. Se instala en paralelo al código existente: no rompe el flujo actual (`bot_server.py`) y puede usarse como plantilla para otros equipos.

## Componentes
- `run_bot.py`: Punto de entrada mínimo del bot.
- `adk_agent/config.py`: Carga de configuración (.env) y creación de `Settings`.
- `adk_agent/sessions.py`: Servicio de sesiones (persistente en disco por defecto) y fábrica para instanciarlo.
- `adk_agent/tools.py`: Herramientas listas (Stack Overflow por RSS, Infobae).
- `adk_agent/agent.py`: Crea el agente ADK y expone `run_agent_message` para obtener respuestas.
- `adk_agent/webex_bot.py`: Lógica de Webex (polling, filtrado de historial, llamada al agente).
- `adk_agent/__init__.py`: Inicializa el paquete.
- `session_store.json`: Persistencia mínima de sesiones para que sobrevivan reinicios.

## Requisitos previos
1) Instalar dependencias: `pip install -r requirements.txt`
2) Configurar `.env` (copiar de `.env.template` si lo generas):  
   - `WEBEX_BOT_TOKEN` (bot)  
   - `WEBEX_ACCESS_TOKEN` (opcional, usuario)  
   - `GOOGLE_API_KEY` (ADK)  

## Uso rápido
```powershell
.\pywebex\Scripts\python.exe run_bot.py
```
- El bot responde solo a mensajes nuevos (no procesa historial).
- Cada usuario en cada sala tiene `session_id = f"{room.id}:{personId}"`.
- Las sesiones se guardan en `session_store.json` junto a `run_bot.py` (persistencia mínima).

## Flujo interno
1) `run_bot.py` carga `.env`, crea `Settings` y lanza `run_webex_bot`.
2) `webex_bot.py`:
   - Autentica Webex.
   - Marca mensajes previos como procesados (no responde historial).
   - Polling: para cada mensaje nuevo, arma `user_id`/`session_id` y llama a `run_agent_message`.
3) `agent.py`:
   - Crea el agente ADK con tools de `tools.py`.
   - Garantiza sesión (persistente) y ejecuta `Runner.run_async`.
   - Extrae texto de los eventos y lo devuelve a Webex.

## Herramientas incluidas
- `stackoverflow_search_rss(query)`: busca en RSS de Stack Overflow (hasta 3 resultados). Si falla, devuelve enlaces de fallback a tags populares.
- `infobae_headlines(topic=None, limit=5)`: titulares recientes desde Infobae (varios feeds probados).

## Cómo adaptar para otros proyectos
- Agrega tus propias tools en `adk_agent/tools.py` (funciones Python) y súmalas en `build_tools()` en `agent.py`.
- Cambia el backend de sesiones implementando otra clase con la misma interfaz de `PersistentInMemorySessionService` y registrándola en `make_session_service`.
- Ajusta la estrategia de IDs de sesión en `webex_bot.py` si necesitas un hilo de conversación diferente (p. ej., por sala en vez de usuario+sala).

