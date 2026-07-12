@echo off
REM =============================================================
REM Restaurant Marketplace - Quick Setup Script for Windows
REM =============================================================

echo.
echo ==========================================
echo سوق الأكل المنزلي - البدء السريع
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت. يرجى تثبيت Python 3.11+ أولاً.
    exit /b 1
)
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo ❌ إصدار Python أقدم من 3.11. يرجى التحديث أولاً.
    exit /b 1
)
echo ✅ Python مثبت

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js غير مثبت. يرجى تثبيت Node.js 20.19+ أولاً.
    exit /b 1
)
node -e "const [major, minor] = process.versions.node.split('.').map(Number); const ok = (major === 20 && minor >= 19) || (major === 22 && minor >= 12) || major > 22; process.exit(ok ? 0 : 1)"
if errorlevel 1 (
    echo ❌ استخدم Node.js 20.19+ أو 22.12+.
    exit /b 1
)
echo ✅ Node.js مثبت

REM Check if Docker is installed (optional but recommended)
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker غير مثبت (اختياري، لكن مُوصى به)
) else (
    echo ✅ Docker مثبت
)

echo.
echo ==========================================
echo الخطوة 1: إعداد Backend
echo ==========================================
echo.

REM Setup backend
if not exist backend\.env copy .env.example backend\.env >nul
if not exist frontend\.env copy .env.example frontend\.env >nul
cd backend

echo إنشاء البيئة الافتراضية...
python -m venv .venv
if errorlevel 1 (
    echo ❌ فشل إنشاء البيئة الافتراضية
    exit /b 1
)
echo ✅ تم إنشاء البيئة الافتراضية

echo تفعيل البيئة الافتراضية...
call .\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ فشل تفعيل البيئة الافتراضية
    exit /b 1
)
echo ✅ تم تفعيل البيئة الافتراضية

echo تثبيت الحزم...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ فشل تثبيت الحزم
    exit /b 1
)
echo ✅ تم تثبيت الحزم

echo.
echo ==========================================
echo الخطوة 2: إعداد قاعدة البيانات
echo ==========================================
echo.

REM Check if Docker is running and start PostgreSQL if available
docker ps >nul 2>&1
if errorlevel 0 (
    echo بدء PostgreSQL عبر Docker...
    docker compose -f ..\docker-compose.yml up -d --wait postgres
    if errorlevel 0 (
        echo ⏳ انتظار تشغيل قاعدة البيانات...
        timeout /t 3 /nobreak
    )
) else (
    echo ⚠️  Docker لم يتم الكشف عنه. تأكد من أن PostgreSQL يعمل محلياً.
)

echo تطبيق الهجرات...
python manage.py migrate
if errorlevel 1 (
    echo ❌ فشل تطبيق الهجرات
    exit /b 1
)
echo ✅ تم تطبيق الهجرات

echo ملء البيانات التجريبية...
python manage.py seed_marketplace
if errorlevel 1 (
    echo ❌ فشل ملء البيانات التجريبية
    exit /b 1
)
echo ✅ تم ملء البيانات التجريبية

cd ..

echo.
echo ==========================================
echo الخطوة 3: إعداد Frontend
echo ==========================================
echo.

cd frontend

echo تثبيت حزم Node...
call npm ci
if errorlevel 1 (
    echo ❌ فشل تثبيت الحزم
    exit /b 1
)
echo ✅ تم تثبيت الحزم

cd ..

echo.
echo ==========================================
echo ✅ تم إكمال الإعداد بنجاح!
echo ==========================================
echo.
echo الخطوات التالية:
echo 1. البيئة الخلفية: cd backend && .\.venv\Scripts\activate && python manage.py runserver
echo 2. واجهة المستخدم: cd frontend && npm run dev
echo.
echo البيانات المرجعية:
echo - المستخدم: alaa، كلمة المرور: Password123!
echo - البائع: seller1، كلمة المرور: Password123!
echo.
echo استمتع بـ سوق الأكل المنزلي! 🎉
echo.
pause
