"""
URL configuration for rme_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet
from apps.patients.views import PatientViewSet
from apps.users.auth import TenantTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import HealthzView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"patients", PatientViewSet, basename="patient")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/healthz", HealthzView.as_view(), name="healthz"),
    path("api/auth/login/", TenantTokenObtainPairView.as_view(), name="login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
