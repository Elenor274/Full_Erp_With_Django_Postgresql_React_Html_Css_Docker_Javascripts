from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from warehouse.models import Warehouse, StockTransaction
from django.contrib.auth.decorators import login_required

def check_warehouse_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_warehouse

@login_required
def stock_transactions(request, pk):
    if not check_warehouse_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    warehouse = get_object_or_404(Warehouse, pk=pk)

    transactions = StockTransaction.objects.filter(
        warehouse=warehouse
    ).select_related("product", "user").order_by("-created_at")

    return render(request, "warehouse/stock_transactions.html", {
        "warehouse": warehouse,
        "transactions": transactions
    })
