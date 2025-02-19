import os 
import sys
import json
from file_selector import select_pdf_file
from openai_pdf_to_text import extract_text_from_pdf as openai_extract
from local_pdf_to_text import extract_text_from_pdf as local_extract
from cost_calculator import calculate_cost

LAST_DIR_FILE = "last_directory.json"

def save_last_directory(directory):
    """Saves the last accessed directory to a file."""
    with open(LAST_DIR_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_dir": directory}, f)

def load_last_directory():
    """Loads the last accessed directory from a file, defaulting to the current directory."""
    if os.path.exists(LAST_DIR_FILE):
        with open(LAST_DIR_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("last_dir", os.getcwd())
    return os.getcwd()

def main():
    # Load the last accessed directory.
    last_dir = load_last_directory()
    pdf_path = select_pdf_file(last_dir)
    
    if not pdf_path:
        print("Error: No file selected. Please select a valid PDF file.")
        sys.exit(1)

    # Save the directory of the selected PDF for future use.
    save_last_directory(os.path.dirname(pdf_path))

    # Ask the user for the processing method.
    processing_choice = input("Choose processing method (1 for OpenAI API, 2 for Local Processing): ").strip()
    
    if processing_choice not in ["1", "2"]:
        print("Error: Invalid selection. Please choose 1 or 2.")
        sys.exit(1)

    # Ask for the page range.
    try:
        start_page = int(input("Enter the starting page number: ").strip())
        end_page = int(input("Enter the ending page number: ").strip())

        if start_page < 1 or end_page < start_page:
            raise ValueError
    except ValueError:
        print("Error: Invalid page numbers. Please enter valid integers (start must be ≤ end).")
        sys.exit(1)

    # Process the PDF based on user selection.
    if processing_choice == "1":
        # OpenAI API Processing.
        language_choice = input("Enter the PDF language (en for English, ru for Russian): ").strip().lower()
        if language_choice not in ["en", "ru"]:
            print("Error: Invalid language selection. Please choose 'en' or 'ru'.")
            sys.exit(1)

        model_choice = input("Choose OpenAI model (1 for GPT-3.5-Turbo, 2 for GPT-4o): ").strip()
        model = "gpt-3.5-turbo" if model_choice == "1" else "gpt-4o"

        extracted_text = openai_extract(pdf_path, language_choice, start_page, end_page, model)
    
        # Calculate and log the cost for OpenAI API usage.
        calculate_cost()
    
    else:
        # Local Processing (No API) – now updated to better handle both English and Russian.
        extracted_text, pdf_name, duration, pages_processed = local_extract(pdf_path, start_page, end_page)

    # Save the extracted text to a file in the same directory as the PDF.
    output_file = os.path.join(os.path.dirname(pdf_path), f"extracted_text_{start_page}-{end_page}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"Text extracted successfully. Saved in '{output_file}'.")

if __name__ == "__main__":
    main()
    