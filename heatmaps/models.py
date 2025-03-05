from django.db import models

class Pitch(models.Model):
    pitcher = models.CharField(max_length=100)
    pitchtype = models.CharField(max_length=100, default='DEFAULT VALUE')
    velo = models.FloatField(default=0)
    platelocheight = models.FloatField()
    platelocside = models.FloatField()
    pitchcall = models.CharField(max_length=100, default='DEFAULT VALUE')
    exitspeed = models.FloatField(default=0)

    def __str__(self):
        return f"{self.platelocheight} {self.platelocside}"