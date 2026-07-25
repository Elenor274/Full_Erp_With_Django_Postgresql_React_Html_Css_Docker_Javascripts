from django.db import models
from django.contrib.auth.models import User


class ProductGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="گروه کالا")

    class Meta:
        verbose_name = "گروه کالا"
        verbose_name_plural = "گروه‌های کالا"

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ("عدد", "عدد"),
        ("کیلوگرم", "کیلوگرم"),
        ("بسته", "بسته"),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="کد کالا")
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, verbose_name="گروه کالا")
    name = models.CharField(max_length=200, verbose_name="شرح کالا")

    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, verbose_name="واحد سنجش")
    initial_stock = models.PositiveIntegerField(default=0, verbose_name="موجودی اولیه")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت واحد")

    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    current_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="کاربر جاری")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین تغییر")

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_stock_in(self):
        from warehouse.models import StockTransaction
        total = StockTransaction.objects.filter(product=self, type="IN").aggregate(
            models.Sum("quantity")
        )["quantity__sum"] or 0
        return float(self.initial_stock) + float(total)

    @property
    def total_stock_out(self):
        from warehouse.models import StockTransaction
        total = StockTransaction.objects.filter(product=self, type="OUT").aggregate(
            models.Sum("quantity")
        )["quantity__sum"] or 0
        return float(total)

    @property
    def stock_balance(self):
        """
        مانده موجودی = (موجودی اولیه + مجموع ورودی‌های انبار/تولید) - (مجموع خروجی‌های انبار/مصرف تولید)
        """
        return self.total_stock_in - self.total_stock_out

    @property
    def real_stock(self):
        return self.stock_balance
