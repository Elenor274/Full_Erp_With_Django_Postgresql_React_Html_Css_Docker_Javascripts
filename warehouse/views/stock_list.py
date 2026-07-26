from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from warehouse.models import Warehouse, StockItem
from django.contrib.auth.decorators import login_required

def check_warehouse_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_warehouse

@login_required
def stock_list(request, pk):
    if not check_warehouse_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    warehouse = get_object_or_404(Warehouse, pk=pk)
    stock_items = StockItem.objects.filter(warehouse=warehouse).select_related("product")

    return render(request, "warehouse/stock_list.html", {
        "warehouse": warehouse,
        "stock_items": stock_items
    })
