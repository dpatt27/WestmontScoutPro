import pandas as pd
import requests
from django.shortcuts import render
from django.http import HttpResponse
from .models import Pitch


def upload_csv(request):
    if request.method == 'POST':
        csv_url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/SampleData-YZQZfKzOO3XT9tOjltR0wcyU37BEyi.csv"
        response = requests.get(csv_url)

        if response.status_code == 200:
            csv_content = response.content.decode('utf-8')
            df = pd.read_csv(pd.compat.StringIO(csv_content))

            # Select only the columns we need
            df = df[['Pitcher', 'PlateLocHeight', 'PlateLocSide']]

            # Insert data into the database
            for _, row in df.iterrows():
                Pitch.objects.create(
                    pitcher=row['Pitcher'],
                    plate_loc_height=row['PlateLocHeight'],
                    plate_loc_side=row['PlateLocSide']
                )

            return HttpResponse("Data uploaded successfully!")
        else:
            return HttpResponse("Failed to fetch CSV file.")

    return render(request, 'pitch_data/upload.html')


def view_data(request):
    pitches = Pitch.objects.all()
    return render(request, 'pitch_data/view_data.html', {'pitches': pitches})

