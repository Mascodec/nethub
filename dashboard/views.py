from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from accounts.models import User

def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
def dashboard(request):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'dashboard/dashboard.html', {'orders': orders})

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    total_orders     = Order.objects.count()
    pending_orders   = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    install_orders   = Order.objects.filter(needs_installation=True, status='pending').count()
    recent_orders    = Order.objects.order_by('-created_at')[:8]
    total_customers  = User.objects.filter(role='customer').count()
    technicians      = User.objects.filter(role='technician')

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_orders':     total_orders,
        'pending_orders':   pending_orders,
        'completed_orders': completed_orders,
        'install_orders':   install_orders,
        'recent_orders':    recent_orders,
        'total_customers':  total_customers,
        'technicians':      technicians,
    })

@login_required
def admin_orders(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    orders = Order.objects.order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    technicians = User.objects.filter(role='technician')
    return render(request, 'dashboard/admin_orders.html', {
        'orders': orders,
        'technicians': technicians,
        'status_filter': status_filter,
    })

@login_required
def admin_order_detail(request, order_id):
    if not is_admin(request.user):
        return redirect('dashboard')

    order = get_object_or_404(Order, id=order_id)
    technicians = User.objects.filter(role='technician')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        technician_id = request.POST.get('technician')

        if new_status:
            order.status = new_status

        if technician_id:
            technician = User.objects.filter(id=technician_id, role='technician').first()
            order.assigned_technician = technician
        else:
            order.assigned_technician = None

        order.save()

        messages.success(request, f'Order #{order.id} updated successfully.')
        return redirect('admin_order_detail', order_id=order.id)

    return render(request, 'dashboard/admin_order_detail.html', {
        'order': order,
        'technicians': technicians,
    })

@login_required
def admin_technicians(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    technicians = User.objects.filter(role='technician')
    return render(request, 'dashboard/admin_technicians.html', {
        'technicians': technicians,
    })

@login_required
def admin_add_technician(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        name     = request.POST.get('name')
        email    = request.POST.get('email')
        phone    = request.POST.get('phone')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admin_add_technician')

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            phone=phone,
            role='technician'
        )
        messages.success(request, f'Technician {name} added successfully.')
        return redirect('admin_technicians')

    return render(request, 'dashboard/admin_add_technician.html')