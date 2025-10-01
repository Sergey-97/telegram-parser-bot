#!/bin/bash
echo "🚀 Starting build process..."

# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем миграцию базы данных
python migrate_db.py

echo "✅ Build completed successfully!"