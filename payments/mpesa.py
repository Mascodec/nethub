import base64
from datetime import datetime
from decimal import Decimal

import requests
from django.conf import settings


class MpesaError(Exception):
    pass


def _require_credentials():
    missing = [
        name
        for name in [
            'MPESA_CONSUMER_KEY',
            'MPESA_CONSUMER_SECRET',
            'MPESA_SHORTCODE',
            'MPESA_PASSKEY',
            'MPESA_CALLBACK_URL',
        ]
        if not getattr(settings, name, '')
    ]
    if missing:
        raise MpesaError(
            'MPESA settings are incomplete. Set ' + ', '.join(missing) + ' in your environment.'
        )


def get_access_token():
    _require_credentials()
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), timeout=15)
    if r.status_code != 200:
        raise MpesaError(f"Token request failed: {r.status_code} {r.text}")
    return r.json()['access_token']


def _password_and_timestamp():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(raw.encode()).decode(), timestamp


def stk_push(phone_number, amount, account_reference, transaction_desc="Payment"):
    _require_credentials()
    token = get_access_token()
    password, timestamp = _password_and_timestamp()
    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(Decimal(str(amount))),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    data = r.json()
    if r.status_code != 200:
        raise MpesaError(data.get('errorMessage', 'STK push failed'))
    return data