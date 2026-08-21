import pandas as pd
from sklearn.linear_model import LinearRegression
from jeopardy.models import Submission

def calculate_momentum(user, start_time_filter=None, end_time_filter=None):
    """
    Computes the student's scoring Momentum using Linear Regression.
    Evaluates cumulative score over elapsed time (in minutes).
    """
    submissions = Submission.objects.filter(user=user, is_correct=True)
    if start_time_filter:
        submissions = submissions.filter(timestamp__gte=start_time_filter)
    if end_time_filter:
        submissions = submissions.filter(timestamp__lte=end_time_filter)
        
    submissions = submissions.order_by('timestamp')
    
    # ----------------------------------------------------
    # Constraint Fulfilled: Cold Start Math Problem
    # n < 2 fallback to prevent division-by-zero or crashes
    # ----------------------------------------------------
    if submissions.count() < 2:
        return 0.0, 'Insufficient Data (n<2)'

    start_time = submissions.first().timestamp
    data = []
    cumulative_score = 0

    for sub in submissions:
        cumulative_score += sub.challenge.points
        # Normalize timestamp to elapsed minutes since first solve
        elapsed_minutes = (sub.timestamp - start_time).total_seconds() / 60.0
        data.append({'time_elapsed': elapsed_minutes, 'score': cumulative_score})

    df = pd.DataFrame(data)
    
    # Independent variable (X): Elapsed time
    # Dependent variable (y): Cumulative score
    X = df[['time_elapsed']].values
    y = df['score'].values

    # Fit the Least Squares model
    model = LinearRegression()
    # Need to handle edge case where time_elapsed is perfectly identical causing singular matrix
    try:
        model.fit(X, y)
        slope = model.coef_[0]
    except Exception:
        return 0.0, 'Stagnation (Math Error)'

    # Categorize momentum
    if slope > 2.0:
        state = 'Flow State (High Momentum)'
    elif slope > 0.5:
        state = 'Steady Progress'
    elif slope > 0:
        state = 'Struggling'
    else:
        state = 'Stagnation (Low Momentum)'
        
    return round(slope, 3), state
