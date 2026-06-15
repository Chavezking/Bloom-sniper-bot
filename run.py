import subprocess
import time

# Start server.py
subprocess.Popen(["python", "app.py"])

# Start bot.py
subprocess.Popen(["python", "bg_worker.py"])

# Keep this process alive so Render doesn’t exit
while True:
    time.sleep(3600)