# app/schemas.py
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class ExplainRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Materia o área (ej: 'matemáticas', 'programación', 'inglés')", example="matemáticas")
    topic: str = Field(..., min_length=1, description="Concepto específico a explicar", example="ecuaciones cuadráticas")

class ExplainResponse(BaseModel):
    explanation: str  # Texto de la explicación generada


class EvaluateRequest(BaseModel):
    question_id: int = Field(..., description="ID del ejercicio a evaluar (provisto por /tutor/exercise)", example=1)
    answer: str = Field(..., min_length=1, description="Respuesta que el estudiante proporciona para el ejercicio", example="La capital de Francia es París.")

class EvaluateResponse(BaseModel):
    correct: bool = Field(..., description="Indica si la respuesta del estudiante es correcta (true/false)")
    feedback: str = Field(..., description="Breve retroalimentación del tutor respecto a la respuesta")
    progress: str = Field(..., description="Resumen del progreso del estudiante (p.ej., cantidad de aciertos totales)")


class Difficulty(str, Enum):
    basico = "basico"
    intermedio = "intermedio"
    avanzado = "avanzado"

class ExerciseRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Materia para la cual se generará el ejercicio (ej: 'matemáticas', 'programación', 'inglés')", example="matemáticas")
    level: Optional[Difficulty] = Field(None, description="Nivel de dificultad ('básico', 'intermedio', 'avanzado'). Si no se especifica, se usará un nivel predeterminado o adaptativo.", example="intermedio")

class ExerciseResponse(BaseModel):
    question_id: int = Field(..., description="Identificador único del ejercicio generado")
    subject: str = Field(..., description="Materia del ejercicio")
    level: Difficulty = Field(..., description="Nivel de dificultad del ejercicio")
    question: str = Field(..., description="Enunciado del ejercicio creado por el tutor")
    options: Optional[List[str]] = Field(None, description="Opciones de respuesta (solo si es un ejercicio de opción múltiple)")