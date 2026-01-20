# =======================
# FILE: models/pdf_model.py
# =======================

class PdfFileModel:
    """Model untuk menyimpan state dari setiap PDF file"""
    
    def __init__(self, file_path: str):
        import uuid
        import os
        self.file_id = f"File-{uuid.uuid4().hex[:8].upper()}"
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.total_pages = 0
        self.current_page = 0
        self.status = "idle"  # idle | processing | completed | error
        self.progress = 0.0  # 0-100
        self.error_message = ""
        
    # def reset(self):
    #     """Reset progress untuk re-run"""
    #     self.current_page = 0
    #     self.progress = 0.0
    #     self.status = "idle"
    #     self.error_message = ""
    
    # def update_progress(self, current_page: int):
    #     """Update progress berdasarkan halaman yang sedang diproses"""
    #     self.current_page = current_page
    #     if self.total_pages > 0:
    #         self.progress = (current_page / self.total_pages) * 100
    
    # def set_completed(self):
    #     """Mark file sebagai completed"""
    #     self.status = "completed"
    #     self.progress = 100.0
    #     self.current_page = self.total_pages
    
    # def set_error(self, error_msg: str):
    #     """Mark file sebagai error"""
    #     self.status = "error"
    #     self.error_message = error_msg
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'file_id': self.file_id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'total_pages': self.total_pages,
            'current_page': self.current_page,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        pdf = cls(data['file_path'])
        pdf.file_id = data['file_id']
        pdf.file_name = data['file_name']
        pdf.total_pages = data['total_pages']
        pdf.current_page = data['current_page']
        pdf.status = data['status']
        pdf.progress = data['progress']
        pdf.error_message = data['error_message']
        return pdf
    
    # def __str__(self):
    #     return f"PesertaModel(nama={self.nama}, nik={self.nik})"
    
    # def __repr__(self):
    #     return self.__str__()