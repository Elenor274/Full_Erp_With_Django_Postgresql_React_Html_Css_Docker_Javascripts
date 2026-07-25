from django import forms
from .models import Machine, Operator, WorkStage, Planning, MaintenanceActivity, BOM, BOMItem, QualityControl
from products.models import Product
from warehouse.models import Warehouse

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['machine_code', 'name', 'status', 'description']
        widgets = {
            'machine_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: M-101'}),
            'name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'نام ماشین'}),
            'status': forms.Select(attrs={'class': 'form-control-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2}),
        }


class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = ['operator_code', 'first_name', 'last_name', 'phone_number', 'status']
        widgets = {
            'operator_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: OP-405'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': '09121234567'}),
            'status': forms.Select(attrs={'class': 'form-control-custom'}),
        }


class WorkStageForm(forms.ModelForm):
    class Meta:
        model = WorkStage
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: WEAVE'}),
            'name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: بافندگی'}),
            'description': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2}),
        }


class PlanningForm(forms.ModelForm):
    start_date = forms.CharField(
        label="تاریخ شروع",
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom jalali-date-input',
            'placeholder': '۱۴۰۵/۰۴/۲۸',
            'autocomplete': 'off'
        })
    )
    end_date = forms.CharField(
        label="تاریخ پایان",
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom jalali-date-input',
            'placeholder': '۱۴۰۵/۰۵/۰۵',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Planning
        fields = [
            'planning_code', 'order', 'product', 'machine', 'operator', 'stage',
            'target_quantity', 'produced_quantity', 'raw_material', 'raw_material_qty',
            'warehouse', 'start_date', 'end_date', 'status', 'stoppage_reason'
        ]
        widgets = {
            'planning_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: PLN-2026-001'}),
            'order': forms.Select(attrs={'class': 'form-control-custom'}),
            'product': forms.Select(attrs={'class': 'form-control-custom'}),
            'machine': forms.Select(attrs={'class': 'form-control-custom'}),
            'operator': forms.Select(attrs={'class': 'form-control-custom'}),
            'stage': forms.Select(attrs={'class': 'form-control-custom'}),
            'target_quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'produced_quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'raw_material': forms.Select(attrs={'class': 'form-control-custom'}),
            'raw_material_qty': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'warehouse': forms.Select(attrs={'class': 'form-control-custom'}),
            'status': forms.Select(attrs={'class': 'form-control-custom'}),
            'stoppage_reason': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2, 'placeholder': 'علت توقف تولید (در صورت تعلیق)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.fields['start_date'].initial = self.instance.start_date_jalali
            if self.instance.end_date:
                self.fields['end_date'].initial = self.instance.end_date_jalali
        else:
            import jdatetime
            try:
                today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
            except Exception:
                today_jalali = "1405/04/28"
            self.fields['start_date'].initial = today_jalali
            self.fields['end_date'].initial = today_jalali

    def clean_jalali_date(self, field_name, required=True):
        val = self.cleaned_data.get(field_name, '')
        if val:
            val = str(val).strip()
        if not val:
            if required:
                raise forms.ValidationError("این فیلد الزامی است.")
            return None
        try:
            import jdatetime
            farsi_to_eng = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
            val = val.translate(farsi_to_eng).replace('-', '/')
            parts = list(map(int, val.split('/')))
            if len(parts) != 3:
                raise Exception()
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            return jd.togregorian()
        except Exception:
            raise forms.ValidationError("فرمت تاریخ نامعتبر است. فرمت صحیح: ۱۴۰۵/۰۴/۲۸")

    def clean_start_date(self):
        return self.clean_jalali_date('start_date', required=True)

    def clean_end_date(self):
        return self.clean_jalali_date('end_date', required=True)


import jdatetime

class MaintenanceActivityForm(forms.ModelForm):
    # فیلدهای تاریخ به صورت رشته‌ای تا مقدار شمسی به درستی وارد و خوانده شود
    date = forms.CharField(label="تاریخ اعلام درخواست", widget=forms.TextInput(attrs={'class': 'form-control-custom jalali-date-input', 'placeholder': '۱۴۰۵/۰۴/۲۸'}))
    deadline_date = forms.CharField(label="مهلت انجام", widget=forms.TextInput(attrs={'class': 'form-control-custom jalali-date-input', 'placeholder': '۱۴۰۵/۰۴/۲۸'}))
    start_date = forms.CharField(label="تاریخ شروع تعمیر", required=False, widget=forms.TextInput(attrs={'class': 'form-control-custom jalali-date-input', 'placeholder': '۱۴۰۵/۰۴/۲۸'}))
    end_date = forms.CharField(label="تاریخ پایان تعمیر", required=False, widget=forms.TextInput(attrs={'class': 'form-control-custom jalali-date-input', 'placeholder': '۱۴۰۵/۰۴/۲۸'}))
    next_checkup_date = forms.CharField(label="تاریخ بازدید دوره‌ای بعدی", required=False, widget=forms.TextInput(attrs={'class': 'form-control-custom jalali-date-input', 'placeholder': '۱۴۰۵/۰۴/۲۸'}))

    class Meta:
        model = MaintenanceActivity
        fields = [
            'maintenance_code', 'date', 'machine', 'location', 'operator', 'has_stoppage',
            'notification_time', 'deadline_date', 'estimated_days', 'requester_unit',
            'repair_type', 'failure_electrical', 'failure_mechanical', 'failure_hydraulic',
            'failure_utilities', 'failure_other', 'execution_group', 'internal_repair_possible',
            'external_repair_reason', 'start_date', 'start_time', 'activity_description',
            'consumables_used', 'end_date', 'end_time', 'total_stoppage_hours',
            'next_checkup_date', 'next_checkup_time', 'manager_approved', 'requester_approved'
        ]
        widgets = {
            'maintenance_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'در صورت خالی بودن خودکار تولید می‌شود'}),
            'machine': forms.Select(attrs={'class': 'form-control-custom', 'id': 'id_machine'}),
            'location': forms.TextInput(attrs={'class': 'form-control-custom', 'id': 'id_location', 'placeholder': 'محل استقرار دستگاه'}),
            'operator': forms.Select(attrs={'class': 'form-control-custom'}),
            'has_stoppage': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'notification_time': forms.TimeInput(attrs={'class': 'form-control-custom', 'type': 'time'}),
            'estimated_days': forms.NumberInput(attrs={'class': 'form-control-custom', 'min': '0'}),
            'requester_unit': forms.Select(attrs={'class': 'form-control-custom'}),
            'repair_type': forms.Select(attrs={'class': 'form-control-custom'}),
            'failure_electrical': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'failure_mechanical': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'failure_hydraulic': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'failure_utilities': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'failure_other': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'execution_group': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'مثال: واحد برق کارخانه'}),
            'internal_repair_possible': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'external_repair_reason': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2, 'placeholder': 'علت عدم امکان رفع عیب در شرکت'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control-custom', 'type': 'time'}),
            'activity_description': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3, 'placeholder': 'شرح اقدامات انجام شده...'}),
            'consumables_used': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2, 'placeholder': 'مثال: بلبرینگ ۶۲۰۴، تسمه A42'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control-custom', 'type': 'time'}),
            'total_stoppage_hours': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01', 'readonly': 'readonly', 'id': 'id_total_stoppage_hours'}),
            'next_checkup_time': forms.TimeInput(attrs={'class': 'form-control-custom', 'type': 'time'}),
            'manager_approved': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'requester_approved': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # پر کردن پیش‌فرض برای تاریخ‌های شمسی در صورت ویرایش
        if self.instance and self.instance.pk:
            if self.instance.date:
                self.fields['date'].initial = self.instance.date_jalali
            if self.instance.deadline_date:
                self.fields['deadline_date'].initial = self.instance.deadline_date_jalali
            if self.instance.start_date:
                self.fields['start_date'].initial = self.instance.start_date_jalali
            if self.instance.end_date:
                self.fields['end_date'].initial = self.instance.end_date_jalali
            if self.instance.next_checkup_date:
                self.fields['next_checkup_date'].initial = self.instance.next_checkup_date_jalali
        else:
            import jdatetime
            try:
                today_jalali = jdatetime.date.today().strftime("%Y/%m/%d")
            except Exception:
                today_jalali = "1405/04/28"
            self.fields['date'].initial = today_jalali
            self.fields['deadline_date'].initial = today_jalali

    def clean_jalali_date(self, field_name, required=True):
        val = self.cleaned_data.get(field_name, '')
        if val:
            val = str(val).strip()
        if not val:
            if required:
                raise forms.ValidationError("این فیلد الزامی است.")
            return None
        try:
            # تبدیل اعداد فارسی به انگلیسی
            farsi_to_eng = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
            val = val.translate(farsi_to_eng)
            val = val.replace('-', '/')
            parts = list(map(int, val.split('/')))
            if len(parts) != 3:
                raise Exception()
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            return jd.togregorian()
        except Exception:
            raise forms.ValidationError("فرمت تاریخ نامعتبر است. فرمت صحیح: ۱۴۰۵/۰۴/۲۸")

    def clean_date(self):
        return self.clean_jalali_date('date', required=True)

    def clean_deadline_date(self):
        return self.clean_jalali_date('deadline_date', required=True)

    def clean_start_date(self):
        return self.clean_jalali_date('start_date', required=False)

    def clean_end_date(self):
        return self.clean_jalali_date('end_date', required=False)

    def clean_next_checkup_date(self):
        return self.clean_jalali_date('next_checkup_date', required=False)


class BOMForm(forms.ModelForm):
    class Meta:
        model = BOM
        fields = ['bom_code', 'product', 'title', 'is_active', 'description']
        widgets = {
            'bom_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'خالی بگذارید تا خودکار تولید شود'}),
            'product': forms.Select(attrs={'class': 'form-control-custom'}),
            'title': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'عنوان فرمول، مانند: فرمول ساخت پارچه فاستونی درجه یک'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2, 'placeholder': 'ملاحظات مهندسی و فنی...'}),
        }


class BOMItemForm(forms.ModelForm):
    class Meta:
        model = BOMItem
        fields = ['component', 'quantity', 'scrap_percentage', 'stage', 'notes']
        widgets = {
            'component': forms.Select(attrs={'class': 'form-control-custom'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.0001', 'placeholder': 'مقدار مصرف'}),
            'scrap_percentage': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.1', 'placeholder': 'درصد پرتی'}),
            'stage': forms.Select(attrs={'class': 'form-control-custom'}),
            'notes': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'توضیحات قطعه'}),
        }


class QualityControlForm(forms.ModelForm):
    inspection_date = forms.CharField(label="تاریخ بازرسی", widget=forms.TextInput(attrs={'class': 'form-control-custom jalali-date-input', 'placeholder': '۱۴۰۵/۰۴/۲۸'}))

    class Meta:
        model = QualityControl
        fields = [
            'qc_code', 'inspection_type', 'product', 'order', 'planning',
            'warehouse', 'inspector', 'inspection_date', 'inspected_quantity',
            'passed_quantity', 'rejected_quantity', 'rework_quantity',
            'defect_reason', 'status', 'action_taken', 'notes'
        ]
        widgets = {
            'qc_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'خالی بگذارید تا خودکار تولید شود'}),
            'inspection_type': forms.Select(attrs={'class': 'form-control-custom'}),
            'product': forms.Select(attrs={'class': 'form-control-custom'}),
            'order': forms.Select(attrs={'class': 'form-control-custom'}),
            'planning': forms.Select(attrs={'class': 'form-control-custom'}),
            'warehouse': forms.Select(attrs={'class': 'form-control-custom'}),
            'inspector': forms.Select(attrs={'class': 'form-control-custom'}),
            'inspected_quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'passed_quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'rejected_quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'rework_quantity': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'defect_reason': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'علت عیب/عدم انطباق، مانند: پارگی تار، نایکنواختی نخ، لکه روغن'}),
            'status': forms.Select(attrs={'class': 'form-control-custom'}),
            'action_taken': forms.Select(attrs={'class': 'form-control-custom'}),
            'notes': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2, 'placeholder': 'ملاحظات بازرس کیفیت'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.inspection_date:
            import jdatetime
            try:
                jd = jdatetime.date.fromgregorian(date=self.instance.inspection_date)
                self.fields['inspection_date'].initial = jd.strftime("%Y/%m/%d")
            except Exception:
                pass
        else:
            import jdatetime
            try:
                self.fields['inspection_date'].initial = jdatetime.date.today().strftime("%Y/%m/%d")
            except Exception:
                self.fields['inspection_date'].initial = "1405/04/28"

    def clean_inspection_date(self):
        val = self.cleaned_data.get('inspection_date', '')
        if val:
            val = str(val).strip()
        if not val:
            raise forms.ValidationError("تاریخ بازرسی الزامی است.")
        try:
            farsi_to_eng = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
            val = val.translate(farsi_to_eng).replace('-', '/')
            parts = list(map(int, val.split('/')))
            if len(parts) != 3:
                raise Exception()
            import jdatetime
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            return jd.togregorian()
        except Exception:
            raise forms.ValidationError("فرمت تاریخ بازرسی نامعتبر است.")

