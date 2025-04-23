# urls.py
from django.urls import path

from ads import views

urlpatterns = [
    path('banner/show/<int:banner_id>/', views.show_banner, name='show_banner'),
    path('banner/click/<int:banner_id>', views.handle_click, name='click'),
]
