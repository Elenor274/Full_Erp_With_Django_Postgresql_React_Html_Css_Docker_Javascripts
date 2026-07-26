from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile

def fa_to_en_digits(text):
    if not text:
        return text
    fa_digits = '۰۱۲۳۴۵۶۷۸۹'
    ar_digits = '٠١٢٣٤٥٦٧٨٩'
    en_digits = '0123456789'
    trans_table = str.maketrans(fa_digits + ar_digits, en_digits * 2)
    return text.translate(trans_table)

class CustomAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')
        return fa_to_en_digits(username).strip() if username else username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return fa_to_en_digits(password) if password else password

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True, label="رمز عبور")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True, label="تکرار رمز عبور")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("رمزهای عبور وارد شده همخوانی ندارند.")
        return cleaned_data

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'access_orders',
            'access_customers',
            'access_products',
            'access_warehouse',
            'access_production',
            'access_production_planning',
            'access_production_execution',
            'access_production_machines',
            'access_production_operators',
            'access_production_stages',
            'access_production_bom',
            'access_production_qc',
            'access_production_maintenance',
            'access_reports',
            'is_admin_user',
        ]
        labels = {
            'access_orders': 'دسترسی به سفارشات',
            'access_customers': 'دسترسی به مشتریان',
            'access_products': 'دسترسی به محصولات',
            'access_warehouse': 'دسترسی به انبار و موجودی',
            'access_production': 'مدیریت ارشد تولید (دسترسی کامل)',
            'access_production_planning': 'دسترسی به برنامه‌ریزی تولید',
            'access_production_execution': 'دسترسی به ثبت عملکرد/شیفت کاری',
            'access_production_machines': 'دسترسی به ماشین‌آلات و تجهیزات',
            'access_production_operators': 'دسترسی به اپراتورها و پرسنل تولید',
            'access_production_stages': 'دسترسی به مراحل کاری و خطوط',
            'access_production_bom': 'دسترسی به درخت محصول (BOM) و MRP',
            'access_production_qc': 'دسترسی به کنترل کیفیت (QC)',
            'access_production_maintenance': 'دسترسی به درخواست‌های تعمیر (نت)',
            'access_reports': 'دسترسی به گزارشات',
            'is_admin_user': 'مدیریت کاربران (ادمین)',
        }

class PasswordChangeCustomForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True, label="رمز عبور جدید")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True, label="تکرار رمز عبور جدید")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("رمزهای عبور وارد شده همخوانی ندارند.")
        return cleaned_data
