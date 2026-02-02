"""
Template selection and recommendation logic.

Provides logic for recommending appropriate poster templates
based on location status and EPA data.
"""

from dataclasses import dataclass
from enum import Enum


class TemplateType(str, Enum):
    """Poster template types per EPA specifications."""

    T1A = "1A"  # Identified, no restrictions
    T1B = "1B"  # Identified, temporary restrictions
    T1C = "1C"  # Identified, season-long restrictions
    T2A = "2A"  # Non-identified, with restrictions
    T2B = "2B"  # Non-identified, no restrictions


@dataclass
class TemplateRecommendation:
    """Result of template recommendation."""

    recommended: TemplateType
    reason: str
    can_override: bool = True


def recommend_template(
    classification: str,
    has_active_alert: bool,
    alert_is_season_long: bool = False,
) -> TemplateRecommendation:
    """
    Recommend appropriate template based on location status.

    Uses EPA guidelines to recommend the correct template based on:
    - Classification (IDENTIFIED vs NON_IDENTIFIED)
    - Presence of active alerts/advisories
    - Whether alerts are season-long

    Args:
        classification: IDENTIFIED or NON_IDENTIFIED.
        has_active_alert: Whether there's an active alert.
        alert_is_season_long: Whether alert is season-long.

    Returns:
        TemplateRecommendation with template code and reason.

    Example:
        >>> recommendation = recommend_template(
        ...     classification="IDENTIFIED",
        ...     has_active_alert=False,
        ... )
        >>> recommendation.recommended
        <TemplateType.T1A: '1A'>
    """
    if classification == "IDENTIFIED":
        if not has_active_alert:
            return TemplateRecommendation(
                recommended=TemplateType.T1A,
                reason="Identified bathing water with no restrictions",
            )
        elif alert_is_season_long:
            return TemplateRecommendation(
                recommended=TemplateType.T1C,
                reason="Identified bathing water with season-long restriction",
            )
        else:
            return TemplateRecommendation(
                recommended=TemplateType.T1B,
                reason="Identified bathing water with temporary restriction",
            )
    else:  # NON_IDENTIFIED
        if has_active_alert:
            return TemplateRecommendation(
                recommended=TemplateType.T2A,
                reason="Non-identified water with restrictions",
            )
        else:
            return TemplateRecommendation(
                recommended=TemplateType.T2B,
                reason="Non-identified water with no restrictions",
            )


def get_template_for_code(code: str) -> TemplateType:
    """
    Get TemplateType from code string.

    Args:
        code: Template code (1A, 1B, 1C, 2A, 2B).

    Returns:
        Corresponding TemplateType.

    Raises:
        ValueError: If code is invalid.
    """
    code = code.upper()
    for template in TemplateType:
        if template.value == code:
            return template
    raise ValueError(f"Invalid template code: {code}")


def get_templates_for_classification(classification: str) -> list[TemplateType]:
    """
    Get all valid templates for a classification.

    Args:
        classification: IDENTIFIED or NON_IDENTIFIED.

    Returns:
        List of valid TemplateType values.
    """
    if classification == "IDENTIFIED":
        return [TemplateType.T1A, TemplateType.T1B, TemplateType.T1C]
    else:
        return [TemplateType.T2A, TemplateType.T2B]
