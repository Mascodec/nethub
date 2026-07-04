from django.http import JsonResponse
from .utils import stk_push


def pay(request):

    phone = "254708374149"   # Sandbox test number
    amount = 1

    response = stk_push(phone, amount)

    return JsonResponse(response)