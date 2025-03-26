import pandas as pd
import json
import os
from datetime import datetime

# Define file paths for data storage
HABITS_FILE = 'habits.json'
LOGS_FILE = 'logs.json'


def save_habits(habits_df):
    """
    Save habits DataFrame to JSON file
    """
    # Convert DataFrame to JSON
    habits_json = habits_df.to_json(orient='records')

    # Write to file
    with open(HABITS_FILE, 'w') as f:
        f.write(habits_json)


def load_habits():
    """
    Load habits from JSON file
    Returns a DataFrame of habits
    """
    if not os.path.exists(HABITS_FILE):
        # Return empty DataFrame if file doesn't exist
        return pd.DataFrame(columns=['id', 'name', 'category', 'frequency', 'created_at'])

    try:
        with open(HABITS_FILE, 'r') as f:
            habits_json = f.read()

        # Convert JSON to DataFrame
        habits_df = pd.read_json(habits_json, orient='records')

        # Ensure all required columns exist
        required_columns = ['id', 'name', 'category', 'frequency', 'created_at']
        for col in required_columns:
            if col not in habits_df.columns:
                if col == 'created_at':
                    habits_df[col] = datetime.now().strftime('%Y-%m-%d')
                else:
                    habits_df[col] = ""

        return habits_df
    except Exception as e:
        # Return empty DataFrame if there's an error
        print(f"Error loading habits: {e}")
        return pd.DataFrame(columns=['id', 'name', 'category', 'frequency', 'created_at'])


def save_logs(logs_df):
    """
    Save logs DataFrame to JSON file
    """
    # Convert DataFrame to JSON
    logs_json = logs_df.to_json(orient='records')

    # Write to file
    with open(LOGS_FILE, 'w') as f:
        f.write(logs_json)


def load_logs():
    """
    Load logs from JSON file
    Returns a DataFrame of logs
    """
    if not os.path.exists(LOGS_FILE):
        # Return empty DataFrame if file doesn't exist
        return pd.DataFrame(columns=['habit_id', 'date', 'completed'])

    try:
        with open(LOGS_FILE, 'r') as f:
            logs_json = f.read()

        # Convert JSON to DataFrame
        logs_df = pd.read_json(logs_json, orient='records')

        # Ensure all required columns exist
        required_columns = ['habit_id', 'date', 'completed']
        for col in required_columns:
            if col not in logs_df.columns:
                if col == 'completed':
                    logs_df[col] = False
                else:
                    logs_df[col] = ""

        return logs_df
    except Exception as e:
        # Return empty DataFrame if there's an error
        print(f"Error loading logs: {e}")
        return pd.DataFrame(columns=['habit_id', 'date', 'completed'])


def export_data():
    """
    Export all data to a single JSON file for backup
    """
    try:
        habits_df = load_habits()
        logs_df = load_logs()

        export_data = {
            'habits': habits_df.to_dict('records'),
            'logs': logs_df.to_dict('records'),
            'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        export_file = f'habit_tracker_export_{datetime.now().strftime("%Y%m%d")}.json'

        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        return export_file
    except Exception as e:
        print(f"Error exporting data: {e}")
        return None


def import_data(file_path):
    """
    Import data from a backup file
    """
    try:
        with open(file_path, 'r') as f:
            import_data = json.load(f)

        # Convert to DataFrames
        habits_df = pd.DataFrame(import_data['habits'])
        logs_df = pd.DataFrame(import_data['logs'])

        # Save imported data
        save_habits(habits_df)
        save_logs(logs_df)

        return True
    except Exception as e:
        print(f"Error importing data: {e}")
        return False
