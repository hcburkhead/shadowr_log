import os
from datetime import datetime, timedelta

# Path to your Combined Casper Log.txt file
log_directory = os.path.expanduser('~/Downloads/shadowrun_log/Casper Logs')
combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")

# Base fake timestamp and increment
base_fake_timestamp = datetime(2089, 3, 13, 23, 59)  # 2089-03-13 11:59 PM
fake_timestamp_increment = timedelta(minutes=1)  # Increment by 1 minute per log

# Backup the original combined log file
backup_file = os.path.join(log_directory, "Combined Casper Log_backup.txt")
if not os.path.exists(backup_file):
    os.rename(combined_log_file, backup_file)
    print(f"Backup created at {backup_file}")
else:
    print("Backup already exists. Proceeding with the existing backup.")

# Read the combined logs from the backup file
if not os.path.exists(backup_file):
    print(f"Backup file {backup_file} not found.")
    exit(1)

with open(backup_file, 'r') as f:
    lines = f.readlines()

updated_lines = []
current_fake_timestamp = base_fake_timestamp

session_counter = 0

for index, line in enumerate(lines):
    stripped_line = line.strip()
    if stripped_line.startswith('Session'):
        # Session header
        session_counter += 1  # Increment session counter
        # Extract the original session number (if needed)
        # session_number = stripped_line.split(' ')[1]
        # Update the session timestamp to the current fake timestamp
        session_header = f"Session {session_counter} - {current_fake_timestamp.strftime('%Y-%m-%d %I:%M %p')}\n"
        updated_lines.append(session_header)
        print(f"Updated session header at line {index}: {session_header.strip()}")
    elif stripped_line == '------------':
        # Separator line
        updated_lines.append(line)
    elif stripped_line == '':
        # Empty line
        updated_lines.append(line)
    else:
        # Log entry
        # Extract the original message without the timestamp
        if ']' in line:
            # Line format: [timestamp] message
            original_message = line.split(']', 1)[1].strip()
        else:
            # Line does not contain a timestamp
            original_message = line.strip()
        # Create new line with fake timestamp
        new_line = f"[{current_fake_timestamp.strftime('%Y-%m-%d %I:%M %p')}] {original_message}\n"
        updated_lines.append(new_line)
        print(f"Updated log entry at line {index}: {new_line.strip()}")
        # Increment the fake timestamp
        current_fake_timestamp += fake_timestamp_increment

# Write the updated lines back to the combined log file
with open(combined_log_file, 'w') as f:
    f.writelines(updated_lines)

print("Timestamps in Combined Casper Log.txt have been updated.")
