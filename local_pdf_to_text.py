import os
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

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """
    Extracts text from a PDF for a given page range using only local processing (no OpenAI API).
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

    duration = (datetime.now() - start_time).total_seconds()
    pdf_name = os.path.basename(pdf_path)

    return extracted_text, pdf_name, duration, end_page - start_page + 1
