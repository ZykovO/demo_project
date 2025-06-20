#!/bin/bash

# Функция для логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Функция для проверки доступности базы данных
wait_for_db() {
    log "🔍 Ожидание доступности базы данных..."
    
    # Максимальное количество попыток
    max_attempts=30
    attempt=1
    
    sleep 5
    return 0

}

# Проверка доступности базы данных
wait_for_db || exit 1

# Применение миграций
log "🛠  Применение миграций..."
python manage.py migrate --noinput

# Сбор статических файлов
log "📦 Сбор статических файлов..."
python manage.py collectstatic --noinput --clear

if [ $? -eq 0 ]; then
    log "✅ Статические файлы успешно собраны"
else
    log "❌ Ошибка при сборе статических файлов"
    exit 1
fi

# Создание суперпользователя (если переменные окружения заданы)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    log "👤 Создание суперпользователя..."
    python manage.py createsuperuser --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || \
    log "⚠️ Не удалось создать суперпользователя (возможно, уже существует)"
fi

# Проверка конфигурации Django
log "🔧 Проверка конфигурации Django..."
python manage.py check --deploy || log "⚠️ Обнаружены проблемы в конфигурации"

# Запуск сервера
log "🚀 Запуск Daphne сервера..."
exec daphne -b 0.0.0.0 -p 8000 backend.asgi:application