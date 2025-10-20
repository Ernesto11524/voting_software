from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Position(models.Model):
    position_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.position_name

class Candidate(models.Model):
    candidate_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_name')
    photo = models.ImageField(upload_to='candidate_photos/')
    candidate_position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidate_position')

    class Meta:
        unique_together = ('candidate_name', 'candidate_position')

    def __str__(self):
        return f"{self.candidate_name.first_name} {self.candidate_name.last_name}"

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    choice = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')

    def __str__(self):
        return f"{self.voter.username} voted {self.choice} for {self.candidate} as {self.position}"