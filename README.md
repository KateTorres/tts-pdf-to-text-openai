# tts_pdf_to_text_openai
This repository provides a PDF text extraction tool that allows users to convert text from PDF files and optionally translate it into English or Russian using OpenAI's API. The tool supports page range selection, automatic logging, and model selection (GPT-3.5-Turbo or GPT-4o) for efficient processing.

# PDF Text Extractor with OpenAI API

## Overview
This project extracts text from PDF files, processes it using the OpenAI API, and provides an option to keep text in English or Russian. The extracted text is saved in the same directory as the source PDF file, and logs are maintained for tracking usage and cost.

## Features
- **Accurate Text Extraction:**  
  Extract text from specific page ranges in a PDF with minimal loss of formatting.
- **Advanced Local Processing:**  
  - **Reassemble Soft Line Breaks:** Joins lines within paragraphs to form complete sentences.  
  - **Fix Hyphenated Word Splits:** Automatically joins words broken by a hyphen with surrounding spaces (e.g., “опубли - кованных” → “опубликованных”) while preserving legitimate compound words.  
  - **Preserve Document Structure:** Maintains paragraph breaks and ensures bullet points begin on new lines.
  - **Clean Punctuation & URLs:** Removes extraneous spaces around punctuation and inside URLs/emails.
- **OpenAI API Integration (Optional):**  
  Process or translate text using GPT-3.5-Turbo for cost efficiency or GPT-4o for higher quality.
- **Automatic Logging:**  
  Tracks tasks including file name, processing duration, pages processed, and cost calculations. Log rotation occurs when file size exceeds 100 KB.
- **User-Friendly Interface:**  
  Easy command-line interaction that remembers your last accessed directory and saves the output in the same folder as the input PDF.
- **Cross-Platform Compatibility:**  
  Works on Windows, Linux, and macOS.

## Installation

### Clone the Repository
```sh
git clone https://github.com/yourusername/pdf-text-extractor.git
cd pdf-text-extractor
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Set OpenAI API Key
```sh
export OPENAI_API_KEY="your-api-key-here"  # Linux/macOS
set OPENAI_API_KEY=your-api-key-here       # Windows (CMD)
$env:OPENAI_API_KEY="your-api-key-here"    # Windows (PowerShell)
```

## Usage

### Windows
```sh
run_pdf_extraction.bat
```

### Linux/macOS
```sh
./run_pdf_extraction.sh
```

### Manual Execution
```sh
python main.py
```

## Cost Calculation
After extracting text from the PDF, the program automatically calculates the cost based on OpenAI's pricing and logs it in `cost_log.json`.

### Running Cost Calculation Separately
```sh
python cost_calculator.py
```

## Logging System
- A log file (`pdf_processing_log.json`) is generated in the script's directory.
- When the log file exceeds 100 KB, a new file is created with a timestamped name.
- Cost calculations are logged in `cost_log.json`.

## Contributions
Contributions are welcome. Submit a pull request or open an issue.

## License
This project is licensed under the MIT License.

## Contact
For questions or suggestions, reach out via [GitHub Issues](https://github.com/yourusername/pdf-text-extractor/issues).

