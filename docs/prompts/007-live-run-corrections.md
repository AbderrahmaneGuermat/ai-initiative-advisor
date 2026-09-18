# Prompt 007 — Recording the First Live Run and Correcting What It Found

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** the project owner asked for explanations in Spanish. The interface, the runtime
  prompts and all project documentation remain in English.

The text below is the instruction exactly as received.

---

Sí, realiza la siguiente iteración. Sigue explicándome el trabajo en español y conserva el inglés en la interfaz, los prompts de ejecución y la documentación del proyecto.

Guarda esta instrucción completa en el siguiente archivo numerado disponible de docs/prompts/, sin modificar los registros anteriores.

1. Registra la primera prueba real.

Documenta el modelo, la configuración, el escenario y los resultados observados. Separa claramente esta ejecución de las pruebas con dobles deterministas.

Aclara el denominador del "40% de rechazos" y distingue peticiones, salidas rechazadas, reparaciones y cancelaciones. Presenta el coste como una estimación basada en el uso disponible; una petición cancelada sin datos de uso no equivale a coste cero.

2. Corrige el timeout y la continuidad.

El mensaje debe indicar qué pasos terminaron y quedaron guardados, y cuál fue interrumpido. Conserva los resultados previamente validados; descarta únicamente la salida incompleta o inválida.

Comprueba que "Continue" puede continuar desde una comparación guardada sin repetirla innecesariamente.

Permite configurar un límite de turno de 300 segundos como margen operativo. No presentes ese aumento como una mejora de rendimiento.

3. Resuelve las referencias a preguntas omitidas.

Mantén la prohibición de citar preguntas skipped o unanswered como clarification.answer.

Ajusta los prompts con ejemplos breves: una respuesta contestada puede respaldar una afirmación; una pregunta omitida debe describirse como información pendiente en missing_evidence u open_unknowns.

Facilita al modelo una lista explícita de las respuestas que sí puede citar, separada del estado de todas las preguntas. No añadas respuestas inventadas ni conviertas desconocidos en valoraciones negativas.

4. Mejora las decisiones del asesor.

El diagnóstico debe ser opcional y, si se elige, ejecutarse antes de la comparación para ese contexto. No impongas una secuencia fija obligatoria.

El selector debe recibir un resumen útil de los hallazgos previos y de las acciones completadas, no únicamente indicadores de que existen.

Por defecto, utiliza una ronda de hasta tres preguntas. Después de que el usuario la envíe, continúa con los datos disponibles y los desconocidos explícitos; no abras automáticamente otra ronda.

5. Reduce y mide las esperas.

Registra, cuando la API los proporcione, tokens de razonamiento y tokens de entrada en caché. No sumes el razonamiento dos veces: ya forma parte de los tokens de salida.

Revisa la configuración de razonamiento compatible con gpt-5-mini y evalúa un esfuerzo menor, manteniendo el mismo modelo. Pide respuestas concisas sin eliminar justificaciones, fuentes ni incertidumbres necesarias.

6. Verifica y publica.

Añade pruebas focalizadas sobre conservación de resultados tras un timeout, continuidad, orden del diagnóstico y tratamiento de preguntas omitidas.

Realiza una única prueba completa de seguimiento con el mismo escenario y respuestas comparables. Informa de duración, peticiones, reparaciones y uso observado, y compáralos con la ejecución anterior. Si algo falla, registra el resultado antes de iniciar nuevas pruebas con coste.

Actualiza el worklog, haz commit y publica en el mismo repositorio y rama ya verificados. No incorpores funciones adicionales en esta iteración.

Termina indicando qué quedó comprobado, qué sigue pendiente y cómo puedo revisar el flujo en el navegador. No des por validada la interfaz si no la has utilizado.
