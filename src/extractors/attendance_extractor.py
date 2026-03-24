import re
from typing import List
from ..dto.session_representative import SessionRepresentative


class AttendanceExtractor:
    """Extracts the attendance list (PRESENTES) from session documents."""
    
    @staticmethod
    def extract_presence_list(text: str) -> List[SessionRepresentative]:
        """
        Extract the presence list from text.
        
        Args:
            text: Full text of the document
            
        Returns:
            List of SessionRepresentative objects
        """
        if not text:
            return []
        
        # Find PRESENTES section
        match = re.search(r"PRESENTES\s*:\s*", text, re.IGNORECASE)
        if not match:
            return []
        
        start = match.end()
        remainder = text[start:]
        
        # Find where the section ends
        end_match = re.search(
            r"\n\s*(AUSENTES|ORDEN\s+DO\s+DIA|ORDEN\s+DO\s+TRABALHO|PAUTA|"
            r"OBSERVA(C|Ç)[AÃ]O|ENCERRAMENTO|PRESIDENTE|SECRET(A|Á)RIO|VEREADORES|ÍNDICE|INDICE)\b",
            remainder,
            re.IGNORECASE,
        )
        
        block = remainder[:end_match.start()] if end_match else remainder
        
        # Split names
        return AttendanceExtractor._split_names(block)
    
    @staticmethod
    def _clean_line(line: str) -> str:
        """Clean a line removing leading markers and extra spaces."""
        line = re.sub(r"^[\s\-–•*\d\.\)]\s*", "", line)
        line = re.sub(r"\s{2,}", " ", line).strip()
        line = line.strip("-–•*;:., ")
        return line
    
    @staticmethod
    def _split_names(block: str) -> List[SessionRepresentative]:
        """
        Split the attendance block into individual representatives.
        Handles the format: APELLIDO followed by Nombre on next line.
        """
        lines = []
        for raw_line in block.splitlines():
            cleaned = AttendanceExtractor._clean_line(raw_line)
            if cleaned:
                lines.append(cleaned)
        
        if len(lines) <= 1:
            single = lines[0] if lines else ""
            if "," in single:
                parts = [AttendanceExtractor._clean_line(item) for item in single.split(",") if AttendanceExtractor._clean_line(item)]
                return [SessionRepresentative(last_name=p, first_name="") for p in parts]
            return [SessionRepresentative(last_name=single, first_name="")] if single else []
        
        # Pair up lines: APELLIDO (uppercase) followed by Nombre (capitalized)
        representatives = []
        i = 0
        while i < len(lines):
            current = lines[i]
            # Check if current line is all uppercase (likely surname)
            if current.isupper() and i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line is not all uppercase, it's likely the first name
                if not next_line.isupper():
                    representatives.append(SessionRepresentative(
                        last_name=current,
                        first_name=next_line
                    ))
                    i += 2
                    continue
            # Otherwise, treat as single name (surname only)
            representatives.append(SessionRepresentative(last_name=current, first_name=""))
            i += 1
        
        return representatives
