import customtkinter as ctk
from tkinter import filedialog, messagebox
import os, logging
from models.pdf_model import PdfFileModel
from services.pdf_service import PdfProcessor, PdfBatchProcessor
from threading import Thread
from config import PDFCONVERTER_DPI

class Pdf2ImagePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#2a2a2a")
        
        self.pdf_files = []  
        self.make_folder = True
        self.individual_processors = {}  
        self.current_batch_processor = None 
        self.is_batch_running = False
        
        self.file_rows = {}  
        self.footer_frame = None
        self.global_progress_bar = None
        self.global_progress_label = None
        
        self._build_ui()
    
    def _build_ui(self):
        self.create_header()
        self.create_controls()
        self.create_file_list_container()
        self.create_footer()
    
    # ==========================================
    # HEADER SECTION
    # ==========================================
    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="#1a73e8", height=100)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="📄 PDF to Image Converter",
            font=("Arial", 28, "bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=20)
        
        desc = ctk.CTkLabel(
            header_frame,
            text=f"Convert PDF pages to high-quality JPG images ({PDFCONVERTER_DPI} DPI)",
            font=("Arial", 13),
            text_color="#e3f2fd"
        )
        desc.pack(side="left", padx=(0, 30))
    
    # ==========================================
    # CONTROL SECTION
    # ==========================================
    def create_controls(self):
        control_frame = ctk.CTkFrame(self, fg_color="#333333", height=80)
        control_frame.pack(fill="x", padx=20, pady=(15, 0))
        control_frame.pack_propagate(False)
        
        upload_btn = ctk.CTkButton(
            control_frame,
            text="📁 Upload PDF Files",
            font=("Arial", 15, "bold"),
            fg_color="#1a73e8",
            hover_color="#1557b0",
            height=45,
            width=200,
            corner_radius=10,
            command=self.upload_pdf_files
        )
        upload_btn.pack(side="left", padx=20, pady=17)
        
        self.folder_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="📁 Create Folder for Each PDF",
            font=("Arial", 14),
            text_color="#ffffff",
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.toggle_folder_setting
        )
        self.folder_checkbox.select() 
        self.folder_checkbox.pack(side="left", padx=30)
        
        self.clear_all_btn = ctk.CTkButton(
            control_frame,
            text="🗑️ Clear All",
            font=("Arial", 14, "bold"),
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            height=40,
            width=120,
            corner_radius=8,
            command=self.clear_all_files
        )
    
    # ==========================================
    # FILE LIST SECTION
    # ==========================================
    def create_file_list_container(self):
        self.list_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.list_wrapper.pack(fill="both", expand=True, padx=20, pady=(15, 0))
        
        list_header = ctk.CTkFrame(self.list_wrapper, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 10))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📋 PDF Files Queue",
            font=("Arial", 16, "bold"),
            text_color="#ffffff"
        )
        list_title.pack(side="left")
        
        self.file_list_scroll = ctk.CTkScrollableFrame(
            self.list_wrapper,
            fg_color="#1f1f1f",
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666"
        )
        self.file_list_scroll.pack(fill="both", expand=True)
        
        self.empty_state = ctk.CTkFrame(self.file_list_scroll, fg_color="transparent")
        self.empty_state.pack(fill="both", expand=True, pady=50)
        
        ctk.CTkLabel(
            self.empty_state,
            text="📭",
            font=("Arial", 48)
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self.empty_state,
            text="No PDF files uploaded yet",
            font=("Arial", 16, "bold"),
            text_color="#666666"
        ).pack()
        
        ctk.CTkLabel(
            self.empty_state,
            text="Click 'Upload PDF Files' to get started",
            font=("Arial", 12),
            text_color="#888888"
        ).pack(pady=(5, 20))
    
    # ==========================================
    # FOOTER SECTION
    # ==========================================
    def create_footer(self):
        self.footer_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=80)
        
        self.global_progress_container = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.global_progress_container.pack(side="left", fill="x", expand=True, padx=20, pady=15)
        
        self.global_progress_label = ctk.CTkLabel(
            self.global_progress_container,
            text="Ready to process 0 files",
            font=("Arial", 13, "bold"),
            text_color="#ffffff"
        )
        self.global_progress_label.pack(anchor="w", pady=(0, 5))
        
        self.global_progress_bar = ctk.CTkProgressBar(
            self.global_progress_container,
            height=25,
            corner_radius=8,
            fg_color="#333333",
            progress_color="#1a73e8"
        )
        self.global_progress_bar.pack_forget()
        self.global_progress_bar.set(0)
        
        self.run_all_btn = ctk.CTkButton(
            self.footer_frame,
            text="▶️ Run All",
            font=("Arial", 16, "bold"),
            fg_color="#34a853",
            hover_color="#2d8e47",
            height=50,
            width=150,
            corner_radius=10,
            command=self.start_batch_processing
        )
        self.run_all_btn.pack(side="right", padx=20, pady=15)
    
    # ==========================================
    # EVENT HANDLERS
    # ==========================================
    def upload_pdf_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_paths:
            return
        
        self.update_idletasks()
        
        def _load_files():
            added_count = 0
            for path in file_paths:
                if any(pdf.file_path == path for pdf in self.pdf_files):
                    continue
                
                pdf_model = PdfFileModel(path)
                processor = PdfProcessor()
                total_pages = processor.get_pdf_info(path)
                
                if total_pages == 0:
                    self.after(0, lambda p=path: messagebox.showerror(
                        "Error", 
                        f"Failed to read PDF: {os.path.basename(p)}"
                    ))
                    continue
                
                pdf_model.total_pages = total_pages
                self.pdf_files.append(pdf_model)
                added_count += 1
            
            if added_count > 0:
                self.after(0, lambda: self.refresh_file_list())
                self.after(0, lambda: self.update_footer_visibility())
        
        Thread(target=_load_files, daemon=True).start()
    
    def toggle_folder_setting(self):
        self.make_folder = self.folder_checkbox.get()
    
    def clear_all_files(self):
        if not self.pdf_files:
            return
        
        if messagebox.askyesno("Confirm", f"Clear all {len(self.pdf_files)} PDF files?"):
            self.pdf_files.clear()
            self.file_rows.clear()
            self.refresh_file_list()
            self.update_footer_visibility()
    
    # ==========================================
    # UI UPDATE METHODS
    # ==========================================
    def refresh_file_list(self):
        for widget in self.file_list_scroll.winfo_children():
            if widget != self.empty_state:
                widget.destroy()
        
        self.file_rows.clear()
        
        if not self.pdf_files:
            try:
                if self.empty_state.winfo_exists():
                    self.empty_state.pack(fill="both", expand=True, pady=50)
            except:
                pass
            self.clear_all_btn.pack_forget()
        else:
            try:
                if self.empty_state.winfo_exists():
                    self.empty_state.pack_forget()
            except:
                pass
            
            self.clear_all_btn.pack(side="right", padx=20, pady=17)
            
            self.create_file_row(self.pdf_files)
                
    
    def update_footer_visibility(self):
        if self.pdf_files:
            if not self.footer_frame.winfo_ismapped():
                self.footer_frame.pack(fill="x", side="bottom", padx=20, pady=(0, 20))
            
            self.global_progress_label.configure(
                text=f"Ready to process {len(self.pdf_files)} files"
            )
            self.global_progress_bar.set(0)
        else:
            if self.footer_frame.winfo_ismapped():
                self.footer_frame.pack_forget()


    # ==========================================
    # FILE ROW CREATION
    # ==========================================
    def create_file_row(self, pdf_list):
        for index, pdf_model in enumerate(pdf_list):
            pdf_model: PdfFileModel

            row_frame = ctk.CTkFrame(
                self.file_list_scroll,
                fg_color="#2a2a2a" , 
                height=70
            )
            row_frame.pack(fill="x", padx=5, pady=3)
            row_frame.pack_propagate(False)
            
            row_frame.grid_columnconfigure(0, weight=0, minsize=50)   # No
            row_frame.grid_columnconfigure(1, weight=0, minsize=50)   # Icon
            row_frame.grid_columnconfigure(2, weight=1, minsize=200)  # Filename
            row_frame.grid_columnconfigure(3, weight=2, minsize=300)  # Progress
            row_frame.grid_columnconfigure(4, weight=0, minsize=120)  # Button
                        
            no_label = ctk.CTkLabel(
                row_frame,
                text=str(index + 1),
                font=("Arial", 14, "bold"),
                text_color="#888888"
            )
            no_label.grid(row=0, column=0, padx=10, sticky="w")
            
            icon_label = ctk.CTkLabel(
                row_frame,
                text="📄",
                font=("Arial", 24)
            )
            icon_label.grid(row=0, column=1, padx=5, sticky="w")
            
            filename = pdf_model.file_name
            if len(filename) > 20:
                display_name = filename[:20] + "..."
            else:
                display_name = filename
            
            name_label = ctk.CTkLabel(
                row_frame,
                text=display_name,
                font=("Arial", 13),
                text_color="#ffffff",
                anchor="w"
            )
            name_label.grid(row=0, column=2, padx=10, sticky="w")
            
            progress_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            progress_container.grid(row=0, column=3, padx=15, sticky="ew")
            
            progress_label = ctk.CTkLabel(
                progress_container,
                text="0%",
                font=("Arial", 12, "bold"),
                text_color="#1a73e8",
                width=50
            )
            progress_label.pack(side="left", padx=(0, 10))
            progress_label.pack_forget() 
            
            progress_bar = ctk.CTkProgressBar(
                progress_container,
                height=20,
                corner_radius=8,
                fg_color="#444444",
                progress_color="#1a73e8"
            )
            progress_bar.pack(side="left", fill="x", expand=True)
            progress_bar.set(0)
            progress_bar.pack_forget()  
            
            status_label = ctk.CTkLabel(
                progress_container,
                text=f"Ready • {pdf_model.total_pages} pages",
                font=("Arial", 12),
                text_color="#888888"
            )
            status_label.pack(side="left", fill="x", expand=True)
            
            run_btn = ctk.CTkButton(
                row_frame,
                text="▶️ Run",
                font=("Arial", 13, "bold"),
                fg_color="#34a853",
                hover_color="#2d8e47",
                height=40,
                width=100,
                corner_radius=8,
                command=lambda idx=index, p=pdf_model: self.start_single_processing(idx,p)
            )
            run_btn.grid(row=0, column=4, padx=10)
            
            
            pdf_model._index = index
            pdf_model._progress_bar = progress_bar
            pdf_model._progress_label = progress_label
            pdf_model._status_label = status_label
            pdf_model._run_btn = run_btn
            
            self.file_rows[pdf_model.file_id] = row_frame
    
    # ==========================================
    # INDIVIDUAL FILE PROCESSING
    # ==========================================
    
    def start_single_processing(self, index: int, pdf_model: PdfFileModel):
        self.global_progress_bar.pack_forget()
        self.global_progress_label.configure(
            text=f"Ready to process {len(self.pdf_files)} files"
        )
                
        pdf_model._status_label.pack_forget()
        pdf_model._progress_label.pack(side="left", padx=(0, 10))
        pdf_model._progress_bar.pack(side="left", fill="x", expand=True)
        pdf_model._progress_bar.set(0)
        pdf_model._run_btn.configure(text="⏳ Running...", fg_color="#666666",state="disabled")
        
        processor = PdfProcessor()
        def process_thread():
            try:
                def on_single_status(pdf_model, status, progress=None):
                    match status:
                        case s if 'running' in s:
                            self.after(0, lambda mod=pdf_model, prog=progress: self._update_row_progress(mod, prog))
                            
                        case s if 'completed' in s:
                            self.after(0, lambda mod=pdf_model: self._on_row_completed(mod))

                        case s if 'error' in s:
                            self.after(0, lambda mod=pdf_model: self._on_row_error(mod))                 

                processor.process_pdf(pdf_model, self.make_folder, on_single_status)
            except Exception as e:
                logging.exception(f"[ERROR] [Single PDF Handler] ->\n{e}")
                self.after(0, lambda id=pdf_model.file_id: self._on_row_error(id))
            
        Thread(target=process_thread, daemon=True).start()
    
    def _update_row_progress(self, model: PdfFileModel, progress):
        for pdf_model in self.pdf_files:
            pdf_model: PdfFileModel
            if model.file_id == pdf_model.file_id:
                if progress >= 100:
                    model._progress_bar.configure(progress_color="#4caf50")  # Green
                    model._progress_label.configure(text_color="#4caf50")
                elif progress >= 50:
                    model._progress_bar.configure(progress_color="#2196f3")  # Blue
                else:
                    model._progress_bar.configure(progress_color="#ff9800")  # Orange
                    
                model._progress_bar.set(progress/100)
                model._progress_label.configure(text=f"{int(progress)}%")
                break
        
    def _on_row_completed(self, model):
        model._progress_bar.configure(progress_color="#34a853")
        model._progress_bar.set(1.0)
        model._run_btn.configure(state="normal",fg_color="#34a853",text="▶️ Run")
 
    def _on_row_error(self, model):
        model._progress_bar.configure(progress_color="#d32f2f")
 
        # ==========================================
        # BATCH PROCESSING (RUN ALL)
        # ==========================================
   
    def start_batch_processing(self):
        if not self.pdf_files:
            messagebox.showinfo("Info", "No PDF files to process")
            return
        
        self.run_all_btn.configure(
            text="⏸❌ Cancel",
            fg_color="#ff0000",
            hover_color="#f50000",
            command=self.cancel_batch_processing
        )
        
        self.global_progress_label.configure(
            text=f"Processing 0/{len(self.pdf_files)} files (0%)"
        )
        self.global_progress_bar.pack(fill="x")
        self.global_progress_bar.set(0)
        
        for pdf_model in self.pdf_files:                                    
            pdf_model._progress_label.configure(text=f"0%")
            pdf_model._progress_label.pack(side="left", padx=(0, 10))
            pdf_model._progress_bar.configure(progress_color="#484848")
            pdf_model._progress_label.configure(text_color="#1a73e8")
            pdf_model._progress_bar.pack(side="left", fill="x", expand=True)
            pdf_model._progress_bar.set(0)
            pdf_model._status_label.destroy()
            pdf_model._run_btn.configure(text="⏳ Running...", fg_color="#666666",state="disabled")
        
        self.current_batch_processor = PdfBatchProcessor() 
        self.is_batch_running = True
        def process_thread():
            try:
                progress_map = {f.file_id: 0 for f in self.pdf_files}
                completed_count = 0
                total_files = len(self.pdf_files)
                def on_single_status(model, status, progress=None):
                    nonlocal completed_count
                    match status:
                        case s if 'running' in s:
                            progress_map[model] = progress
                        
                            self.after(0, lambda mod=model, prog=progress: self._update_row_progress(mod, prog))
                            
                            total_progress = sum(progress_map.values())
                            avg_progress = total_progress / (total_files * 100)  
                            self.after(0, lambda avg=avg_progress: self._on_global_progress(completed_count, total_files, avg))

                        case s if 'completed' in s:
                            completed_count += 1
                            progress_map[model] = 100  
                            
                            self.after(0, lambda mod=model: self._on_row_completed(mod))
                            
                            avg_progress = sum(progress_map.values()) / (total_files * 100)
                            self.after(0, lambda avg=avg_progress: self._on_global_progress(completed_count, total_files, avg))
                        
                        case s if 'cancelled' in s:
                            self.after(0, lambda mod=pdf_model: self._on_row_cancelled(mod))
                            
                        case s if 'error' in s:
                            self.after(0,lambda mod=model: self._on_row_error(mod))
                
                def on_global_status(status):
                    match status:
                        case s if 'completed' in s:
                            self.after(0, lambda: self._on_global_progress(completed_count, total_files, 1.0))
                            self.after(300, lambda: self._on_global_completed())

                        case s if 'error' in s:
                            self.after(0, lambda: self._on_global_error())
                        
                        case s if 'cancelled' in s:
                            self.after(0, lambda: self._on_global_cancelled())
                
                self.current_batch_processor.process_all(
                    self.pdf_files,
                    self.make_folder,
                    on_single_status,
                    on_global_status
                )
                
            except Exception as e:
                logging.exception(f"[ERROR] [Batch PDF Handler] ->\n{e}")
                self.after(0, lambda: self._on_global_error())
                
        thread = Thread(target=process_thread, daemon=True)
        thread.start()
        
    def cancel_batch_processing(self):
        if not self.is_batch_running or not self.current_batch_processor:
            return
        
        self.current_batch_processor.cancel()
        
        if self.current_batch_processor:
            if not self.current_batch_processor.cleaned:
                self.current_batch_processor.cleanup_converted_files()
        
        for pdf_model in self.pdf_files:
            if hasattr(pdf_model, '_progress_bar'):
                current_progress = pdf_model._progress_bar.get()
                if current_progress < 1.0:  
                    self._on_row_cancelled(pdf_model)
        
        self.is_batch_running = False
        
        self.global_progress_bar.configure(progress_color="#d32f2f")
        self.global_progress_label.configure(text="❌ Batch cancelled - Converted files deleted")
        
        self.run_all_btn.configure(
            text="▶️ Run All",
            fg_color="#34a853",
            hover_color="#2d8e47",
            command=self.start_batch_processing,
            state="normal"
        )

    def _on_row_cancelled(self, model: PdfFileModel):
        model._progress_bar.configure(progress_color="#d32f2f")  # Red
        model._progress_label.configure(text_color="#d32f2f")
        
        if hasattr(model, '_run_btn'):
            model._run_btn.configure(
                state="normal",
                fg_color="#34a853",
                text="▶️ Run"
            )

    def _on_global_cancelled(self):
        self.is_batch_running = False
        
        if self.current_batch_processor:
            if not self.current_batch_processor.cleaned:
                self.current_batch_processor.cleanup_converted_files()
        
        self.global_progress_bar.configure(progress_color="#d32f2f")
        self.global_progress_label.configure(text="❌ Batch cancelled - Files cleaned up")
        
        self.run_all_btn.configure(
            text="▶️ Run All",
            fg_color="#34a853",
            hover_color="#2d8e47",
            command=self.start_batch_processing,
            state="normal"
        )
        
        for pdf_model in self.pdf_files:
            if hasattr(pdf_model, '_progress_bar'):
                if pdf_model._progress_bar.get() < 1.0:
                    self._on_row_cancelled(pdf_model)
   
    # Handler Global Progress 
    def _on_global_progress(self, completed: int, total: int, progress: float):
        if progress * 100 >= 100:
            self.global_progress_bar.configure(progress_color="#4caf50")  # Green
        elif progress * 100 >= 50:
            self.global_progress_bar.configure(progress_color="#2196f3")  # Blue
        else:
            self.global_progress_bar.configure(progress_color="#ff9800")
        self.global_progress_bar.set(progress)
        
        remaining = total - completed
        
        if remaining > 0:
            self.global_progress_label.configure(
                text=f"Processing {completed}/{total} files ({int(progress * 100)}%) • {remaining} remaining"
            )
        else:
            self.global_progress_label.configure(
                text=f"Completed {completed}/{total} files (100%)"
            )
    
    def _on_global_completed(self):
        self.is_batch_running = False 
        self.global_progress_bar.set(1.0)
        self.global_progress_bar.configure(progress_color="#34a853")
        
        completed = len(self.pdf_files)
        status_text = f"✓ {completed} completed"
     
        self.global_progress_label.configure(text=status_text)
        
        self.run_all_btn.configure(
            text="▶️ Run All",
            fg_color="#34a853",
            hover_color="#2d8e47",
            command=self.start_batch_processing  
        )
        
        self.is_batch_running = False
    
    def _on_global_error(self):
        self.is_batch_running = False 
    
        if self.current_batch_processor:
            if not self.current_batch_processor.cleaned:
                self.current_batch_processor.cleanup_converted_files()
        
        self.global_progress_bar.configure(progress_color="#d32f2f")
        self.global_progress_label.configure(text="❌ Error - Converted files deleted")
        
        self.run_all_btn.configure(
            text="▶️ Run All",
            fg_color="#34a853",
            hover_color="#2d8e47",
            command=self.start_batch_processing,
            state="normal"
        )