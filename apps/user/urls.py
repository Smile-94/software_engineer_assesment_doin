from django.urls import path

from apps.user.views.login_view import TokenObtainView, TokenRefreshView

urlpatterns = [
    path("login/", TokenObtainView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
]
