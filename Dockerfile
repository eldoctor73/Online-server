# استخدم صورة Python الرسمية
FROM python:3.11-slim

# اضبط فولدر العمل
WORKDIR /app

# انسخ ملفات المشروع كلها
COPY . .

# ثبّت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# ضبط البيئة (Fly.io يعطي PORT تلقائي)
ENV PORT=8080

# أمر تشغيل السيرفر
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
