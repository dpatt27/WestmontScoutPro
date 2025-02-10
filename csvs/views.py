from django.shortcuts import render
from .forms import CsvModelForm
from .models import Csv
import csv
from heatmaps.models import Pitch
#from django.http import HttpResponse
# Create your views here.
def upload_file_view(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = CsvModelForm()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)

            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    row = "".join(row)
                    row = row.replace(",", " ")
                    row = row.split()
                    pitcher = row[5]
                    platelocheight = row[45]
                    platelocside = row[41]
                    print(row)
                    Pitch.objects.create(
                        pitcher=pitcher,
                        platelocheight=platelocheight,
                        platelocside=platelocside,
                    )
            obj.activated = True
            obj.save()
    return render(request, 'csvs/upload.html', {'form': form})