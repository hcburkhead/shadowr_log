#!/bin/bash

# Navigate to the project directory
cd ~/Downloads/shadowrun_log

# Run the renumbering script to ensure sessions are sequential
python3 renumber_sessions.py

# Launch the Flask app
export FLASK_APP=app.py
export FLASK_ENV=development
nohup python3 -m flask run --host=0.0.0.0 --port=5001 &

# Wait for the server to start
sleep 2

# Open Firefox in fullscreen mode with a new window pointing to the login page
open -na "Firefox" --args -new-window "http://127.0.0.1:5001/login"
