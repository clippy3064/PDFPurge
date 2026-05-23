import logging
import cv2
import numpy as np
import fitz  # PyMuPDF
import pytesseract
from pathlib import Path
from typing import List, Tuple, Dict, Any
from PIL import Image

# Configure logger
logger = logging.getLogger("docpurge.pdf_engine")

class PDFProcessingError(Exception):
    """Custom exception for PDF processing failures."""
    pass

def clean_pdf(input_path: Path, output_path: Path, settings: Dict[str, Any]) -> bool:
    """
    Orchestrates the PDF sanitization pipeline: 
    Rasterize -> Preprocess -> Detect -> Erase -> Reconstruct.
    
    Args:
        input_path: Path to source PDF.
        output_path: Path for the sanitized output PDF.
        settings: Configuration dictionary containing pdf_settings.
        
    Returns:
        True if successful, False otherwise.
    """
    pdf_settings = settings.get("pdf_settings", {})
    dpi = pdf_settings.get("dpi", 300)
    targets = pdf_settings.get("target_words", [])
    ocr_lang = pdf_settings.get("ocr_lang", "chi_sim+eng")
    
    if not targets:
        logger.warning(f"No target words provided for {input_path}. Skipping.")
        return True

    try:
        # Open PDF
        doc = fitz.open(input_path)
        processed_images = []

        logger.info(f"Processing PDF: {input_path.name} ({len(doc)} pages)")

        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 1. Rasterization
            # Use matrix for DPI scaling (72 DPI is default)
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert PyMuPDF pixmap to numpy array (OpenCV format)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            if pix.n == 4: # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3: # RGB
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # 2. Preprocessing
            # Convert to grayscale and apply Adaptive Thresholding
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            block_size = pdf_settings.get("adaptive_threshold_block_size", 11)
            c_val = pdf_settings.get("adaptive_threshold_c", 2)
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, block_size, c_val
            )

            # 3. Detection
            # Use Tesseract OCR on the thresholded image to find fragments
            boxes = _detect_fragments(thresh, targets, ocr_lang)
            
            if boxes:
                logger.debug(f"Page {page_num + 1}: Detected {len(boxes)} fragments.")
                # 4. Erasing
                # Fill detected regions. Since we want "surgical" removal, 
                # we use inpainting or simple filling with background color.
                img = _erase_fragments(img, boxes)
            else:
                logger.debug(f"Page {page_num + 1}: No fragments detected.")

            # Convert back to PIL Image for PDF reconstruction
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            processed_images.append(Image.fromarray(img_rgb))

        # 5. Reconstruction
        if processed_images:
            processed_images[0].save(
                output_path, 
                save_all=True, 
                append_images=processed_images[1:], 
                resolution=dpi
            )
            # Convert the image-based PDF to a standard PDF via PyMuPDF if needed, 
            # but PIL save as PDF is sufficient for a wrapper.
            # Note: To ensure output is exactly .pdf, PIL handles it.
            
        doc.close()
        return True

    except Exception as e:
        logger.error(f"Failed to process PDF {input_path}: {str(e)}")
        return False

def _detect_fragments(image: np.ndarray, targets: List[str], lang: str) -> List[Tuple[int, int, int, int]]:
    """
    Locates target text fragments in a binary image using Tesseract OCR.
    
    Returns:
        A list of bounding boxes (x, y, w, h).
    """
    boxes = []
    try:
        # pytesseract.image_to_data returns a dictionary containing coordinates
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if any(target in text for target in targets):
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                boxes.append((x, y, w, h))
    except Exception as e:
        logger.warning(f"OCR Detection error: {e}")
        
    return boxes

def _erase_fragments(image: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> np.ndarray:
    """
    Erases detected regions using inpainting to maintain background consistency.
    """
    # Create a mask for all detected boxes
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for (x, y, w, h) in boxes:
        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    
    # Use Telea inpainting to fill the holes based on surrounding pixels
    # This is more "surgical" than filling with pure white
    result = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return result
