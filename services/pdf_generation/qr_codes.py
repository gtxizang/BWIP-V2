"""
QR code generation utilities.

Provides functions for generating QR codes for poster use.
"""

import base64
import io
import logging
from typing import NamedTuple

import qrcode
from PIL import Image

from .exceptions import QRCodeGenerationError

logger = logging.getLogger(__name__)


class QRCodeConfig(NamedTuple):
    """Configuration for a QR code."""

    data: str
    label: str


# Standard QR codes used in posters
STANDARD_QR_CODES = {
    "tide_tables": QRCodeConfig(
        data="https://www.met.ie/forecasts/marine-tides",
        label="Tide Tables",
    ),
    "weather": QRCodeConfig(
        data="https://www.met.ie/forecasts/beach",
        label="Weather Forecast",
    ),
    "bathing_faq": QRCodeConfig(
        data="https://www.beaches.ie/faq",
        label="Bathing FAQ",
    ),
    "beaches_ie": QRCodeConfig(
        data="https://www.beaches.ie",
        label="beaches.ie",
    ),
}


def generate_qr_code(
    data: str,
    size: int = 200,
    error_correction: int = qrcode.constants.ERROR_CORRECT_M,
) -> bytes:
    """
    Generate a QR code image.

    Args:
        data: The data to encode in the QR code.
        size: Size of the QR code in pixels.
        error_correction: Error correction level.

    Returns:
        PNG image bytes.

    Raises:
        QRCodeGenerationError: If generation fails.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Resize if needed
        if img.size[0] != size:
            img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        raise QRCodeGenerationError(f"Failed to generate QR code: {e}")


def generate_qr_code_base64(data: str, size: int = 200) -> str:
    """
    Generate a QR code as a base64 data URI.

    Args:
        data: The data to encode in the QR code.
        size: Size of the QR code in pixels.

    Returns:
        Base64 data URI string for embedding in HTML.
    """
    image_bytes = generate_qr_code(data, size)
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def generate_poster_qr_codes(size: int = 200) -> dict[str, str]:
    """
    Generate all standard QR codes for a poster.

    Args:
        size: Size of each QR code in pixels.

    Returns:
        Dict mapping QR code names to base64 data URIs.
    """
    qr_codes = {}
    for name, config in STANDARD_QR_CODES.items():
        try:
            qr_codes[name] = generate_qr_code_base64(config.data, size)
        except QRCodeGenerationError:
            logger.warning(f"Failed to generate QR code: {name}")
            qr_codes[name] = ""
    return qr_codes


def generate_beach_url_qr_code(beach_id: str, size: int = 200) -> str:
    """
    Generate a QR code for a specific beach page.

    Args:
        beach_id: The beaches.ie beach identifier.
        size: Size of the QR code in pixels.

    Returns:
        Base64 data URI string.
    """
    url = f"https://www.beaches.ie/beach/{beach_id}"
    return generate_qr_code_base64(url, size)
