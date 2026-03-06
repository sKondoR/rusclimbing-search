"""Custom exceptions for the application."""

from fastapi import HTTPException


class EventNotFoundException(HTTPException):
    """Raised when an event is not found."""

    def __init__(self, message: str = "Event not found"):
        super().__init__(status_code=404, detail=message)


class TeamNotFoundException(HTTPException):
    """Raised when a team is not found."""

    def __init__(self, message: str = "Team not found"):
        super().__init__(status_code=404, detail=message)


class DatabaseError(HTTPException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(status_code=500, detail=message)


class ParsingError(HTTPException):
    """Raised when parsing fails."""

    def __init__(self, message: str = "Parsing failed"):
        super().__init__(status_code=500, detail=message)
