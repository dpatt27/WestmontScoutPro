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

    columns_to_keep = ['pitcher', 'platelocheight', 'platelocside', 'exitspeed', 'pitchcall']
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
    elif heatmapType == 'whiffs':
        whiffs_df = new_df[new_df['pitchcall'] == 'StrikeSwinging']
        sns.kdeplot(
            x=whiffs_df['platelocside'],
            y=whiffs_df['platelocheight'],
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
    if heatmapType == 'whiffs':
        title += ' (Whiffs)'
    plt.title(title)
    plt.xlabel('PlateLocSide')
    plt.ylabel('PlateLocHeight')
    plt.xlim(-2.21, 2.21)
    plt.ylim(0.0, 4.5)

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
    pitch_order = ["Fastball", "Slider", "Changeup"]
    unique_pitches = [pitch for pitch in df['pitchtype'].unique() if pitch not in pitch_order]
    pitch_order.extend(unique_pitches)

    # Create figure
    plt.figure(figsize=(6, 4))  # Adjusted figsize to make the plot smaller

    # Improved scatter plot
    sns.scatterplot(
        x=df['platelocside'],
        y=df['platelocheight'],
        hue=df['pitchtype'],
        palette="tab10",  # Use a better color scheme
        hue_order=pitch_order,  # Specify the custom order for the legend
        s=20,  # Increase size for visibility
        edgecolor='black',
        alpha=0.75  # Better opacity for visibility
    )

    # Strike zone (adjusted to better proportions)
    strike_zone = patches.Rectangle(
        (-0.75, 1.5), 1.7, 2.0,
        linewidth=2, edgecolor='black', facecolor='none', linestyle='dashed'
    )
    plt.gca().add_patch(strike_zone)

    # Adjust limits for better framing
    plt.xlim(-2.21, 2.21)
    plt.ylim(0.0, 4.5)

    # Better titles and labels
    plt.title(f'Pitch Locations for {batter}', fontsize=14, fontweight='bold')
    plt.xlabel('Plate Location Side', fontsize=12)
    plt.ylabel('Plate Location Height', fontsize=12)
    plt.legend(title='Pitch Type', fontsize=6)

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
    pitch_summary_html = None
    summary_html = None

    if batter:
        conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
        query = "SELECT * FROM heatmaps_pitch WHERE batter = ?"
        df = pd.read_sql_query(query, conn, params=(batter,))
        conn.close()

        pitches_plot = generate_pitches_plot(batter)

        # Calculate high-level stats
        nonzero_exit_speeds = df[df["exitspeed"] > 0]["exitspeed"]
        chases = len(df[
                         (df["pitchcall"] == "StrikeSwinging") &
                         ~((df["platelocside"].between(-0.75, 1.5)) & (df["platelocheight"].between(1.5, 3.5)))
                         ])

        whiffs = len(df[df["pitchcall"] == "StrikeSwinging"])

        # Calculate Total Swings
        total_swings = len(
            df[df["pitchcall"].isin(["FoulBallNotFieldable", "InPlay", "StrikeSwinging", "FoulBallFieldable"])])

        balls_in_play = df[df["pitchcall"] == "InPlay"]

        # Calculate Hard-Hit Balls (exit speed > 90)
        hard_hits = len(balls_in_play[balls_in_play["exitspeed"] > 90])

        # Calculate Percentages (avoid division by zero)
        chase_percentage = round((chases / total_swings) * 100, 2) if total_swings > 0 else 0
        whiff_percentage = round((whiffs / total_swings) * 100, 2) if total_swings > 0 else 0
        hard_hit_percentage = round((hard_hits / len(balls_in_play)) * 100, 2) if len(balls_in_play) > 0 else 0

        summary = {
            "Plate Appearances": len(df[df["pitchcall"].isin(["InPlay", "Walk", "HitByPitch"])]) + len(
                df[df["korbb"] == "Strikeout"]),
            "Hits": len(df[df["playresult"] == "Single"]) + len(df[df["playresult"] == "Double"]) + len(
                df[df["playresult"] == "Triple"]) + len(df[df["playresult"] == "HomeRun"]),
            "1B": len(df[df["playresult"] == "Single"]),
            "2B": len(df[df["playresult"] == "Double"]),
            "3B": len(df[df["playresult"] == "Triple"]),
            "HR": len(df[df["playresult"] == "HomeRun"]),
            "Walks + HBP": len(df[df["korbb"] == "Walk"]),
            "Strikeouts": len(df[df["korbb"] == "Strikeout"]),
            "Chase%": chase_percentage,
            "Whiff%": whiff_percentage,
            "HardHit%": hard_hit_percentage,
            "AvgEV": round(nonzero_exit_speeds.mean(), 2),
            "MaxEV": round(df["exitspeed"].max(), 2),

        }


        # Convert summary to DataFrame for display
        summary_df = pd.DataFrame([summary])
        summary_df = summary_df.style.set_properties(**{
            "background-color": "#003366",
            "color": "white",
            "border-color": "white",
            "text-align": "center"
        }).set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#990000'), ('color', 'white')]
        }])

        # Convert summary DataFrame to HTML table
        summary_html = summary_df.to_html(classes="table table-striped", index=False)

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
        'selected_team': team,
        'pitch_summary': pitch_summary_html,
        'summary': summary_html
    })