import os
import openai
import PyPDF2
import json
import time
from datetime import datetime
import re

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

def remove_header_footer(page_text):
    """
    Remove header and footer if they are separated from the main text by a 'long line'
    of dashes, underscores, or equals.
    Search each page for a line containing 5 or more of these characters.
    Everything above the first such line and below the last such line is removed.
    """
    lines = page_text.splitlines()
    separator_pattern = re.compile(r'^[\-=_]{5,}\s*$')
    # Find first separator
    first_sep_idx = None
    for i, line in enumerate(lines):
        if separator_pattern.match(line.strip()):
            first_sep_idx = i
            break
    if first_sep_idx is not None:
        lines = lines[first_sep_idx + 1:]
    # Find last separator
    last_sep_idx = None
    for i in reversed(range(len(lines))):
        if separator_pattern.match(lines[i].strip()):
            last_sep_idx = i
            break
    if last_sep_idx is not None:
        lines = lines[:last_sep_idx]
    return "\n".join(lines)

def process_pdf_text(raw_text):
    """
    Processes the raw text extracted from the PDF by:
      1. Normalizing newlines.
      2. Replacing soft line breaks (a newline not immediately followed by another newline) with a space.
      3. Splitting on two or more consecutive newlines to preserve true paragraph breaks.
      4. Trimming each paragraph and rejoining them with two newlines.
    """
    normalized = re.sub(r'\r\n', '\n', raw_text)
    soft_joined = re.sub(r'\n(?!\n)', ' ', normalized)
    paragraphs = re.split(r'\n\s*\n', soft_joined)
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return "\n\n".join(paragraphs)

def fix_hyphenated_splits(text):
    """
    Joins words that have been split by a hyphen with surrounding spaces,
    if both parts are entirely alphabetic.
    For example:
      "опубли - кованных" → "опубликованных"
      "докумен - тов" → "документов"
    Words containing numbers (e.g. "word123") remain unchanged.
    """
    pattern = re.compile(r'(?P<left>\b[а-яёa-z]+)\s*-\s*(?P<right>[а-яёa-z]+\b)', re.IGNORECASE)
    def join_match(m):
        left = m.group('left')
        right = m.group('right')
        if left == left.lower() and right == right.lower():
            return left + right
        else:
            return m.group(0)
    return pattern.sub(join_match, text)

def fix_split_words(text):
    """
    Fixes small accidental splits where a word is broken with a space.
    Only joins if both groups are alphabetic (thus preserving numbers in words like "word123").
    """
    common_words = {"and", "for", "the", "but", "not", "or", "nor", "a", "an",
                    "in", "on", "by", "of", "to", "at", "if", "is", "it", "as"}
    pattern = re.compile(r'([a-zа-яё]{4,})\s+([a-zа-яё]{1,3})(\b)', re.IGNORECASE)
    def replacer(match):
        left = match.group(1)
        right = match.group(2)
        if right.lower() in common_words:
            return match.group(0)
        return left + right + match.group(3)
    return pattern.sub(replacer, text)

def insert_newlines_before_bullets(text):
    """
    Ensures that bullet points (lines beginning with "•") start on a new line.
    """
    return re.sub(r'\s*(•)', r'\n\1', text)

def fix_punctuation_spacing(text):
    """
    Cleans up spacing around punctuation:
      - Removes extra spaces before punctuation marks.
      - Ensures exactly one space after punctuation if followed by a letter or digit.
      - Collapses multiple consecutive spaces into one.
    """
    text = re.sub(r'\s+([.,?!;:])', r'\1', text)
    text = re.sub(r'([.,?!;:])([A-Za-zА-Яа-яЁё0-9])', r'\1 \2', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text

def fix_urls_and_emails(text):
    """
    Removes extraneous spaces inside URLs and email addresses.
    For example:
      "druginfo@fda. hhs. gov" → "druginfo@fda.hhs.gov"
      "http://www. fda. gov/Page" → "http://www.fda.gov/Page"
    """
    text = re.sub(r'(\S+@\S+)', lambda m: m.group(1).replace(' ', ''), text)
    text = re.sub(r'(https?://\S+)', lambda m: m.group(1).replace(' ', ''), text)
    return text

def extract_text_from_pdf(pdf_path, language="en", start_page=1, end_page=None, model="gpt-3.5-turbo"):
    """
    Extracts text from the PDF file using OpenAI API.
    
    For each page:
      - Extract text.
      - Remove header and footer (if a separator line is found).
    Then pages are batched and processed via OpenAI API.
    The processing includes:
      - Reassembling soft line breaks while preserving paragraph breaks.
      - Fixing hyphenated splits (only joining purely alphabetic fragments).
      - Fixing accidental splits.
      - Inserting newlines before bullet points.
      - Cleaning up punctuation and URLs/emails.
      
    Finally, the processed text is saved to a text file with the same base name as the input PDF.
    """
    global requests_made, tokens_used_today, last_request_time
    start_time_dt = datetime.now()
    pdf_text = ""
    batch_size = 5  # Process 5 pages per API request
    api_calls = 0

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        if end_page is None or end_page > num_pages:
            end_page = num_pages

        page_texts = []
        for i in range(start_page - 1, end_page):
            raw_page_text = reader.pages[i].extract_text() or ""
            # Process header/footer removal for each page individually.
            cleaned_page_text = remove_header_footer(raw_page_text).strip()
            if cleaned_page_text:
                page_texts.append(cleaned_page_text)
            if len(page_texts) >= batch_size or i == end_page - 1:
                combined_text = "\n".join(page_texts)
                enforce_rate_limit()
                output_text, token_usage = process_text_with_openai(combined_text, model)
                pdf_text += output_text
                tokens_used_today += token_usage
                requests_made += 1
                api_calls += 1
                last_request_time = time.time()
                page_texts = []
                if tokens_used_today >= MAX_TOKENS_PER_DAY:
                    print("Daily token limit reached. Stopping further processing.")
                    break

    # Save the output text using the exact base name of the input PDF.
    base_name = os.path.basename(pdf_path)
    base, ext = os.path.splitext(base_name)
    text_file_path = os.path.join(os.path.dirname(pdf_path), base + ".txt")
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(pdf_text)

    duration = (datetime.now() - start_time_dt).total_seconds()
    pdf_name = os.path.basename(pdf_path)
    log_task(pdf_name, text_file_path, model, {"total_tokens_used": tokens_used_today},
             start_time_dt.strftime("%Y-%m-%d %H:%M:%S"), duration, api_calls)
    return pdf_text

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
