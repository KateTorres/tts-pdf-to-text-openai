# utils/logging_utils.py

import os
import json

def append_to_json_log(log_path, entry):
    """
    Append a log entry to a JSON log file. Creates the file if missing or empty.
    """
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
