from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.core.paginator import Paginator

from products.models import Product
from .models import Machine, Operator, WorkStage, Planning, MaintenanceActivity, BOM, BOMItem, QualityControl
from .forms import MachineForm, OperatorForm, WorkStageForm, PlanningForm, MaintenanceActivityForm, BOMForm, QualityControlForm

# =====================================================================
# برنامه‌ریزی تولید
# =====================================================================

@login_required
def planning_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    sort = request.GET.get('sort', '-created_at')
    direction = request.GET.get('dir', 'desc')
    page_number = request.GET.get('page', 1)

    plans = Planning.objects.all().select_related('order', 'product', 'machine', 'operator', 'stage')

    # جستجو
    if query:
        plans = plans.filter(
            Q(planning_code__icontains=query) |
            Q(product__name__icontains=query) |
            Q(machine__name__icontains=query) |
            Q(operator__last_name__icontains=query) |
            Q(order__order_code__icontains=query)
        )

    # فیلتر وضعیت
    if status_filter:
        plans = plans.filter(status=status_filter)

    # مرتب‌سازی
    sort_field = sort
    if direction == 'desc' and not sort.startswith('-'):
        sort_field = '-' + sort
    elif direction == 'asc' and sort.startswith('-'):
        sort_field = sort[1:]

    plans = plans.order_by(sort_field)

    paginator = Paginator(plans, 10)
    page_obj = paginator.get_page(page_number)

    status_choices = Planning.STATUS_CHOICES

    return render(request, 'production/planning_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'sort': sort,
        'direction': direction,
    })


@login_required
def planning_detail(request, pk):
    plan = get_object_or_404(Planning, pk=pk)
    return render(request, 'production/planning_detail.html', {'plan': plan})


@login_required
def planning_create(request):
    if request.method == 'POST':
        form = PlanningForm(request.POST)
        if form.is_valid():
            plan = form.save()
            
            # پردازش خودکار تولید و کسر انبار
            if plan.status == 'completed':
                success, msg = plan.complete_production(user=request.user)
                messages.success(request, f"برنامه‌ریزی ثبت شد. {msg}")
            elif plan.status == 'producing' and not plan.material_deducted:
                success, msg = plan.deduct_inventory(user=request.user)
                if success:
                    messages.success(request, f"برنامه‌ریزی ثبت شد. {msg}")
                else:
                    messages.warning(request, f"برنامه‌ریزی ثبت شد ولی: {msg}")
            else:
                messages.success(request, "برنامه‌ریزی تولید با موفقیت ثبت شد.")
                
            return redirect('production:planning_list')
    else:
        form = PlanningForm()

    return render(request, 'production/planning_create.html', {'form': form})


@login_required
def planning_edit(request, pk):
    plan = get_object_or_404(Planning, pk=pk)
    old_status = plan.status

    if request.method == 'POST':
        form = PlanningForm(request.POST, instance=plan)
        if form.is_valid():
            updated_plan = form.save()
            
            # پردازش خودکار تولید و کسر انبار در ویرایش
            if updated_plan.status == 'completed':
                success, msg = updated_plan.complete_production(user=request.user)
                messages.success(request, f"برنامه‌ریزی ویرایش شد. {msg}")
            elif updated_plan.status == 'producing' and not updated_plan.material_deducted:
                success, msg = updated_plan.deduct_inventory(user=request.user)
                if success:
                    messages.success(request, f"برنامه‌ریزی ویرایش شد. {msg}")
                else:
                    messages.warning(request, f"برنامه‌ریزی ویرایش شد ولی: {msg}")
            else:
                messages.success(request, "برنامه‌ریزی تولید با موفقیت ویرایش شد.")
                
            return redirect('production:planning_list')
    else:
        form = PlanningForm(instance=plan)

    return render(request, 'production/planning_edit.html', {'form': form, 'plan': plan})


@login_required
def planning_delete(request, pk):
    plan = get_object_or_404(Planning, pk=pk)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, "برنامه‌ریزی تولید با موفقیت حذف شد.")
        return redirect('production:planning_list')
    return render(request, 'production/planning_confirm_delete.html', {'plan': plan})


@login_required
def planning_deduct(request, pk):
    """
    متد دستی کسر موجودی انبار برای یک برنامه‌ریزی تولید خاص
    """
    plan = get_object_or_404(Planning, pk=pk)
    success, msg = plan.deduct_inventory(user=request.user)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect('production:planning_detail', pk=pk)


# =====================================================================
# ماشین‌آلات
# =====================================================================

@login_required
def machine_list(request):
    machines = Machine.objects.all().order_by('machine_code')
    return render(request, 'production/machine_list.html', {'machines': machines})


@login_required
def machine_create(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ماشین جدید با موفقیت اضافه شد.")
            return redirect('production:machine_list')
    else:
        form = MachineForm()
    return render(request, 'production/machine_create.html', {'form': form})


@login_required
def machine_edit(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, "ماشین با موفقیت ویرایش شد.")
            return redirect('production:machine_list')
    else:
        form = MachineForm(instance=machine)
    return render(request, 'production/machine_edit.html', {'form': form, 'machine': machine})


@login_required
def machine_delete(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        machine.delete()
        messages.success(request, "ماشین با موفقیت حذف شد.")
        return redirect('production:machine_list')
    return render(request, 'production/machine_confirm_delete.html', {'machine': machine})


# =====================================================================
# اپراتورها
# =====================================================================

@login_required
def operator_list(request):
    operators = Operator.objects.all().order_by('operator_code')
    return render(request, 'production/operator_list.html', {'operators': operators})


@login_required
def operator_create(request):
    if request.method == 'POST':
        form = OperatorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "اپراتور جدید با موفقیت ثبت شد.")
            return redirect('production:operator_list')
    else:
        form = OperatorForm()
    return render(request, 'production/operator_create.html', {'form': form})


@login_required
def operator_edit(request, pk):
    operator = get_object_or_404(Operator, pk=pk)
    if request.method == 'POST':
        form = OperatorForm(request.POST, instance=operator)
        if form.is_valid():
            form.save()
            messages.success(request, "اپراتور با موفقیت ویرایش شد.")
            return redirect('production:operator_list')
    else:
        form = OperatorForm(instance=operator)
    return render(request, 'production/operator_edit.html', {'form': form, 'operator': operator})


@login_required
def operator_delete(request, pk):
    operator = get_object_or_404(Operator, pk=pk)
    if request.method == 'POST':
        operator.delete()
        messages.success(request, "اپراتور با موفقیت حذف شد.")
        return redirect('production:operator_list')
    return render(request, 'production/operator_confirm_delete.html', {'operator': operator})


# =====================================================================
# مراحل کاری
# =====================================================================

@login_required
def stage_list(request):
    stages = WorkStage.objects.all().order_by('code')
    return render(request, 'production/stage_list.html', {'stages': stages})


@login_required
def stage_create(request):
    if request.method == 'POST':
        form = WorkStageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "مرحله کاری جدید با موفقیت تعریف شد.")
            return redirect('production:stage_list')
    else:
        form = WorkStageForm()
    return render(request, 'production/stage_create.html', {'form': form})


@login_required
def stage_edit(request, pk):
    stage = get_object_or_404(WorkStage, pk=pk)
    if request.method == 'POST':
        form = WorkStageForm(request.POST, instance=stage)
        if form.is_valid():
            form.save()
            messages.success(request, "مرحله کاری با موفقیت ویرایش شد.")
            return redirect('production:stage_list')
    else:
        form = WorkStageForm(instance=stage)
    return render(request, 'production/stage_edit.html', {'form': form, 'stage': stage})


@login_required
def stage_delete(request, pk):
    stage = get_object_or_404(WorkStage, pk=pk)
    if request.method == 'POST':
        stage.delete()
        messages.success(request, "مرحله کاری با موفقیت حذف شد.")
        return redirect('production:stage_list')
    return render(request, 'production/stage_confirm_delete.html', {'stage': stage})


# =====================================================================
# نگهداری و تعمیرات (نت)
# =====================================================================

@login_required
def maintenance_list(request):
    query = request.GET.get('q', '')
    repair_type_filter = request.GET.get('repair_type', '')
    dept_filter = request.GET.get('dept', '')
    stoppage_filter = request.GET.get('stoppage', '')
    
    records = MaintenanceActivity.objects.all().select_related('machine', 'operator')
    
    if query:
        records = records.filter(
            Q(maintenance_code__icontains=query) |
            Q(machine__name__icontains=query) |
            Q(machine__machine_code__icontains=query) |
            Q(location__icontains=query) |
            Q(execution_group__icontains=query) |
            Q(consumables_used__icontains=query)
        )
        
    if repair_type_filter:
        records = records.filter(repair_type=repair_type_filter)
        
    if dept_filter:
        records = records.filter(requester_unit=dept_filter)
        
    if stoppage_filter == 'yes':
        records = records.filter(has_stoppage=True)
    elif stoppage_filter == 'no':
        records = records.filter(has_stoppage=False)
        
    paginator = Paginator(records, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'production/maintenance_list.html', {
        'page_obj': page_obj,
        'query': query,
        'repair_types': MaintenanceActivity.REPAIR_TYPES,
        'departments': MaintenanceActivity.DEPARTMENTS,
        'repair_type_filter': repair_type_filter,
        'dept_filter': dept_filter,
        'stoppage_filter': stoppage_filter,
    })


@login_required
def maintenance_detail(request, pk):
    record = get_object_or_404(MaintenanceActivity, pk=pk)
    return render(request, 'production/maintenance_detail.html', {'record': record})


@login_required
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceActivityForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"درخواست تعمیرات {record.maintenance_code} با موفقیت ثبت گردید.")
            return redirect('production:maintenance_list')
        else:
            messages.error(request, "لطفاً خطاهای فرم را تصحیح فرمایید.")
    else:
        form = MaintenanceActivityForm()
        
    return render(request, 'production/maintenance_create.html', {'form': form})


@login_required
def maintenance_edit(request, pk):
    record = get_object_or_404(MaintenanceActivity, pk=pk)
    if request.method == 'POST':
        form = MaintenanceActivityForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"درخواست تعمیرات {record.maintenance_code} با موفقیت بروزرسانی شد.")
            return redirect('production:maintenance_list')
        else:
            messages.error(request, "لطفاً خطاهای فرم را تصحیح فرمایید.")
    else:
        form = MaintenanceActivityForm(instance=record)
        
    return render(request, 'production/maintenance_edit.html', {'form': form, 'record': record})


@login_required
def maintenance_delete(request, pk):
    record = get_object_or_404(MaintenanceActivity, pk=pk)
    if request.method == 'POST':
        code = record.maintenance_code
        record.delete()
        messages.success(request, f"درخواست تعمیرات {code} با موفقیت حذف گردید.")
        return redirect('production:maintenance_list')
    return render(request, 'production/maintenance_confirm_delete.html', {'record': record})


# =====================================================================
# ساختار درخت محصول (BOM) و انفجار مواد (BOM Explosion)
# =====================================================================

@login_required
def bom_list(request):
    query = request.GET.get('q', '')
    boms = BOM.objects.all().select_related('product').prefetch_related('items__component')
    if query:
        boms = boms.filter(
            Q(bom_code__icontains=query) |
            Q(title__icontains=query) |
            Q(product__name__icontains=query) |
            Q(product__code__icontains=query)
        )
    return render(request, 'production/bom_list.html', {'boms': boms, 'query': query})


@login_required
def bom_detail(request, pk):
    bom = get_object_or_404(BOM.objects.select_related('product').prefetch_related('items__component', 'items__stage'), pk=pk)
    return render(request, 'production/bom_detail.html', {'bom': bom})


@login_required
def bom_create(request):
    if request.method == 'POST':
        form = BOMForm(request.POST)
        if form.is_valid():
            bom = form.save()
            # پردازش اقلام BOM از فرم دینامیک
            components = request.POST.getlist('component[]')
            quantities = request.POST.getlist('quantity[]')
            scrap_rates = request.POST.getlist('scrap_percentage[]')
            stages = request.POST.getlist('stage[]')
            notes_list = request.POST.getlist('notes[]')

            for i in range(len(components)):
                comp_id = components[i]
                if comp_id:
                    qty = quantities[i] if i < len(quantities) and quantities[i] else 1.0
                    scrap = scrap_rates[i] if i < len(scrap_rates) and scrap_rates[i] else 0.0
                    stg_id = stages[i] if i < len(stages) and stages[i] else None
                    nt = notes_list[i] if i < len(notes_list) else ''

                    BOMItem.objects.create(
                        bom=bom,
                        component_id=comp_id,
                        quantity=qty,
                        scrap_percentage=scrap,
                        stage_id=stg_id if stg_id else None,
                        notes=nt
                    )
            messages.success(request, f"ساختار درخت محصول {bom.bom_code} با موفقیت تعریف شد.")
            return redirect('production:bom_detail', pk=bom.pk)
    else:
        form = BOMForm()
    products = Product.objects.all().order_by('name')
    stages = WorkStage.objects.all().order_by('code')
    return render(request, 'production/bom_create.html', {'form': form, 'products': products, 'stages': stages})


@login_required
def bom_edit(request, pk):
    bom = get_object_or_404(BOM, pk=pk)
    if request.method == 'POST':
        form = BOMForm(request.POST, instance=bom)
        if form.is_valid():
            bom = form.save()
            # پاک کردن اقلام قبلی و ثبت اقلام جدید
            bom.items.all().delete()
            components = request.POST.getlist('component[]')
            quantities = request.POST.getlist('quantity[]')
            scrap_rates = request.POST.getlist('scrap_percentage[]')
            stages = request.POST.getlist('stage[]')
            notes_list = request.POST.getlist('notes[]')

            for i in range(len(components)):
                comp_id = components[i]
                if comp_id:
                    qty = quantities[i] if i < len(quantities) and quantities[i] else 1.0
                    scrap = scrap_rates[i] if i < len(scrap_rates) and scrap_rates[i] else 0.0
                    stg_id = stages[i] if i < len(stages) and stages[i] else None
                    nt = notes_list[i] if i < len(notes_list) else ''

                    BOMItem.objects.create(
                        bom=bom,
                        component_id=comp_id,
                        quantity=qty,
                        scrap_percentage=scrap,
                        stage_id=stg_id if stg_id else None,
                        notes=nt
                    )
            messages.success(request, f"ساختار درخت محصول {bom.bom_code} ویرایش گردید.")
            return redirect('production:bom_detail', pk=bom.pk)
    else:
        form = BOMForm(instance=bom)
    products = Product.objects.all().order_by('name')
    stages = WorkStage.objects.all().order_by('code')
    existing_items = bom.items.all().select_related('component', 'stage')
    return render(request, 'production/bom_edit.html', {
        'form': form,
        'bom': bom,
        'products': products,
        'stages': stages,
        'existing_items': existing_items
    })


@login_required
def bom_delete(request, pk):
    bom = get_object_or_404(BOM, pk=pk)
    if request.method == 'POST':
        code = bom.bom_code
        bom.delete()
        messages.success(request, f"ساختار درخت BOM {code} حذف شد.")
        return redirect('production:bom_list')
    return render(request, 'production/bom_confirm_delete.html', {'bom': bom})


@login_required
def bom_explosion(request):
    """انفجار مواد اولیه (BOM Explosion / MRP)"""
    selected_product_id = request.GET.get('product_id', '')
    selected_order_id = request.GET.get('order_id', '')
    batch_quantity = request.GET.get('quantity', '1000')

    try:
        batch_qty = float(batch_quantity)
    except Exception:
        batch_qty = 1000.0

    selected_product = None
    selected_order = None
    explosion_results = []
    has_bom = True

    if selected_order_id:
        from orders.models import Order
        selected_order = Order.objects.filter(id=selected_order_id).first()
        if selected_order and selected_order.items.exists():
            first_item = selected_order.items.first()
            selected_product = first_item.product
            batch_qty = float(first_item.quantity)

    elif selected_product_id:
        selected_product = Product.objects.filter(id=selected_product_id).first()

    if selected_product:
        active_bom = BOM.objects.filter(product=selected_product, is_active=True).first()
        if not active_bom:
            active_bom = BOM.objects.filter(product=selected_product).first()

        if active_bom:
            items = active_bom.items.all().select_related('component', 'stage')
            for item in items:
                comp = item.component
                net_req = float(item.quantity) * batch_qty
                scrap_rate = float(item.scrap_percentage)
                gross_req = net_req * (1.0 + (scrap_rate / 100.0))
                real_stock = float(comp.real_stock)
                shortage = gross_req - real_stock if gross_req > real_stock else 0.0

                explosion_results.append({
                    'component': comp,
                    'unit': comp.unit,
                    'stage': item.stage,
                    'unit_usage': float(item.quantity),
                    'net_required': round(net_req, 2),
                    'scrap_percentage': scrap_rate,
                    'gross_required': round(gross_req, 2),
                    'current_stock': round(real_stock, 2),
                    'shortage': round(shortage, 2),
                    'is_deficient': shortage > 0,
                })
        else:
            has_bom = False

    all_products = Product.objects.all().order_by('name')
    from orders.models import Order
    all_orders = Order.objects.filter(status__in=['registered', 'production']).order_by('-id')[:20]

    return render(request, 'production/bom_explosion.html', {
        'products': all_products,
        'orders': all_orders,
        'selected_product': selected_product,
        'selected_order': selected_order,
        'batch_quantity': batch_qty,
        'explosion_results': explosion_results,
        'has_bom': has_bom,
    })


# =====================================================================
# کنترل کیفیت (QC)
# =====================================================================

@login_required
def qc_list(request):
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')

    qc_records = QualityControl.objects.all().select_related('product', 'order', 'planning', 'inspector', 'warehouse')

    if query:
        qc_records = qc_records.filter(
            Q(qc_code__icontains=query) |
            Q(product__name__icontains=query) |
            Q(product__code__icontains=query) |
            Q(defect_reason__icontains=query)
        )
    if type_filter:
        qc_records = qc_records.filter(inspection_type=type_filter)
    if status_filter:
        qc_records = qc_records.filter(status=status_filter)

    total_inspected = qc_records.aggregate(Sum('inspected_quantity'))['inspected_quantity__sum'] or 0
    total_passed = qc_records.aggregate(Sum('passed_quantity'))['passed_quantity__sum'] or 0
    total_rejected = qc_records.aggregate(Sum('rejected_quantity'))['rejected_quantity__sum'] or 0
    overall_pass_rate = round((float(total_passed) / float(total_inspected) * 100), 1) if total_inspected > 0 else 100.0

    return render(request, 'production/qc_list.html', {
        'qc_records': qc_records,
        'query': query,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'total_inspected': total_inspected,
        'total_passed': total_passed,
        'total_rejected': total_rejected,
        'overall_pass_rate': overall_pass_rate,
        'inspection_types': QualityControl.INSPECTION_TYPES,
        'status_choices': QualityControl.STATUS_CHOICES,
    })


@login_required
def qc_detail(request, pk):
    qc = get_object_or_404(QualityControl.objects.select_related('product', 'order', 'planning', 'inspector', 'warehouse'), pk=pk)
    return render(request, 'production/qc_detail.html', {'qc': qc})


@login_required
def qc_create(request):
    if request.method == 'POST':
        form = QualityControlForm(request.POST)
        if form.is_valid():
            qc = form.save(commit=False)
            if not qc.inspector:
                qc.inspector = request.user
            qc.save()
            messages.success(request, f"برگه کنترل کیفیت {qc.qc_code} با موفقیت ثبت شد.")
            return redirect('production:qc_list')
        else:
            messages.error(request, "لطفاً خطاهای فرم را برطرف نمایید.")
    else:
        form = QualityControlForm()
    return render(request, 'production/qc_create.html', {'form': form})


@login_required
def qc_edit(request, pk):
    qc = get_object_or_404(QualityControl, pk=pk)
    if request.method == 'POST':
        form = QualityControlForm(request.POST, instance=qc)
        if form.is_valid():
            form.save()
            messages.success(request, f"برگه کنترل کیفیت {qc.qc_code} بروزرسانی شد.")
            return redirect('production:qc_list')
    else:
        form = QualityControlForm(instance=qc)
    return render(request, 'production/qc_edit.html', {'form': form, 'qc': qc})


@login_required
def qc_delete(request, pk):
    qc = get_object_or_404(QualityControl, pk=pk)
    if request.method == 'POST':
        code = qc.qc_code
        qc.delete()
        messages.success(request, f"برگه کنترل کیفیت {code} حذف شد.")
        return redirect('production:qc_list')
    return render(request, 'production/qc_confirm_delete.html', {'qc': qc})

