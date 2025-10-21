# Guía de Estilo de Código Python

## 1. Introducción

**Propósito:** Asegurar que todo el código fuente del proyecto sea consistente, legible y mantenible, independientemente de quién lo escriba.

**Alcance:** Esta guía se aplica a **todo el código Python** del proyecto. Específicamente, a los archivos: `inscripcion_actividad.py`, `test_inscripcion_actividades.py`, `app_fastapi.py`, y `front_inscripcion.py`.

***

## 2. Estándar Base: PEP 8

El estándar de estilo de este proyecto se basa directamente en el documento canónico de la comunidad Python.

**Documento Oficial PEP 8:** [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)

***

## 3. Reglas Clave de PEP 8

Las siguientes reglas son mandatorias y se aplicarán mediante herramientas de automatización.

| Regla | Descripción | Ejemplo Correcto |
| :--- | :--- | :--- |
| **Longitud de Línea** | Limitar todas las líneas a un máximo de **79 caracteres**. | `if a == b and c == d:` |
| **Indentación** | Usar **4 espacios** por nivel. **No usar tabuladores**. | `def funcion():` <br> `    pass` |
| **Líneas en Blanco** | Usar **2 líneas** para separar funciones y clases de nivel superior. Usar **1 línea** para separar métodos dentro de una clase. | *(Separación visual clara)* |
| **Espacios en Operadores** | Usar un espacio alrededor de operadores binarios. | `x = 1 + y` (no `x=1+y`) |
| **Espacios en Comas** | Usar un espacio después de las comas en listas, tuplas, etc. | `mi_lista = [1, 2, 3]` (no `[1,2,3]`) |
| **Espacios en Paréntesis** | No usar espacios pegados a paréntesis o corchetes. | `print(variable)` (no `print ( variable )`) |
| **Convenciones de Nombres** | Usar **`lower_case_with_underscores`** para variables, funciones,métodos y archivos. | `mi_variable`, `calcular_impuesto()` |

### Agrupación y Orden de Importaciones

Las sentencias `import` deben estar **siempre en la parte superior del archivo** y agrupadas en el siguiente orden, separadas por una línea en blanco:

1.  **Librerías estándar** de Python (`import os`).
2.  **Librerías de terceros** (`import requests`).
3.  **Librerías locales** del proyecto (`from . import mi_modulo`).

***

## 4. Política de Excepciones

Para asegurar la **máxima consistencia y legibilidad**, este proyecto se adhiere de manera **estricta** al estándar de estilo **PEP 8**.

* **No se permiten excepciones** a ninguna de las reglas definidas en el documento oficial.
* Todo el código debe superar la validación de herramientas de *linting* (como `flake8`) sin requerir la configuración de advertencias o reglas a ignorar.

**Única Desviación Permitida (Comentarios):**

* El equipo tiene libertad para gestionar el estilo y la densidad de los **comentarios internos** (`#`) según lo consideren necesario para una mejor documentación del código, sin que esto afecte la configuración del *linter*.

***

## 5. Reglas Adicionales del Equipo

### Nomenclatura para los Tests

Los *tests* deben seguir una convención estricta para identificar claramente su propósito y resultado esperado:

* **Formato:** `test_nombre_pasa` o `test_nombre_falla`.
* **Regla:** Todos los *tests* deben comenzar con la palabra clave **`test_`**.
* **Representatividad:** El nombre debe ser representativo de la funcionalidad que se está probando.
* **Resultado Esperado:** Finalizar con `_pasa` o `_falla` para indicar el resultado esperado.

**Ejemplos:** `test_usuario_registrado_pasa()`, `test_usuario_sin_credenciales_falla()`.

### Estructura del Repositorio

La estructura del repositorio debe ser la siguiente:
- .idea/
    - inspectionProfiles/
- .pytest_cache/
    - v/
        - cache/
- data/
- database/
- frontend/
- src/
    - __pycache__/
- test/
    - __pycache__/


| Directorio | Propósito |
| :--- | :--- |
| **`data`** | Contendrá todo el código relacionado con la **base de datos** y acceso a datos. |
| **`database`** | Contendrá la **base de datos**. |
| **`frontend`** | Contendrá todo el código relacionado con la **interfaz de usuario** (frontend). |
| **`source`** | Contendrá todo el código relacionado con la **lógica de negocio** del sistema. |
| **`test`** | Contendrá todo el código relacionado con las **pruebas** unitarias e integración. |

Los archivos principales de la API (`app_fastapi.py`) y el **documento de estilos** (`documentos_de_estilos_de_codigo.py`) deben ubicarse en la **raíz** del directorio.

***

## 6. Herramientas de Automatización

Para hacer cumplir la guía de estilos PEP 8, utilizaremos las siguientes herramientas en el *workflow* de desarrollo:

* **Linter (`Flake8`):** Actúa como el "detector". Analiza el código y notifica cuando no se cumplen las reglas de PEP 8.
* **Formateador (`autopep8`):** Actúa como el "corrector". Reescribe automáticamente el código para que cumpla con las reglas.

***

## 7. Criterio de Validación del Proyecto

El proyecto pasará exitosamente la validación del documento de estilos de código solo cuando se cumplan **ambas** condiciones:

1.  Pasa la validación de la herramienta **`flake8`** (sin ignorar advertencias).
2.  Cumple con todas las **Reglas Adicionales del Equipo** definidas en la Sección 5.