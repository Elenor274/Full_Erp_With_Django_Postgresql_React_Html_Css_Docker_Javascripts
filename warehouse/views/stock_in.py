from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from warehouse.models import Warehouse, StockItem, StockTransaction
from warehouse.forms import StockInForm


def check_warehouse_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_warehouse

@login_required
def stock_in(request, pk):
    if not check_warehouse_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")

    warehouse = get_object_or_404(Warehouse, pk=pk)

    # اگر درخواست POST بود → عملیات ورودی انجام شود
    if request.method == "POST":
        form = StockInForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            unit = form.cleaned_data["unit"]
            supplier_name = form.cleaned_data["supplier_name"]
            transaction_category = form.cleaned_data["transaction_category"]
            delivery_date = form.cleaned_data["delivery_date"]
            reference = form.cleaned_data["reference"]
            order_remaining = form.cleaned_data["order_remaining"]

            # 1) ثبت تراکنش ورودی
            StockTransaction.objects.create(
                warehouse=warehouse,
                product=product,
                type=StockTransaction.IN,
                quantity=quantity,
                unit=unit,
                supplier_name=supplier_name,
                transaction_category=transaction_category,
                delivery_date=delivery_date,
                reference=reference,
                order_remaining=order_remaining,
                user=request.user
            )

            # 2) افزایش موجودی
            stock_item, created = StockItem.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={"quantity": 0}
            )

            stock_item.quantity += quantity
            stock_item.save()

            return redirect("warehouse:stock_list", pk=warehouse.id)

    # اگر GET بود → فقط فرم نمایش داده شود
    else:
        form = StockInForm()

    return render(request, "warehouse/stock_in.html", {
        "warehouse": warehouse,
        "form": form
    })
