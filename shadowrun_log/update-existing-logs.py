import os
from datetime import datetime

log_directory = os.path.expanduser('~/Downloads/shadowrun_log/Casper Logs')
combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")

def convert_to_12_hour_format(log):
    try:
        parts = log.split(' ', 2)
        date = parts[0].strip('[')
        time = parts[1].strip(']')
        print(f"Parsing date: {date}, time: {time}")
        
        # Check if the time is already in 12-hour format
        if "AM" in time or "PM" in time:
            dt = datetime.strptime(f"{date} {time}", '%Y-%m-%d %I:%M:%S %p')
        else:
            dt = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M:%S')

        converted = f"[{dt.strftime('%Y-%m-%d %I:%M %p')}] {parts[2]}"
        print(f"Converted '{log}' to '{converted}'")
        return converted
    except Exception as e:
        print(f"Error converting log: {log}")
        print(e)
        return log

def convert_session_to_12_hour_format(session):
    try:
        lines = session.split('\n')
        header = lines[0]
        parts = header.split(' - ')
        print(f"Parsing session header: {parts}")
        
        # Check if the time is already in 12-hour format
        if "AM" in parts[1] or "PM" in parts[1]:
            dt = datetime.strptime(parts[1], '%Y-%m-%d %I:%M:%S %p')
        else:
            dt = datetime.strptime(parts[1], '%Y-%m-%d %H:%M:%S')

        converted_header = f"{parts[0]} - {dt.strftime('%Y-%m-%d %I:%M %p')}"
        converted_lines = [convert_to_12_hour_format(line) for line in lines[1:] if line]
        converted = f"{converted_header}\n" + "\n".join(converted_lines)
        print(f"Converted session '{session}' to '{converted}'")
        return converted
    except Exception as e:
        print(f"Error converting session: {session}")
        print(e)
        return session

if os.path.exists(combined_log_file):
    with open(combined_log_file, 'r') as file:
        logs = file.read().split("\n------------\n")
    
    converted_logs = []
    for log in logs:
        print(f"Original log: {log}")
        if log.startswith("Session"):
            converted_logs.append(convert_session_to_12_hour_format(log))
        else:
            converted_logs.append("\n".join([convert_to_12_hour_format(line) for line in log.split('\n') if line]))
        print(f"Converted log: {converted_logs[-1]}")
    
    with open(combined_log_file, 'w') as file:
        file.write("\n------------\n".join(converted_logs))

print("Logs updated to 12-hour format without seconds.")