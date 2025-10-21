-- Activar chequeo de claves foráneas en SQLite
PRAGMA foreign_keys = ON;

-- =========================
-- Tablas base
-- =========================
CREATE TABLE IF NOT EXISTS ACTIVIDAD (
    id        INTEGER PRIMARY KEY,
    nombre    TEXT    NOT NULL,
    vestimenta INTEGER NOT NULL DEFAULT 0 CHECK (vestimenta IN (0,1)), -- booleano 0/1
    cupos_max INTEGER NOT NULL CHECK (cupos_max >= 0),
    duracion  TEXT,
    terminos_y_condiciones TEXT,
    fecha     DATE
);

CREATE TABLE IF NOT EXISTS HORARIOS (
    id   INTEGER PRIMARY KEY,
    hora TEXT NOT NULL                                 -- ej. "16:00"
    -- Opcional: validar formato HH:MM (simple)
    -- , CHECK (hora GLOB '[0-2][0-9]:[0-5][0-9]')
);

CREATE TABLE IF NOT EXISTS VISITANTE (
    dni              INTEGER PRIMARY KEY,
    nombre           TEXT NOT NULL,
    edad             INTEGER CHECK (edad IS NULL OR edad >= 0)
);

CREATE TABLE IF NOT EXISTS TALLA (
    id     INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

-- =========================================
-- Relación Actividad × Horario (con fecha)
-- =========================================
CREATE TABLE IF NOT EXISTS ACTIVIDAD_X_HORARIO (
    id_actividad      INTEGER NOT NULL,
    id_horario        INTEGER NOT NULL,
    fecha             DATE    NOT NULL,
    cupos_disponibles INTEGER NOT NULL CHECK (cupos_disponibles >= 0),

    -- PK compuesta: una fila por (actividad, horario, fecha)
    PRIMARY KEY (id_actividad, id_horario, fecha),

    FOREIGN KEY (id_actividad) REFERENCES ACTIVIDADES (id) ON DELETE CASCADE,
    FOREIGN KEY (id_horario)   REFERENCES HORARIOS  (id) ON DELETE CASCADE
);
-- =========================
-- Inscripciones
-- =========================
CREATE TABLE IF NOT EXISTS INSCRIPCION (
    id_actividad INTEGER NOT NULL,
    id_horario   INTEGER NOT NULL,
    fecha        DATE    NOT NULL,
    dni          INTEGER NOT NULL,
    id_talla     INTEGER NOT NULL,

    -- Una inscripción por visitante para una combinación actividad-horario-fecha
    PRIMARY KEY (id_actividad, id_horario, fecha, dni),

    -- FK a la relación actividad×horario×fecha
    FOREIGN KEY (id_actividad, id_horario, fecha)
        REFERENCES ACTIVIDADES_X_HORARIOS (id_actividad, id_horario, fecha)
        ON DELETE CASCADE,

    FOREIGN KEY (dni)     REFERENCES VISITANTES (dni) ON DELETE CASCADE,
    FOREIGN KEY (id_talla) REFERENCES TALLAS (id)
);

-- =========================
-- Índices útiles (performance)
-- =========================
CREATE INDEX IF NOT EXISTS idx_axh_actividad_fecha
    ON ACTIVIDADES_X_HORARIOS (id_actividad, fecha);

CREATE INDEX IF NOT EXISTS idx_inscripcion_dni
    ON INSCRIPCIONES (dni);

CREATE INDEX IF NOT EXISTS idx_inscripcion_talla
    ON INSCRIPCIONES (id_talla);