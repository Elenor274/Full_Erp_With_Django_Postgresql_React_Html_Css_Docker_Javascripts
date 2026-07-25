from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # مسیرهای core (شامل login و dashboard)
    path('', include(('core.urls', 'core'), namespace='core')),

    # مسیرهای customers
    path('customers/', include(('customers.urls', 'customers'), namespace='customers')),

    # مسیرهای orders
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),

    # مسیرهای products
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # مسیرهای warehouse
    path('warehouse/', include(('warehouse.urls', 'warehouse'), namespace='warehouse')),

    # مسیرهای production (برنامه‌ریزی، ماشین‌آلات، اپراتورها و مراحل کاری)
    path('production/', include(('production.urls', 'production'), namespace='production')),

    # مسیرهای کاربران
    path('users/', include(('users.urls', 'users'), namespace='users')),
]

# سرو کردن فایل‌های static و media در حالت توسعه و سرور
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
