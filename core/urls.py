from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('bike/<int:pk>/', views.BikeDetailView.as_view(), name='bike_detail'),
    path('bike/<int:bike_id>/book/', views.book_bike, name='book_bike'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]