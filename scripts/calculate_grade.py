#!/usr/bin/env python3
"""Autoevaluación del taller de Integration Testing.

Calcula una nota de 0 a 100 en dos pasos y la escribe como tabla Markdown en
``$GITHUB_STEP_SUMMARY`` (o por consola si se ejecuta localmente):

    1. PyTest Execution  (20 %): proporción de pruebas del equipo que pasan
       sobre el código SANO (sin mutar).
    2. Mutation Testing  (80 %): proporción de mutantes "asesinados" (killed)
       por las pruebas del equipo, usando mutmut.

Uso:
    python scripts/calculate_grade.py

El script NUNCA aborta la ejecución del workflow: ante cualquier fallo de una
herramienta, otorga 0 puntos en ese apartado y continúa.
"""

from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# --- Pesos de la nota final -------------------------------------------------
PYTEST_WEIGHT = 20.0
MUTATION_WEIGHT = 80.0

# --- Curva con meta para la nota de mutación --------------------------------
# El 100 % de mutantes asesinados es casi inalcanzable (mensajes de error,
# mutantes equivalentes, etc.). En vez de exigir el 100 %, fijamos una META
# realista: matar este porcentaje de mutantes (o más) otorga el 80 % completo.
# Por debajo de la meta, los puntos se reparten en proporción.
#
#   Ejemplos con MUTATION_TARGET = 0.55:
#     - killed 55 % o más -> 80.00 / 80  (meta alcanzada = puntaje completo)
#     - killed 44 %        -> 80 × (0.44 / 0.55) = 64.00 / 80
#     - killed 27.5 %      -> 80 × (0.275 / 0.55) = 40.00 / 80
#
# Con 0.55, un taller COMPLETO (~56 % de mutantes) ya llega al 80/80 (nota 100),
# lo cual es justo cuando no se enseñó mutation testing: hacer todo = nota top.
# Sube la meta (p. ej. 0.70) para exigir más si vas a explicar la técnica.
MUTATION_TARGET = 0.55

ROOT = Path(__file__).resolve().parent.parent
PYTEST_REPORT = ROOT / "pytest-report.xml"
MUTMUT_REPORT = ROOT / "mutmut-report.xml"


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Ejecuta un comando capturando salida, sin lanzar excepción por exit-code."""
    print(f"\n$ {' '.join(cmd)}", flush=True)
    # Forzamos UTF-8 en el proceso hijo y al decodificar su salida para que los
    # emojis del reporte de mutmut no rompan en consolas no-UTF8 (Windows cp1252).
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    result = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=env,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


# ---------------------------------------------------------------------------
# Paso 1 — PyTest sobre el código sano.
# ---------------------------------------------------------------------------
def run_pytest() -> tuple[float, int, int]:
    """Devuelve (puntos_sobre_20, pruebas_pasadas, pruebas_totales)."""
    _run([
        sys.executable, "-m", "pytest",
        f"--junitxml={PYTEST_REPORT}",
        "-q",
    ])

    if not PYTEST_REPORT.exists():
        print("No se generó el reporte de pytest; 0 puntos en este apartado.")
        return 0.0, 0, 0

    tree = ET.parse(PYTEST_REPORT)
    root = tree.getroot()

    total = failures = errors = skipped = 0
    # El reporte puede ser <testsuites> con varios <testsuite> o uno solo.
    suites = root.findall("testsuite") or [root]
    for suite in suites:
        total += int(suite.get("tests", 0))
        failures += int(suite.get("failures", 0))
        errors += int(suite.get("errors", 0))
        skipped += int(suite.get("skipped", 0))

    # Los tests aún NO implementados se marcan con pytest.skip(...) en las
    # plantillas. Cuentan como PENDIENTES: entran en el denominador pero no
    # suman puntos. Así el 20 % crece a medida que el equipo completa sus TODOs
    # y, al mismo tiempo, la suite sigue en verde para que mutmut no aborte.
    if total <= 0:
        print("No se encontraron pruebas; 0 puntos en este apartado.")
        return 0.0, 0, 0

    passed = total - failures - errors - skipped
    points = PYTEST_WEIGHT * passed / total
    return round(points, 2), passed, total


# ---------------------------------------------------------------------------
# Paso 2 — Mutation Testing con mutmut.
# ---------------------------------------------------------------------------
def run_mutation() -> tuple[float, int, int]:
    """Devuelve (puntos_sobre_80, mutantes_asesinados, mutantes_totales)."""
    # mutmut devuelve un exit-code distinto de 0 cuando sobreviven mutantes;
    # eso es información, no un fallo del script -> ignoramos el returncode.
    _run([sys.executable, "-m", "mutmut", "run"])

    junit = _run([sys.executable, "-m", "mutmut", "junitxml"])
    MUTMUT_REPORT.write_text(junit.stdout, encoding="utf-8")

    if not junit.stdout.strip():
        print("mutmut no produjo reporte; 0 puntos en este apartado.")
        return 0.0, 0, 0

    try:
        root = ET.fromstring(junit.stdout)
    except ET.ParseError as exc:
        print(f"No se pudo parsear el reporte de mutmut: {exc}")
        return 0.0, 0, 0

    # En el JUnit XML de mutmut cada <testcase> es un mutante.
    # Un mutante SOBREVIVIENTE aparece con un hijo <failure>.
    # Un mutante ASESINADO (killed) aparece como testcase que pasa.
    testcases = root.findall(".//testcase")
    total = len(testcases)
    if total == 0:
        print("mutmut no generó mutantes; 0 puntos en este apartado.")
        return 0.0, 0, 0

    survived = sum(1 for tc in testcases if tc.find("failure") is not None)
    killed = total - survived

    # Curva con meta: alcanzar MUTATION_TARGET (o más) da el 80 % completo;
    # por debajo se reparte en proporción a la meta (nunca más de 1.0).
    kill_ratio = killed / total
    curved = min(1.0, kill_ratio / MUTATION_TARGET) if MUTATION_TARGET > 0 else 1.0
    points = MUTATION_WEIGHT * curved
    return round(points, 2), killed, total


# ---------------------------------------------------------------------------
# Reporte final -> $GITHUB_STEP_SUMMARY
# ---------------------------------------------------------------------------
def write_summary(markdown: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(markdown + "\n")
    print("\n" + markdown)


def build_markdown(
    pytest_points: float,
    passed: int,
    total_tests: int,
    mutation_points: float,
    killed: int,
    total_mutants: int,
    final: float,
) -> str:
    mut_pct = (100 * killed / total_mutants) if total_mutants else 0
    test_pct = (100 * passed / total_tests) if total_tests else 0
    return "\n".join([
        "## 🧪 Resultado de la Autoevaluación — OrderSystem",
        "",
        "| Paso | Métrica | Detalle | Puntos |",
        "| --- | --- | --- | --- |",
        f"| 1. PyTest Execution | {test_pct:.1f} % pruebas OK | "
        f"{passed}/{total_tests} pruebas pasan | **{pytest_points:.2f} / {PYTEST_WEIGHT:.0f}** |",
        f"| 2. Mutation Testing | {mut_pct:.1f} % mutantes 💀 (meta {MUTATION_TARGET*100:.0f} %) | "
        f"{killed}/{total_mutants} mutantes asesinados | **{mutation_points:.2f} / {MUTATION_WEIGHT:.0f}** |",
        "",
        f"### 🏆 NOTA FINAL: **{final:.2f} / 100**",
        "",
        f"> _La nota de mutación usa una **meta del {MUTATION_TARGET*100:.0f} %**: "
        f"matar ese porcentaje de mutantes (o más) otorga el puntaje completo. "
        "Se recalcula en cada push a `main`._",
    ])


def main() -> int:
    print("=" * 60)
    print(" AUTOEVALUACIÓN - Taller de Integration Testing ")
    print("=" * 60)

    pytest_points, passed, total_tests = run_pytest()
    mutation_points, killed, total_mutants = run_mutation()

    final = round(pytest_points + mutation_points, 2)

    markdown = build_markdown(
        pytest_points, passed, total_tests,
        mutation_points, killed, total_mutants,
        final,
    )
    write_summary(markdown)

    # El workflow SIEMPRE termina en verde: la nota es el resultado, no un fallo.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
