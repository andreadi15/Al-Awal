# =======================
# FILE: pages/pdf2image.py
# =======================

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
        
        # State
        self.pdf_files = []  # List[PdfFileModel]
        self.make_folder = True
        self.individual_processors = {}  # {index: PdfProcessor}
        self.current_batch_processor = None  # ✅ TAMBAH INI - Track batch processor
        self.is_batch_running = False
        
        # UI Components (will be created)
        self.file_rows = {}  # List of row widgets
        self.footer_frame = None
        self.global_progress_bar = None
        self.global_progress_label = None
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build complete UI structure"""
        self.create_header()
        self.create_controls()
        self.create_file_list_container()
        self.create_footer()
    
    # ==========================================
    # HEADER SECTION
    # ==========================================
    def create_header(self):
        """Create header with title and description"""
        header_frame = ctk.CTkFrame(self, fg_color="#1a73e8", height=100)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="📄 PDF to Image Converter",
            font=("Arial", 28, "bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=20)
        
        # Description
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
        """Create upload button and settings"""
        control_frame = ctk.CTkFrame(self, fg_color="#333333", height=80)
        control_frame.pack(fill="x", padx=20, pady=(15, 0))
        control_frame.pack_propagate(False)
        
        # Left side - Upload button
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
        
        # Center - Checkbox for folder creation
        self.folder_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="📁 Create Folder for Each PDF",
            font=("Arial", 14),
            text_color="#ffffff",
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.toggle_folder_setting
        )
        self.folder_checkbox.select()  # Default checked
        self.folder_checkbox.pack(side="left", padx=30)
        
        # Right side - Clear all button (hidden by default)
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
        # Will pack when files are added
    
    # ==========================================
    # FILE LIST SECTION
    # ==========================================
    def create_file_list_container(self):
        """Create scrollable container for file list"""
        # Container wrapper
        self.list_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.list_wrapper.pack(fill="both", expand=True, padx=20, pady=(15, 0))
        
        # Header
        list_header = ctk.CTkFrame(self.list_wrapper, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 10))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📋 PDF Files Queue",
            font=("Arial", 16, "bold"),
            text_color="#ffffff"
        )
        list_title.pack(side="left")
        
        # Scrollable frame for files
        self.file_list_scroll = ctk.CTkScrollableFrame(
            self.list_wrapper,
            fg_color="#1f1f1f",
            scrollbar_button_color="#888888",
            scrollbar_button_hover_color="#666666"
        )
        self.file_list_scroll.pack(fill="both", expand=True)
        
        # Empty state
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
        """Create footer with global progress and run all button"""
        self.footer_frame = ctk.CTkFrame(self, fg_color="#1f1f1f", height=80)
        # Will pack when files are added
        
        # Global progress container
        self.global_progress_container = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.global_progress_container.pack(side="left", fill="x", expand=True, padx=20, pady=15)
        
        # Progress label
        self.global_progress_label = ctk.CTkLabel(
            self.global_progress_container,
            text="Ready to process 0 files",
            font=("Arial", 13, "bold"),
            text_color="#ffffff"
        )
        self.global_progress_label.pack(anchor="w", pady=(0, 5))
        
        # Progress bar
        self.global_progress_bar = ctk.CTkProgressBar(
            self.global_progress_container,
            height=25,
            corner_radius=8,
            fg_color="#333333",
            progress_color="#1a73e8"
        )
        self.global_progress_bar.pack_forget()
        self.global_progress_bar.set(0)
        
        # Run All / Pause All button
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
        """Open file dialog and add PDF files to list"""
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_paths:
            return
        
        # Show loading indicator
        self.update_idletasks()
        
        def _load_files():
            added_count = 0
            for path in file_paths:
                # Check duplicate
                if any(pdf.file_path == path for pdf in self.pdf_files):
                    continue
                
                # Create model and get info
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
            
            # Update UI in main thread
            if added_count > 0:
                self.after(0, lambda: self.refresh_file_list())
                self.after(0, lambda: self.update_footer_visibility())
        
        # Run in thread
        Thread(target=_load_files, daemon=True).start()
    
    def toggle_folder_setting(self):
        """Toggle folder creation setting"""
        self.make_folder = self.folder_checkbox.get()
        print(f"[PDF2IMG] Folder creation: {self.make_folder}")
    
    def clear_all_files(self):
        """Clear all files from list"""
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
        """Refresh the file list display"""
        # Clear existing rows
        for widget in self.file_list_scroll.winfo_children():
            if widget != self.empty_state:
                widget.destroy()
        
        self.file_rows.clear()
        
        # Show empty state or file rows
        if not self.pdf_files:
            # Show empty state
            try:
                if self.empty_state.winfo_exists():
                    self.empty_state.pack(fill="both", expand=True, pady=50)
            except:
                pass
            self.clear_all_btn.pack_forget()
        else:
            # Hide empty state
            try:
                if self.empty_state.winfo_exists():
                    self.empty_state.pack_forget()
            except:
                pass
            
            # Show clear all button
            self.clear_all_btn.pack(side="right", padx=20, pady=17)
            
            # Create rows
            self.create_file_row(self.pdf_files)
                
    
    def update_footer_visibility(self):
        """Show/hide footer based on file count"""
        if self.pdf_files:
            if not self.footer_frame.winfo_ismapped():
                self.footer_frame.pack(fill="x", side="bottom", padx=20, pady=(0, 20))
            
            # Update label
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
        """
        Create single file row with all components
        
        Row structure:
        [No] [Icon] [Filename] [Progress Bar + %] [Run/Pause Button]
        """
        for index, pdf_model in enumerate(pdf_list):
            pdf_model: PdfFileModel

            row_frame = ctk.CTkFrame(
                self.file_list_scroll,
                fg_color="#2a2a2a" , #if index % 2 == 0 else "#333333"
                height=70
            )
            row_frame.pack(fill="x", padx=5, pady=3)
            row_frame.pack_propagate(False)
            
            # Configure grid
            row_frame.grid_columnconfigure(0, weight=0, minsize=50)   # No
            row_frame.grid_columnconfigure(1, weight=0, minsize=50)   # Icon
            row_frame.grid_columnconfigure(2, weight=1, minsize=200)  # Filename
            row_frame.grid_columnconfigure(3, weight=2, minsize=300)  # Progress
            row_frame.grid_columnconfigure(4, weight=0, minsize=120)  # Button
                        
            # Column 0: Number
            no_label = ctk.CTkLabel(
                row_frame,
                text=str(index + 1),
                font=("Arial", 14, "bold"),
                text_color="#888888"
            )
            no_label.grid(row=0, column=0, padx=10, sticky="w")
            
            # Column 1: PDF Icon
            icon_label = ctk.CTkLabel(
                row_frame,
                text="📄",
                font=("Arial", 24)
            )
            icon_label.grid(row=0, column=1, padx=5, sticky="w")
            
            # Column 2: Filename (truncated)
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
            
            # Column 3: Progress container
            progress_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            progress_container.grid(row=0, column=3, padx=15, sticky="ew")
            
            # Progress percentage label (hidden initially)
            progress_label = ctk.CTkLabel(
                progress_container,
                text="0%",
                font=("Arial", 12, "bold"),
                text_color="#1a73e8",
                width=50
            )
            progress_label.pack(side="left", padx=(0, 10))
            progress_label.pack_forget()  # Hide initially
            
            # Progress bar (hidden initially)
            progress_bar = ctk.CTkProgressBar(
                progress_container,
                height=20,
                corner_radius=8,
                fg_color="#444444",
                progress_color="#1a73e8"
            )
            progress_bar.pack(side="left", fill="x", expand=True)
            progress_bar.set(0)
            progress_bar.pack_forget()  # Hide initially
            
            # Status label (shown initially)
            status_label = ctk.CTkLabel(
                progress_container,
                text=f"Ready • {pdf_model.total_pages} pages",
                font=("Arial", 12),
                text_color="#888888"
            )
            status_label.pack(side="left", fill="x", expand=True)
            
            # Column 4: Action button
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
            
            # Store references
            
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
        """Start processing single file"""
        # row_widget = self.file_rows[pdf_model.file_id]
        self.global_progress_bar.pack_forget()
        self.global_progress_label.configure(
            text=f"Ready to process {len(self.pdf_files)} files"
        )
        
        index = next((i for i, f in enumerate(self.pdf_files) if f.file_id == pdf_model.file_id),None)
        
        print(f"[DEBUG] Starting processing for index {index + 1}")
        print(f"[DEBUG] File path: {pdf_model.file_path}")
        print(f"[DEBUG] Total pages: {pdf_model.total_pages}")
        
        # Update UI - show progress bar
        pdf_model._status_label.pack_forget()
        pdf_model._progress_label.pack(side="left", padx=(0, 10))
        pdf_model._progress_bar.pack(side="left", fill="x", expand=True)
        pdf_model._progress_bar.set(0)
        pdf_model._run_btn.configure(text="⏳ Running...", fg_color="#666666",state="disabled")
        
        print("asasasasas")
        # Create processor
        processor = PdfProcessor()
        # self.individual_processors[pdf_model.file_id] = processor
        # self.individual_processors[index] = processor
        print("accccc")
        # Define callbacks
        def process_thread():
            try:
                def on_single_status(pdf_model, status, progress=None):
                    match status:
                        case s if 'running' in s:
                            # self.after(0, pdf_model.update_progress(progress))                    
                            self.after(0, lambda mod=pdf_model, prog=progress: self._update_row_progress(mod, prog))
                            
                        case s if 'completed' in s:
                            # pdf_model.set_completed()
                            self.after(0, lambda mod=pdf_model: self._on_row_completed(mod))

                        case s if 'error' in s:
                            # pdf_model.set_error(message)
                            self.after(0, lambda mod=pdf_model: self._on_row_error(mod))                 
                
                # Start processing
                # pdf_model.status = "processing"
                processor.process_pdf(pdf_model, self.make_folder, on_single_status)
            except Exception as e:
                logging.exception(f"[ERROR] [Single PDF Handler] ->\n{e}")
                self.after(0, lambda id=pdf_model.file_id: self._on_row_error(id))
            
        Thread(target=process_thread, daemon=True).start()
    
    # def pause_single_file(self, index: int):
    #     """Pause single file processing"""
    #     pdf_model = self.pdf_files[index]
    #     processor = self.individual_processors.get(index)
        
    #     if processor:
    #         processor.pause()
    #         pdf_model.status = "paused"
    
    def _update_row_progress(self, model: PdfFileModel, progress):
        """Update row progress bar and label"""
        # if index >= len(self.file_rows):
        #     return
        # pdf_model = next(p for p in self.pdf_files if p.file_id == file_id)
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
        """Handle file completion"""
        # if file_id >= len(self.file_rows):
        #     return
        
        # pdf_model = next(p for p in self.pdf_files if p.file_id == file_id)
        # pdf_model = self.pdf_files[file_id]
        
        # Update UI
        model._progress_bar.configure(progress_color="#34a853")
        model._progress_bar.set(1.0)
        model._run_btn.configure(state="normal",fg_color="#34a853",text="▶️ Run")
        # row_widget._progress_label.configure(text="✓ 100%", text_color="#34a853")
        # row_widget._action_btn.configure(
        #     text="✓ Done",
        #     fg_color="#555555",
        #     state="disabled"
        # )
    
    # # def _on_file_paused(self, index: int):
    #     """Handle file paused"""
    #     if index >= len(self.file_rows):
    #         return
        
    #     row_widget = self.file_rows[index]
        
    #     # Update UI - RED progress bar
    #     row_widget._progress_bar.configure(progress_color="#d32f2f")
    #     row_widget._action_btn.configure(
    #         text="⏸️ Paused",
    #         fg_color="#d32f2f",
    #         state="disabled"
    #     )
    
    def _on_row_error(self, model):
        """Handle file error"""
        # if index >= len(self.file_rows):
        #     return
        
        # pdf_model = next(p for p in self.pdf_files if p.file_id == file_id)
        
        # Update UI
        model._progress_bar.configure(progress_color="#d32f2f")
        # row_widget._status_label.configure(text=f"❌ Error: {error_msg[:30]}")
        # row_widget._action_btn.configure(
        #     text="❌ Error",
        #     fg_color="#d32f2f",
        #     state="disabled"
        # )


        # ==========================================
        # BATCH PROCESSING (RUN ALL)
        # ==========================================
   
    def start_batch_processing(self):
        """Start processing all files sequentially"""
        if not self.pdf_files:
            messagebox.showinfo("Info", "No PDF files to process")
            return
        
        # Check if any files can be processed
        # processable = [p for p in self.pdf_files if p.status not in ["completed", "paused"]]
        # if not processable:
        #     messagebox.showinfo("Info", "All files are already processed or paused")
        #     return
        
        # Reset all idle files
        # for pdf_model in self.pdf_files:
        #     if pdf_model.status == "idle":
        #         pdf_model.reset()
        
        # Update Run All button
        self.run_all_btn.configure(
            text="⏸❌ Cancel",
            fg_color="#ff0000",
            hover_color="#f50000",
            command=self.cancel_batch_processing
        )
        
        # Update global progress
        self.global_progress_label.configure(
            text=f"Processing 0/{len(self.pdf_files)} files (0%)"
        )
        self.global_progress_bar.pack(fill="x")
        self.global_progress_bar.set(0)
        
        for pdf_model in self.pdf_files:
            # row_frame = self.peserta_rows[pdf_model.file_id]
            # row_frame.grid_columnconfigure(3, weight=0, minsize=200)
                                    
            pdf_model._progress_label.configure(text=f"0%")
            pdf_model._progress_label.pack(side="left", padx=(0, 10))
            pdf_model._progress_bar.configure(progress_color="#484848")
            pdf_model._progress_label.configure(text_color="#1a73e8")
            pdf_model._progress_bar.pack(side="left", fill="x", expand=True)
            pdf_model._progress_bar.set(0)
            pdf_model._status_label.destroy()
            pdf_model._run_btn.configure(text="⏳ Running...", fg_color="#666666",state="disabled")
        
        self.current_batch_processor = PdfBatchProcessor()  # ✅ UBAH INI - Store reference
        self.is_batch_running = True  # ✅  
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
                            # self.after(0, self.reset_progress)
                            self.after(0, lambda: self._on_global_error())
                        
                        case s if 'cancelled' in s:
                            self.after(0, lambda: self._on_global_cancelled())
                
                # Start batch processing
                self.current_batch_processor.process_all(
                    self.pdf_files,
                    self.make_folder,
                    on_single_status,
                    on_global_status
                )
                
                # Update UI for all files
                # for index, pdf_model in enumerate(self.pdf_files):
                #     if pdf_model.status == "idle":
                #         self._prepare_row_for_processing(index)
            except Exception as e:
                logging.exception(f"[ERROR] [Batch PDF Handler] ->\n{e}")
                self.after(0, lambda: self._on_global_error())
                
        thread = Thread(target=process_thread, daemon=True)
        thread.start()
        
    def cancel_batch_processing(self):
        """Cancel batch processing and cleanup"""
        if not self.is_batch_running or not self.current_batch_processor:
            return
        
        # Set cancel flag
        self.current_batch_processor.cancel()
        
        # Cleanup converted files
        if self.current_batch_processor:
            if not self.current_batch_processor.cleaned:
                self.current_batch_processor.cleanup_converted_files()
        
        # Update all non-completed rows to cancelled (red)
        for pdf_model in self.pdf_files:
            if hasattr(pdf_model, '_progress_bar'):
                current_progress = pdf_model._progress_bar.get()
                if current_progress < 1.0:  # Not completed
                    self._on_row_cancelled(pdf_model)
        
        self.is_batch_running = False
        
        # Update global UI
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
        """Handle row cancelled - Mark as red"""
        model._progress_bar.configure(progress_color="#d32f2f")  # Red
        model._progress_label.configure(text_color="#d32f2f")
        
        # Re-enable button for retry
        if hasattr(model, '_run_btn'):
            model._run_btn.configure(
                state="normal",
                fg_color="#34a853",
                text="▶️ Run"
            )

    def _on_global_cancelled(self):
        """Handle batch cancelled"""
        self.is_batch_running = False
        
        # Cleanup
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
        
        # Mark incomplete files as red
        for pdf_model in self.pdf_files:
            if hasattr(pdf_model, '_progress_bar'):
                if pdf_model._progress_bar.get() < 1.0:
                    self._on_row_cancelled(pdf_model)
    
    # # def pause_all_processing(self):
    #     """Pause all processing"""
    #     if not self.batch_processor.is_running:
    #         return
        
    #     # Pause batch processor
    #     self.batch_processor.pause_all()
        
    #     # Update UI
    #     for index, pdf_model in enumerate(self.pdf_files):
    #         if pdf_model.status == "processing":
    #             # Mark as paused and turn RED
    #             pdf_model.status = "paused"
    #             self._on_file_paused(index)
    #         elif pdf_model.status == "idle":
    #             # Idle files: increment global progress by 1
    #             # (simulate as "skipped")
    #             pass
        
    #     # Update Run All button
    #     self.run_all_btn.configure(
    #         text="▶️ Run All",
    #         fg_color="#34a853",
    #         hover_color="#2d8e47"
    #     )
        
    #     # Set global progress to 100% when Pause All is clicked
    #     self.global_progress_bar.set(1.0)
    #     self.global_progress_label.configure(
    #         text="⏸️ Processing paused"
    #     )
        
    #     messagebox.showinfo("Paused", "All processing has been paused")
    
    # # def _prepare_row_for_processing(self, index: int):
    #     """Prepare row UI for processing state"""
    #     if index >= len(self.file_rows):
    #         return
        
    #     row_widget = self.file_rows[index]
        
    #     # Show progress bar
    #     row_widget._status_label.pack_forget()
    #     row_widget._progress_label.pack(side="left", padx=(0, 10))
    #     row_widget._progress_bar.pack(side="left", fill="x", expand=True)
    #     row_widget._progress_bar.set(0)
    #     row_widget._progress_label.configure(text="0%", text_color="#1a73e8")
    #     row_widget._progress_bar.configure(progress_color="#1a73e8")
        
    #     # Update button
    #     row_widget._action_btn.configure(
    #         text="⏸️ Pause",
    #         fg_color="#ff9800",
    #         state="normal",
    #         command=lambda idx=index: self.pause_single_file(idx)
    #     )
    
    def _on_global_progress(self, completed: int, total: int, progress: float):
        """Update global progress bar and label"""
        
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
        """Handle batch processing completion"""
        # Update global progress
        self.is_batch_running = False 
        self.global_progress_bar.set(1.0)
        self.global_progress_bar.configure(progress_color="#34a853")
        
        # # Count statuses
        completed = len(self.pdf_files)
        # paused = sum(1 for p in self.pdf_files if p.status == "paused")
        # error = sum(1 for p in self.pdf_files if p.status == "error")
        
        # Update label
        status_text = f"✓ {completed} completed"
        # if paused > 0:
        #     status_text += f" • ⏸️ {paused} paused"
        # if error > 0:
        #     status_text += f" • ❌ {error} failed"
        
        self.global_progress_label.configure(text=status_text)
        
        # Reset Run All button
        self.run_all_btn.configure(
            text="▶️ Run All",
            fg_color="#34a853",
            hover_color="#2d8e47",
            command=self.start_batch_processing  # ✅ Reset command
        )
        
        # Show completion message
        # message = f"Batch processing completed!\n\n"
        # message += f"✓ Success: {completed}\n"
        # if paused > 0:
        #     message += f"⏸️ Paused: {paused}\n"
        # if error > 0:
        #     message += f"❌ Failed: {error}\n"
        
        # messagebox.showinfo("Completed", message)
        self.is_batch_running = False
    
    def _on_global_error(self):
        self.is_batch_running = False  # ✅ TAMBAH
    
        # Cleanup converted files on error
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
        
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    def save_state(self):
        """Save page state to session (called by main app)"""
        try:
            from services.session import session
            
            state = {
                'pdf_files': [pdf.to_dict() for pdf in self.pdf_files],
                'make_folder': self.make_folder
            }
            
            session.set('pdf2image_state', state)
            print(f"[PDF2IMG] State saved: {len(self.pdf_files)} files")
            
        except Exception as e:
            print(f"[PDF2IMG] Error saving state: {e}")
    
    def restore_state(self):
        """Restore page state from session"""
        try:
            from services.session import session
            
            state = session.get('pdf2image_state')
            if not state:
                return
            
            # Restore files
            saved_files = state.get('pdf_files', [])
            if saved_files:
                self.pdf_files = [PdfFileModel.from_dict(f) for f in saved_files]
                
                # Reset processing states (don't restore running processes)
                for pdf in self.pdf_files:
                    if pdf.status == "processing":
                        pdf.status = "idle"
                        pdf.reset()
            
            # Restore settings
            self.make_folder = state.get('make_folder', True)
            if self.make_folder:
                self.folder_checkbox.select()
            else:
                self.folder_checkbox.deselect()
            
            # Refresh UI
            self.refresh_file_list()
            self.update_footer_visibility()
            
            print(f"[PDF2IMG] State restored: {len(self.pdf_files)} files")
            
        except Exception as e:
            print(f"[PDF2IMG] Error restoring state: {e}")