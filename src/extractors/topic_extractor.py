import re
from typing import List, Tuple
from ..dto.session_topic import SessionTopic
from ..dto.intervention import Intervention
from ..dto.session_representative import SessionRepresentative


class TopicExtractor:
    """Extracts topics and their interventions from session documents."""
    
    @staticmethod
    def find_topic_sections(
        full_text: str, 
        index_items: List[Tuple[str, str]]
    ) -> List[SessionTopic]:
        """
        Find and parse each topic section with its interventions.
        
        Args:
            full_text: Complete text of the session (after index page)
            index_items: List of (number, title) tuples from the index
            
        Returns:
            List of SessionTopic objects with their interventions
        """
        topics = []
        
        # Find session start
        session_start_match = re.search(
            r'Sra?\.\s+Presidente.*?Habiendo\s+qu[óo]rum.*?abierta\s+la\s+sesi[óo]n',
            full_text,
            re.IGNORECASE | re.DOTALL
        )
        
        search_offset = session_start_match.start() if session_start_match else 0
        search_text = full_text[search_offset:]
        
        for i, (number, title) in enumerate(index_items):
            # Search for topic header
            pattern = r'\n' + re.escape(number) + r'\.\s+[A-ZÁÉÍÓÚÑ]'
            match = re.search(pattern, search_text)
            
            if not match:
                continue
            
            start = match.start() + search_offset
            
            # Find where this topic ends (next topic or end of document)
            end = len(full_text)
            if i + 1 < len(index_items):
                next_number = index_items[i + 1][0]
                next_pattern = r'\n' + re.escape(next_number) + r'\.\s+[A-ZÁÉÍÓÚÑ]'
                next_match = re.search(next_pattern, full_text[start + 10:])
                if next_match:
                    end = start + 10 + next_match.start()
            
            topic_text = full_text[start:end]
            interventions = TopicExtractor._parse_interventions(topic_text)
            
            topics.append(SessionTopic(
                number=number,
                title=title,
                interventions=interventions
            ))
        
        return topics
    
    @staticmethod
    def _parse_interventions(text: str) -> List[Intervention]:
        """
        Parse interventions from a topic text block.
        
        Args:
            text: Text block containing interventions
            
        Returns:
            List of Intervention objects
        """
        interventions = []
        lines = text.split('\n')
        current_intervention = None
        current_text = []
        
        # Pattern for speaker roles:
        # 1. Sr./Sra. + Title (Name): "Sr. Presidente (Abdala)"
        # 2. Sr./Sra. + Name: "Sr. Pagotto" or "Sr. De Pedro"
        # 3. Title (Name): "Senador (García)"
        speaker_pattern = (
            r'^((?:Sr[a]?\.?\s+)?(?:Presidente|Vicepresidente|Secretari[oa]|'
            r'Senador[a]?|Ministro[a]?)|Sr[a]?\.)\s*'
            r'(?:\(([^)]+)\)|([A-ZÁÉÍÓÚÑa-záéíóúñ]\w+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]\w+)*))\s*\.?\s*-\s*(.*)$'
        )
        
        for line in lines:
            match = re.match(speaker_pattern, line.strip(), re.IGNORECASE)
            
            if match:
                # Save previous intervention
                if current_intervention:
                    full_text = ' '.join(current_text).strip()
                    if len(full_text) >= 10:
                        interventions.append(Intervention(
                            speaker=SessionRepresentative(last_name=current_intervention['name'], first_name=""),
                            role=current_intervention['role'],
                            text=full_text
                        ))
                
                # Extract role and name
                role = match.group(1).strip()
                # Name can be in parentheses (group 2) or directly after role (group 3)
                name = match.group(2) if match.group(2) else match.group(3)
                first_text = match.group(4).strip()
                
                # Check if this is just the president giving the floor to someone else
                if re.search(r'tiene\s+la\s+palabra|a\s+continuaci[óo]n|palabra\s+(el|la|al)\s+(senador|senadora)', 
                             first_text, re.IGNORECASE):
                    current_intervention = None
                    current_text = []
                    continue
                
                current_intervention = {'role': role, 'name': name.strip() if name else 'Unknown'}
                current_text = [first_text] if first_text else []
            elif current_intervention and line.strip():
                # Check if this line contains "tiene la palabra" which means end of this intervention
                if re.search(r'tiene\s+la\s+palabra|a\s+continuaci[óo]n|palabra\s+(el|la|al)\s+(senador|senadora)', 
                            line, re.IGNORECASE):
                    # Save current intervention before this line
                    full_text = ' '.join(current_text).strip()
                    if len(full_text) >= 10:
                        interventions.append(Intervention(
                            speaker=SessionRepresentative(last_name=current_intervention['name'], first_name=""),
                            role=current_intervention['role'],
                            text=full_text
                        ))
                    current_intervention = None
                    current_text = []
                    continue
                
                # Continuation of current intervention
                if re.match(r'^\d+\.\s+[A-ZÁÉÍÓÚÑ]', line.strip()):
                    break
                current_text.append(line.strip())
        
        # Save last intervention
        if current_intervention:
            full_text = ' '.join(current_text).strip()
            if len(full_text) >= 10:
                interventions.append(Intervention(
                    speaker=SessionRepresentative(last_name=current_intervention['name'], first_name=""),
                    role=current_intervention['role'],
                    text=full_text
                ))
        
        return interventions
