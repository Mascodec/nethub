import requests
from requests.auth import HTTPBasicAuth
from decouple import config

consumer_key = config("CONSUMER_KEY")
consumer_secret = config("CONSUMER_SECRET")

url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

response = requests.get(
    url,
    auth=HTTPBasicAuth(consumer_key, consumer_secret)
)

print(response.status_code)
print(response.text)