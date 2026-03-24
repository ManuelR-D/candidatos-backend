"""Filter class for representative data."""
from typing import Optional, Any


class RepresentativeFilter:
    """Filter for representative queries."""
    
    def __init__(self, province_service, party_service, coalition_service):
        """
        Initialize the filter with required services.
        
        Args:
            province_service: Service for province operations
            party_service: Service for party operations
            coalition_service: Service for coalition operations
        """
        self.province_service = province_service
        self.party_service = party_service
        self.coalition_service = coalition_service
    
    def filter_representatives(
        self,
        representatives: list,
        province: Optional[str] = None,
        party: Optional[str] = None,
        coalition: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Filter representatives by province, party, and coalition.
        
        Args:
            representatives: List of representative objects to filter
            province: Optional province name filter (case-insensitive substring match)
            party: Optional party name filter (case-insensitive substring match)
            coalition: Optional coalition name filter (case-insensitive substring match)
            
        Returns:
            List of filtered representative dictionaries
        """
        filtered_reps = []
        
        for rep in representatives:
            # Get province, party, and coalition info using services
            # Extract actual values from model attributes using getattr to avoid Column type issues
            province_id = getattr(rep, 'Province_id', None)
            party_id = getattr(rep, 'Party_id', None)
            coalition_id = getattr(rep, 'Coalition_id', None)
            
            province_obj = self.province_service.get_by_id(province_id) if province_id is not None else None
            party_obj = self.party_service.get_by_id(party_id) if party_id is not None else None
            coalition_obj = self.coalition_service.get_by_id(coalition_id) if coalition_id is not None else None
            
            # Extract string values using getattr to avoid Column type inference issues
            province_name: Optional[str] = getattr(province_obj, 'Name', None) if province_obj else None
            party_name: Optional[str] = getattr(party_obj, 'Name', None) if party_obj else None
            coalition_name: Optional[str] = getattr(coalition_obj, 'Name', None) if coalition_obj else None
            
            # Apply filters
            if province and province_name is not None:
                if province.upper() not in province_name.upper():
                    continue
            if party and party_name is not None:
                if party.upper() not in party_name.upper():
                    continue
            if coalition and coalition_name is not None:
                if coalition.upper() not in coalition_name.upper():
                    continue
            
            # Build representative dictionary
            filtered_reps.append({
                'id': str(rep.UniqueID),
                'external_id': rep.External_id,
                'full_name': rep.Full_name,
                'last_name': rep.Last_name,
                'first_name': rep.First_name,
                'province': province_name,
                'party': party_name,
                'coalition': coalition_name,
                'legal_start_date': rep.Legal_start_date.isoformat() if rep.Legal_start_date else None,
                'legal_end_date': rep.Legal_end_date.isoformat() if rep.Legal_end_date else None,
                'real_start_date': rep.Real_start_date.isoformat() if rep.Real_start_date else None,
                'real_end_date': rep.Real_end_date,
                'email': rep.Email,
                'phone': rep.Phone,
                'photo_url': rep.Photo_url,
                'facebook_url': rep.Facebook_url,
                'twitter_url': rep.Twitter_url,
                'instagram_url': rep.Instagram_url,
                'youtube_url': rep.Youtube_url
            })
        
        return filtered_reps
