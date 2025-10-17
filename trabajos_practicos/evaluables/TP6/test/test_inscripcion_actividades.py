import datetime

import pytest

def test_inscribir_actividad_con_talle_pasa(mocker):
    # PRECONDICIONES
    fecha_actual = "17-10-2025"
    fecha_actividad = "18-10-2025"
    horario_actividad = "16:00"
    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 15, "talle": "L"}
    ]
    acepta_terminos_condiciones = True

    # 🔹 Mock de conexión y cursor
    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("datetime.datetime").now.return_value = fecha_actual

    # 🔹 Simular fetchone() secuencial:
    # 1️⃣ SELECT actividad_x_horario → cupos disponibles
    # 2️⃣ Talla M existe, 3️⃣ Talla S existe, 4️⃣ Talla XS existe
    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),   # id_actividad, id_horario, cupos_disponibles
        (1,), (2,), (3,),  # ids de talles
    ]

    # 🔹 Ejecutar función
    inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones)

    # 🔹 Verificar que se hizo el SELECT correcto
    mock_cursor.execute.assert_any_call(
        mocker.ANY, ("Palestra", "18-10-2025", "16:00")
    )

    # 🔹 Verificar que se actualizan los cupos
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (2, 1, 2, "18-10-2025")
    )

    # 🔹 Verificar que se insertaron inscripciones
    insert_calls = [c for c in mock_cursor.execute.call_args_list if "INSERT INTO INSCRIPCION" in str(c)]
    assert len(insert_calls) == len(personas)

    # 🔹 Verificar que se hizo commit
    mock_conn.return_value.commit.assert_called_once()

def test_inscribir_actividad_sin_talle_requerido_pasa(mocker):
    fecha_actual = "17-10-2025"
    fecha_actividad = "17-10-2025"
    horario_actividad = "16:00"
    actividad = "Safari"
    personas = [{"dni": 100000, "nombre": "Juan Perez", "edad": 18},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20},
        {"dni": 100002, "nombre": "Pepito", "edad": 18}]

    acepta_terminos_condiciones = True

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("datetime.datetime").now.return_value = fecha_actual

    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),  # id_actividad, id_horario, cupos_disponibles
        (1,), (2,), (3,),  # ids de talles
    ]

    # 🔹 Ejecutar función
    inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones)

    # 🔹 Verificar que se hizo el SELECT correcto
    mock_cursor.execute.assert_any_call(
        mocker.ANY, ("Palestra", "18-10-2025", "16:00")
    )

    # 🔹 Verificar que se actualizan los cupos
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (2, 1, 2, "18-10-2025")
    )

    # 🔹 Verificar que se insertaron inscripciones
    insert_calls = [c for c in mock_cursor.execute.call_args_list if "INSERT INTO INSCRIPCION" in str(c)]
    assert len(insert_calls) == len(personas)

    # 🔹 Verificar que se hizo commit
    mock_conn.return_value.commit.assert_called_once()


def test_inscribir_actividad_sin_cupos_disponibles_falla(mocker):
    #PRECONDICIONES
    fecha_actual = "17-10-2025"
    horario_actividad = "16:00"
    fecha_actividad = "18-10-2025"
    actividad = "Palestra"
    personas = [{"dni": 100000, "nombre": "juan perez", "edad": 18, "talle": "XL"},
                {"dni": 100001, "nombre": "mari perez", "edad": 20, "talle": "L"},
                {"dni": 100002, "nombre": "Pepito", "edad": 32, "talle": "S"}]
    acepta_terminos_condiciones = True

    # 🔹 Mock de la conexión y el cursor
    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_date = mocker.patch("datetime.datetime")

    mock_date.now.return_value = fecha_actual

    # 🔹 Simulamos que la actividad "Palestra" tiene solo 2 cupos disponibles
    mock_cursor.fetchone.return_value = (
        1,           # id_actividad
        2,           # id_horario
        "17/10/2025",
        2            # cupos_disponibles
    )

    # 🔹 Importamos la función a probar
    # 🔹 Ejecutamos la función y esperamos un ValueError
    # VALIDACIONES
    try:
        inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones)
        assert False, "Debería lanzar un ValueError por falta de cupos"
    except ValueError as e:
        assert str(e) == "No hay cupos suficientes para inscribir a todas las personas."

    # 🔹 Verificamos que se consultó correctamente la actividad
    mock_cursor.execute.assert_any_call(
        mocker.ANY, ("Palestra", "17/10/2025", "16:00")
    )

    # 🔹 No deberían haberse hecho inserciones en la tabla INSCRIPCION
    assert mock_cursor.execute.call_count == 1

    # 🔹 No debería haberse hecho commit porque no se insertó nada
    mock_conn.return_value.commit.assert_not_called()

def test_inscribir_actividad_con_talle_requerido_con_talle_invalido_falla(mocker):
    fecha_actual = "17-10-2025"
    fecha_actividad = "18-10-2025"
    horario_actividad = "16:00"
    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 17, "talle": ""}
    ]
    acepta_terminos_condiciones = True

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("datetime.datetime").now.return_value = fecha_actual

    try:
        inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones)
        assert False, "Debería lanzar un ValueError por falta de talles"
    except ValueError as e:
        assert str(e) == "Talle de persona invalido"



def test_inscribir_actividad_sin_aceptar_terminos_falla(mocker):
    fecha_actual = "17-10-2025"
    fecha_actividad = "17-10-2025"
    horario_actividad = "16:00"
    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 18, "talle": "L"}
    ]
    acepta_terminos_condiciones = False

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("datetime.datetime").now.return_value = fecha_actual

    try:
        inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones)
        assert False, "Debería lanzar un ValueError por no aceptar los terminos y condiciones"
    except ValueError as e:
        assert str(e) == "Se deben aceptar los terminos y condiciones"

@pytest.mark.parametrize("fecha_actual, fecha_actividad, horario_actividad, acepta_terminos, mensaje_esperado", [
    ("20-10-2025","20-10-2025", "10:00", True, "No se permiten inscripciones los lunes."),  # lunes
    ("25-12-2025", "25-12-2025", "10:00", True, "No se permiten inscripciones en Navidad."), # navidad
    ("01-01-2025", "01-01-2025", "10:00", True, "No se permiten inscripciones en Año Nuevo."), # año nuevo
    ("17-10-2025", "17-10-2025", "22:00", True, "El parque está cerrado en ese horario."),   # fuera de horario
    ("17-10-2025", "17-10-2025", "10:25", True, "No hay horario para esa actividad."),
    ("15-10-2025", "18-10-2025", "10:30", True, "no se puede inscribir con mas de dos dias de anticipacion"),# actividad sin horario
    ("18-10-2025", "15-10-2025", "10:30", True, "no se puede inscribir a actividades ya realizadas")
])
def test_inscribir_actividad_en_horario_no_valido_falla(mocker,fecha_actual, fecha_actividad, horario_actividad, acepta_terminos, mensaje_esperado):
    """
    Casos en los que la inscripción debe fallar:
    - Fecha inválida (lunes, 25/12 o 01/01)
    - Horario fuera de 9 a 19
    - La actividad no tiene horario disponible en ese momento
    """

    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 19, "talle": "L"},
    ]

    # 🔹 Mockear la conexión (no debería usarse si la validación es previa)
    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("datetime.datetime").now.return_value = fecha_actual

    # 🔹 Simular que no hay horario registrado para esa actividad (caso 5)
    mock_cursor.fetchone.return_value = None

    # 🔹 Ejecutar la función y verificar que lanza un ValueError con el mensaje esperado
    with pytest.raises(ValueError, match=mensaje_esperado):
        inscribir_actividad(
            actividad, fecha_actividad, horario_actividad, personas, acepta_terminos
        )

    # 🔹 En estos casos, nunca debería llegar a ejecutar un INSERT ni commit
    mock_cursor.execute.assert_not_called()
    mock_conn.return_value.commit.assert_not_called()


# test parametrizables para la palestra y tirolesa
@pytest.mark.parametrize("actividad, edad_minima, personas_invalidas", [
    ("Palestra", 12, [{"dni": 100002, "nombre": "Pepito", "edad": 10}]),   # menor a 12
    ("Tirolesa", 8,  [{"dni": 100003, "nombre": "Carlitos", "edad": 7}]),  # menor a 8
])
def test_inscribir_actividad_falla_por_edad_minima(mocker, actividad, edad_minima, personas_invalidas):
    # 🔹 PRECONDICIONES
    fecha_actual = "17-10-2025"
    fecha_actividad = "18-10-2025"
    horario_actividad = "16:00"
    personas_validas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": edad_minima + 1},
        {"dni": 100001, "nombre": "Maria Perez", "edad": edad_minima + 2}
    ]
    personas = personas_validas + personas_invalidas
    acepta_terminos_condiciones = True

    # 🔹 Mock de la conexión y el cursor
    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("datetime.datetime").now.return_value = fecha_actual

    # 🔹 Simular que hay cupos suficientes
    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),  # id_actividad, id_horario, cupos_disponibles
    ]

    # 🔹 Ejecutar la función y verificar que lanza un ValueError
    with pytest.raises(ValueError, match="no cumple con la edad mínima"):
        inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones)

    # 🔹 Verificar que NO se realizaron inserts ni commits
    assert mock_conn.return_value.commit.call_count == 0
    assert all("INSERT" not in str(call) for call in mock_cursor.execute.call_args_list)


