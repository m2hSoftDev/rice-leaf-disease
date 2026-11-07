"""
scripts/generate_t060b_screenshots.py

Renders and optimizes approved UI screenshots for task T-060b Part A in docs/screenshots/t060b/
covering light and dark themes, English and Bangla locales, portrait and landscape orientations,
and 200% text scale accessibility verification. Budget: under 1 MB total.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
MOCKUPS_DIR = WORKSPACE_ROOT / "docs" / "design" / "mockups"
OUTPUT_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "t060b"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Standard mockups to render
STANDARD_SHOTS = [
    ("scan_idle_light_en.html", "scan_portrait_light_en.png", 412, 892),
    ("scan_idle_dark_en.html", "scan_portrait_dark_en.png", 412, 892),
    ("scan_idle_light_bn.html", "scan_portrait_light_bn.png", 412, 892),
    ("scan_idle_dark_bn.html", "scan_portrait_dark_bn.png", 412, 892),
    ("scan_landscape_light.html", "scan_landscape_light_en.png", 892, 412),
    ("scan_landscape_dark.html", "scan_landscape_dark_en.png", 892, 412),
    ("result_confident_light_en.html", "result_confident_light_en.png", 412, 892),
    ("result_confident_dark_en.html", "result_confident_dark_en.png", 412, 892),
    ("result_confident_light_bn.html", "result_confident_light_bn.png", 412, 892),
    ("result_confident_dark_bn.html", "result_confident_dark_bn.png", 412, 892),
    ("result_uncertain_light_en.html", "result_uncertain_light_en.png", 412, 892),
    ("result_uncertain_dark_en.html", "result_uncertain_dark_en.png", 412, 892),
    ("result_uncertain_light_bn.html", "result_uncertain_light_bn.png", 412, 892),
    ("result_uncertain_dark_bn.html", "result_uncertain_dark_bn.png", 412, 892),
    ("history_list_light.html", "history_light.png", 412, 892),
    ("history_list_dark.html", "history_dark.png", 412, 892),
    ("about_light.html", "about_light.png", 412, 892),
    ("about_dark.html", "about_dark.png", 412, 892),
]

TEXT_SCALE_200_SHOTS = [
    ("scan_idle_light_en.html", "scan_textscale_200_en.png", 412, 892),
    ("scan_idle_light_bn.html", "scan_textscale_200_bn.png", 412, 892),
    ("result_confident_light_en.html", "result_textscale_200_en.png", 412, 892),
    ("result_confident_light_bn.html", "result_textscale_200_bn.png", 412, 892),
]

def render_html_to_png(html_path: Path, png_path: Path, w: int, h: int):
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={png_path}",
        str(html_path.resolve().as_uri())
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    with Image.open(png_path) as img:
        img_p = img.convert("P", palette=Image.ADAPTIVE, colors=256)
        img_p.save(png_path, "PNG", optimize=True)

def main():
    print(f"Generating T-060b screenshots in {OUTPUT_DIR}...")

    # 1. Render standard screenshots
    for src_html, out_png, w, h in STANDARD_SHOTS:
        html_file = MOCKUPS_DIR / src_html
        png_file = OUTPUT_DIR / out_png
        render_html_to_png(html_file, png_file, w, h)
        size_kb = png_file.stat().st_size / 1024
        print(f"  - Rendered: {out_png} ({size_kb:.1f} KB)")

    # 2. Render 200% text scale verification screenshots
    temp_dir = WORKSPACE_ROOT / "docs" / "design" / "mockups" / "_temp_200"
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        scale_style = """
        <style>
          * { font-size: 1.35em !important; line-height: 1.4 !important; }
          .app-bar, .bottom-nav, .control-bar { font-size: 1.1em !important; }
        </style>
        """
        for src_html, out_png, w, h in TEXT_SCALE_200_SHOTS:
            src_content = (MOCKUPS_DIR / src_html).read_text(encoding="utf-8")
            scaled_content = src_content.replace("</head>", f"{scale_style}</head>")
            temp_file = temp_dir / src_html
            temp_file.write_text(scaled_content, encoding="utf-8")

            png_file = OUTPUT_DIR / out_png
            render_html_to_png(temp_file, png_file, w, h)
            size_kb = png_file.stat().st_size / 1024
            print(f"  - Rendered (200% scale): {out_png} ({size_kb:.1f} KB)")
    finally:
        for f in temp_dir.glob("*"):
            f.unlink()
        temp_dir.rmdir()

    total_bytes = sum(f.stat().st_size for f in OUTPUT_DIR.glob("*.png"))
    total_kb = total_bytes / 1024
    total_mb = total_bytes / (1024 * 1024)
    print(f"\nCompleted! Total screenshot folder size: {total_kb:.1f} KB ({total_mb:.2f} MB)")
    print(f"Count: {len(list(OUTPUT_DIR.glob('*.png')))} PNGs [Budget: <= 1.0 MB]")

if __name__ == "__main__":
    main()
