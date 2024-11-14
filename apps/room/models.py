from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.number} - {self.id}"
