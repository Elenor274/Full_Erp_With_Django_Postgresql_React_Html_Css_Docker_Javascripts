@echo off
REM فایل اجرای لوکال روی سیستم ویندوز ۱۱ با دیتابیس PostgreSQL و دسترسی شبکه LAN

echo ===================================================
echo     Textile ERP - Local Launch (PostgreSQL + LAN)
echo ===================================================

set DB_ENGINE=postgresql
set DB_NAME=textile_db
set DB_USER=postgres
set DB_PASSWORD=1234
set DB_HOST=localhost
set DB_PORT=5432
set ENABLE_SECURE_COOKIES=false

echo.
echo [1/4] Checking and Applying Database Migrations...
python manage.py migrate

echo.
echo [2/4] Seeding Database & Creating Admin User in PostgreSQL...
python seed_data.py

echo.
echo [3/4] Collecting Static Files...
python manage.py collectstatic --noinput

echo.
echo [4/4] Starting Django Server on 0.0.0.0:8000...
echo.
echo Server is running! Access URLs:
echo   - Local PC:       http://localhost:8000
echo   - Other LAN PCs:  http://YOUR_WINDOWS_IP:8000
echo.
echo Default Superuser Credentials:
echo   Username: admin
echo   Password: admin1234
echo ===================================================

python manage.py runserver 0.0.0.0:8000
pause
