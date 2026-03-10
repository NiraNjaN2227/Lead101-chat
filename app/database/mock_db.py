"""
Mock Database Module
====================
Loads student records from students_data.json with indexed lookups.
Updated for the comprehensive schema with fees_info, support_info, college_details.
"""

import json
import os
from typing import Dict, List, Optional, Any


_DATA_FILE = os.path.join(os.path.dirname(__file__), "students_data.json")


def _load_students() -> List[Dict[str, Any]]:
    """Load all student records from the JSON data file."""
    if not os.path.exists(_DATA_FILE):
        print(f"Data file not found: {_DATA_FILE}")
        print("  Place students_data.json in app/database/")
        return []
    with open(_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


_ALL_STUDENTS: List[Dict[str, Any]] = _load_students()

# ── Indexes ──
_index_by_id: Dict[str, Dict[str, Any]] = {}
_index_by_app_id: Dict[str, Dict[str, Any]] = {}
_index_by_phone: Dict[str, Dict[str, Any]] = {}
_index_by_email: Dict[str, Dict[str, Any]] = {}
_index_by_name: Dict[str, Dict[str, Any]] = {}
_index_by_roll: Dict[str, Dict[str, Any]] = {}


def _build_indexes() -> None:
    """Build all lookup indexes."""
    for student in _ALL_STUDENTS:
        sid = student.get("student_id", "")
        _index_by_id[sid] = student

        aid = student.get("application_id", "")
        _index_by_app_id[aid] = student

        # Contact
        contact = student.get("personal_info", {}).get("contact", {})
        phone = contact.get("phone", "")
        email = contact.get("email", "").lower()
        whatsapp = contact.get("whatsapp", "")

        if phone:
            _index_by_phone[phone] = student
        if whatsapp and whatsapp != phone:
            _index_by_phone[whatsapp] = student
        if email:
            _index_by_email[email] = student

        # Name
        name = student.get("personal_info", {}).get("full_name", "").lower()
        if name:
            _index_by_name[name] = student

        # Roll number
        roll = student.get("admission_info", {}).get("student_roll_number", "")
        if roll:
            _index_by_roll[roll.upper()] = student


_build_indexes()
print(f"Mock DB loaded: {len(_ALL_STUDENTS)} student(s), {len(_index_by_id)} indexed")


# ── Public API ──

def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    """Lookup by student_id."""
    return _index_by_id.get(student_id.upper() if student_id else "")


def search_student(query: str) -> Optional[Dict[str, Any]]:
    """Search by student_id, application_id, phone, email, name, or roll number."""
    if not query:
        return None
    q = query.strip()
    return (
        _index_by_id.get(q.upper())
        or _index_by_app_id.get(q.upper())
        or _index_by_phone.get(q)
        or _index_by_email.get(q.lower())
        or _index_by_name.get(q.lower())
        or _index_by_roll.get(q.upper())
    )


def get_all_students() -> List[Dict[str, Any]]:
    """Return all student records."""
    return _ALL_STUDENTS
