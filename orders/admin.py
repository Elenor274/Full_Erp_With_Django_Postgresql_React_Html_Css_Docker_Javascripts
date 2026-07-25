from django.contrib import admin
from .models import Order, OrderItem, OrderDesignFile


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderDesignFileInline(admin.TabularInline):
    model = OrderDesignFile
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'sepidar_code', 'customer', 'status', 'created_at', 'total_amount_display')
    list_filter = ('status', 'created_at')
    search_fields = ('order_code', 'sepidar_code', 'customer__name')

    inlines = [OrderItemInline, OrderDesignFileInline]

    def total_amount_display(self, obj):
        return obj.total_amount
    total_amount_display.short_description = "مبلغ کل"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'weight', 'model_name', 'color')


@admin.register(OrderDesignFile)
class OrderDesignFileAdmin(admin.ModelAdmin):
    list_display = ('order', 'file_name', 'title', 'uploaded_at')
    search_fields = ('order__order_code', 'title', 'file')

