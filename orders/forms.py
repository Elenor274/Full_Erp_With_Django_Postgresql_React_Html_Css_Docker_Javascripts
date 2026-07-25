from django import forms
from .models import Order, OrderItem, OrderDesignFile
from django.forms import inlineformset_factory


import jdatetime


class OrderForm(forms.ModelForm):
    order_date = forms.CharField(
        label="تاریخ سفارش‌گذاری",
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom jalali-date-input',
            'placeholder': '۱۴۰۵/۰۴/۲۸',
            'autocomplete': 'off'
        })
    )
    delivery_date = forms.CharField(
        label="تاریخ ارسال سفارش",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom jalali-date-input',
            'placeholder': '۱۴۰۵/۰۵/۱۵',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Order
        fields = ['order_code', 'sepidar_code', 'customer', 'order_date', 'delivery_date', 'description']
        widgets = {
            'order_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: ORD-1405-01'}),
            'sepidar_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: SEP-9812'}),
            'customer': forms.Select(attrs={'class': 'form-control-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3, 'placeholder': 'توضیحات و ملاحظات سفارش...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.order_date:
                self.fields['order_date'].initial = self.instance.order_date_jalali
            if self.instance.delivery_date:
                self.fields['delivery_date'].initial = self.instance.delivery_date_jalali
        else:
            try:
                today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
            except Exception:
                today_jalali = "1405/04/28"
            self.fields['order_date'].initial = today_jalali

    def clean_jalali_date(self, field_name, required=True):
        val = self.cleaned_data.get(field_name, '')
        if val:
            val = str(val).strip()
        if not val:
            if required:
                raise forms.ValidationError("این فیلد الزامی است.")
            return None
        try:
            farsi_to_eng = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
            val = val.translate(farsi_to_eng).replace('-', '/')
            parts = list(map(int, val.split('/')))
            if len(parts) != 3:
                raise Exception()
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            return jd.togregorian()
        except Exception:
            raise forms.ValidationError("فرمت تاریخ نامعتبر است. فرمت صحیح: ۱۴۰۵/۰۴/۲۸")

    def clean_order_date(self):
        return self.clean_jalali_date('order_date', required=True)

    def clean_delivery_date(self):
        return self.clean_jalali_date('delivery_date', required=False)


class OrderDesignFileForm(forms.ModelForm):
    class Meta:
        model = OrderDesignFile
        fields = ['file', 'title']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-custom', 'accept': '.psd,.dwg,.dxf,.catpart,.catproduct,.catdrawing,.sldprt,.sldasm,.slddrw,.step,.stp,.igs,.iges,.pdf,.png,.jpg,.jpeg,.zip,.rar'}),
            'title': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'عنوان یا توضیحات نقشه (مثلاً: نقشه برش کتیا، فایل فتوشاپ چاپ، اتوکد)'}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'weight', 'model_name', 'color']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control-custom'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'placeholder': 'تعداد'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control-custom', 'placeholder': 'وزن (KG)'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: M-101'}),
            'color': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: سرمه‌ای'}),
        }


# نسخهٔ صحیح و نهایی — مخصوص ایجاد و ویرایش
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,          # یک آیتم خالی بساز تا فیلدها نمایش داده شوند
    can_delete=False  # چون دکمه حذف نداریم
)

