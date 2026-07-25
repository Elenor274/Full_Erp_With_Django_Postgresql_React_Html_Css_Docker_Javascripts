from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("create/", views.order_create, name="order_create"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
    path("<int:pk>/edit/", views.order_edit, name="order_edit"),

    # آپلود و حذف نقشه‌های واحد طراحی
    path("<int:pk>/upload-design-file/", views.order_upload_design_file, name="order_upload_design_file"),
    path("design-file/<int:file_id>/delete/", views.order_delete_design_file, name="order_delete_design_file"),

    # GET → نمایش صفحه تأیید حذف
    path("<int:pk>/delete/", views.order_delete_confirm, name="order_delete_confirm"),

    # POST → انجام حذف
    path("<int:pk>/delete/confirm/", views.order_delete, name="order_delete"),
]

