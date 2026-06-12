# app/main.py
import httpx
from fastapi import FastAPI
from app.schemas import ExplainRequest, ExplainResponse, ExerciseRequest, ExerciseResponse, EvaluateRequest, EvaluateResponse
from app.llm_client import generar_respuesta
from app.llm_client import OLLAMA_URL, DEFAULT_MODEL
import json                # Para usar json.loads
import logging             # Para usar logging.error (u otras funciones de logging)
from fastapi import HTTPException  # Para usar HTTPException

logging.basicConfig(level=logging.INFO)

exercise_counter = 1  # Contador global para asignar ID a cada ejercicio generado
exercise_storage = {}  # Diccionario para almacenar respuestas correctas: {question_id: answer}

evaluation_count = 0  # Contador global de intentos de evaluación realizados
correct_count = 0     # Contador global de respuestas correctas del estudiante



# Inicializar la aplicación FastAPI con metadatos opcionales
app = FastAPI(
    title="EduBot Adaptativo",
    description="MVP - Tutor Inteligente Adaptativo para e-learning (LATAM)",
    version="0.1.0"
)

# Ruta raíz opcional para verificación de estado del servicio
@app.get("/")
def root():
    return {"message": "EduBot API is running"}

# --- Endpoint: /tutor/explain --- #
@app.post("/tutor/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest):
      # Crear prompt en español con la materia y el tema a explicar
      prompt = (
          f"Eres un tutor experto en {request.subject} y hablas español. "
          f"Explica de manera clara y concisa el concepto de '{request.topic}' "
          f"como si fuera para un estudiante de Latinoamérica, con un ejemplo práctico."
      )
      # Llamar al modelo de lenguaje a través de Ollama para obtener la explicación
      texto_explicacion = await generar_respuesta(prompt)
      # Retornar la explicación en el formato definido por ExplainResponse
      return {"explanation": texto_explicacion}


# --- Endpoint: /tutor/exercise --- #
@app.post("/tutor/exercise", response_model=ExerciseResponse)
async def generate_exercise(request: ExerciseRequest):
    level = request.level.value if request.level else "intermedio"
    subject = request.subject
    
    # Construir prompt para el LLM
    prompt = (
        f"Eres un tutor experto en {subject} y hablas español. "
        f"Genera un ejercicio de nivel {level} en la materia de {subject}. "
        f"Responde solo con un JSON que tenga 'question', 'options' (si es una pregunta de opción múltiple) y 'answer'"
        f"No incluyas saludos ni explicaciones adicionales."
    )
    respuesta_llm = await generar_respuesta(prompt)
    
    # Analizar la respuesta del LLM, esperando un JSON válido
    try:
        data = json.loads(respuesta_llm)
    except json.JSONDecodeError:
        logging.error(f"Respuesta LLM no válida JSON: {respuesta_llm}")
        raise HTTPException(status_code=500, detail="Formato de ejercicio no válido recibido.")
    
    # Crear un id único para el ejercicio y almacenar respuesta correcta
    global exercise_counter
    qid = exercise_counter
    exercise_counter += 1
    correct_answer = data.get("answer")
    exercise_storage[qid] = {
    "question": data.get("question", ""),
    "subject": subject,
    "answer": correct_answer
}
    logging.info(f"Ejercicio {qid} generado - Materia: {subject}, Nivel: {level}")
    # Preparar la respuesta (no incluyas la respuesta correcta en el output)
    return {
        "question_id": qid,
        "subject": subject,
        "level": level,
        "question": data.get("question", ""),
        "options": data.get("options", None)
    }

# --- Endpoint: /tutor/evaluate --- #
@app.post("/tutor/evaluate", response_model=EvaluateResponse)
async def evaluate_answer(request: EvaluateRequest):
    # Extraer datos de entrada
    qid = request.question_id
    user_answer = request.answer

    # Verificar que el ID de pregunta exista
    if qid not in exercise_storage:
        raise HTTPException(status_code=404, detail="El ejercicio con ese ID no existe o expiró.")

    # Recuperar respuesta correcta (y contexto si disponible) 
    record = exercise_storage[qid]
    if isinstance(record, dict):
        correct_answer = record.get("answer", "")
        question_text = record.get("question", "")
        subject = record.get("subject", "")
    else:
        # Manejo de compatibilidad: por si se almacenó solo la respuesta como cadena
        correct_answer = str(record)
        question_text = ""
        subject = ""

    # Normalizar las cadenas para comparación (minúsculas, sin espacios extremos)
    student_answer_norm = user_answer.strip().lower()
    correct_answer_norm = str(correct_answer).strip().lower()
    is_correct = (student_answer_norm == correct_answer_norm)
    logging.info(f"Pregunta {qid} evaluada - Resultado: {'correcta' if is_correct else 'incorrecta'}")

    # Generar retroalimentación
    if is_correct:
        feedback_text = "¡Respuesta correcta! Muy bien, sigue así."
    else:
        # Generar explicación breve con ayuda del LLM
        # Incluir el contexto de la pregunta y la respuesta correcta para una mejor retroalimentación
        feedback_prompt = (
            f"Eres un tutor de {subject} que está evaluando la respuesta de un estudiante.\n"
            f"Pregunta: {question_text}\n"
            f"Respuesta del estudiante: {user_answer}\n"
            f"La respuesta correcta es: {correct_answer}.\n"
            f"Explica en una o dos oraciones por qué la respuesta correcta es {correct_answer} y brinda un consejo para el estudiante."
            f"Habla directamente al estudiante usando 'tú'."
        )
        feedback_text = (await generar_respuesta(feedback_prompt)).strip()
        # Si accidentalmente el LLM responde con un JSON, extraer el texto
        if feedback_text.startswith("{"):
            try:
                possible_json = json.loads(feedback_text)
                if isinstance(possible_json, str):
                    feedback_text = possible_json
                elif isinstance(possible_json, dict) and "feedback" in possible_json:
                    feedback_text = possible_json["feedback"]
            except json.JSONDecodeError:
                # Si no es JSON válido, dejaremos tal cual
                pass
    
    if qid in exercise_storage:
        del exercise_storage[qid]

    # Actualizar métricas de progreso
    global evaluation_count, correct_count
    evaluation_count += 1
    if is_correct:
        correct_count += 1
    # Calcular porcentaje de aciertos
    percentage = int((correct_count / evaluation_count) * 100)
    progress_summary = f"{correct_count} de {evaluation_count} correctas ({percentage}%)"

    # Retornar resultado de la evaluación
    return {
        "correct": is_correct,
        "feedback": feedback_text,
        "progress": progress_summary
    }

TIMEOUT_SECS = 120  # Timeout global para llamadas a Ollama (en segundos)    
# --- Endpoint: /tutor/preload --- #
@app.on_event("startup")
async def preload_model():
    async with httpx.AsyncClient() as client:
        await client.post(
            OLLAMA_URL,
            json={ "model": DEFAULT_MODEL, "prompt": "", "keep_alive": "24h", "stream": False },
            timeout=TIMEOUT_SECS  # ampliado por precaución
        )
