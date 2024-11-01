from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import uuid
from datetime import datetime, timedelta
import re
import signal

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') 

# Credentials
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# Log directory
log_directory = os.path.expanduser('~/Downloads/shadowrun_log/Casper Logs')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logs = []

# Fake timestamp increment
fake_timestamp_increment = timedelta(minutes=1)  # Increment by 1 minute per log

def get_last_fake_timestamp():
    combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")
    if not os.path.exists(combined_log_file):
        # If the combined log does not exist, start from the base timestamp
        return datetime(2089, 3, 13, 23, 59)
    else:
        # Read the combined log file and find the last timestamp
        with open(combined_log_file, 'r') as f:
            lines = f.readlines()
        for line in reversed(lines):
            stripped_line = line.strip()
            if stripped_line.startswith('[') and ']' in stripped_line:
                timestamp_str = stripped_line.split(']')[0][1:]  # Remove '[' and ']'
                try:
                    last_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %I:%M %p')
                    return last_timestamp + fake_timestamp_increment
                except ValueError:
                    continue
        # If no valid timestamp found, start from the base timestamp
        return datetime(2089, 3, 13, 23, 59)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        unix_mode = request.form.get('unix_mode') == 'on'

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['unix_mode'] = unix_mode
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')

@app.route('/')
def index():
    if 'logged_in' in session:
        unix_mode = session.get('unix_mode', False)
        return render_template('index.html', unix_mode=unix_mode)
    else:
        return redirect(url_for('login'))

@app.route('/log', methods=['POST'])
def add_log():
    if 'logged_in' in session:
        log_message = request.form['log_message']

        # Use the fake timestamp
        if logs:
            last_timestamp_str = logs[-1]['timestamp']
            last_timestamp = datetime.strptime(last_timestamp_str, '%Y-%m-%d %I:%M %p')
            current_time = last_timestamp + fake_timestamp_increment
        else:
            # Get the last fake timestamp from the combined log
            current_time = get_last_fake_timestamp()

        formatted_timestamp = current_time.strftime('%Y-%m-%d %I:%M %p')
        log_id = str(uuid.uuid4())
        logs.append({'id': log_id, 'timestamp': formatted_timestamp, 'message': log_message})
        return jsonify({'entry': f"[{formatted_timestamp}] {log_message}"})
    else:
        return redirect(url_for('login'))

@app.route('/logs', methods=['GET'])
def get_logs():
    if 'logged_in' in session:
        return jsonify({'logs': logs})
    else:
        return redirect(url_for('login'))

@app.route('/edit_log', methods=['POST'])
def edit_log():
    if 'logged_in' in session:
        log_id = request.form.get('log_id')
        new_message = request.form.get('new_message', '').strip()

        if not log_id or not new_message:
            return jsonify({'success': False, 'error': 'Missing log_id or new_message.'}), 400

        # Edit log in current session
        for log in logs:
            if log['id'] == log_id:
                log['message'] = new_message
                return jsonify({'success': True})

        # Edit log in combined log file
        combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")
        if not os.path.exists(combined_log_file):
            return jsonify({'success': False, 'error': 'Log file does not exist'})

        # Read the combined logs into a list of lines
        with open(combined_log_file, 'r') as f:
            logs_list = f.readlines()

        # Update the specific log entry
        updated = False
        with open(combined_log_file, 'w') as f:
            for line in logs_list:
                if f"UUID: {log_id}" in line:
                    # Update the log message
                    line_parts = line.strip().split('UUID:')
                    if len(line_parts) == 2:
                        timestamp_part = line_parts[0]
                        new_line = f"{timestamp_part}UUID: {log_id} - {new_message}\n"
                        f.write(new_line)
                        updated = True
                    else:
                        f.write(line)
                else:
                    f.write(line)

        if updated:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Log entry not found.'}), 404
    else:
        return redirect(url_for('login'))

@app.route('/end_session', methods=['POST'])
def end_session():
    if 'logged_in' in session:
        if not logs:
            # If no logs have been added, do not create a new session
            return jsonify(success=True)

        session_count = 1
        while os.path.exists(os.path.join(log_directory, f"Casper Log {session_count}.txt")):
            session_count += 1

        # Save session logs to a new file
        with open(os.path.join(log_directory, f"Casper Log {session_count}.txt"), 'w') as file:
            for log in logs:
                file.write(f"[{log['timestamp']}] UUID: {log['id']} - {log['message']}\n")

        # Append session logs to a combined log file
        combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")
        with open(combined_log_file, 'a') as combined_file:
            # Use the last fake timestamp for the session header
            if logs:
                session_time = logs[-1]['timestamp']
            else:
                session_time = get_last_fake_timestamp().strftime('%Y-%m-%d %I:%M %p')

            combined_file.write(f"Session {session_count} - {session_time}\n")
            for log in logs:
                combined_file.write(f"[{log['timestamp']}] UUID: {log['id']} - {log['message']}\n")
            combined_file.write("------------\n")

        logs.clear()

        return jsonify(success=True)
    else:
        return redirect(url_for('login'))

@app.route('/combined_log', methods=['GET'])
def combined_log():
    if 'logged_in' in session:
        combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")
        sessions = []
        current_session = None

        try:
            with open(combined_log_file, 'r') as file:
                logs_list = file.readlines()

            for idx, line in enumerate(logs_list):
                line = line.strip()
                if line.startswith('Session') and '-' in line:
                    if current_session:
                        sessions.append(current_session)
                    session_title, session_time = line.split(' - ', 1)
                    current_session = {
                        'sessionTitle': session_title.strip(),
                        'sessionTimestamp': session_time.strip(),
                        'logs': []
                    }
                elif line == '------------':
                    continue  # Ignore separator lines
                elif line:
                    # Assumes it's a log entry
                    match = re.match(r'\[(.*?)\]\s+UUID:\s*(.*?)\s*-\s*(.*)', line)
                    if match:
                        timestamp_str = match.group(1)
                        log_id = match.group(2)
                        message = match.group(3)
                        current_session['logs'].append({
                            'id': log_id,
                            'timestamp': timestamp_str,
                            'message': message,
                            'isEditable': True
                        })
            if current_session:
                sessions.append(current_session)

            # Reverse sessions to have the newest session first
            sessions.reverse()

            return jsonify({'sessions': sessions})
        except FileNotFoundError:
            return jsonify({'sessions': []})
        except Exception as e:
            # Log the exception
            print(f"Error parsing combined log: {e}")
            return jsonify({'sessions': []})
    else:
        return redirect(url_for('login'))

@app.route('/exit_unix_mode', methods=['POST'])
def exit_unix_mode():
    if 'logged_in' in session:
        session['unix_mode'] = False
        return jsonify({'success': True})
    else:
        return redirect(url_for('login'))

# Unix Mode Commands
@app.route('/unix_command', methods=['POST'])
def unix_command():
    if 'logged_in' in session and session.get('unix_mode'):
        global logs  # Declares 'logs' as global
        command = request.form.get('command', '').strip()

        if command == 'help':
            return jsonify({'output': 'Available commands: checkLog, deleteLog, help, clear, exit'})
        elif command == 'clear':
            return jsonify({'clear': True})
        elif command == 'exit':
            session['unix_mode'] = False
            return jsonify({'exit': True})
        elif command == 'checkLog':
            # Return the last 10 logs
            last_logs = logs[-10:] if len(logs) >= 10 else logs
            if last_logs:
                output = '\n'.join([f"[{log['timestamp']}] {log['message']}" for log in last_logs])
            else:
                output = 'No logs available.'
            return jsonify({'output': output})
        elif command.startswith('deleteLog'):
            # Delete a log by UUID
            parts = command.split()
            if len(parts) == 2:
                log_id = parts[1]
                # Delete from current session logs
                logs = [log for log in logs if log['id'] != log_id]

                # Delete from combined log
                combined_log_file = os.path.join(log_directory, "Combined Casper Log.txt")
                if os.path.exists(combined_log_file):
                    with open(combined_log_file, 'r') as f:
                        lines = f.readlines()
                    with open(combined_log_file, 'w') as f:
                        for line in lines:
                            if f"UUID: {log_id}" not in line:
                                f.write(line)
                return jsonify({'output': f'Log {log_id} deleted.'})
            else:
                return jsonify({'output': 'Usage: deleteLog <UUID>'})
        else:
            return jsonify({'output': f'Command not recognized: {command}'})
    else:
        return redirect(url_for('login'))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if 'logged_in' in session:
        # Try Werkzeug shutdown first
        if request.environ.get('werkzeug.server.shutdown'):
            shutdown_server()
        else:
            # if Werkzeug shutdown isn't available kill process
            os.kill(os.getpid(), signal.SIGTERM)
        return 'Server shutting down...'
    else:
        return redirect(url_for('login'))

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)