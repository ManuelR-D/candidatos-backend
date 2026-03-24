"""Session Parser service for parsing PDFs and storing data in the database."""
from typing import Optional, TYPE_CHECKING, cast
from collections import defaultdict
from datetime import date, datetime
from uuid import UUID
import unicodedata
from src.session_parser import SessionParser
from src.service.postgres_service import PostgreService
from src.ai.ai_summarizer import AISummarizer

if TYPE_CHECKING:
    from src.dto.models.representative import Representative
from src.service.senate_session_service import SenateSessionService
from src.service.topic_service import TopicService
from src.service.attendance_session_service import AttendanceSessionService
from src.service.attendance_service import AttendanceService
from src.service.representative_service import RepresentativeService
from src.service.intervention_service import InterventionService
from src.service.representative_topic_summary_service import RepresentativeTopicSummaryService
import logging

logger = logging.getLogger(__name__)
MINIMUM_TOPIC_LENGTH_FOR_SUMMARY = 120  # Minimum length of text to consider generating a summary

class SessionParserService:
    """Service for parsing session PDFs and storing the data in the database."""
    
    def __init__(self, postgres_service: PostgreService, summarizer: Optional[AISummarizer] = None):
        """
        Initialize SessionParserService.
        
        Args:
            postgres_service: PostgreSQL service instance
            summarizer: Optional AISummarizer for generating representative-topic summaries
        """
        self.db = postgres_service
        self.summarizer = summarizer
        self.senate_session_service = SenateSessionService(postgres_service)
        self.topic_service = TopicService(postgres_service)
        self.attendance_session_service = AttendanceSessionService(postgres_service)
        self.attendance_service = AttendanceService(postgres_service)
        self.representative_service = RepresentativeService(postgres_service)
        self.intervention_service = InterventionService(postgres_service)
        self.representative_topic_summary_service = RepresentativeTopicSummaryService(postgres_service)
    
    def parse_and_store_session(self, pdf_path: str, session_date: Optional[date] = None, 
                                session_type_id: Optional[int] = None, debug: bool = False,
                                topic_filter: Optional[str] = None) -> dict:
        """
        Parse a session PDF and store all extracted data in the database.
        
        Args:
            pdf_path: Path to the PDF file to parse
            session_date: Date of the session (if None, uses current date)
            session_type_id: Optional ID of the session type
            debug: If True, print debug information
            topic_filter: Optional topic display string to parse (e.g., "6. Homenajes")
            
        Returns:
            Dictionary with summary of stored data including session_id and counts
        """
        # Use current date if not provided
        if session_date is None:
            session_date = datetime.now().date()
        
        # Parse the PDF
        parser = SessionParser(pdf_path, debug=debug, summarizer=self.summarizer)
        parsed_data = parser.parse_all()
        
        # Store senate session (upsert to avoid duplicates on re-parse)
        session_id = self.senate_session_service.upsert(session_date, session_type_id)
        
        # Store topics and interventions
        topics_count = 0
        interventions_count = 0
        not_found_speakers = []
        topic_filter_normalized = (topic_filter or "").strip().lower()
        filtered_topics = []
        for session_topic in parsed_data['topics']:
            topic_display = f"{session_topic.number}. {session_topic.title}"
            if topic_filter_normalized and topic_display.strip().lower() != topic_filter_normalized:
                logger.info(f"Skipping topic '{topic_display}' due to filter.")
                continue
            filtered_topics.append(session_topic)

        for session_topic in filtered_topics:
            topic_display = f"{session_topic.number}. {session_topic.title}"
            logger.info(f"Storing topic: {topic_display}")
            topic_id = self.topic_service.upsert(
                session_id,
                topic_display
            )
            topics_count += 1

            rep_texts: dict[UUID, list[str]] = defaultdict(list)
            rep_names: dict[UUID, str] = {}
            
            # Store interventions for this topic
            for idx, intervention_data in enumerate(session_topic.interventions, start=1):
                # Skip if this looks like body text (too long for a name)
                speaker_full = f"{intervention_data.speaker.last_name} {intervention_data.speaker.first_name}".strip()
                if len(speaker_full) > 80:  # Names shouldn't be this long
                    continue
                
                representative = self._find_representative_by_name(
                    intervention_data.speaker.last_name,
                    intervention_data.speaker.first_name,
                    session_date=session_date
                )
                
                if representative and representative.UniqueID is not None:
                    rep_id = cast(UUID, representative.UniqueID)
                    self.intervention_service.insert(
                        topic_id=topic_id,
                        representative_id=rep_id,
                        text=intervention_data.text,
                        role=intervention_data.role,
                        intervention_order=idx
                    )
                    interventions_count += 1

                    rep_texts[rep_id].append(intervention_data.text)
                    full_name = representative.Full_name
                    if not isinstance(full_name, str):
                        full_name = None
                    rep_names[rep_id] = full_name or speaker_full
                elif debug:
                    not_found_speakers.append(speaker_full)

            if self.summarizer and rep_texts:
                for rep_id, texts in rep_texts.items():
                    combined_text = "\n\n".join(texts).strip()
                    should_generate = self._should_generate_summary(topic_id, rep_id, combined_text)
                    if not should_generate:
                        continue

                    try:
                        summary = self.summarizer.summarize(
                            combined_text,
                            summary_type="concise",
                            max_length=80,
                            rep_name=rep_names.get(rep_id),
                            topic_name=topic_display
                        )
                        self.representative_topic_summary_service.upsert(
                            representative_id=rep_id,
                            topic_id=topic_id,
                            summary=summary
                        )
                    except Exception as e:
                        if debug:
                            print(f"Warning: Failed to generate summary for representative-topic: {e}")
        
        # Store attendance
        # First, ensure we have a "Present" attendance type
        present_attendance_id = self._get_or_create_attendance_type("Present")
        
        attendance_count = 0
        for session_rep in parsed_data['attendance']:
            # Skip invalid entries (dates, page numbers, headers, etc.)
            last_name = session_rep.last_name.strip().strip(',').strip()
            
            # Filter out very long "names" (likely body text)
            if len(last_name) > 50:
                continue
                
            if len(last_name) < 3 or any(keyword in last_name.upper() for keyword in 
                ['ÍNDICE', 'SESIÓN', 'PÁG', 'DIRECCIÓN', 'DICIEMBRE', 'ENERO', 
                 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO',
                 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'APÉNDICE', 'ACTA', 
                 'CONVOCATORIA', 'INSERCIÓN', 'TAQUÍGRAFO', 'EXTRAORDINARIA',
                 'HIMNO', 'BANDERA', 'JURAMENTO', 'ASUNTOS', 'ENTRADOS',
                 'CUESTIÓN', 'PRIVILEGIO', 'PRESUPUESTO', 'RÉGIMEN', 'PENAL',
                 'NACIONAL', 'ORDEN DEL DÍA']):
                continue
            
            # Try to find the representative in the database
            representative = self._find_representative_by_name(
                session_rep.last_name,
                session_rep.first_name,
                session_date=session_date
            )
            
            if representative and representative.UniqueID is not None:
                self.attendance_session_service.insert(
                    cast(UUID, representative.UniqueID),
                    session_id,
                    present_attendance_id
                )
                attendance_count += 1
            else:
                not_found_speakers.append(f"{session_rep.last_name} {session_rep.first_name}".strip())
        return {
            'session_id': session_id,
            'session_date': session_date,
            'topics_stored': topics_count,
            'interventions_stored': interventions_count,
            'attendance_stored': attendance_count,
            'topics_parsed': len(filtered_topics),
            'attendance_parsed': len(parsed_data['attendance']),
            'index_items': len(parsed_data['index']),
            'not_found_speakers': not_found_speakers
        }

    def _should_generate_summary(self, topic_id: int, rep_id: UUID, combined_text: str) -> bool:
        if len(combined_text) <= MINIMUM_TOPIC_LENGTH_FOR_SUMMARY:
            return False
        
        existing_summary = self.representative_topic_summary_service.get_by_representative_and_topic(
            representative_id=rep_id,
            topic_id=topic_id
        )

        if existing_summary and (existing_summary.Summary or "").strip():
            return False
        return True
    
    def _get_or_create_attendance_type(self, attendance_name: str) -> int:
        """
        Get or create an attendance type.
        
        Args:
            attendance_name: Name of the attendance type
            
        Returns:
            The unique_id of the attendance type
        """
        # Try to get existing attendance type
        existing = self.attendance_service.get_by_name(attendance_name)
        if existing and existing.UniqueID is not None:
            return cast(int, existing.UniqueID)
        
        # Create new attendance type
        return self.attendance_service.insert(attendance_name)
    
    def _find_representative_by_name(
        self,
        last_name: str,
        first_name: str,
        session_date: Optional[date] = None
    ) -> Optional['Representative']:
        """
        Find a representative by their name.
        
        Args:
            last_name: Representative's last name (may contain full name in "LAST, First" format)
            first_name: Representative's first name (may be empty if full name is in last_name)
            
        Returns:
            Representative object if found, None otherwise
        """
        # If first_name is empty and last_name contains a comma, split it
        if not first_name and ',' in last_name:
            parts = last_name.split(',', 1)
            if len(parts) == 2:
                last_name = parts[0].strip()
                first_name = parts[1].strip()
        
        # Get all representatives and search for a match
        all_representatives = self.representative_service.get_all()
        if session_date:
            filtered_representatives = []
            for rep in all_representatives:
                legal_end_date = cast(Optional[date], rep.Legal_end_date)
                if legal_end_date is None or legal_end_date >= session_date:
                    filtered_representatives.append(rep)
            all_representatives = filtered_representatives
        
        # Normalize names for comparison - remove commas, extra spaces, accents
        def normalize(text: object) -> str:
            """Remove accents, convert to uppercase, strip whitespace and commas."""
            if text is None:
                return ""
            if not isinstance(text, str):
                text = str(text)
            if not text:
                return ""
            # Remove accents
            text = unicodedata.normalize('NFD', text)
            text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
            # Uppercase and clean
            return text.strip().strip(',').strip().upper()
        
        last_name_normalized = normalize(last_name)
        first_name_normalized = normalize(first_name)

        def tokens(text: str) -> list[str]:
            return [token for token in text.split() if token]
        
        # Skip if last name looks invalid (too short or contains weird patterns)
        # Check for exact matches to avoid filtering real names like "PAGOTTO"
        invalid_patterns = ['_', 'INDICE', 'SESION']
        # For page numbers, check if it's exactly "PAG" or starts with "PAG."
        if (len(last_name_normalized) < 3 or 
            any(pattern in last_name_normalized for pattern in invalid_patterns) or
            last_name_normalized == 'PAG' or 
            last_name_normalized.startswith('PAG.')):
            return None
        
        for rep in all_representatives:
            # Handle potential None values in representative names
            rep_last = rep.Last_name or ""
            rep_first = rep.First_name or ""
            rep_last_normalized = normalize(rep_last)
            rep_first_normalized = normalize(rep_first)
            
            # Exact match
            if rep_last_normalized == last_name_normalized and rep_first_normalized == first_name_normalized:
                return rep
            
            # Match by last name only if first name is empty (for speakers with only last name)
            if not first_name_normalized and rep_last_normalized == last_name_normalized:
                return rep
            
            # Partial match: if one name contains the other (for cases like "Belén" vs "MARÍA BELÉN")
            if rep_last_normalized == last_name_normalized:
                if first_name_normalized and rep_first_normalized:
                    # Check if one contains the other
                    if first_name_normalized in rep_first_normalized or rep_first_normalized in first_name_normalized:
                        return rep
        
        # Fuzzy matching: Try progressively dropping words from search last name
        # This handles cases where we search for "LEDESMA ABDALA" but DB has "LEDESMA ABDALA DE ZAMORA"
        # Try the full search term first, then drop words one at a time from the end
        if last_name_normalized:
            last_name_words = last_name_normalized.split()
            
            # Try progressively shorter versions (drop last word each iteration)
            for num_words in range(len(last_name_words), 0, -1):
                truncated_search_last_name = ' '.join(last_name_words[:num_words])
                
                for rep in all_representatives:
                    rep_last = rep.Last_name or ""
                    rep_first = rep.First_name or ""
                    rep_last_normalized = normalize(rep_last)
                    rep_first_normalized = normalize(rep_first)
                    
                    # Check if the DB last name starts with the truncated search last name
                    # Only match if it's followed by a space or is the complete name
                    if (rep_last_normalized == truncated_search_last_name or 
                        rep_last_normalized.startswith(truncated_search_last_name + ' ')):
                        # Also check first name compatibility
                        if not first_name_normalized or rep_first_normalized == first_name_normalized:
                            return rep
                        # Check if one first name contains the other
                        if first_name_normalized and rep_first_normalized:
                            if first_name_normalized in rep_first_normalized or rep_first_normalized in first_name_normalized:
                                return rep
        
        # Fuzzy matching: Try matching with reversed word order in first name
        # This handles cases like "Marcela Andrea" vs "ANDREA MARCELA"
        if first_name_normalized and ' ' in first_name_normalized:
            first_name_words = first_name_normalized.split()
            reversed_first_name = ' '.join(reversed(first_name_words))
            
            for rep in all_representatives:
                rep_last = rep.Last_name or ""
                rep_first = rep.First_name or ""
                rep_last_normalized = normalize(rep_last)
                rep_first_normalized = normalize(rep_first)
                
                # Check if last name matches and reversed first name matches
                if rep_last_normalized == last_name_normalized and rep_first_normalized == reversed_first_name:
                    return rep

        # Flexible matching:
        # 1) Assume the representative exists.
        # 2) If exact not found, try matching by any first-name token.
        # 3) If multiple (or none), narrow by any last-name token.
        search_first_tokens = tokens(first_name_normalized)
        search_last_tokens = tokens(last_name_normalized)

        candidates_by_name: list['Representative'] = []
        if search_first_tokens:
            for rep in all_representatives:
                rep_first_tokens = tokens(normalize(rep.First_name or ""))
                if any(token in rep_first_tokens for token in search_first_tokens):
                    candidates_by_name.append(rep)

        base_candidates = candidates_by_name if candidates_by_name else all_representatives

        if search_last_tokens:
            narrowed = []
            for rep in base_candidates:
                rep_last_tokens = tokens(normalize(rep.Last_name or ""))
                if any(token in rep_last_tokens for token in search_last_tokens):
                    narrowed.append(rep)
            if len(narrowed) == 1:
                return narrowed[0]
            if len(narrowed) > 1:
                def score(rep: 'Representative') -> tuple[int, int]:
                    rep_last_tokens = tokens(normalize(rep.Last_name or ""))
                    rep_first_tokens = tokens(normalize(rep.First_name or ""))
                    last_overlap = sum(1 for token in search_last_tokens if token in rep_last_tokens)
                    first_overlap = sum(1 for token in search_first_tokens if token in rep_first_tokens)
                    return (last_overlap, first_overlap)

                narrowed.sort(key=score, reverse=True)
                return narrowed[0]

        if len(base_candidates) == 1:
            return base_candidates[0]
        
        # Debug: If we reach here, no match was found
        return None
