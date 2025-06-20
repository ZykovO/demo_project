# backend/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from auth_app.views import RegisterView, MyTokenObtainPairView, UserProfileView, ValidateTokenView

from api_docs.schema import urlpatterns as docs_urls
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/validate/', ValidateTokenView.as_view(), name='token_validate'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),

    path('api/', include('blog.urls'))

] + docs_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)