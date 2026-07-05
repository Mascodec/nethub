import base64
import datetime
import requests
from decouple import config
from requests.auth import HTTPBasicAuth


def get_access_token():
    consumer_key = config("CONSUMER_KEY")
    consumer_secret = config("CONSUMER_SECRET")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(consumer_key, consumer_secret)
    )

    return response.json()["access_token"]


def stk_push(phone_number, amount):

    access_token = get_access_token()

    shortcode = config("BUSINESS_SHORTCODE")
    passkey = config("PASSKEY")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        (shortcode + passkey + timestamp).encode()
    ).decode()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": config("CALLBACK_URL"),
        "AccountReference": "Bree Nethub",
        "TransactionDesc": "Payment"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    return response.json()