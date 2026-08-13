"""INTEGRANTE 2 — Top-Down · Nivel Medio (Lógica de Negocio)
================================================================

OBJETIVO
    Probar `app/order_service.py` creando Mocks/Stubs de la BD y de la pasarela
    de pagos con `unittest.mock.MagicMock`. Validar las REGLAS DE NEGOCIO:
        1. IVA (16 %) en el cálculo del total.
        2. Rechazo por stock insuficiente.
        3. Rechazo cuando la pasarela declina el pago.
        4. Que un pedido exitoso persista y descuente stock.

TÉCNICA
    - Estrategia: Top-Down. El servicio es "el de arriba"; la BD y la pasarela
      (lo de abajo) se sustituyen por MagicMock (stubs con valores fijos).
    - Herramienta: `unittest.mock.MagicMock`.

CLASE BAJO PRUEBA
    `app.order_service.OrderService(db, payment_gateway)`
"""

from unittest.mock import MagicMock

import pytest

from app.order_service import (
    OrderService,
    OutOfStockError,
    PaymentRejectedError,
)


def make_service(stock=10, price=100.0, approved=True, reason="declined"):
    """Helper: construye un OrderService con dependencias simuladas.

    Ajusta los parámetros para provocar cada escenario de negocio.
    """
    db = MagicMock()
    db.get_stock.return_value = stock
    db.get_price.return_value = price
    db.save_order.return_value = "ORD-TEST"

    gateway = MagicMock()
    gateway.charge.return_value = {
        "approved": approved,
        "transaction_id": "tx_1" if approved else None,
        "reason": reason,
    }
    return OrderService(db, gateway), db, gateway


# --- EJEMPLO RESUELTO: regla del IVA ---------------------------------------
def test_calculate_total_aplica_iva():
    """100.00 x 2 unidades + 16 % IVA = 232.00."""
    service, _, _ = make_service()
    total = service.calculate_total(unit_price=100.0, quantity=2)
    assert total == 232.0


# --- TODO INTEGRANTE 2 -----------------------------------------------------
# TODO 1: Cantidad inválida.
#   - `calculate_total(100.0, 0)` y `calculate_total(100.0, -1)` deben lanzar
#     `ValueError`. Usa `with pytest.raises(ValueError): ...`.
def test_calculate_total_cantidad_invalida():
    pytest.skip("TODO pendiente: completa este test (Integrante responsable).")


# TODO 2: Stock insuficiente.
#   - Configura el servicio con stock=1 y pide quantity=5.
#   - `place_order(...)` debe lanzar `OutOfStockError`.
#   - EXTRA: verifica que NUNCA se intentó cobrar
#     (`gateway.charge.assert_not_called()`).
def test_place_order_sin_stock():
    pytest.skip("TODO pendiente: completa este test (Integrante responsable).")


# TODO 3: Pago rechazado.
#   - Configura el servicio con approved=False.
#   - `place_order(...)` debe lanzar `PaymentRejectedError`.
#   - EXTRA: verifica que el pedido NO se guardó (`db.save_order.assert_not_called()`).
def test_place_order_pago_rechazado():
    pytest.skip("TODO pendiente: completa este test (Integrante responsable).")


# TODO 4: Camino feliz completo.
#   - approved=True, stock suficiente.
#   - Verifica que el resultado tiene status == "CONFIRMED" y el total con IVA.
#   - Verifica que se descontó el stock:
#     `db.update_stock` fue llamado con (product_id, stock - quantity).
def test_place_order_confirmado_descuenta_stock():
    pytest.skip("TODO pendiente: completa este test (Integrante responsable).")
