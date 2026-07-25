from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("trace/", views.product_trace, name="product_trace"),
    path("new/", views.product_create, name="product_create"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/delete/", views.product_delete_confirm, name="product_delete_confirm"),
    path("<int:pk>/delete/confirm/", views.product_delete, name="product_delete"),
    path("<int:pk>/", views.product_detail, name="product_detail"),

    # گروه کالا
    path("groups/", views.group_list, name="group_list"),
    path("groups/new/", views.group_create, name="group_create"),
    path("groups/<int:pk>/edit/", views.group_edit, name="group_edit"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
]
