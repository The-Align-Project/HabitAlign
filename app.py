import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import data_handler as dh
import visualizations as vis
import utils
import base64
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS styles
def local_css():
    style = """
    <style>
        /* Main typography styles */
        .main-header {
            font-size: 2.5rem;
            color: #8BC34A;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .sub-header {
            font-size: 1.8rem;
            margin-top: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #8BC34A;
            color: #333333;
            font-weight: 600;
        }

        /* Card and container styles */
        .card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
            transition: all 0.2s ease;
            border: 1px solid #f0f0f0;
        }

        .card:hover {
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }

        .habit-name {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333333;
        }

        .streak-badge {
            background-color: #E8F5E9;
            color: #388E3C;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 0.8rem;
            display: inline-block;
            font-weight: 600;
            border: 1px solid #C8E6C9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }

        .stat-card {
            background-color: #F9FBE7;
            border-left: 4px solid #8BC34A;
            padding: 1.2rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.04);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        }

        .category-header {
            background-color: #F1F8E9;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            margin-bottom: 1.2rem;
            font-weight: 600;
            color: #33691E;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            border: 1px solid #DCEDC8;
        }

        /* Custom checkbox styling */
        div[role="checkbox"] {
            transform: scale(1.2);
        }

        div[data-baseweb="checkbox"] label {
            font-weight: 500;
        }

        /* Form styling */
        div[data-testid="stForm"] {
            background-color: #FAFAFA;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #EEEEEE;
            box-shadow: 0 3px 10px rgba(0,0,0,0.03);
        }

        div[data-testid="stFormSubmitButton"] > button {
            background-color: #8BC34A;
            color: white;
            font-weight: 600;
            padding: 0.3rem 1.5rem;
            border-radius: 6px;
            box-shadow: 0 2px 5px rgba(139, 195, 74, 0.3);
            transition: all 0.2s ease;
        }

        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #7CB342;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(139, 195, 74, 0.4);
        }

        /* Input styling */
        input, select, .stDateInput {
            border-radius: 6px !important;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 5px 5px 0px 0px;
            padding: 10px 20px;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background-color: #F1F8E9;
            color: #558B2F;
        }

        /* Expander styling */
        details {
            background-color: #FAFAFA;
            border-radius: 8px;
            margin-bottom: 0.8rem;
            border: 1px solid #EEEEEE;
            transition: all 0.2s ease;
        }

        details:hover {
            background-color: #F5F5F5;
            border-color: #E0E0E0;
        }

        details summary {
            padding: 0.8rem 1.2rem;
            font-weight: 600;
            cursor: pointer;
        }

        details[open] {
            padding-bottom: 1rem;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
        }

        /* Button styling */
        .stButton button {
            border-radius: 6px;
            font-weight: 600;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            transition: all 0.2s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* Make alerts more attractive */
        div[data-testid="stAlert"] {
            border-radius: 8px;
            border-left-width: 10px;
            font-weight: 500;
        }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)


# Apply custom CSS
local_css()

# Initialize session state if needed
if 'habits' not in st.session_state:
    # Try to load existing habits or create an empty DataFrame
    try:
        st.session_state.habits = dh.load_habits()
    except:
        st.session_state.habits = pd.DataFrame(columns=['id', 'name', 'category', 'frequency', 'created_at'])
        dh.save_habits(st.session_state.habits)

if 'logs' not in st.session_state:
    # Try to load existing logs or create an empty DataFrame
    try:
        st.session_state.logs = dh.load_logs()
    except:
        st.session_state.logs = pd.DataFrame(columns=['habit_id', 'date', 'completed'])
        dh.save_logs(st.session_state.logs)

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"


# Helper function for sidebar icons
def get_icon_html(icon, size=24, color="#8BC34A"):
    return f'<span style="color:{color}; font-size: {size}px; margin-right: 10px;">{icon}</span>'


# Sidebar for navigation with enhanced UI
with st.sidebar:
    # Logo and title
    st.markdown(
        f'<div style="display: flex; align-items: center; margin-bottom: 20px;">'
        f'<h1 style="margin: 0; color: #8BC34A; display: flex; align-items: center;">'
        f'<span style="margin-right: 10px;">🌟</span> Habit Tracker</h1>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<p style="margin-bottom: 20px; color: #666;">Track, manage, and visualize your daily habits.</p>',
                unsafe_allow_html=True)

    # Navigation with icons
    st.markdown("### Navigation", unsafe_allow_html=True)

    # Create custom radio buttons with icons
    dash_html = get_icon_html("📊") + "Dashboard"
    manage_html = get_icon_html("✏️") + "Manage Habits"
    analytics_html = get_icon_html("📈") + "Analytics"

    options = ["Dashboard", "Manage Habits", "Analytics"]
    icons_html = [dash_html, manage_html, analytics_html]

    # Display custom navigation
    selected_idx = options.index(st.session_state.active_tab) if st.session_state.active_tab in options else 0
    selected_tab = st.radio(
        "Navigation",
        options,
        format_func=lambda x: icons_html[options.index(x)],
        index=selected_idx,
        label_visibility="collapsed"
    )

    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab

    st.markdown('<hr style="margin: 20px 0; border: none; height: 1px; background-color: #eee;">',
                unsafe_allow_html=True)

    # Display basic stats in sidebar with enhanced UI
    if not st.session_state.habits.empty:
        st.markdown('<h3 style="color: #333; margin-bottom: 15px;">Quick Stats</h3>', unsafe_allow_html=True)

        total_habits = len(st.session_state.habits)
        if not st.session_state.logs.empty:
            today = datetime.now().strftime('%Y-%m-%d')
            today_logs = st.session_state.logs[st.session_state.logs['date'] == today]
            completed_today = len(today_logs[today_logs['completed'] == True])

            # Custom metrics with nicer styling
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div style="font-size: 0.9rem; color: #666;">Total Habits</div>'
                    f'<div style="font-size: 1.7rem; font-weight: bold; color: #333;">{total_habits}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col2:
                completion_pct = int((completed_today / total_habits) * 100) if total_habits > 0 else 0
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div style="font-size: 0.9rem; color: #666;">Today\'s Progress</div>'
                    f'<div style="font-size: 1.7rem; font-weight: bold; color: #333;">{completed_today}/{total_habits}</div>'
                    f'<div style="height: 6px; background-color: #EEEEEE; border-radius: 3px; margin-top: 5px;">'
                    f'<div style="width: {completion_pct}%; height: 100%; background-color: #8BC34A; border-radius: 3px;"></div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Calculate and display longest streak
            longest_streak = utils.get_longest_streak(st.session_state.habits, st.session_state.logs)
            if longest_streak[0] != "":
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div style="font-size: 0.9rem; color: #666;">Longest Streak</div>'
                    f'<div style="font-size: 1.2rem; font-weight: bold; color: #333;">{longest_streak[1]} days</div>'
                    f'<div style="font-size: 0.9rem; color: #666;">{longest_streak[0]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

# Main content area
if st.session_state.active_tab == "Dashboard":
    # Display a modern header with today's date
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')

    st.markdown(
        f'<h1 class="main-header">Habit Dashboard</h1>'
        f'<div style="display: flex; justify-content: center; margin-bottom: 20px;">'
        f'<div style="background-color: #F1F8E9; padding: 8px 16px; border-radius: 20px; font-size: 1.1rem;">'
        f'<span style="color: #689F38; margin-right: 8px;">📅</span>'
        f'Today: {today.strftime("%A, %B %d, %Y")}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if st.session_state.habits.empty:
        # Improved empty state
        st.markdown(
            '<div style="text-align: center; padding: 40px 20px; background-color: #F5F5F5; border-radius: 10px; margin: 20px 0;">'
            '<div style="font-size: 60px; margin-bottom: 20px;">📝</div>'
            '<h3 style="margin-bottom: 15px; color: #555;">No habits yet</h3>'
            '<p style="color: #777; margin-bottom: 25px;">Start by creating your first habit in the "Manage Habits" section.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        # Display habits for today
        st.markdown('<h2 class="sub-header">Today\'s Habits</h2>', unsafe_allow_html=True)

        # Get habits
        habits_per_row = 3
        all_habits = st.session_state.habits.to_dict('records')

        # Group habits by category
        habits_by_category = {}
        for habit in all_habits:
            category = habit['category']
            if category not in habits_by_category:
                habits_by_category[category] = []
            habits_by_category[category].append(habit)

        # Habit stats summary
        total_habits = len(all_habits)
        today_logs = st.session_state.logs[st.session_state.logs['date'] == today_str]
        completed_today = len(today_logs[today_logs['completed'] == True])
        completion_pct = int((completed_today / total_habits) * 100) if total_habits > 0 else 0

        # Display progress bar at the top
        st.markdown(
            f'<div style="background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 25px;">'
            f'<div style="display: flex; justify-content: space-between; margin-bottom: 10px;">'
            f'<div style="font-weight: 600; color: #333;">Today\'s Progress</div>'
            f'<div style="color: #333;">{completed_today}/{total_habits} completed ({completion_pct}%)</div>'
            f'</div>'
            f'<div style="height: 8px; background-color: #EEEEEE; border-radius: 4px;">'
            f'<div style="width: {completion_pct}%; height: 100%; background-color: #8BC34A; border-radius: 4px;"></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Display habits by category with improved styling
        for category, habits in habits_by_category.items():
            # Category header
            st.markdown(f'<div class="category-header">{category}</div>', unsafe_allow_html=True)

            # Create rows of habits as cards
            for i in range(0, len(habits), habits_per_row):
                cols = st.columns(habits_per_row)
                for j in range(habits_per_row):
                    if i + j < len(habits):
                        habit = habits[i + j]

                        # Check if habit was completed today
                        completed = False
                        existing_log = st.session_state.logs[
                            (st.session_state.logs['habit_id'] == habit['id']) &
                            (st.session_state.logs['date'] == today_str)
                            ]

                        if not existing_log.empty:
                            completed = existing_log.iloc[0]['completed']

                        with cols[j]:
                            # Get streak information
                            current_streak = utils.get_current_streak(habit['id'], st.session_state.logs)

                            # Create a card for each habit
                            st.markdown(
                                f'<div class="card">'
                                f'<div class="habit-name">{habit["name"]}</div>'
                                f'<div class="streak-badge">🔥 {current_streak} day streak</div>',
                                unsafe_allow_html=True
                            )

                            # Create checkbox for marking habit completion
                            if st.checkbox("Completed", value=completed, key=f"check_{habit['id']}"):
                                # If checkbox is checked and no log exists for today, create one
                                if existing_log.empty:
                                    new_log = pd.DataFrame({
                                        'habit_id': [habit['id']],
                                        'date': [today_str],
                                        'completed': [True]
                                    })
                                    st.session_state.logs = pd.concat([st.session_state.logs, new_log],
                                                                      ignore_index=True)
                                    dh.save_logs(st.session_state.logs)
                                # If checkbox is checked and log exists but is marked incomplete, update it
                                elif not existing_log.iloc[0]['completed']:
                                    st.session_state.logs.loc[
                                        (st.session_state.logs['habit_id'] == habit['id']) &
                                        (st.session_state.logs['date'] == today_str),
                                        'completed'
                                    ] = True
                                    dh.save_logs(st.session_state.logs)
                            else:
                                # If checkbox is unchecked but a completed log exists, update it
                                if not existing_log.empty and existing_log.iloc[0]['completed']:
                                    st.session_state.logs.loc[
                                        (st.session_state.logs['habit_id'] == habit['id']) &
                                        (st.session_state.logs['date'] == today_str),
                                        'completed'
                                    ] = False
                                    dh.save_logs(st.session_state.logs)
                                # If checkbox is unchecked and no log exists, create one marked as incomplete
                                elif existing_log.empty:
                                    new_log = pd.DataFrame({
                                        'habit_id': [habit['id']],
                                        'date': [today_str],
                                        'completed': [False]
                                    })
                                    st.session_state.logs = pd.concat([st.session_state.logs, new_log],
                                                                      ignore_index=True)
                                    dh.save_logs(st.session_state.logs)

                            # Close the card div
                            st.markdown('</div>', unsafe_allow_html=True)

        # Display the calendar heatmap for all habits
        st.markdown('<h2 class="sub-header">Monthly Overview</h2>', unsafe_allow_html=True)
        st.markdown(
            '<p style="margin-bottom: 20px; color: #666;">Track your consistency across all habits</p>',
            unsafe_allow_html=True
        )

        # Create a card for the chart
        st.markdown('<div class="card" style="padding: 20px;">', unsafe_allow_html=True)
        fig = vis.create_calendar_heatmap(st.session_state.habits, st.session_state.logs)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_tab == "Manage Habits":
    # Modern title with icon
    st.markdown(
        '<h1 class="main-header">Manage Your Habits</h1>'
        '<p style="text-align: center; margin-bottom: 30px; color: #666;">Create and organize your habits to build better routines</p>',
        unsafe_allow_html=True
    )

    # Create columns for layout
    col1, col2 = st.columns([1, 1])

    with col1:
        # Form for adding a new habit with improved styling
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #333; margin-bottom: 20px; display: flex; align-items: center;">'
                    '<span style="color: #8BC34A; margin-right: 10px;">➕</span> Add New Habit</h3>',
                    unsafe_allow_html=True)

        with st.form(key="add_habit_form"):
            habit_name = st.text_input("Habit Name", placeholder="E.g., Morning Meditation")

            # Default categories or let the user create their own
            default_categories = ["Health", "Productivity", "Self-care", "Relationships", "Other"]
            category_options = default_categories.copy()

            # Add existing categories if they're not in the default list
            if not st.session_state.habits.empty:
                existing_categories = st.session_state.habits['category'].unique()
                for cat in existing_categories:
                    if cat not in category_options:
                        category_options.append(cat)

            # Let the user select a category or create a new one
            select_category = st.selectbox(
                "Select Category",
                options=category_options + ["Create New Category"],
                index=0
            )

            # If user wants to create a new category, show a text input
            if select_category == "Create New Category":
                new_category = st.text_input("Enter New Category", placeholder="E.g., Learning")
                if new_category:
                    category = new_category
                else:
                    category = "Other"  # Default if they don't enter anything
            else:
                category = select_category

            # Display frequency selector with icons
            st.markdown('<p style="margin-bottom: 5px; font-weight: 500;">Frequency</p>', unsafe_allow_html=True)
            freq_cols = st.columns(4)

            with freq_cols[0]:
                daily = st.checkbox("Daily", value=True, key="daily_freq")
            with freq_cols[1]:
                weekly = st.checkbox("Weekly", value=False, key="weekly_freq")
            with freq_cols[2]:
                monthly = st.checkbox("Monthly", value=False, key="monthly_freq")
            with freq_cols[3]:
                custom = st.checkbox("Custom", value=False, key="custom_freq")

            # Determine the frequency based on checkboxes
            if daily:
                frequency = "Daily"
            elif weekly:
                frequency = "Weekly"
            elif monthly:
                frequency = "Monthly"
            else:
                frequency = "Custom"

            # Submit button for the form
            submit_button = st.form_submit_button(label="Add Habit")

            if submit_button:
                if habit_name:
                    # Create new habit
                    new_habit_id = utils.generate_id()
                    new_habit = pd.DataFrame({
                        'id': [new_habit_id],
                        'name': [habit_name],
                        'category': [category],
                        'frequency': [frequency],
                        'created_at': [datetime.now().strftime('%Y-%m-%d')]
                    })

                    # Add to session state and save
                    st.session_state.habits = pd.concat([st.session_state.habits, new_habit], ignore_index=True)
                    dh.save_habits(st.session_state.habits)
                    st.success(f"Added new habit: {habit_name}")
                    st.rerun()
                else:
                    st.error("Please enter a habit name.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Display tips for creating effective habits
        st.markdown(
            '<div class="card" style="background-color: #F9FBE7;">'
            '<h3 style="color: #33691E; margin-bottom: 15px; display: flex; align-items: center;">'
            '<span style="margin-right: 10px;">💡</span> Tips for Effective Habits</h3>'
            '<ul style="color: #555; padding-left: 20px;">'
            '<li><strong>Start Small</strong> - Focus on habits you can do in less than 2 minutes initially</li>'
            '<li><strong>Be Specific</strong> - Define exactly what you\'ll do and when</li>'
            '<li><strong>Stack Habits</strong> - Link new habits to existing behaviors</li>'
            '<li><strong>Track Consistently</strong> - Check in daily to maintain your streaks</li>'
            '<li><strong>Be Patient</strong> - It takes about 66 days to form a habit fully</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )

    # Display existing habits for management
    if not st.session_state.habits.empty:
        st.subheader("Manage Existing Habits")

        # Add filters
        filter_container = st.container()
        with filter_container:
            col1, col2 = st.columns(2)
            with col1:
                filter_category = st.multiselect(
                    "Filter by Category",
                    options=["All"] + list(st.session_state.habits['category'].unique()),
                    default="All"
                )

            # Apply filters
            filtered_habits = st.session_state.habits.copy()
            if filter_category and "All" not in filter_category:
                filtered_habits = filtered_habits[filtered_habits['category'].isin(filter_category)]

        # Display habits in a more modern UI
        for _, habit in filtered_habits.iterrows():
            with st.expander(f"{habit['name']} ({habit['category']})", expanded=False):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Name:** {habit['name']}")
                    st.write(f"**Category:** {habit['category']}")
                    st.write(f"**Frequency:** {habit['frequency']}")
                    st.write(f"**Created:** {habit['created_at']}")

                    # Display streak information
                    current_streak = utils.get_current_streak(habit['id'], st.session_state.logs)
                    st.write(f"**Current Streak:** {current_streak} days")

                with col2:
                    # Edit button
                    if st.button("Edit", key=f"edit_{habit['id']}"):
                        st.session_state.edit_habit_id = habit['id']
                        st.rerun()

                    # Delete button with confirmation
                    if st.button("Delete", key=f"delete_{habit['id']}"):
                        st.session_state.delete_habit_id = habit['id']
                        st.rerun()

                # Display a mini log history
                logs_for_habit = st.session_state.logs[st.session_state.logs['habit_id'] == habit['id']]
                if not logs_for_habit.empty:
                    # Get the last 7 days of logs
                    last_7_days = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
                    recent_logs = logs_for_habit[logs_for_habit['date'].isin(last_7_days)]

                    st.write("**Recent Activity:**")
                    log_cols = st.columns(7)

                    for i, date in enumerate(last_7_days):
                        log_entry = recent_logs[recent_logs['date'] == date]
                        display_date = datetime.strptime(date, '%Y-%m-%d').strftime('%a, %b %d')

                        with log_cols[i]:
                            st.write(display_date)
                            if not log_entry.empty and log_entry.iloc[0]['completed']:
                                st.write("✅")
                            else:
                                st.write("❌")

    # Handle edit habit (if edit button was clicked)
    if 'edit_habit_id' in st.session_state:
        habit_to_edit = st.session_state.habits[st.session_state.habits['id'] == st.session_state.edit_habit_id].iloc[0]

        st.subheader(f"Edit Habit: {habit_to_edit['name']}")

        with st.form(key="edit_habit_form"):
            new_name = st.text_input("Habit Name", value=habit_to_edit['name'])

            # Category selection similar to the add form
            default_categories = ["Health", "Productivity", "Self-care", "Relationships", "Other"]
            category_options = default_categories.copy()

            # Add existing categories
            existing_categories = st.session_state.habits['category'].unique()
            for cat in existing_categories:
                if cat not in category_options:
                    category_options.append(cat)

            # Find the index of the current category
            try:
                current_category_index = category_options.index(habit_to_edit['category'])
            except ValueError:
                current_category_index = 0

            select_category = st.selectbox(
                "Select Category",
                options=category_options + ["Create New Category"],
                index=current_category_index
            )

            if select_category == "Create New Category":
                new_category = st.text_input("Enter New Category")
                if new_category:
                    category = new_category
                else:
                    category = habit_to_edit['category']  # Keep original if they don't enter anything
            else:
                category = select_category

            # Find the index of the current frequency
            frequency_options = ["Daily", "Weekly", "Monthly", "Custom"]
            try:
                current_frequency_index = frequency_options.index(habit_to_edit['frequency'])
            except ValueError:
                current_frequency_index = 0

            frequency = st.selectbox(
                "Frequency",
                options=frequency_options,
                index=current_frequency_index
            )

            update_button = st.form_submit_button(label="Update Habit")
            cancel_button = st.form_submit_button(label="Cancel")

            if update_button:
                if new_name:
                    # Update the habit
                    st.session_state.habits.loc[
                        st.session_state.habits['id'] == st.session_state.edit_habit_id,
                        ['name', 'category', 'frequency']
                    ] = [new_name, category, frequency]

                    dh.save_habits(st.session_state.habits)
                    st.success(f"Updated habit: {new_name}")

                    # Clear the edit state and refresh
                    del st.session_state.edit_habit_id
                    st.rerun()
                else:
                    st.error("Please enter a habit name.")

            if cancel_button:
                # Clear the edit state and refresh
                del st.session_state.edit_habit_id
                st.rerun()

    # Handle delete habit (if delete button was clicked)
    if 'delete_habit_id' in st.session_state:
        habit_to_delete = \
        st.session_state.habits[st.session_state.habits['id'] == st.session_state.delete_habit_id].iloc[0]

        st.subheader(f"Delete Habit: {habit_to_delete['name']}")
        st.warning("Are you sure you want to delete this habit? This will also delete all log entries for this habit.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete"):
                # Remove the habit
                st.session_state.habits = st.session_state.habits[
                    st.session_state.habits['id'] != st.session_state.delete_habit_id]

                # Remove related log entries
                st.session_state.logs = st.session_state.logs[
                    st.session_state.logs['habit_id'] != st.session_state.delete_habit_id]

                # Save both dataframes
                dh.save_habits(st.session_state.habits)
                dh.save_logs(st.session_state.logs)

                # Clear the delete state and refresh
                del st.session_state.delete_habit_id
                st.success(f"Deleted habit: {habit_to_delete['name']}")
                st.rerun()

        with col2:
            if st.button("Cancel"):
                # Clear the delete state and refresh
                del st.session_state.delete_habit_id
                st.rerun()

elif st.session_state.active_tab == "Analytics":
    # Modern analytics title
    st.markdown(
        '<h1 class="main-header">Habit Analytics</h1>'
        '<p style="text-align: center; margin-bottom: 30px; color: #666;">Visualize your progress and identify patterns</p>',
        unsafe_allow_html=True
    )

    if st.session_state.habits.empty or st.session_state.logs.empty:
        # Enhanced empty state for analytics
        st.markdown(
            '<div style="text-align: center; padding: 40px 20px; background-color: #F5F5F5; border-radius: 10px; margin: 20px 0;">'
            '<div style="font-size: 60px; margin-bottom: 20px;">📊</div>'
            '<h3 style="margin-bottom: 15px; color: #555;">No data yet</h3>'
            '<p style="color: #777; margin-bottom: 25px;">Create habits and log your progress to see analytics.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        # Enhanced date selector with modern styling
        st.markdown('<div class="card" style="padding: 20px; margin-bottom: 25px;">', unsafe_allow_html=True)
        st.markdown(
            '<h3 style="color: #333; margin-bottom: 15px; display: flex; align-items: center;">'
            '<span style="color: #8BC34A; margin-right: 10px;">📅</span> Select Date Range</h3>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30),
                max_value=datetime.now()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now(),
                min_value=start_date
            )

        # Display selected date range summary
        date_range_days = (end_date - start_date).days + 1
        st.markdown(
            f'<p style="text-align: center; margin-top: 10px; color: #666;">'
            f'Analyzing data for <strong>{date_range_days} days</strong> from '
            f'<strong>{start_date.strftime("%b %d, %Y")}</strong> to <strong>{end_date.strftime("%b %d, %Y")}</strong>'
            f'</p>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Convert to string format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Filter logs by date range
        filtered_logs = st.session_state.logs[
            (st.session_state.logs['date'] >= start_date_str) &
            (st.session_state.logs['date'] <= end_date_str)
            ]

        if filtered_logs.empty:
            st.markdown(
                '<div style="text-align: center; padding: 30px 20px; background-color: #F5F5F5; border-radius: 10px; margin: 20px 0;">'
                '<div style="font-size: 40px; margin-bottom: 15px;">🔍</div>'
                '<h3 style="margin-bottom: 10px; color: #555;">No data for this period</h3>'
                '<p style="color: #777;">Try selecting a different date range.</p>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            # Create enhanced tabs for different visualizations
            tab_style = """
            <style>
                .stTabs [data-baseweb="tab-list"] {
                    gap: 10px;
                }
                .stTabs [data-baseweb="tab"] {
                    border-radius: 5px 5px 0px 0px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                .stTabs [aria-selected="true"] {
                    background-color: #F1F8E9;
                    color: #558B2F;
                }
            </style>
            """
            st.markdown(tab_style, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📊 Completion Rates", "🔥 Streaks", "📆 Calendar View"])

            with tab1:
                st.markdown('<h2 class="sub-header">Habit Completion Rates</h2>', unsafe_allow_html=True)
                st.markdown(
                    '<p style="color: #666; margin-bottom: 20px;">Compare how consistently you complete each habit</p>',
                    unsafe_allow_html=True)

                # Card for first chart
                st.markdown('<div class="card" style="padding: 20px; margin-bottom: 25px;">', unsafe_allow_html=True)
                completion_fig = vis.create_completion_chart(st.session_state.habits, filtered_logs)
                st.plotly_chart(completion_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Card for second chart
                st.markdown('<div class="card" style="padding: 20px;">', unsafe_allow_html=True)
                st.markdown('<h3 style="color: #333; margin-bottom: 15px;">Trend Over Time</h3>',
                            unsafe_allow_html=True)
                trend_fig = vis.create_completion_trend(filtered_logs, start_date_str, end_date_str)
                st.plotly_chart(trend_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<h2 class="sub-header">Streak Analysis</h2>', unsafe_allow_html=True)
                st.markdown('<p style="color: #666; margin-bottom: 20px;">Track your consistent habit performance</p>',
                            unsafe_allow_html=True)

                # Calculate total habit data
                total_habits = len(st.session_state.habits)
                active_streaks = sum(1 for _, habit in st.session_state.habits.iterrows()
                                     if utils.get_current_streak(habit['id'], st.session_state.logs) > 0)

                # Show summary cards
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(
                        f'<div class="card" style="padding: 15px; text-align: center;">'
                        f'<div style="font-size: 0.9rem; color: #666;">Total Habits</div>'
                        f'<div style="font-size: 1.7rem; font-weight: bold; color: #333;">{total_habits}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        f'<div class="card" style="padding: 15px; text-align: center;">'
                        f'<div style="font-size: 0.9rem; color: #666;">Active Streaks</div>'
                        f'<div style="font-size: 1.7rem; font-weight: bold; color: #333;">{active_streaks}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with col3:
                    longest_streak = utils.get_longest_streak(st.session_state.habits, st.session_state.logs)
                    st.markdown(
                        f'<div class="card" style="padding: 15px; text-align: center;">'
                        f'<div style="font-size: 0.9rem; color: #666;">Longest Streak</div>'
                        f'<div style="font-size: 1.7rem; font-weight: bold; color: #333;">{longest_streak[1]} days</div>'
                        f'<div style="font-size: 0.8rem; color: #777;">{longest_streak[0]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                # Card for streak chart
                st.markdown('<div class="card" style="padding: 20px; margin-top: 20px;">', unsafe_allow_html=True)
                streak_fig = vis.create_streak_chart(st.session_state.habits, st.session_state.logs)
                st.plotly_chart(streak_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Generate streak suggestions with better styling
                st.markdown(
                    '<h3 style="color: #333; margin: 25px 0 15px 0; display: flex; align-items: center;">'
                    '<span style="color: #8BC34A; margin-right: 10px;">💡</span> Streak Insights</h3>',
                    unsafe_allow_html=True
                )

                habits_need_attention = utils.get_habits_needing_attention(st.session_state.habits,
                                                                           st.session_state.logs)

                if habits_need_attention:
                    for habit_name in habits_need_attention:
                        st.markdown(
                            f'<div class="card" style="padding: 15px; background-color: #FFF3E0; margin-bottom: 10px;">'
                            f'<p style="margin: 0; color: #E65100;"><strong>Action needed:</strong> Your habit \'{habit_name}\' '
                            f'is at risk of breaking its streak. Make sure to complete it today!</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f'<div class="card" style="padding: 15px; background-color: #E8F5E9; margin-bottom: 10px;">'
                        f'<p style="margin: 0; color: #2E7D32;"><strong>Great job!</strong> All your habits are on track. '
                        f'Keep up the good work!</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            with tab3:
                st.markdown('<h2 class="sub-header">Calendar View</h2>', unsafe_allow_html=True)
                st.markdown(
                    '<p style="color: #666; margin-bottom: 20px;">See your habit completion patterns over time</p>',
                    unsafe_allow_html=True)

                # Card for calendar selector
                st.markdown('<div class="card" style="padding: 20px; margin-bottom: 20px;">', unsafe_allow_html=True)

                # Let user select which habit to view with improved UI
                st.markdown('<p style="font-weight: 500; margin-bottom: 10px;">Select a habit to view:</p>',
                            unsafe_allow_html=True)

                habit_options = st.session_state.habits['name'].tolist()
                habit_options.insert(0, "All Habits")

                # Create a row of buttons for habit selection
                cols = st.columns(min(5, len(habit_options)))

                if 'selected_calendar_habit' not in st.session_state:
                    st.session_state.selected_calendar_habit = "All Habits"

                for i, habit in enumerate(habit_options):
                    with cols[i % 5]:
                        is_selected = st.session_state.selected_calendar_habit == habit
                        button_style = "primary" if is_selected else "secondary"
                        if st.button(habit, key=f"habit_btn_{habit}", type=button_style):
                            st.session_state.selected_calendar_habit = habit
                            st.rerun()

                selected_habit = st.session_state.selected_calendar_habit
                st.markdown(
                    f'<p style="text-align: center; margin-top: 10px; color: #666;">Viewing: <strong>{selected_habit}</strong></p>',
                    unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Card for calendar visualization
                st.markdown('<div class="card" style="padding: 20px;">', unsafe_allow_html=True)

                if selected_habit == "All Habits":
                    # Show heatmap for all habits
                    calendar_fig = vis.create_calendar_heatmap(st.session_state.habits, filtered_logs)
                else:
                    # Get the habit ID
                    habit_id = st.session_state.habits[st.session_state.habits['name'] == selected_habit]['id'].iloc[0]

                    # Show heatmap for selected habit
                    calendar_fig = vis.create_calendar_heatmap(
                        st.session_state.habits[st.session_state.habits['id'] == habit_id],
                        filtered_logs[filtered_logs['habit_id'] == habit_id]
                    )

                st.plotly_chart(calendar_fig, use_container_width=True)

                # Add calendar tips
                st.markdown(
                    '<div style="background-color: #F9FBE7; padding: 15px; border-radius: 8px; margin-top: 20px;">'
                    '<h4 style="color: #33691E; margin-bottom: 10px;">Calendar Tips</h4>'
                    '<ul style="color: #555; margin-bottom: 0;">'
                    '<li>Darker colors indicate higher completion rates</li>'
                    '<li>Hover over dates to see detailed statistics</li>'
                    '<li>Look for patterns in your consistency</li>'
                    '</ul>'
                    '</div>',
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
