from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import json
from .models import VulnBoxStatus, ArenaAssignment, ADSession, UptimeLog
from accounts.models import Team

@login_required
def arena_pvp(request):
    if not hasattr(request.user, 'profile'):
        return render(request, 'attack_defense/arena.html', {'error': 'User has no profile.'})
        
    user_team = request.user.profile.team
    
    if not user_team:
        return render(request, 'attack_defense/arena.html', {'error': 'You are not assigned to a team.'})
        
    if hasattr(user_team, 'arena_assignment'):
        assignment = user_team.arena_assignment
        my_box = {
            'name': assignment.vulnbox_name, 
            'ip': assignment.vulnbox_ip, 
            'web_port': assignment.web_port, 
            'ssh_port': assignment.ssh_port,
            'container_name': getattr(user_team.vulnbox, 'container_name', 'Unknown') if hasattr(user_team, 'vulnbox') else 'Unknown',
        }
    else:
        my_box = None
        
    target_box = None
    latest_session = ADSession.objects.filter(team=user_team).order_by('-created_at').first()
    
    from django.db.models import Sum, F
    ad_points = 0
    if latest_session:
        total = ADSession.objects.filter(team=user_team).aggregate(
            t=Sum(F('points_earned') + F('defense_points'))
        )['t']
        ad_points = total if total else 0
        
        if latest_session.target_team and hasattr(latest_session.target_team, 'arena_assignment'):
            target_assignment = latest_session.target_team.arena_assignment
            target_box = {
                'name': target_assignment.vulnbox_name,
                'ip': target_assignment.vulnbox_ip,
                'web_port': target_assignment.web_port,
                'ssh_port': target_assignment.ssh_port
            }

    if not my_box or not target_box:
        return render(request, 'attack_defense/arena.html', {'error': 'Arena assignments or sessions are not fully configured yet.'})

    context = {
        'my_box': my_box,
        'target_box': target_box,
        'ad_points': ad_points,
        'team_name': user_team.name,
        'session_number': latest_session.session_number if latest_session else None
    }
    
    return render(request, 'attack_defense/arena.html', context)

@login_required
def admin_vulnbox_status(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    statuses = VulnBoxStatus.objects.all()
    data = []
    for s in statuses:
        latest_session = ADSession.objects.filter(team=s.team).order_by('-created_at').first()
        data.append({
            'team': s.team.name,
            'container_name': s.container_name,
            'is_up': s.is_up,
            'last_checked': s.last_checked.strftime('%Y-%m-%d %H:%M:%S'),
            'session_number': latest_session.session_number if latest_session else '-',
            'target_flag': latest_session.target_flag if latest_session else '-'
        })
        
    return JsonResponse({'statuses': data})

@login_required
def uptime_chart_data(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Fetch the last 30 logs for the chart
    logs = UptimeLog.objects.order_by('-timestamp')[:60]
    
    # Process into datasets by container_name
    chart_data = {}
    timestamps = []
    
    for log in reversed(logs):
        ts = log.timestamp.strftime('%H:%M:%S')
        if ts not in timestamps:
            timestamps.append(ts)
        
        if log.container_name not in chart_data:
            chart_data[log.container_name] = []
            
        chart_data[log.container_name].append({
            'x': ts,
            'y': 1 if log.is_up else 0
        })

    datasets = []
    colors = ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)', 'rgba(255, 206, 86, 1)']
    for i, (container, data_points) in enumerate(chart_data.items()):
        datasets.append({
            'label': container,
            'data': data_points,
            'borderColor': colors[i % len(colors)],
            'stepped': True,
            'fill': False
        })

    return JsonResponse({
        'labels': timestamps,
        'datasets': datasets
    })

@login_required
def admin_dashboard(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        return render(request, 'attack_defense/arena.html', {'error': 'Unauthorized'})
    return render(request, 'attack_defense/admin_dashboard.html')

@login_required
def admin_setup(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        return render(request, 'attack_defense/arena.html', {'error': 'Unauthorized'})
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_container':
            team_id = request.POST.get('team_id')
            box_type = request.POST.get('box_type')
            vulnbox_ip = request.POST.get('vulnbox_ip')
            
            if box_type == 'A':
                vulnbox_name = "Team A Box"
                container_name = "ctf_team_a_vulnbox"
                web_port = 8081
                ssh_port = 2221
            elif box_type == 'B':
                vulnbox_name = "Team B Box"
                container_name = "ctf_team_b_vulnbox"
                web_port = 8082
                ssh_port = 2222
            else:
                messages.error(request, "Invalid Box Type selected.")
                return redirect('ad_admin_setup')
            
            team = Team.objects.filter(id=team_id).first()
            if team:
                ArenaAssignment.objects.update_or_create(
                    team=team,
                    defaults={
                        'vulnbox_name': vulnbox_name,
                        'vulnbox_ip': vulnbox_ip,
                        'web_port': web_port,
                        'ssh_port': ssh_port,
                    }
                )
                if container_name:
                    VulnBoxStatus.objects.filter(container_name=container_name).exclude(team=team).delete()
                    VulnBoxStatus.objects.update_or_create(
                        team=team,
                        defaults={'container_name': container_name}
                    )
                messages.success(request, f"Updated container assignment for {team.name}")
                
        elif action == 'create_ad_session':
            session_number = request.POST.get('session_number')
            team_a_id = request.POST.get('team_a_id')
            team_b_id = request.POST.get('team_b_id')
            team_a_flag = request.POST.get('team_a_flag', 'CTF{default_a}')
            team_b_flag = request.POST.get('team_b_flag', 'CTF{default_b}')
            
            # Create two entries for the match: A attacks B, B attacks A
            ADSession.objects.update_or_create(
                session_number=session_number, team_id=team_a_id,
                defaults={'target_team_id': team_b_id, 'target_flag': team_b_flag, 'points_earned': 0, 'is_active': True}
            )
            ADSession.objects.update_or_create(
                session_number=session_number, team_id=team_b_id,
                defaults={'target_team_id': team_a_id, 'target_flag': team_a_flag, 'points_earned': 0, 'is_active': True}
            )
            
            # Initial flag injection for immediate effect
            import docker
            try:
                client = docker.from_env()
                team_a = Team.objects.get(id=team_a_id)
                team_b = Team.objects.get(id=team_b_id)
                if hasattr(team_a, 'vulnbox') and team_a.vulnbox.is_up:
                    container = client.containers.get(team_a.vulnbox.container_name)
                    container.exec_run(f"sh -c 'echo {team_b_flag} > /var/www/html/flag.txt'")
                if hasattr(team_b, 'vulnbox') and team_b.vulnbox.is_up:
                    container = client.containers.get(team_b.vulnbox.container_name)
                    container.exec_run(f"sh -c 'echo {team_a_flag} > /var/www/html/flag.txt'")
            except Exception as e:
                pass # Fail silently, daemon will handle it eventually
            
            messages.success(request, f"Created/Updated Session {session_number}")
            
        elif action == 'stop_ad_session':
            session_number = request.POST.get('session_number')
            ADSession.objects.filter(session_number=session_number).update(is_active=False)
            messages.success(request, f"Stopped Session {session_number}")

        elif action == 'delete_ad_session':
            session_number = request.POST.get('session_number')
            ADSession.objects.filter(session_number=session_number).delete()
            messages.success(request, f"Deleted Session {session_number}")

        return redirect('ad_admin_setup')

    from django.db.models import Sum, F
    teams = Team.objects.annotate(ad_points_total=Sum(F('ad_sessions__points_earned') + F('ad_sessions__defense_points')))
    assignments = ArenaAssignment.objects.all()
    
    session_numbers = ADSession.objects.values_list('session_number', flat=True).distinct().order_by('-session_number')
    
    import docker
    try:
        client = docker.from_env()
        containers = client.containers.list()
        container_names = [c.name for c in containers if 'vulnbox' in c.name.lower()]
    except Exception:
        container_names = ['ctf_team_a_vulnbox', 'ctf_team_b_vulnbox']
        
    return render(request, 'attack_defense/setup.html', {
        'teams': teams,
        'assignments': assignments,
        'session_numbers': session_numbers,
        'container_names': container_names
    })

@login_required
def ad_sessions_table(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    sessions = ADSession.objects.all().order_by('-session_number', 'team__name')
    session_data = []
    
    for s in sessions:
        # Find their own flag (the target_flag of the session where they are the target)
        opponent_session = ADSession.objects.filter(session_number=s.session_number, target_team=s.team).first()
        own_flag = opponent_session.target_flag if opponent_session else 'Unknown'
        
        session_data.append({
            'session_number': s.session_number,
            'team': s.team.name,
            'target_team': s.target_team.name if s.target_team else 'None',
            'own_flag': own_flag,
            'target_flag': s.target_flag,
            'points_earned': s.points_earned,
            'defense_points': s.defense_points,
            'is_active': s.is_active,
            'created_at': s.created_at
        })
        
    return render(request, 'attack_defense/partials/sessions_table.html', {'ad_sessions': session_data})

@login_required
def ad_points_table(request):
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    sessions_filter = request.GET.get('sessions', '')
    session_list = [s.strip() for s in sessions_filter.split(',') if s.strip().isdigit()]
    
    from django.db.models import Sum
    
    qs = ADSession.objects.all()
    if session_list:
        qs = qs.filter(session_number__in=session_list)
        
    teams = Team.objects.all()
    team_points = []
    
    for team in teams:
        team_qs = qs.filter(team=team)
        aggs = team_qs.aggregate(
            flag_pts=Sum('points_earned'),
            sla_pts=Sum('defense_points')
        )
        flag_pts = aggs['flag_pts'] or 0
        sla_pts = aggs['sla_pts'] or 0
        
        team_points.append({
            'team': team.name,
            'flag_pts': flag_pts,
            'sla_pts': sla_pts,
            'total_pts': flag_pts + sla_pts
        })
        
    return render(request, 'attack_defense/partials/points_table.html', {'team_points': team_points})

@login_required
def submit_ad_flag(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            submitted_flag = data.get('flag', '').strip()
            
            user_team = getattr(request.user.profile, 'team', None)
            if not user_team:
                return JsonResponse({'status': 'error', 'message': 'You are not in a team.'})
            
            # Find active session
            latest_session = ADSession.objects.filter(team=user_team).order_by('-created_at').first()
            if not latest_session:
                return JsonResponse({'status': 'error', 'message': 'No active Attack-Defense session found.'})
            
            if latest_session.is_captured:
                return JsonResponse({'status': 'error', 'message': 'Your team has already captured the flag for this session/rotation!'})
                
            if submitted_flag == latest_session.target_flag:
                # Team-based rate limiting / cooldown check
                now = timezone.now()
                if latest_session.last_submission_time and (now - latest_session.last_submission_time).total_seconds() < 60:
                    return JsonResponse({'status': 'error', 'message': 'Please wait 60 seconds before submitting another flag.'})
                    
                latest_session.last_submission_time = now
                latest_session.is_captured = True
                latest_session.points_earned += 10
                latest_session.save()
                
                return JsonResponse({'status': 'success', 'message': f'Flag accepted! +10 Points in Session {latest_session.session_number}!'})
            else:
                now = timezone.now()
                if latest_session.last_submission_time and (now - latest_session.last_submission_time).total_seconds() < 10:
                     return JsonResponse({'status': 'error', 'message': 'Please wait 10 seconds before guessing again.'})
                latest_session.last_submission_time = now
                latest_session.save()
                return JsonResponse({'status': 'error', 'message': 'Incorrect flag.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
