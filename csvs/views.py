from django.shortcuts import render
from .forms import CsvModelForm
from .models import Csv
import csv
from heatmaps.models import Pitch
import pandas as pd
#from django.http import HttpResponse
# Create your views here.
def upload_file_view(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = CsvModelForm()
        obj = Csv.objects.filter(activated=False).first()  # Updated this line
        if obj:  # Check if obj is not None
            df = pd.read_csv(obj.file_name.path)
            columns_to_keep = ['Pitcher', 'TaggedPitchType', 'RelSpeed', 'PlateLocHeight', 'PlateLocSide', 'PitchCall', 'ExitSpeed', 'Batter', 'BatterTeam', 'PlayResult', 'KorBB']
            new_df = df[columns_to_keep]
            new_df['ExitSpeed'] = new_df['ExitSpeed'].fillna(0)
            new_df = new_df.dropna()
            print(new_df)
            for index, row in new_df.iterrows():
                pitch_instance = Pitch(
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
                    korbb = row['KorBB'],
                )
                pitch_instance.save()
            obj.activated = True
            obj.save()
    return render(request, 'csvs/upload.html', {'form': form})
