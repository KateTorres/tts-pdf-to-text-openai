import os
import re
import unicodedata
import PyPDF2
from datetime import datetime

def is_russian_word(word):
    return bool(re.match(r'^[а-яА-ЯёЁ-]+$', word))

def contains_foreign_language(words):
    non_russian = 0
    for word in words:
        if not is_russian_word(word):
            non_russian += 1
            if non_russian >= 3:
                return True
        else:
            non_russian = 0
    return False

def is_page_number(line):
    return bool(re.match(r'^\s*\d+\s*$', line))

def clean_line(line):
    line = line.replace("*", "")
    line = re.sub(r'(?<!\w)\d+(?!\w)', '', line)
    return line.strip()

def normalize_hyphenated_words(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', text)
    return re.sub(r'(\b\w+)-\s*\n\s*([а-яёa-z]\w+)', r'\1\2', text, flags=re.IGNORECASE)

def process_extracted_text(text):
    text = normalize_hyphenated_words(text)
    lines = text.split("\n")
    processed_lines, paragraph = [], []

    for i in range(len(lines)):
        line = clean_line(lines[i].strip())
        if is_page_number(line): continue
        if not line:
            if paragraph:
                processed_lines.append(" ".join(paragraph))
                paragraph = []
            continue
        if lines[i].startswith((" ", "\t")):
            if paragraph:
                processed_lines.append(" ".join(paragraph))
                paragraph = []
        words = line.split()
        if contains_foreign_language(words): continue
        paragraph.append(" ".join(words))

    if paragraph:
        processed_lines.append(" ".join(paragraph))
    return "\n\n".join(processed_lines)

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    start_time = datetime.now()
    extracted_text = ""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        if end_page is None or end_page > len(reader.pages):
            end_page = len(reader.pages)

        for i in range(start_page - 1, end_page):
            text = reader.pages[i].extract_text()
            if text:
                extracted_text += text + "\n"

    processed = process_extracted_text(extracted_text)
    pdf_name = os.path.basename(pdf_path)
    return processed, pdf_name, (datetime.now() - start_time).total_seconds(), end_page - start_page + 1
