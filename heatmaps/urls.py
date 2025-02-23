from django.urls import path
from .views import heatmap_view

urlpatterns = [
    path('', heatmap_view, name='heatmap_view'),
]