from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from config.django.security import security_config

urlpatterns = [
    path("admin/", admin.site.urls),
]

if security_config.DEBUG:
    urlpatterns += [
        path("dev/api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("dev/api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("dev/api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ] + debug_toolbar_urls()
