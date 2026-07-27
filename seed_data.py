#!/usr/bin/env python3
import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'textile_erp.settings')
django.setup()

from django.contrib.auth.models import User
from customers.models import Customer
from products.models import ProductGroup, Product
from warehouse.models import Warehouse, StockItem, StockTransaction
from orders.models import Order, OrderItem
from production.models import Machine, Operator, WorkStage, Planning

def seed_database():
    print("Seeding database...")

    # 1. Create or Update Superuser
    user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'first_name': 'مدیر', 'last_name': 'سیستم'})
    user.set_password('admin123')
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.save()
    if created:
        print("Created superuser: admin / admin123")
    else:
        print("Updated superuser: admin / admin123")

    # 2. Create Warehouses
    wh_raw, _ = Warehouse.objects.get_or_create(
        code="WH-RAW",
        defaults={
            'name': "انبار مرکزی مواد اولیه (نخ و رنگ)",
            'description': "انبار نگهداری مواد اولیه ریسندگی و رنگرزی",
            'warehouse_type': "raw_material"
        }
    )
    wh_finished, _ = Warehouse.objects.get_or_create(
        code="WH-FIN",
        defaults={
            'name': "انبار محصولات نهایی",
            'description': "انبار نگهداری پارچه‌های بافته شده و تکمیلی",
            'warehouse_type': "finished_goods"
        }
    )
    print("Created Warehouses.")

    # 3. Create Product Groups & Products
    pg_yarn, _ = ProductGroup.objects.get_or_create(name="نخ و الیاف")
    pg_dye, _ = ProductGroup.objects.get_or_create(name="رنگ و مواد شیمیایی")
    pg_fabric, _ = ProductGroup.objects.get_or_create(name="پارچه")

    # Raw Materials (stored in raw warehouse)
    yarn_cotton, _ = Product.objects.get_or_create(
        code="Y-COT-30",
        defaults={
            'name': "نخ پنبه شانه شده نمره ۳۰",
            'group': pg_yarn,
            'unit': "کیلوگرم",
            'unit_price': 350000.00,
            'description': "نخ پنبه صد در صد طبیعی درجه یک"
        }
    )
    yarn_poly, _ = Product.objects.get_or_create(
        code="Y-POLY-150",
        defaults={
            'name': "نخ پلی‌استر ۱۵۰ دنیر",
            'group': pg_yarn,
            'unit': "کیلوگرم",
            'unit_price': 180000.00,
            'description': "نخ فیلامنت پلی‌استر نیمه مات"
        }
    )
    dye_indigo, _ = Product.objects.get_or_create(
        code="D-IND-BL",
        defaults={
            'name': "رنگ نیل پودری (Indigo)",
            'group': pg_dye,
            'unit': "کیلوگرم",
            'unit_price': 850000.00,
            'description': "رنگ مخصوص رنگرزی پارچه‌های جین"
        }
    )

    # Finished Fabrics (stored in finished warehouse)
    fabric_denim, _ = Product.objects.get_or_create(
        code="F-DNM-12",
        defaults={
            'name': "پارچه جین ۱۲ اونس کجراه",
            'group': pg_fabric,
            'unit': "کیلوگرم",  # Match choices in model
            'unit_price': 240000.00,
            'description': "پارچه جین سنگین‌وزن مناسب شلوار و کت"
        }
    )
    fabric_cotton, _ = Product.objects.get_or_create(
        code="F-COT-SH",
        defaults={
            'name': "پارچه پیراهنی پنبه‌ای عرض ۱۵۰",
            'group': pg_fabric,
            'unit': "کیلوگرم",  # Match choices in model
            'unit_price': 150000.00,
            'description': "پارچه خنک پیراهنی طرح ساده"
        }
    )
    print("Created Products.")

    # 4. Set Initial Stock in Warehouse
    stock_cotton, _ = StockItem.objects.get_or_create(
        warehouse=wh_raw,
        product=yarn_cotton,
        defaults={'quantity': 5000.00, 'min_stock': 500.00}
    )
    stock_poly, _ = StockItem.objects.get_or_create(
        warehouse=wh_raw,
        product=yarn_poly,
        defaults={'quantity': 8000.00, 'min_stock': 1000.00}
    )
    stock_dye, _ = StockItem.objects.get_or_create(
        warehouse=wh_raw,
        product=dye_indigo,
        defaults={'quantity': 1200.00, 'min_stock': 100.00}
    )

    stock_denim, _ = StockItem.objects.get_or_create(
        warehouse=wh_finished,
        product=fabric_denim,
        defaults={'quantity': 1500.00, 'min_stock': 200.00}
    )
    print("Initialized StockItems.")

    # 5. Create Customers & Orders
    cust_1, _ = Customer.objects.get_or_create(
        customer_code="CUST-101",
        defaults={
            'name': "صنایع پوشاک هاکوپیان",
            'last_name': "تهران",
            'phone_number': "02188888888"
        }
    )
    cust_2, _ = Customer.objects.get_or_create(
        customer_code="CUST-102",
        defaults={
            'name': "تولیدی پوشاک سالیان",
            'last_name': "کرج",
            'phone_number': "02634444444"
        }
    )

    order_1, _ = Order.objects.get_or_create(
        customer=cust_1,
        order_code="ORD-1402-001",
        defaults={
            'status': 'registered',
            'description': 'تولید فوری پارچه جین ۱۲ اونس برای کالکشن پاییزه'
        }
    )
    OrderItem.objects.get_or_create(
        order=order_1,
        product=fabric_denim,
        defaults={
            'quantity': 3000,
            'weight': 1200.00,
            'model_name': 'M-101 (سنگ‌شور)',
            'color': 'نیلی دودی'
        }
    )

    order_2, _ = Order.objects.get_or_create(
        customer=cust_2,
        order_code="ORD-1402-002",
        defaults={
            'status': 'registered',
            'description': 'سفارش پارچه پیراهنی پنبه‌ای'
        }
    )
    OrderItem.objects.get_or_create(
        order=order_2,
        product=fabric_cotton,
        defaults={
            'quantity': 2000,
            'weight': 800.00,
            'model_name': 'P-202 (چهارخانه)',
            'color': 'سفید آبی'
        }
    )
    print("Created Customers and Orders.")

    # 6. Create Production Assets (Machines, Operators, WorkStages)
    m_1, _ = Machine.objects.get_or_create(
        machine_code="MCH-SLZ-01",
        name="ماشین بافندگی سولزر سوئیسی ۱",
        status="active",
        description="ماشین بافندگی با عرض ۳۹۰ سانتی‌متر"
    )
    m_2, _ = Machine.objects.get_or_create(
        machine_code="MCH-JET-02",
        name="دستگاه رنگرزی جت تحت فشار ۲",
        status="active",
        description="دستگاه رنگرزی با ظرفیت ۵۰۰ کیلوگرم پارچه"
    )
    m_3, _ = Machine.objects.get_or_create(
        machine_code="MCH-SPN-03",
        name="ماشین ریسندگی روتور آلمانی",
        status="repair",
        description="سیستم ریسندگی الیاف کوتاه"
    )

    op_1, _ = Operator.objects.get_or_create(
        operator_code="OP-9101",
        first_name="اصغر",
        last_name="فرهادی",
        phone_number="09121111111",
        status="active"
    )
    op_2, _ = Operator.objects.get_or_create(
        operator_code="OP-9102",
        first_name="کریم",
        last_name="باقری",
        phone_number="09122222222",
        status="active"
    )
    op_3, _ = Operator.objects.get_or_create(
        operator_code="OP-9103",
        first_name="مرتضی",
        last_name="پورعلی‌گنجی",
        phone_number="09123333333",
        status="leave"
    )

    ws_1, _ = WorkStage.objects.get_or_create(code="SPN", name="ریسندگی (Spinning)", description="تبدیل الیاف پنبه و پلی‌استر به نخ")
    ws_2, _ = WorkStage.objects.get_or_create(code="WVG", name="بافندگی (Weaving)", description="بافت تار و پود نخ‌ها و تبدیل به پارچه خام")
    ws_3, _ = WorkStage.objects.get_or_create(code="DYE", name="رنگرزی و تکمیل (Dyeing)", description="رنگرزی پارچه خام با نیل و اعمال پرداخت نهایی")
    ws_4, _ = WorkStage.objects.get_or_create(code="PKN", name="بسته‌بندی و کنترل کیفیت", description="کنترل کیفیت نهایی و رول کردن پارچه‌ها")
    print("Created Production Assets.")

    # 7. Create Plannings
    Planning.objects.get_or_create(
        planning_code="PLN-1402-101",
        order=order_1,
        product=fabric_denim,
        stage=ws_2,
        machine=m_1,
        operator=op_1,
        raw_material=yarn_cotton,
        raw_material_qty=1200.00,
        warehouse=wh_raw,
        defaults={
            'target_quantity': 1500.00,
            'produced_quantity': 0.00,
            'start_date': datetime.date.today(),
            'end_date': datetime.date.today() + datetime.timedelta(days=7),
            'status': 'pending',
            'material_deducted': False
        }
    )

    Planning.objects.get_or_create(
        planning_code="PLN-1402-102",
        order=order_1,
        product=fabric_denim,
        stage=ws_3,
        machine=m_2,
        operator=op_2,
        raw_material=dye_indigo,
        raw_material_qty=150.00,
        warehouse=wh_raw,
        defaults={
            'target_quantity': 1500.00,
            'produced_quantity': 450.00,
            'start_date': datetime.date.today() - datetime.timedelta(days=2),
            'end_date': datetime.date.today() + datetime.timedelta(days=5),
            'status': 'producing',
            'material_deducted': True
        }
    )
    print("Created Sample Production Plannings.")
    print("All seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
