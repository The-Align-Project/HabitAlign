import uuid
import pandas as pd
from datetime import datetime, timedelta


def generate_id():
    """Generate a unique ID for a habit or log entry"""
    return str(uuid.uuid4())


def get_current_streak(habit_id, logs_df):
    """
    Calculate current streak for a specific habit
    Returns the number of consecutive days the habit has been completed
    """
    if logs_df.empty:
        return 0

    # Filter logs for this habit
    habit_logs = logs_df[logs_df['habit_id'] == habit_id].copy()

    if habit_logs.empty:
        return 0

    # Convert dates to datetime
    habit_logs['date'] = pd.to_datetime(habit_logs['date'])

    # Sort by date in descending order (most recent first)
    habit_logs = habit_logs.sort_values('date', ascending=False)

    # Get today and yesterday
    today = datetime.now().date()

    # Check if there's a log for today
    today_log = habit_logs[habit_logs['date'].dt.date == today]
    if today_log.empty or not today_log.iloc[0]['completed']:
        # If no log for today or today is incomplete, check yesterday
        yesterday = today - timedelta(days=1)
        yesterday_log = habit_logs[habit_logs['date'].dt.date == yesterday]

        if yesterday_log.empty or not yesterday_log.iloc[0]['completed']:
            # If no log for yesterday or yesterday is incomplete, streak is 0
            return 0

    # Calculate the streak
    streak = 0
    current_date = today

    while True:
        # Check if there's a log for current_date
        current_log = habit_logs[habit_logs['date'].dt.date == current_date]

        if current_log.empty:
            # If there's a gap and it's not today (today can be incomplete and still count), break
            if current_date != today:
                break
        elif not current_log.iloc[0]['completed']:
            # If the habit was not completed on this date, break
            if current_date != today:
                break
        else:
            # If completed, increment streak
            streak += 1

        # Move to previous day
        current_date -= timedelta(days=1)

        # Check logs for the current date
        current_date_logs = habit_logs[habit_logs['date'].dt.date == current_date]

        if current_date_logs.empty or not current_date_logs.iloc[0]['completed']:
            # If no log or not completed for this date, streak ends
            break

    return streak


def get_longest_streak(habits_df, logs_df):
    """
    Find the habit with the longest streak and return (habit_name, streak_length)
    """
    if habits_df.empty or logs_df.empty:
        return ("", 0)

    max_streak = 0
    max_streak_habit = ""

    for _, habit in habits_df.iterrows():
        habit_id = habit['id']
        habit_logs = logs_df[logs_df['habit_id'] == habit_id].copy()

        if habit_logs.empty:
            continue

        # Convert dates to datetime
        habit_logs['date'] = pd.to_datetime(habit_logs['date'])

        # Sort by date
        habit_logs = habit_logs.sort_values('date')

        # Get completed logs
        completed_logs = habit_logs[habit_logs['completed'] == True]

        if completed_logs.empty:
            continue

        # Calculate the longest streak
        streak = 1
        max_streak_for_habit = 1

        for i in range(1, len(completed_logs)):
            current_date = completed_logs.iloc[i]['date'].date()
            prev_date = completed_logs.iloc[i - 1]['date'].date()

            if (current_date - prev_date).days == 1:
                streak += 1
            else:
                streak = 1

            max_streak_for_habit = max(max_streak_for_habit, streak)

        if max_streak_for_habit > max_streak:
            max_streak = max_streak_for_habit
            max_streak_habit = habit['name']

    return (max_streak_habit, max_streak)


def get_habits_needing_attention(habits_df, logs_df):
    """
    Identify habits that are at risk of breaking streaks (no check-in today for habits with streaks)
    """
    if habits_df.empty or logs_df.empty:
        return []

    habits_at_risk = []
    today = datetime.now().date().strftime('%Y-%m-%d')

    for _, habit in habits_df.iterrows():
        habit_id = habit['id']

        # Check if there's a streak for this habit
        current_streak = get_current_streak(habit_id, logs_df)

        if current_streak >= 2:  # Only consider habits with established streaks
            # Check if there's a log for today
            today_log = logs_df[(logs_df['habit_id'] == habit_id) & (logs_df['date'] == today)]

            if today_log.empty or not today_log.iloc[0]['completed']:
                # This habit has a streak but no completion for today
                habits_at_risk.append(habit['name'])

    return habits_at_risk
