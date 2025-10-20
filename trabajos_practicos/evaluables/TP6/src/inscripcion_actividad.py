import datetime
import sqlite3



def inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones):

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

    cursor.execute("""
        UPDATE ACTIVIDAD_X_HORARIO AXH 
        SET cupos_disponibles = ? 
        WHERE AXH.id_actividad = ? AND AXH.id_horario = ? AND AXH.fecha = ?
        """, (cupos_actualizados, id_actividad, id_horario, fecha_actividad))

    for persona in personas:
        cursor.execute("""
        SELECT id FROM TALLA
        WHERE nombre = ?""", (persona["talle"]))

        id_talle = cursor.fetchone()

        cursor.execute("""
        INSERT INTO INSCRIPCION (id_actividad, id_horario, fecha, dni, id_talla) 
        VALUES (?, ?, ?, ?, ?)
        """, (id_actividad, id_horario, fecha_actividad, persona["dni"], id_talle))

    conn.commit()
    cursor.close()

    print(row)




