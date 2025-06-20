FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование entrypoint.sh с правильными правами
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser

# Создание директорий для статики и медиа
RUN mkdir -p /app/static /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# Копирование исходного кода
COPY --chown=appuser:appuser . .

# Убеждаемся, что entrypoint.sh имеет правильные права после копирования
RUN chmod +x /app/entrypoint.sh && chown appuser:appuser /app/entrypoint.sh

# Переключаемся на пользователя
USER appuser

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Порт приложения
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]