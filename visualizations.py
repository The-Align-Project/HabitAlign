import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


def create_calendar_heatmap(habits_df, logs_df):
    """
    Create a calendar heatmap visualization of habit completion
    """
    if habits_df.empty or logs_df.empty:
        # Create an empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No data available for calendar view",
            xaxis_title="Date",
            yaxis_title="Completion"
        )
        return fig

    # Get date range (last 30 days by default)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    # Create a date range
    date_range = pd.date_range(start=start_date, end=end_date)

    # Create a dataframe with all dates
    all_dates_df = pd.DataFrame({'date': date_range})
    all_dates_df['date_str'] = all_dates_df['date'].dt.strftime('%Y-%m-%d')

    # Convert logs dates to datetime
    logs_df = logs_df.copy()
    logs_df['date'] = pd.to_datetime(logs_df['date'])

    # Group by date and count completed habits
    if 'habit_id' in logs_df.columns and 'completed' in logs_df.columns:
        completion_by_date = logs_df[logs_df['completed'] == True].groupby(
            logs_df['date'].dt.strftime('%Y-%m-%d')
        ).size().reset_index(name='completed_count')

        # Get total habits by date
        total_by_date = logs_df.groupby(
            logs_df['date'].dt.strftime('%Y-%m-%d')
        ).size().reset_index(name='total_count')

        # Merge with date range
        completion_df = all_dates_df.merge(
            completion_by_date,
            left_on='date_str',
            right_on='date',
            how='left'
        )

        completion_df = completion_df.merge(
            total_by_date,
            left_on='date_str',
            right_on='date',
            how='left'
        )

        # Fill NaN values with 0
        completion_df['completed_count'] = completion_df['completed_count'].fillna(0)
        completion_df['total_count'] = completion_df['total_count'].fillna(0)

        # Calculate completion percentage
        completion_df['completion_pct'] = np.where(
            completion_df['total_count'] > 0,
            completion_df['completed_count'] / completion_df['total_count'] * 100,
            0
        )

        # Format dates for display
        completion_df['date_display'] = completion_df['date'].dt.strftime('%b %d')

        # Create the heatmap
        fig = px.bar(
            completion_df,
            x='date_display',
            y='completion_pct',
            color='completion_pct',
            color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
            labels={'completion_pct': 'Completion %', 'date_display': 'Date'},
            title="Habit Completion Calendar"
        )

        # Add hover information
        fig.update_traces(
            hovertemplate='<b>Date:</b> %{x}<br><b>Completion:</b> %{y:.1f}%'
        )

        # Update layout
        fig.update_layout(
            xaxis={'type': 'category'},
            yaxis={'range': [0, 100]},
            height=400
        )
    else:
        # Create an empty figure if the logs don't have required columns
        fig = go.Figure()
        fig.update_layout(
            title="No data available for calendar view",
            xaxis_title="Date",
            yaxis_title="Completion"
        )

    return fig


def create_completion_chart(habits_df, logs_df):
    """
    Create a bar chart showing completion rates for each habit
    """
    if habits_df.empty or logs_df.empty:
        # Create an empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No completion data available",
            xaxis_title="Habit",
            yaxis_title="Completion Rate (%)"
        )
        return fig

    # Calculate completion rate for each habit
    completion_data = []

    for _, habit in habits_df.iterrows():
        habit_id = habit['id']
        habit_name = habit['name']

        # Filter logs for this habit
        habit_logs = logs_df[logs_df['habit_id'] == habit_id]

        if not habit_logs.empty:
            # Calculate completion rate
            completed_count = habit_logs[habit_logs['completed'] == True].shape[0]
            total_count = habit_logs.shape[0]
            completion_rate = (completed_count / total_count) * 100 if total_count > 0 else 0

            completion_data.append({
                'habit': habit_name,
                'completion_rate': completion_rate,
                'completed_count': completed_count,
                'total_count': total_count
            })

    if not completion_data:
        # Create an empty figure if no completion data
        fig = go.Figure()
        fig.update_layout(
            title="No completion data available",
            xaxis_title="Habit",
            yaxis_title="Completion Rate (%)"
        )
        return fig

    # Create DataFrame from completion data
    completion_df = pd.DataFrame(completion_data)

    # Sort by completion rate descending
    completion_df = completion_df.sort_values('completion_rate', ascending=False)

    # Create the bar chart
    fig = px.bar(
        completion_df,
        x='habit',
        y='completion_rate',
        color='completion_rate',
        color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
        labels={'completion_rate': 'Completion Rate (%)', 'habit': 'Habit'},
        title="Habit Completion Rates"
    )

    # Add hover information
    fig.update_traces(
        hovertemplate='<b>Habit:</b> %{x}<br><b>Completion Rate:</b> %{y:.1f}%<br><b>Completed:</b> %{customdata[0]} / %{customdata[1]}',
        customdata=completion_df[['completed_count', 'total_count']].values
    )

    # Update layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        yaxis={'range': [0, 100]}
    )

    return fig


def create_completion_trend(logs_df, start_date, end_date):
    """
    Create a line chart showing habit completion trend over time
    """
    if logs_df.empty:
        # Create an empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No trend data available",
            xaxis_title="Date",
            yaxis_title="Completion Rate (%)"
        )
        return fig

    # Convert dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Create a date range
    date_range = pd.date_range(start=start_date, end=end_date)

    # Create a dataframe with all dates
    all_dates_df = pd.DataFrame({'date': date_range})
    all_dates_df['date_str'] = all_dates_df['date'].dt.strftime('%Y-%m-%d')

    # Convert logs dates to datetime
    logs_df = logs_df.copy()
    logs_df['date'] = pd.to_datetime(logs_df['date'])

    # Group by date and calculate completion rate
    daily_completion = logs_df.groupby(logs_df['date'].dt.strftime('%Y-%m-%d')).agg(
        completed_count=('completed', lambda x: sum(x == True)),
        total_count=('completed', 'count')
    ).reset_index()

    # Calculate completion rate
    daily_completion['completion_rate'] = (daily_completion['completed_count'] / daily_completion['total_count']) * 100

    # Merge with all dates to ensure all dates are included
    trend_df = all_dates_df.merge(
        daily_completion,
        left_on='date_str',
        right_on='date',
        how='left'
    )

    # Fill NaN values
    trend_df['completion_rate'] = trend_df['completion_rate'].fillna(0)

    # Format dates for display
    trend_df['date_display'] = trend_df['date'].dt.strftime('%b %d')

    # Create the line chart
    fig = px.line(
        trend_df,
        x='date_display',
        y='completion_rate',
        markers=True,
        labels={'completion_rate': 'Completion Rate (%)', 'date_display': 'Date'},
        title="Habit Completion Trend"
    )

    # Add hover information
    fig.update_traces(
        hovertemplate='<b>Date:</b> %{x}<br><b>Completion Rate:</b> %{y:.1f}%'
    )

    # Add moving average to show trend
    window_size = min(7, len(trend_df))  # Use 7-day window or smaller if less data
    if window_size > 1:
        trend_df['moving_avg'] = trend_df['completion_rate'].rolling(window=window_size, min_periods=1).mean()

        fig.add_trace(
            go.Scatter(
                x=trend_df['date_display'],
                y=trend_df['moving_avg'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='rgba(0, 128, 255, 0.7)', width=2, dash='dot')
            )
        )

    # Update layout
    fig.update_layout(
        xaxis={'type': 'category'},
        yaxis={'range': [0, 100]},
        height=400
    )

    return fig


def create_streak_chart(habits_df, logs_df):
    """
    Create a bar chart showing current streaks for each habit
    """
    if habits_df.empty or logs_df.empty:
        # Create an empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No streak data available",
            xaxis_title="Habit",
            yaxis_title="Current Streak (Days)"
        )
        return fig

    # Calculate current streak for each habit
    streak_data = []

    for _, habit in habits_df.iterrows():
        habit_id = habit['id']
        habit_name = habit['name']

        # Filter logs for this habit
        habit_logs = logs_df[logs_df['habit_id'] == habit_id]

        if not habit_logs.empty:
            # Calculate current streak
            # This is a simplified calculation; the actual streak logic is in utils.py
            current_streak = 0

            # Convert logs dates to datetime
            habit_logs = habit_logs.copy()
            habit_logs['date'] = pd.to_datetime(habit_logs['date'])

            # Sort by date in descending order
            habit_logs = habit_logs.sort_values('date', ascending=False)

            # Go through logs to calculate streak
            for i, row in habit_logs.iterrows():
                if row['completed']:
                    current_date = row['date'].date()

                    if i == 0:
                        current_streak = 1
                    else:
                        prev_date = habit_logs.iloc[i - 1]['date'].date()
                        day_diff = (prev_date - current_date).days

                        if day_diff == 1 and habit_logs.iloc[i - 1]['completed']:
                            current_streak += 1
                        else:
                            break
                else:
                    break

            streak_data.append({
                'habit': habit_name,
                'current_streak': current_streak
            })

    if not streak_data:
        # Create an empty figure if no streak data
        fig = go.Figure()
        fig.update_layout(
            title="No streak data available",
            xaxis_title="Habit",
            yaxis_title="Current Streak (Days)"
        )
        return fig

    # Create DataFrame from streak data
    streak_df = pd.DataFrame(streak_data)

    # Sort by streak descending
    streak_df = streak_df.sort_values('current_streak', ascending=False)

    # Create the bar chart
    fig = px.bar(
        streak_df,
        x='habit',
        y='current_streak',
        color='current_streak',
        color_continuous_scale=[(0, "lightblue"), (1, "darkblue")],
        labels={'current_streak': 'Current Streak (Days)', 'habit': 'Habit'},
        title="Current Habit Streaks"
    )

    # Add hover information
    fig.update_traces(
        hovertemplate='<b>Habit:</b> %{x}<br><b>Current Streak:</b> %{y} days'
    )

    # Update layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'}
    )

    return fig
