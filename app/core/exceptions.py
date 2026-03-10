class AIBackendException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class StudentNotFoundException(AIBackendException):
    """Raised when a student ID cannot be found."""
    pass

class LLMServiceException(AIBackendException):
    """Raised when the LLM service fails."""
    pass

class IntentDetectionException(AIBackendException):
    """Raised when intent detection fails critically."""
    pass
