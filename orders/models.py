import os
from django.db import models
from customers.models import Customer
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('registered', 'ثبت شده'),
        ('cutting', 'برش'),
        ('sewing', 'دوخت'),
        ('quality', 'کنترل کیفیت'),
        ('warehouse', 'انبار'),
        ('delivered', 'تحویل داده شد'),
        ('cancelled', 'لغو شده'),
    ]

    order_code = models.CharField(max_length=20, unique=True, verbose_name='کد سفارش')
    sepidar_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='کد سپیدار')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='مشتری')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name='وضعیت')
    order_date = models.DateField(blank=True, null=True, verbose_name='تاریخ سفارش‌گذاری')
    delivery_date = models.DateField(blank=True, null=True, verbose_name='تاریخ ارسال سفارش')
    description = models.TextField(blank=True, verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین ویرایش')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']

    @property
    def order_date_jalali(self):
        if not self.order_date:
            return ""
        import jdatetime
        try:
            return jdatetime.date.fromgregorian(date=self.order_date).strftime("%Y/%m/%d")
        except Exception:
            return ""

    @property
    def delivery_date_jalali(self):
        if not self.delivery_date:
            return ""
        import jdatetime
        try:
            return jdatetime.date.fromgregorian(date=self.delivery_date).strftime("%Y/%m/%d")
        except Exception:
            return ""

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"{self.order_code} - {self.customer.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="محصول")

    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    weight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='وزن (KG)')
    model_name = models.CharField(max_length=100, blank=True, verbose_name='مدل')
    color = models.CharField(max_length=100, blank=True, verbose_name='رنگ')

    @property
    def total_price(self):
        return self.quantity * self.product.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderDesignFile(models.Model):
    """مدل ذخیره‌سازی نقشه‌ها و فایل‌های واحد طراحی (Photoshop, Catia, AutoCAD, PDF و...)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='design_files', verbose_name='سفارش مرتبط')
    file = models.FileField(upload_to='order_drawings/%Y/%m/', verbose_name='فایل نقشه / طراحی')
    title = models.CharField(max_length=255, blank=True, verbose_name='عنوان / توضیحات نقشه')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ بارگذاری')

    class Meta:
        verbose_name = 'نقشه واحد طراحی'
        verbose_name_plural = 'نقشه‌های واحد طراحی'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} ({self.order.order_code})"

    @property
    def file_name(self):
        if self.file and hasattr(self.file, 'name'):
            return os.path.basename(self.file.name)
        return ''

    @property
    def extension(self):
        if not self.file:
            return ''
        return os.path.splitext(self.file.name)[1].lower().replace('.', '')

    @property
    def file_type_info(self):
        ext = self.extension
        if ext in ['psd']:
            return {'label': 'Photoshop (PSD)', 'badge': 'bg-primary text-white', 'icon': 'image'}
        elif ext in ['dwg', 'dxf']:
            return {'label': 'AutoCAD (DWG/DXF)', 'badge': 'bg-danger text-white', 'icon': 'layers'}
        elif ext in ['catpart', 'catproduct', 'catdrawing']:
            return {'label': 'CATIA (3D/2D)', 'badge': 'bg-warning text-dark', 'icon': 'box'}
        elif ext in ['sldprt', 'sldasm', 'slddrw']:
            return {'label': 'SolidWorks', 'badge': 'bg-danger text-white', 'icon': 'cpu'}
        elif ext in ['step', 'stp', 'igs', 'iges']:
            return {'label': '3D CAD (STEP/IGES)', 'badge': 'bg-info text-dark', 'icon': 'box'}
        elif ext in ['pdf']:
            return {'label': 'سند PDF', 'badge': 'bg-danger text-white', 'icon': 'file-text'}
        elif ext in ['png', 'jpg', 'jpeg', 'webp']:
            return {'label': 'تصویر (Image)', 'badge': 'bg-success text-white', 'icon': 'image'}
        elif ext in ['zip', 'rar', '7z']:
            return {'label': 'فایل فشرده (ZIP/RAR)', 'badge': 'bg-secondary text-white', 'icon': 'archive'}
        else:
            return {'label': ext.upper() if ext else 'فایل فنی', 'badge': 'bg-dark text-white', 'icon': 'file'}

    @property
    def file_size_display(self):
        try:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except Exception:
            return "نامشخص"

