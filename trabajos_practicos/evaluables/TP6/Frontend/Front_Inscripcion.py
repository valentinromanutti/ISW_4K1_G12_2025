import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QCheckBox,
    QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget,
    QMessageBox, QDialog, QFormLayout, QDateEdit, QCalendarWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QPalette


# ----------------------------------------
# FUNCIÓN LÓGICA DE INSCRIPCIÓN (validaciones)
# ----------------------------------------
def inscribir_actividad(actividad, fecha_actividad, horario_actividad, personas, acepta_terminos_condiciones):
    if not acepta_terminos_condiciones:
        raise ValueError("Se deben aceptar los terminos y condiciones")

    try:
        fecha_actividad_dt = datetime.strptime(fecha_actividad, "%d-%m-%Y")
        fecha_actual_dt = datetime.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y")
    except Exception:
        raise ValueError("Formato de fecha inválido")
    
    if fecha_actividad_dt.day == 25 and fecha_actividad_dt.month == 12:
        raise ValueError("No se permiten inscripciones en Navidad.")
    if fecha_actividad_dt.day == 1 and fecha_actividad_dt.month == 1:
        raise ValueError("No se permiten inscripciones en Año Nuevo.")

    if fecha_actividad_dt < fecha_actual_dt:
        raise ValueError("No se puede inscribir a actividades ya realizadas")

    if fecha_actividad_dt > fecha_actual_dt + timedelta(days=2):
        raise ValueError("No se puede inscribir con mas de dos dias de anticipacion")

    if fecha_actividad_dt.weekday() == 0:
        raise ValueError("No se permiten inscripciones los lunes.")

    

    try:
        hora, minuto = map(int, horario_actividad.split(":"))
    except ValueError:
        raise ValueError("Formato de hora inválido")

    if hora < 9 or (hora > 18 or (hora == 18 and minuto > 30)):
        raise ValueError("El parque está cerrado en ese horario.")

    if minuto not in (0, 30):
        raise ValueError("No hay horario para esa actividad.")

    if not personas or len(personas) == 0:
        raise ValueError("Debe inscribir al menos una persona.")

    for persona in personas:
        edad_minima = {"Palestra": 12, "Tirolesa": 8}.get(actividad, 0)
        if persona["edad"] < edad_minima:
            raise ValueError(f"La edad mínima para {actividad} es {edad_minima} años.")
        if actividad in ["Palestra", "Tirolesa"] and not persona.get("talle"):
            raise ValueError(f"El talle es obligatorio para la actividad {actividad}.")

    return "Inscripción realizada correctamente."


# ----------------------------------------
# Diálogo de Términos y Condiciones
# ----------------------------------------
class TerminosDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Términos y Condiciones de Participación")
        self.setMinimumSize(700, 550)
        self.aceptado = False

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        texto = QTextEdit()
        texto.setReadOnly(True)
        texto.setStyleSheet("""
            QTextEdit {
                background-color: #2B2D42;
                color: #FFFFFF;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }
        """)

        texto.setText("""Términos y Condiciones de Participación en Actividades

Al inscribirte en una actividad del parque, confirmás que comprendés y aceptás los siguientes términos y condiciones de participación.

La inscripción será válida únicamente para las actividades habilitadas dentro del listado oficial del parque, que incluye Tirolesa, Safari, Palestra y Jardinería. Cada una de ellas cuenta con cupos limitados por horario, por lo que la reserva quedará confirmada solamente si existen lugares disponibles al momento de realizar la inscripción. No se podrán realizar cambios de horario una vez confirmada la participación.

Durante el proceso de inscripción deberás ingresar correctamente los datos personales de cada participante, incluyendo nombre completo, DNI, edad y, en caso de que la actividad lo requiera, la talla de vestimenta correspondiente. Es responsabilidad del visitante proporcionar información veraz y actualizada, ya que la organización no se hará responsable por errores o inconvenientes ocasionados por datos incorrectos.

Algunas actividades pueden requerir equipamiento o vestimenta específica, como cascos, arneses o indumentaria especial. En esos casos, el participante deberá respetar las indicaciones del personal del parque y cumplir con todos los requisitos de seguridad. La falta de cumplimiento podrá impedir la participación en la actividad, sin derecho a reembolso o compensación.

El visitante declara encontrarse en condiciones físicas y mentales aptas para realizar la actividad elegida. Los menores de edad deberán estar acompañados por un adulto responsable en todo momento. La organización se reserva el derecho de admisión y permanencia, pudiendo negar o interrumpir la participación en caso de incumplimiento de las normas o por motivos de seguridad.

En situaciones de condiciones climáticas adversas, razones operativas o fuerza mayor, el parque podrá suspender o reprogramar la actividad sin previo aviso. En caso de reprogramación, se notificará a los participantes utilizando los medios de contacto proporcionados al momento de la inscripción.

Al confirmar tu inscripción, manifestás haber leído y comprendido estos términos y condiciones, y aceptás participar bajo tu propia responsabilidad, respetando las indicaciones del personal y las normas del parque.
""")

        self.checkbox = QCheckBox("He leído y acepto los términos y condiciones")
        self.checkbox.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold;")

        botones_layout = QHBoxLayout()
        self.boton_aceptar = QPushButton("Aceptar")
        self.boton_aceptar.setEnabled(False)
        self.boton_cancelar = QPushButton("Cancelar")

        self.boton_aceptar.setStyleSheet("background-color: #00ADB5; color: #FFFFFF; border-radius: 6px; padding: 8px 16px; font-weight: bold;")
        self.boton_cancelar.setStyleSheet("background-color: #393E46; color: #FFFFFF; border-radius: 6px; padding: 8px 16px;")

        self.checkbox.stateChanged.connect(lambda s: self.boton_aceptar.setEnabled(bool(s)))
        self.boton_aceptar.clicked.connect(self.confirmar)
        self.boton_cancelar.clicked.connect(self.reject)

        botones_layout.addStretch()
        botones_layout.addWidget(self.boton_cancelar)
        botones_layout.addWidget(self.boton_aceptar)

        layout.addWidget(texto)
        layout.addWidget(self.checkbox)
        layout.addLayout(botones_layout)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #222831; color: #FFFFFF;")

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
            QDialog { background-color: #222831; color: #FFFFFF; }
            QLineEdit, QComboBox {
                background-color: #393E46; color: #FFFFFF;
                border: 1px solid #00ADB5; border-radius: 6px; padding: 6px;
            }
            QPushButton {
                background-color: #00ADB5; color: #FFFFFF;
                border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #06C1CB; }
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
                "talle": self.talle.currentText().strip() if self.talle else None
            }

            edad_minima = {"Palestra": 12, "Tirolesa": 8}.get(self.actividad, 0)
            if persona["edad"] < edad_minima:
                raise ValueError(f"La edad mínima para {self.actividad} es {edad_minima} años.")

            if self.requiere_talle and not persona["talle"]:
                raise ValueError(f"El talle es obligatorio para la actividad {self.actividad}.")

            self.persona_valida = persona
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ----------------------------------------
# Ventana principal
# ----------------------------------------
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inscripción de Actividades")
        self.setMinimumSize(900, 650)
        self.personas = []

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#2B2D42"))
        palette.setColor(QPalette.ColorRole.Window, QColor("#1E1E2E"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow { background-color: #1E1E2E; color: #FFFFFF; }
            QLabel { color: #FFFFFF; font-size: 14px; }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #2B2D42; color: #FFFFFF; border-radius: 8px;
                padding: 6px; border: 1px solid #00ADB5;
            }
            QListWidget {
                background-color: #2B2D42; color: #FFFFFF; border-radius: 8px;
                padding: 6px; border: 1px solid #00ADB5;
            }
            QPushButton {
                background-color: #00ADB5; color: #FFFFFF; border: none;
                padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #06C1CB; }
            QMessageBox { background-color: #2B2D42; color: #FFFFFF; }
        """)

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)

        titulo = QLabel("Inscripción de Actividades")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(titulo)

        form_layout = QHBoxLayout()
        self.combo_actividad = QComboBox()
        self.combo_actividad.addItems(["Palestra", "Tirolesa", "Safari", "Jardinería"])

        self.fecha_input = QDateEdit(calendarPopup=True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("dd-MM-yyyy")
        self.configurar_calendario()

        self.hora_combo = QComboBox()
        self.hora_combo.addItems(self.generar_horarios())

        form_layout.addWidget(QLabel("Actividad:"))
        form_layout.addWidget(self.combo_actividad)
        form_layout.addWidget(QLabel("Fecha:"))
        form_layout.addWidget(self.fecha_input)
        form_layout.addWidget(QLabel("Horario:"))
        form_layout.addWidget(self.hora_combo)
        layout.addLayout(form_layout)

        layout.addWidget(QLabel("Personas inscritas:"))
        self.lista_personas = QListWidget()
        layout.addWidget(self.lista_personas)

        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar Persona")
        btn_eliminar = QPushButton("Eliminar Persona")
        btn_inscribir = QPushButton("Inscribir")
        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addWidget(btn_inscribir)
        layout.addLayout(botones_layout)

        btn_agregar.clicked.connect(self.agregar_persona)
        btn_eliminar.clicked.connect(self.eliminar_persona)
        btn_inscribir.clicked.connect(self.inscribir)

        central.setLayout(layout)
        self.setCentralWidget(central)

    # ----------------------------------------
    def configurar_calendario(self):
        calendario: QCalendarWidget = self.fecha_input.calendarWidget()
        calendario.setGridVisible(True)
        calendario.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        calendario.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        paleta = QPalette()
        paleta.setColor(QPalette.ColorRole.Base, QColor("#1E1E2E"))
        paleta.setColor(QPalette.ColorRole.Window, QColor("#1E1E2E"))
        paleta.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
        paleta.setColor(QPalette.ColorRole.Highlight, QColor("#00ADB5"))
        paleta.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        calendario.setPalette(paleta)

        calendario.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #1E1E2E;
                color: #FFFFFF;
                selection-background-color: #00ADB5;
                selection-color: black;
                font-weight: 500;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #1E1E2E;
                color: #FFFFFF;
            }
            QCalendarWidget QToolButton {
                background-color: #00ADB5;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #06C1CB;
            }
        """)

        formato_uniforme = QTextCharFormat()
        formato_uniforme.setForeground(QColor("#FFFFFF"))
        for dia in range(1, 8):
            calendario.setWeekdayTextFormat(Qt.DayOfWeek(dia), formato_uniforme)

        formato_hoy = QTextCharFormat()
        formato_hoy.setForeground(QColor("#00FFFF"))
        formato_hoy.setFontWeight(QFont.Weight.Bold)
        formato_hoy.setBackground(QColor("#2B2D42"))
        calendario.setDateTextFormat(QDate.currentDate(), formato_hoy)

    # ----------------------------------------
    def generar_horarios(self):
        horarios = []
        hora, minuto = 9, 0
        while hora < 19:
            horarios.append(f"{hora:02d}:{minuto:02d}")
            minuto += 30
            if minuto >= 60:
                minuto = 0
                hora += 1
        if horarios and horarios[-1] == "19:00":
            horarios.pop()
        return horarios

    # ----------------------------------------
    def agregar_persona(self):
        actividad = self.combo_actividad.currentText()
        dialogo = DialogoPersona(actividad, self)
        if dialogo.exec():
            persona = dialogo.persona_valida
            if persona:
                self.personas.append(persona)
                self.lista_personas.addItem(
                    f"{persona['dni']} - {persona['nombre']} ({persona['edad']} años"
                    + (f", talle {persona['talle']}" if persona['talle'] else "") + ")"
                )

    def eliminar_persona(self):
        fila = self.lista_personas.currentRow()
        if fila >= 0:
            self.lista_personas.takeItem(fila)
            del self.personas[fila]
        else:
            QMessageBox.warning(self, "Advertencia", "Seleccione una persona para eliminar.")

    # ----------------------------------------
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
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
