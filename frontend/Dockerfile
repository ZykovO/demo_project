# Стадия сборки
FROM node:20-alpine AS builder

WORKDIR /app

# Копирование файлов конфигурации (включая package-lock.json)
COPY package*.json ./
COPY angular.json ./
COPY tsconfig*.json ./

# Установка ВСЕХ зависимостей (используем npm install если нет package-lock.json)
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Копирование исходного кода
COPY src/ ./src/
COPY public/ ./public/

# Сборка приложения для продакшена
RUN npm run build --prod

# Стадия запуска
FROM nginx:1.25-alpine

# Копирование собранного приложения
COPY --from=builder /app/dist/frontend/browser/* /usr/share/nginx/html/

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom server config
COPY nginx.conf /etc/nginx/conf.d/

# Порт
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
