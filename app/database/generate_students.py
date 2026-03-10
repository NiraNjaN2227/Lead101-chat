"""
Student Data Generator
======================
Generates 750 production-grade mock student records for the CON AI admission chatbot.
Uses only standard library modules — no external dependencies.

Usage:
    python -m app.database.generate_students
"""

import random
import json
import os
from datetime import datetime, timedelta

# ============================================================================
# DATA POOLS
# ============================================================================

MALE_FIRST_NAMES = [
    "Aarav", "Arjun", "Aditya", "Akash", "Amit", "Anand", "Aniket", "Ankur",
    "Ashwin", "Bharat", "Chetan", "Deepak", "Dev", "Dhruv", "Ganesh", "Gaurav",
    "Harsh", "Hemant", "Ishaan", "Jayesh", "Karan", "Kartik", "Kunal", "Lakshya",
    "Manish", "Mohit", "Nakul", "Naveen", "Nikhil", "Omkar", "Pranav", "Prateek",
    "Rahul", "Rajesh", "Ravi", "Rohit", "Sachin", "Sahil", "Sameer", "Sanjay",
    "Shankar", "Shivam", "Siddharth", "Suresh", "Tanmay", "Tushar", "Varun",
    "Vijay", "Vikram", "Vinay", "Yash", "Yogesh", "Abhinav", "Ajay", "Vivek",
    "Pavan", "Manoj", "Sunil", "Ramesh", "Dinesh"
]

FEMALE_FIRST_NAMES = [
    "Aanya", "Aditi", "Akshara", "Ananya", "Anjali", "Anushka", "Aparna",
    "Bhavya", "Chaitra", "Deepika", "Diya", "Divya", "Gauri", "Harini",
    "Ishita", "Jaya", "Kavya", "Keerthi", "Kriti", "Lakshmi", "Madhavi",
    "Meera", "Megha", "Nandini", "Neha", "Nisha", "Pallavi", "Pooja",
    "Priya", "Radhika", "Riya", "Sakshi", "Sanvi", "Sarika", "Shreya",
    "Simran", "Sneha", "Sonal", "Sruthi", "Swati", "Tanvi", "Trisha",
    "Uma", "Vandana", "Varsha", "Vidya", "Yamini", "Zara", "Aishwarya",
    "Archana", "Bhavana", "Charulata", "Durga", "Esha", "Fatima"
]

LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Gupta", "Kumar", "Patel", "Reddy", "Nair",
    "Iyer", "Rao", "Joshi", "Mehta", "Shah", "Malhotra", "Chopra", "Kapoor",
    "Bhat", "Menon", "Pillai", "Das", "Mukherjee", "Banerjee", "Chatterjee",
    "Sen", "Bose", "Ghosh", "Roy", "Dutta", "Mishra", "Pandey", "Tiwari",
    "Saxena", "Agarwal", "Srivastava", "Chauhan", "Yadav", "Thakur", "Rathore",
    "Patil", "Deshmukh", "Kulkarni", "Jain", "Goyal", "Sethi", "Khanna"
]

# City → (State, Pincode prefix)
CITIES = {
    "Chennai":      ("Tamil Nadu",        "600"),
    "Bangalore":    ("Karnataka",         "560"),
    "Mumbai":       ("Maharashtra",       "400"),
    "Delhi":        ("Delhi",             "110"),
    "Hyderabad":    ("Telangana",         "500"),
    "Pune":         ("Maharashtra",       "411"),
    "Kolkata":      ("West Bengal",       "700"),
    "Ahmedabad":    ("Gujarat",           "380"),
    "Jaipur":       ("Rajasthan",         "302"),
    "Lucknow":      ("Uttar Pradesh",     "226"),
    "Coimbatore":   ("Tamil Nadu",        "641"),
    "Kochi":        ("Kerala",            "682"),
    "Indore":       ("Madhya Pradesh",    "452"),
    "Bhopal":       ("Madhya Pradesh",    "462"),
    "Nagpur":       ("Maharashtra",       "440"),
    "Vizag":        ("Andhra Pradesh",    "530"),
    "Chandigarh":   ("Chandigarh",        "160"),
    "Mysore":       ("Karnataka",         "570"),
    "Madurai":      ("Tamil Nadu",        "625"),
    "Trichy":       ("Tamil Nadu",        "620"),
}

STREETS = [
    "MG Road", "Anna Nagar", "Gandhi Street", "Nehru Road", "Rajaji Nagar",
    "Lake View Colony", "Park Avenue", "Temple Road", "Station Road",
    "Bazaar Street", "Cross Street", "Main Road", "Layout Road",
    "Sector 5", "Sector 12", "Sector 21", "Phase 2", "Block C",
    "Orchid Avenue", "Rose Garden Colony", "Vidya Nagar", "Shanti Nagar",
    "Ram Nagar", "Krishna Colony", "Saraswati Street"
]

BOARDS = ["CBSE", "ICSE", "TN State Board", "KA State Board", "MH State Board",
           "AP State Board", "UP State Board", "WB State Board"]

SCHOOLS = [
    "St. Joseph's Higher Secondary School", "DAV Public School",
    "Kendriya Vidyalaya", "Delhi Public School", "Ryan International School",
    "Bharatiya Vidya Bhavan", "Chinmaya Vidyalaya", "Velammal Matriculation School",
    "Loyola School", "Modern School", "Cambridge International School",
    "National Public School", "Presidency School", "Vidya Mandir Senior Secondary School",
    "Army Public School", "Air Force School", "Jawahar Navodaya Vidyalaya",
    "St. Xavier's School", "Bishop Cotton School", "La Martiniere College",
    "Santhome Higher Secondary School", "Hindu Senior Secondary School",
    "Govt. Higher Secondary School", "Sacred Heart School", "Don Bosco School"
]

TWELFTH_STREAMS = ["Science", "Commerce", "Arts"]

COURSES = [
    ("B.Tech Computer Science", "Computer Science"),
    ("B.Tech AI", "Artificial Intelligence"),
    ("BCA", "Computer Applications"),
    ("BBA", "Business Administration"),
    ("MBA", "Business Administration"),
    ("B.Sc Data Science", "Data Science"),
]

COLLEGES = [
    "SRM Institute of Science and Technology",
    "VIT University",
    "Amity University",
    "Christ University",
    "Manipal Academy of Higher Education",
    "Lovely Professional University",
    "BITS Pilani",
]

COUNSELORS = [
    {"name": "Pradeep Kumar",   "phone": "+919876543210"},
    {"name": "Sunita Rao",      "phone": "+919876543211"},
    {"name": "Manoj Sharma",    "phone": "+919876543212"},
    {"name": "Rekha Nair",      "phone": "+919876543213"},
    {"name": "Vijay Menon",     "phone": "+919876543214"},
    {"name": "Anita Gupta",     "phone": "+919876543215"},
    {"name": "Suresh Iyer",     "phone": "+919876543216"},
    {"name": "Deepa Joshi",     "phone": "+919876543217"},
    {"name": "Ramesh Patil",    "phone": "+919876543218"},
    {"name": "Kavitha Reddy",   "phone": "+919876543219"},
]

ADMISSION_STATUSES = ["Applied", "Under Review", "Accepted", "Rejected", "Fees Pending", "Enrolled"]
LEAD_SOURCES = ["Website", "WhatsApp", "Walk-in", "Referral", "Social Media", "Education Fair", "Google Ads"]
COMMUNICATION_CHANNELS = ["WhatsApp", "Email", "Phone", "SMS"]
INTEREST_LEVELS = ["Low", "Medium", "High"]

CONVERSATION_TEMPLATES = [
    "Student inquired about {course} program details and fee structure.",
    "Follow-up call regarding admission status for {course}.",
    "Student requested scholarship information for {course}.",
    "Initial inquiry about hostel facilities and campus life.",
    "Student asked about placement statistics for {department} department.",
    "Parent called to verify admission process for {course}.",
    "Document verification pending — student to submit originals.",
    "Student confirmed interest in {course}, awaiting fee payment.",
    "Counselor discussed eligibility criteria for {course} admission.",
    "Student compared {college} with other institutions.",
    "Walk-in visit — student toured the {department} department lab.",
    "WhatsApp inquiry about {course} last date for application.",
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def random_date(start_year: int, end_year: int) -> str:
    """Generate a random date string in YYYY-MM-DD format."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    random_day = start + timedelta(days=random.randint(0, delta))
    return random_day.strftime("%Y-%m-%d")


def random_timestamp(start_year: int, end_year: int) -> str:
    """Generate a random ISO 8601 timestamp."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = int((end - start).total_seconds())
    random_sec = start + timedelta(seconds=random.randint(0, delta))
    return random_sec.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_phone() -> str:
    """Generate a realistic Indian phone number (+91 followed by 10 digits starting with 6-9)."""
    first_digit = random.choice([6, 7, 8, 9])
    rest = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+91{first_digit}{rest}"


def generate_email(first_name: str, last_name: str, idx: int) -> str:
    """Generate a realistic email address."""
    domains = ["gmail.com", "yahoo.co.in", "outlook.com", "hotmail.com", "rediffmail.com"]
    separator = random.choice([".", "_", ""])
    suffix = random.choice(["", str(random.randint(1, 99)), str(idx)])
    return f"{first_name.lower()}{separator}{last_name.lower()}{suffix}@{random.choice(domains)}"


def calculate_age(dob_str: str) -> int:
    """Calculate age from date of birth string (YYYY-MM-DD) relative to 2026-02-18."""
    dob = datetime.strptime(dob_str, "%Y-%m-%d")
    reference = datetime(2026, 2, 18)
    age = reference.year - dob.year
    if (reference.month, reference.day) < (dob.month, dob.day):
        age -= 1
    return age


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_student(idx: int) -> dict:
    """Generate a single student record."""

    # --- IDs ---
    student_id = f"STU2026{idx:04d}"
    application_id = f"APP2026{idx:04d}"

    # --- Personal Info ---
    gender = random.choice(["Male", "Female"])
    if gender == "Male":
        first_name = random.choice(MALE_FIRST_NAMES)
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"

    dob = random_date(2002, 2008)
    age = calculate_age(dob)

    phone = generate_phone()
    # 80% chance WhatsApp is the same number
    whatsapp = phone if random.random() < 0.8 else generate_phone()
    email = generate_email(first_name, last_name, idx)

    city = random.choice(list(CITIES.keys()))
    state, pincode_prefix = CITIES[city]
    pincode = pincode_prefix + str(random.randint(100, 999)).zfill(3)
    street = random.choice(STREETS)

    # --- Academic Info ---
    board_10 = random.choice(BOARDS)
    school_10 = random.choice(SCHOOLS)
    year_10 = random.choice([2020, 2021, 2022, 2023])
    marks_10 = random.randint(250, 490)
    max_marks_10 = 500
    percentage_10 = round((marks_10 / max_marks_10) * 100, 2)

    board_12 = random.choice(BOARDS)
    school_12 = random.choice(SCHOOLS)
    stream_12 = random.choice(TWELFTH_STREAMS)
    year_12 = year_10 + 2
    marks_12 = random.randint(600, 1150)
    max_marks_12 = 1200
    percentage_12 = round((marks_12 / max_marks_12) * 100, 2)

    # Entrance exams — some students have them, some don't
    jee = round(random.uniform(50.0, 99.9), 2) if random.random() < 0.4 else None
    cet = random.randint(50, 180) if random.random() < 0.3 else None
    neet = random.randint(300, 700) if random.random() < 0.15 else None

    # --- Admission Info ---
    course, department = random.choice(COURSES)
    college = random.choice(COLLEGES)
    application_date = random_date(2025, 2026)
    admission_status = random.choice(ADMISSION_STATUSES)
    counselor = random.choice(COUNSELORS)

    total_fees = random.randint(50, 300) * 1000  # 50k–300k in steps of 1k
    if admission_status == "Enrolled":
        paid_fees = total_fees
    elif admission_status == "Fees Pending":
        paid_fees = random.randint(0, int(total_fees * 0.7))
    elif admission_status in ["Accepted", "Under Review"]:
        paid_fees = random.randint(0, int(total_fees * 0.5))
    elif admission_status == "Rejected":
        paid_fees = 0
    else:  # Applied
        paid_fees = random.choice([0, random.randint(0, int(total_fees * 0.3))])

    remaining_fees = total_fees - paid_fees

    if paid_fees == 0:
        payment_status = "Unpaid"
    elif paid_fees >= total_fees:
        payment_status = "Fully Paid"
    else:
        payment_status = "Partially Paid"

    # --- Documents ---
    def random_doc(bias_uploaded=0.7, bias_verified=0.5):
        uploaded = random.random() < bias_uploaded
        verified = uploaded and (random.random() < bias_verified)
        return {"uploaded": uploaded, "verified": verified}

    documents = {
        "tenth_marksheet": random_doc(0.9, 0.7),
        "twelfth_marksheet": random_doc(0.85, 0.5),
        "passport": random_doc(0.3, 0.2),
        "photo": random_doc(0.95, 0.8),
    }

    # --- Interaction Info ---
    lead_source = random.choice(LEAD_SOURCES)
    last_contacted = random_date(2025, 2026)
    communication_channel = random.choice(COMMUNICATION_CHANNELS)
    lead_score = random.randint(0, 100)

    if lead_score >= 70:
        interest_level = "High"
    elif lead_score >= 40:
        interest_level = "Medium"
    else:
        interest_level = "Low"

    conversation_summary = random.choice(CONVERSATION_TEMPLATES).format(
        course=course, department=department, college=college
    )

    # --- System Metadata ---
    created_at = random_timestamp(2025, 2025)
    updated_at = random_timestamp(2026, 2026)

    # --- Assemble Record ---
    return {
        "student_id": student_id,
        "application_id": application_id,

        "personal_info": {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "gender": gender,
            "date_of_birth": dob,
            "age": age,

            "contact": {
                "phone": phone,
                "whatsapp": whatsapp,
                "email": email,
            },

            "address": {
                "street": street,
                "city": city,
                "state": state,
                "country": "India",
                "pincode": pincode,
            }
        },

        "academic_info": {
            "tenth": {
                "board": board_10,
                "school": school_10,
                "year": year_10,
                "marks_obtained": marks_10,
                "max_marks": max_marks_10,
                "percentage": percentage_10,
            },
            "twelfth": {
                "board": board_12,
                "school": school_12,
                "stream": stream_12,
                "year": year_12,
                "marks_obtained": marks_12,
                "max_marks": max_marks_12,
                "percentage": percentage_12,
            },
            "entrance_exams": {
                "jee_percentile": jee,
                "cet_score": cet,
                "neet_score": neet,
            }
        },

        "admission_info": {
            "applied_college": college,
            "applied_course": course,
            "department": department,

            "application_date": application_date,
            "admission_status": admission_status,

            "counselor": {
                "name": counselor["name"],
                "phone": counselor["phone"],
            },

            "fees": {
                "total_fees": total_fees,
                "paid_fees": paid_fees,
                "remaining_fees": remaining_fees,
                "payment_status": payment_status,
            }
        },

        "documents": documents,

        "interaction_info": {
            "lead_source": lead_source,
            "last_contacted": last_contacted,
            "communication_channel": communication_channel,
            "lead_score": lead_score,
            "student_interest_level": interest_level,
            "conversation_summary": conversation_summary,
        },

        "system_metadata": {
            "created_at": created_at,
            "updated_at": updated_at,
            "record_version": 1,
            "is_active": True,
        }
    }


def main():
    """Generate 750 student records and write to students_data.json."""
    NUM_STUDENTS = 3

    random.seed(42)  # Reproducible output

    students = [generate_student(i + 1) for i in range(NUM_STUDENTS)]

    output_path = os.path.join(os.path.dirname(__file__), "students_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {NUM_STUDENTS} student records → {output_path}")
    print(f"   First ID: {students[0]['student_id']}")
    print(f"   Last  ID: {students[-1]['student_id']}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
