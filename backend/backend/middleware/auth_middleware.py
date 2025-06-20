from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

from django.http import JsonResponse


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Пропускаем проверку для публичных путей
        if any(request.path.startswith(path) for path in settings.PUBLIC_PATHS):
            return None

        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'error': 'Authorization header must start with Bearer'},
                status=401
            )

        try:
            auth = JWTAuthentication()
            request.META['HTTP_AUTHORIZATION'] = auth_header  # Устанавливаем заголовок
            auth_result = auth.authenticate(request)
            if auth_result is not None:
                request.user, request.auth = auth_result
            else:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
        except AuthenticationFailed as e:
            return JsonResponse(
                {'error': str(e)},
                status=401
            )