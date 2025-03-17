from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('heatmaps/', views.heatmap_view, name='heatmap_view'),
    path('get_pitchtypes/', views.get_pitchtypes, name='get_pitchtypes'),
    path('hitters/', views.hitters_view, name='hitters_view'),
]
