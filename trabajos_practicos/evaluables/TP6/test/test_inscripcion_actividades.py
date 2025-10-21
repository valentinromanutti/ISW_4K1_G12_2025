import datetime
from src.inscripcion_actividad import inscribir_actividad
import pytest
import sqlite3


def test_inscribir_actividad_con_talle_pasa(mocker):
    # PRECONDICIONES
    fecha_actual = "17-10-2025"
    hora_actual = "12:00:00"

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

    # 🔹 Parsear fecha_actual y hora_actual para crear objeto datetime
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    # 🔹 Mock de datetime.datetime.now() - devuelve un objeto datetime real
    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    # 🔹 Simular fetchone() secuencial:
    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),  # id_actividad, id_horario, cupos_disponibles
        (1,), (2,), (3,),  # ids de talles
    ]

    # 🔹 Ejecutar función
    inscribir_actividad(
        actividad,
        fecha_actividad,
        horario_actividad,
        personas,
        acepta_terminos_condiciones
    )

    # 🔹 Verificar que se hizo el SELECT correcto
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (actividad, fecha_actividad, horario_actividad)
    )

    # 🔹 Verificar que se insertaron inscripciones
    insert_calls = [c for c in mock_cursor.execute.call_args_list
                    if "INSERT INTO INSCRIPCIONES" in str(c)]

    assert len(insert_calls) == len(personas)

    # 🔹 Verificar que se actualizan los cupos
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (2, 1, 2, fecha_actividad)
    )

    # 🔹 Verificar que se hizo commit
    mock_conn.return_value.commit.assert_called_once()


def test_inscribir_actividad_sin_talle_requerido_pasa(mocker):
    fecha_actual = "17-10-2025"
    hora_actual = "12:00:00"

    fecha_actividad = "17-10-2025"
    horario_actividad = "16:00"
    actividad = "Safari"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20},
        {"dni": 100002, "nombre": "Pepito", "edad": 18}
    ]
    acepta_terminos_condiciones = True

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    # 🔹 Parsear fecha_actual y hora_actual para crear objeto datetime
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),  # id_actividad, id_horario, cupos_disponibles
    ]

    # 🔹 Ejecutar función
    inscribir_actividad(
        actividad,
        fecha_actividad,
        horario_actividad,
        personas,
        acepta_terminos_condiciones
    )

    # 🔹 Verificar que se hizo el SELECT correcto
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (actividad, fecha_actividad, horario_actividad)
    )

    # 🔹 Verificar que se actualizan los cupos
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (2, 1, 2, fecha_actividad)
    )

    # 🔹 Verificar que se insertaron inscripciones
    insert_calls = [c for c in mock_cursor.execute.call_args_list
                    if "INSERT INTO INSCRIPCIONES" in str(c)]

    assert len(insert_calls) == len(personas)

    # 🔹 Verificar que se hizo commit
    mock_conn.return_value.commit.assert_called_once()


def test_inscribir_actividad_sin_cupos_disponibles_falla(mocker):
    fecha_actual = "17-10-2025"
    hora_actual = "12:00:00"

    horario_actividad = "16:00"
    fecha_actividad = "18-10-2025"
    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "juan perez", "edad": 18, "talle": "XL"},
        {"dni": 100001, "nombre": "mari perez", "edad": 20, "talle": "L"},
        {"dni": 100002, "nombre": "Pepito", "edad": 32, "talle": "S"}
    ]
    acepta_terminos_condiciones = True

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    # 🔹 Parsear fecha_actual y hora_actual para crear objeto datetime
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    # 🔹 Simulamos que la actividad "Palestra" tiene solo 2 cupos disponibles
    mock_cursor.fetchone.side_effect = [
        (1, 2, 2),  # id_actividad, id_horario, cupos_disponibles
        (1,), (2,), (3,),  # ids de talles
    ]

    try:
        inscribir_actividad(
            actividad,
            fecha_actividad,
            horario_actividad,
            personas,
            acepta_terminos_condiciones
        )
        assert False, "Debería lanzar un ValueError por falta de cupos"
    except ValueError as e:
        assert str(e) == (
            "No hay cupos suficientes para inscribir a todas las personas."
        )

    # 🔹 Verificamos que se consultó correctamente la actividad
    mock_cursor.execute.assert_any_call(
        mocker.ANY, (actividad, fecha_actividad, horario_actividad)
    )

    # 🔹 No deberían haberse hecho inserciones en la tabla INSCRIPCION
    # El SELECT es la única llamada esperada en este punto.
    assert mock_cursor.execute.call_count == 1

    # 🔹 No debería haberse hecho commit porque no se insertó nada
    mock_conn.return_value.commit.assert_not_called()


def test_inscribir_actividad_con_talle_requerido_con_talle_invalido_falla(
        mocker):
    fecha_actual = "17-10-2025"
    hora_actual = "12:00:00"

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

    # 🔹 Parsear fecha_actual y hora_actual para crear objeto datetime
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),  # id_actividad, id_horario, cupos_disponibles
        (1,), (2,), None
    ]

    try:
        inscribir_actividad(
            actividad,
            fecha_actividad,
            horario_actividad,
            personas,
            acepta_terminos_condiciones
        )
        assert False, "Debería lanzar un ValueError por falta de talles"
    except ValueError as e:
        assert str(e) == "Talle de persona invalido"


def test_inscribir_actividad_sin_aceptar_terminos_falla(mocker):
    fecha_actividad = "17-10-2025"
    horario_actividad = "16:00"
    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 18, "talle": "L"}
    ]
    acepta_terminos_condiciones = False

    mocker.patch("sqlite3.connect")

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        2025, 10, 17, 12, 0, 0
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    try:
        inscribir_actividad(
            actividad,
            fecha_actividad,
            horario_actividad,
            personas,
            acepta_terminos_condiciones
        )
        assert False, (
            "Debería lanzar un ValueError por no aceptar los terminos y "
            "condiciones"
        )
    except ValueError as e:
        assert str(e) == "Se deben aceptar los terminos y condiciones"


@pytest.mark.parametrize(
    ("fecha_actual, hora_actual, fecha_actividad, horario_actividad, "
     "acepta_terminos"),
    [
        ("20-10-2025", "8:00:00", "20-10-2025", "10:00", True),  # lunes
        ("25-12-2025", "8:00:00", "25-12-2025", "10:00", True),  # navidad
        ("01-01-2025", "8:00:00", "01-01-2025", "10:00", True),  # año nuevo
        ("17-10-2025", "8:00:00", "17-10-2025",
         "22:00", True),  # fuera de horario
        ("17-10-2025", "8:00:00", "17-10-2025",
         "10:25", True),  # actividad sin horario
    ])
def test_inscribir_actividad_en_horario_no_valido_falla(
        mocker, fecha_actual, hora_actual, fecha_actividad,
        horario_actividad, acepta_terminos):
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

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    # Parsear la fecha actual del test
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    # 🔹 Simular que no hay horario registrado para esa actividad
    mock_cursor.fetchone.return_value = None

    # 🔹 Ejecutar la función y verificar que lanza un ValueError
    with pytest.raises(ValueError, match="No hay horario para esa actividad."):
        inscribir_actividad(
            actividad,
            fecha_actividad,
            horario_actividad,
            personas,
            acepta_terminos
        )

    # 🔹 En estos casos, nunca debería llegar a ejecutar un INSERT ni commit
    mock_conn.return_value.commit.assert_not_called()


@pytest.mark.parametrize(
    "actividad, edad_minima, personas_invalidas",
    [
        (
            "Palestra", 12,
            [
                {"dni": 100002, "nombre": "Pepito", "edad": 10, "talle": "L"}
            ]
        ),  # menor a 12
        (
            "Tirolesa", 8,
            [
                {"dni": 100003, "nombre": "Carlitos", "edad": 7, "talle": "S"}
            ]
        ),  # menor a 8
    ])
def test_inscribir_actividad_inferior_edad_minima_falla(
        mocker, actividad, edad_minima, personas_invalidas):
    fecha_actividad = "18-10-2025"
    horario_actividad = "16:00"
    personas_validas = [
        {"dni": 100000, "nombre": "Juan Perez",
         "edad": edad_minima + 1, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez",
         "edad": edad_minima + 2, "talle": "S"},
    ]
    personas = personas_validas + personas_invalidas
    acepta_terminos_condiciones = True

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        2025, 10, 17, 12, 0, 0
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    # 🔹 Simular que hay cupos suficientes
    mock_cursor.fetchone.side_effect = [
        (1, 2, 5),  # id_actividad, id_horario, cupos_disponibles
        (1,), (2,), (3,)  # id de los talles cuando se haga el fetch
    ]

    # 🔹 Ejecutar la función y verificar que lanza un ValueError
    with pytest.raises(ValueError, match="no cumple con la edad mínima"):
        inscribir_actividad(
            actividad,
            fecha_actividad,
            horario_actividad,
            personas,
            acepta_terminos_condiciones
        )

    # 🔹 Verificar que NO se realizaron commits
    assert mock_conn.return_value.commit.call_count == 0


@pytest.mark.parametrize(
    "fecha_actual, hora_actual, fecha_actividad, horario_actividad",
    [
        # actividad realizada el dia anterior
        ("21-10-2025", "8:00:00", "20-10-2025", "10:00"),
        # actividad realizada un minuto antes
        ("20-10-2025", "10:01:00", "20-10-2025", "10:00")
    ])
def test_inscribir_actividad_ya_realizada_falla(
        mocker, fecha_actual, hora_actual, fecha_actividad,
        horario_actividad):
    acepta_terminos_condiciones = True

    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 19, "talle": "L"},
    ]

    mock_conn = mocker.patch("sqlite3.connect")

    # Parsear la fecha actual del test
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    with pytest.raises(
            ValueError,
            match="No se puede inscribir a actividades ya realizadas"):
        inscribir_actividad(
            actividad,
            fecha_actividad,
            horario_actividad,
            personas,
            acepta_terminos_condiciones
        )

    # 🔹 Verificar que NO se realizaron commits
    assert mock_conn.return_value.commit.call_count == 0


def test_inscribir_actividad_mas_de_dos_dias_antes_falla(mocker):
    fecha_actividad = "20-10-2025"
    horario_actividad = "16:00"
    actividad = "Palestra"
    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 15, "talle": "L"}
    ]
    acepta_terminos_condiciones = True

    mocker.patch("sqlite3.connect")

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        2025, 10, 17, 12, 0, 0
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    match_msg = ("No se puede inscribir a una actividad con más de dos dias "
                 "de anticipacion")
    with pytest.raises(ValueError, match=match_msg):
        inscribir_actividad(actividad, fecha_actividad,
                            horario_actividad, personas,
                            acepta_terminos_condiciones)


@pytest.mark.parametrize("personas", [
    [{"dni": None, "nombre": "Juan Perez", "edad": 18, "talle": "M"}],
    [{"dni": 100000, "nombre": None, "edad": 18, "talle": "M"}],
    [{"dni": 100000, "nombre": "Juan Perez", "edad": None, "talle": "M"}]
])
def test_inscribir_actividad_sin_campos_persona_completos_falla(mocker,
                                                                personas):

    fecha_actual = "17-10-2025"
    hora_actual = "12:00:00"

    fecha_actividad = "19-10-2025"
    horario_actividad = "16:00"

    acepta_terminos_condiciones = True
    actividad = "Palestra"

    mock_conn = mocker.patch("sqlite3.connect")
    # F841: La variable mock_cursor ya no es necesaria aquí.
    # mock_cursor = mock_conn.return_value.cursor.return_value

    # Parsear la fecha actual del test
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))

    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    with pytest.raises(ValueError, match="Los datos de la persona están "
                                         "incompletos"):
        inscribir_actividad(actividad, fecha_actividad, horario_actividad,
                            personas, acepta_terminos_condiciones)

    # 🔹 Verificar que NO se realizaron commits
    assert mock_conn.return_value.commit.call_count == 0


def test_inscribir_actividad_dos_veces_falla(mocker):
    fecha_actual = "17-10-2025"
    hora_actual = "12:00:00"
    fecha_actividad = "19-10-2025"
    horario_actividad = "16:00"
    acepta_terminos_condiciones = True
    actividad = "Palestra"

    personas = [
        {"dni": 100000, "nombre": "Juan Perez", "edad": 18, "talle": "M"},
        {"dni": 100001, "nombre": "Maria Perez", "edad": 20, "talle": "S"},
        {"dni": 100002, "nombre": "Pepito", "edad": 15, "talle": "L"}
    ]

    mock_conn = mocker.patch("sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    dia, mes, anio = map(int, fecha_actual.split("-"))
    hora, minuto, segundo = map(int, hora_actual.split(":"))
    mock_datetime = mocker.patch("src.inscripcion_actividad.datetime")

    mock_datetime.datetime.now.return_value = datetime.datetime(
        anio, mes, dia, hora, minuto, segundo
    )
    mock_datetime.datetime.side_effect = (
        lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
    )

    # Función que simula comportamiento del cursor.fetchone()
    llamadas = {"n": 0}

    def fake_fetchone():
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            return (1, 2, 5)  # SELECT principal
        elif llamadas["n"] in (2, 3):
            return (1,)  # SELECT de talla
        elif llamadas["n"] == 4:
            # Simula un error SQL en el tercer intento
            raise sqlite3.IntegrityError("Registro duplicado en INSCRIPCIONES")

    mock_cursor.fetchone.side_effect = fake_fetchone

    match_msg = ("No se puede inscribir con el mismo DNI en un mismo horario "
                 "de actividad")
    with pytest.raises(ValueError, match=match_msg):
        inscribir_actividad(actividad, fecha_actividad,
                            horario_actividad, personas,
                            acepta_terminos_condiciones)
