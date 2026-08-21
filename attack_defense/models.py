from django.db import models
from accounts.models import Team

class VulnBoxStatus(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='vulnbox')
    container_name = models.CharField(max_length=100, unique=True)
    is_up = models.BooleanField(default=False)
    last_checked = models.DateTimeField(auto_now=True)
    uptime_ticks = models.IntegerField(default=0)
    last_flag_rotation = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.team.name} Box - {'UP' if self.is_up else 'DOWN'}"

class ArenaAssignment(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='arena_assignment')
    vulnbox_name = models.CharField(max_length=100, help_text="e.g. Team A VulnBox")
    vulnbox_ip = models.GenericIPAddressField()
    web_port = models.IntegerField(default=80)
    ssh_port = models.IntegerField(default=22)
    target_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_by', help_text="The team this team is assigned to attack")
    flag = models.CharField(max_length=255, default='CTF{default}')
    ad_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} Assignment"

class ADSession(models.Model):
    session_number = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='ad_sessions')
    target_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    target_flag = models.CharField(max_length=255)
    points_earned = models.IntegerField(default=0)
    defense_points = models.IntegerField(default=0)
    is_captured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_submission_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session {self.session_number}: {self.team.name} -> {self.target_team.name if self.target_team else 'None'}"

class UptimeLog(models.Model):
    container_name = models.CharField(max_length=100)
    is_up = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
