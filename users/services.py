"""
Сервисные функции для взаимодействия с Stripe API.
При создании платежа: продукт → цена → сессия Checkout.
Цены в Stripe передаются в копейках (amount * 100).
"""
import stripe
from django.conf import settings
from typing import Optional


def get_stripe_api_key() -> Optional[str]:
    """Возвращает API-ключ Stripe из настроек."""
    key = getattr(settings, 'STRIPE_SECRET_KEY', None) or ''
    return key if key else None


def create_stripe_product(name: str, description: str = '') -> dict:
    """
    Создаёт продукт в Stripe.
    https://stripe.com/docs/api/products/create
    """
    stripe.api_key = get_stripe_api_key()
    product = stripe.Product.create(
        name=name,
        description=description or None,
    )
    return {'id': product.id, 'object': product}


def create_stripe_price(
    product_id: str,
    amount_cents: int,
    currency: str = 'rub',
) -> dict:
    """
    Создаёт цену в Stripe для продукта (разовый платёж).
    amount_cents — сумма в копейках (рубли * 100).
    https://stripe.com/docs/api/prices/create
    """
    stripe.api_key = get_stripe_api_key()
    price = stripe.Price.create(
        currency=currency,
        unit_amount=amount_cents,
        product=product_id,
    )
    return {'id': price.id, 'object': price}


def create_stripe_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Создаёт сессию Checkout для оплаты.
    Возвращает dict с полями: id (session_id), url (ссылка на оплату).
    https://stripe.com/docs/api/checkout/sessions/create
    """
    stripe.api_key = get_stripe_api_key()
    params = {
        'mode': 'payment',
        'line_items': [{'price': price_id, 'quantity': 1}],
        'success_url': success_url,
        'cancel_url': cancel_url,
    }
    if customer_email:
        params['customer_email'] = customer_email
    if metadata:
        params['metadata'] = metadata
    session = stripe.checkout.Session.create(**params)
    return {
        'id': session.id,
        'url': session.url,
        'payment_status': getattr(session, 'payment_status', None),
        'status': getattr(session, 'status', None),
    }


def retrieve_stripe_checkout_session(session_id: str) -> Optional[dict]:
    """
    Получает данные сессии Checkout по id (для проверки статуса платежа).
    https://stripe.com/docs/api/checkout/sessions/retrieve
    """
    api_key = get_stripe_api_key()
    if not api_key:
        return None
    stripe.api_key = api_key
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'id': session.id,
            'payment_status': session.payment_status,
            'status': session.status,
            'url': getattr(session, 'url', None),
        }
    except stripe.error.InvalidRequestError:
        return None
