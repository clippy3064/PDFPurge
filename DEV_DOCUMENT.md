# DEV_DOCUMENT.md - Project DocPurge

## 1. Project Overview
**DocPurge** is a high-precision CLI tool designed to sanitize educational documents by removing watermarks from PDFs and images from Word documents. It is specifically optimized for "surgical" removals using computer vision.

### 1.1 Core Goals
- **Precision:** Remove specific text fragments (watermarks) without damaging the underlying content.
- **Automation:** Process entire directories recursively.
- **Configurability:** Use an external YAML file to manage thresholds and target patterns.

---

## 2. System Architecture

### 2.1 High-Level Flow
`User Input (CLI)` $\rightarrow$ `Config Loader` $\rightarrow$ `Batch Processor` $\rightarrow$ `Specific Engine (PDF/Word)` $\rightarrow$ `Output File`

### 2.2 PDF Processing Pipeline (The "Surgical" Flow)
1. **Rasterization:** Convert PDF pages to high-resolution images using `PyMuPDF`.
2. **Preprocessing:** Convert to grayscale and apply Adaptive Thresholding (OpenCV).
3. **Detection:** Use `Tesseract OCR` to locate the coordinates of target fragments (e.g., "工附").
4. **Erasing:** Fill detected regions with the background color (Inpainting/Filling).
5. **Reconstruction:** Convert processed images back into a PDF wrapper.

### 2.3 Word Processing Pipeline (The "Nuke" Flow)
1. **Parsing:** Load `.docx` or `.docm` using `python-docx`.
2. **Iterative Removal:** Traverse all document elements.
3. **Element Deletion:** Identify and remove `InlineShapes` and `Shapes`.
4. **Property Scrub:** Clear `core_properties` (Author, Created Date, etc.).

---

## 3. Environment & Dependencies

### 3.1 System Requirements
- **OS:** Linux / WSL2
- **Python:** 3.10+
- **External Binaries:** 
    - `tesseract-ocr` (The OCR engine)
    - `poppler-utils` (For PDF rendering support)

### 3.2 Python Libraries
| Library | Purpose |
| :--- | :--- |
| `pymupdf` | Fast PDF parsing and image extraction |
| `opencv-python` | Image processing and mask generation |
| `pytesseract` | Wrapper for Tesseract OCR |
| `python-docx` | Word document manipulation |
| `pyyaml` | Configuration management |

---

## 4. Configuration Specification (`settings.yaml`)

The tool relies on a YAML config to avoid hardcoding.

```yaml
paths:
  input_dir: "./input"
  output_dir: "./output"
  log_file: "purge.log"

pdf_settings:
  dpi: 300
  adaptive_threshold_block_size: 11
  adaptive_threshold_c: 2
  target_words: ["工附", "微信", "圣贤", "资料"]
  ocr_lang: "chi_sim+eng"

word_settings:
  remove_images: true
  remove_metadata: true
```

---

## 5. Implementation Roadmap

### Node 1: Foundation & Config
- Setup directory structure.
- Implement `config_loader.py` to parse `settings.yaml`.

### Node 2: The Word Nuke (Low Complexity)
- Implement `word_engine.py`.
- Create the image erasure loop.
- Test with various `.docx` samples.

### Node 3: PDF Rasterization & OCR (Medium Complexity)
- Implement the PDF $\rightarrow$ Image $\rightarrow$ OCR pipeline.
- Create the coordinate-mapping logic for watermarks.

### Node 4: PDF Surgical Erasing (High Complexity)
- Implement the OpenCV filling logic.
- Implement the Image $\rightarrow$ PDF reconstruction.
- Tune thresholds for "surgical" precision.

### Node 5: Batch Orchestration & CLI
- Implement `processor.py` for recursive directory walking.
- Create `main.py` with `argparse` for CLI interaction.
- Implement "Dry Run" mode.

---

## 6. Safety & Constraints
- **Backup First:** The tool should always write to an `output_dir` rather than overwriting source files.
- **OCR Failures:** If Tesseract fails to find a word, it should log a warning but continue processing the page.
- **Memory Management:** Process PDFs page-by-page to avoid OOM errors on large documents.
