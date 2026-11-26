#!/usr/bin/env python3
"""Build or verify the portable skill ZIP using only the Python standard library."""

import argparse
import hashlib
import io
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "blue-ladder-content-studio"
DEFAULT_OUTPUT = ROOT / "dist" / f"{SKILL_NAME}.zip"
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "assets/icon.svg",
    "assets/infographic-input-example.json",
    "references/article-index.md",
    "references/stock-articles.md",
    "references/style-guide.md",
    "references/visual-guide.md",
    "scripts/select_examples.py",
    "scripts/make_kpi_infographic.py",
    "scripts/validate_html_zip.py",
    "requirements.txt",
)


def package_members():
    """Use an explicit file list so caches, local outputs and Git data stay out."""
    members = {}
    for relative in REQUIRED_FILES:
        source = ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"Missing or non-regular package file: {relative}")
        if not source.resolve().is_relative_to(ROOT):
            raise ValueError(f"Package file resolves outside this repository: {relative}")
        members[f"{SKILL_NAME}/{relative}"] = source.read_bytes()

    skill = members[f"{SKILL_NAME}/SKILL.md"].decode("utf-8")
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", skill, flags=re.S)
    if not frontmatter:
        raise ValueError("SKILL.md must begin with YAML frontmatter.")
    header = frontmatter.group(1)
    if not re.search(rf"(?m)^name:\s*{re.escape(SKILL_NAME)}\s*$", header):
        raise ValueError(f"SKILL.md name must be {SKILL_NAME}.")
    if not re.search(r"(?m)^description:\s*\S", header):
        raise ValueError("SKILL.md needs a non-empty description.")
    return members


def archive_bytes(members):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(members.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data, compresslevel=9)
    return output.getvalue()


def verify_archive(data, members):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(members):
            raise ValueError("ZIP file list does not match the distributable skill files.")
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"Corrupt ZIP member: {corrupt}")
        for name, expected in members.items():
            if archive.read(name) != expected:
                raise ValueError(f"ZIP content is out of date: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Check the existing ZIP and checksum without changing files")
    args = parser.parse_args()
    try:
        members = package_members()
        output = args.output.resolve()
        checksum_path = output.with_name(output.name + ".sha256")
        if args.check:
            data = output.read_bytes()
            verify_archive(data, members)
            checksum = f"{hashlib.sha256(data).hexdigest()}  {output.name}\n"
            if checksum_path.read_text(encoding="utf-8") != checksum:
                raise ValueError("ZIP checksum file is missing, invalid or out of date.")
            action = "Verified"
        else:
            data = archive_bytes(members)
            verify_archive(data, members)
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + ".tmp")
            temporary.write_bytes(data)
            temporary.replace(output)
            checksum = f"{hashlib.sha256(data).hexdigest()}  {output.name}\n"
            checksum_path.write_text(checksum, encoding="utf-8", newline="\n")
            action = "Created"
        print(f"{action} {output} ({len(members)} files, {len(data):,} bytes)")
        print(f"SHA-256: {hashlib.sha256(data).hexdigest()}")
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Skill package failed: {error}\n")


if __name__ == "__main__":
    main()
