import matplotlib
from django.shortcuts import render
import sqlite3
import seaborn as sns
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from django.conf import settings


def generate_heatmap(pitcher=None):
    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    query = "SELECT * FROM heatmaps_pitch"
    if pitcher:
        query += f" WHERE Pitcher = '{pitcher}'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    columns_to_keep = ['pitcher', 'platelocheight', 'platelocside']
    new_df = df[columns_to_keep].dropna()

    sns.kdeplot(
        x=new_df['platelocside'],
        y=new_df['platelocheight'],
        cmap="Reds",
        thresh=0,
        fill=True,
        bw_adjust=0.5
    )

    rect = patches.Rectangle((-0.71, 1.5), 1.42, 2, linewidth=1, edgecolor='black', facecolor='none')
    plt.gca().add_patch(rect)
    plt.title('Heatmap of Location for {}'.format(pitcher))
    plt.xlabel('PlateLocSide')
    plt.ylabel('PlateLocHeight')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64

def heatmap_view(request):
    pitcher = request.GET.get('pitcher')
    heatmap = generate_heatmap(pitcher)

    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    pitchers_df = pd.read_sql_query("SELECT DISTINCT Pitcher FROM heatmaps_pitch", conn)
    conn.close()
    pitchers = pitchers_df['pitcher'].tolist()

    return render(request, 'heatmaps/heatmaps.html', {'heatmap': heatmap, 'pitchers': pitchers})