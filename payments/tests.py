from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.models import Order
from .models import Payment
from .views import normalize_phone


class PaymentModelTests(TestCase):
    def test_payment_can_reference_order_model(self):
        user = get_user_model().objects.create_user(username='tester', password='secret123')
        order = Order.objects.create(customer=user, total_amount='10.00')

        payment = Payment.objects.create(
            booking=order,
            phone_number='254712345678',
            amount='10.00',
        )

        self.assertEqual(payment.booking, order)
        self.assertEqual(payment.booking.total_amount, order.total_amount)


class PaymentViewTests(TestCase):
    def test_normalize_phone_supports_local_and_international_formats(self):
        self.assertEqual(normalize_phone('0712345678'), '254712345678')
        self.assertEqual(normalize_phone('254712345678'), '254712345678')
