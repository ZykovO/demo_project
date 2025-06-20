from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserSerializer, MyTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

CustomUser = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    Создает учетную запись пользователя и возвращает данные пользователя.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'username'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email пользователя (должен быть уникальным)"
                ),
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Имя пользователя"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Пароль (минимум 8 символов)"
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Пользователь успешно создан",
                schema=CustomUserSerializer
            ),
            400: openapi.Response(
                description="Неверные входные данные",
                examples={
                    "application/json": {
                        "email": ["Это поле обязательно."],
                        "password": ["Это поле обязательно."],
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Получение JWT токенов (access и refresh) для аутентификации.
    Требует email и password пользователя.
    """
    serializer_class = MyTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Получение JWT токенов для аутентификации",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email пользователя"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Пароль пользователя"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Успешная аутентификация",
                examples={
                    "application/json": {
                        "refresh": "eyJhbGciOi...",
                        "access": "eyJhbGciOi...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "user123"
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Неверные учетные данные",
                examples={
                    "application/json": {
                        "detail": "No active account found with the given credentials"
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveAPIView):
    """
    Получение профиля текущего аутентифицированного пользователя.
    Требует действительный JWT токен в заголовке Authorization.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Получение профиля текущего пользователя",
        responses={
            200: openapi.Response(
                description="Профиль пользователя",
                schema=CustomUserSerializer
            ),
            401: openapi.Response(
                description="Неавторизованный доступ",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ValidateTokenView(generics.GenericAPIView):
    """
    Проверка валидности JWT токена.
    Возвращает информацию о пользователе, если токен действителен.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Проверка валидности JWT токена",
        responses={
            200: openapi.Response(
                description="Токен валиден",
                examples={
                    "application/json": {
                        "valid": True,
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "user123"
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Недействительный токен",
                examples={
                    "application/json": {
                        "detail": "Токен недействителен или просрочен"
                    }
                }
            )
        }
    )
    def get(self, request):
        return Response({'valid': True, 'user': CustomUserSerializer(request.user).data})