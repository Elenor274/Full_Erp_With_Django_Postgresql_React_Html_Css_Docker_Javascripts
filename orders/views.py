# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import OrderForm, OrderItemFormSet, OrderDesignFileForm
from .models import Order, OrderDesignFile

# -----------------------------
# ایجاد سفارش
# -----------------------------
@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST, request.FILES)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()

            # پردازش فایل‌های نقشه واحدهای طراحی (Catia, Photoshop, AutoCAD, PDF, ...)
            files = request.FILES.getlist('design_files')
            titles = request.POST.getlist('design_titles')
            for idx, f in enumerate(files):
                title = titles[idx] if idx < len(titles) else f.name
                OrderDesignFile.objects.create(
                    order=order,
                    file=f,
                    title=title or f.name
                )

            messages.success(request, f"سفارش {order.order_code} با موفقیت ثبت شد.")
            return redirect("orders:order_detail", pk=order.pk)

    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, "orders/order_create.html", {
        "form": form,
        "formset": formset
    })


# -----------------------------
# لیست سفارش‌ها
# -----------------------------
@login_required
def order_list(request):
    orders = Order.objects.all().prefetch_related('design_files').order_by("-id")
    return render(request, "orders/order_list.html", {"orders": orders})


# -----------------------------
# جزئیات سفارش
# -----------------------------
@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    design_files = order.design_files.all()
    design_file_form = OrderDesignFileForm()
    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items,
        "design_files": design_files,
        "design_file_form": design_file_form,
    })


# -----------------------------
# آپلود نقشه جدید مستقیم از جزئیات سفارش
# -----------------------------
@login_required
@require_POST
def order_upload_design_file(request, pk):
    order = get_object_or_404(Order, pk=pk)
    files = request.FILES.getlist('file')
    title = request.POST.get('title', '')
    
    if files:
        for f in files:
            OrderDesignFile.objects.create(
                order=order,
                file=f,
                title=title or f.name
            )
        messages.success(request, "نقشه‌(های) جدید واحد طراحی با موفقیت آپلود شد.")
    else:
        messages.error(request, "لطفاً حداقل یک فایل نقشه انتخاب کنید.")
        
    return redirect("orders:order_detail", pk=order.pk)


# -----------------------------
# حذف نقشه طراحی
# -----------------------------
@login_required
@require_POST
def order_delete_design_file(request, file_id):
    design_file = get_object_or_404(OrderDesignFile, pk=file_id)
    order_pk = design_file.order.pk
    file_name = design_file.file_name
    design_file.file.delete(save=False)
    design_file.delete()
    messages.success(request, f"نقشه «{file_name}» با موفقیت حذف شد.")
    return redirect("orders:order_detail", pk=order_pk)


# -----------------------------
# ویرایش سفارش
# -----------------------------
@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, request.FILES, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            # آپلود نقشه‌های جدید در ویرایش سفارش
            files = request.FILES.getlist('design_files')
            titles = request.POST.getlist('design_titles')
            for idx, f in enumerate(files):
                title = titles[idx] if idx < len(titles) else f.name
                OrderDesignFile.objects.create(
                    order=order,
                    file=f,
                    title=title or f.name
                )

            messages.success(request, f"سفارش {order.order_code} به‌روزرسانی شد.")
            return redirect("orders:order_detail", pk=order.pk)

    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, "orders/order_edit.html", {
        "form": form,
        "formset": formset,
        "order": order,
        "design_files": order.design_files.all()
    })


# -----------------------------
# حذف سفارش
# -----------------------------
@login_required
@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.success(request, f"سفارش {order.order_code} حذف شد.")
    return redirect("orders:order_list")


@login_required
def order_delete_confirm(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/order_delete_confirm.html", {
        "order": order
    })

