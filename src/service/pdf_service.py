from __future__ import annotations

import io
import os
from typing import Optional

import pdfkit

from ..utils.pdf_utils import (
    rewrite_tailwind_play_to_static,
    rewrite_local_css_hrefs_to_file_urls,
)


def render_html_to_pdf_bytes(html: str, javascript_delay_ms: int = 2000) -> bytes:
    """Render HTML to PDF bytes using wkhtmltopdf via pdfkit.

    - Rewrites Tailwind Play CDN to a static CSS link for deterministic rendering
    - Rewrites local CSS hrefs to absolute file:/// URLs within /app
    - Enables JS and adds a small delay for any runtime scripts
    """

    html_input = rewrite_tailwind_play_to_static(html)
    html_input = rewrite_local_css_hrefs_to_file_urls(html_input)

    # Configure wkhtmltopdf binary if set
    wkhtml = os.environ.get("WKHTMLTOPDF_CMD")
    config = pdfkit.configuration(wkhtmltopdf=wkhtml) if wkhtml else None

    options = {
        "enable-javascript": None,
        "javascript-delay": javascript_delay_ms,
        "no-stop-slow-scripts": None,
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore",
        "enable-local-file-access": None,
    }

    return pdfkit.from_string(html_input, False, configuration=config, options=options)


