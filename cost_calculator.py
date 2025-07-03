import os
import json
from datetime import datetime

COST_LOG_FILE = "cost_log.json"
MODEL_PRICING = {
    "gpt-3.5-turbo": 0.0015,  # dollars per 1K tokens (input + output)
    "gpt-4o": 0.005           # dollars per 1K tokens
}

def calculate_cost():
    if not os.path.exists(COST_LOG_FILE):
        print("No cost log found. Skipping cost calculation.")
        return

    with open(COST_LOG_FILE, "r", encoding="utf-8") as f:
        try:
            cost_data = json.load(f)
        except json.JSONDecodeError:
            print("Invalid cost log file.")
            return

    total_cost = 0.0
    print("\n--- OpenAI API Cost Summary ---")
    for entry in cost_data:
        tokens = entry.get("tokens", 0)
        model = entry.get("model", "unknown")
        rate = MODEL_PRICING.get(model, 0)
        cost = (tokens / 1000.0) * rate
        total_cost += cost
        print(f"{entry['timestamp']}: {entry['file']} | Model: {model} | Tokens: {tokens} | Cost: ${cost:.4f}")

    print(f"\nTotal estimated cost: ${total_cost:.4f}\n")

def log_cost(file_name, model, tokens):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": file_name,
        "model": model,
        "tokens": tokens
    }

    if os.path.exists(COST_LOG_FILE):
        with open(COST_LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(COST_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
