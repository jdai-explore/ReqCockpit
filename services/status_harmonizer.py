"""
Status harmonization service for ReqCockpit
Normalizes supplier-specific status values to standard categories
"""
import logging
from typing import Optional, Dict
from config import DEFAULT_STATUS_MAPPINGS, NormalizedStatus

logger = logging.getLogger(__name__)


class StatusHarmonizer:
    """
    Harmonizes supplier status values to standardized categories
    
    Applies fuzzy matching and custom supplier-specific mappings to convert
    various status representations into normalized values.
    """
    
    def __init__(self):
        self.custom_mappings: Dict[int, Dict[str, NormalizedStatus]] = {}
        self.stats = {
            'total_normalized': 0,
            'default_mapping_used': 0,
            'custom_mapping_used': 0,
            'unknown_statuses': 0
        }
    
    def normalize_status(self, 
                        original_status: Optional[str], 
                        supplier_id: Optional[int] = None) -> NormalizedStatus:
        """
        Normalize a supplier status to standard category
        
        Args:
            original_status: Original status string from supplier
            supplier_id: Optional supplier ID for custom mappings
            
        Returns:
            NormalizedStatus enum value
        """
        if not original_status:
            return NormalizedStatus.NOT_SET
        
        # Clean the status string
        cleaned_status = original_status.strip().lower()
        
        # Try custom mapping first if supplier ID provided
        if supplier_id and supplier_id in self.custom_mappings:
            custom_map = self.custom_mappings[supplier_id]
            if cleaned_status in custom_map:
                self.stats['custom_mapping_used'] += 1
                self.stats['total_normalized'] += 1
                return custom_map[cleaned_status]
        
        # Try default mappings
        if cleaned_status in DEFAULT_STATUS_MAPPINGS:
            self.stats['default_mapping_used'] += 1
            self.stats['total_normalized'] += 1
            return DEFAULT_STATUS_MAPPINGS[cleaned_status]
        
        # Try fuzzy matching with common variants
        fuzzy_result = self._fuzzy_match(cleaned_status)
        if fuzzy_result:
            self.stats['default_mapping_used'] += 1
            self.stats['total_normalized'] += 1
            return fuzzy_result
        
        # Unknown status - log for analysis
        self.stats['unknown_statuses'] += 1
        logger.warning(f"Unknown status value: '{original_status}'")
        
        # Default to clarification needed for safety
        return NormalizedStatus.CLARIFICATION
    
    def _fuzzy_match(self, status: str) -> Optional[NormalizedStatus]:
        """
        Perform fuzzy matching for common status variants
        
        Args:
            status: Cleaned, lowercase status string
            
        Returns:
            Matched NormalizedStatus or None
        """
        # Accepted patterns
        accepted_patterns = ['accept', 'agree', 'ok', 'comply', 'confirm', 'approved']
        if any(pattern in status for pattern in accepted_patterns):
            return NormalizedStatus.ACCEPTED
        
        # Clarification patterns
        clarify_patterns = ['clarif', 'question', 'unclear', 'pending', 'tbc', 
                          'to be clarified', 'needs discussion']
        if any(pattern in status for pattern in clarify_patterns):
            return NormalizedStatus.CLARIFICATION
        
        # Rejected patterns
        reject_patterns = ['reject', 'decline', 'not accept', 'disagree', 'nok', 
                         'not ok', 'refused']
        if any(pattern in status for pattern in reject_patterns):
            return NormalizedStatus.REJECTED
        
        return None
    
    def load_custom_mappings(self, supplier_id: int, mappings: Dict[str, str]):
        """
        Load custom status mappings for a specific supplier
        
        Args:
            supplier_id: Supplier database ID
            mappings: Dictionary of {original_status: normalized_status}
        """
        normalized_mappings = {}
        
        for original, normalized in mappings.items():
            # Clean original status
            cleaned_original = original.strip().lower()
            
            # Convert normalized string to enum
            try:
                if normalized.upper() == "ACCEPTED":
                    norm_enum = NormalizedStatus.ACCEPTED
                elif normalized.upper() == "CLARIFICATION":
                    norm_enum = NormalizedStatus.CLARIFICATION
                elif normalized.upper() == "REJECTED":
                    norm_enum = NormalizedStatus.REJECTED
                else:
                    norm_enum = NormalizedStatus.NOT_SET
                
                normalized_mappings[cleaned_original] = norm_enum
                
            except Exception as e:
                logger.warning(f"Invalid normalized status '{normalized}': {e}")
                continue
        
        self.custom_mappings[supplier_id] = normalized_mappings
        logger.info(f"Loaded {len(normalized_mappings)} custom mappings for supplier {supplier_id}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get harmonization statistics
        
        Returns:
            Dictionary of statistics
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'total_normalized': 0,
            'default_mapping_used': 0,
            'custom_mapping_used': 0,
            'unknown_statuses': 0
        }
    
    def get_status_color(self, status: NormalizedStatus) -> str:
        """
        Get color code for a normalized status
        
        Args:
            status: NormalizedStatus enum value
            
        Returns:
            Hex color code
        """
        from config import STATUS_COLORS
        return STATUS_COLORS.get(status, "#6c757d")
    
    def get_status_display_name(self, status: NormalizedStatus) -> str:
        """
        Get display name for a normalized status
        
        Args:
            status: NormalizedStatus enum value
            
        Returns:
            Human-readable status name
        """
        return status.value


# Global harmonizer instance
harmonizer = StatusHarmonizer()