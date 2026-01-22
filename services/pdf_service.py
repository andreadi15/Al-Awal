# =======================
# FILE: services/pdf_service.py
# =======================

import os, sys, time, logging
import threading
from typing import Optional
from config import PDFCONVERTER_DPI

    
def setup_dependencies():
    """Auto-install PyMuPDF if not available"""
    try:
        import fitz 
        logging.error("[PDF Service] PyMuPDF already installed ✓")
    except ImportError:
        logging.error("[PDF Service] PyMuPDF not found. Installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
            logging.error("[PDF Service] PyMuPDF installation complete ✓")
        except subprocess.CalledProcessError as e:
            logging.error(f"[PDF Service] Failed to install PyMuPDF: {e}")
            raise RuntimeError("Failed to install required dependency: PyMuPDF")

setup_dependencies()

import fitz
from models.pdf_model import PdfFileModel

# ptocess PDF Single
class PdfProcessor:    
    def __init__(self):
        self.is_cancelled = False
        self.is_running = False
        self.is_paused = False
        self.current_thread: Optional[threading.Thread] = None
    
    def get_pdf_info(self, pdf_path: str) -> int:
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            return total_pages
        except Exception as e:
            logging.error(f"[ERROR] Failed to get PDF info: {e}")
            return 0
    
    def process_pdf(
        self, 
        pdf_model: PdfFileModel, 
        make_folder: bool,
        progress_callback=None,
    ):
        try:
            pdf_path = pdf_model.file_path
            base_name = os.path.basename(pdf_path).replace(".pdf", "")
            pdf_dir = os.path.dirname(pdf_path)
            
            if make_folder:
                output_dir = os.path.join(pdf_dir, base_name)
                os.makedirs(output_dir, exist_ok=True)
            else:
                output_dir = pdf_dir
            
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            pdf_model.total_pages = total_pages
            
            for page_num in range(total_pages):               
                if self.is_cancelled:
                    doc.close()
                    progress_callback(pdf_model, 'cancelled')
                    return False
                
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=int(PDFCONVERTER_DPI))
                
                output_filename = f"{base_name} - page {page_num + 1}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                pix.save(output_path)
                percent = ((page_num + 1) / total_pages) * 100
                progress_callback(pdf_model, 'running', percent)
                time.sleep(0.02)
            
            output_dir_info = {
                'output_dir': output_dir,
                'make_folder': make_folder,
                'base_name': base_name
            }
            pdf_model._conversion_info = output_dir_info
            
            doc.close()
            progress_callback(pdf_model, 'completed')
            return True
            
        except Exception as e:
            progress_callback(pdf_model, 'error')
            logging.error(f"[ERROR] [Single PDF Process] -> {str(e)}")
            return False
        
class PdfBatchProcessor:
    def __init__(self):
        self.processor = PdfProcessor()
        self.is_cancelled = False
        self.cleaned = False
        self.converted_files = []
        
    def process_all(
        self,
        pdf_models: list[PdfFileModel],
        make_folder: bool,
        single_callback,  
        global_callback
    ):
        self.cleaned = False
        self.converted_files.clear()
 
        for pdf_model in pdf_models:
            if self.is_cancelled:
                global_callback('cancelled')
                return

            self.processor.is_cancelled = False
            
            self.converted_files.append({
                'model': pdf_model,
                'make_folder': make_folder
            })
                
            result = self.processor.process_pdf(pdf_model, make_folder, single_callback)
            
            if not result:
                if global_callback:
                    global_callback('error')
                return
        
        
        global_callback('completed')
    
    def cancel(self):
        self.is_cancelled = True
        self.processor.is_cancelled = True
        
    def reset(self):
        self.is_cancelled = False
        self.processor.is_cancelled = False
        self.converted_files.clear()

    def cleanup_converted_files(self):
        import shutil
        
        deleted_count = 0
        for item in self.converted_files:
            try:
                pdf_model = item['model']
                make_folder = item['make_folder']
                
                pdf_path = pdf_model.file_path
                base_name = os.path.basename(pdf_path).replace(".pdf", "")
                pdf_dir = os.path.dirname(pdf_path)
                
                if make_folder:
                    output_dir = os.path.join(pdf_dir, base_name)
                    if os.path.exists(output_dir) and os.path.isdir(output_dir):
                        shutil.rmtree(output_dir)
                        deleted_count += 1
                else:
                    base_name = os.path.basename(pdf_model.file_path).replace(".pdf", "")
                    pdf_dir = os.path.dirname(pdf_model.file_path)
                    
                    for file in os.listdir(pdf_dir):
                        if file.startswith(base_name) and file.endswith(".jpg"):
                            file_path = os.path.join(pdf_dir, file)
                            os.remove(file_path)
                            deleted_count += 1
            
            except Exception as e:
                logging.error(f"[CLEANUP] Error deleting: {e}")
        
        self.converted_files.clear()
        self.cleaned = True