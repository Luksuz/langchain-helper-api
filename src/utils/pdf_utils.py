import re


def rewrite_tailwind_play_to_static(html_input: str) -> str:
    """Replace Tailwind Play CDN <script> with a static CSS link compatible with wkhtmltopdf.

    The Play CDN is JavaScript-based and may not run under wkhtmltopdf's WebKit.
    Rewriting to a precompiled stylesheet yields deterministic rendering.
    """
    if "cdn.tailwindcss.com" not in html_input:
        return html_input

    return re.sub(
        r"<script[^>]*src=\"https://cdn\.tailwindcss\.com\"[^>]*></script>",
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">',
        html_input,
        flags=re.IGNORECASE,
    )


def rewrite_local_css_hrefs_to_file_urls(html_input: str) -> str:
    """Rewrite local CSS hrefs to absolute file:///app paths so wkhtmltopdf can load them.

    Supports href values like:
      - /assets/tailwind.min.css
      - assets/tailwind.min.css
      - tailwind.min.css
    Already-absolute file:// URLs are left unchanged.
    """

    def _rewrite(match: re.Match) -> str:
        quote = match.group(1)
        href = match.group(2)
        if href.startswith("file://"):
            return match.group(0)
        if href.startswith("/assets/"):
            new_href = "file:///app" + href
        elif href.startswith("assets/"):
            new_href = "file:///app/" + href
        elif href == "tailwind.min.css":
            new_href = "file:///app/assets/tailwind.min.css"
        else:
            return match.group(0)
        return match.group(0).replace(f"href={quote}{href}{quote}", f"href={quote}{new_href}{quote}")

    return re.sub(
        r"<link[^>]*rel=\"stylesheet\"[^>]*href=([\"\'])([^\"\']+)([\"\'])[^>]*>",
        _rewrite,
        html_input,
        flags=re.IGNORECASE,
    )


