from django.db import models

class Pitch(models.Model):
    pitcher = models.CharField(max_length=100)
    plate_loc_height = models.FloatField()
    plate_loc_side = models.FloatField()

    def __str__(self):
        return f"{self.pitcher} - Height: {self.plate_loc_height}, Side: {self.plate_loc_side}"

