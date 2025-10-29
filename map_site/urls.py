# map_site/urls.py
from django.contrib import admin
from django.urls import path
from maps import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.hydrogen, name='home'),
    path('hydrogen/', views.hydrogen, name='map_hydrogen'),
    path('steel/', views.steel, name='map_steel'),
]
