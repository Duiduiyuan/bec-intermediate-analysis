#!/usr/bin/env python3
"""Render model-prepared BEC bilingual paragraphs as annotated A4 PNGs."""

import argparse
import json
import random
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 2480, 3508
SCALE, SUPERSAMPLE = 3.125, 2
FACTOR = SCALE * SUPERSAMPLE
# Four output pixels protect the minimum margin from resampling/ink bearings.
MARGIN = 40 + 4 / SCALE
AVAILABLE = WIDTH / SCALE - 2 * MARGIN
PALETTES = {
    1: ("#FFFFF0", "#75B26B", "#C2E0A4", "#52734D"),
    2: ("#999B84", "#EFD9D1", "#CFA495", "#F4EEED"),
    3: ("#222831", "#FFD369", "#3C4046", "#EEEEEE"),
    4: ("#EFE8DD", "#303841", "#76ABAE", "#FF5722"),
    5: ("#F5F5F5", "#17444D", "#B8CCCC", "#FF0000"),
}


def find_font(explicit, chinese=False):
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ValueError(f"Font file does not exist: {path}")
        return path
    names = (
        ("SourceHanSansSC-Light.otf", "SourceHanSansSC-Light-2.otf")
        if chinese else ("Outfit-VariableFont_wght.ttf", "Outfit-Light.ttf")
    )
    for root in (Path(__file__).resolve().parents[1] / "assets/fonts",
                 Path.home() / "Library/Fonts", Path("/Library/Fonts")):
        for name in names:
            if (root / name).is_file():
                return root / name
    try:
        result = subprocess.run(
            ["fc-list", "--format", "%{file}\t%{family}\t%{style}\n"],
            check=True, capture_output=True, text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        result = None
    if result:
        for row in result.stdout.splitlines():
            file, family, style = row.split("\t", 2)
            family_ok = (
                "Source Han Sans SC" in family or "思源黑体" in family
                if chinese else "Outfit" in family
            )
            if family_ok and "Light" in style.split(","):
                return Path(file)
    name = "Source Han Sans SC Light" if chinese else "Outfit Light"
    flag = "--chinese-font" if chinese else "--english-font"
    raise ValueError(f"Missing {name}. Install it or provide its file using {flag}.")


def load_font(path, size, chinese=False):
    font = ImageFont.truetype(str(path), round(size * FACTOR))
    family, style = font.getname()
    expected = ("Source Han Sans SC", "思源黑体") if chinese else ("Outfit",)
    if not any(name in family for name in expected):
        raise ValueError(f"Wrong font family: {family}")
    try:
        axes = font.get_variation_axes()
    except OSError:
        axes = []
    if axes:
        values = [axis["default"] for axis in axes]
        for i, axis in enumerate(axes):
            if axis["name"] == b"Weight":
                values[i] = 300
                break
        else:
            raise ValueError(f"Cannot select Light weight for {path}")
        font.set_variation_by_axes(values)
    elif "light" not in style.lower() or "extralight" in style.lower():
        raise ValueError(f"Expected Light weight, got {style}: {path}")
    return font


def measure(text, font):
    return font.getlength(text) / FACTOR


def wrap_chinese(text, font):
    lines, line = [], ""
    for char in text:
        if line and measure(line + char, font) > AVAILABLE:
            carry = ""
            if char in "，。！？；：、）》】”’…" or line[-1] in "（《【“‘":
                carry, line = line[-1], line[:-1]
            lines.append(line)
            line = carry
        line += char
    if line:
        lines.append(line)
    return lines


def prepare_paragraph(row, number, english, chinese):
    text = " ".join(row["text"].split())
    translation = " ".join(row["translation"].split())
    if not text or not translation:
        raise ValueError(f"Paragraph {number}: English and translation are required.")
    if re.search(r"[\u3400-\u9fff]", text):
        raise ValueError(f"Paragraph {number}: remove supplied Chinese from source English.")
    notes = []
    for entry in row.get("notes", []):
        phrase, note = entry["phrase"], entry["note"]
        start = text.find(phrase)
        if not phrase or start < 0 or not note or "\n" in note:
            raise ValueError(f"Paragraph {number}: invalid note {entry!r}")
        end = start + len(phrase)
        if any(start < n[1] and end > n[0] for n in notes):
            raise ValueError(f"Paragraph {number}: overlapping annotated phrases.")
        notes.append((start, end, note))
    # Merge whitespace-delimited words touched by a multiword annotation.
    words = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    atoms, i = [], 0
    while i < len(words):
        start, end = words[i]
        while True:
            target = max([end] + [b for a, b, _ in notes if a < end and b > start])
            if target <= end:
                break
            while end < target:
                i += 1
                end = words[i][1]
        atoms.append((start, end))
        i += 1
    lines = []
    start, end = atoms[0]
    for a, b in atoms[1:]:
        if measure(text[start:b], english) > AVAILABLE:
            lines.append((start, end))
            start = a
        end = b
    lines.append((start, end))
    if any(measure(text[a:b], english) > AVAILABLE for a, b in lines):
        raise ValueError(f"Paragraph {number}: a word or annotated phrase exceeds page width.")
    if " ".join(text[a:b] for a, b in lines) != text:
        raise ValueError(f"Paragraph {number}: English changed during wrapping.")
    translated = wrap_chinese(translation, chinese)
    if len(translated) > 2:
        raise ValueError(
            f"Paragraph {number}: translation needs more than two lines; "
            "cannot fit the fixed 72px paragraph spacing. Keep the full meaning; "
            "request a layout adjustment if a concise translation still does not fit."
        )
    return {"number": number, "text": text, "lines": lines,
            "translation": translated, "notes": notes}


def render(paragraphs, english, chinese, style, output_dir):
    background, english_color, chinese_color, note_color = PALETTES[style]
    pages, page, y = [], [], MARGIN
    for para in paragraphs:
        last_offset = (len(para["lines"]) - 1) * 36
        tail = 62 if len(para["translation"]) == 1 else 68
        if y + last_offset + tail > HEIGHT / SCALE - MARGIN:
            if page:
                pages.append(page)
            page, y = [], MARGIN
        if y + last_offset + tail > HEIGHT / SCALE - MARGIN:
            raise ValueError(f"Paragraph {para['number']}: exceeds one full page; cannot split it.")
        page.append((para, y))
        y += last_offset + 72
    if page:
        pages.append(page)

    reports, images = [], []
    for page_number, page in enumerate(pages, 1):
        im = Image.new("RGB", (WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE), background)
        draw, boxes = ImageDraw.Draw(im), []

        def add_box(box, label):
            left, top, right, bottom = (n / FACTOR for n in box)
            if (left < 40 or top < 40 or right > WIDTH / SCALE - 40
                    or bottom > HEIGHT / SCALE - 40):
                raise ValueError(f"Page {page_number}, {label}: exceeds 40px margins.")
            for a, b, c, d, other in boxes:
                if left < c and right > a and top < d and bottom > b:
                    raise ValueError(
                        f"Page {page_number}: {label} overlaps {other}. "
                        "Shorten the note or select fewer annotations."
                    )
            boxes.append((left, top, right, bottom, label))

        def put(text, x, y, font, color, label):
            position = (round(x * FACTOR), round(y * FACTOR))
            add_box(draw.textbbox(position, text, font=font, anchor="lt"), label)
            draw.text(position, text, font=font, fill=color, anchor="lt")

        for para, y in page:
            number, text = para["number"], para["text"]
            for line_number, (a, b) in enumerate(para["lines"]):
                line_y = y + line_number * 36
                put(text[a:b], MARGIN, line_y, english, english_color,
                    f"paragraph {number} English line {line_number + 1}")
                for start, end, note in para["notes"]:
                    if not (a <= start < end <= b):
                        continue
                    left = MARGIN + measure(text[a:start], english)
                    right = MARGIN + measure(text[a:end], english)
                    middle = (left + right) / 2
                    label = f"paragraph {number} note {text[start:end]!r}"
                    underline = tuple(round(v * FACTOR) for v in
                                      (left, line_y + 22, right, line_y + 22))
                    add_box((underline[0], underline[1] - SUPERSAMPLE,
                             underline[2], underline[3] + SUPERSAMPLE), label + " underline")
                    draw.line(underline, fill=note_color, width=2 * SUPERSAMPLE)
                    put(note, middle - measure(note, chinese) / 2,
                        line_y + 24, chinese, note_color, label)
            last_y = y + (len(para["lines"]) - 1) * 36
            translation_y = last_y + (48 if len(para["translation"]) == 1 else 40)
            for i, line in enumerate(para["translation"]):
                put(line, MARGIN, translation_y + i * 14, chinese, chinese_color,
                    f"paragraph {number} translation line {i + 1}")

        path = output_dir / f"{output_dir.name}-{page_number:02d}.png"
        images.append((im.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS), path))
        reports.append({"path": str(path), "paragraphs": [p["number"] for p, _ in page]})
    # Validate every page before writing any output.
    output_dir.mkdir(parents=True, exist_ok=True)
    for im, path in images:
        im.save(path, optimize=True)
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON containing paragraphs")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--style", type=int, choices=PALETTES)
    parser.add_argument("--english-font")
    parser.add_argument("--chinese-font")
    args = parser.parse_args()
    style = args.style if args.style is not None else random.choice(list(PALETTES))
    print(json.dumps({"style": style}, ensure_ascii=False), flush=True)
    try:
        english = load_font(find_font(args.english_font), 20)
        chinese = load_font(find_font(args.chinese_font, chinese=True), 12, chinese=True)
        data = json.loads(args.input.read_text(encoding="utf-8"))
        if not data["paragraphs"]:
            raise ValueError("At least one English paragraph is required.")
        paragraphs = [prepare_paragraph(p, i, english, chinese)
                      for i, p in enumerate(data["paragraphs"], 1)]
        pages = render(paragraphs, english, chinese, style, args.output_dir.resolve())
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"Style {style}: {error}\n")
    print(json.dumps({"style": style, "size": [WIDTH, HEIGHT],
                      "paragraph_count": len(paragraphs), "pages": pages}, ensure_ascii=False))


if __name__ == "__main__":
    main()
