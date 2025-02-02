import os
import openai
import PyPDF2
import json
import time
from datetime import datetime

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY_JOHN"))
LOG_FILE = "pdf_processing_log.json"

# OpenAI API quota
MAX_REQUESTS_PER_MINUTE = 3
MAX_TOKENS_PER_MINUTE = 40000
MAX_TOKENS_PER_DAY = 200000

# Global counters for tracking requests and tokens
requests_made = 0
tokens_used_today = 0
last_request_time = None

def enforce_rate_limit():
    """Ensures compliance with OpenAI API rate limits."""
    global requests_made, last_request_time

    if requests_made >= MAX_REQUESTS_PER_MINUTE:
        elapsed_time = time.time() - last_request_time
        if elapsed_time < 60:
            wait_time = 60 - elapsed_time
            print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        requests_made = 0  # Reset counter

def log_task(pdf_name, text_file, model_used, tokens_used, start_time, duration, api_calls):
    """Logs details of the PDF processing task to a JSON log file."""
    log_entry = {
        "timestamp": start_time,
        "task_duration_seconds": round(duration, 2),
        "pdf_file": pdf_name,
        "text_file": text_file,
        "model_used": model_used,
        "tokens_used": tokens_used,
        "api_calls_made": api_calls
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=4, ensure_ascii=False)

def extract_text_from_pdf(pdf_path, language="en", start_page=1, end_page=None, model="gpt-3.5-turbo"):
    """Extracts text from a PDF using OpenAI API and saves it in the same directory as the PDF."""
    global requests_made, tokens_used_today, last_request_time
    start_time = datetime.now()
    extracted_text = ""
    batch_size = 5  # Process 5 pages per API request
    api_calls = 0

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        if end_page is None or end_page > num_pages:
            end_page = num_pages

        page_texts = []
        for i in range(start_page - 1, end_page):
            text = reader.pages[i].extract_text()
            if text:
                page_texts.append(text)

            if len(page_texts) >= batch_size or i == end_page - 1:
                combined_text = "\n".join(page_texts)
                enforce_rate_limit()

                output_text, token_usage = process_text_with_openai(combined_text, model)
                extracted_text += output_text

                tokens_used_today += token_usage
                requests_made += 1
                api_calls += 1
                last_request_time = time.time()

                page_texts = []

                if tokens_used_today >= MAX_TOKENS_PER_DAY:
                    print("Daily token limit reached. Stopping further processing.")
                    break

    duration = (datetime.now() - start_time).total_seconds()
    pdf_name = os.path.basename(pdf_path)
    log_task(pdf_name, pdf_path, model, {"total_tokens_used": tokens_used_today}, start_time.strftime("%Y-%m-%d %H:%M:%S"), duration, api_calls)

    return extracted_text

def process_text_with_openai(text, model):
    """Sends text to OpenAI API and returns the processed output."""
    global requests_made, tokens_used_today

    if not text.strip():
        return "", 0

    prompt_text = f"Ensure the following text is properly extracted and formatted:\n\n{text}"

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.3,
        max_tokens=min(len(text.split()) * 2, 1000)
    )

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = input_tokens + output_tokens

    return response.choices[0].message.content, total_tokens
