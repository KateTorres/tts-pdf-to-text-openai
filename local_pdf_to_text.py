import os
import re
import PyPDF2
import json
from datetime import datetime

LOG_FILE = "pdf_processing_log.json"

def log_task(pdf_name, text_file, start_time, duration, pages_processed):
    """
    Logs details of the PDF processing task to a JSON log file.
    """
    log_entry = {
        "timestamp": start_time,
        "task_duration_seconds": round(duration, 2),
        "pdf_file": pdf_name,
        "text_file": text_file,
        "pages_processed": pages_processed,
        "method_used": "Local Processing (No API)"
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

def process_pdf_text(raw_text):
    """
    Processes the raw text extracted from the PDF by:
      1. Normalizing newline characters.
      2. Replacing soft line breaks (a newline not immediately followed by another newline) with a space.
      3. Splitting on two or more consecutive newlines to preserve true paragraph breaks.
      4. Trimming each paragraph and rejoining them with two newlines.
    """
    # Normalize newlines to "\n"
    normalized = re.sub(r'\r\n', '\n', raw_text)
    # Replace any newline that is not immediately followed by another newline with a space
    soft_joined = re.sub(r'\n(?!\n)', ' ', normalized)
    # Split into paragraphs on two or more newlines
    paragraphs = re.split(r'\n\s*\n', soft_joined)
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return "\n\n".join(paragraphs)

def fix_hyphenated_splits(text):
    """
    Joins words that have been split by a hyphen with surrounding spaces,
    if both parts are entirely lowercase. For example:
      "опубли - кованных" → "опубликованных"
      "докумен - тов" → "документов"
    Proper compound names like "Нью -Йоркской" remain unchanged.
    """
    # Pattern matches a hyphen between word parts (letters only, including Russian letters)
    pattern = re.compile(r'(?P<left>\b[а-яёa-z]+)\s*-\s*(?P<right>[а-яёa-z]+\b)', re.IGNORECASE)
    def join_match(m):
        left = m.group('left')
        right = m.group('right')
        # Only join if both parts are all lowercase
        if left == left.lower() and right == right.lower():
            return left + right
        else:
            return m.group(0)
    return pattern.sub(join_match, text)

def fix_split_words(text):
    """
    Optionally fixes small accidental splits where a word is broken with a space.
    For example, "developm ent" → "development" if the right fragment is 1–3 letters and not a common word.
    (This function can be tuned or removed if it causes unwanted merging.)
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

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """
    Extracts text from the PDF file using local processing.
    The text is processed to:
      - Replace soft line breaks with spaces while preserving paragraph breaks.
      - Join words split by hyphens if they appear to be broken by a line break.
      - Optionally fix small accidental splits.
      - Ensure bullet points start on new lines.
      - Clean up punctuation and fix URLs/emails.
    """
    start_time = datetime.now()
    extracted_text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        if end_page is None or end_page > num_pages:
            end_page = num_pages
        for i in range(start_page - 1, end_page):
            page_text = reader.pages[i].extract_text()
            if page_text:
                extracted_text += page_text + "\n"
    # Process raw text to preserve paragraphs
    processed_text = process_pdf_text(extracted_text)
    # Join hyphenated word splits (if both parts are lowercase)
    processed_text = fix_hyphenated_splits(processed_text)
    # Optionally, fix other small accidental splits
    processed_text = fix_split_words(processed_text)
    # Ensure bullet points start on a new line
    processed_text = insert_newlines_before_bullets(processed_text)
    # Clean up punctuation and fix URLs/emails
    processed_text = fix_punctuation_spacing(processed_text)
    processed_text = fix_urls_and_emails(processed_text)
    
    duration = (datetime.now() - start_time).total_seconds()
    pdf_name = os.path.basename(pdf_path)
    # Optionally log the task:
    # log_task(pdf_name, "extracted_text.txt", start_time.isoformat(), duration, end_page - start_page + 1)
    return processed_text, pdf_name, duration, end_page - start_page + 1
