# app/llm_client.py
import os
import httpx
import logging 

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


timeout_config = httpx.Timeout(read=120, connect=20, write=120, pool=10)  # 10s para conexión, 120s para lectura
async def generar_respuesta(prompt: str, modelo: str = DEFAULT_MODEL) -> str:
    # Realiza la petición asíncrona al API de Ollama
    try:
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            res = await client.post(OLLAMA_URL, json={"model": modelo, "prompt": prompt, "stream": False}, timeout=None)
            logging.info(f"Respuesta del LLM recibida : HTTP {res.status_code} - {res.text[:100]}")
            res.raise_for_status()
            data = res.json()
    except Exception as e:
        logging.error(f"Error al llamar a Ollama: {repr(e)}")
        # Si hay error (timeout, conexión, etc.), devuelve mensaje de error genérico
        return "Lo siento, no se pudo obtener la explicación en este momento."
    # Procesar la respuesta JSON de Ollama
    logging.debug(f"Datos recibidos de Ollama: {data}")
    texto = data.get("response", "")  # obtener el texto generado
    return texto.strip()