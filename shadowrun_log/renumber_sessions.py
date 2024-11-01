import os
import re

# Directories
log_directory = os.path.expanduser('~/Downloads/shadowrun_log/Casper Logs')
combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")

# Function to renumber sessions in the individual log files
def renumber_sessions():
    # Get all session files sorted by creation time
    session_files = sorted([f for f in os.listdir(log_directory) if f.startswith("Casper Log") and f.endswith(".txt")])
    
    # Initialize session counter
    session_counter = 1
    
    for old_filename in session_files:
        # Determine the new filename
        new_filename = f"Casper Log {session_counter}.txt"
        
        # Rename the file to match the new session number
        os.rename(os.path.join(log_directory, old_filename), os.path.join(log_directory, new_filename))
        
        session_counter += 1

    print("Sessions renumbered successfully.")

# Function to renumber sessions in the combined log file
def renumber_combined_log():
    if os.path.exists(combined_log_file):
        with open(combined_log_file, 'r') as file:
            combined_logs = file.read()
        
        # Split the combined log by session
        sessions = combined_logs.split("\n------------\n")
        
        # Initialize session counter
        session_counter = 1
        updated_sessions = []
        
        for session in sessions:
            # Update the session number in the header
            session = re.sub(r"Session \d+", f"Session {session_counter}", session)
            updated_sessions.append(session)
            session_counter += 1
        
        # Write the updated sessions back to the combined log file
        with open(combined_log_file, 'w') as file:
            file.write("\n------------\n".join(updated_sessions))
        
        print("Combined log renumbered successfully.")

# Run the renumbering functions
renumber_sessions()
renumber_combined_log()
