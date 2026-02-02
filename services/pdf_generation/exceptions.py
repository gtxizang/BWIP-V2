"""
Exceptions for the PDF generation service.

Custom exceptions for handling PDF generation errors.
"""

from apps.core.exceptions import BWIPException


class PDFGenerationError(BWIPException):
    """Base exception for PDF generation errors."""

    default_message = "PDF generation failed."


class TemplateNotFoundError(PDFGenerationError):
    """Raised when poster template is not found."""

    default_message = "Poster template not found."


class InvalidTemplateSizeError(PDFGenerationError):
    """Raised when requested size is invalid."""

    default_message = "Invalid poster size requested."


class QRCodeGenerationError(PDFGenerationError):
    """Raised when QR code generation fails."""

    default_message = "Failed to generate QR code."


class RenderingError(PDFGenerationError):
    """Raised when template rendering fails."""

    default_message = "Failed to render poster template."
