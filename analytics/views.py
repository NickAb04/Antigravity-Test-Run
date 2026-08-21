from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from jeopardy.models import Submission
from accounts.models import Team
from .services import calculate_momentum
import json
import csv
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.http import HttpResponse

@staff_member_required
def ai_dashboard(request):
    """
    Secure dashboard only accessible by Faculty / Administrators (is_staff).
    Iterates over all participants and computes real-time regression stats.
    """
    start_str = request.GET.get('start_time')
    end_str = request.GET.get('end_time')
    
    start_time = None
    end_time = None
    
    if start_str:
        dt = parse_datetime(start_str)
        if dt:
            start_time = make_aware(dt) if is_naive(dt) else dt
            
    if end_str:
        dt = parse_datetime(end_str)
        if dt:
            end_time = make_aware(dt) if is_naive(dt) else dt

    users = User.objects.filter(profile__role='participant').select_related('profile__team')
    analytics_data = []
    
    for user in users:
        momentum_slope, learning_state = calculate_momentum(user, start_time, end_time)
        analytics_data.append({
            'username': user.username,
            'team': user.profile.team.name if hasattr(user, 'profile') and user.profile.team else 'No Team',
            'momentum': momentum_slope,
            'state': learning_state
        })
        
    # Sort by momentum highest to lowest
    analytics_data.sort(key=lambda x: x['momentum'], reverse=True)
    
    # Prepare Graph Data for Teams
    teams = Team.objects.all()
    chart_data = {'datasets': []}
    
    for team in teams:
        submissions = Submission.objects.filter(user__profile__team=team, is_correct=True)
        if start_time:
            submissions = submissions.filter(timestamp__gte=start_time)
        if end_time:
            submissions = submissions.filter(timestamp__lte=end_time)
            
        submissions = submissions.order_by('timestamp')
        
        if not submissions.exists():
            continue
            
        team_data = []
        cum_score = 0
        for sub in submissions:
            cum_score += sub.challenge.points
            team_data.append({'x': sub.timestamp.isoformat(), 'y': cum_score})
            
        chart_data['datasets'].append({
            'label': team.name,
            'data': team_data,
            'tension': 0.2
        })
        
    context = {
        'analytics_data': analytics_data,
        'chart_data_json': json.dumps(chart_data),
        'start_time_val': start_str or '',
        'end_time_val': end_str or ''
    }
        
    return render(request, 'analytics/ai_dashboard.html', context)

@staff_member_required
def export_submissions_csv(request):
    """
    Export Jeopardy flag submissions to a CSV file.
    Supports filtering by start_time and end_time.
    """
    start_str = request.GET.get('start_time')
    end_str = request.GET.get('end_time')
    
    submissions = Submission.objects.all().select_related('user', 'user__profile__team', 'challenge', 'challenge__category').order_by('timestamp')
    
    if start_str:
        dt = parse_datetime(start_str)
        if dt:
            start_time = make_aware(dt) if is_naive(dt) else dt
            submissions = submissions.filter(timestamp__gte=start_time)
            
    if end_str:
        dt = parse_datetime(end_str)
        if dt:
            end_time = make_aware(dt) if is_naive(dt) else dt
            submissions = submissions.filter(timestamp__lte=end_time)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ctf_submissions_export.csv"'

    writer = csv.writer(response)
    # Header Row
    writer.writerow(['Timestamp', 'Username', 'Team Name', 'Challenge Title', 'Category', 'Submitted Flag', 'Is Correct', 'Points Awarded'])

    for sub in submissions:
        team_name = sub.user.profile.team.name if hasattr(sub.user, 'profile') and sub.user.profile.team else 'No Team'
        points = sub.challenge.points if sub.is_correct else 0
        
        # Format timestamp to string for CSV
        ts_str = sub.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        writer.writerow([
            ts_str,
            sub.user.username,
            team_name,
            sub.challenge.title,
            sub.challenge.category.name,
            sub.submitted_flag,
            sub.is_correct,
            points
        ])

    return response
