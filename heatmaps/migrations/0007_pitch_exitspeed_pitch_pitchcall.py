# Generated by Django 4.2.18 on 2025-03-05 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heatmaps', '0006_remove_pitch_exitvelo_remove_pitch_pitchcall'),
    ]

    operations = [
        migrations.AddField(
            model_name='pitch',
            name='exitspeed',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='pitch',
            name='pitchcall',
            field=models.CharField(default='DEFAULT VALUE', max_length=100),
        ),
    ]
