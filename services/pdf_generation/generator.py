"""
PDF poster generator.

Provides the main PosterPDFGenerator class for generating
print-ready PDF posters using WeasyPrint.
"""

import logging
from pathlib import Path
from typing import Any

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import CSS, HTML

from apps.locations.models import Location

from .exceptions import PDFGenerationError, TemplateNotFoundError
from .qr_codes import generate_beach_url_qr_code, generate_poster_qr_codes

logger = logging.getLogger(__name__)


class PosterPDFGenerator:
    """
    Generator for bathing water information posters.

    Creates print-ready PDF posters using WeasyPrint and Django templates.
    Supports multiple sizes (A1, A3, A4, A5) and orientations.

    Example:
        >>> generator = PosterPDFGenerator()
        >>> pdf_bytes = generator.generate_poster(
        ...     location=location,
        ...     template_type="1A",
        ...     size="A1",
        ...     orientation="PORTRAIT",
        ...     language="en",
        ...     epa_data=epa_data,
        ...     user=request.user,
        ... )
    """

    @property
    def SIZES(self) -> dict[str, tuple[int, int]]:
        """Get paper sizes from settings."""
        return settings.PDF_GENERATION.get("SIZES", {
            "A1": (594, 841),
            "A3": (297, 420),
            "A4": (210, 297),
            "A5": (148, 210),
        })

    @property
    def DPI(self) -> int:
        """Get DPI from settings."""
        return settings.PDF_GENERATION.get("DPI", 300)

    def __init__(self) -> None:
        """Initialize the PDF generator."""
        self.base_template_dir = Path(settings.BASE_DIR) / "templates" / "pdf"

    def generate_poster(
        self,
        location: Location,
        template_type: str,
        size: str,
        orientation: str,
        language: str,
        epa_data: dict[str, Any],
        user: Any = None,
    ) -> bytes:
        """
        Generate a poster PDF.

        Args:
            location: The bathing water location.
            template_type: Template code (1A, 1B, 1C, 2A, 2B).
            size: Paper size (A1, A3, A4, A5).
            orientation: PORTRAIT or LANDSCAPE.
            language: Language code (en, ga, bilingual).
            epa_data: EPA data formatted for poster.
            user: User generating the poster.

        Returns:
            PDF file bytes.

        Raises:
            TemplateNotFoundError: If template not found.
            PDFGenerationError: If generation fails.
        """
        try:
            # Get dimensions
            width_mm, height_mm = self._get_dimensions(size, orientation)

            # Calculate scale factor relative to A1
            scale_factor = self._calculate_scale_factor(size)

            # Generate QR codes
            qr_size = int(200 * scale_factor)
            qr_codes = generate_poster_qr_codes(qr_size)
            qr_codes["beach_url"] = generate_beach_url_qr_code(
                location.beaches_ie_id, qr_size
            )

            # Build template context
            context = self._build_context(
                location=location,
                template_type=template_type,
                size=size,
                orientation=orientation,
                language=language,
                epa_data=epa_data,
                qr_codes=qr_codes,
                scale_factor=scale_factor,
            )

            # Render HTML
            template_name = f"pdf/{template_type.lower()}_{language}.html"
            try:
                html_content = render_to_string(template_name, context)
            except Exception as e:
                logger.error(f"Template not found: {template_name}")
                # Try fallback to English
                template_name = f"pdf/{template_type.lower()}_en.html"
                try:
                    html_content = render_to_string(template_name, context)
                except Exception:
                    raise TemplateNotFoundError(
                        f"Template not found: {template_type}_{language}"
                    )

            # Generate CSS
            css_content = self._get_print_css(width_mm, height_mm, scale_factor)

            # Generate PDF
            html = HTML(string=html_content, base_url=str(settings.BASE_DIR))
            css = CSS(string=css_content)

            pdf_bytes = html.write_pdf(stylesheets=[css])

            logger.info(
                f"Generated poster: {location.name_en} - {template_type} ({size})"
            )
            return pdf_bytes

        except TemplateNotFoundError:
            raise
        except Exception as e:
            logger.exception("PDF generation failed")
            raise PDFGenerationError(f"PDF generation failed: {e}")

    def _get_dimensions(
        self,
        size: str,
        orientation: str,
    ) -> tuple[int, int]:
        """
        Get paper dimensions in mm.

        Args:
            size: Paper size code.
            orientation: PORTRAIT or LANDSCAPE.

        Returns:
            Tuple of (width_mm, height_mm).
        """
        if size not in self.SIZES:
            size = "A1"

        width, height = self.SIZES[size]

        if orientation == "LANDSCAPE":
            return height, width
        return width, height

    def _calculate_scale_factor(self, size: str) -> float:
        """
        Calculate scale factor relative to A1.

        Args:
            size: Paper size code.

        Returns:
            Scale factor (1.0 for A1, smaller for smaller sizes).
        """
        a1_width = self.SIZES["A1"][0]
        current_width = self.SIZES.get(size, self.SIZES["A1"])[0]
        return current_width / a1_width

    def _build_context(
        self,
        location: Location,
        template_type: str,
        size: str,
        orientation: str,
        language: str,
        epa_data: dict[str, Any],
        qr_codes: dict[str, str],
        scale_factor: float,
    ) -> dict[str, Any]:
        """
        Build template context.

        Args:
            location: Location model instance.
            template_type: Template code.
            size: Paper size.
            orientation: Portrait or landscape.
            language: Language code.
            epa_data: EPA data dict.
            qr_codes: QR code data URIs.
            scale_factor: Size scale factor.

        Returns:
            Context dict for template rendering.
        """
        # Get facilities as convenience booleans
        facilities = location.get_facilities()

        return {
            # Location data
            "location": location,
            "beach_name": location.get_name(language),
            "beach_name_en": location.name_en,
            "beach_name_ga": location.name_ga,
            "classification": location.classification,
            "is_identified": location.is_identified,
            "local_authority_name": location.local_authority.name if location.local_authority else "",
            # Custom notification (passed through from epa_data)
            "custom_notification": epa_data.get("custom_notification", ""),
            # EPA data
            "epa_data": epa_data,
            "water_quality_status": epa_data.get("classification", ""),
            "last_sample_date": epa_data.get("last_sample_date", ""),
            "ecoli_value": epa_data.get("ecoli_value"),
            "enterococci_value": epa_data.get("enterococci_value"),
            "has_active_alert": epa_data.get("has_active_alerts", False),
            "alert_details": epa_data.get("alert_details", {}),
            "recent_measurements": epa_data.get("recent_measurements", []),
            # Facilities
            "facilities": facilities,
            "has_toilets": facilities.get("toilets", False),
            "has_parking": facilities.get("parking", False),
            "has_lifeguard": facilities.get("lifeguard", False),
            "has_disability_access": facilities.get("disability_access", False),
            "has_blue_flag": facilities.get("blue_flag", False),
            "dogs_allowed": facilities.get("dogs_allowed", True),
            # QR codes
            "qr_codes": qr_codes,
            "qr_tide_tables": qr_codes.get("tide_tables", ""),
            "qr_weather": qr_codes.get("weather", ""),
            "qr_bathing_faq": qr_codes.get("bathing_faq", ""),
            "qr_beaches_ie": qr_codes.get("beaches_ie", ""),
            "qr_beach_url": qr_codes.get("beach_url", ""),
            # Poster settings
            "template_type": template_type,
            "size": size,
            "orientation": orientation,
            "language": language,
            "scale_factor": scale_factor,
            # Debug
            "debug_mode": epa_data.get("debug_mode", False),
        }

    def _get_print_css(
        self,
        width_mm: int,
        height_mm: int,
        scale_factor: float,
    ) -> str:
        """
        Generate CSS for print output.

        Args:
            width_mm: Page width in mm.
            height_mm: Page height in mm.
            scale_factor: Scale factor for fonts.

        Returns:
            CSS string.
        """
        # Base font sizes (for A1)
        base_title_size = 72
        base_subtitle_size = 48
        base_body_size = 24
        base_small_size = 18

        return f"""
        @page {{
            size: {width_mm}mm {height_mm}mm;
            margin: 10mm;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, Helvetica, sans-serif;
            font-size: {base_body_size * scale_factor}pt;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 0;
        }}

        .poster {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}

        .poster-header {{
            background-color: #006699;
            color: white;
            padding: {20 * scale_factor}mm;
            text-align: center;
        }}

        .poster-title {{
            font-size: {base_title_size * scale_factor}pt;
            font-weight: bold;
            margin: 0 0 {10 * scale_factor}mm 0;
        }}

        .poster-subtitle {{
            font-size: {base_subtitle_size * scale_factor}pt;
            margin: 0;
        }}

        .poster-content {{
            flex: 1;
            padding: {15 * scale_factor}mm;
        }}

        .water-quality {{
            background-color: #f8f8f8;
            padding: {15 * scale_factor}mm;
            border-radius: {5 * scale_factor}mm;
            margin-bottom: {15 * scale_factor}mm;
        }}

        .alert-box {{
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            padding: {10 * scale_factor}mm;
            border-radius: {5 * scale_factor}mm;
            margin-bottom: {15 * scale_factor}mm;
        }}

        .alert-box.danger {{
            background-color: #f8d7da;
            border-color: #dc3545;
        }}

        .facilities {{
            display: flex;
            flex-wrap: wrap;
            gap: {10 * scale_factor}mm;
        }}

        .facility {{
            display: flex;
            align-items: center;
            gap: {5 * scale_factor}mm;
        }}

        .qr-grid {{
            display: flex;
            justify-content: space-around;
            margin-top: {15 * scale_factor}mm;
        }}

        .qr-item {{
            text-align: center;
        }}

        .qr-item img {{
            width: {60 * scale_factor}mm;
            height: {60 * scale_factor}mm;
        }}

        .qr-label {{
            font-size: {base_small_size * scale_factor}pt;
            margin-top: {5 * scale_factor}mm;
        }}

        .poster-footer {{
            background-color: #f8f8f8;
            padding: {10 * scale_factor}mm;
            text-align: center;
            font-size: {base_small_size * scale_factor}pt;
        }}

        .section-title {{
            font-size: {base_subtitle_size * scale_factor}pt;
            font-weight: bold;
            color: #006699;
            margin-bottom: {10 * scale_factor}mm;
            border-bottom: 2px solid #006699;
            padding-bottom: {5 * scale_factor}mm;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: {5 * scale_factor}mm;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background-color: #006699;
            color: white;
        }}

        .status-excellent {{
            color: #28a745;
            font-weight: bold;
        }}

        .status-good {{
            color: #17a2b8;
            font-weight: bold;
        }}

        .status-sufficient {{
            color: #ffc107;
            font-weight: bold;
        }}

        .status-poor {{
            color: #dc3545;
            font-weight: bold;
        }}

        @media print {{
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
        """
