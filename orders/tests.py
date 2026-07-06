from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from orders.models import Order
from payments.models import Payment


class CheckoutPaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='secret123',
            role='customer',
        )
        self.client.force_login(self.user)

    def test_cash_payment_option_is_available(self):
        order = Order.objects.create(customer=self.user, total_amount=1000)
        response = self.client.get(reverse('payments:pay', args=[order.id]))
        self.assertContains(response, 'Cash')

    def test_cash_payment_creates_successful_payment(self):
        order = Order.objects.create(customer=self.user, total_amount=1000)
        response = self.client.post(
            reverse('payments:pay', args=[order.id]),
            {'payment_method': Payment.Method.CASH},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Payment.objects.filter(booking=order, payment_method=Payment.Method.CASH).exists())
