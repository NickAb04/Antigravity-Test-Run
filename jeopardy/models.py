from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Challenge(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='challenges')
    description = models.TextField()
    points = models.IntegerField(default=10)
    flag = models.CharField(max_length=255)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.points} pts)"

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_flag = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True) # CRITICAL for AI Analytics

    def __str__(self):
        return f"{self.user.username} -> {self.challenge.title} [{self.is_correct}]"
