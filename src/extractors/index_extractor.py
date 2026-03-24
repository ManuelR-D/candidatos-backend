import re
from typing import List, Tuple


class IndexExtractor:
    """Extracts the index/table of contents from session documents."""
    
    @staticmethod
    def extract_items(text: str, debug: bool = False) -> List[Tuple[str, str]]:
        """
        Extract index items as (number, title) tuples.
        
        Args:
            text: Full text of the document
            debug: If True, print debug information
            
        Returns:
            List of (number, title) tuples
        """
        items = []
        match = re.search(r"[ÍI]NDICE\s*\n", text, re.IGNORECASE)
        if not match:
            return []
        
        if debug:
            lines_before = text[:match.start()].count('\n')
            print(f"[DEBUG] ÍNDICE encontrado en la línea ~{lines_before}")
        
        start = match.end()
        remainder = text[start:]
        
        # Find where the index block ends
        index_block = IndexExtractor._find_index_block(remainder, debug)
        
        if debug:
            print(f"[DEBUG] Tamaño del bloque de índice: {len(index_block)} caracteres")
        
        # Parse numbered items from the index block
        items = IndexExtractor._parse_numbered_items(index_block)
        
        if debug:
            print(f"[DEBUG] Items extraídos antes de filtrar: {len(items)}")
        
        # Filter to keep only continuous sequence
        filtered = IndexExtractor._filter_continuous_sequence(items, debug)
        
        if debug:
            print(f"[DEBUG] Items después de filtrar: {len(filtered)}")
        
        return filtered
    
    @staticmethod
    def _find_index_block(text: str, debug: bool = False) -> str:
        """Find and extract the index block from the text."""
        # Look for PRESENTES marker
        end_match = re.search(r"\n\s*PRESENTES\s*:", text, re.IGNORECASE)
        
        if end_match:
            if debug:
                print(f"[DEBUG] Bloque de índice termina antes de PRESENTES:")
            return text[:end_match.start()]
        
        # Fallback: look for appendix items (I., II., III.)
        end_match = re.search(r"\n\s*I\.\s+", text)
        if end_match:
            if debug:
                print(f"[DEBUG] Bloque de índice termina antes de apéndice (I.)")
            return text[:end_match.start()]
        
        # Last resort: take first 1500 characters
        if debug:
            print(f"[DEBUG] No se encontró fin del índice, usando primeros 1500 caracteres")
        return text[:1500]
    
    @staticmethod
    def _parse_numbered_items(index_block: str) -> List[Tuple[str, str]]:
        """Parse numbered items from the index block."""
        items = []
        
        for line in index_block.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Match main numbered items (1., 2., etc.)
            match = re.match(r'^(\d+)\.\s+(.+)', line)
            if match:
                num = int(match.group(1))
                # Only accept sequential or near-sequential numbers
                if not items or (num <= int(items[-1][0]) + 3):
                    items.append((match.group(1), match.group(2)))
            elif items and not re.match(r'^\d+\.', line) and not re.match(r'^[IVX]+\.', line, re.IGNORECASE):
                # Continuation of previous item
                items[-1] = (items[-1][0], items[-1][1] + ' ' + line)
        
        return items
    
    @staticmethod
    def _filter_continuous_sequence(items: List[Tuple[str, str]], debug: bool = False) -> List[Tuple[str, str]]:
        """Filter items to keep only continuous sequence starting from 1."""
        filtered = []
        
        for num_str, title in items:
            num = int(num_str)
            
            if not filtered:
                if num == 1:
                    filtered.append((num_str, title))
            else:
                last_num = int(filtered[-1][0])
                # Allow continuation if within reasonable range
                if num <= last_num + 2:
                    filtered.append((num_str, title))
                else:
                    if debug:
                        print(f"[DEBUG] Detenido en salto: {last_num} -> {num}")
                    break
        
        return filtered
