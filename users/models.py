from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    
    # تجاری و بازرگانی
    access_orders = models.BooleanField(default=False, verbose_name="دسترسی به سفارشات")
    access_customers = models.BooleanField(default=False, verbose_name="دسترسی به مشتریان")
    
    # کالا و انبار
    access_products = models.BooleanField(default=False, verbose_name="دسترسی به محصولات")
    access_warehouse = models.BooleanField(default=False, verbose_name="دسترسی به انبار و موجودی")
    
    # تولید (تفکیک دقیق و مستقل بخش‌ها)
    access_production = models.BooleanField(default=False, verbose_name="مدیریت ارشد تولید (دسترسی کامل به کل بخش تولید)")
    access_production_planning = models.BooleanField(default=False, verbose_name="دسترسی به برنامه‌ریزی تولید")
    access_production_execution = models.BooleanField(default=False, verbose_name="دسترسی به ثبت عملکرد/کارکرد شیفت (سرپرست واحد)")
    access_production_machines = models.BooleanField(default=False, verbose_name="دسترسی به ماشین‌آلات و تجهیزات")
    access_production_operators = models.BooleanField(default=False, verbose_name="دسترسی به اپراتورها و پرسنل تولید")
    access_production_stages = models.BooleanField(default=False, verbose_name="دسترسی به مراحل کاری و خطوط تولید")
    access_production_bom = models.BooleanField(default=False, verbose_name="دسترسی به ساختار درخت محصول (BOM) و MRP")
    access_production_qc = models.BooleanField(default=False, verbose_name="دسترسی به کنترل کیفیت (QC)")
    access_production_maintenance = models.BooleanField(default=False, verbose_name="دسترسی به تعمیر و نگهداری (نت)")
    
    # گزارشات و ادمین
    access_reports = models.BooleanField(default=False, verbose_name="دسترسی به گزارشات")
    is_admin_user = models.BooleanField(default=False, verbose_name="مدیریت کاربران (ادمین)")

    def __str__(self):
        return f"پروفایل {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
