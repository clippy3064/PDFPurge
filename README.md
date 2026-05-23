PDFPurge: The Surgical Document Sanitizer

Stop squinting through watermarks. Start purging.

PDFPurge is a high-precision CLI utility designed to sanitize educational and corporate documents. It specializes
in the "surgical" removal of intrusive watermarks from PDF files and the total erasure of imagery from Microsoft
Word documents. In short: it's a digital vacuum cleaner for your documents, designed for anyone who is tired of
seeing stamped across every single page of their life.

### 🚀 Features (The "Surgical" Suite)

- Surgical PDF Cleaning: Using a sophisticated pipeline of PyMuPDF, OpenCV, and Tesseract OCR, the tool identifies
and erases specific text fragments without destroying the rest of the page. It's basically a scalpel for your
PDFs. 
- The Word "Nuke": Rapidly strips all InlineShapes and images from .docx and .docm files. If it's a picture and
it's in the way, it's gone. Poof. 💥
- Recursive Batch Automation: Point it at a root folder and watch it cleanse entire directory trees automatically.
No more cleaning files one by one like a peasant.
- Configuration-Driven Logic: Fully customizable via settings.yaml. You define the target words and the
thresholds; the tool does the dirty work. No hardcoding, no stress.
- The "Safety Valve" (Dry Run): Includes a --dry-run mode so you can see exactly what will be destroyed before you
actually pull the trigger.

### 🛠️ Technical Hoard (The Stack)

- Language: Python 3.10+ (The engine of chaos)
- Vision: OpenCV + Tesseract OCR (The eyes that see through the watermarks)
- Parsing: PyMuPDF + python-docx (The hands that dismantle the docs)
- Config: PyYAML (The brain that remembers your preferences)