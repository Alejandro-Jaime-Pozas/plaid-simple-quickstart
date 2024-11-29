from django.urls import path
from . import views

urlpatterns = [
    path('api/create_link_token/', views.create_link_token, name='create_link_token'),
    path('api/exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
    path('api/balance/', views.get_balance, name='get_balance'),
    path('api/csrf_token/', views.csrf_token, name='csrf_token'),
]
