#!/usr/bin/env python3
"""Add the user's x/y/z key to screenshot prices, without editing source JPEGs.

Prices and LONG/SHORT badges are transcribed, not calculated or fetched live.
The CSV's pixel coordinates identify the last blue price point, NOT projected
candles or targets (especially on SPCX). Re-run from any directory with:

    python3 scripts/label_current_prices.py

Requires Pillow and the DejaVu Sans fonts (or pass --font-dir).
"""

import argparse
import csv
import math
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "current_price_points.csv"
REPORT_PATH = ROOT / "Triangle Signals.md"
BEGIN_TABLE = "<!-- current-prices:start -->"
END_TABLE = "<!-- current-prices:end -->"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FOOTER_HEIGHT = 260
POINT_RADIUS = 15
BADGE_RADIUS = 42
BADGE_OFFSET = (72, -78)
BACKGROUND = "#0d131e"
WHITE = "#f1f5f9"
MUTED = "#a8b5c8"
SIGNALS = {
    "x": {"label": "Long", "color": "#22c55e", "emoji": "🟢"},
    "y": {"label": "Short", "color": "#ef4444", "emoji": "🔴"},
    "z": {"label": "Hazard", "color": "#f59e0b", "emoji": "🟠"},
}
BADGE_MARKERS = {"LONG": "x", "SHORT": "y"}


def load_points(path=DATA_PATH):
    """Fail rather than silently assigning a signal to an unrecognized badge."""
    with Path(path).open(encoding="utf-8", newline="") as source:
        points = list(csv.DictReader(source))
    seen = set()
    for point in points:
        ticker = point["ticker"]
        if ticker in seen:
            raise ValueError(f"Duplicate current point: {ticker}")
        seen.add(ticker)
        datetime.strptime(point["captured_local"], "%Y-%m-%d %H:%M:%S")
        price = Decimal(point["price_usd"])
        if not price.is_finite() or price <= 0:
            raise ValueError(f"Invalid price for {ticker}")
        expected = BADGE_MARKERS.get(point["chart_bias"])
        if expected is None or point["marker"] != expected:
            raise ValueError(f"Current-price marker must match the source badge: {ticker}")
        # No current screenshot carries an explicit Hazard badge. Historical
        # orange warning points remain z/Hazard in the report; never infer a new
        # current warning from a down day or an old triangle.
        image_path = (ROOT / point["source_image"]).resolve()
        if not image_path.is_relative_to(ROOT / "Charts"):
            raise ValueError(f"Source must be inside Charts: {ticker}")
        with Image.open(image_path) as image:
            x, y = int(point["point_x_px"]), int(point["point_y_px"])
            if image.size != (3024, 1964):
                raise ValueError(f"Recheck pixel coordinates for resized source: {ticker}")
            if not (0 <= x < image.width and 0 <= y < image.height):
                raise ValueError(f"Point outside chart: {ticker}")
    return points


def output_path(point):
    date = point["captured_local"].split()[0]
    return ROOT / "Charts" / point["ticker"] / f"{point['ticker']}-{date}-labeled.png"


def font(size, directory=FONT_DIR, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(Path(directory) / name), size)


def draw_marker(draw, anchor, symbol, font_directory=FONT_DIR):
    """Keep the price line visible inside a ring; put the letter beside it."""
    color = SIGNALS[symbol]["color"]
    x, y = anchor
    bx, by = x + BADGE_OFFSET[0], y + BADGE_OFFSET[1]
    length = math.hypot(bx - x, by - y)
    ux, uy = (bx - x) / length, (by - y) / length
    line = (
        x + ux * POINT_RADIUS, y + uy * POINT_RADIUS,
        bx - ux * BADGE_RADIUS, by - uy * BADGE_RADIUS,
    )
    draw.line(line, fill=BACKGROUND, width=8)
    draw.line(line, fill=color, width=4)
    draw.ellipse(
        (x - POINT_RADIUS, y - POINT_RADIUS, x + POINT_RADIUS, y + POINT_RADIUS),
        outline=color, width=4,
    )
    draw.ellipse(
        (bx - BADGE_RADIUS, by - BADGE_RADIUS, bx + BADGE_RADIUS, by + BADGE_RADIUS),
        fill=BACKGROUND, outline=color, width=3,
    )
    draw.text(
        (bx, by - 3), symbol, fill=color,
        font=font(66, font_directory, bold=True), anchor="mm",
    )


def render_point(point, font_directory=FONT_DIR):
    symbol = point["marker"]
    signal = SIGNALS[symbol]
    with Image.open(ROOT / point["source_image"]) as image:
        source = image.convert("RGB")
    # Paste at original resolution. Only the small marker is drawn on the
    # screenshot; the explanatory text sits in a NEW footer below it.
    result = Image.new("RGB", (source.width, source.height + FOOTER_HEIGHT), BACKGROUND)
    result.paste(source, (0, 0))
    draw = ImageDraw.Draw(result)
    anchor = int(point["point_x_px"]), int(point["point_y_px"])
    draw_marker(draw, anchor, symbol, font_directory)

    top = source.height
    draw.line((0, top + 1, source.width, top + 1), fill="#334155", width=3)
    date = point["captured_local"].split()[0]
    draw.text(
        (150, top + 28), f"{point['ticker']}  /  {date} SCREENSHOT  /  {point['interval']}",
        fill=MUTED, font=font(27, font_directory),
    )
    draw.text(
        (150, top + 75), symbol, fill=signal["color"],
        font=font(60, font_directory, bold=True),
    )
    draw.text(
        (220, top + 88), f"{signal['label']}  ·  USD {point['price_usd']}",
        fill=WHITE, font=font(43, font_directory, bold=True),
    )
    draw.text(
        (150, top + 176), "Current = price shown in the screenshot, not a live quote.",
        fill=MUTED, font=font(27, font_directory),
    )
    draw.line((1490, top + 30, 1490, top + 225), fill="#334155", width=2)
    draw.text(
        (1600, top + 28), "PRICE-POINT KEY", fill=MUTED,
        font=font(27, font_directory),
    )
    for left, (letter, key) in zip((1600, 1990, 2380), SIGNALS.items()):
        draw.text(
            (left, top + 78), letter, fill=key["color"],
            font=font(54, font_directory, bold=True),
        )
        draw.text(
            (left + 65, top + 94), key["label"], fill=WHITE,
            font=font(34, font_directory, bold=True),
        )
    draw.text(
        (1600, top + 176), "Current label follows the original LONG/SHORT badge.",
        fill=MUTED, font=font(26, font_directory),
    )
    destination = output_path(point)
    result.save(destination, format="PNG", optimize=True)
    return destination


def markdown_table(points):
    lines = [
        "| Ticker | Chart | Current displayed price (USD) | Label | Annotated chart |",
        "|---|---|---|---|---|",
    ]
    for point in points:
        signal = SIGNALS[point["marker"]]
        path = output_path(point).relative_to(ROOT).as_posix()
        label = f"{signal['emoji']} **{point['marker']} — {signal['label']}**"
        lines.append(
            f"| **{point['ticker']}** | {point['interval']} | **${point['price_usd']}** "
            f"| {label} | [View labeled chart]({path}) |"
        )
    return "\n".join(lines)


def update_report(points):
    text = REPORT_PATH.read_text(encoding="utf-8")
    if text.count(BEGIN_TABLE) != 1 or text.count(END_TABLE) != 1:
        raise ValueError("The report must contain one current-prices table placeholder")
    before, rest = text.split(BEGIN_TABLE, 1)
    _, after = rest.split(END_TABLE, 1)
    REPORT_PATH.write_text(
        before + BEGIN_TABLE + "\n" + markdown_table(points) + "\n" + END_TABLE + after,
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=FONT_DIR)
    args = parser.parse_args()
    points = load_points()
    # Fail on missing fonts before generating any files.
    font(26, args.font_dir)
    font(26, args.font_dir, bold=True)
    for point in points:
        print(render_point(point, args.font_dir).relative_to(ROOT))
    update_report(points)
    print(f"Updated {len(points)} current-price labels and {REPORT_PATH.name}.")


if __name__ == "__main__":
    main()
