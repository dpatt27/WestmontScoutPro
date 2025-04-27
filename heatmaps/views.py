from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import seaborn as sns
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64


def home_view(request):
    return render(request, 'home.html')


def generate_heatmap(pitcher=None, pitchtype=None, heatmapType='location'):
    query = "SELECT * FROM heatmaps_pitch"
    conditions = []
    if pitcher:
        conditions.append(f"pitcher = '{pitcher}'")
    if pitchtype:
        conditions.append(f"pitchtype = '{pitchtype}'")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    df = pd.read_sql_query(query, connection)

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

    pitchers_df = pd.read_sql_query("SELECT DISTINCT pitcher FROM heatmaps_pitch", connection)
    pitchers = pitchers_df['pitcher'].tolist()

    pitchtypes = []
    if pitcher:
        pitchtypes_df = pd.read_sql_query(
            f"SELECT DISTINCT pitchtype FROM heatmaps_pitch WHERE pitcher = '{pitcher}'", connection
        )
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
        pitchtypes_df = pd.read_sql_query(
            f"SELECT DISTINCT pitchtype FROM heatmaps_pitch WHERE pitcher = '{pitcher}'", connection
        )
        pitchtypes = pitchtypes_df['pitchtype'].tolist()
    return JsonResponse({'pitchtypes': pitchtypes})


def generate_pitches_plot(batter):
    query = "SELECT platelocside, platelocheight, pitchtype FROM heatmaps_pitch WHERE batter = %s"
    df = pd.read_sql_query(query, connection, params=[batter])

    pitch_order = ["Fastball", "Slider", "Changeup"]
    unique_pitches = [pitch for pitch in df['pitchtype'].unique() if pitch not in pitch_order]
    pitch_order.extend(unique_pitches)

    plt.figure(figsize=(6, 4))

    sns.scatterplot(
        x=df['platelocside'],
        y=df['platelocheight'],
        hue=df['pitchtype'],
        palette="tab10",
        hue_order=pitch_order,
        s=20,
        edgecolor='black',
        alpha=0.75
    )

    strike_zone = patches.Rectangle(
        (-0.75, 1.5), 1.7, 2.0,
        linewidth=2, edgecolor='black', facecolor='none', linestyle='dashed'
    )
    plt.gca().add_patch(strike_zone)

    plt.xlim(-2.21, 2.21)
    plt.ylim(0.0, 4.5)
    plt.title(f'Pitch Locations for {batter}', fontsize=14, fontweight='bold')
    plt.xlabel('Plate Location Side', fontsize=12)
    plt.ylabel('Plate Location Height', fontsize=12)
    plt.legend(title='Pitch Type', fontsize=6)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return image_base64


def hitters_view(request):
    batter = request.GET.get('batter')
    team = request.GET.get('team')

    max_exit_velo = None
    pitches_plot = None
    pitch_summary_html = None
    summary_html = None

    if batter:
        query = "SELECT * FROM heatmaps_pitch WHERE batter = %s"
        df = pd.read_sql_query(query, connection, params=[batter])

        pitches_plot = generate_pitches_plot(batter)

        nonzero_exit_speeds = df[df["exitspeed"] > 0]["exitspeed"]
        chases = len(df[
                         (df["pitchcall"] == "StrikeSwinging") &
                         ~((df["platelocside"].between(-0.75, 1.5)) & (df["platelocheight"].between(1.5, 3.5)))
                         ])
        whiffs = len(df[df["pitchcall"] == "StrikeSwinging"])
        total_swings = len(
            df[df["pitchcall"].isin(["FoulBallNotFieldable", "InPlay", "StrikeSwinging", "FoulBallFieldable"])])
        balls_in_play = df[df["pitchcall"] == "InPlay"]
        hard_hits = len(balls_in_play[balls_in_play["exitspeed"] > 90])

        chase_percentage = round((chases / total_swings) * 100, 2) if total_swings > 0 else 0
        whiff_percentage = round((whiffs / total_swings) * 100, 2) if total_swings > 0 else 0
        hard_hit_percentage = round((hard_hits / len(balls_in_play)) * 100, 2) if len(balls_in_play) > 0 else 0

        summary = {
            "Plate Appearances": len(df[df["pitchcall"].isin(["InPlay", "Walk", "HitByPitch"])]) + len(
                df[df["korbb"] == "Strikeout"]),
            "Hits": len(df[df["playresult"] == "Single"]) + len(df[df["playresult"] == "Double"]) +
                    len(df[df["playresult"] == "Triple"]) + len(df[df["playresult"] == "HomeRun"]),
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

        summary_html = summary_df.to_html(classes="table table-striped", index=False)

    batters_query = "SELECT DISTINCT batter FROM heatmaps_pitch"
    teams_query = "SELECT DISTINCT batter_team FROM heatmaps_pitch"

    if team:
        batters_query += " WHERE batter_team = %s"
        batters_df = pd.read_sql_query(batters_query, connection, params=[team])
    else:
        batters_df = pd.read_sql_query(batters_query, connection)

    teams_df = pd.read_sql_query(teams_query, connection)

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
