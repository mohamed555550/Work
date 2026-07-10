#!/bin/bash

# =============================================================
# Restaurant Marketplace - Quick Setup Script for Linux/macOS
# =============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "=========================================="
echo "سوق الأكل المنزلي - البدء السريع"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python 3.11+ أولاً."
    exit 1
fi
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "❌ إصدار Python أقدم من 3.11. يرجى التحديث أولاً."
    exit 1
fi
echo "✅ Python3 مثبت"

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js غير مثبت. يرجى تثبيت Node.js 20.19+ أولاً."
    exit 1
fi
if ! node -e 'const [major, minor] = process.versions.node.split(".").map(Number); const ok = (major === 20 && minor >= 19) || (major === 22 && minor >= 12) || major > 22; process.exit(ok ? 0 : 1)'; then
    echo "❌ استخدم Node.js 20.19+ أو 22.12+."
    exit 1
fi
echo "✅ Node.js مثبت"

# Check if Docker is installed (optional)
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker غير مثبت (اختياري، لكن مُوصى به)"
else
    echo "✅ Docker مثبت"
fi

echo ""
echo "=========================================="
echo "الخطوة 1: إعداد Backend"
echo "=========================================="
echo ""

# Setup backend
if [ ! -f backend/.env ]; then
    cp .env.example backend/.env
fi
if [ ! -f frontend/.env ]; then
    cp .env.example frontend/.env
fi
cd backend

echo "إنشاء البيئة الافتراضية..."
python3 -m venv .venv
echo "✅ تم إنشاء البيئة الافتراضية"

echo "تفعيل البيئة الافتراضية..."
source .venv/bin/activate
echo "✅ تم تفعيل البيئة الافتراضية"

echo "تثبيت الحزم..."
pip install -q -r requirements.txt
echo "✅ تم تثبيت الحزم"

echo ""
echo "=========================================="
echo "الخطوة 2: إعداد قاعدة البيانات"
echo "=========================================="
echo ""

# Check if Docker is available
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "بدء PostgreSQL عبر Docker..."
    docker compose -f ../docker-compose.yml up -d --wait postgres
    echo "⏳ انتظار تشغيل قاعدة البيانات..."
else
    echo "⚠️  Docker لم يتم الكشف عنه. تأكد من أن PostgreSQL يعمل محلياً."
fi

echo "تطبيق الهجرات..."
python manage.py migrate
echo "✅ تم تطبيق الهجرات"

echo "ملء البيانات التجريبية..."
python manage.py seed_marketplace
echo "✅ تم ملء البيانات التجريبية"

cd ..

echo ""
echo "=========================================="
echo "الخطوة 3: إعداد Frontend"
echo "=========================================="
echo ""

cd frontend

echo "تثبيت حزم Node..."
npm ci --silent
echo "✅ تم تثبيت الحزم"

cd ..

echo ""
echo "=========================================="
echo "✅ تم إكمال الإعداد بنجاح!"
echo "=========================================="
echo ""
echo "الخطوات التالية:"
echo "1. البيئة الخلفية: cd backend && source .venv/bin/activate && python manage.py runserver"
echo "2. واجهة المستخدم: cd frontend && npm run dev"
echo ""
echo "البيانات المرجعية:"
echo "- المستخدم: alaa، كلمة المرور: Password123!"
echo "- البائع: seller1، كلمة المرور: Password123!"
echo ""
echo "استمتع بـ سوق الأكل المنزلي! 🎉"
echo ""
