from django.urls import path
from .views import FavoriteListView, FavoriteCreateView, FavoriteDeleteView

urlpatterns = [
    path('', FavoriteListView.as_view(), name='favorite_list'),
    path('add/', FavoriteCreateView.as_view(), name='favorite_add'),
    path('<int:pk>/remove/', FavoriteDeleteView.as_view(), name='favorite_remove'),
]
