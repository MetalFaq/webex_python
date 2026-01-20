# Problemas de multi-tools con google_search en convivencia con tools desarrolladas con Python
Ese error es esperado: el GoogleSearchTool de ADK está pensado como “built‑in” y choca con el modo de llamadas de función (AFC) cuando convive con otras tools propias. Para Gemini 1.x directamente no admite más de una tool; para Gemini 2.x, la advertencia “Tool use with function calling is unsupported” aparece si mezclas esa tool declarativa (no callable) con tus propias funciones.

## Workarounds prácticos:

Usar solo GoogleSearchTool (sin otras tools) en el agente.
O bien quitarla y quedarte con tus tools Python (como hicimos con Stack Overflow). Si necesitas Google Search, implementarla como una tool propia (HTTP) o usar otro canal de búsqueda (Vertex AI Search, etc.) en lugar del built‑in.
Si quieres insistir, podrías probar GoogleSearchTool(bypass_multi_tools_limit=True) pero en la práctica suele seguir fallando con AFC cuando hay otras tools.
En resumen: el built‑in de Google Search no se lleva bien con tools adicionales bajo AFC; lo más estable es mantener solo tus tools propias o usar exclusivamente esa tool en un agente dedicado.

# Despliegue en producción del bot: manejo de sesiones en memoria vs backend persistente
Hoy el bot usa una sola sesión fija (USER_ID, SESSION_ID) con InMemorySessionService, así que todo se mezcla. Para producción, cambia a un esquema per-user/per-room y un backend persistente:

## Identidades:
user_id: usa msg.personId (el ID del usuario en Webex).
session_id: para DMs usa msg.roomId; para grupos puedes usar roomId o f"{roomId}:{msg.personId}" si quieres hilos por usuario dentro del grupo.

## Session service:
InMemory solo sirve en dev; se pierde en cada reinicio y no escala.
Usa un backend persistente (ej. Firestore/Redis/Spanner) o un VertexAiSessionService si la lib lo ofrece, o implementa un BaseSessionService propio contra tu datastore.

## Código a ajustar:
En get_agent_response, pasa user_id/session_id calculados desde el mensaje (no constantes globales). Si mantienes la interfaz sync, cambia la firma para aceptar esos valores.
En ensure_session_async, usa esos IDs; crea la sesión si no existe en el backend.
En bot_server.py, al llegar un mensaje arma user_id y session_id y llámalos al agent; no uses un loop/loop nuevo por llamada si vas a alta concurrencia (mejor un único event loop o un hilo dedicado).

## Estado y durabilidad:
Define TTL o políticas de expiración de sesiones.
Si quieres continuidad tras un deploy, el backend de sesiones debe ser compartido.

## Resiliencia:
Maneja timeouts/reintentos a ADK, rate limits de Webex.
Registra errores sin volcar metadata sensible; rota tokens y carga desde .env/secrets manager.

## Comportamiento:
Filtro de historial: mantener la lógica de ignorar mensajes previos al arranque.
Responde solo a mensajes de texto y omite los del propio bot.
Con esos cambios, cada usuario/room mantiene su propio hilo de conversación y las sesiones sobreviven reinicios.

# Principales impactos al pasar a sesiones por usuario/room y hacerlas persistentes

## Memoria y CPU del bot
Con InMemorySessionService cada sesión queda en RAM; a más usuarios, más memoria. Si además creas un event loop por mensaje, sube CPU. Solución: un solo loop async y backend persistente.

## Almacenamiento: 
si persistes sesiones (Firestore/Redis/SQL), crece el uso de disco/ram en el backend conforme crece el número de sesiones y su estado; define qué guardas (historial breve, estado mínimo) y aplica TTL/expiración.

## Latencia y RPS: 
cada mensaje implica I/O a Webex + ADK + backend de sesiones; más usuarios ⇒ más llamadas simultáneas. Usa conexiones persistentes/pooling y timeouts razonables; evita bloquear en operaciones sync.

## Escalabilidad/concurrencia:
con un backend compartido, varias réplicas del bot pueden atender en paralelo; sin backend (solo memoria) pierdes estado al reiniciar y no puedes escalar horizontalmente.

## Limpieza: 
define políticas de expiración de sesiones (por inactividad) para evitar crecimiento indefinido de memoria/almacenamiento y mantener el costo bajo.

## Costos de tokens: 
más sesiones y más mensajes ⇒ más tokens procesados por el modelo; vigila cuotas de ADK y rate limits de Webex.

En resumen: el impacto principal es más memoria/almacenamiento y más I/O por mensaje. Mitígalo con backend de sesiones, TTL, loop async único, pooling y límites de historial.