# 1. استخدام نسخة بايثون خفيفة
FROM python:3.11-slim

# 2. تحديد مجلد العمل جوه الحاوية
WORKDIR /app

# 3. نسخ ملف المتطلبات الأول
COPY requirements.txt .

# 4. تسطيب المكتبات الأساسية
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 5. نسخ باقي ملفات المشروع (main.py, interface.py, controllers, models, etc.)
COPY . .

# 6. فتح البورتات اللي هنحتاجها (5000 للسيرفر، 8501 للواجهة)
EXPOSE 5000 8501

# ملحوظة: مش هنكتب أمر التشغيل (CMD) هنا، 
# هنكتبه في ملف الـ docker-compose عشان نقدر نشغل السيرفر والواجهة من نفس الصورة