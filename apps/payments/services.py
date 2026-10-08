import logging

logger = logging.getLogger('pos')


class PaymentGatewayError(Exception):
    pass


class PaymentGatewayService:
    """Adaptador base para Stripe/Adyen/MercadoPago."""

    @staticmethod
    def charge(amount, currency, token, metadata=None):
        if not token:
            raise PaymentGatewayError('Token de pago requerido')
        logger.info('Pago externo autorizado: %s %s', amount, currency)
        return {'status': 'authorized', 'gateway_reference': f'gw_{token[-6:]}' }
