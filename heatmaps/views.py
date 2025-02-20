from django.shortcuts import render
import sqlite3
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from django.conf import settings
from .models import Pitch

def generate_heatmap():
    # Connect to SQLite database
    conn = sqlite3.connect('db.sqlite3')
    df = pd.read_sql_query("SELECT * FROM heatmaps_pitch", conn)
    conn.close()
    print(df.columns)

    columns_to_keep = ['pitcher', 'platelocheight', 'platelocside']

    # Create a new DataFrame with only the selected columns
    new_df = df[columns_to_keep]
    new_df = new_df.dropna()

    # Create the heatmap
    location_df = new_df[['platelocheight', 'platelocside']]  # Use filtered_df if filtering

    # Create a scatterplot with color based on location
    sns.kdeplot(
        x=location_df['platelocside'],
        y=location_df['platelocheight'],
        cmap="Reds",
        shade=True,
        thresh=0,
        fill=True,
        bw_adjust=0.5
    )

    # Create the strike zone rectangle
    rect = patches.Rectangle((-0.71, 1.5), 1.42, 2, linewidth=1, edgecolor='black', facecolor='none')

    # Add the rectangle to the plot
    plt.gca().add_patch(rect)

    plt.title('Heatmap of Location and Exit Speed')
    plt.xlabel('PlateLocSide')
    plt.ylabel('PlateLocHeight')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64

def heatmap_view(request):
    heatmap = generate_heatmap()
    return render(request, 'heatmaps/heatmaps.html', {'heatmap': heatmap})
