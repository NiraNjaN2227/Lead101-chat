import json
import logging
from typing import Dict, List, Optional
from app.core.config import settings


logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self):
        self.data_path = settings.STUDENT_DATA_PATH
        self.students: List[Dict] = []
        # O(1) Lookup Maps
        self.student_map: Dict[str, Dict] = {} # ID -> Student
        self.phone_map: Dict[str, Dict] = {}   # Phone -> Student
        self._load_data()

    def _load_data(self):
        """Loads student data from JSON into memory and builds indices."""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.students = json.load(f)
                
                # Build O(1) indices
                for student in self.students:
                    # Index by ID
                    s_id = student.get("student_id")
                    if s_id:
                        self.student_map[s_id.upper()] = student
                    
                    # Index by Phone (Normalize generic match)
                    contact = student.get("personal_info", {}).get("contact", {})
                    phone = contact.get("phone")
                    whatsapp = contact.get("whatsapp")
                    
                    if phone:
                        self.phone_map[phone] = student
                    if whatsapp and whatsapp != phone:
                        self.phone_map[whatsapp] = student
                        
            logger.info(f"Loaded {len(self.students)} students from {self.data_path}")
            logger.info(f"Indexed {len(self.phone_map)} phone numbers.")
            
        except FileNotFoundError:
            logger.error(f"Student data file not found at {self.data_path}")
            self.students = []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {self.data_path}")
            self.students = []

    async def get_student(self, student_id: str) -> Optional[Dict]:
        """Fetch student by ID (O(1) Lookup)."""
        student = self.student_map.get(student_id.upper())
        if not student:
            return None
        return student

    async def search_student_by_phone(self, phone: str) -> Optional[Dict]:
        """Search student by phone number (O(1) Lookup)."""
        # Direct lookup in Hash Map
        return self.phone_map.get(phone)
