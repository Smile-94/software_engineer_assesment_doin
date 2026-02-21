from django.urls import path

from apps.broker.views.broker_account_view import CreateBrokerAccountView

# <<--------------------------------- Broker URLs --------------------------------->>
urlpatterns = [
    path("accounts/", CreateBrokerAccountView.as_view(), name="create"),
]
