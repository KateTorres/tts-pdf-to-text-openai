import os
import openai
import PyPDF2
import json
import time
from datetime import datetime
import re
from tqdm import tqdm
from cost_calculator import log_cost

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY_JOHN"))

MAX_REQUESTS_PER_MINUTE = 3
MAX_TOKENS_PER_MINUTE = 40000
MAX_TOKENS_PER_DAY = 200000

requests_made = 0
tokens_used_today = 0
last_request_time = None

def enforce_rate_limit():
    global requests_made, last_request_time
    if requests_made >= MAX_REQUESTS_PER_MINUTE:
        elapsed = time.time() - last_request_time
        if elapsed < 60:
            time.sleep(60 - elapsed)
        requests_made = 0

def extract_text_from_pdf(pdf_path, language="en", start_page=1, end_page=None, model="gpt-3.5-turbo"):
    global requests_made, tokens_used_today, last_request_time
    start_time = datetime.now()
    pdf_text = ""
    api_calls = 0
    batch_size = 5

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        if end_page is None or end_page > num_pages:
            end_page = num_pages

        total_pages = end_page - (start_page - 1)
        progress_bar = tqdm(total=total_pages, desc="Processing PDF pages", unit="page")

        page_texts = []
        for i in range(start_page - 1, end_page):
            raw_text = reader.pages[i].extract_text() or ""
            cleaned = remove_header_footer(raw_text).strip()
            if cleaned:
                page_texts.append(cleaned)

            progress_bar.update(1)

            if len(page_texts) >= batch_size or i == end_page - 1:
                combined = "\n".join(page_texts)
                enforce_rate_limit()
                output, tokens = process_text_with_openai(combined, model)
                pdf_text += output
                tokens_used_today += tokens
                requests_made += 1
                api_calls += 1
                last_request_time = time.time()
                page_texts = []

                if tokens_used_today >= MAX_TOKENS_PER_DAY:
                    print("Daily token limit reached.")
                    break

        progress_bar.close()

    text_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}-extracted_text_{start_page}-{end_page}.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(pdf_text)

    log_cost(text_file, model, tokens_used_today)
    return pdf_text

def remove_header_footer(text):
    lines = text.splitlines()
    pattern = re.compile(r'^[\-=_]{5,}\s*$')
    first, last = None, None
    for i, line in enumerate(lines):
        if pattern.match(line.strip()):
            first = i
            break
    if first is not None:
        lines = lines[first + 1:]
    for i in reversed(range(len(lines))):
        if pattern.match(lines[i].strip()):
            last = i
            break
    if last is not None:
        lines = lines[:last]
    return "\n".join(lines)

def process_text_with_openai(text, model):
    if not text.strip():
        return "", 0
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"Clean and format this text:\n{text}"}],
        temperature=0.3,
        max_tokens=min(len(text.split()) * 2, 1000)
    )
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    return response.choices[0].message.content, input_tokens + output_tokens
