from django.urls import path
from .views import home, upload_csv

urlpatterns = [
    path('', home, name='home'),  # Add this line
    path('upload/', upload_csv, name='upload_csv'),
]