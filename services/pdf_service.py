# =======================
# FILE: services/pdf_service.py
# =======================

import os, sys
import threading
from typing import Callable, Optional

    
def setup_dependencies():
    """Auto-install PyMuPDF if not available"""
    try:
        import fitz 
        print("[PDF Service] PyMuPDF already installed ✓")
    except ImportError:
        print("[PDF Service] PyMuPDF not found. Installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
            print("[PDF Service] PyMuPDF installation complete ✓")
        except subprocess.CalledProcessError as e:
            print(f"[PDF Service] Failed to install PyMuPDF: {e}")
            raise RuntimeError("Failed to install required dependency: PyMuPDF")

setup_dependencies()

import fitz
from models.pdf_model import PdfFileModel


class PdfProcessor:
    """Service untuk convert PDF to Images dengan threading support"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.current_thread: Optional[threading.Thread] = None
    
    def get_pdf_info(self, pdf_path: str) -> int:
        """Get total pages dari PDF file"""
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            return total_pages
        except Exception as e:
            print(f"[ERROR] Failed to get PDF info: {e}")
            return 0
    
    def process_pdf(
        self, 
        pdf_model: PdfFileModel, 
        make_folder: bool,
        progress_callback: Callable[[int, int], None],
        completion_callback: Callable[[bool, str], None]
    ):
        """
        Process single PDF file (run in thread)
        
        Args:
            pdf_model: PdfFileModel instance
            make_folder: True = create folder, False = save alongside PDF
            progress_callback: Called on each page (current_page, total_pages)
            completion_callback: Called when done (success: bool, message: str)
        """
        
        def _process():
            try:
                pdf_path = pdf_model.file_path
                base_name = os.path.basename(pdf_path).replace(".pdf", "")
                pdf_dir = os.path.dirname(pdf_path)
                
                # Determine output directory
                if make_folder:
                    output_dir = os.path.join(pdf_dir, base_name)
                    os.makedirs(output_dir, exist_ok=True)
                else:
                    output_dir = pdf_dir
                
                # Open PDF
                doc = fitz.open(pdf_path)
                total_pages = len(doc)
                pdf_model.total_pages = total_pages
                
                # Process each page
                for page_num in range(total_pages):
                    # Check if paused
                    if self.is_paused:
                        doc.close()
                        completion_callback(False, "Paused by user")
                        return
                    
                    # Load and convert page
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=200)
                    
                    # Save image
                    output_filename = f"{base_name} - page {page_num + 1}.jpg"
                    output_path = os.path.join(output_dir, output_filename)
                    pix.save(output_path)
                    
                    # Update progress
                    progress_callback(page_num + 1, total_pages)
                
                doc.close()
                completion_callback(True, f"Successfully converted {total_pages} pages")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                completion_callback(False, error_msg)
        
        # Run in thread
        self.is_running = True
        self.is_paused = False
        self.current_thread = threading.Thread(target=_process, daemon=True)
        self.current_thread.start()
    
    def pause(self):
        """Pause current processing"""
        self.is_paused = True
        self.is_running = False
    
    def resume(self):
        """Resume processing (not implemented - would need state saving)"""
        self.is_paused = False
    
    def stop(self):
        """Stop current processing"""
        self.is_paused = True
        self.is_running = False
        if self.current_thread and self.current_thread.is_alive():
            # Thread will stop on next page check
            pass


class PdfBatchProcessor:
    """Service untuk process multiple PDFs"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.current_index = 0
        self.processors = {} 
        
    def process_all(
        self,
        pdf_models: list[PdfFileModel],
        make_folder: bool,
        file_progress_callback: Callable[[int, int, int], None],  # (file_index, current_page, total_pages)
        global_progress_callback: Callable[[int, int], None],  # (completed_files, total_files)
        completion_callback: Callable[[int, int], None]  # (success_count, total_count)
    ):
        """
        Process all PDFs sequentially
        
        Args:
            pdf_models: List of PdfFileModel
            make_folder: Folder creation setting
            file_progress_callback: Per-file progress update
            global_progress_callback: Global progress update
            completion_callback: All files done
        """
        
        def _process_next(index: int):
            if index >= len(pdf_models) or self.is_paused:
                # All done or paused
                success_count = sum(1 for p in pdf_models if p.status == "completed")
                completion_callback(success_count, len(pdf_models))
                self.is_running = False
                return
            
            pdf_model = pdf_models[index]
            processor = PdfProcessor()
            self.processors[index] = processor
            
            def on_progress(current_page, total_pages):
                file_progress_callback(index, current_page, total_pages)
            
            def on_complete(success, message):
                if success:
                    pdf_model.set_completed()
                else:
                    if "Paused" in message:
                        pdf_model.status = "paused"
                    else:
                        pdf_model.set_error(message)
                
                # Update global progress
                completed = sum(1 for p in pdf_models[:index+1] if p.status in ["completed", "paused", "error"])
                global_progress_callback(completed, len(pdf_models))
                
                _process_next(index + 1)
            
            pdf_model.status = "processing"
            processor.process_pdf(pdf_model, make_folder, on_progress, on_complete)
        
        self.is_running = True
        self.is_paused = False
        self.current_index = 0
        _process_next(0)
    
    def pause_all(self):
        """Pause all processing"""
        self.is_paused = True
        for processor in self.processors.values():
            processor.pause()
    
    def stop_all(self):
        """Stop all processing"""
        self.is_paused = True
        self.is_running = False
        for processor in self.processors.values():
            processor.stop()