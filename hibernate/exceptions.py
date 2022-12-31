"""Custom exceptions for hibernate package."""

class OpenShiftNotFound(Exception):
    """Raised when OpenShift CLI (oc) returns a NotFound error."""
