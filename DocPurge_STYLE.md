# DocPurge_STYLE.md - Development Guidelines

## 1. Coding Standards
- **Language:** Python 3.10+
- **Style Guide:** PEP 8.
- **Naming Convention:** 
    - Functions/Variables: `snake_case`
    - Classes: `PascalCase`
    - Constants: `UPPER_SNAKE_CASE`
- **Typing:** Mandatory type hinting for all function signatures (`def func(x: int) -> str:`).

## 2. Structural Principles
- **Decoupling:** The `processor.py` should not know *how* the `pdf_engine` works, only that it can call `clean_pdf()`.
- **Functional Pureness:** Processing functions should not modify input files in-place; they must always return a new file or write to a designated output path.
- **Error Handling:** 
    - Use specific exceptions (e.g., `PDFProcessingError`, `ConfigError`).
    - Wrap external binary calls (Tesseract) in try-except blocks.

## 3. Logging & Output
- **No `print()` for Logic:** Use the `logging` module for all status and error messages.
- **Log Levels:** 
    - `INFO`: High-level progress (e.g., "Processing file X...").
    - `DEBUG`: Detailed steps (e.g., "Detected watermark at (100, 200)").
    - `ERROR`: Critical failures that stop a file from being processed.
- **Console Output:** Use a clean, minimal progress bar (e.g., `tqdm`) for batch operations.

## 4. Performance Goals
- **Memory:** Process PDF pages as a generator/stream to handle 100MB+ files without crashing.
- **Speed:** Use `PyMuPDF` for rendering as it is significantly faster than `pdf2image`.
- **OCR Optimization:** Only run Tesseract on grayscale, thresholded images to increase detection speed and accuracy.
