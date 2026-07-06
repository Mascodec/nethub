from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from orders.models import Order
from services.models import Service


class AdminOrderUpdateTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='secret123',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.technician = User.objects.create_user(
            username='tech',
            email='tech@example.com',
            password='secret123',
            role='technician',
        )
        self.service = Service.objects.create(name='Install', price=5000, is_active=True)
        self.order = Order.objects.create(
            customer=self.admin,
            status='pending',
            needs_installation=True,
            service=self.service,
            total_amount=5000,
        )

    def test_admin_can_update_order_status_without_crashing(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('admin_order_detail', args=[self.order.id]),
            {'status': 'processing', 'technician': str(self.technician.id)},
        )

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')
        self.assertEqual(self.order.assigned_technician, self.technician)
