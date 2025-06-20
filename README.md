# Тестовое задание — SPA-приложение «Комментарии»

**Исполнитель:** Зыков Александр

## 📌 Описание задачи

Реализовать одностраничное (SPA) приложение для отображения и добавления комментариев с системой оповещений в реальном времени.

---

## ✅ Реализованный функционал

1. 🔐 Авторизация с использованием JWT токенов
2. 📝 Отображение постов и связанных комментариев
3. 📎 Превью вложений (если есть)
4. ➕ Добавление комментариев
5. 🔔 Уведомления через WebSocket об ответах на комментарии или новых комментариях в посте

---

## 🚀 Как запустить проект

1. **Склонировать репозиторий:**

   ```bash
   git clone https://github.com/ZykovO/demo_project.git
   cd demo_project
   touch .env
   ```
   *Заполнить .env файл параметрами*
   ```dotenv
      POSTGRES_DB=demo_project
      POSTGRES_USER=psp_admin
      POSTGRES_PASSWORD=psp
      
      # Внешний IP или доменное имя
      HOST=34.123.41.229
      
      
      DJANGO_SUPERUSER_USERNAME=admin
      DJANGO_SUPERUSER_EMAIL=admin@admin.ua
      DJANGO_SUPERUSER_PASSWORD=admin
   ```
   *Заменить хост в конфиге ангуляра /frontend/src/app/environments/environment.ts*
   ```
   export const environment = {
      production: false,
      apiUrl: 'http://34.30.243.182:8000/api/',
      wsUrl: 'ws://34.30.243.182:8000/ws/notifications/'
      };

   ```

2. **Убедиться, что установлен Docker и Docker Compose.**

3. **Запустить контейнеры:**

   ```bash
   docker-compose up --build
   ```

4. **Перейти в Django Admin по адресу:**

   ```
   http://host:8000/admin/
   ```

5. **В админ-панели:**
    - Создать ещё одного обычного пользователя
    - Создать пару постов для тестирования

   ⚠️ *Регистрация пользователей и создание постов через API не реализованы.*

---

## 🛠 Стек технологий

- **Backend:** Django, Django REST Framework, JWT, WebSockets (Channels)
- **Frontend:** Angular
- **База данных:** PostgreSQL
- **Docker:** для развёртывания

---

## 📎 Структура проекта

```
project-root/
├── backend/        # Django-приложение
├── frontend/       # Angular SPA
└── db/             # DB sql create
```

---
