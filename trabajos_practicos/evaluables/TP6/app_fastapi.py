import sqlite3
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# IMPORTACIÓN DE LA LÓGICA DE NEGOCIO

try:
    from src.inscripcion_actividad import inscribir_actividad
except ImportError:
    print(
        r"¡ADVERTENCIA! No se pudo importar 'inscripcion_actividad'. "
        r"Asegúrate de que '\src\' esté en la ruta."
    )
    raise

# --- MODELOS PYDANTIC ---


class PersonaInscripcion(BaseModel):
    """
    Define la estructura de cada persona en la lista. Se asume que la
    función importada espera un diccionario con estos campos.
    """
    dni: int
    nombre: str
    edad: int
    talle: Optional[str] = None


class InscripcionRequest(BaseModel):
    # Define la estructura del cuerpo completo de la solicitud POST.
    actividad: str
    fecha_actividad: str  # Formato DD-MM-YYYY
    horario_actividad: str  # Formato HH:MM
    personas: List[PersonaInscripcion]
    acepta_terminos_condiciones: bool

# --- SERVIDOR FASTAPI Y ENDPOINT ---


app = FastAPI(
    title="Servidor de Inscripciones",
    description="API para gestionar inscripciones."
)


@app.post(
    "/inscribir",
    status_code=201,
    response_model=dict,
    tags=["Inscripciones"]
)
def handle_inscripcion(request_data: InscripcionRequest):
    """
    Endpoint POST para registrar a una o más personas a una actividad,
    llamando a la función externa.
    """
    # 1. Preparar los datos para la función importada
    # Convertir el objeto Pydantic a una lista de diccionarios, que es
    # lo que espera la función.
    personas_dict = [p.dict() for p in request_data.personas]

    # 2. Llamar a la lógica de negocio
    try:
        # La función inscribir_actividad se encarga de toda la
        # validación y la DB.
        resultado = inscribir_actividad(
            request_data.actividad,
            request_data.fecha_actividad,
            request_data.horario_actividad,
            personas_dict,
            request_data.acepta_terminos_condiciones
        )

        # Respuesta exitosa
        return {"mensaje": "Inscripción realizada con éxito.",
                "datos": resultado}

    except ValueError as e:
        # Errores de validación de negocio (capturados de la función)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Errores internos o de base de datos
        print(f"Error interno: {e}")
        # Se puede agregar un manejo específico para FileNotFoundError
        # si la DB falla.
        if "FileNotFoundError" in str(e):
            raise HTTPException(
                status_code=500,
                detail="Error de configuración: Base de datos no encontrada."
            )

        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al procesar la inscripción."
        )
