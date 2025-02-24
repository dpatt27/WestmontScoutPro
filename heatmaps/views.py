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

def generate_heatmap(pitcher=None, pitchtype=None):
    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    query = "SELECT * FROM heatmaps_pitch"
    conditions = []
    if pitcher:
        conditions.append(f"Pitcher = '{pitcher}'")
    if pitchtype:
        conditions.append(f"pitchtype = '{pitchtype}'")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    df = pd.read_sql_query(query, conn)
    conn.close()

    columns_to_keep = ['pitcher', 'platelocheight', 'platelocside']
    new_df = df[columns_to_keep].dropna()

    sns.kdeplot(
        x=new_df['platelocside'],
        y=new_df['platelocheight'],
        cmap="coolwarm",
        thresh=0.1,
        fill=True,
        bw_adjust=0.5
    )

    rect = patches.Rectangle((-0.71, 1.5), 1.42, 2, linewidth=1, edgecolor='black', facecolor='none')
    plt.gca().add_patch(rect)
    title = 'Heatmap of Location for'
    if pitcher:
        title += f' {pitcher}'
    if pitchtype:
        title += f' ({pitchtype})'
    plt.title(title)
    plt.xlabel('PlateLocSide')
    plt.ylabel('PlateLocHeight')
    plt.xlim(-2.21, 2.21)  # Set x-axis limits
    plt.ylim(0.5, 4.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.clf()  # Clear the current figure
    plt.close()
    return image_base64

def heatmap_view(request):
    pitcher = request.GET.get('pitcher')
    pitch_type = request.GET.get('pitchtype')
    heatmap = generate_heatmap(pitcher, pitch_type)

    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    pitchers_df = pd.read_sql_query("SELECT DISTINCT pitcher FROM heatmaps_pitch", conn)
    pitchtypes_df = pd.read_sql_query("SELECT DISTINCT pitchtype FROM heatmaps_pitch", conn)
    conn.close()
    pitchers = pitchers_df['pitcher'].tolist()
    pitchtypes = pitchtypes_df['pitchtype'].tolist()

    return render(request, 'heatmaps/heatmaps.html', {
        'heatmap': heatmap,
        'pitchers': pitchers,
        'pitchtypes': pitchtypes,
        'selected_pitcher': pitcher,
        'selected_pitchtype': pitch_type
    })