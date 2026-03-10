"""
Knowledge Base
==============
Static FAQ and college-related knowledge for conversational queries.
Used when the user asks general questions (not student-specific data).
The LLM uses this as context instead of making up answers.
"""

from typing import Optional


# ============================================================================
# FAQ DATABASE
# ============================================================================

KNOWLEDGE_BASE = {
    "admission_process": {
        "question_patterns": [
            "how to apply", "admission process", "how do i get admitted",
            "steps for admission", "application process", "how to enroll",
            "how to get admission",
        ],
        "answer": (
            "The admission process typically involves these steps:\n"
            "1. Fill out the online application form\n"
            "2. Upload required documents (10th & 12th marksheets, photo, ID proof)\n"
            "3. Pay the application fee\n"
            "4. Attend counseling (if required)\n"
            "5. Receive your admission decision\n"
            "6. Pay the admission fees to confirm your seat"
        ),
    },
    "required_documents": {
        "question_patterns": [
            "what documents", "required documents", "which documents",
            "documents needed", "what to upload", "list of documents",
        ],
        "answer": (
            "You'll typically need these documents:\n"
            "• 10th marksheet\n"
            "• 12th marksheet\n"
            "• Passport-size photo\n"
            "• ID proof (Aadhaar/Passport)\n"
            "• Transfer certificate\n"
            "• Migration certificate (if applicable)"
        ),
    },
    "payment_methods": {
        "question_patterns": [
            "how to pay", "payment methods", "pay fees online",
            "payment options", "can i pay online", "fee payment",
        ],
        "answer": (
            "You can pay your fees through:\n"
            "• Online payment portal (UPI, Net Banking, Cards)\n"
            "• Bank challan/demand draft\n"
            "• Contact your counselor for payment assistance"
        ),
    },
    "scholarship": {
        "question_patterns": [
            "scholarship", "financial aid", "fee waiver",
            "merit scholarship", "discount", "concession",
        ],
        "answer": (
            "For scholarship information:\n"
            "• Merit-based scholarships are available for top performers\n"
            "• Contact your assigned counselor for specific scholarship options\n"
            "• Check the college website for detailed eligibility criteria"
        ),
    },
    "contact": {
        "question_patterns": [
            "contact", "help desk", "support", "phone number",
            "email address", "customer care", "helpline",
        ],
        "answer": (
            "For additional support:\n"
            "• Contact your assigned counselor (ask me for their details!)\n"
            "• Visit the college admission office\n"
            "• Check the college website for helpline numbers"
        ),
    },
    "refund": {
        "question_patterns": [
            "refund", "cancel admission", "withdraw", "money back",
            "cancellation",
        ],
        "answer": (
            "For refund or cancellation queries:\n"
            "• Refund policies vary by college\n"
            "• Contact your counselor or the admission office directly\n"
            "• Keep your payment receipts handy"
        ),
    },
    "hostel": {
        "question_patterns": [
            "hostel", "accommodation", "room", "stay",
            "boarding", "dormitory",
        ],
        "answer": (
            "For hostel/accommodation queries:\n"
            "• Hostel availability depends on the college\n"
            "• Contact the admission office or your counselor\n"
            "• Apply for hostel separately during admission"
        ),
    },
}


# ============================================================================
# KNOWLEDGE SEARCH
# ============================================================================

def search_knowledge(message: str) -> Optional[str]:
    """
    Search the FAQ knowledge base for a matching answer.
    Returns the answer text if found, None otherwise.
    """
    msg = message.strip().lower()

    for topic, entry in KNOWLEDGE_BASE.items():
        for pattern in entry["question_patterns"]:
            if pattern in msg:
                return entry["answer"]

    return None
