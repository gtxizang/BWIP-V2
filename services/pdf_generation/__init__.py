"""
PDF generation service for BWIP.

Provides poster PDF generation using WeasyPrint.
"""

from .generator import PosterPDFGenerator
from .templates import TemplateRecommendation, TemplateType, recommend_template

__all__ = [
    "PosterPDFGenerator",
    "TemplateType",
    "TemplateRecommendation",
    "recommend_template",
]
