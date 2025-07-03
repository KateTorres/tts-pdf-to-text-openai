# PDF Text Extraction Toolkit

This toolkit extracts and cleans text from PDF files using either:
- Local processing (offline, no API)
- OpenAI API (GPT-3.5-Turbo or GPT-4o), with automatic cost tracking

Features include paragraph restoration, hyphenation fix, formatting cleanup, and GUI-based file selection.

---

## Features

- Extract PDF text using PyPDF2 (offline) or OpenAI GPT API
- Clean line breaks, fix split or hyphenated words, remove headers/footers
- Track OpenAI token usage and estimated cost per document
- GUI-based file picker (remembers last folder used)
- Cross-platform support (Windows `.bat`, Linux `.sh`)
- Modular code with reusable components (`utils/`)

---

## How to Install

### 1. Clone the repository

git clone https://github.com/your-username/pdf-text-extractor.git
cd pdf-text-extractor

## 2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt

## 3. (Linux only) Install Tkinter if not already installed

## 4. OpenAI Access (if not yet )
⚠️ Note: Each run with OpenAI API will consume tokens and may incur charges. Use the built-in cost calculator to track expenses.

OpenAI API Setup
Go to OpenAI API Keys
Click "Create new secret key"
Copy the key and set it as an environment variable.

## Run
### On Windows:
python main.py or run_pdf_extraction.bat

### On Linux/macOS:
chmod +x run_pdf_extraction.py (first time that you use it)
./run_pdf_extraction.sh

## Project Structure
```
graphql
Copy
Edit
.
├── main.py 
├── cost_calculator.py 
├── local_pdf_to_text.py
├── openai_pdf_to_text.py 
├── file_selector.py
├── requirements.txt
├── run_pdf_exctraction.bat
├── run_pdf_extraction.py
├── CHANGELOG.md
├── .gitignore
├── pdf_processing_log.json
├── cost_log.json
├── last_directory.json
├── utils/
│   ├── dialogs.py
│   ├── paths.py
│   ├── logging_utils.py
```
## Program Flow
- Select a PDF file
- Choose either:
    - Local processing
    - OpenAI API processing
- Enter page range
- Output is saved as .txt
- Logs are updated with task and cost info

## Logs
- pdf_processing_log.json: Info about each extraction
- cost_log.json: Cost breakdown (OpenAI only)
- last_directory.json: Remembers folder between runs

## License
This project is licensed under the MIT License.
You are free to use, modify, and distribute this software for personal or commercial purposes.
See the LICENSE file for details.
