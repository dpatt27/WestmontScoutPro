from django.db import models

class Pitch(models.Model):
    pitcher = models.CharField(max_length=100)
    plate_loc_height = models.FloatField()
    plate_loc_side = models.FloatField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_loc_height} {self.plate_loc_side}"