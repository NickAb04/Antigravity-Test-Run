from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Q, Max
from django.utils import timezone
from .models import Category, Challenge, Submission
from accounts.models import Team
import json
from datetime import timedelta

@login_required
def dashboard(request):
    categories = Category.objects.prefetch_related('challenges').all()
    solved_challenge_ids = Submission.objects.filter(user=request.user, is_correct=True).values_list('challenge_id', flat=True)

    context = {
        'categories': categories,
        'solved_challenge_ids': solved_challenge_ids
    }
    return render(request, 'jeopardy/dashboard.html', context)

@login_required
def submit_flag(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            challenge_id = data.get('challenge_id')
            submitted_flag = data.get('flag', '').strip()

            challenge = get_object_or_404(Challenge, id=challenge_id)

            # Prevent resubmission
            if Submission.objects.filter(user=request.user, challenge=challenge, is_correct=True).exists():
                return JsonResponse({'status': 'error', 'message': 'You have already solved this challenge!'})

            # Rate Limiting: 5-second cooldown
            last_submission = Submission.objects.filter(user=request.user).order_by('-timestamp').first()
            if last_submission and timezone.now() < last_submission.timestamp + timedelta(seconds=5):
                return JsonResponse({'status': 'error', 'message': 'Slow down! Please wait 5 seconds between submissions.'})

            # Check correctness
            is_correct = (challenge.flag == submitted_flag)
            
            # Log Submission
            Submission.objects.create(
                user=request.user,
                challenge=challenge,
                submitted_flag=submitted_flag,
                is_correct=is_correct
            )

            if is_correct:
                return JsonResponse({'status': 'success', 'message': 'Correct Flag! Points awarded.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Incorrect Flag. Try again!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def leaderboard(request):
    return render(request, 'jeopardy/leaderboard.html')

@login_required
def leaderboard_data(request):
    teams = Team.objects.annotate(
        score=Sum('members__user__submissions__challenge__points', filter=Q(members__user__submissions__is_correct=True)),
        last_solve=Max('members__user__submissions__timestamp', filter=Q(members__user__submissions__is_correct=True))
    )
    
    leaderboard_list = []
    for team in teams:
        leaderboard_list.append({
            'name': team.name,
            'score': team.score or 0,
            'last_solve': team.last_solve.isoformat() if team.last_solve else 'N/A'
        })
    
    # Sort by score descending, then earlier solve wins tie
    leaderboard_list.sort(key=lambda x: (-x['score'], x['last_solve'] if x['last_solve'] != 'N/A' else '9999-12-31'))
    
    return JsonResponse({'leaderboard': leaderboard_list})
