from django.db import models, transaction
from django.contrib.auth.models import User
from orders.models import Order
from products.models import Product
from warehouse.models import Warehouse, StockItem, StockTransaction

class Machine(models.Model):
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('repair', 'در حال تعمیر'),
        ('inactive', 'غیرفعال'),
    ]

    machine_code = models.CharField(max_length=50, unique=True, verbose_name="کد ماشین")
    name = models.CharField(max_length=100, verbose_name="نام ماشین")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "ماشین"
        verbose_name_plural = "ماشین‌آلات"

    def __str__(self):
        return f"{self.machine_code} - {self.name} ({self.get_status_display()})"


class Operator(models.Model):
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('leave', 'مرخصی'),
        ('inactive', 'غیرفعال'),
    ]

    operator_code = models.CharField(max_length=50, unique=True, verbose_name="کد اپراتور")
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="شماره تماس")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت")

    class Meta:
        verbose_name = "اپراتور"
        verbose_name_plural = "اپراتورها"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.operator_code})"


class WorkStage(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="کد مرحله")
    name = models.CharField(max_length=100, verbose_name="نام مرحله کاری")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "مرحله کاری"
        verbose_name_plural = "مراحل کاری"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Planning(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار شروع'),
        ('producing', 'در حال تولید'),
        ('completed', 'تکمیل شده'),
        ('suspended', 'متوقف شده'),
    ]

    planning_code = models.CharField(max_length=50, unique=True, verbose_name="کد برنامه‌ریزی")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="سفارش مرتبط")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_plans', verbose_name="محصول تولیدی")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="ماشین")
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, verbose_name="اپراتور")
    stage = models.ForeignKey(WorkStage, on_delete=models.CASCADE, verbose_name="مرحله تولید")
    
    target_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مقدار هدف تولید")
    produced_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مقدار تولید شده واقعی")
    
    # کسر اتوماتیک مواد اولیه از انبار
    raw_material = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='planning_raw_materials', verbose_name="مواد اولیه مصرفی")
    raw_material_qty = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مقدار مواد اولیه مصرفی")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="انبار مبدا مواد اولیه")
    material_deducted = models.BooleanField(default=False, verbose_name="آیا مواد اولیه کسر شده است؟")

    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت برنامه‌ریزی")
    stoppage_reason = models.TextField(blank=True, null=True, verbose_name="علت توقف")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "برنامه‌ریزی تولید"
        verbose_name_plural = "برنامه‌ریزی‌های تولید"
        ordering = ['-start_date', '-created_at']

    @property
    def start_date_jalali(self):
        if not self.start_date:
            return ""
        import jdatetime
        try:
            return jdatetime.date.fromgregorian(date=self.start_date).strftime("%Y/%m/%d")
        except Exception:
            return ""

    @property
    def end_date_jalali(self):
        if not self.end_date:
            return ""
        import jdatetime
        try:
            return jdatetime.date.fromgregorian(date=self.end_date).strftime("%Y/%m/%d")
        except Exception:
            return ""

    def __str__(self):
        return f"{self.planning_code} - {self.product.name} ({self.get_status_display()})"

    def deduct_inventory(self, user=None):
        """
        کسر اتوماتیک مواد اولیه از انبار مشخص شده.
        این متد با استفاده از تراکنش دیتابیس اجرا می‌شود تا از ثبات موجودی مطمئن شویم.
        """
        if self.material_deducted:
            return False, "مواد اولیه قبلاً از انبار کسر شده است."

        try:
            with transaction.atomic():
                # قفل کردن ردیف موجودی برای جلوگیری از Race Conditions
                stock_item, created = StockItem.objects.select_for_update().get_or_create(
                    warehouse=self.warehouse,
                    product=self.raw_material,
                    defaults={'quantity': 0}
                )

                # کسر موجودی (در صورت نیاز به بررسی منفی شدن می‌توان شرط گذاشت ولی برای انعطاف سیستم اجازه ثبت منفی با هشدار هم داده می‌شود)
                stock_item.quantity -= self.raw_material_qty
                stock_item.save()

                # ثبت سند خروجی انبار (StockTransaction)
                StockTransaction.objects.create(
                    warehouse=self.warehouse,
                    product=self.raw_material,
                    type=StockTransaction.OUT,
                    quantity=self.raw_material_qty,
                    unit=self.raw_material.unit,
                    transaction_category='production',
                    reference=f"برنامه‌ریزی {self.planning_code}",
                    user=user,
                )

                # علامت‌گذاری برنامه‌ریزی به عنوان کسر شده
                self.material_deducted = True
                self.save()

                return True, "کسر موجودی با موفقیت انجام شد."
        except Exception as e:
            return False, f"خطا در کسر موجودی: {str(e)}"

    def complete_production(self, user=None):
        """
        تکمیل ساخت محصول و اضافه کردن محصول نهایی تولید شده به انبار محصولات نهایی
        همچنین به‌روزرسانی خودکار وضعیت سفارش مرتبط در صورت تکمیل تمام برنامه‌ریزی‌های سفارش
        """
        messages_list = []
        # ۱. کسر مواد اولیه در صورت عدم کسر قبلی
        if not self.material_deducted:
            success, msg = self.deduct_inventory(user=user)
            messages_list.append(msg)

        # ۲. رسید محصول نهایی به انبار محصولات نهایی
        fg_warehouse = Warehouse.objects.filter(warehouse_type='finished_goods').first()
        if not fg_warehouse:
            fg_warehouse = Warehouse.objects.first()

        if fg_warehouse and self.produced_quantity > 0:
            ref_str = f"رسید تولید {self.planning_code}"
            already_received = StockTransaction.objects.filter(
                warehouse=fg_warehouse,
                product=self.product,
                type=StockTransaction.IN,
                reference=ref_str
            ).exists()

            if not already_received:
                try:
                    with transaction.atomic():
                        stock_item, _ = StockItem.objects.select_for_update().get_or_create(
                            warehouse=fg_warehouse,
                            product=self.product,
                            defaults={'quantity': 0}
                        )
                        stock_item.quantity += self.produced_quantity
                        stock_item.save()

                        StockTransaction.objects.create(
                            warehouse=fg_warehouse,
                            product=self.product,
                            type=StockTransaction.IN,
                            quantity=self.produced_quantity,
                            unit=self.product.unit,
                            transaction_category='production',
                            reference=ref_str,
                            user=user,
                        )
                        messages_list.append(f"مقدار {self.produced_quantity} {self.product.unit} به انبار {fg_warehouse.name} اضافه شد.")
                except Exception as e:
                    messages_list.append(f"خطا در رسید محصول به انبار: {str(e)}")

        # ۳. به‌روزرسانی وضعیت سفارش
        if self.order:
            all_plans = Planning.objects.filter(order=self.order)
            if all_plans.exists() and all(p.status == 'completed' for p in all_plans):
                self.order.status = 'warehouse'
                self.order.save()
                messages_list.append(f"وضعیت سفارش #{self.order.order_code} به «انبار» تغییر یافت.")

        return True, " / ".join(messages_list) if messages_list else "تولید با موفقیت تکمیل شد."


class MaintenanceActivity(models.Model):
    REPAIR_TYPES = [
        ('emergency', 'تعمیر اضطراری (EM)'),
        ('preventive', 'نگهداری پیشگیرانه (PM)'),
        ('periodic', 'سرویس دوره‌ای'),
        ('overhaul', 'اورهال / بازسازی'),
        ('other', 'سایر موارد'),
    ]

    DEPARTMENTS = [
        ('machining', 'واحد ماشینکاری'),
        ('weaving', 'واحد بافندگی'),
        ('spinning', 'واحد ریسندگی'),
        ('cutting', 'واحد برشکاری'),
        ('sewing', 'واحد دوخت'),
        ('dyeing', 'واحد رنگرزی'),
        ('finishing', 'واحد تکمیل'),
        ('other', 'سایر واحدها'),
    ]

    maintenance_code = models.CharField(max_length=50, unique=True, verbose_name="شماره / کد درخواست نت")
    date = models.DateField(verbose_name="تاریخ اعلام درخواست")
    
    # کد دستگاه و نام دستگاه
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name="دستگاه")
    
    # محل استقرار (به طور اتوماتیک یا دستی)
    location = models.CharField(max_length=150, blank=True, null=True, verbose_name="محل استقرار")
    
    # اپراتور
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="اپراتور")
    
    # توقف دارد / ندارد
    has_stoppage = models.BooleanField(default=False, verbose_name="توقف خط تولید (دارد/ندارد)")
    
    # ساعت اعلام
    notification_time = models.TimeField(verbose_name="ساعت اعلام درخواست")
    
    # مهلت انجام
    deadline_date = models.DateField(verbose_name="مهلت انجام")
    
    # زمان تقریبی (چند روز)
    estimated_days = models.PositiveIntegerField(default=1, verbose_name="زمان تقریبی (روز)")
    
    # درخواست کننده
    requester_unit = models.CharField(max_length=50, choices=DEPARTMENTS, default='machining', verbose_name="واحد درخواست‌کننده")
    
    # نوع تعمیر
    repair_type = models.CharField(max_length=30, choices=REPAIR_TYPES, default='emergency', verbose_name="نوع تعمیر")
    
    # حالت‌های خرابی (تیک‌زدنی)
    failure_electrical = models.BooleanField(default=False, verbose_name="خرابی برقی")
    failure_mechanical = models.BooleanField(default=False, verbose_name="خرابی مکانیکی")
    failure_hydraulic = models.BooleanField(default=False, verbose_name="خرابی هیدرولیک")
    failure_utilities = models.BooleanField(default=False, verbose_name="خرابی تاسیساتی")
    failure_other = models.BooleanField(default=False, verbose_name="سایر موارد خرابی")
    
    # گروه اجرایی
    execution_group = models.CharField(max_length=100, default="واحد تعمیرات و نگهداری (نت)", verbose_name="گروه اجرایی تعمیر")
    
    # آیا رفع عیب داخل شرکت امکان‌پذیر است؟
    internal_repair_possible = models.BooleanField(default=True, verbose_name="امکان رفع عیب داخل شرکت")
    external_repair_reason = models.TextField(blank=True, null=True, verbose_name="علت عدم امکان رفع در شرکت")
    
    # روند انجام تعمیرات
    start_date = models.DateField(blank=True, null=True, verbose_name="تاریخ شروع تعمیر")
    start_time = models.TimeField(blank=True, null=True, verbose_name="ساعت شروع تعمیر")
    
    activity_description = models.TextField(blank=True, null=True, verbose_name="شرح کامل فعالیت")
    consumables_used = models.TextField(blank=True, null=True, verbose_name="قطعات مصرفی مورد نیاز")
    
    end_date = models.DateField(blank=True, null=True, verbose_name="تاریخ پایان تعمیر")
    end_time = models.TimeField(blank=True, null=True, verbose_name="ساعت پایان تعمیر")
    
    # مجموع توقف (محاسبه اتوماتیک)
    total_stoppage_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="مجموع ساعت توقف")
    
    # بازدید بعدی / چک‌آپ دوره‌ای
    next_checkup_date = models.DateField(blank=True, null=True, verbose_name="تاریخ بازدید دوره‌ای بعدی")
    next_checkup_time = models.TimeField(blank=True, null=True, verbose_name="ساعت بازدید دوره‌ای بعدی")
    
    # تاییدات
    manager_approved = models.BooleanField(default=False, verbose_name="تایید مسئول نت")
    requester_approved = models.BooleanField(default=False, verbose_name="تایید درخواست‌کننده")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "درخواست نت (نگهداری و تعمیرات)"
        verbose_name_plural = "درخواست‌های نت (نگهداری و تعمیرات)"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.maintenance_code} - {self.machine.name} ({self.get_repair_type_display()})"

    @property
    def date_jalali(self):
        return self._to_jalali(self.date)

    @property
    def deadline_date_jalali(self):
        return self._to_jalali(self.deadline_date)

    @property
    def start_date_jalali(self):
        return self._to_jalali(self.start_date)

    @property
    def end_date_jalali(self):
        return self._to_jalali(self.end_date)

    @property
    def next_checkup_date_jalali(self):
        return self._to_jalali(self.next_checkup_date)

    def _to_jalali(self, date_field):
        if not date_field:
            return ""
        import jdatetime
        try:
            jd = jdatetime.date.fromgregorian(date=date_field)
            return jd.strftime("%Y/%m/%d")
        except Exception:
            return ""

    def save(self, *args, **kwargs):
        # تولید خودکار کد در صورت عدم وجود
        if not self.maintenance_code:
            import jdatetime
            try:
                year = jdatetime.date.today().year
            except Exception:
                year = 1405
            
            last_record = MaintenanceActivity.objects.all().order_by('id').last()
            if last_record:
                last_id = last_record.id
            else:
                last_id = 0
            
            self.maintenance_code = f"MNT-{year}-{last_id + 1:04d}"

        # محاسبه اتوماتیک زمان توقف کل به ساعت
        if self.start_date and self.end_date:
            import datetime
            try:
                start_dt = datetime.datetime.combine(self.start_date, self.start_time or datetime.time(0, 0))
                end_dt = datetime.datetime.combine(self.end_date, self.end_time or datetime.time(0, 0))
                
                duration = end_dt - start_dt
                total_hours = duration.total_seconds() / 3600.0
                if total_hours < 0:
                    total_hours = 0
                self.total_stoppage_hours = round(total_hours, 2)
            except Exception:
                pass
        super().save(*args, **kwargs)


class BOM(models.Model):
    bom_code = models.CharField(max_length=50, unique=True, verbose_name="کد ساختار BOM")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='boms', verbose_name="محصول اصلی (پایه)")
    title = models.CharField(max_length=150, verbose_name="عنوان فرمول / ساختار درخت")
    is_active = models.BooleanField(default=True, verbose_name="نسخه فعال / اصلی")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات و ملاحظات فنی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ساختار درخت محصول (BOM)"
        verbose_name_plural = "ساختار درخت محصولات (BOM)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bom_code} - {self.product.name} ({self.title})"

    def save(self, *args, **kwargs):
        if not self.bom_code:
            import jdatetime
            try:
                year = jdatetime.date.today().year
            except Exception:
                year = 1405
            last_record = BOM.objects.all().order_by('id').last()
            last_id = last_record.id if last_record else 0
            self.bom_code = f"BOM-{year}-{last_id + 1:04d}"
        super().save(*args, **kwargs)

    @property
    def total_components_count(self):
        return self.items.count()


class BOMItem(models.Model):
    bom = models.ForeignKey(BOM, on_delete=models.CASCADE, related_name='items', verbose_name="ساختار درخت BOM")
    component = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_usages', verbose_name="ماده اولیه / قطعه")
    quantity = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="مقدار مصرف استاندارد (به ازای ۱ واحد محصول)")
    scrap_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="درصد ضایعات / پرتی (%)")
    stage = models.ForeignKey(WorkStage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="مرحله مصرف کاری")
    notes = models.CharField(max_length=255, blank=True, null=True, verbose_name="ملاحظات قطعه")

    class Meta:
        verbose_name = "قلم BOM"
        verbose_name_plural = "اقلام BOM"

    def __str__(self):
        return f"{self.component.name} ({self.quantity} {self.component.unit})"

    @property
    def gross_quantity_per_unit(self):
        from decimal import Decimal
        return self.quantity * (Decimal('1.0') + (self.scrap_percentage / Decimal('100.0')))


class QualityControl(models.Model):
    INSPECTION_TYPES = [
        ('incoming', 'ورودی مواد اولیه (IQC)'),
        ('in_process', 'حین تولید (PQC)'),
        ('finished', 'محصول نهایی (FQC)'),
    ]

    STATUS_CHOICES = [
        ('passed', 'تایید شده (سالم)'),
        ('conditional', 'تایید مشروط'),
        ('rejected', 'مردود / ضایعات'),
    ]

    ACTION_CHOICES = [
        ('accept', 'ورود به انبار اصلی'),
        ('rework', 'ارجاع به دوباره‌کاری'),
        ('scrap', 'انتقال به انبار ضایعات'),
        ('return', 'مرجوع به تامین‌کننده'),
    ]

    qc_code = models.CharField(max_length=50, unique=True, verbose_name="شماره برگه QC")
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPES, default='in_process', verbose_name="نوع بازرسی")
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="کالا / محصول بازرسی شده")
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="سفارش مرتبط")
    planning = models.ForeignKey(Planning, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="برنامه‌ریزی تولید مرتبط")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="انبار مربوطه")
    
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="بازرس کیفیت")
    inspection_date = models.DateField(verbose_name="تاریخ بازرسی")
    
    inspected_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="کل مقدار بازرسی شده")
    passed_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مقدار سالم / تایید شده")
    rejected_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مقدار ضایعات / مردودی")
    rework_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مقدار نیازمند دوباره‌کاری")
    
    defect_reason = models.CharField(max_length=255, blank=True, null=True, verbose_name="نوع عیب / علت عدم تایید")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='passed', verbose_name="نتیجه بازرسی")
    action_taken = models.CharField(max_length=20, choices=ACTION_CHOICES, default='accept', verbose_name="اقدام انجام شده")
    notes = models.TextField(blank=True, null=True, verbose_name="توضیحات فنی بازرس")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "برگه کنترل کیفیت (QC)"
        verbose_name_plural = "برگه‌های کنترل کیفیت (QC)"
        ordering = ['-inspection_date', '-created_at']

    def __str__(self):
        return f"{self.qc_code} - {self.product.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.qc_code:
            import jdatetime
            try:
                year = jdatetime.date.today().year
            except Exception:
                year = 1405
            last_record = QualityControl.objects.all().order_by('id').last()
            last_id = last_record.id if last_record else 0
            self.qc_code = f"QC-{year}-{last_id + 1:04d}"
        super().save(*args, **kwargs)

    @property
    def pass_rate(self):
        if self.inspected_quantity and self.inspected_quantity > 0:
            return round((float(self.passed_quantity) / float(self.inspected_quantity)) * 100, 1)
        return 0.0

    @property
    def defect_rate(self):
        if self.inspected_quantity and self.inspected_quantity > 0:
            return round((float(self.rejected_quantity) / float(self.inspected_quantity)) * 100, 1)
        return 0.0


