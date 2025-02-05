from django.db import models

class Pitch(models.Model):
    pitcher = models.CharField(max_length=100)
    platelocheight = models.FloatField(null=True, blank=True)
    platelocside = models.FloatField(null=True, blank=True)