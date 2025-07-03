import os
import sys
from file_selector import select_pdf_file
from openai_pdf_to_text import extract_text_from_pdf as openai_extract
from local_pdf_to_text import extract_text_from_pdf as local_extract
from cost_calculator import calculate_cost

LAST_DIR_FILE = "last_directory.json"

def save_last_directory(path):
    with open(LAST_DIR_FILE, "w", encoding="utf-8") as f:
        f.write(path)

def load_last_directory():
    if os.path.exists(LAST_DIR_FILE):
        with open(LAST_DIR_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return os.getcwd()

def main():
    last_dir = load_last_directory()
    pdf_path = select_pdf_file(last_dir)

    if not pdf_path:
        print("No file selected.")
        sys.exit(1)

    save_last_directory(os.path.dirname(pdf_path))

    method = input("Choose method: 1 = OpenAI, 2 = Local: ").strip()
    if method not in ["1", "2"]:
        print("Invalid method.")
        sys.exit(1)

    try:
        start_page = int(input("Start page: ").strip())
        end_page = int(input("End page: ").strip())
        if start_page < 1 or end_page < start_page:
            raise ValueError
    except ValueError:
        print("Invalid page range.")
        sys.exit(1)

    if method == "1":
        lang = input("Language (en): ").strip().lower() or "en"
        model = "gpt-4o" if input("Model? (1 = 3.5, 2 = 4o): ").strip() == "2" else "gpt-3.5-turbo"
        text = openai_extract(pdf_path, lang, start_page, end_page, model)
        calculate_cost()
    else:
        text, pdf_name, duration, pages = local_extract(pdf_path, start_page, end_page)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = os.path.join(os.path.dirname(pdf_path), f"{base_name}-extracted_text_{start_page}-{end_page}.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
