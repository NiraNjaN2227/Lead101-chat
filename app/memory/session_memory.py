from typing import Dict, List, Optional

class SessionMemory:
    """
    Manages short-term conversation memory for user sessions.
    Stores messages in-memory and enforces a maximum history limit.
    """

    def __init__(self, max_messages: int = 10):
        """
        Initialize the session memory.

        Args:
            max_messages (int): Maximum number of messages to retain per session.
        """
        self.max_messages = max_messages
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        # Stores the identified student_id per session
        self._student_ids: Dict[str, str] = {}

    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> None:
        """
        Add a message to the session history.

        Args:
            session_id (str): The unique session identifier.
            role (str): The sender's role ('user' or 'assistant').
            content (str): The message content.
            intent (str, optional): The detected intent (only for user messages).
        """
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'.")

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        message = {
            "role": role,
            "content": content,
            "intent": intent
        }
        self.sessions[session_id].append(message)

        # Trim history if exceeding max_messages
        if len(self.sessions[session_id]) > self.max_messages:
            self.sessions[session_id] = self.sessions[session_id][-self.max_messages:]

    def get_last_intent(self, session_id: str) -> Optional[str]:
        """
        Get the LAST user intent from memory.

        Args:
           session_id (str): The unique session identifier.

        Returns:
           Optional[str]: The last detected intent, or None if not found.
        """
        if session_id not in self.sessions or not self.sessions[session_id]:
            return None
            
        # Iterate backwards to find the last user message with an intent
        for message in reversed(self.sessions[session_id]):
            if message["role"] == "user" and message.get("intent"):
                return message["intent"]
        
        return None

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve the conversation history for a session.
        Returns a simplified list for LLM context (role, content).
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.sessions.get(session_id, [])
        ]

    def clear_session(self, session_id: str) -> None:
        """Clear the history for a specific session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        self._student_ids.pop(session_id, None)

    def set_student_id(self, session_id: str, student_id: str) -> None:
        """Store the identified student_id for this session."""
        self._student_ids[session_id] = student_id

    def get_student_id(self, session_id: str) -> Optional[str]:
        """Get the stored student_id for this session, or None."""
        return self._student_ids.get(session_id)
