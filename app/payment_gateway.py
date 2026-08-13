"""Capa 3 - Pasarela de Pagos Externa.

IMPORTANTE (premisa del taller):
    Este servicio HTTP externo AÚN NO está disponible en el entorno de
    desarrollo. Si se llama a ``charge`` sin interceptar la red, la librería
    ``requests`` lanzará un error de conexión real.

    El Integrante 4 usará ``requests-mock`` para interceptar las peticiones
    HTTP y simular respuestas (200 OK, 402 Payment Required, Timeouts),
    probando así el código REAL de esta capa (estrategia Bottom-Up).

Contrato que consume ``OrderService``:
    charge(card_token, amount) -> dict con, al menos, la clave "approved".
        Ejemplo aprobado:  {"approved": True,  "transaction_id": "tx_123"}
        Ejemplo rechazado: {"approved": False, "reason": "insufficient_funds"}
"""

import requests


class PaymentGatewayError(Exception):
    """Error genérico de la pasarela (respuesta HTTP inesperada, red, etc.)."""


class PaymentGateway:
    """Cliente HTTP de la pasarela de pagos."""

    BASE_URL = "https://payments.example.com/api/v1"

    def __init__(self, base_url: str | None = None, timeout: float = 5.0) -> None:
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout

    def charge(self, card_token: str, amount: float) -> dict:
        """Cobra ``amount`` a la tarjeta identificada por ``card_token``.

        Reglas de traducción de la respuesta HTTP a nuestro contrato:
            - 200 OK               -> pago aprobado.
            - 402 Payment Required -> pago rechazado (no es una excepción).
            - Cualquier otro código -> ``PaymentGatewayError``.
            - Timeout / error de red -> ``PaymentGatewayError``.
        """
        url = f"{self.base_url}/charges"
        payload = {"card_token": card_token, "amount": amount}

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
        except requests.exceptions.Timeout as exc:
            raise PaymentGatewayError("La pasarela de pagos no respondió a tiempo.") from exc
        except requests.exceptions.RequestException as exc:
            raise PaymentGatewayError(f"Error de red al contactar la pasarela: {exc}") from exc

        if response.status_code == 200:
            data = response.json()
            return {
                "approved": True,
                "transaction_id": data.get("transaction_id"),
            }

        if response.status_code == 402:
            data = response.json()
            return {
                "approved": False,
                "reason": data.get("reason", "payment_required"),
            }

        raise PaymentGatewayError(
            f"Respuesta inesperada de la pasarela: HTTP {response.status_code}."
        )
