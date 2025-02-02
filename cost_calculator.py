import os
import json
import requests
from datetime import datetime

LOG_FILE = "pdf_processing_log.json"
COST_LOG_FILE = "cost_log.json"
OPENAI_PRICING_URL = "https://openai.com/pricing"

# Default Pricing (Updated dynamically if fetched successfully)
PRICING = {
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},  # Per 1K tokens
    "gpt-4o": {"input": 0.005, "output": 0.015},  # Per 1K tokens
}

def fetch_openai_pricing():
    """
    Fetch OpenAI pricing from the official website.
    Currently, OpenAI does not provide an API for this, so we rely on manual updates.
    """
    try:
        print("Fetching OpenAI pricing...")
        response = requests.get(OPENAI_PRICING_URL, timeout=10)
        if response.status_code == 200:
            print("Pricing fetched successfully. Using stored values.")
        else:
            print(f"Failed to fetch pricing. Using default values. HTTP {response.status_code}")
    except requests.RequestException:
        print("Network issue: Unable to fetch OpenAI pricing. Using stored values.")

def calculate_cost():
    """
    Reads `pdf_processing_log.json`, calculates total cost, and logs it to `cost_log.json`.
    """
    if not os.path.exists(LOG_FILE):
        print(f"Log file `{LOG_FILE}` not found.")
        return
    
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        try:
            logs = json.load(file)
        except json.JSONDecodeError:
            print("Error: Log file contains invalid JSON.")
            return
    
    total_cost = 0
    cost_entries = []

    for log in logs:
        model = log.get("model_used", "gpt-3.5-turbo")
        tokens_used = log.get("tokens_used", {}).get("total_tokens_used", 0)
        api_calls = log.get("api_calls_made", 1)

        # Assume a 50/50 input and output token split
        input_tokens = tokens_used // 2
        output_tokens = tokens_used - input_tokens

        # Calculate cost per model
        input_cost = (input_tokens / 1000) * PRICING.get(model, {}).get("input", 0)
        output_cost = (output_tokens / 1000) * PRICING.get(model, {}).get("output", 0)

        total_entry_cost = input_cost + output_cost
        total_cost += total_entry_cost

        # Prepare log entry
        cost_entries.append({
            "timestamp": log["timestamp"],
            "pdf_file": log["pdf_file"],
            "tokens_used": tokens_used,
            "api_calls": api_calls,
            "model_used": model,
            "cost_estimate_usd": round(total_entry_cost, 6)
        })

    # Save results to cost log
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_cost_usd": round(total_cost, 6),
        "details": cost_entries
    }

    if os.path.exists(COST_LOG_FILE):
        with open(COST_LOG_FILE, "r", encoding="utf-8") as file:
            try:
                cost_logs = json.load(file)
            except json.JSONDecodeError:
                cost_logs = []
    else:
        cost_logs = []

    cost_logs.append(log_entry)

    with open(COST_LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(cost_logs, file, indent=4, ensure_ascii=False)

    print(f"Cost calculation completed. Total estimated cost: ${total_cost:.6f}")

if __name__ == "__main__":
    fetch_openai_pricing()
    calculate_cost()
