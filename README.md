# EduBot Adaptativo – Tutor Inteligente para E-learning en Español

EduBot Adaptativo es un proyecto académico de un tutor inteligente diseñado para plataformas de educación en línea, que se adapta al nivel de cada estudiante. Su propósito es brindar una experiencia de aprendizaje personalizada, generando explicaciones claras, ejercicios prácticos adaptativos y retroalimentación inmediata en español, utilizando tecnologías modernas de Inteligencia Artificial (LLM).

## Objetivo y Motivación del Proyecto

El objetivo pedagógico de EduBot Adaptativo es asistir al estudiante en su proceso de aprendizaje, similar a contar con un tutor humano:

- Explicando conceptos de forma clara y personalizada, adaptando el lenguaje y la profundidad al nivel del estudiante.
- Generando ejercicios de práctica ajustados al nivel de habilidad del estudiante, para reforzar el aprendizaje de diferentes materias (Matemáticas, Programación, Inglés).
- Evaluando las respuestas de los estudiantes y proporcionando retroalimentación inmediata que explique aciertos y errores, ayudando al estudiante a mejorar.

El proyecto toma como referencia casos de uso reales como cursos en plataformas e-learning (ej. Platzi, Coursera en español) y entornos de aprendizaje virtual en Latinoamérica. La idea es demostrar cómo la IA, y en concreto los Large Language Models (LLMs), pueden hacer la educación a distancia más interactiva y personalizada.

## Arquitectura del Sistema

EduBot Adaptativo se construyó siguiendo una arquitectura simple y modular:

- **API REST con FastAPI:** es la base de interacción del tutor. Define tres endpoints principales (/tutor/explain, /tutor/exercise, /tutor/evaluate) para las funcionalidades de explicación, generación de ejercicios y evaluación respectivamente. Se usan modelos de datos Pydantic para la validación de la entrada/salida de cada endpoint.
- **Modelo de Lenguaje (LLM) Local vía Ollama:** el motor de IA que genera explicaciones y ejercicios es un modelo de lenguaje grande (LLM) ejecutándose localmente a través de la herramienta Ollama. Esto permite procesar solicitudes en español utilizando un modelo de ~3B parámetros sin depender de servicios externos de Internet, manteniendo privacidad, reducción de costos y control sobre los datos.
- **Adaptación del nivel de dificultad:** el sistema mantiene un modelo simple del estudiante en memoria (almacenado temporalmente en variables Python, que podrían fácilmente persistirse en una base de datos o un almacén como Redis). Este modelo almacena los ejercicios presentados y las estadísticas de aciertos del estudiante. Basándose en el desempeño (respuestas correctas/incorrectas), el tutor ajusta el nivel de dificultad de futuros ejercicios: subiendo el nivel tras varios aciertos consecutivos o presentando ejercicios de repaso tras errores.

### Resumen del flujo interno:

1. FastAPI recibe la solicitud del usuario en un endpoint (/explain, /exercise o /evaluate).
2. Prepara un prompt adecuado en español para el modelo de lenguaje, incluyendo contexto del estudiante (materia, nivel, rendimiento previo).
3. Se envía el prompt al servidor Ollama local (por defecto en http://localhost:11434) para generar la respuesta con el modelo LLM cargado.
4. FastAPI procesa la respuesta del LLM, la formatea según el contrato definido (por ejemplo, extrayendo texto o separando pregunta y opciones de un JSON generado) y la envía de vuelta al cliente en formato JSON.

## Flujo de Funcionalidad
El tutor inteligente está pensado para ser utilizado en ciclos de aprendizaje que integran los tres endpoints en secuencia:

1. **Explicación de un concepto (POST /tutor/explain):** El estudiante solicita al tutor que explique un tema específico en determinada materia. El tutor responde con una explicación adaptada al nivel del alumno, utilizando ejemplos claros y lenguaje sencillo. (Ejemplo: el estudiante pide una explicación de "derivadas" en Matemáticas).
2. **Ejercicio adaptativo (POST /tutor/exercise):** Basado en la materia (y eventualmente el desempeño previo del estudiante), el tutor genera un ejercicio práctico. Si el estudiante especifica un nivel (básico, intermedio, avanzado), se produce el ejercicio en esa dificultad; en caso contrario, se usa un nivel por defecto (inicialmente intermedio, modulable según las futuras respuestas del estudiante). El tutor devuelve el enunciado de la pregunta (y opciones si es de selección múltiple), sin revelar la respuesta correcta. (Ejemplo: en Programación, se puede generar un ejercicio pidiendo escribir un fragmento de código de acuerdo a un concepto dado).
3. **Evaluación y retroalimentación (POST /tutor/evaluate):** El estudiante envía su respuesta al ejercicio indicando el question_id asociado. El tutor compara la respuesta del estudiante con la solución guardada y devuelve un veredicto (correcto o incorrecto). Además, proporciona una retroalimentación inmediata: si la respuesta fue correcta, felicita y refuerza; si fue incorrecta, brinda una breve explicación o consejo, frecuentemente generado por el LLM, para guiar al estudiante hacia la respuesta correcta. El sistema actualiza las métricas de progreso (cantidad de aciertos totales y porcentaje de precisión) y ajusta internamente el nivel de dificultad para próximos ejercicios (incrementándolo tras varios aciertos consecutivos, por ejemplo, o reduciéndolo si hay errores seguidos). Esto ejemplifica la adaptabilidad del tutor. (Ejemplo: si el estudiante se equivoca en un ejercicio de nivel intermedio, el siguiente ejercicio podría mantenerse en nivel intermedio o incluso descender a básico, reforzando conceptos base).

## Tecnologías Utilizadas y LLM Local (Ollama)
### Tecnologías principales:
- Lenguaje de programación Python 3.
- Framework FastAPI para exponer las funcionalidades mediante una API REST, aprovechando su rapidez y la integración nativa con Pydantic para validación de datos.
- Pydantic para definir los formatos JSON de entrada/salida (schemas) de cada endpoint, facilitando la validación y autogeneración de documentación interactiva (Swagger UI).
- Ollama: plataforma para ejecutar Modelos de Lenguaje Localmente. Permite cargar modelos avanzados (como Llama 2, Mistral, etc.) sin conexiones externas, manteniendo los datos de los estudiantes privados y dentro del entorno local.
- Modelo LLM configurado por defecto: en este MVP se utilizó un modelo de ~3B parámetros con soporte robusto para español (etiquetado como "llama3.2:3b" en Ollama). Este modelo, similar en capacidades a una variante de Llama de tamaño medio, es suficiente para generar explicaciones y ejercicios básicos en español.

### Por qué un LLM local (Ollama):

- **Privacidad y control:** Al ejecutar de forma local, los datos de estudiantes (sus respuestas, preguntas) no se transmiten a terceros, protegiendo la privacidad.
- **Independencia de conexión: **El sistema funciona offline sin depender de servicios en la nube. Esto es ideal en entornos educativos que requieren alta disponibilidad o control de datos (p. ej., universidades con políticas de datos estrictas).
- **Adiestramiento en español:** Los modelos disponibles en Ollama (como Llama 2) han sido entrenados en múltiples idiomas, incluyendo español. Esto permite que el tutor se comunique fluidamente en español, integrando la jerga y contextos latinoamericanos cuando corresponde.
- **Flexibilidad y extensibilidad:** Ollama facilita probar distintos modelos LLM (se han considerado Llama 2 7B o Mistral 7B) e incluso permite ajustar prompts y parámetros localmente sin costos adicionales, lo que es adecuado para entornos académicos y experimentales.

## Endpoints y Ejemplos de Uso
El sistema expone tres endpoints principales. A continuación se describen brevemente, junto con ejemplos de llamadas (usando curl para demostración) y sus respuestas:

1. **/tutor/explain – Explicación de un concepto:**
**Descripción:** Recibe un JSON con un subject (materia, p.ej. "matematicas", "programacion", "ingles") y un topic (tema específico). Retorna un JSON con una explicación en español adaptada al nivel del estudiante. Útil para introducir o reforzar un concepto teórico antes de practicar.

**Ejemplo:**

curl -X POST "http://127.0.0.1:8000/tutor/explain" -H "Content-Type: application/json" \
     -d '{"subject": "matematicas", "topic": "derivadas"}'

**Respuesta (JSON):**

{
  "explanation": "Una derivada representa la razón de cambio instantánea de una función..."
}

*(El campo "explanation" contiene uno o dos párrafos en español explicando el tema de manera sencilla, adaptada al conocimiento del estudiante.)*

- **2. /tutor/exercise – Generación de un ejercicio adaptativo:**
Descripción: Recibe un JSON con subject (materia) y un campo opcional level (nivel de dificultad: "basico", "intermedio", "avanzado"). Devuelve un JSON con un nuevo ejercicio: un question_id (identificador único), la pregunta (enunciado) y opcionalmente una lista de options (si es de opción múltiple). La respuesta correcta del ejercicio se almacena internamente para evaluación posterior, pero no se envía al usuario. Si level no se especifica, el tutor elige un nivel por defecto (inicialmente intermedio) o adaptado según el desempeño previo.
**Ejemplo:**
curl -X POST "http://127.0.0.1:8000/tutor/exercise" -H "Content-Type: application/json" \
     -d '{"subject": "programacion", "level": "basico"}'

**Respuesta (JSON):**

{
  "question_id": 2,
  "subject": "programacion",
  "level": "basico",
  "question": "Escribe un programa que imprima los números pares del 1 al 10 en Python.",
  "options": null
}

*(En este ejemplo, se generó un ejercicio básico de programación sin opciones, asumiendo que la respuesta esperada es un fragmento de código. Si fuera una pregunta de opción múltiple, el campo "options" contendría una lista de opciones y la respuesta seguiría almacenada internamente hasta la evaluación.)*

- **3. /tutor/evaluate – Evaluación de la respuesta del estudiante:**
**Descripción:** Recibe un JSON con question_id (ID del ejercicio a evaluar) y la answer proporcionada por el estudiante. Compara la respuesta con la correcta, devuelve si es correcta (true/false), un feedback (breve explicación en español) y un indicador de progress (porcentaje de aciertos acumulados en la sesión). Tras evaluar, el tutor descarta el ejercicio de la memoria para que no se reevalúe múltiples veces el mismo.
**Ejemplo (respuesta correcta):**

curl -X POST "http://127.0.0.1:8000/tutor/evaluate" -H "Content-Type: application/json" \
     -d '{"question_id": 2, "answer": "for num in range(2, 11, 2): print(num)"}'

**Respuesta:**

{
  "correct": true,
  "feedback": "¡Respuesta correcta! Muy bien, sigue así.",
  "progress": "1 de 1 correctas (100%)"
}

**Ejemplo (respuesta incorrecta):**

curl -X POST "http://127.0.0.1:8000/tutor/evaluate" -H "Content-Type: application/json" \
     -d '{"question_id": 2, "answer": "print(*range(2, 11, 2))"}'

**Respuesta:**
{
  "correct": false,
  "feedback": "La respuesta proporcionada no es la esperada. Recuerda que debes usar un bucle for para recorrer del 1 al 10 e imprimir los números pares. ¡Tú puedes corregirlo!",
  "progress": "1 de 2 correctas (50%)"
}
*(Aquí la respuesta del estudiante fue incorrecta y el tutor, además de marcarla como tal, ofreció una breve pista: sugiere al estudiante que recuerde utilizar un bucle for para resolver el ejercicio.)*

**Requisitos Previos:**
- Python 3.9+ instalado.
- Modelo LLM local disponible a través de Ollama. (Para replicar, se recomienda usar https://ai.meta.com/llama/ u otro modelo en español como Mistral mediante Ollama).
- Instalar dependencias Python especificadas en requirements.txt (FastAPI, Uvicorn, requests/httpx, pydantic, etc.).
pip install -r requirements.txt

**Ejecución del servidor:**

**1. Iniciar Ollama** con el modelo elegido (asegúrate de tenerlo descargado en Ollama). Por defecto, el sistema buscará un modelo llamado "llama3.2:3b", pero puedes cambiarlo en app/llm_client.py o cargar un modelo alternativo configurando la variable de entorno OLLAMA_MODEL.
**2. Iniciar la API FastAPI:** ejecutar en terminal desde la raíz del proyecto:
uvicorn app.main:app --reload
Con --reload, el servidor recargará automáticamente los cambios en el código en entorno de desarrollo. Por defecto, la API estará disponible en <http://127.0.0.1:8000>
**3. Explorar la API:**Una vez en ejecución, puedes abrir <http://127.0.0.1:8000/docs> para acceder a la interfaz interactiva (Swagger UI) y probar los endpoints con ejemplos.

*(Nota: En el MVP se utiliza almacenamiento en memoria y variables globales para simplicidad; en producción se recomienda usar una solución persistente como Redis u otra base de datos para manejar el estado de las sesiones entre múltiples instancias del servidor.)*

# Conclusión
**EduBot Adaptativo** demuestra un caso de uso de tutoría inteligente: integrando **IA generativa local** con una API educativa se logra una experiencia personalizada y adaptable para el estudiante. En el contexto académico, este proyecto cumple con los criterios establecidos:

**- Calidad pedagógica:** Explicaciones claras en español y feedback inmediato tras cada respuesta, fomentando la comprensión del estudiante.
**- Adaptabilidad:** Ajusta la dificultad de ejercicios según las respuestas del alumno, manteniendo métricas de progreso (aciertos y porcentaje de éxito).
**- Funcionalidad técnica:** El MVP es completamente funcional con una API RESTful (FastAPI) y un LLM local (Ollama), demostrando la integración de tecnologías modernas en un entorno educativo.
**- Presentación:** El código está estructurado con buenas prácticas (FastAPI + Pydantic) y el proyecto incluye documentación (este README) con instrucciones y ejemplos de uso.