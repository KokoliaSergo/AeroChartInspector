import os
import pymupdf

class PDFLoader:
    @staticmethod
    def validate_and_load(file_path: str):
        if not file_path or not os.path.exists(file_path):
            return False, None, "File does not exist."
        
        try:
            doc = pymupdf.open(file_path)
        except Exception as e:
            return False, None, f"Unable to open PDF: {str(e)}"
        
        if doc.page_count != 1:
            doc.close()
            return False, None, "Version 1 supports one-page PDF charts only."
            
        return True, doc, ""