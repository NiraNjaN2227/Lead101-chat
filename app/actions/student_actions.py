"""
Student Actions
===============
Action functions called by the Orchestrator when a matching intent is detected.
Each function navigates the nested student schema and returns a
structured result dict for the ConversationAgent.
"""

from typing import Dict, Any, Optional
from app.database.mock_db import get_student


def get_fee_status(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve fee details for a student.

    Returns:
        Dict with student name, fee breakdown, payment status, and admission status.
    """
    student = get_student(student_id)
    if not student:
        return None

    fees = student.get("admission_info", {}).get("fees", {})
    return {
        "student_id": student_id,
        "student_name": student.get("personal_info", {}).get("full_name", "Unknown"),
        "applied_course": student.get("admission_info", {}).get("applied_course", "Unknown"),
        "total_fees": fees.get("total_fees", 0),
        "paid_fees": fees.get("paid_fees", 0),
        "remaining_fees": fees.get("remaining_fees", 0),
        "payment_status": fees.get("payment_status", "Unknown"),
        "admission_status": student.get("admission_info", {}).get("admission_status", "Unknown"),
    }


def get_document_status(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve document upload and verification status for a student.

    Returns:
        Dict with per-document uploaded/verified booleans and an overall summary.
    """
    student = get_student(student_id)
    if not student:
        return None

    documents = student.get("documents", {})

    # Build per-doc summary
    doc_details = {}
    total_docs = 0
    uploaded_count = 0
    verified_count = 0

    for doc_name, doc_info in documents.items():
        total_docs += 1
        is_uploaded = doc_info.get("uploaded", False)
        is_verified = doc_info.get("verified", False)
        if is_uploaded:
            uploaded_count += 1
        if is_verified:
            verified_count += 1
        doc_details[doc_name] = {
            "uploaded": is_uploaded,
            "verified": is_verified,
        }

    return {
        "student_id": student_id,
        "student_name": student.get("personal_info", {}).get("full_name", "Unknown"),
        "documents": doc_details,
        "summary": {
            "total": total_docs,
            "uploaded": uploaded_count,
            "verified": verified_count,
            "pending_upload": total_docs - uploaded_count,
            "pending_verification": uploaded_count - verified_count,
        },
    }


def get_admission_date(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve admission-related dates and status for a student.

    Returns:
        Dict with application date, admission status, college, and course info.
    """
    student = get_student(student_id)
    if not student:
        return None

    admission = student.get("admission_info", {})
    return {
        "student_id": student_id,
        "student_name": student.get("personal_info", {}).get("full_name", "Unknown"),
        "application_date": admission.get("application_date", "Unknown"),
        "admission_status": admission.get("admission_status", "Unknown"),
        "applied_college": admission.get("applied_college", "Unknown"),
        "applied_course": admission.get("applied_course", "Unknown"),
        "counselor_name": admission.get("counselor", {}).get("name", "Unknown"),
        "counselor_phone": admission.get("counselor", {}).get("phone", "Unknown"),
    }
