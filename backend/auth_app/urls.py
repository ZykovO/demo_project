# auth_project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from auth_app.views import (
    RegisterView,
    MyTokenObtainPairView,
    UserProfileView,
    ValidateTokenView
)

urlpatterns = [
    path('admin/', admin.site.urls),

]