from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('pay/<int:booking_id>/', views.pay_for_booking, name='pay'),
    path('status/<int:payment_id>/', views.payment_status, name='status'),
    path('callback/', views.mpesa_callback, name='callback'),
]