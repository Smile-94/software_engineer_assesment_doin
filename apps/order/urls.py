from django.urls import path

from apps.order.views.order_views import OrderListAPIView

# <<--------------------------------- Order URLs --------------------------------->>
urlpatterns = [
    path("", OrderListAPIView.as_view(), name="orders"),
]
