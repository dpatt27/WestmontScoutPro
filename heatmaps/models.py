from django.db import models

class Pitch(models.Model):
    pitcher = models.CharField(max_length=100)
    platelocheight = models.FloatField()
    platelocside = models.FloatField()


    def __str__(self):
        return f"{self.platelocheight} {self.platelocside}"