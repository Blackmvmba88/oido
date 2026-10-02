# Oído

**Oído** es un sistema modular de escucha continua para capturar voz y canto, conservar audio crudo, transcribir en vivo e interpretar el contexto sin destruir el registro original.

## Principio central

Oído no genera sólo una transcripción. Genera un **cuaderno inteligente**:

- conserva exactamente lo dicho;
- muestra texto en vivo;
- marca ideas, decisiones, preguntas, README, roadmap, tareas y bugs;
- detecta versos, rimas, repeticiones y posibles hooks;
- conserva marcas de tiempo para regresar al audio original;
- separa la captura, transcripción e interpretación para que una falla no destruya las demás capas.

## Arquitectura redundante

```text
MIC / LINE / LOOPBACK
        |
        v
+---------------------+
| 1. CAPTURE          |
| audio crudo continuo|
+----------+----------+
           |
     +-----+------------------+
     |                        |
     v                        v
+------------+          +-------------+
| Recorder   |          | Live buffer |
| WAV/FLAC   |          | ring buffer |
+------------+          +------+------+ 
                           |
                           v
                    +-------------+
                    | 2. LISTENER |
                    | VAD + STT   |
                    +------+------+ 
                           |
                           v
                    +-------------+
                    | 3. WRITER   |
                    | texto limpio|
                    +------+------+ 
                           |
                           v
                    +------------------+
                    | 4. CONTEXT ENGINE|
                    +--------+---------+
                             |
       +----------+----------+----------+-----------+
       |          |          |          |           |
      IDEA      README    ROADMAP      LYRIC       NOTE
                                          |
                                   rhyme / hook /
                                   meter / repeat
                             |
                             v
                    +------------------+
                    | 5. NOTEBOOK UI   |
                    | marcas + colores |
                    | subrayados       |
                    | timeline         |
                    +------------------+
```

## El cuaderno

Cada fragmento conserva dos capas:

1. **Texto original:** nunca se reescribe ni se pierde.
2. **Anotaciones:** interpretaciones que pueden cambiar sin tocar el original.

Ejemplo:

```text
20:51:08  “La noche mastica despacio mi nombre...”

        ╰─ ✦ POSIBLE VERSO
           ↳ rima asonante detectada
           ↳ imagen fuerte
           ↳ posible apertura de canción

20:51:14  “y estaría bueno que el programa separara esto...”

        ╰─ 💡 IDEA
           ↳ proyecto: Oído
           ↳ componente: Context Engine
```

## Tipos iniciales

- 💡 Idea
- 🧭 Roadmap
- 📘 README / documentación
- ✅ Tarea
- 🐛 Bug
- ⚙️ Feature
- ❓ Pregunta
- 🔒 Decisión
- 🎵 Letra / verso
- 🔁 Rima / repetición
- 🎯 Hook potencial
- 🎤 Canto
- 🗣️ Voz hablada
- 📝 Nota

## Redundancia

La captura de audio es independiente de la transcripción.

Si el STT falla, **el audio sigue existiendo** y el segmento puede reprocesarse posteriormente con otro motor.

Cada segmento tendrá:

```json
{
  "id": "segment-id",
  "start_ms": 0,
  "end_ms": 4180,
  "audio_path": "...",
  "raw_text": "...",
  "clean_text": "...",
  "mode": "speech|singing|unknown",
  "annotations": [],
  "stt_engine": "...",
  "confidence": 0.0
}
```

## Módulos previstos

```text
oido/
├── capture/
├── listener/
├── writer/
├── context/
├── notebook/
├── storage/
├── audio/
└── tests/
```

## Objetivo del MVP

1. Escuchar continuamente.
2. Guardar audio por segmentos.
3. Mostrar transcripción en tiempo real.
4. Mantener una línea de tiempo completa.
5. Detectar voz hablada vs canto cuando sea posible.
6. Clasificar contexto.
7. Decorar el texto con anotaciones sin modificar el original.
8. Poder pulsar cualquier nota y reproducir el audio exacto que la originó.

---

**BlackMamba RECORDS / Iyari Gomez**
