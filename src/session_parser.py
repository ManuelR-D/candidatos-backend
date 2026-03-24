import fitz
from typing import List, Tuple, Optional
import re
from .dto.session_topic import SessionTopic
from .dto.session_representative import SessionRepresentative
from .extractors import IndexExtractor, AttendanceExtractor, TopicExtractor
from .ai.ai_summarizer import AISummarizer


class SessionParser:
    """Main parser for legislative session documents."""
    
    def __init__(self, pdf_path: str, debug: bool = False, summarizer: Optional[AISummarizer] = None):
        """
        Initialize the parser.
        
        Args:
            pdf_path: Path to the PDF file
            debug: If True, print debug information
            summarizer: Optional AISummarizer instance for generating representative-topic summaries
        """
        self.pdf_path = pdf_path
        self.debug = debug
        self.summarizer = summarizer
        self._full_text = None
        self._index_page = None
    
    def extract_full_text(self) -> str:
        """Extract all text from the PDF."""
        if self._full_text is None:
            doc = fitz.open(self.pdf_path)
            text = ""
            try:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text += str(page.get_text("text")) + "\n"
            finally:
                doc.close()
            self._full_text = text
        return self._full_text
    
    def find_index_page(self) -> int:
        """Find the page number where the index is located (0-indexed)."""
        if self._index_page is None:
            doc = fitz.open(self.pdf_path)
            index_page = -1
            try:
                for page_num in range(min(10, doc.page_count)):
                    page = doc.load_page(page_num)
                    text = str(page.get_text("text"))
                    if re.search(r'[ÍI]NDICE\s*\n', text, re.IGNORECASE):
                        index_page = page_num
                        break
            finally:
                doc.close()
            self._index_page = index_page
        return self._index_page
    
    def extract_text_after_index(self) -> str:
        """Extract text from PDF starting after the index page."""
        index_page = self.find_index_page()
        
        doc = fitz.open(self.pdf_path)
        text = ""
        try:
            start_page = index_page + 1 if index_page >= 0 else 0
            for page_num in range(start_page, doc.page_count):
                page = doc.load_page(page_num)
                text += str(page.get_text("text")) + "\n"
        finally:
            doc.close()
        return text
    
    def extract_index(self) -> List[Tuple[str, str]]:
        """Extract the index/table of contents."""
        full_text = self.extract_full_text()
        return IndexExtractor.extract_items(full_text, debug=self.debug)
    
    def extract_attendance(self) -> List[SessionRepresentative]:
        """Extract the attendance/presence list."""
        full_text = self.extract_full_text()
        return AttendanceExtractor.extract_presence_list(full_text)
    
    def extract_topics(self, index_items: Optional[List[Tuple[str, str]]] = None) -> List[SessionTopic]:
        """
        Extract topics and their interventions.
        
        Args:
            index_items: Optional pre-extracted index items. If None, will extract automatically.
            
        Returns:
            List of Topic objects
        """
        if index_items is None:
            index_items = self.extract_index()
        
        content_text = self.extract_text_after_index()
        return TopicExtractor.find_topic_sections(content_text, index_items)
    
    def parse_all(self) -> dict:
        """
        Parse all components of the session.
        
        Returns:
            Dictionary with 'index', 'attendance', and 'topics' keys
        """
        index_items = self.extract_index()
        attendance = self.extract_attendance()
        topics = self.extract_topics(index_items)
        
        return {
            'index': index_items,
            'attendance': attendance,
            'topics': topics
        }
