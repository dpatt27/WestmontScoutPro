
import csv
from django.shortcuts import render, redirect
from .forms import CSVUploadForm
from .models import Pitch


def home(request):
    return render(request, 'heatmaps/home.html')

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Pitch.objects.create(
                    pitcher=row['pitcher'],
                    platelocheight=row.get('platelocheight') or None,
                    platelocside=row.get('platelocside') or None
                )
            return redirect('success')
    else:
        form = CSVUploadForm()
    return render(request, 'heatmaps/upload_csv.html', {'form': form})