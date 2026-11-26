#!/usr/bin/env python3
"""Validate an article ZIP with separate, relative image files (stdlib only)."""

import argparse
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit
import zipfile


MAX_ZIP_BYTES = 10_000_000
CSS_ESCAPE = re.compile(r"\\(?:([0-9a-fA-F]{1,6})(?:\r\n|[ \t\r\n\f])?|([^\r\n\f]))")
CSS_URL = re.compile(r'''\burl\s*\(\s*(?:"([^"]*)"|'([^']*)'|([^\s()'";]+))\s*\)''', re.I)


def css_image_references(css):
    """Read ordinary url() references; reject unsupported indirect URL syntax."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\\(?:\r\n|[\r\n\f])", "", css)

    def unescape(match):
        if match.group(1):
            value = int(match.group(1), 16)
            return chr(value) if 0 < value <= 0x10FFFF else "\ufffd"
        return match.group(2)

    css = CSS_ESCAPE.sub(unescape, css)
    if re.search(r"@import\b", css, re.I):
        raise ValueError("CSS @import is unsupported; use local <link rel='stylesheet'> files instead.")
    if re.search(r"\b(?:-webkit-image-set|image-set|image|attr)\s*\(", css, re.I):
        raise ValueError("Use ordinary CSS url(...) for images; image-set(), image(), and attr() are unsupported.")
    matches = list(CSS_URL.finditer(css))
    starts = {match.start() for match in matches}
    if any(match.start() not in starts for match in re.finditer(r"\burl\s*\(", css, re.I)):
        raise ValueError("CSS has an invalid or unsupported url(...); use a quoted static image path.")
    return [next(value for value in match.groups() if value is not None) for match in matches]


class ArticleImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.errors = []
        self.images = 0
        self.inline_css = []
        self.stylesheets = []
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "base":
            self.errors.append("HTML must not use <base>.")
        if "style" in attrs:
            self.inline_css.append(attrs["style"] or "")
        if tag == "style":
            self._in_style = True
        if tag == "link" and "stylesheet" in (attrs.get("rel") or "").lower().split():
            if not (attrs.get("href") or "").strip():
                self.errors.append("Every stylesheet link needs a non-empty href.")
            else:
                self.stylesheets.append(attrs["href"])
        if tag == "img":
            self.images += 1
            if not attrs.get("src", "").strip():
                self.errors.append("Every <img> needs a non-empty src.")
            else:
                self.references.append(attrs["src"])
            if not attrs.get("alt", "").strip():
                self.errors.append("Every content image needs descriptive alt text.")
        if tag in ("img", "source") and "srcset" in attrs:
            for candidate in attrs["srcset"].split(","):
                parts = candidate.strip().split()
                if parts:
                    self.references.append(parts[0])

    def handle_data(self, data):
        if self._in_style:
            self.inline_css.append(data)

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False


def resolve_reference(reference, origin, actual_files, stylesheet=False):
    """Resolve a relative URL exactly as HTML/CSS does, without leaving the ZIP."""
    reference = reference.strip()
    parsed = urlsplit(reference)
    path = unquote(parsed.path)
    if (
        parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
        or not path or path.startswith("/") or "\\" in path or ":" in path
        or any(ord(character) < 32 for character in path)
    ):
        raise ValueError(f"Resource must use a ZIP-relative path without a URL scheme: {reference}")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(origin), path))
    parts = PurePosixPath(resolved).parts
    if not parts or resolved.startswith("../") or resolved in (".", ".."):
        raise ValueError(f"Resource escapes the ZIP: {reference}")
    if stylesheet:
        if not resolved.lower().endswith(".css"):
            raise ValueError(f"Stylesheet must reference a local .css file: {reference}")
    elif parts[0] != "images":
        raise ValueError(f"Image must resolve to the ZIP's images/ folder: {reference}")
    if resolved not in actual_files:
        raise ValueError(f"Resource missing from ZIP (check spelling/case): {resolved}")
    return resolved


def validate(archive):
    if archive.stat().st_size > MAX_ZIP_BYTES:
        raise ValueError(f"ZIP exceeds 10MB: {archive.stat().st_size:,} bytes.")
    with zipfile.ZipFile(archive) as package:
        entries = package.infolist()
        names = [entry.filename for entry in entries]
        if len(set(names)) != len(names):
            raise ValueError("ZIP contains duplicate paths.")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise ValueError(f"Invalid ZIP path: {name}")
        html_files = [name for name in names if name.lower().endswith(".html")]
        if len(html_files) != 1 or len(PurePosixPath(html_files[0]).parts) != 1:
            raise ValueError("ZIP must contain exactly one HTML file at its root.")
        corrupt = package.testzip()
        if corrupt:
            raise ValueError(f"Corrupt ZIP member: {corrupt}")
        html = package.read(html_files[0]).decode("utf-8-sig")
        parser = ArticleImages()
        parser.feed(html)
        parser.close()
        if parser.errors:
            raise ValueError(" ".join(parser.errors))
        if not parser.images:
            raise ValueError("Article ZIP has no <img> tags; preserve article images.")
        if "data:image" in html.lower() or "base64," in html.lower():
            raise ValueError("HTML must not embed image data/base64.")
        actual_files = {entry.filename for entry in entries if not entry.is_dir()}
        for reference in parser.references:
            resolve_reference(reference, html_files[0], actual_files)
        for css in parser.inline_css:
            for reference in css_image_references(css):
                resolve_reference(reference, html_files[0], actual_files)
        for reference in parser.stylesheets:
            css_path = resolve_reference(reference, html_files[0], actual_files, stylesheet=True)
            css = package.read(css_path).decode("utf-8-sig")
            for image_reference in css_image_references(css):
                resolve_reference(image_reference, css_path, actual_files)
        return parser.images


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    try:
        count = validate(args.archive)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
    size = args.archive.stat().st_size
    print(f"OK: {size:,} bytes ({size / 1_000_000:.2f}MB), {count} image tags; ZIP paths resolve.")


if __name__ == "__main__":
    main()
