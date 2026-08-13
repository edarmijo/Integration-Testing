"""INTEGRANTE 5 — Bottom-Up · Driver Integrador (End-to-End ascendente)
================================================================

OBJETIVO
    Unir las piezas construidas por los Integrantes 3 y 4 con la clase REAL
    `OrderService` para ejecutar un test de integración de abajo hacia arriba:

        [Fake DB en memoria]  +  [PaymentGateway real con HTTP simulado]
                              │
                              ▼
                    OrderService (código real)
                              │
                              ▼
                    Pedido confirmado End-to-End

    A diferencia de los Integrantes 1 y 2 (que mockean TODO), aquí solo se
    simulan las FRONTERAS del sistema (BD inexistente y red de pagos). La
    lógica de negocio se ejecuta de verdad.

TÉCNICA
    - Estrategia: Bottom-Up integrador.
    - Piezas: `FakeDb` (Integrante 3) + `requests-mock` (Integrante 4)
      + `OrderService` real.
"""

import pytest

from app.order_service import OrderService, PaymentRejectedError, OutOfStockError
from app.payment_gateway import PaymentGateway

# Reutilizamos el Fake construido por el Integrante 3.
from tests.bottom_up.test_db_driver import FakeDb


PAY_URL = "https://pagos.test/api/v1/charges"


@pytest.fixture
def integrated_service():
    """Ensambla el sistema real con sus fronteras simuladas."""
    db = FakeDb(stock={"SKU-1": 10}, prices={"SKU-1": 100.0})
    gateway = PaymentGateway(base_url="https://pagos.test/api/v1")
    service = OrderService(db, gateway)
    return service, db


# --- EJEMPLO RESUELTO: pedido feliz de extremo a extremo -------------------
def test_pedido_end_to_end_confirmado(requests_mock, integrated_service):
    service, db = integrated_service
    requests_mock.post(PAY_URL, status_code=200, json={"transaction_id": "tx_1"})

    resultado = service.place_order("SKU-1", 2, "tok_visa")

    # 1) La lógica de negocio calculó el total con IVA (100 x 2 x 1.16).
    assert resultado["total"] == 232.0
    assert resultado["status"] == "CONFIRMED"
    # 2) El estado del Fake cambió de verdad: el stock bajó de 10 a 8.
    assert db.get_stock("SKU-1") == 8
    # 3) El pedido quedó persistido en la BD en memoria.
    assert resultado["order_id"] in db.orders


# --- TODO INTEGRANTE 5 -----------------------------------------------------
# TODO 1: Pago rechazado NO altera el estado.
#   - Simula un 402 en `PAY_URL`.
#   - Verifica que `place_order(...)` lanza `PaymentRejectedError`.
#   - CLAVE de integración: el stock NO debe haber bajado y NO debe existir
#     ningún pedido guardado (`db.orders == {}`).
def test_pedido_rechazado_no_cambia_estado(requests_mock, integrated_service):
    service, db = integrated_service
    requests_mock.post(PAY_URL, status_code=402, json={"reason": "insufficient_funds"})
    
    with pytest.raises(PaymentRejectedError):
        service.place_order("SKU-1", 2, "tok_visa")
    
    assert db.get_stock("SKU-1") == 10
    assert db.orders == {}


# TODO 2: Sin stock nunca se llega a la red.
#   - Pide una cantidad mayor al stock disponible (p. ej. 999).
#   - Verifica que se lanza `OutOfStockError` y que NO se registró ninguna
#     petición HTTP (`requests_mock.call_count == 0`).
def test_pedido_sin_stock_no_llama_pasarela(requests_mock, integrated_service):
    service, db = integrated_service
    
    with pytest.raises(OutOfStockError):
        service.place_order("SKU-1", 999, "tok_visa")

    assert requests_mock.call_count == 0


# TODO 3: Dos pedidos consecutivos descuentan stock de forma acumulada.
#   - Simula 200 OK. Haz dos pedidos de 3 unidades cada uno.
#   - Verifica que el stock final es 10 - 3 - 3 = 4 y que hay 2 pedidos guardados.
def test_dos_pedidos_descuentan_stock_acumulado(requests_mock, integrated_service):
    service, db = integrated_service
    requests_mock.post(PAY_URL, status_code=200, json={"transaction_id": "tx_1"})
    service.place_order("SKU-1", 3, "tok_visa")
    service.place_order("SKU-1", 3, "tok_visa")

    assert db.get_stock("SKU-1") == 4
    assert len(db.orders) == 2
