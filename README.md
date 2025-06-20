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
   ```

2. **Убедиться, что установлен Docker и Docker Compose.**

3. **Запустить контейнеры:**

   ```bash
   docker-compose up --build
   ```

4. **Войти в контейнер Django и создать суперпользователя:**

   ```bash
   docker exec -it backend bash
   python manage.py createsuperuser
   ```

5. **Перейти в Django Admin по адресу:**

   ```
   http://localhost:8000/admin/
   ```

6. **В админ-панели:**
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
