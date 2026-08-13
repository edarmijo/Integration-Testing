"""Capa 1 - Interfaz de Línea de Comandos (CLI).

Es la capa más externa. Su única responsabilidad es:
    - Recibir los datos del pedido.
    - Delegar TODO el trabajo en ``OrderService``.
    - Traducir el resultado (o las excepciones) a mensajes de texto.

El Integrante 1 probará esta capa mockeando por completo ``OrderService``
(estrategia Top-Down): a la CLI no le importa CÓMO se procesa el pedido, solo
que llama al servicio y formatea correctamente la respuesta y los errores.
"""

import argparse

from app.db_connector import DbConnector
from app.order_service import (
    OrderService,
    OutOfStockError,
    PaymentRejectedError,
)
from app.payment_gateway import PaymentGateway


def build_service() -> OrderService:
    """Construye un ``OrderService`` con las dependencias reales.

    En el entorno de desarrollo esto usa una BD y una pasarela que NO existen,
    por eso en las pruebas se inyecta un servicio simulado en su lugar.
    """
    return OrderService(DbConnector(), PaymentGateway())


def run_order(service: OrderService, product_id: str, quantity: int, card_token: str) -> str:
    """Ejecuta un pedido a través de ``service`` y devuelve un mensaje de texto.

    Contrato de salida (lo que el Integrante 1 debe verificar):
        - Éxito:            "OK: pedido <id> confirmado, total=<total>"
        - Sin stock:        "ERROR: sin stock (<detalle>)"
        - Pago rechazado:   "ERROR: pago rechazado (<detalle>)"
        - Cualquier otro:   "ERROR: inesperado (<detalle>)"
    """
    try:
        result = service.place_order(product_id, quantity, card_token)
    except OutOfStockError as exc:
        return f"ERROR: sin stock ({exc})"
    except PaymentRejectedError as exc:
        return f"ERROR: pago rechazado ({exc})"
    except Exception as exc:  # noqa: BLE001 - la CLI nunca debe reventar.
        return f"ERROR: inesperado ({exc})"

    return f"OK: pedido {result['order_id']} confirmado, total={result['total']}"


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de la CLI. Devuelve el código de salida del proceso."""
    parser = argparse.ArgumentParser(description="OrderSystem CLI")
    parser.add_argument("product_id", help="Identificador del producto")
    parser.add_argument("quantity", type=int, help="Cantidad a pedir")
    parser.add_argument("card_token", help="Token de la tarjeta de pago")
    args = parser.parse_args(argv)

    service = build_service()
    message = run_order(service, args.product_id, args.quantity, args.card_token)

    print(message)
    return 0 if message.startswith("OK:") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
