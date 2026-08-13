"""Capa 2 - Lógica de Negocio (OrderService).

Esta es la capa central del sistema. NO habla directamente con la red ni con
la base de datos: recibe sus dependencias por INYECCIÓN (un conector de BD y
una pasarela de pagos). Gracias a esto se puede probar con Mocks/Stubs/Fakes.

Reglas de negocio implementadas:
    1. IVA: el total = subtotal + IVA (16 %).
    2. Stock: no se puede pedir más cantidad de la disponible.
    3. Cantidad: debe ser un entero positivo.
    4. Pagos: si la pasarela rechaza el pago, el pedido NO se persiste.
"""

# Tasa de IVA aplicada a todos los pedidos (16 %).
IVA_RATE = 0.16


class OrderError(Exception):
    """Error base de la lógica de negocio de pedidos."""


class OutOfStockError(OrderError):
    """No hay stock suficiente para satisfacer la cantidad solicitada."""


class PaymentRejectedError(OrderError):
    """La pasarela de pagos rechazó el cobro."""


class OrderService:
    """Orquesta el ciclo de vida de un pedido usando BD y pasarela de pagos."""

    def __init__(self, db, payment_gateway, iva_rate: float = IVA_RATE) -> None:
        self.db = db
        self.payment_gateway = payment_gateway
        self.iva_rate = iva_rate

    def calculate_total(self, unit_price: float, quantity: int) -> float:
        """Calcula el total con IVA para ``quantity`` unidades.

        Lanza ``ValueError`` si la cantidad no es un entero positivo.
        """
        if quantity <= 0:
            raise ValueError("La cantidad debe ser un entero positivo.")

        subtotal = unit_price * quantity
        total = subtotal * (1 + self.iva_rate)
        return round(total, 2)

    def place_order(self, product_id: str, quantity: int, card_token: str) -> dict:
        """Crea un pedido completo de principio a fin.

        Flujo:
            1. Consulta stock en la BD.
            2. Valida que haya stock suficiente.
            3. Consulta el precio y calcula el total con IVA.
            4. Cobra a través de la pasarela de pagos.
            5. Si el pago es aprobado, persiste el pedido y descuenta stock.

        Devuelve un dict: {"order_id", "total", "status"}.
        """
        stock = self.db.get_stock(product_id)
        if quantity > stock:
            raise OutOfStockError(
                f"Stock insuficiente para {product_id!r}: "
                f"solicitado={quantity}, disponible={stock}."
            )

        unit_price = self.db.get_price(product_id)
        total = self.calculate_total(unit_price, quantity)

        payment = self.payment_gateway.charge(card_token, total)
        if not payment.get("approved"):
            raise PaymentRejectedError(
                f"Pago rechazado: {payment.get('reason', 'desconocido')}."
            )

        order = {
            "product_id": product_id,
            "quantity": quantity,
            "total": total,
            "transaction_id": payment.get("transaction_id"),
        }
        order_id = self.db.save_order(order)
        self.db.update_stock(product_id, stock - quantity)

        return {"order_id": order_id, "total": total, "status": "CONFIRMED"}
