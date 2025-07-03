import os
import re
import unicodedata
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

def is_russian_word(word):
    """Check if a word consists mainly of Russian characters."""
    return bool(re.match(r'^[а-яА-ЯёЁ-]+$', word))  # Allow hyphenated words

def contains_foreign_language(words):
    """
    Detect if there are at least 3 consecutive non-Russian words.
    If yes, classify as foreign language and remove the section.
    """
    non_russian_count = 0
    for word in words:
        if not is_russian_word(word):
            non_russian_count += 1
            if non_russian_count >= 3:  # Threshold for detecting a foreign segment
                return True
        else:
            non_russian_count = 0  # Reset counter if a Russian word is found
    return False

def is_page_number(line):
    """Check if the line consists of only a page number."""
    return bool(re.match(r'^\s*\d+\s*$', line))  # Matches lines with only numbers (page numbers)

def clean_line(line):
    """Remove unwanted characters like * and superscript/subscript numbers."""
    line = line.replace("*", "")  # Remove asterisks

    # Remove numbers that are likely indexes (superscripts/subscripts)
    line = re.sub(r'(?<!\w)\d+(?!\w)', '', line)  # Removes numbers that are isolated (not part of a word)

    return line.strip()

def normalize_hyphenated_words(text):
    """
    Joins words split by a hyphen at the end of a line while recognizing different hyphen variations.
    Fixes cases where a hyphen is followed by a newline.
    """
    # Normalize various hyphen variations to a standard hyphen (-)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', text)  # Convert different dashes to standard hyphen

    # Join words that were split across lines due to hyphenation.
    # The next line must start with a lowercase letter to be merged.
    text = re.sub(r'(\b\w+)-\s*\n\s*([а-яёa-z]\w+)', r'\1\2', text, flags=re.IGNORECASE)

    return text

def process_extracted_text(text):
    """
    Cleans extracted text:
    - Removes page numbers
    - Removes superscript/subscript indexes
    - Joins hyphenated words (recognizing different hyphen characters)
    - Removes non-Russian words only if 3+ appear consecutively
    - Maintains paragraph structure
    """
    # Normalize and join hyphenated words first
    text = normalize_hyphenated_words(text)

    lines = text.split("\n")
    processed_lines = []
    paragraph = []

    for i in range(len(lines)):
        line = clean_line(lines[i].strip())  # Remove unwanted symbols

        # Exclude page numbers
        if is_page_number(line):
            continue

        # Detect paragraph break
        if not line:
            if paragraph:
                processed_lines.append(" ".join(paragraph))
                paragraph = []
            continue

        # If line starts with an indentation, begin a new paragraph
        if lines[i].startswith(" ") or lines[i].startswith("\t"):
            if paragraph:
                processed_lines.append(" ".join(paragraph))
                paragraph = []

        words = line.split()

        # Check for foreign language exclusion
        if contains_foreign_language(words):
            continue  # Skip the entire section if foreign words dominate

        paragraph.append(" ".join(words))

    # Add last paragraph if exists
    if paragraph:
        processed_lines.append(" ".join(paragraph))

    return "\n\n".join(processed_lines)  # Use double newline to indicate paragraphs

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """
    Extracts text from a PDF for a given page range and applies text processing rules.
    """
    start_time = datetime.now()
    extracted_text = ""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        if end_page is None or end_page > num_pages:
            end_page = num_pages

        for i in range(start_page - 1, end_page):
            text = reader.pages[i].extract_text()
            if text:
                extracted_text += text + "\n"

    # Clean and format extracted text
    processed_text = process_extracted_text(extracted_text)

    duration = (datetime.now() - start_time).total_seconds()
    pdf_name = os.path.basename(pdf_path)

    return processed_text, pdf_name, duration, end_page - start_page + 1

def save_processed_text(text, pdf_name):
    """
    Saves the cleaned text to a .txt file.
    """
    text_file = pdf_name.replace(".pdf", "_processed.txt")
    with open(text_file, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"Processed text saved to: {text_file}")
    return text_file

if __name__ == "__main__":
    pdf_path = input("Enter the PDF file path: ")
    
    if not os.path.exists(pdf_path):
        print("Error: File not found.")
    else:
        processed_text, pdf_name, duration, pages_processed = extract_text_from_pdf(pdf_path)
        text_file = save_processed_text(processed_text, pdf_name)
        log_task(pdf_name, text_file, str(datetime.now()), duration, pages_processed)
