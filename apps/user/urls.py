from django.urls import path

from apps.user.views.login_view import TokenObtainView

urlpatterns = [
    path("login/", TokenObtainView.as_view(), name="login"),
]
