from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from warehouse.models import Warehouse, StockItem, StockTransaction
from django.contrib.auth.decorators import login_required

def check_warehouse_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_warehouse

@login_required
def warehouse_detail(request, pk):
    if not check_warehouse_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    stock_items = StockItem.objects.filter(warehouse=warehouse).select_related('product')
    total_items = stock_items.count()
    low_stock_items = StockItem.objects.filter(warehouse=warehouse, quantity__lte=F('reorder_point')).count()
    
    transactions = StockTransaction.objects.filter(warehouse=warehouse).select_related('product', 'user').order_by('-created_at')
    total_transactions = transactions.count()

    return render(request, "warehouse/warehouse_detail.html", {
        "warehouse": warehouse,
        "stock_items": stock_items,
        "transactions": transactions,
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "total_transactions": total_transactions,
    })

