import time
import docker
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from attack_defense.models import VulnBoxStatus, UptimeLog, ADSession

def generate_flag():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"CTF{{{random_str}}}"

class Command(BaseCommand):
    help = 'Monitors Docker container status, awards SLA points, and rotates flags automatically'

    def handle(self, *args, **options):
        try:
            client = docker.from_env()
        except docker.errors.DockerException as e:
            self.stderr.write(self.style.ERROR(f"Failed to connect to Docker daemon: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("Started VulnBox monitoring daemon..."))
        
        while True:
            now = timezone.now()
            statuses = VulnBoxStatus.objects.all()
            for status in statuses:
                try:
                    container = client.containers.get(status.container_name)
                    is_up = container.status == 'running'
                except docker.errors.NotFound:
                    is_up = False
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error checking {status.container_name}: {e}"))
                    is_up = False
                
                # SLA Points Logic
                if is_up:
                    status.uptime_ticks += 1
                    if status.uptime_ticks >= 6:  # 6 * 10s = 60s (1 minute)
                        # Award 1 defense point to their latest session
                        latest_session = ADSession.objects.filter(team=status.team, is_active=True).order_by('-created_at').first()
                        if latest_session:
                            latest_session.defense_points += 1
                            latest_session.save()
                        status.uptime_ticks = 0
                else:
                    status.uptime_ticks = 0 # reset if down
                
                # Automated Flag Rotation Logic (every 120 seconds)
                if not status.last_flag_rotation or (now - status.last_flag_rotation).total_seconds() >= 120:
                    new_flag = generate_flag()
                    
                    if is_up:
                        try:
                            # Inject flag into the container
                            container.exec_run(f"sh -c 'echo {new_flag} > /var/www/html/flag.txt'")
                            self.stdout.write(self.style.SUCCESS(f"Rotated flag for {status.team.name} ({status.container_name})"))
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Failed to inject flag for {status.team.name}: {e}"))
                            
                    # Update all sessions attacking this team
                    attacking_sessions = ADSession.objects.filter(target_team=status.team, is_active=True)
                    for session in attacking_sessions:
                        session.target_flag = new_flag
                        session.is_captured = False
                        session.last_submission_time = None
                        session.save()
                    
                    status.last_flag_rotation = now

                status.is_up = is_up
                status.save()
                
                # Log for dashboard charting
                UptimeLog.objects.create(container_name=status.container_name, is_up=is_up)
                
            # Database Pruning Logic (Keep logs for only the last 24 hours)
            cutoff = now - timedelta(days=1)
            UptimeLog.objects.filter(timestamp__lt=cutoff).delete()
                
            time.sleep(10)
