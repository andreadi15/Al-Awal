# =======================
# FILE: services/pdf_service.py
# =======================

import os, sys, time, logging
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
        self.is_cancelled = False
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
        progress_callback=None,
    ):
        """
        Process single PDF file (run in thread)
        
        Args:
            pdf_model: PdfFileModel instance
            make_folder: True = create folder, False = save alongside PDF
            progress_callback: Called on each page (current_page, total_pages)
            completion_callback: Called when done (success: bool, message: str)
        """
        
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
                # if self.is_paused:
                #     doc.close()
                #     progress_callback(pdf_model.file_id, 'error', "Paused by user")
                #     return
                
                if self.is_cancelled:
                    doc.close()
                    progress_callback(pdf_model, 'cancelled')
                    return False
                
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=200)
                
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
        
        # self.is_running = True
        # self.is_paused = False
    
    # def cancel(self):
    #     """Cancel current processing"""
    #     self.is_cancelled = True
    
    # def pause(self):
    #     """Pause current processing"""
    #     self.is_paused = True
    #     self.is_running = False
    
    # def resume(self):
    #     """Resume processing (not implemented - would need state saving)"""
    #     self.is_paused = False
    
    # def stop(self):
    #     """Stop current processing"""
    #     self.is_paused = True
    #     self.is_running = False
    #     if self.current_thread and self.current_thread.is_alive():
    #         # Thread will stop on next page check
    #         pass


class PdfBatchProcessor:
    """Service untuk process multiple PDFs"""
    
    def __init__(self):
        # self.is_running = False
        # self.is_paused = False
        # self.current_index = 0
        # self.processors = {} 
        self.processor = PdfProcessor()
        self.is_cancelled = False
        self.converted_files = []
        
    def process_all(
        self,
        pdf_models: list[PdfFileModel],
        make_folder: bool,
        single_callback,  
        global_callback
    ):
        self.converted_files.clear()
        # def _process_next(index: int):
        #     if index >= len(pdf_models) or self.is_paused:
        #         success_count = sum(1 for p in pdf_models if p.status == "completed")
        #         completion_callback(success_count, len(pdf_models))
        #         self.is_running = False
        #         return
            
        #     pdf_model = pdf_models[index]
            
        #     self.processors[index] = processor
            
        #     def on_complete(success, message):
        #         if success:
        #             pdf_model.set_completed()
        #         else:
        #             if "Paused" in message:
        #                 pdf_model.status = "paused"
        #             else:
        #                 pdf_model.set_error(message)
                
        #         completed = sum(1 for p in pdf_models[:index+1] if p.status in ["completed", "paused", "error"])
        #         global_progress_callback(completed, len(pdf_models))
                
        #         _process_next(index + 1)
            
        #     pdf_model.status = "processing"

        # for idx, pdf_model in enumerate(pdf_models,start=1):
        for pdf_model in pdf_models:
            if self.is_cancelled:
                global_callback('cancelled')
                return

            self.processor.is_cancelled = False
            
            result = self.processor.process_pdf(pdf_model, make_folder, single_callback)
            
            if not result:
                if global_callback:
                    global_callback('error')
                return
        
        self.converted_files.append({
            'model': pdf_model,
            'make_folder': make_folder
        })
        global_callback('completed')
        
        # self.is_running = True
        # self.is_paused = False
        # self.current_index = 0
        # _process_next(0)
    
    def cancel(self):
        """Cancel batch processing"""
        self.is_cancelled = True
        self.processor.is_cancelled = True
        
    def reset(self):
        """Reset flags"""
        self.is_cancelled = False
        self.processor.is_cancelled = False
        self.converted_files.clear()

    def cleanup_converted_files(self):
        """Delete all converted files/folders from this batch"""
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
                    # Delete entire folder
                    if os.path.exists(output_dir) and os.path.isdir(output_dir):
                        shutil.rmtree(output_dir)
                        deleted_count += 1
                        print(f"[CLEANUP] Deleted folder: {output_dir}")
                else:
                    # Delete individual image files
                    base_name = os.path.basename(pdf_model.file_path).replace(".pdf", "")
                    pdf_dir = os.path.dirname(pdf_model.file_path)
                    
                    for file in os.listdir(pdf_dir):
                        if file.startswith(base_name) and file.endswith(".jpg"):
                            file_path = os.path.join(pdf_dir, file)
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"[CLEANUP] Deleted file: {file_path}")
            
            except Exception as e:
                logging.error(f"[CLEANUP] Error deleting: {e}")
        
        print(f"[CLEANUP] Total deleted: {deleted_count} items")
        self.converted_files.clear()
        
    # def pause_all(self):
    #     """Pause all processing"""
    #     self.is_paused = True
    #     for processor in self.processors.values():
    #         processor.pause()
    
    # def stop_all(self):
    #     """Stop all processing"""
    #     self.is_paused = True
    #     self.is_running = False
    #     for processor in self.processors.values():
    #         processor.stop()