"""FastAPI service layer package for Jarvis."""

# Package initialization for the API module
# Note: api.main is NOT imported here to avoid circular-dependency traps
# when external modules (e.g. server.py) import from api.security.
# Direct imports like `from api.security import ...` bypass __init__ cleanly.

__version__ = "2.0.0"
__author__ = "Jarvis Team"
__all__ = []