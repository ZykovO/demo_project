#!/bin/bash

# Функция для логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Функция для проверки доступности базы данных
wait_for_db() {
    log "🔍 Ожидание доступности базы данных..."

    max_attempts=30
    attempt=1

    sleep 5
    return 0
}

wait_for_db || exit 1

log "🛠  Применение миграций..."
python manage.py migrate --noinput

if [ $? -eq 0 ]; then
    log "✅ Миграции успешно применены"
else
    log "❌ Ошибка при применении миграций"
    exit 1
fi

log "📦 Сбор статических файлов..."
python manage.py collectstatic --noinput --clear

if [ $? -eq 0 ]; then
    log "✅ Статические файлы успешно собраны"
else
    log "❌ Ошибка при сборе статических файлов"
    exit 1
fi

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    log "👤 Создание суперпользователя..."

    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = "$DJANGO_SUPERUSER_USERNAME"
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"

if not User.objects.filter(username=username).exists():
    print("Создаем суперпользователя...")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print("Суперпользователь уже существует.")
EOF
fi

log "🔧 Проверка конфигурации Django..."
python manage.py check --deploy || log "⚠️ Обнаружены проблемы в конфигурации"

log "🚀 Запуск Daphne сервера..."
exec daphne -b 0.0.0.0 -p 8000 backend.asgi:application
