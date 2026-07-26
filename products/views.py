from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.db.models import Q, F, ExpressionWrapper, IntegerField, Subquery, OuterRef
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import ProductForm, ProductGroupForm
from .models import Product, ProductGroup
from warehouse.models import StockItem, StockTransaction
from orders.models import OrderItem, Order
from production.models import Planning, QualityControl


from django.contrib import messages

def check_product_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_products

# -----------------------------
# لیست کالاها
# -----------------------------
@login_required
def product_list(request):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")

    query = request.GET.get("q", "")
    group_filter = request.GET.get("group", "")
    sort = request.GET.get("sort", "code")
    direction = request.GET.get("dir", "asc")
    page_number = request.GET.get("page", 1)

    products = Product.objects.all()

    # فیلتر جستجو
    if query:
        products = products.filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(group__name__icontains=query)
        )

    # فیلتر گروه کالا
    if group_filter:
        products = products.filter(group_id=group_filter)

    # مرتب‌سازی
    if sort == "real_stock":
        stock_subquery = StockItem.objects.filter(
            product=OuterRef("pk")
        ).values("product").annotate(
            total=models.Sum("quantity")
        ).values("total")

        products = products.annotate(
            real_stock_value=Subquery(stock_subquery, output_field=IntegerField())
        )

        sort_field = "real_stock_value"
    else:
        sort_field = sort

    if direction == "desc":
        sort_field = "-" + sort_field

    products = products.order_by(sort_field)

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(page_number)

    groups = ProductGroup.objects.all()

    return render(request, "products/product_list.html", {
        "page_obj": page_obj,
        "query": query,
        "sort": sort,
        "direction": direction,
        "groups": groups,
        "group_filter": group_filter,
    })


# -----------------------------
# ردیابی و رهگیری بر اساس کد کالا
# -----------------------------
@login_required
def product_trace(request):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    code = request.GET.get("code", "").strip() or request.GET.get("q", "").strip()
    if not code:
        return redirect("products:product_list")
    
    product = Product.objects.filter(Q(code__iexact=code) | Q(code__icontains=code) | Q(name__icontains=code)).first()
    if product:
        return redirect("products:product_detail", pk=product.pk)
    else:
        return redirect(f"/products/?q={code}")


# -----------------------------
# جزئیات و رهگیری کامل کالا (360 درجه)
# -----------------------------
@login_required
def product_detail(request, pk):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    product = get_object_or_404(Product, pk=pk)

    stock_items = StockItem.objects.filter(product=product).select_related('warehouse')
    transactions = StockTransaction.objects.filter(product=product).select_related(
        'warehouse', 'user'
    ).order_by('-created_at')[:30]

    order_items = OrderItem.objects.filter(
        product=product
    ).select_related('order', 'order__customer').order_by('-order__created_at')

    plannings = Planning.objects.filter(
        Q(product=product) | Q(raw_material=product)
    ).select_related('order', 'machine', 'operator', 'stage', 'warehouse').order_by('-created_at')

    qc_records = QualityControl.objects.filter(
        product=product
    ).select_related('inspector', 'warehouse', 'order').order_by('-inspection_date')

    return render(request, "products/product_detail.html", {
        'product': product,
        'stock_items': stock_items,
        'transactions': transactions,
        'order_items': order_items,
        'plannings': plannings,
        'qc_records': qc_records,
    })


from django.contrib import messages

def check_product_permission(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False
    return profile.is_admin_user or profile.access_products

# -----------------------------
# ایجاد کالا
# -----------------------------
@login_required
def product_create(request):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.current_user = request.user
            product.save()
            return redirect("products:product_list")
    else:
        form = ProductForm()

    return render(request, "products/product_create.html", {"form": form})


# -----------------------------
# ویرایش کالا
# -----------------------------
@login_required
def product_edit(request, pk):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.current_user = request.user
            updated.save()
            return redirect("products:product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_edit.html", {"form": form, "product": product})


# -----------------------------
# حذف کالا
# -----------------------------
@login_required
def product_delete_confirm(request, pk):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_delete_confirm.html", {"product": product})


@login_required
def product_delete(request, pk):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("products:product_list")


# -----------------------------
# CRUD گروه کالا
# -----------------------------
@login_required
def group_list(request):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    groups = ProductGroup.objects.all()
    return render(request, "products/group_list.html", {"groups": groups})


@login_required
def group_create(request):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = ProductGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("products:group_list")
    else:
        form = ProductGroupForm()

    return render(request, "products/group_create.html", {"form": form})


@login_required
def group_edit(request, pk):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    group = get_object_or_404(ProductGroup, pk=pk)

    if request.method == "POST":
        form = ProductGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("products:group_list")
    else:
        form = ProductGroupForm(instance=group)

    return render(request, "products/group_edit.html", {"form": form, "group": group})


@login_required
def group_delete(request, pk):
    if not check_product_permission(request.user):
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect("core:dashboard")
    group = get_object_or_404(ProductGroup, pk=pk)
    group.delete()
    return redirect("products:group_list")
