import os

def read_snort_alerts(log_path="/var/log/snort/alert.vpn"):
    if not os.path.exists(log_path):
        return ["Snort alert log not found."]
    try:
        with open(log_path, 'r') as f:
            return f.readlines()[-20:]  # last 20 alerts
    except Exception as e:
        return [f"Error reading log: {e}"]
