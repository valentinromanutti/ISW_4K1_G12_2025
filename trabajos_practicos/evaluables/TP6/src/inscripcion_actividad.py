import datetime
import sqlite3



def inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones):

    if not acepta_terminos_condiciones:
        raise ValueError("Se deben aceptar los terminos y condiciones")

    #Validacion de que la actividad no haya sucedido
    fecha_actual, horario_actual = datetime.datetime.now().strftime("%d-%m-%Y %H:%M").split(" ")

    dia_actual, mes_actual, anio_actual= (int(fecha) for fecha in fecha_actual.split("-"))
    dia_actividad, mes_actividad, anio_actividad = (int(fecha) for fecha in fecha_actividad.split("-"))

    hora_actual, minutos_actual, _ = (int (horario) for horario in horario_actual.split(":"))
    hora_actividad, minutos_actividad = (int (horario) for horario in horario_actividad.split(":"))

    if (
            anio_actividad < anio_actual or
            (anio_actividad == anio_actual and mes_actividad < mes_actual) or
            (anio_actividad == anio_actual and mes_actividad == mes_actual and dia_actividad < dia_actual) or
            (anio_actividad == anio_actual and mes_actividad == mes_actual and dia_actividad == dia_actual and  hora_actividad < hora_actual) or
            (anio_actividad == anio_actual and mes_actividad == mes_actual and dia_actividad == dia_actual and  hora_actividad == hora_actual and minutos_actividad < minutos_actual)
    ):
        raise ValueError("No se puede inscribir a actividades ya realizadas")

    conn = sqlite3.connect('../data/parque.db')
    cursor = conn.cursor()

    fecha_hora = datetime.datetime.now()
    fecha_actual = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")

    #busca el id del horario, id de la actividad y cupos disponibles para esa actividad en ese horario
    cursor.execute("""
    SELECT A.id, H.id, AXH.cupos_disponibles
    FROM ACTIVIDAD_X_HORARIO AXH 
    join ACTIVIDAD A on A.id = AXH.id_actividad 
    join HORARIOS H on AXH.id_horario = H.id
    WHERE A.nombre = ? AND AXH.fecha = ? AND H.hora = ?
    """, (actividad, fecha_actividad, horario_actividad))

    row = cursor.fetchone()

    if row is None:
        raise ValueError("No hay horario para esa actividad.")

    id_actividad, id_horario, cupos_disponibles = row
    cupos_actualizados = cupos_disponibles - len(personas)

    if cupos_actualizados < 0:
        raise ValueError("No hay cupos suficientes para inscribir a todas las personas.")

    cursor.execute("""
        UPDATE ACTIVIDAD_X_HORARIO AXH 
        SET cupos_disponibles = ? 
        WHERE AXH.id_actividad = ? AND AXH.id_horario = ? AND AXH.fecha = ?
        """, (cupos_actualizados, id_actividad, id_horario, fecha_actividad))


    for persona in personas:
        if (actividad == "Palestra" and persona["edad"] < 12 or actividad == "Tirolesa" and persona["edad"] < 8):
            raise ValueError("no cumple con la edad mínima")
        if actividad in ("Palestra", "Tirolesa"):
            cursor.execute("""
            SELECT id FROM TALLA
            WHERE nombre = ?""", (persona["talle"]))

            id_talle = cursor.fetchone()

            cursor.execute("""
            INSERT INTO INSCRIPCION (id_actividad, id_horario, fecha, dni, id_talla) 
            VALUES (?, ?, ?, ?, ?)
            """, (id_actividad, id_horario, fecha_actividad, persona["dni"], id_talle))
            if id_talle is None:
                raise ValueError("Talle de persona invalido")


        else:
            cursor.execute("""
                        INSERT INTO INSCRIPCION (id_actividad, id_horario, fecha, dni) 
                        VALUES (?, ?, ?, ?)
                        """, (id_actividad, id_horario, fecha_actividad, persona["dni"]))
    conn.commit()
    cursor.close()

    print(row)




