# 🧵 Hama Textile ERP — Enterprise Fabric & Textile Factory Management System
## 🧵 سامانه جامع مدیریت کارخانه پارچه و نساجی حاما

![Django Version](https://img.shields.io/badge/Django-5.0.2-092E20?style=for-the-badge&logo=django)
![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-4169E1?style=for-the-badge&logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

---

### 🌐 English Overview

**Hama Textile ERP** is a full-featured, enterprise-grade Textile & Fabric Manufacturing ERP system built with Django, PostgreSQL, and modern web technologies. Designed specifically for textile weaving, dyeing, finishing, and garment production plants, it covers the entire operational workflow from customer order intake and design file management to Bill of Materials (BOM) calculation, production planning, machine monitoring, roll inventory tracking, and quality control (QC).

### 🇮🇷 معرفی سیستم به فارسی

**سامانه ERP اختصاصی صنایع نساجی و تولید پارچه حاما** یک سیستم یکپارچه مدیریت منابع سازمانی است که ویژه برنامه‌ریزی تولید، کنترل کیفی، انبارداری تخصصی طاقه‌های پارچه، مدیریت مشتریان، سفارشات فروش، محاسبه ساختار مواد (BOM) و پایش خطوط بافندگی طراحی شده است.

---

## 📸 System Screenshots / پیش‌نمایش محیط نرم‌افزار

| Screen / بخش | Preview / تصویر |
| :--- | :--- |
| **🔑 Login Screen / صفحه ورود** | ![Login](assets/images/login.png) |
| **📊 Executive Dashboard / داشبورد مدیریتی** | ![Dashboard](assets/images/dashboard.png) |
| **🛒 Order Management / مدیریت سفارشات** | ![Orders](assets/images/orders.png) |
| **👥 Customer Directory / مدیریت مشتریان** | ![Customers](assets/images/customers.png) |
| **🎨 Product & Fabric Catalog / کاتالوگ پارچه‌ها** | ![Products](assets/images/products.png) |
| **📦 Roll Inventory & Warehouse / انبارداری و طاقه‌ها** | ![Warehouse](assets/images/warehouse.png) |
| **🗓️ BOM & Production Planning / برنامه‌ریزی تولید** | ![Planning](assets/images/planning.png) |
| **⚙️ Machinery Execution / پایش خط تولید** | ![Production](assets/images/production.png) |

---

## ✨ Key Features / امکانات کلیدی

- **📊 Live Machinery & OEE Dashboard:** Real-time monitoring of loom machines, dyeing vats, production logs, maintenance requests, and KPIs.
- **🏬 Textile Warehouse & Roll Tracking:** Multi-warehouse inventory management with barcode scanning support, fabric roll weights, and reorder alerts.
- **🧾 Sales Orders & Design Attachments:** Track Sepidar integration codes, custom fabric dimensions, order progress, and design files.
- **🛠️ Bill of Materials (BOM) & Planning:** Automated calculation of yarn, dye, and chemical requirements for production plans.
- **👥 Role-Based Access Control (RBAC):** Granular user permissions for Dashboard, Sales, Warehouse, Production Execution, and Quality Control.
- **🗓️ Persian Jalali & Gregorian Calendar Support:** Full compatibility with Jalali date pickers and reports.

---

## 🛠️ Tech Stack / تکنولوژی‌های استفاده‌شده

- **Backend:** Python 3.11 / Django 5.x
- **Database:** PostgreSQL (Primary) / SQLite (Development Fallback)
- **Frontend:** HTML5, CSS3 (Tailwind & Custom Glassmorphism Theme), Bootstrap 5 (RTL), Feather Icons, Chart.js
- **Date Engine:** `jdatetime` (Solar Hijri Calendar)
- **Export Tools:** OpenPyXL, Pillow, ReportLab

---

## 🚀 Quick Start & Installation / راهنمای نصب و اجرا

### 1️⃣ Clone the Repository / کلون کردن پروژه‌
```bash
git clone https://github.com/your-username/textile-erp.git
cd textile-erp
```

### 2️⃣ Create Virtual Environment / محیط مجازی
```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell / CMD)
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies / نصب نیازمندی‌ها
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables / تنظیم فایل محیطی
Copy `.env.example` to `.env` and fill in your PostgreSQL credentials:
```bash
cp .env.example .env
```
Inside `.env`:
```env
SECRET_KEY=your-custom-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

DB_ENGINE=django.db.backends.postgresql
DB_NAME=textile_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Set to True if you don't have PostgreSQL running and want quick SQLite test
USE_SQLITE=False
```

### 5️⃣ Initialize Database & Seed Sample Data / دیتابیس و داده‌های اولیه
```bash
# Run database migrations
python manage.py migrate

# Seed initial test data (Admin user, Warehouses, Machines, Sample Orders)
python seed_data.py
```

### 6️⃣ Run Development Server / اجرای سرور
```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/login/`

**Default Credentials:**
- **Username:** `admin`
- **Password:** `admin123`

---

## 📂 Project Architecture / ساختار پروژه

```text
textile-erp/
│
├── core/               # Main dashboard, KPI aggregations, base templates
├── customers/          # Customer profiles and buyer management
├── orders/             # Sales orders, line items, and CAD/design file attachments
├── products/           # Product groups, fabric specs (gsm, weave, color)
├── production/         # Production planning, machines, logs, BOM, maintenance
├── users/              # RBAC middleware, user profiles, authentication
├── warehouse/          # Multi-warehouse stock tracking and roll inventory
│
├── static/             # CSS stylesheets, JS scripts, images
├── templates/          # Global layout templates and modal components
├── seed_data.py        # Database initializer & sample data generator
├── manage.py           # Django management CLI
├── .env.example        # Environment variable template (No secrets)
├── requirements.txt    # Python package dependencies
└── README.md           # Documentation
```

---

## 📤 GitHub Commit Instructions / دستورات ارسال به گیت‌هاب

To push the latest secure changes to your GitHub repository:

```bash
# 1. Check status
git status

# 2. Add modified & new files
git add .

# 3. Commit changes with a clean message
git commit -m "feat: setup PostgreSQL configuration with fallback, clean env variables, update dashboard & README"

# 4. Push to main branch
git push origin main
```

---

## 📜 License / مجوز

This project is licensed under the **MIT License**.
