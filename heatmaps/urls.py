from django.urls import path
from .views import heatmap_view, home_view

urlpatterns = [
    path('', heatmap_view, name='heatmap_view'),
    path('', home_view, name='home')
]