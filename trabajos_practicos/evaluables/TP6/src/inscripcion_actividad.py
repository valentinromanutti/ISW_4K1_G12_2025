import datetime
import sqlite3
from sqlite3 import IntegrityError, OperationalError


def inscribir_actividad(
        actividad, fecha_actividad, horario_actividad, personas,
        acepta_terminos_condiciones):
    # -----------------------------------------------------------
    # VALIDACIONES INICIALES (antes de la conexión a la DB)
    # -----------------------------------------------------------
    if not acepta_terminos_condiciones:
        raise ValueError("Se deben aceptar los terminos y condiciones")

    fecha_hora_actual = datetime.datetime.now()

    # Parsear la fecha de la actividad
    dia_actividad, mes_actividad, anio_actividad = (
        int(fecha) for fecha in fecha_actividad.split("-"))
    hora_actividad, minutos_actividad = (
        int(horario) for horario in horario_actividad.split(":"))

    # Crear objeto datetime para la actividad
    fecha_hora_actividad = datetime.datetime(
        anio_actividad, mes_actividad, dia_actividad, hora_actividad,
        minutos_actividad)

    # Validación de que la actividad no haya sucedido
    if fecha_hora_actividad < fecha_hora_actual:
        raise ValueError("No se puede inscribir a actividades ya realizadas")

    # Validación de anticipación máxima de 2 días
    diferencia_dias = (fecha_hora_actividad.date() -
                       fecha_hora_actual.date()).days

    if diferencia_dias > 2:
        raise ValueError(
            "No se puede inscribir a una actividad con "
            "más de dos dias de anticipacion")

    # Validación de que todos los datos de las personas esten cargados
    for persona in personas:
        if not all([
            persona.get("dni"),
            persona.get("nombre"),
            persona.get("edad")
        ]):
            raise ValueError("Los datos de la persona están incompletos")

    # -----------------------------------------------------------
    # MANEJO DE CONEXIÓN ROBUSTO
    # -----------------------------------------------------------
    conn = None  # Se inicializa la conexión para el bloque finally
    row = None
    try:
        conn = sqlite3.connect('data/parque.db')
        cursor = conn.cursor()

        # busca el id del horario, id de la actividad y cupos disponibles
        cursor.execute(
            "SELECT A.id, H.id, AXH.cupos_disponibles "
            "FROM ACTIVIDADES_X_HORARIOS AXH "
            "join ACTIVIDADES A on A.id = AXH.id_actividad "
            "join HORARIOS H on AXH.id_horario = H.id "
            "WHERE A.nombre = ? AND AXH.fecha = ? AND H.hora = ?",
            (actividad, fecha_actividad, horario_actividad))
        # print("paso") # Se comenta print de debug

        row = cursor.fetchone()

        if row is None:
            raise ValueError("No hay horario para esa actividad.")

        id_actividad, id_horario, cupos_disponibles = row
        cupos_actualizados = cupos_disponibles - len(personas)

        if cupos_actualizados < 0:
            raise ValueError(
                "No hay cupos suficientes para"
                " inscribir a todas las personas.")

        # 1. ACTUALIZA CUPOS
        cursor.execute("""
        UPDATE ACTIVIDADES_X_HORARIOS
        SET cupos_disponibles = ?
        WHERE id_actividad = ? AND id_horario = ? AND fecha = ?
        """, (cupos_actualizados, id_actividad, id_horario, fecha_actividad))

        # print("paso2") # Se comenta print de debug

        # 2. INSERTA INSCRIPCIONES
        try:
            for persona in personas:
                es_palestra = (
                    actividad == "Palestra" and persona["edad"] < 12)
                es_tirolesa = (
                    actividad == "Tirolesa" and persona["edad"] < 8)

                if es_palestra or es_tirolesa:
                    raise ValueError("no cumple con la edad mínima")

                if actividad in ("Palestra", "Tirolesa"):
                    cursor.execute("""
                    SELECT id FROM TALLAS
                    WHERE nombre = ?""", (persona.get("talle"),))
                    # Se usa .get para evitar KeyError si 'talle' falta

                    id_talle = cursor.fetchone()

                    if id_talle is None:
                        raise ValueError("Talle de persona invalido")

                    cursor.execute("""
                    INSERT INTO INSCRIPCIONES
                    (id_actividad, id_horario, fecha, dni,
                     id_talla, nombre_visitante)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        id_actividad, id_horario, fecha_actividad,
                        persona["dni"], id_talle[0], persona["nombre"]))
                else:
                    # CORRECCIÓN DE ERROR SQL: Se aseguran 6 placeholders.
                    cursor.execute("""
                    INSERT INTO INSCRIPCIONES
                    (id_actividad, id_horario, fecha, dni,
                     id_talla, nombre_visitante)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        id_actividad, id_horario, fecha_actividad,
                        persona["dni"], None, persona["nombre"]))
                    # Se pasa None como id_talla

        except IntegrityError as e:
            print(e)
            raise ValueError(
                "No se puede inscribir con el mismo DNI en un mismo "
                "horario de actividad")

        # Si todo se ejecutó sin errores
        conn.commit()
        return row

    except (ValueError, IntegrityError, OperationalError) as e:
        # Si ocurre un error de validación o de DB, se garantiza el rollback.
        if conn:
            conn.rollback()
        raise e  # Relanzamos la excepción

    finally:
        # ESTE BLOQUE SE EJECUTA SIEMPRE: Asegura el cierre de la conexión.
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conn:
            conn.close()


def mostrar_cupos_para_fecha_hora_actividad(
        actividad, fecha_actividad, horario_actividad):

    conn = sqlite3.connect('data/parque.db')
    cursor = conn.cursor()

    # busca el id del horario, id de la actividad y cupos disponibles
    cursor.execute("""
    SELECT AXH.cupos_disponibles
    FROM ACTIVIDADES_X_HORARIOS AXH
    join ACTIVIDADES A on A.id = AXH.id_actividad
    join HORARIOS H on AXH.id_horario = H.id
    WHERE A.nombre = ? AND AXH.fecha = ? AND H.hora = ?
    """, (actividad, fecha_actividad, horario_actividad))

    return cursor.fetchone()