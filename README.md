# Taller de Integration Testing — OrderSystem

Bienvenidos al taller práctico de **Pruebas de Integración en Python**. Trabajarán
en **equipos de 5** aplicando las estrategias **Top-Down** y **Bottom-Up** sobre un
sistema de procesamiento de pedidos por capas. Su nota (0–100) se calcula
**automáticamente** con GitHub Actions.

---

## EMPIEZA AQUÍ (lo primero que debe hacer el equipo)

> **No hagas _Fork_ ni clones este repositorio directamente.** Sigue estos pasos.

**Paso 1 — UN solo integrante** crea el repositorio del equipo con el botón verde
**"Use this template" → "Create a new repository"**:

![Botón Use this template](docs/usar-plantilla.png)

**Paso 2 —** ese integrante agrega a los otros 4 como colaboradores:
`Settings → Collaborators → Add people`.

**Paso 3 — los 5 integrantes** clonan el repositorio **del equipo** (no este):
usen el botón **"Code" → HTTPS** para copiar la URL y luego:

```bash
git clone https://github.com/EL-EQUIPO/su-repo-del-equipo.git
```

---

## Contexto del sistema

`OrderSystem` está dividido en 4 capas:

| Capa | Módulo | Responsabilidad | ¿Existe hoy? |
| :--: | ------ | --------------- | ------------ |
| 1 | `app/cli.py` | Interfaz de línea de comandos (UI) | Sí |
| 2 | `app/order_service.py` | Lógica de negocio (IVA, stock, pagos) | Sí |
| 3 | `app/payment_gateway.py` | Pasarela de pagos externa (HTTP) | **No desplegada** |
| 4 | `app/db_connector.py` | Persistencia / Base de datos | **No desplegada** |

> **Premisa clave:** la base de datos (Capa 4) y la API de pagos (Capa 3)
> **aún no existen**. Sus métodos lanzan errores de conexión si se ejecutan
> directamente. Deben probar la integración del sistema **antes** de que la
> infraestructura real esté disponible, usando dobles de prueba (mocks, stubs,
> fakes e interceptores HTTP).

**Top-Down** empieza por las capas altas y simula las bajas.
**Bottom-Up** construye y prueba primero las capas base y va integrando hacia arriba.

---

## Asignación de roles (cada quien trabaja en UN archivo)

| # | Rol | Archivo a completar | Estrategia | Herramienta clave |
| :-: | --- | ------------------- | ---------- | ----------------- |
| 1 | Top-Down · Nivel Superior | `tests/top_down/test_cli.py` | Top-Down | `pytest-mock` (`mocker.patch`) |
| 2 | Top-Down · Nivel Medio | `tests/top_down/test_service.py` | Top-Down | `unittest.mock.MagicMock` |
| 3 | Bottom-Up · Persistencia | `tests/bottom_up/test_db_driver.py` | Bottom-Up | `pytest.fixture` (Fake en memoria) |
| 4 | Bottom-Up · Red/Pagos | `tests/bottom_up/test_payment_driver.py` | Bottom-Up | `requests-mock` |
| 5 | Bottom-Up · Driver Integrador | `tests/bottom_up/test_full_integration.py` | Bottom-Up E2E | Fake (3) + requests-mock (4) + `OrderService` real |

Cada archivo trae un **ejemplo resuelto** y una lista de **`# TODO`** que deben completar.
El Integrante 5 **reutiliza** el `FakeDb` del Integrante 3 y la técnica del Integrante 4.

---

## Estructura del proyecto

```
.
├── app/
│   ├── __init__.py
│   ├── cli.py                 # Capa 1
│   ├── order_service.py       # Capa 2
│   ├── payment_gateway.py     # Capa 3 (no desplegada)
│   └── db_connector.py        # Capa 4 (no desplegada)
├── tests/
│   ├── top_down/
│   │   ├── test_cli.py            # Integrante 1
│   │   └── test_service.py        # Integrante 2
│   └── bottom_up/
│       ├── test_db_driver.py      # Integrante 3
│       ├── test_payment_driver.py # Integrante 4
│       └── test_full_integration.py # Integrante 5
├── scripts/
│   └── calculate_grade.py     # Motor de autoevaluación (0–100)
├── .github/workflows/
│   └── autograding.yml        # Ejecuta la nota en cada push a main
├── requirements.txt
├── setup.cfg                  # Configuración de mutmut
├── pytest.ini
└── conftest.py
```

---

## Puesta en marcha (local)

Requisito: **Python 3.11+**.

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ejecutar **todas** las pruebas:

```bash
pytest -v
```

Ejecutar **solo tu archivo** mientras trabajas:

```bash
pytest tests/top_down/test_cli.py -v
```

Ver los **`print(...)`** de tu código y tus tests (pytest los oculta por defecto):

```bash
pytest tests/top_down/test_cli.py -v -s
```

---

## Nota y dónde verla

En cada `push` a `main`, GitHub Actions califica solo (0–100):

- **PyTest — 20 %:** proporción de las pruebas del equipo que pasan.
- **Mutation Testing — 80 %:** el sistema "rompe" el código de `app/` en muchos cambios pequeños; cada test que **detecta** un cambio suma. Con detectar el **55 % o más** se obtiene el puntaje completo.

Miren su nota en **Actions → última ejecución → Summary**. Se recalcula en cada push.

---

## Reglas de trabajo

- Cada quien trabaja en **su archivo** de `tests/`; hagan commits pequeños y frecuentes.
- Corran `pytest` en local antes de subir.
- **No modifiquen `app/`.** Su trabajo es escribir **pruebas**; cambiar el código
  de la aplicación para "subir la nota" invalida el ejercicio.
