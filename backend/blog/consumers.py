import json
import uuid
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Подключение к WebSocket."""
        try:
            token = self.get_token()
            if not token:
                await self.close(code=4001)
                return

            user = await self.get_user_from_token(token)
            if not user or user.is_anonymous:
                await self.close(code=4001)
                return

            self.user = user
            self.user_group_name = f"user_{user.id}"

            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )

            await self.accept()

            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Подключен как {user.username}',
                'user_id': user.id
            }))

        except Exception as e:
            print(f"WebSocket connection error: {str(e)}")
            await self.close(code=4002)  # Internal error

    async def disconnect(self, close_code):
        """Отключение от WebSocket."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Получение сообщения от клиента."""
        try:
            data = json.loads(text_data)
            # Можно добавить обработку команд от клиента
            # Например, запрос на получение непрочитанных уведомлений
            if data.get('action') == 'get_unread_count':
                # Здесь можно добавить логику получения количества непрочитанных уведомлений
                pass
        except json.JSONDecodeError:
            pass

    async def notification_message(self, event):
        """Отправка уведомления клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    def get_token(self):
        """Получает JWT токен из заголовков или query параметров."""
        # Сначала пробуем получить из заголовков
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization')

        if auth_header:
            try:
                token = auth_header.decode('utf-8').split(' ')[1]  # Bearer <token>
                return token
            except (IndexError, UnicodeDecodeError):
                pass

        # Если не нашли в заголовках, пробуем query параметры
        query_string = self.scope['query_string'].decode('utf-8')
        if 'token=' in query_string:
            try:
                token = query_string.split('token=')[1].split('&')[0]
                return token
            except IndexError:
                pass

        return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Получает пользователя по JWT токену."""
        try:
            # Проверяем токен
            UntypedToken(token)

            # Декодируем токен
            decoded_data = jwt_decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            # Получаем пользователя
            user_id = decoded_data.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                return user

        except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
            pass

        return AnonymousUser()