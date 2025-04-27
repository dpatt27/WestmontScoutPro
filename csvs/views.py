from django.shortcuts import render, redirect
from .forms import CsvModelForm
from .models import Csv
import csv
from heatmaps.models import Pitch
import pandas as pd
#from django.http import HttpResponse
# Create your views here.
import io

def upload_file_view(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        csv_file = request.FILES['file_name']  # No save to disk

        # Read CSV directly
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        df = pd.read_csv(io_string)

        columns_to_keep = [
            'Pitcher', 'TaggedPitchType', 'RelSpeed', 'PlateLocHeight',
            'PlateLocSide', 'PitchCall', 'ExitSpeed', 'Batter',
            'BatterTeam', 'PlayResult', 'KorBB'
        ]
        new_df = df[columns_to_keep]
        new_df['ExitSpeed'] = new_df['ExitSpeed'].fillna(0)
        new_df = new_df.dropna()

        for _, row in new_df.iterrows():
            Pitch.objects.create(
                pitcher=row['Pitcher'],
                pitchtype=row['TaggedPitchType'],
                velo=row['RelSpeed'],
                platelocheight=row['PlateLocHeight'],
                platelocside=row['PlateLocSide'],
                pitchcall=row['PitchCall'],
                exitspeed=row['ExitSpeed'],
                batter=row['Batter'],
                batter_team=row['BatterTeam'],
                playresult=row['PlayResult'],
                korbb=row['KorBB'],
            )

        return redirect('home')  # or any page you want after success

    return render(request, 'csvs/upload.html', {'form': form})
