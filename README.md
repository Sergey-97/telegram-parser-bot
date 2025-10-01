# Telegram Parser Bot

Бот для автоматического парсинга Telegram каналов, анализа контента через нейросети и публикации обзоров.

## Функционал

- 📡 Парсинг Telegram каналов по расписанию
- 🧠 Анализ контента через NLP модели
- 📊 Суммаризация и анализ тональности
- 📤 Автоматическая публикация в целевой канал
- 🌐 Работа 24/7 на Render.com

## Структура проекта
telegram_parser_bot/
├── bot.py # Основной файл бота
├── config.py # Конфигурация
├── database.py # Модели базы данных
├── parser.py # Парсер каналов
├── nlp_processor.py # NLP обработка
├── scheduler.py # Планировщик задач
├── migrate_db.py # Миграции БД
├── health_check.py # Health check сервер
├── build.sh # Скрипт сборки
├── requirements.txt # Зависимости Python
├── runtime.txt # Версия Python
└── render.yaml # Конфиг Render


## Установка и запуск

1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Настроить переменные окружения
4. Запустить: `python bot.py`

## Deploy на Render

Проект автоматически деплоится на Render при пуше в main ветку.