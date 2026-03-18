from typing import Dict, Any

class ContextBuilder:
    """
    Minimizes the student profile context sent to the LLM based on intent.
    Strategies:
    - fees: only fee info
    - admission: only admission info
    - academic: only academic info
    - etc.
    """
    
    @staticmethod
    def build_context(intent: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a subset of student_data relevant to the intent.
        Always includes basic identity info (name, id).
        """
        if not student_data:
            return {}

        # Base context (always included)
        # Fix: map 'name' to 'student_name' as expected by templates
        base_context = {
            "student_id": student_data.get("student_id"),
            "student_name": student_data.get("personal_info", {}).get("full_name"),
            "first_name": student_data.get("personal_info", {}).get("first_name"),
        }
        
        # Specific fields based on intent
        relevant_data = {}
        
        if intent == "fees":
            # Flatten fees_info for template compatibility
            fees_info = student_data.get("fees_info", {})
            relevant_data.update(fees_info) # Puts fee_structure, payment_summary at root
        
        elif intent == "admission_status" or intent == "admission_deadline":
            # Flatten admission_info
            adm_info = student_data.get("admission_info", {})
            relevant_data.update(adm_info)
            # documents might be relevant for admission status
            relevant_data["documents"] = student_data.get("documents")
            
        elif intent == "course" or intent == "roll_number":
            # Flatten admission_info for course/dept
            adm_info = student_data.get("admission_info", {})
            relevant_data.update(adm_info)
            # academic_info might be relevant
            relevant_data["academic_info"] = student_data.get("academic_info")
            
        elif intent == "documents":
            relevant_data["documents"] = student_data.get("documents")
            # Flatten admission status just in case
            relevant_data["admission_status"] = student_data.get("admission_info", {}).get("admission_status")
            
        elif intent == "contact" or intent == "support" or intent == "counselor":
            # Do NOT flatten support_info because template_support expects d.get("support_info")
            relevant_data["support_info"] = student_data.get("support_info", {})
            # However, template_counselor expects flattened 'assigned_counselor'
            relevant_data.update(student_data.get("support_info", {}))
            relevant_data["college_details"] = student_data.get("admission_info", {}).get("college_details")

        elif intent == "college":
            adm_info = student_data.get("admission_info", {})
            relevant_data.update(adm_info)
            
        elif intent == "profile":
            relevant_data["personal_info"] = student_data.get("personal_info")
            relevant_data["academic_info"] = student_data.get("academic_info")
            
        elif intent == "payment_methods":
             fees_info = student_data.get("fees_info", {})
             relevant_data.update(fees_info)

        else:
            # Fallback for complex/unknown intents: Return specific summary sections or full profile if critically needed.
            # Requirement: "Do NOT send unnecessary fields."
            # For unknown, we might start with a broader set but exclude heavy internal metadata.
            relevant_data = student_data.copy()
            relevant_data.pop("system_metadata", None)
            relevant_data.pop("interaction_info", None)

        # Merge base and relevant
        return {**base_context, **relevant_data}
