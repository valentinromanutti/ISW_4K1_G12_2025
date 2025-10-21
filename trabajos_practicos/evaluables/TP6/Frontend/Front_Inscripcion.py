import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QCheckBox,
    QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget,
    QMessageBox, QDialog, QFormLayout, QDateEdit, QCalendarWidget, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QPalette


# ----------------------------------------
# FUNCIÓN LÓGICA DE INSCRIPCIÓN
# ----------------------------------------
def inscribir_actividad(
        actividad, fecha_actividad, horario_actividad, personas,
        acepta_terminos_condiciones):
    if not acepta_terminos_condiciones:
        raise ValueError("Se deben aceptar los términos y condiciones")

    fecha_actividad_dt = datetime.strptime(fecha_actividad, "%d-%m-%Y")
    fecha_actual_dt = datetime.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y")

    if fecha_actividad_dt.day == 25 and fecha_actividad_dt.month == 12:
        raise ValueError("No se permiten inscripciones en Navidad.")
    if fecha_actividad_dt.day == 1 and fecha_actividad_dt.month == 1:
        raise ValueError("No se permiten inscripciones en Año Nuevo.")
    if fecha_actividad_dt < fecha_actual_dt:
        raise ValueError("No se puede inscribir a actividades ya realizadas")
    if fecha_actividad_dt > fecha_actual_dt + timedelta(days=2):
        raise ValueError("No se puede inscribir con más de dos días de anticipación")
    if fecha_actividad_dt.weekday() == 0:
        raise ValueError("No se permiten inscripciones los lunes.")

    hora, minuto = map(int, horario_actividad.split(":"))
    if hora < 9 or (hora > 18 or (hora == 18 and minuto > 0)):
        raise ValueError("El parque está cerrado en ese horario.")
    if minuto not in (0, 30):
        raise ValueError("No hay horario para esa actividad.")

    if not personas:
        raise ValueError("Debe inscribir al menos una persona.")

    for persona in personas:
        edad_minima = {"Palestra": 12, "Tirolesa": 8}.get(actividad, 0)
        if persona["edad"] < edad_minima:
            raise ValueError(f"La edad mínima para {actividad} es {edad_minima} años.")
        if actividad in ["Palestra", "Tirolesa"] and not persona.get("talle"):
            raise ValueError(f"El talle es obligatorio para {actividad}.")

    return "Inscripción realizada correctamente."


# ----------------------------------------
# Diálogo de Términos
# ----------------------------------------
class TerminosDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Términos y Condiciones de Participación")
        self.setMinimumSize(450, 400)  # 🔹 Más chico
        self.aceptado = False

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        texto = QTextEdit()
        texto.setReadOnly(True)
        texto.setStyleSheet("""
            QTextEdit {
                background-color: #134611;
                color: #E8FCCF;
                border: none;
                font-size: 13px;
                font-weight: 500;
            }
        """)

        # 🔹 Texto original completo
        texto.setText("""Términos y Condiciones de Participación en Actividades

Al inscribirte en una actividad del parque, confirmás que comprendés y aceptás los siguientes términos y condiciones de participación.

La inscripción será válida únicamente para las actividades habilitadas dentro del listado oficial del parque, que incluye Tirolesa, Safari, Palestra y Jardinería. Cada una de ellas cuenta con cupos limitados por horario, por lo que la reserva quedará confirmada solamente si existen lugares disponibles al momento de realizar la inscripción.

No se permitirá la participación en actividades fuera del horario operativo del parque, que se encuentra comprendido entre las 9:00 y las 18:00 horas. Las actividades no se realizarán los días lunes ni en fechas festivas como Navidad o Año Nuevo.

Cada participante deberá cumplir con los requisitos de edad mínima y, en el caso de actividades como Tirolesa o Palestra, con la utilización obligatoria del equipo de seguridad adecuado, incluyendo arnés y casco del talle correspondiente.

El parque se reserva el derecho de cancelar o reprogramar actividades debido a condiciones climáticas adversas o por motivos de seguridad, notificando a los inscriptos por los medios de comunicación disponibles.

Al aceptar estos términos y condiciones, el participante declara haber leído y comprendido las normas establecidas y se compromete a cumplir con las indicaciones del personal del parque durante la actividad.
""")

        self.checkbox = QCheckBox("He leído y acepto los términos y condiciones")
        self.checkbox.setStyleSheet("color: #E8FCCF; font-size: 13px; font-weight: bold;")

        botones_layout = QHBoxLayout()
        self.boton_aceptar = QPushButton("Aceptar")
        self.boton_aceptar.setEnabled(False)
        self.boton_cancelar = QPushButton("Cancelar")

        for b in (self.boton_aceptar, self.boton_cancelar):
            b.setMinimumHeight(30)
            b.setStyleSheet(
                "background-color: #96E072; color: #134611; border-radius: 6px; font-weight: bold;"
            )

        self.checkbox.stateChanged.connect(lambda s: self.boton_aceptar.setEnabled(bool(s)))
        self.boton_aceptar.clicked.connect(self.confirmar)
        self.boton_cancelar.clicked.connect(self.reject)

        botones_layout.addWidget(self.boton_cancelar)
        botones_layout.addWidget(self.boton_aceptar)

        layout.addWidget(texto)
        layout.addWidget(self.checkbox)
        layout.addLayout(botones_layout)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #134611; color: #E8FCCF;")

    def confirmar(self):
        self.aceptado = True
        self.accept()


# ----------------------------------------
# Ventana para agregar persona
# ----------------------------------------
class DialogoPersona(QDialog):
    def __init__(self, actividad, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Persona")
        self.actividad = actividad
        self.persona_valida = None

        layout = QFormLayout()
        self.setStyleSheet("""
            QDialog { background-color: #134611; color: #E8FCCF; }
            QLineEdit, QComboBox {
                background-color: #3E8914; color: #E8FCCF;
                border: 1px solid #96E072; border-radius: 6px; padding: 6px;
            }
            QPushButton {
                background-color: #96E072; color: #134611;
                border: none; padding: 8px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E8FCCF; }
        """)

        self.dni = QLineEdit()
        self.nombre = QLineEdit()
        self.edad = QLineEdit()
        layout.addRow("DNI:", self.dni)
        layout.addRow("Nombre:", self.nombre)
        layout.addRow("Edad:", self.edad)

        self.requiere_talle = self.actividad in ["Palestra", "Tirolesa"]
        if self.requiere_talle:
            self.talle = QComboBox()
            self.talle.addItems(["", "XS", "S", "M", "L", "XL"])
            layout.addRow("Talle:", self.talle)
        else:
            self.talle = None

        boton = QPushButton("Guardar")
        boton.clicked.connect(self.guardar)
        layout.addRow(boton)
        self.setLayout(layout)

    def guardar(self):
        try:
            persona = {
                "dni": int(self.dni.text()),
                "nombre": self.nombre.text(),
                "edad": int(self.edad.text()),
                "talle": (self.talle.currentText().strip() if self.talle else None)
            }
            edad_minima = {"Palestra": 12, "Tirolesa": 8}.get(self.actividad, 0)
            if persona["edad"] < edad_minima:
                raise ValueError(f"La edad mínima para {self.actividad} es {edad_minima} años.")
            if self.requiere_talle and not persona["talle"]:
                raise ValueError(f"El talle es obligatorio para {self.actividad}.")
            self.persona_valida = persona
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ----------------------------------------
# Ventana principal mobile-friendly
# ----------------------------------------
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inscripción de Actividades")
        self.resize(600, 800)
        self.personas = []

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#134611"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#3E8914"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#E8FCCF"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#E8FCCF"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#96E072"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#134611"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow { background-color: #134611; color: #E8FCCF; }
            QLabel { color: #E8FCCF; font-size: 14px; }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #3E8914; color: #E8FCCF;
                border-radius: 8px; padding: 6px;
                border: 1px solid #96E072;
            }
            QListWidget {
                background-color: #3E8914; color: #E8FCCF;
                border-radius: 8px; padding: 6px;
                border: 1px solid #96E072;
            }
            QPushButton {
                background-color: #96E072; color: #134611;
                border: none; padding: 10px; border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E8FCCF; }
        """)

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        titulo = QLabel("Inscripción de Actividades")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        titulo.setStyleSheet("margin-bottom: 15px; color: #E8FCCF;")
        layout.addWidget(titulo)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.combo_actividad = QComboBox()
        self.combo_actividad.addItems(["Palestra", "Tirolesa", "Safari", "Jardinería"])
        self.fecha_input = QDateEdit(calendarPopup=True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("dd-MM-yyyy")
        self.configurar_calendario()
        self.hora_combo = QComboBox()
        self.hora_combo.addItems(self.generar_horarios())

        form_layout.addRow(QLabel("Actividad:"), self.combo_actividad)
        form_layout.addRow(QLabel("Fecha:"), self.fecha_input)
        form_layout.addRow(QLabel("Horario:"), self.hora_combo)
        layout.addLayout(form_layout)

        layout.addWidget(QLabel("Personas inscritas:"))
        self.lista_personas = QListWidget()
        layout.addWidget(self.lista_personas)

        botones_layout = QVBoxLayout()
        botones_layout.setSpacing(8)
        btn_agregar = QPushButton("Agregar Persona")
        btn_eliminar = QPushButton("Eliminar Persona")
        btn_inscribir = QPushButton("Inscribir")
        for btn in (btn_agregar, btn_eliminar, btn_inscribir):
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            botones_layout.addWidget(btn)
        layout.addLayout(botones_layout)

        btn_agregar.clicked.connect(self.agregar_persona)
        btn_eliminar.clicked.connect(self.eliminar_persona)
        btn_inscribir.clicked.connect(self.inscribir)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def configurar_calendario(self):
        calendario = self.fecha_input.calendarWidget()
        calendario.setGridVisible(True)
        calendario.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        calendario.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        paleta = QPalette()
        paleta.setColor(QPalette.ColorRole.Base, QColor("#3E8914"))
        paleta.setColor(QPalette.ColorRole.Window, QColor("#134611"))
        paleta.setColor(QPalette.ColorRole.Text, QColor("#E8FCCF"))
        paleta.setColor(QPalette.ColorRole.Highlight, QColor("#96E072"))
        paleta.setColor(QPalette.ColorRole.HighlightedText, QColor("#134611"))
        calendario.setPalette(paleta)

        formato_hoy = QTextCharFormat()
        formato_hoy.setForeground(QColor("#E8FCCF"))
        formato_hoy.setFontWeight(QFont.Weight.Bold)
        formato_hoy.setBackground(QColor("#3DA35D"))
        calendario.setDateTextFormat(QDate.currentDate(), formato_hoy)

    def generar_horarios(self):
        horarios = []
        hora, minuto = 9, 0
        while True:
            horarios.append(f"{hora:02d}:{minuto:02d}")
            if hora == 18 and minuto == 0:
                break
            minuto += 30
            if minuto >= 60:
                minuto = 0
                hora += 1
        return horarios

    def agregar_persona(self):
        actividad = self.combo_actividad.currentText()
        dialogo = DialogoPersona(actividad, self)
        if dialogo.exec():
            persona = dialogo.persona_valida
            if persona:
                self.personas.append(persona)
                texto_talle = f", talle {persona['talle']}" if persona['talle'] else ""
                self.lista_personas.addItem(
                    f"{persona['dni']} - {persona['nombre']} ({persona['edad']} años{texto_talle})"
                )

    def eliminar_persona(self):
        fila = self.lista_personas.currentRow()
        if fila >= 0:
            self.lista_personas.takeItem(fila)
            del self.personas[fila]
        else:
            QMessageBox.warning(self, "Advertencia", "Seleccione una persona para eliminar.")

    def inscribir(self):
        if not self.personas:
            QMessageBox.warning(self, "Atención", "Debe agregar al menos una persona antes de inscribirse.")
            return

        dialogo_terminos = TerminosDialog()
        if not dialogo_terminos.exec() or not dialogo_terminos.aceptado:
            QMessageBox.warning(self, "Atención", "Debe aceptar los términos y condiciones para continuar.")
            return

        try:
            mensaje = inscribir_actividad(
                self.combo_actividad.currentText(),
                self.fecha_input.date().toString("dd-MM-yyyy"),
                self.hora_combo.currentText(),
                self.personas,
                True
            )
            QMessageBox.information(self, "Éxito", "✅ " + mensaje)
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))


# ----------------------------------------
# MAIN
# ----------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    paleta = QPalette()
    paleta.setColor(QPalette.ColorRole.Window, QColor("#134611"))
    paleta.setColor(QPalette.ColorRole.Base, QColor("#3E8914"))
    paleta.setColor(QPalette.ColorRole.Text, QColor("#E8FCCF"))
    paleta.setColor(QPalette.ColorRole.WindowText, QColor("#E8FCCF"))
    paleta.setColor(QPalette.ColorRole.Button, QColor("#96E072"))
    paleta.setColor(QPalette.ColorRole.ButtonText, QColor("#134611"))
    paleta.setColor(QPalette.ColorRole.Highlight, QColor("#96E072"))
    paleta.setColor(QPalette.ColorRole.HighlightedText, QColor("#134611"))
    app.setPalette(paleta)

    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
