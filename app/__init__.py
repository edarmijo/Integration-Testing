"""OrderSystem - Sistema de procesamiento de pedidos por capas.

Capas:
    1. UI/CLI ............. app.cli
    2. Lógica de Negocio .. app.order_service
    3. Pasarela de Pagos .. app.payment_gateway   (externa, aún NO desplegada)
    4. Persistencia ....... app.db_connector       (base de datos, aún NO desplegada)
"""

__version__ = "1.0.0"
