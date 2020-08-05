from django.urls import path, re_path
from rbac import views

urlpatterns = [
    path('customers/', views.customers),
    path('orders/', views.orders),
]
