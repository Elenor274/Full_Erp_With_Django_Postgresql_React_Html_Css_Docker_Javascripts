from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from warehouse.models import Warehouse, StockItem, StockTransaction
from warehouse.forms import StockOutForm


def check_warehouse_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_warehouse

@login_required
def stock_out(request, pk):
    if not check_warehouse_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")

    warehouse = get_object_or_404(Warehouse, pk=pk)

    # اگر درخواست POST بود → عملیات خروج انجام شود
    if request.method == "POST":
        form = StockOutForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            unit = form.cleaned_data["unit"]
            consumption_amount = form.cleaned_data["consumption_amount"]
            transaction_category = form.cleaned_data["transaction_category"]
            delivery_date = form.cleaned_data["delivery_date"]
            reference = form.cleaned_data["reference"]

            # بررسی موجودی کالا در انبار
            try:
                stock_item = StockItem.objects.get(warehouse=warehouse, product=product)
            except StockItem.DoesNotExist:
                messages.error(request, "این کالا در این انبار موجود نیست.")
                return redirect("warehouse:stock_out", pk=warehouse.id)

            # بررسی کافی بودن موجودی
            if stock_item.quantity < quantity:
                messages.error(request, "موجودی کافی نیست.")
                return redirect("warehouse:stock_out", pk=warehouse.id)

            # ثبت تراکنش خروج
            StockTransaction.objects.create(
                warehouse=warehouse,
                product=product,
                type=StockTransaction.OUT,
                quantity=quantity,
                unit=unit,
                consumption_amount=consumption_amount,
                transaction_category=transaction_category,
                delivery_date=delivery_date,
                reference=reference,
                user=request.user
            )

            # کاهش موجودی
            stock_item.quantity -= quantity
            stock_item.save()

            messages.success(request, "خروج کالا با موفقیت ثبت شد.")
            return redirect("warehouse:stock_list", pk=warehouse.id)

    # اگر GET بود → فقط فرم نمایش داده شود
    else:
        form = StockOutForm()

    return render(request, "warehouse/stock_out.html", {
        "warehouse": warehouse,
        "form": form
    })
