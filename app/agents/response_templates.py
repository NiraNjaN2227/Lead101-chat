"""
Response Templates — Zero-LLM responses for structured intents.
Updated for comprehensive student schema.
"""

from typing import Any, Dict, Optional


def _fmt(amount: Any) -> str:
    """Format number as Indian Rupees."""
    if amount is None:
        return "N/A"
    try:
        amount = int(amount)
        s = str(amount)
        if len(s) <= 3:
            return f"Rs. {s}"
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while remaining:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        groups.reverse()
        return f"Rs. {','.join(groups)},{last3}"
    except (ValueError, TypeError):
        return f"Rs. {amount}"


def _yn(val: Any) -> str:
    """Bool to friendly text."""
    if val is True:
        return "Yes"
    elif val is False:
        return "Not yet"
    return "Unknown"


# ── Templates ──

def template_greeting(d: Dict) -> str:
    name = d.get("student_name", "")
    if name:
        return f"Hi {name}! How can I help you today? You can ask about your admission status, fees, course, documents, counselor, or profile."
    return "Hi there! How can I help you? You can ask about admission status, fees, course, documents, or profile."


def template_fees(d: Dict) -> str:
    name = d.get("student_name", "Student")
    structure = d.get("fee_structure", {})
    summary = d.get("payment_summary", {})

    if not structure and not summary:
        return f"Sorry {name}, I don't have fee information in your records."

    parts = [f"Here's your fee summary, {name}:\n"]

    if structure:
        parts.append("Fee Breakdown:")
        parts.append(f"  Tuition: {_fmt(structure.get('tuition_fees'))}")
        parts.append(f"  Admission: {_fmt(structure.get('admission_fees'))}")
        parts.append(f"  Other: {_fmt(structure.get('other_fees'))}")
        parts.append(f"  Total: {_fmt(structure.get('total_fees'))}")

    if summary:
        parts.append("\nPayment Status:")
        parts.append(f"  Paid: {_fmt(summary.get('paid_amount'))}")
        parts.append(f"  Remaining: {_fmt(summary.get('remaining_amount'))}")
        parts.append(f"  Status: {summary.get('payment_status', 'N/A')}")
        parts.append(f"  Last Payment: {summary.get('last_payment_date', 'N/A')}")
        parts.append(f"  Next Deadline: {summary.get('next_payment_deadline', 'N/A')}")

    return "\n".join(parts)


def template_payment_methods(d: Dict) -> str:
    name = d.get("student_name", "Student")
    methods = d.get("payment_methods", {})
    summary = d.get("payment_summary", {})

    if not methods:
        return f"Sorry {name}, I don't have payment method info in your records."

    parts = [f"Here's how you can pay your fees, {name}:\n"]

    # Online
    url = methods.get("online_payment_url")
    accepted = methods.get("accepted_methods", [])
    if url:
        parts.append("Online Payment:")
        parts.append(f"  Link: {url}")
        if accepted:
            parts.append(f"  Accepted: {', '.join(accepted)}")

    # Offline
    location = methods.get("offline_payment_location")
    contact = methods.get("offline_payment_contact")
    if location:
        parts.append("\nOffline Payment:")
        parts.append(f"  Location: {location}")
        if contact:
            parts.append(f"  Contact: {contact}")

    if summary:
        remaining = _fmt(summary.get("remaining_amount"))
        deadline = summary.get("next_payment_deadline", "N/A")
        parts.append(f"\nRemaining amount: {remaining} (due by {deadline})")

    return "\n".join(parts)


def template_admission_status(d: Dict) -> str:
    name = d.get("student_name", "Student")
    status = d.get("admission_status")
    if not status:
        return f"Sorry {name}, I don't have admission status info in your records."

    parts = [f"Here's your admission update, {name}:"]
    parts.append(f"  Admission Status: {status}")
    if d.get("enrollment_status"):
        parts.append(f"  Enrollment: {d['enrollment_status']}")
    if d.get("applied_college"):
        parts.append(f"  College: {d['applied_college']}")
    if d.get("applied_course"):
        parts.append(f"  Course: {d['applied_course']}")
    if d.get("application_date"):
        parts.append(f"  Applied on: {d['application_date']}")
    if d.get("admission_confirmation_date"):
        parts.append(f"  Confirmed on: {d['admission_confirmation_date']}")

    return "\n".join(parts)


def template_admission_deadline(d: Dict) -> str:
    name = d.get("student_name", "Student")
    deadline = d.get("admission_deadline")
    if not deadline:
        return f"Sorry {name}, I don't have deadline info in your records."

    parts = [f"{name}, here's your deadline info:"]
    parts.append(f"  Admission Deadline: {deadline}")
    if d.get("admission_status"):
        parts.append(f"  Current Status: {d['admission_status']}")
    if d.get("enrollment_status"):
        parts.append(f"  Enrollment: {d['enrollment_status']}")

    return "\n".join(parts)


def template_roll_number(d: Dict) -> str:
    name = d.get("student_name", "Student")
    roll = d.get("student_roll_number")
    if not roll:
        return f"Sorry {name}, I don't have roll number info in your records."

    parts = [f"{name}, here's your roll number info:"]
    parts.append(f"  Roll Number: {roll}")
    if d.get("applied_course"):
        parts.append(f"  Course: {d['applied_course']}")
    if d.get("department"):
        parts.append(f"  Department: {d['department']}")

    return "\n".join(parts)


def template_course(d: Dict) -> str:
    name = d.get("student_name", "Student")
    course = d.get("applied_course")
    if not course:
        return f"Sorry {name}, I don't have course info in your records."

    parts = [f"Here's your course info, {name}:"]
    parts.append(f"  Course: {course}")
    if d.get("department"):
        parts.append(f"  Department: {d['department']}")
    if d.get("applied_college"):
        parts.append(f"  College: {d['applied_college']}")

    return "\n".join(parts)


def template_documents(d: Dict) -> str:
    name = d.get("student_name", "Student")
    docs = d.get("documents")
    if not docs or not isinstance(docs, dict):
        return f"Sorry {name}, I don't have document info in your records."

    parts = [f"Here's your document status, {name}:\n"]
    for doc_name, info in docs.items():
        if isinstance(info, dict):
            label = doc_name.replace("_", " ").title()
            uploaded = _yn(info.get("uploaded"))
            verified = _yn(info.get("verified"))
            line = f"  {label}: Uploaded: {uploaded} | Verified: {verified}"
            if info.get("verification_status"):
                line += f" ({info['verification_status']})"
            if info.get("remarks"):
                line += f"\n    Note: {info['remarks']}"
            if info.get("verified_date"):
                line += f" (Verified on: {info['verified_date']})"
            parts.append(line)

    return "\n".join(parts)


def template_academic(d: Dict) -> str:
    name = d.get("student_name", "Student")
    academic = d.get("academic_info")
    if not academic:
        return f"Sorry {name}, I don't have academic info in your records."

    parts = [f"Here's your academic summary, {name}:\n"]

    tenth = academic.get("tenth", {})
    if tenth:
        parts.append("10th Standard:")
        parts.append(f"  Board: {tenth.get('board', 'N/A')}")
        parts.append(f"  School: {tenth.get('school', 'N/A')}")
        parts.append(f"  Year: {tenth.get('year', 'N/A')}")
        parts.append(f"  Marks: {tenth.get('marks_obtained', 'N/A')}/{tenth.get('max_marks', 'N/A')} ({tenth.get('percentage', 'N/A')}%)")

    twelfth = academic.get("twelfth", {})
    if twelfth:
        parts.append("\n12th Standard:")
        parts.append(f"  Board: {twelfth.get('board', 'N/A')}")
        parts.append(f"  School: {twelfth.get('school', 'N/A')}")
        parts.append(f"  Stream: {twelfth.get('stream', 'N/A')}")
        parts.append(f"  Year: {twelfth.get('year', 'N/A')}")
        parts.append(f"  Marks: {twelfth.get('marks_obtained', 'N/A')}/{twelfth.get('max_marks', 'N/A')} ({twelfth.get('percentage', 'N/A')}%)")

    return "\n".join(parts)


def template_profile(d: Dict) -> str:
    name = d.get("student_name", "Student")
    info = d.get("personal_info")
    if not info:
        return f"Sorry {name}, I don't have profile info in your records."

    parts = [f"Here's your profile, {name}:\n"]
    parts.append(f"  Name: {info.get('full_name', 'N/A')}")
    parts.append(f"  Gender: {info.get('gender', 'N/A')}")
    parts.append(f"  Date of Birth: {info.get('date_of_birth', 'N/A')}")
    parts.append(f"  Age: {info.get('age', 'N/A')}")

    contact = info.get("contact", {})
    if contact:
        parts.append(f"  Phone: {contact.get('phone', 'N/A')}")
        parts.append(f"  Email: {contact.get('email', 'N/A')}")

    address = info.get("address", {})
    if address:
        parts.append(f"  Address: {address.get('street', '')}, {address.get('city', '')}, {address.get('state', '')} - {address.get('pincode', '')}")

    return "\n".join(parts)


def template_counselor(d: Dict) -> str:
    name = d.get("student_name", "Student")
    counselor = d.get("assigned_counselor")
    if not counselor:
        return f"Sorry {name}, I don't have counselor info in your records."

    return (
        f"Here's your counselor info, {name}:\n"
        f"  Name: {counselor.get('name', 'N/A')}\n"
        f"  Phone: {counselor.get('phone', 'N/A')}\n"
        f"  Email: {counselor.get('email', 'N/A')}\n\n"
        f"Feel free to reach out to them for admission queries!"
    )


def template_college(d: Dict) -> str:
    name = d.get("student_name", "Student")
    college = d.get("applied_college")
    details = d.get("college_details", {})

    if not college:
        return f"Sorry {name}, I don't have college info in your records."

    parts = [f"Here's your college info, {name}:"]
    parts.append(f"  College: {college}")
    if details:
        if details.get("college_address"):
            parts.append(f"  Address: {details['college_address']}")
        if details.get("college_phone"):
            parts.append(f"  Phone: {details['college_phone']}")
        if details.get("college_email"):
            parts.append(f"  Email: {details['college_email']}")
        if details.get("student_portal_url"):
            parts.append(f"  Student Portal: {details['student_portal_url']}")
        if details.get("accounts_office_location"):
            parts.append(f"  Accounts Office: {details['accounts_office_location']}")
        if details.get("accounts_office_timings"):
            parts.append(f"  Office Timings: {details['accounts_office_timings']}")

    return "\n".join(parts)


def template_support(d: Dict) -> str:
    name = d.get("student_name", "Student")
    support = d.get("support_info")
    if not support:
        return f"Sorry {name}, I don't have support info in your records."

    parts = [f"Here are your support contacts, {name}:\n"]

    counselor = support.get("assigned_counselor", {})
    if counselor:
        parts.append("Counselor:")
        parts.append(f"  {counselor.get('name', 'N/A')} - {counselor.get('phone', 'N/A')}")
        parts.append(f"  Email: {counselor.get('email', 'N/A')}")

    tech = support.get("technical_support", {})
    if tech:
        parts.append("\nTechnical Support:")
        parts.append(f"  Phone: {tech.get('phone', 'N/A')}")
        parts.append(f"  Email: {tech.get('email', 'N/A')}")

    office = support.get("admission_office", {})
    if office:
        parts.append("\nAdmission Office:")
        parts.append(f"  Location: {office.get('location', 'N/A')}")
        parts.append(f"  Hours: {office.get('office_hours', 'N/A')}")

    return "\n".join(parts)


def template_unknown(d: Dict) -> str:
    name = d.get("student_name", "")
    prefix = f"{name}, I" if name else "I"
    return (
        f"{prefix}'m not sure I understood that. You can ask me about:\n"
        f"  - Admission status\n"
        f"  - Fees & payments\n"
        f"  - How/where to pay\n"
        f"  - Course & college details\n"
        f"  - Document verification\n"
        f"  - Academic records\n"
        f"  - Counselor & support contacts\n"
        f"  - Admission deadline\n"
        f"  - Roll number"
    )


# ── Registry ──

TEMPLATE_REGISTRY = {
    "greeting": template_greeting,
    "fees": template_fees,
    "payment_methods": template_payment_methods,
    "admission_status": template_admission_status,
    "admission_deadline": template_admission_deadline,
    "roll_number": template_roll_number,
    "course": template_course,
    "documents": template_documents,
    "academic": template_academic,
    "profile": template_profile,
    "counselor": template_counselor,
    "college": template_college,
    "support": template_support,
    "unknown": template_unknown,
}


def generate_template_response(intent: str, data: Dict[str, Any]) -> Optional[str]:
    """Generate a response using templates. Returns None if no template exists."""
    fn = TEMPLATE_REGISTRY.get(intent)
    return fn(data) if fn else None
