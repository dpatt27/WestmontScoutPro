from django.shortcuts import render
from django.http import JsonResponse
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

def home_view(request):
    return render(request, 'home.html')

def generate_heatmap(pitcher=None, pitchtype=None, heatmapType='location'):
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

    columns_to_keep = ['pitcher', 'platelocheight', 'platelocside', 'exitspeed']
    new_df = df[columns_to_keep].dropna()

    plt.figure(figsize=(10, 8))
    if heatmapType == 'exitVelo':
        sns.kdeplot(
            x=new_df['platelocside'],
            y=new_df['platelocheight'],
            weights=new_df['exitspeed'],
            cmap="coolwarm",
            fill=True,
            bw_adjust=0.5
        )
    else:
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
    plt.xlim(-2.21, 2.21)
    plt.ylim(0.5, 4.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.clf()
    plt.close()
    return image_base64

def heatmap_view(request):
    pitcher = request.GET.get('pitcher')
    pitch_type = request.GET.get('pitchtype')
    heatmap_type = request.GET.get('heatmapType', 'location')
    heatmap = generate_heatmap(pitcher, pitch_type, heatmap_type)

    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    pitchers_df = pd.read_sql_query("SELECT DISTINCT pitcher FROM heatmaps_pitch", conn)
    conn.close()
    pitchers = pitchers_df['pitcher'].tolist()

    pitchtypes = []
    if pitcher:
        conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
        pitchtypes_df = pd.read_sql_query(f"SELECT DISTINCT pitchtype FROM heatmaps_pitch WHERE pitcher = '{pitcher}'", conn)
        conn.close()
        pitchtypes = pitchtypes_df['pitchtype'].tolist()

    return render(request, 'heatmaps/heatmaps.html', {
        'heatmap': heatmap,
        'pitchers': pitchers,
        'pitchtypes': pitchtypes,
        'selected_pitcher': pitcher,
        'selected_pitchtype': pitch_type,
        'selected_heatmapType': heatmap_type
    })

def get_pitchtypes(request):
    pitcher = request.GET.get('pitcher')
    pitchtypes = []
    if pitcher:
        conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
        pitchtypes_df = pd.read_sql_query(f"SELECT DISTINCT pitchtype FROM heatmaps_pitch WHERE pitcher = '{pitcher}'", conn)
        conn.close()
        pitchtypes = pitchtypes_df['pitchtype'].tolist()
    return JsonResponse({'pitchtypes': pitchtypes})

def generate_pitches_plot(batter):
    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    query = f"SELECT * FROM heatmaps_pitch WHERE batter = '{batter}'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    plt.figure(figsize=(10, 8))
    sns.scatterplot(
        x=df['platelocside'],
        y=df['platelocheight'],
        hue=df['pitchtype'],
        palette='viridis',
        s=100,
        edgecolor='w',
        alpha=0.7
    )
    rect = patches.Rectangle((-0.71, 1.5), 1.42, 2, linewidth=1, edgecolor='black', facecolor='none')
    plt.gca().add_patch(rect)
    plt.xlim(-2.21, 2.21)
    plt.ylim(0.5, 4.5)
    plt.title(f'Pitches Seen by {batter}')
    plt.xlabel('Plate Location Side')
    plt.ylabel('Plate Location Height')
    plt.legend(title='Pitch Type')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.clf()
    plt.close()
    return image_base64

def hitters_view(request):
    batter = request.GET.get('batter')

    max_exit_velo = None
    pitches_plot = None

    if batter:
        conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
        query = f"SELECT MAX(exitspeed) as max_exit_velo FROM heatmaps_pitch WHERE batter = '{batter}'"
        max_exit_velo = pd.read_sql_query(query, conn)['max_exit_velo'].iloc[0]
        conn.close()

        pitches_plot = generate_pitches_plot(batter)

    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    batters_df = pd.read_sql_query("SELECT DISTINCT batter FROM heatmaps_pitch", conn)
    conn.close()
    batters = batters_df['batter'].tolist()

    return render(request, 'heatmaps/hitters.html', {
        'batters': batters,
        'selected_batter': batter,
        'max_exit_velo': max_exit_velo,
        'pitches_plot': pitches_plot
    })