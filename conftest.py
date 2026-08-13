"""Configuración global de pruebas.

Garantiza que la raíz del proyecto esté en ``sys.path`` para poder importar el
paquete ``app`` desde cualquier archivo de ``tests/`` (tanto con pytest como
cuando mutmut ejecuta la suite).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
