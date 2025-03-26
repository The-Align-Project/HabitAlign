import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import data_handler as dh
import visualizations as vis
import utils

# Page configuration
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Sidebar for navigation
with st.sidebar:
    st.title("Habit Tracker")
    selected_tab = st.radio("Navigation", ["Dashboard", "Manage Habits", "Analytics"])

    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab

    st.divider()

    # Display basic stats in sidebar
    if not st.session_state.habits.empty:
        st.subheader("Quick Stats")
        total_habits = len(st.session_state.habits)
        if not st.session_state.logs.empty:
            today = datetime.now().strftime('%Y-%m-%d')
            today_logs = st.session_state.logs[st.session_state.logs['date'] == today]
            completed_today = len(today_logs[today_logs['completed'] == True])
            st.metric("Total Habits", total_habits)
            st.metric("Completed Today", f"{completed_today}/{total_habits}")

            # Calculate and display longest streak
            longest_streak = utils.get_longest_streak(st.session_state.habits, st.session_state.logs)
            if longest_streak[0] != "":
                st.metric("Longest Streak", f"{longest_streak[1]} days ({longest_streak[0]})")

# Main content area
if st.session_state.active_tab == "Dashboard":
    st.title("Habit Dashboard")

    # Show today's date
    today = datetime.now()
    st.subheader(f"Today: {today.strftime('%A, %B %d, %Y')}")

    if st.session_state.habits.empty:
        st.info("You don't have any habits set up yet. Go to 'Manage Habits' to create your first habit!")
    else:
        # Today's habits section
        st.subheader("Today's Habits")

        # Get today's date as string
        today_str = today.strftime('%Y-%m-%d')

        # Create columns for better organization
        habits_per_row = 3
        all_habits = st.session_state.habits.to_dict('records')

        # Group habits by category
        habits_by_category = {}
        for habit in all_habits:
            category = habit['category']
            if category not in habits_by_category:
                habits_by_category[category] = []
            habits_by_category[category].append(habit)

        # Display habits by category
        for category, habits in habits_by_category.items():
            st.write(f"### {category}")

            # Create rows of habits
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
                            st.write(f"**{habit['name']}**")

                            # Get streak information
                            current_streak = utils.get_current_streak(habit['id'], st.session_state.logs)

                            # Display streak info
                            st.write(f"Current streak: {current_streak} days")

                            # Create the checkbox for marking habit completion
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

        # Display the calendar heatmap for all habits
        st.subheader("Monthly Overview")
        st.write("Track your consistency across all habits")
        fig = vis.create_calendar_heatmap(st.session_state.habits, st.session_state.logs)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.active_tab == "Manage Habits":
    st.title("Manage Your Habits")

    # Form for adding a new habit
    with st.form(key="add_habit_form"):
        st.subheader("Add New Habit")
        habit_name = st.text_input("Habit Name")

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
            new_category = st.text_input("Enter New Category")
            if new_category:
                category = new_category
            else:
                category = "Other"  # Default if they don't enter anything
        else:
            category = select_category

        frequency = st.selectbox(
            "Frequency",
            options=["Daily", "Weekly", "Monthly", "Custom"],
            index=0
        )

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
    st.title("Habit Analytics")

    if st.session_state.habits.empty or st.session_state.logs.empty:
        st.info("You need to create habits and log some data before analytics can be displayed.")
    else:
        # Add date range selector
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

        # Convert to string format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Filter logs by date range
        filtered_logs = st.session_state.logs[
            (st.session_state.logs['date'] >= start_date_str) &
            (st.session_state.logs['date'] <= end_date_str)
            ]

        if filtered_logs.empty:
            st.info("No data available for the selected date range.")
        else:
            # Create tabs for different visualizations
            tab1, tab2, tab3 = st.tabs(["Completion Rates", "Streaks", "Calendar View"])

            with tab1:
                st.subheader("Habit Completion Rates")

                # Calculate completion rates for each habit
                completion_fig = vis.create_completion_chart(st.session_state.habits, filtered_logs)
                st.plotly_chart(completion_fig, use_container_width=True)

                # Add overall completion trend over time
                trend_fig = vis.create_completion_trend(filtered_logs, start_date_str, end_date_str)
                st.plotly_chart(trend_fig, use_container_width=True)

            with tab2:
                st.subheader("Streak Analysis")

                # Show current and longest streaks for each habit
                streak_fig = vis.create_streak_chart(st.session_state.habits, st.session_state.logs)
                st.plotly_chart(streak_fig, use_container_width=True)

                # Generate streak suggestions
                st.subheader("Streak Insights")
                habits_need_attention = utils.get_habits_needing_attention(st.session_state.habits,
                                                                           st.session_state.logs)

                if habits_need_attention:
                    for habit_name in habits_need_attention:
                        st.info(
                            f"💡 Your habit '{habit_name}' needs attention - you're at risk of breaking your streak.")
                else:
                    st.success("Great job! All your habits are on track.")

            with tab3:
                st.subheader("Calendar Heatmap")

                # Let user select which habit to view
                habit_options = st.session_state.habits['name'].tolist()
                habit_options.insert(0, "All Habits")

                selected_habit = st.selectbox("Select Habit", options=habit_options)

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
