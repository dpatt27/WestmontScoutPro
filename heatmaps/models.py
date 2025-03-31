from django.db import models

class Pitch(models.Model):
    pitcher = models.CharField(max_length=100)
    pitchtype = models.CharField(max_length=100, default='DEFAULT VALUE')
    velo = models.FloatField(default=0)
    platelocheight = models.FloatField()
    platelocside = models.FloatField()
    pitchcall = models.CharField(max_length=100, default='DEFAULT VALUE')
    exitspeed = models.FloatField(default=0)
    batter = models.CharField(max_length=100, default='DEFAULT VALUE')
    batter_team = models.CharField(max_length=100, default='DEFAULT VALUE')
    playresult = models.CharField(max_length=100, default='DEFAULT VALUE')
    korbb = models.CharField(max_length=100, default='DEFAULT VALUE')

    def __str__(self):
        return f"{self.platelocheight} {self.platelocside}"