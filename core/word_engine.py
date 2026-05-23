import logging
from pathlib import Path
from docx import Document
from docx.oxml.shape import CT_Shape
from docx.oxml.inline_shape import CT_InlineShape

logger = logging.getLogger(__name__)

def clean_word(input_path: Path, output_path: Path, settings: dict) -> bool:
    """
    Sanitizes a Word document by removing images (InlineShapes and Shapes) 
    and scrubbing core metadata properties.
    
    Args:
        input_path (Path): Path to the source .docx file.
        output_path (Path): Path where the sanitized file will be saved.
        settings (dict): Configuration settings containing 'word_settings'.
        
    Returns:
        bool: True if the document was successfully cleaned and saved, False otherwise.
    """
    try:
        doc = Document(input_path)
        word_settings = settings.get('word_settings', {})
        
        # 1. Remove Images/Shapes
        if word_settings.get('remove_images', True):
            # Remove InlineShapes (Images embedded in text)
            # Note: python-docx doesn't provide a direct list of InlineShapes to remove,
            # so we must access the underlying XML.
            for shape in doc.inline_shapes:
                # To remove an inline shape, we must remove its parent element from the XML
                parent = shape._inline.getparent()
                if parent is not None:
                    parent.remove(shape._inline)
            
            # Remove Shapes (Floating images, text boxes, etc.)
            # These are stored in the document's 'shapes' collection in the XML
            # Accessing doc.element.body to find all CT_Shape elements
            for shape in doc.element.body.xpath('//wp:cNvSpc | //w:drawing'):
                # This is a broad stroke to find drawing elements that might be shapes
                # python-docx handles basic inline shapes, but floating shapes 
                # require lower-level XML manipulation.
                parent = shape.getparent()
                if parent is not None:
                    parent.remove(shape)

        # 2. Scrub Metadata
        if word_settings.get('remove_metadata', True):
            prop = doc.core_properties
            prop.author = ""
            prop.category = ""
            prop.comments = ""
            prop.content_status = ""
            prop.created = None # Note: Some versions of python-docx might not allow None
            prop.identifier = ""
            prop.keywords = ""
            prop.last_modified_by = ""
            prop.subject = ""
            prop.title = ""
            # created and modified dates are often read-only or handled by the OS/App,
            # but we set them to empty where the API allows.

        doc.save(output_path)
        logger.info(f"Successfully cleaned Word document: {input_path.name}")
        return True

    except Exception as e:
        logger.error(f"Failed to clean Word document {input_path}: {str(e)}")
        return False
