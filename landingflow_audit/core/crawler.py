"""PageCrawler module for discovering and parsing HTML files from local directory."""

import os
from html.parser import HTMLParser
from pathlib import Path


class LandingPageParser(HTMLParser):
    """Custom HTML parser to extract anchors, forms, and CTAs."""

    CTA_PATTERNS = [
        "start free trial",
        "request demo",
        "sign up",
        "get started",
        "buy now",
        "subscribe",
        "try free",
        "book a demo",
        "contact us",
        "learn more"
    ]

    def __init__(self):
        super().__init__()
        self.anchors = []
        self.forms = []
        self.ctas = []
        self.current_form = None
        self.current_tag = None
        self.current_attrs = {}

    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        self.current_tag = tag
        self.current_attrs = dict(attrs)

        if tag == "a":
            # Extract anchor tag
            href = self.current_attrs.get("href", "")
            if href:
                self.anchors.append({
                    "href": href,
                    "text": "",  # Will be filled by handle_data
                    "attrs": self.current_attrs
                })

        elif tag == "form":
            # Start tracking a form
            self.current_form = {
                "action": self.current_attrs.get("action", ""),
                "method": self.current_attrs.get("method", "get").lower(),
                "inputs": []
            }

        elif tag == "input" and self.current_form is not None:
            # Add input to current form
            input_data = {
                "type": self.current_attrs.get("type", "text"),
                "name": self.current_attrs.get("name", ""),
                "required": "required" in self.current_attrs
            }
            self.current_form["inputs"].append(input_data)

        elif tag == "button":
            # Buttons can also be CTAs, track current tag for data handling
            pass

    def handle_endtag(self, tag):
        """Handle closing HTML tags."""
        if tag == "form" and self.current_form is not None:
            # Form ended, save it
            self.forms.append(self.current_form)
            self.current_form = None

        self.current_tag = None
        self.current_attrs = {}

    def handle_data(self, data):
        """Handle text content within tags."""
        text = data.strip()
        if not text:
            return

        # Fill in anchor text
        if self.current_tag == "a" and self.anchors:
            # Update the last anchor's text
            if not self.anchors[-1]["text"]:
                self.anchors[-1]["text"] = text

        # Detect CTA patterns in text
        text_lower = text.lower()
        for pattern in self.CTA_PATTERNS:
            if pattern in text_lower:
                cta_entry = {
                    "text": text,
                    "element": self.current_tag or "text",
                    "pattern_matched": pattern
                }
                # Avoid duplicates (same text and element)
                if not any(c["text"] == text and c["element"] == cta_entry["element"] for c in self.ctas):
                    self.ctas.append(cta_entry)
                break


class PageCrawler:
    """Discovers and parses HTML files from a local directory structure.

    The PageCrawler scans the specified data directory for HTML files,
    parses their content, and extracts relevant metadata for analysis.
    Uses only Python standard library (html.parser, pathlib).
    """

    def __init__(self, data_dir):
        """Initialize the PageCrawler with a target directory.

        Args:
            data_dir: Path to the directory containing HTML files to crawl.
        """
        self.data_dir = Path(data_dir)

    def crawl(self) -> dict:
        """Crawl the data directory and parse all HTML files.

        Returns:
            dict: Structured data containing:
                - pages: List of HTML file paths (relative to data_dir)
                - anchors: List of anchor tags with href, text, source_page
                - forms: List of forms with action, method, inputs, source_page
                - ctas: List of CTAs with text, element, source_page
        """
        pages = []
        all_anchors = []
        all_forms = []
        all_ctas = []

        # Walk directory tree depth-first
        for root, dirs, files in os.walk(self.data_dir, followlinks=True):
            for filename in files:
                if filename.endswith(".html"):
                    file_path = Path(root) / filename

                    # Get relative path from data_dir
                    try:
                        relative_path = file_path.relative_to(self.data_dir)
                    except ValueError:
                        # If file is outside data_dir (shouldn't happen), use name
                        relative_path = Path(filename)

                    pages.append(str(relative_path))

                    # Parse the HTML file
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            html_content = f.read()

                        parser = LandingPageParser()
                        parser.feed(html_content)

                        # Add source_page to all extracted items
                        for anchor in parser.anchors:
                            all_anchors.append({
                                "href": anchor["href"],
                                "text": anchor["text"],
                                "source_page": str(relative_path)
                            })

                        for form in parser.forms:
                            all_forms.append({
                                "action": form["action"],
                                "method": form["method"],
                                "inputs": form["inputs"],
                                "source_page": str(relative_path)
                            })

                        for cta in parser.ctas:
                            all_ctas.append({
                                "text": cta["text"],
                                "element": cta["element"],
                                "source_page": str(relative_path)
                            })

                    except Exception as e:
                        # Handle malformed HTML gracefully - log but continue
                        print(f"Warning: Failed to parse {relative_path}: {e}")
                        continue

        return {
            "pages": pages,
            "anchors": all_anchors,
            "forms": all_forms,
            "ctas": all_ctas
        }
