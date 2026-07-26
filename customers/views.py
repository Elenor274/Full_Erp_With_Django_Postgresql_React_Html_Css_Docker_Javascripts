from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Customer
from .forms import CustomerForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def check_customer_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_customers

@login_required
def customer_list(request):
    if not check_customer_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect('core:dashboard')

    query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')

    allowed_fields = ['customer_code', 'name', 'last_name', 'phone_number']
    if sort not in allowed_fields:
        sort = 'name'

    ordering = '-' + sort if direction == 'desc' else sort
    customers = Customer.objects.all().order_by(ordering)

    if query:
        customers = customers.filter(
            Q(customer_code__icontains=query) |
            Q(name__icontains=query) |
            Q(last_name__icontains=query)
        )

    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, 'customers/list.html', {
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
        'direction': direction,
    })

@login_required
def customer_create(request):
    if not check_customer_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect('core:dashboard')
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/create.html', {'form': form})

@login_required
def customer_edit(request, pk):
    if not check_customer_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect('core:dashboard')
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/edit.html', {'form': form, 'customer': customer})

@login_required
def customer_delete_confirm(request, pk):
    if not check_customer_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect('core:dashboard')
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/confirm_delete.html', {'customer': customer})

@login_required
@require_POST
def customer_delete(request, pk):
    if not check_customer_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect('core:dashboard')
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.success(request, f'مشتری با موفقیت حذف شد')
    return redirect('customers:customer_list')
