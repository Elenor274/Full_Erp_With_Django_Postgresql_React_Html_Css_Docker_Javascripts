from django.shortcuts import render, redirect
from django.contrib import messages
from warehouse.models import Warehouse
from django.contrib.auth.decorators import login_required

def check_warehouse_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_warehouse

@login_required
def warehouse_list(request):
    if not check_warehouse_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    warehouses = Warehouse.objects.all()

    return render(request, "warehouse/warehouse_list.html", {
        "warehouses": warehouses
    })
