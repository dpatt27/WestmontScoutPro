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

    # Parameterized query to prevent SQL injection
    query = "SELECT platelocside, platelocheight, pitchtype FROM heatmaps_pitch WHERE batter = ?"
    df = pd.read_sql_query(query, conn, params=(batter,))
    conn.close()

    # Create figure
    plt.figure(figsize=(10, 8))

    # Improved scatter plot
    sns.scatterplot(
        x=df['platelocside'],
        y=df['platelocheight'],
        hue=df['pitchtype'],
        palette="tab10",  # Use a better color scheme
        s=120,  # Increase size for visibility
        edgecolor='black',
        alpha=0.75  # Better opacity for visibility
    )

    # Strike zone (adjusted to better proportions)
    strike_zone = patches.Rectangle(
        (-0.85, 1.5), 1.7, 2.0,
        linewidth=2, edgecolor='black', facecolor='none', linestyle='dashed'
    )
    plt.gca().add_patch(strike_zone)

    # Adjust limits for better framing
    plt.xlim(-2.2, 2.2)
    plt.ylim(0.5, 4.5)

    # Better titles and labels
    plt.title(f'Pitch Locations for {batter}', fontsize=14, fontweight='bold')
    plt.xlabel('Plate Location Side', fontsize=12)
    plt.ylabel('Plate Location Height', fontsize=12)
    plt.legend(title='Pitch Type', fontsize=10)

    # Save plot as a Base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)  # High DPI for clarity
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()  # Close plot to prevent memory issues

    return image_base64


def hitters_view(request):
    batter = request.GET.get('batter')
    team = request.GET.get('team')

    max_exit_velo = None
    pitches_plot = None

    if batter:
        conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
        query = "SELECT MAX(exitspeed) as max_exit_velo FROM heatmaps_pitch WHERE batter = ?"
        max_exit_velo = pd.read_sql_query(query, conn, params=(batter,))['max_exit_velo'].iloc[0]
        conn.close()
        pitches_plot = generate_pitches_plot(batter)

    conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
    batters_query = "SELECT DISTINCT batter FROM heatmaps_pitch"
    teams_query = "SELECT DISTINCT batter_team FROM heatmaps_pitch"

    if team:
        batters_query += " WHERE batter_team = ?"
        batters_df = pd.read_sql_query(batters_query, conn, params=(team,))
    else:
        batters_df = pd.read_sql_query(batters_query, conn)

    teams_df = pd.read_sql_query(teams_query, conn)
    conn.close()

    batters = batters_df['batter'].tolist()
    teams = teams_df['batter_team'].tolist()

    return render(request, 'heatmaps/hitters.html', {
        'batters': batters,
        'selected_batter': batter,
        'max_exit_velo': max_exit_velo,
        'pitches_plot': pitches_plot,
        'teams': teams,
        'selected_team': team
    })