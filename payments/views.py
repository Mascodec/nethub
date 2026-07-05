import json, re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .mpesa import stk_push, MpesaError
from .models import Payment
from orders.models import Order

def normalize_phone(raw):
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('0'):
        digits = '254' + digits[1:]
    elif digits.startswith('7') or digits.startswith('1'):
        digits = '254' + digits
    return digits

@login_required
def pay_for_booking(request, booking_id):
    booking = get_object_or_404(Order, pk=booking_id, customer=request.user)
    if request.method == 'POST':
        phone = normalize_phone(request.POST.get('phone_number', ''))
        if not re.match(r'^254(7|1)\d{8}$', phone):
            return render(request, 'payments/pay.html', {'booking': booking, 'error': 'Invalid phone number'})

        payment = Payment.objects.create(booking=booking, phone_number=phone, amount=booking.total_amount)
        try:
            resp = stk_push(phone, booking.total_amount, f"BOOKING{booking.id}")
        except MpesaError as e:
            payment.status = Payment.Status.FAILED
            payment.result_desc = str(e)
            payment.save()
            return render(request, 'payments/pay.html', {'booking': booking, 'error': str(e)})

        payment.merchant_request_id = resp.get('MerchantRequestID', '')
        payment.checkout_request_id = resp.get('CheckoutRequestID', '')
        payment.save()
        return render(request, 'payments/waiting.html', {'booking': booking, 'payment': payment})
    return render(request, 'payments/pay.html', {'booking': booking})

@login_required
def payment_status(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, booking__customer=request.user)
    return JsonResponse({'status': payment.status, 'result_desc': payment.result_desc,
                          'mpesa_receipt_number': payment.mpesa_receipt_number})

@csrf_exempt
@require_POST
def mpesa_callback(request):
    data = json.loads(request.body)
    stk = data.get('Body', {}).get('stkCallback', {})
    checkout_id = stk.get('CheckoutRequestID')
    result_code = stk.get('ResultCode')

    try:
        payment = Payment.objects.get(checkout_request_id=checkout_id)
    except Payment.DoesNotExist:
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    payment.result_code = str(result_code)
    payment.result_desc = stk.get('ResultDesc', '')
    if result_code == 0:
        for item in stk.get('CallbackMetadata', {}).get('Item', []):
            if item.get('Name') == 'MpesaReceiptNumber':
                payment.mpesa_receipt_number = item.get('Value', '')
        payment.status = Payment.Status.SUCCESS
        payment.booking.status = 'confirmed'
        payment.booking.save()
    else:
        payment.status = Payment.Status.FAILED
    payment.save()
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})