from django.urls import path
from .views import CartListView, CartItemCreateView, CartItemUpdateView, CartItemDeleteView

urlpatterns = [
    path('', CartListView.as_view(), name='cart_list'),
    path('add/', CartItemCreateView.as_view(), name='cart_add'),
    path('<int:pk>/update/', CartItemUpdateView.as_view(), name='cart_update'),
    path('<int:pk>/remove/', CartItemDeleteView.as_view(), name='cart_remove'),
]
