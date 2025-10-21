import datetime
import sqlite3


def inscribir_actividad(
        actividad, fecha_actividad, horario_actividad, personas,
        acepta_terminos_condiciones):
    if not acepta_terminos_condiciones:
        raise ValueError("Se deben aceptar los terminos y condiciones")

    # Obtener fecha y hora actual como objeto datetime
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
            "No se puede inscribir a una actividad con más de dos dias de "
            "anticipacion")

    conn = sqlite3.connect('data/parque.db')
    cursor = conn.cursor()
    #Validacion de que todos los datos de las personas esten cargados sin tener en cuenta la talla
    for persona in personas:
        if not all([persona.get("dni"), persona.get("nombre"), persona.get("edad")]):
            raise ValueError("Los datos de la persona están incompletos")

    # busca el id del horario, id de la actividad y cupos disponibles para esa actividad en ese horario
    cursor.execute("""
    SELECT A.id, H.id, AXH.cupos_disponibles
    FROM ACTIVIDADES_X_HORARIOS AXH 
    join ACTIVIDADES A on A.id = AXH.id_actividad 
    join HORARIOS H on AXH.id_horario = H.id
    WHERE A.nombre = ? AND AXH.fecha = ? AND H.hora = ?
    """, (actividad, fecha_actividad, horario_actividad))

    row = cursor.fetchone()

    if row is None:
        raise ValueError("No hay horario para esa actividad.")

    id_actividad, id_horario, cupos_disponibles = row
    cupos_actualizados = cupos_disponibles - len(personas)

    if cupos_actualizados < 0:
        raise ValueError(
            "No hay cupos suficientes para inscribir a todas las personas.")

    cursor.execute("""
        UPDATE ACTIVIDADES_X_HORARIOS AXH 
        SET cupos_disponibles = ? 
        WHERE AXH.id_actividad = ? AND AXH.id_horario = ? AND AXH.fecha = ?
        """, (cupos_actualizados, id_actividad, id_horario, fecha_actividad))

    for persona in personas:
        es_palestra = (actividad == "Palestra" and persona["edad"] < 12)
        es_tirolesa = (actividad == "Tirolesa" and persona["edad"] < 8)

        if es_palestra or es_tirolesa:
            raise ValueError("no cumple con la edad mínima")
        if actividad in ("Palestra", "Tirolesa"):
            cursor.execute("""
            SELECT id FROM TALLA
            WHERE nombre = ?""", (persona["talle"],))

            id_talle = cursor.fetchone()

            if id_talle is None:
                raise ValueError("Talle de persona invalido")

            cursor.execute("""
            INSERT INTO INSCRIPCIONES (id_actividad, id_horario, fecha, dni, id_talla) 
            VALUES (?, ?, ?, ?, ?)
            """, (
                id_actividad, id_horario, fecha_actividad,
                persona["dni"], id_talle[0]))

        else:
            cursor.execute("""
                        INSERT INTO INSCRIPCIONES (id_actividad, id_horario, fecha, dni) 
                        VALUES (?, ?, ?, ?)
                        """, (id_actividad, id_horario, fecha_actividad, persona["dni"]))
    conn.commit()
    cursor.close()

    print(row)
