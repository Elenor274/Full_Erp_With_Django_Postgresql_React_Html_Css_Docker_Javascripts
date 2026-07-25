# core/views.py
from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse, NoReverseMatch
from django.db.models import Q, Sum, Count

from orders.models import Order, OrderItem
from customers.models import Customer
from production.models import Planning, Machine, Operator
from warehouse.models import Warehouse, StockItem

def logout_view(request):
    logout(request)
    return redirect('core:login')

@login_required
def dashboard(request):
    recent_qs = Order.objects.select_related('customer').prefetch_related('design_files').order_by('-created_at')[:20]
    recent_orders = []
    for o in recent_qs:
        customer_name = '—'
        try:
            if getattr(o, 'customer', None):
                customer_name = getattr(o.customer, 'name', str(o.customer))
            else:
                customer_name = getattr(o, 'customer_name', '—')
        except Exception:
            customer_name = getattr(o, 'customer_name', '—')

        design_files_info = [
            {
                'file_url': df.file.url,
                'title': df.title or df.file_name,
                'ext': df.extension.upper(),
                'badge': df.file_type_info['badge'],
                'icon': df.file_type_info['icon'],
            }
            for df in o.design_files.all()
        ]

        tot_val = getattr(o, 'total_amount', getattr(o, 'total', 0)) or 0
        try:
            tot_int = int(tot_val)
        except (ValueError, TypeError):
            tot_int = 0

        recent_orders.append({
            'id': o.pk,
            'code': o.order_code,
            'customer': customer_name,
            'date': o.created_at.strftime('%Y/%m/%d %H:%M') if getattr(o, 'created_at', None) else '—',
            'total': f"{tot_int:,}" if tot_int else "0",
            'status': o.get_status_display() if hasattr(o, 'get_status_display') else getattr(o, 'status', '—'),
            'status_color': '#0b66ff',
            'status_bg': 'rgba(11,102,255,0.06)',
            'design_files': design_files_info,
            'view_url': f"/orders/{o.pk}/",
            'edit_url': f"/orders/{o.pk}/edit/",
            'delete_url': f"/orders/{o.pk}/delete/",
        })

    totals = {
        'in_progress_orders': Order.objects.filter(status__in=['pending', 'processing']).count(),
        'customers_count': Customer.objects.count(),
        'total_orders': Order.objects.count(),
    }

    inventory = []
    if apps.is_installed('inventory'):
        try:
            InventoryItem = apps.get_model('inventory', 'InventoryItem')
            inventory_qs = InventoryItem.objects.all()[:50]
            inventory = [
                {
                    'sku': getattr(it, 'sku', ''),
                    'name': getattr(it, 'name', ''),
                    'qty': getattr(it, 'quantity', 0),
                    'threshold': getattr(it, 'reorder_threshold', 1)
                }
                for it in inventory_qs
            ]
        except Exception:
            inventory = []

    url_names = {
        'warehouse_index': 'warehouse:index',
        'products_create': 'products:product_create',
        'customers_create': 'customers:customer_create',
        'reminders': 'core:reminders',
        'settings': 'core:settings',
        'logout': 'core:logout',
        'orders_create': 'orders:order_create',
        'orders_list': 'orders:order_list',
    }

    safe_urls = {}
    for key, name in url_names.items():
        try:
            safe_urls[key] = reverse(name)
        except NoReverseMatch:
            safe_urls[key] = '#'

    context = {
        'recent_orders': recent_orders,
        'totals': totals,
        'inventory': inventory,
        'urls': safe_urls,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def reports_hub(request):
    current_tab = request.GET.get('tab', 'tracking')
    query = request.GET.get('q', '').strip()
    
    # 1. TRACKING DATA
    tracked_orders = []
    if current_tab == 'tracking':
        # Default to show some recent orders if no query, or filter if queried
        if query:
            orders_qs = Order.objects.filter(
                Q(order_code__icontains=query) |
                Q(sepidar_code__icontains=query) |
                Q(customer__customer_code__icontains=query) |
                Q(customer__name__icontains=query) |
                Q(customer__last_name__icontains=query)
            ).select_related('customer').distinct()
        else:
            orders_qs = Order.objects.select_related('customer').all()[:6]
            
        # Map statuses for progress stepper
        status_steps = {
            'registered': 1,
            'cutting': 2,
            'sewing': 3,
            'quality': 4,
            'warehouse': 5,
            'delivered': 6,
            'cancelled': -1
        }
        
        for o in orders_qs:
            # associated plans
            plans = Planning.objects.filter(order=o).select_related('machine', 'operator', 'stage', 'product')
            has_suspension = plans.filter(status='suspended').exists()
            suspended_plans = plans.filter(status='suspended')
            
            tracked_orders.append({
                'order': o,
                'items_list': o.items.all().select_related('product'),
                'step_idx': status_steps.get(o.status, 1),
                'plans': plans,
                'has_suspension': has_suspension,
                'suspended_plans': suspended_plans,
                'total_amount': o.total_amount
            })
            
    # 2. PRODUCTION DATA
    production_summary = {}
    stoppages = []
    if current_tab == 'production':
        plans_all = Planning.objects.all()
        production_summary = {
            'total_plans': plans_all.count(),
            'pending': plans_all.filter(status='pending').count(),
            'producing': plans_all.filter(status='producing').count(),
            'completed': plans_all.filter(status='completed').count(),
            'suspended': plans_all.filter(status='suspended').count(),
        }
        stoppages = Planning.objects.filter(status='suspended').select_related('order', 'machine', 'operator', 'stage', 'product', 'order__customer')
        
    # 3. WAREHOUSE DATA
    warehouse_data = []
    low_stock_items = []
    if current_tab == 'warehouse':
        warehouses = Warehouse.objects.all()
        stock_items = StockItem.objects.select_related('warehouse', 'product').all()
        for wh in warehouses:
            wh_items = stock_items.filter(warehouse=wh)
            warehouse_data.append({
                'warehouse': wh,
                'items': wh_items,
                'total_qty': wh_items.aggregate(total=Sum('quantity'))['total'] or 0
            })
        low_stock_items = stock_items.filter(quantity__lt=50) # low stock criteria
        
    # 4. SALES DATA
    sales_data = {}
    if current_tab == 'sales':
        orders_all = Order.objects.all()
        sales_data = {
            'total_orders_count': orders_all.count(),
            'status_counts': orders_all.values('status').annotate(count=Count('id')),
            'top_customers': Customer.objects.annotate(order_count=Count('order')).order_by('-order_count')[:5]
        }
        # calculate total values per status
        status_totals = {}
        for o in orders_all:
            status_totals[o.status] = status_totals.get(o.status, 0) + o.total_amount
        sales_data['status_totals'] = status_totals
        sales_data['total_revenue'] = sum(status_totals.values())

    context = {
        'current_tab': current_tab,
        'query': query,
        'tracked_orders': tracked_orders,
        'production_summary': production_summary,
        'stoppages': stoppages,
        'warehouse_data': warehouse_data,
        'low_stock_items': low_stock_items,
        'sales_data': sales_data,
    }
    return render(request, 'core/reports_hub.html', context)


from django.contrib import messages
from .models import ErpSettings
from .forms import ErpSettingsForm

@login_required
def settings_view(request):
    # Only superusers or system admins can change settings
    if not request.user.is_superuser:
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_admin_user:
            messages.error(request, "شما دسترسی لازم برای ویرایش تنظیمات سامانه را ندارید.")
            return redirect('core:dashboard')

    settings_obj, created = ErpSettings.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = ErpSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "تنظیمات عمومی سامانه با موفقیت بروزرسانی شد.")
            return redirect('core:settings')
    else:
        form = ErpSettingsForm(instance=settings_obj)

    return render(request, 'core/settings.html', {'form': form, 'settings_obj': settings_obj})

