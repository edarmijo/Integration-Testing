"""Capa 4 - Persistencia.

IMPORTANTE (premisa del taller):
    La base de datos real AÚN NO EXISTE ni está desplegada en el entorno de
    desarrollo. Por eso TODOS los métodos que tocan la red/BD lanzan
    ``DatabaseConnectionError`` si se ejecutan directamente.

    Esta clase define el CONTRATO (la interfaz) que la lógica de negocio
    espera. El Integrante 3 construirá un "Fake State Driver" en memoria que
    implemente estos mismos métodos para poder probar la integración
    (estrategia Bottom-Up) SIN necesidad de la BD real.

Métodos del contrato que ``OrderService`` consume:
    - get_stock(product_id)      -> int
    - get_price(product_id)      -> float
    - save_order(order)          -> str   (devuelve el id del pedido creado)
    - update_stock(product_id, new_stock) -> None
"""


class DatabaseConnectionError(Exception):
    """Se lanza cuando se intenta hablar con una BD que aún no está desplegada."""


class DbConnector:
    """Conector a la base de datos de pedidos (NO implementado todavía)."""

    def __init__(self, dsn: str | None = None) -> None:
        # DSN = Data Source Name. Apunta a un servidor que todavía no existe.
        self.dsn = dsn or "postgresql://db.orders.internal:5432/orders"
        self._connected = False

    # --- Ciclo de vida de la conexión -------------------------------------
    def connect(self) -> None:
        """Abre la conexión. Falla porque la BD no está desplegada."""
        raise DatabaseConnectionError(
            f"No se pudo conectar a la base de datos en '{self.dsn}': "
            "la infraestructura aún no está desplegada."
        )

    def close(self) -> None:
        self._connected = False

    # --- Operaciones del contrato -----------------------------------------
    def get_stock(self, product_id: str) -> int:
        raise DatabaseConnectionError(
            f"get_stock({product_id!r}) falló: base de datos no disponible."
        )

    def get_price(self, product_id: str) -> float:
        raise DatabaseConnectionError(
            f"get_price({product_id!r}) falló: base de datos no disponible."
        )

    def save_order(self, order: dict) -> str:
        raise DatabaseConnectionError(
            "save_order(...) falló: base de datos no disponible."
        )

    def update_stock(self, product_id: str, new_stock: int) -> None:
        raise DatabaseConnectionError(
            f"update_stock({product_id!r}, {new_stock}) falló: "
            "base de datos no disponible."
        )
