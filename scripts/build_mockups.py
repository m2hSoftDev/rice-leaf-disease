"""
scripts/build_mockups.py

Generates standalone Material 3 HTML wireframes in docs/design/mockups/,
renders them to PNG in docs/screenshots/design_proposal/ using Chrome headless,
optimizes PNGs under 2 MB, and creates docs/design/index.html.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
MOCKUPS_DIR = WORKSPACE_ROOT / "docs" / "design" / "mockups"
SCREENSHOTS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "design_proposal"
INDEX_HTML = WORKSPACE_ROOT / "docs" / "design" / "index.html"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

MOCKUPS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Shared CSS Template
CSS_BASE = """
:root {
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Bengali", sans-serif;
  --bg-color: #F8FAF6;
  --surface-color: #FFFFFF;
  --surface-variant: #EEF2EB;
  --surface-container: #F0F4ED;
  --on-surface: #191C19;
  --on-surface-variant: #424940;
  --primary: #236A34;
  --primary-container: #A7F3B3;
  --on-primary: #FFFFFF;
  --on-primary-container: #00210A;
  --outline: #72796F;
  --outline-variant: #C2C8BE;
  --error: #BA1A1A;
  --error-container: #FFDAD6;
  --on-error-container: #410002;
  --nav-bg: #F0F4ED;
  --card-border: rgba(0, 0, 0, 0.06);
}

[data-theme="dark"] {
  --bg-color: #111411;
  --surface-color: #191C19;
  --surface-variant: #2D312C;
  --surface-container: #191C19;
  --on-surface: #E1E3DF;
  --on-surface-variant: #C2C8BE;
  --primary: #8CD699;
  --primary-container: #055320;
  --on-primary: #003914;
  --on-primary-container: #A7F3B3;
  --outline: #8C9388;
  --outline-variant: #424940;
  --error: #FFB4AB;
  --error-container: #4D0005;
  --on-error-container: #FFDAD6;
  --nav-bg: #151815;
  --card-border: rgba(255, 255, 255, 0.08);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
}

body {
  width: 412px;
  height: 892px;
  background-color: var(--bg-color);
  color: var(--on-surface);
  font-family: var(--font-family);
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

body.landscape {
  width: 892px;
  height: 412px;
  flex-direction: row;
}

/* Status Bar */
.status-bar {
  height: 24px;
  background-color: var(--surface-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-size: 11px;
  font-weight: 600;
  color: var(--on-surface);
  flex-shrink: 0;
  z-index: 10;
}
.status-bar.transparent {
  background: transparent;
  color: #FFFFFF;
  text-shadow: 0 1px 2px rgba(0,0,0,0.8);
}
.status-icons {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* App Bar */
.app-bar {
  height: 56px;
  background-color: var(--surface-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--card-border);
  z-index: 10;
}
.app-bar.scrim {
  background: linear-gradient(to bottom, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0) 100%);
  border-bottom: none;
  color: #FFFFFF;
}
.app-bar-title {
  font-size: 19px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: -0.2px;
}
.app-bar.scrim .app-bar-title {
  color: #FFFFFF;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}
.icon-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
}
.lang-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 16px;
  background: var(--surface-variant);
  color: var(--primary);
  border: 1px solid var(--outline-variant);
}
.app-bar.scrim .lang-badge {
  background: rgba(0,0,0,0.4);
  color: #FFFFFF;
  border: 1px solid rgba(255,255,255,0.3);
}

/* Content Area */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

/* Cards */
.card {
  background-color: var(--surface-color);
  border-radius: 18px;
  padding: 16px;
  border: 1px solid var(--card-border);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-tonal {
  background-color: var(--surface-variant);
}
.card-primary {
  background-color: var(--primary-container);
  color: var(--on-primary-container);
  border: none;
}
.card-error {
  background-color: var(--error-container);
  color: var(--on-error-container);
  border: none;
}

/* Typography */
.title-lg { font-size: 22px; font-weight: 700; }
.title-md { font-size: 16px; font-weight: 600; }
.body-md { font-size: 14px; line-height: 1.4; color: var(--on-surface-variant); }
.body-sm { font-size: 12px; color: var(--on-surface-variant); }

/* Buttons */
.btn-primary {
  height: 48px;
  background-color: var(--primary);
  color: var(--on-primary);
  border-radius: 14px;
  border: none;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  width: 100%;
}
.btn-outlined {
  height: 48px;
  background-color: transparent;
  color: var(--primary);
  border: 1.5px solid var(--outline);
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  width: 100%;
}

/* NavigationBar */
.bottom-nav {
  height: 80px;
  background-color: var(--nav-bg);
  display: flex;
  align-items: center;
  justify-content: space-around;
  flex-shrink: 0;
  border-top: 1px solid var(--card-border);
  z-index: 10;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--on-surface-variant);
  font-size: 12px;
  font-weight: 500;
  width: 64px;
}
.nav-item.active {
  color: var(--on-surface);
  font-weight: 700;
}
.nav-pill {
  width: 60px;
  height: 32px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.nav-item.active .nav-pill {
  background-color: var(--primary-container);
  color: var(--on-primary-container);
}

/* Full Bleed Camera Preview */
.camera-viewport {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}
.viewfinder-frame {
  position: absolute;
  top: 48%;
  left: 50%;
  transform: translate(-50%, -55%);
  width: 250px;
  height: 250px;
  border: 2px dashed rgba(255,255,255,0.7);
  border-radius: 20px;
  box-shadow: 0 0 0 2000px rgba(0,0,0,0.3);
  z-index: 2;
  pointer-events: none;
}
.vf-bracket {
  position: absolute;
  width: 24px;
  height: 24px;
  border-color: #A7F3B3;
  border-style: solid;
}
.vf-tl { top: -3px; left: -3px; border-width: 4px 0 0 4px; border-top-left-radius: 20px; }
.vf-tr { top: -3px; right: -3px; border-width: 4px 4px 0 0; border-top-right-radius: 20px; }
.vf-bl { bottom: -3px; left: -3px; border-width: 0 0 4px 4px; border-bottom-left-radius: 20px; }
.vf-br { bottom: -3px; right: -3px; border-width: 0 4px 4px 0; border-bottom-right-radius: 20px; }

.guidance-chip {
  position: absolute;
  top: 66%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.75);
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.25);
  white-space: nowrap;
  z-index: 3;
}

.capture-overlay {
  position: absolute;
  bottom: 80px; /* Above nav bar */
  left: 0;
  width: 100%;
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 8px;
}

.disclaimer-strip {
  background: rgba(25, 28, 25, 0.88);
  color: #E1E3DF;
  font-size: 11px;
  padding: 6px 14px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.18);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  cursor: pointer;
  max-width: 90%;
}

.control-panel {
  width: 100%;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 24px;
}
.control-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}
.btn-gallery {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #FFFFFF;
}
.shutter-outer {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  border: 3.5px solid #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.shutter-inner {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.btn-help {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #FFFFFF;
}

/* Landscape Dock */
.landscape-preview {
  flex: 1;
  position: relative;
  height: 100%;
  overflow: hidden;
}
.landscape-dock {
  width: 130px;
  height: 100%;
  background: rgba(17, 20, 17, 0.95);
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
  padding: 16px 0;
  border-left: 1px solid rgba(255,255,255,0.12);
  z-index: 10;
}
"""

def generate_svg_camera_bg(width=412, height=892):
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:0;">
      <defs>
        <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#1B381B"/>
          <stop offset="50%" stop-color="#2D5A27"/>
          <stop offset="100%" stop-color="#132613"/>
        </linearGradient>
        <radialGradient id="sun" cx="0.8" cy="0.15" r="0.8">
          <stop offset="0%" stop-color="rgba(255,255,220,0.3)"/>
          <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
        </radialGradient>
      </defs>
      <rect width="{width}" height="{height}" fill="url(#bgGrad)"/>
      <rect width="{width}" height="{height}" fill="url(#sun)"/>
      <!-- Realistic Rice Leaf blade in focus -->
      <path d="M {width*0.5} 0 Q {width*0.6} {height*0.4} {width*0.5} {height} Q {width*0.4} {height*0.4} {width*0.5} 0 Z" fill="#5F9346" stroke="#3F6B2C" stroke-width="3"/>
      <line x1="{width*0.5}" y1="0" x2="{width*0.5}" y2="{height}" stroke="#80BC64" stroke-width="2"/>
      <!-- Brown spot lesions on leaf -->
      <ellipse cx="{width*0.48}" cy="{height*0.42}" rx="14" ry="8" fill="#5D4037" opacity="0.9"/>
      <ellipse cx="{width*0.48}" cy="{height*0.42}" rx="8" ry="4" fill="#A1887F" opacity="0.95"/>
      <ellipse cx="{width*0.52}" cy="{height*0.47}" rx="10" ry="6" fill="#5D4037" opacity="0.9"/>
      <ellipse cx="{width*0.47}" cy="{height*0.52}" rx="16" ry="9" fill="#5D4037" opacity="0.9"/>
      <ellipse cx="{width*0.47}" cy="{height*0.52}" rx="9" ry="5" fill="#A1887F" opacity="0.95"/>
    </svg>
    """

def generate_svg_leaf():
    return """
    <svg width="100%" height="160" viewBox="0 0 380 160" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="380" height="160" rx="14" fill="#2E4A28"/>
      <path d="M20 80 Q 190 20 360 80 Q 190 140 20 80 Z" fill="#4C8C40" stroke="#386B2E" stroke-width="2"/>
      <line x1="20" y1="80" x2="360" y2="80" stroke="#71B363" stroke-width="2"/>
      <ellipse cx="140" cy="74" rx="12" ry="7" fill="#5D4037"/>
      <ellipse cx="140" cy="74" rx="7" ry="4" fill="#A1887F"/>
      <ellipse cx="220" cy="85" rx="15" ry="8" fill="#5D4037"/>
      <ellipse cx="220" cy="85" rx="8" ry="4" fill="#A1887F"/>
      <ellipse cx="270" cy="78" rx="10" ry="6" fill="#5D4037"/>
    </svg>
    """

def wrap_html(title, theme, inner_body, is_landscape=False, is_bn=False):
    lang_attr = 'lang="bn"' if is_bn else 'lang="en"'
    landscape_class = 'class="landscape"' if is_landscape else ''
    return f"""<!DOCTYPE html>
<html {lang_attr} data-theme="{theme}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    {CSS_BASE}
  </style>
</head>
<body {landscape_class}>
  {inner_body}
</body>
</html>"""

def make_bottom_nav(active_tab="scan", is_bn=False):
    tabs = [
        ("scan", "Scan" if not is_bn else "স্ক্যান", '<path d="M12 15.2a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>'),
        ("history", "History" if not is_bn else "হিস্ট্রি", '<path d="M13 3a9 9 0 00-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0013 21a9 9 0 000-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>'),
        ("about", "About" if not is_bn else "সম্পর্কে", '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>'),
    ]
    items = []
    for key, label, svg_path in tabs:
        active = " active" if active_tab == key else ""
        items.append(f"""
        <div class="nav-item{active}">
          <div class="nav-pill">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">{svg_path}</svg>
          </div>
          <span>{label}</span>
        </div>
        """)
    return f'<div class="bottom-nav">{"".join(items)}</div>'

# ==============================================================================
# 1. GENERATE FULL BLEED CAPTURE SCREENS
# ==============================================================================
def build_capture_screen(theme="light", state="idle", is_bn=False, is_landscape=False):
    app_title = "ধানের পাতার রোগ শনাক্তকরণ" if is_bn else "Rice Leaf Disease Detection"
    lang_btn = "English" if is_bn else "বাংলা"
    tooltip = "ইংরেজিতে দেখুন" if is_bn else "Switch to Bangla"
    disclaimer = "⚠️ জরুরি সতর্কবার্তা: এটি কেবল তথ্য ও পরামর্শের জন্য। বিস্তারিত দেখতে ট্যাপ করুন।" if is_bn else "⚠️ Advisory notice: Advisory tool only. Tap for details."
    guide_text = "পাতার আক্রান্ত অংশটি ফ্রেমের মাঝে রাখুন" if is_bn else "Position diseased rice leaf in center"
    shutter_label = "ছবি তুলুন" if is_bn else "Capture"
    gallery_label = "গ্যালারি" if is_bn else "Gallery"
    help_label = "সাহায্য" if is_bn else "Help"

    if is_landscape:
        # 892 x 412 Landscape Viewport
        body = f"""
        <div class="landscape-preview">
          {generate_svg_camera_bg(762, 412)}
          <div class="status-bar transparent" style="position: absolute; top:0; left:0; width:100%;">
            <span>12:00</span>
            <div class="status-icons"><span>5G</span><span>100%</span></div>
          </div>
          <div class="app-bar scrim" style="position: absolute; top:24px; left:0; width:100%;">
            <div class="app-bar-title">{app_title}</div>
            <button class="lang-badge" title="{tooltip}">{lang_btn}</button>
          </div>
          <div class="viewfinder-frame" style="width: 200px; height: 200px; top: 52%;">
            <div class="vf-bracket vf-tl"></div><div class="vf-bracket vf-tr"></div>
            <div class="vf-bracket vf-bl"></div><div class="vf-bracket vf-br"></div>
          </div>
          <div class="guidance-chip" style="top: 78%; font-size: 11px; padding: 4px 12px;">{guide_text}</div>
          <div class="disclaimer-strip" style="position: absolute; bottom: 8px; left: 16px; margin: 0; font-size: 10px;">
            {disclaimer}
          </div>
        </div>
        <div class="landscape-dock">
          <div class="control-item">
            <div class="btn-gallery">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M22 16V4c0-1.1-.9-2-2-2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2zm-11-4l2.03 2.71L16 11l4 5H8l3-4zM2 6v14c0 1.1.9 2 2 2h14v-2H4V6H2z"/></svg>
            </div>
            <span>{gallery_label}</span>
          </div>
          <div class="control-item">
            <div class="shutter-outer">
              <div class="shutter-inner"></div>
            </div>
            <span>{shutter_label}</span>
          </div>
          <div class="control-item">
            <div class="btn-help">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"/></svg>
            </div>
            <span>{help_label}</span>
          </div>
        </div>
        """
        return wrap_html(f"Scan Landscape ({theme})", theme, body, is_landscape=True, is_bn=is_bn)

    # 412 x 892 Portrait Viewport
    state_overlay = ""
    shutter_style = ""
    shutter_click_disabled = ""

    if state == "permission":
        shutter_style = "opacity: 0.35; filter: grayscale(1); pointer-events: none;"
        state_overlay = f"""
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.6); z-index: 4; display: flex; align-items: center; justify-content: center; padding: 24px;">
          <div class="card" style="text-align: center; max-width: 330px; padding: 24px; box-shadow: 0 12px 32px rgba(0,0,0,0.5);">
            <div style="width: 52px; height: 52px; border-radius: 50%; background: var(--error-container); color: var(--error); display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto;">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M21 6.5l-4 4V7c0-.55-.45-1-1-1H9.82L21 17.18V6.5zM3.27 2L2 3.27 4.73 6H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.21 0 .39-.08.55-.18L19.73 21 21 19.73 3.27 2zM5 16V8h1.73l8 8H5z"/></svg>
            </div>
            <h3 class="title-md" style="font-size: 18px; margin-bottom: 6px;">Camera Access Required</h3>
            <p class="body-md" style="font-size: 13px; margin-bottom: 16px;">To scan rice leaves live in the field, please grant camera permission in device settings.</p>
            <div style="background: var(--surface-variant); padding: 10px; border-radius: 10px; font-size: 12px; margin-bottom: 16px; font-weight: 500;">
              ✨ You can still choose leaf photos from your gallery below.
            </div>
            <button class="btn-primary" style="margin-bottom: 8px;">Open App Settings</button>
            <button class="btn-outlined">Choose from Gallery</button>
          </div>
        </div>
        """
    elif state == "selected":
        state_overlay = f"""
        <div style="position: absolute; bottom: 180px; left: 16px; right: 16px; z-index: 6;">
          <div class="card" style="box-shadow: 0 8px 24px rgba(0,0,0,0.4); padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span class="title-md">Leaf Photo Selected</span>
              <span style="font-size: 12px; color: var(--primary); font-weight: 600;">Ready</span>
            </div>
            <p class="body-sm" style="margin-bottom: 12px;">Confirm the disease lesions are centered before running inference.</p>
            <div style="display: flex; gap: 10px;">
              <button class="btn-primary" style="flex: 1;">Analyze Leaf</button>
              <button class="btn-outlined" style="flex: 1;">Retake / Change</button>
            </div>
          </div>
        </div>
        """
    elif state == "analyzing":
        shutter_style = "opacity: 0.35; pointer-events: none;"
        state_overlay = f"""
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); z-index: 4; display: flex; align-items: center; justify-content: center; padding: 24px;">
          <div class="card" style="text-align: center; max-width: 300px; padding: 24px; box-shadow: 0 12px 32px rgba(0,0,0,0.5);">
            <div style="width: 44px; height: 44px; border: 4px solid var(--primary-container); border-top: 4px solid var(--primary); border-radius: 50%; margin: 0 auto 14px auto; animation: spin 1s linear infinite;"></div>
            <h3 class="title-md" style="font-size: 17px; margin-bottom: 4px;">Analyzing Rice Leaf...</h3>
            <p class="body-sm">Running on-device AI model (MobileNetV2)...</p>
          </div>
        </div>
        <style>@keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style>
        """

    body = f"""
    <div class="camera-viewport">
      {generate_svg_camera_bg(412, 892)}
      <div class="viewfinder-frame">
        <div class="vf-bracket vf-tl"></div><div class="vf-bracket vf-tr"></div>
        <div class="vf-bracket vf-bl"></div><div class="vf-bracket vf-br"></div>
      </div>
      <div class="guidance-chip">{guide_text}</div>
    </div>

    {state_overlay}

    <div class="status-bar transparent">
      <span>12:00</span>
      <div class="status-icons"><span>5G</span><span>100%</span></div>
    </div>

    <div class="app-bar scrim">
      <div class="app-bar-title">{app_title}</div>
      <button class="lang-badge" title="{tooltip}">{lang_btn}</button>
    </div>

    <div style="flex: 1;"></div>

    <div class="capture-overlay">
      <div class="disclaimer-strip">
        {disclaimer}
      </div>
      <div class="control-panel">
        <div class="control-item">
          <div class="btn-gallery">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M22 16V4c0-1.1-.9-2-2-2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2zm-11-4l2.03 2.71L16 11l4 5H8l3-4zM2 6v14c0 1.1.9 2 2 2h14v-2H4V6H2z"/></svg>
          </div>
          <span>{gallery_label}</span>
        </div>
        <div class="control-item" style="{shutter_style}">
          <div class="shutter-outer">
            <div class="shutter-inner"></div>
          </div>
          <span>{shutter_label}</span>
        </div>
        <div class="control-item">
          <div class="btn-help">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"/></svg>
          </div>
          <span>{help_label}</span>
        </div>
      </div>
    </div>

    {make_bottom_nav(active_tab="scan", is_bn=is_bn)}
    """
    return wrap_html(f"Scan ({state}, {theme})", theme, body, is_bn=is_bn)


# ==============================================================================
# 2. WRITE ALL CAPTURE MOCKUPS
# ==============================================================================
print("Generating Capture Page wireframes...")

# 2.1 Idle Viewfinder (Light/Dark x EN/BN)
for theme in ["light", "dark"]:
    for is_bn in [False, True]:
        lang_suffix = "bn" if is_bn else "en"
        html = build_capture_screen(theme=theme, state="idle", is_bn=is_bn, is_landscape=False)
        (MOCKUPS_DIR / f"scan_idle_{theme}_{lang_suffix}.html").write_text(html, encoding="utf-8")

# 2.2 Landscape Viewports (Light & Dark)
for theme in ["light", "dark"]:
    html_ls = build_capture_screen(theme=theme, state="idle", is_bn=False, is_landscape=True)
    (MOCKUPS_DIR / f"scan_landscape_{theme}.html").write_text(html_ls, encoding="utf-8")

# 2.3 Camera Permission Denied (Light & Dark)
for theme in ["light", "dark"]:
    html_perm = build_capture_screen(theme=theme, state="permission", is_bn=False)
    (MOCKUPS_DIR / f"scan_permission_{theme}.html").write_text(html_perm, encoding="utf-8")

# 2.4 Photo Selected State (Light & Dark)
for theme in ["light", "dark"]:
    html_sel = build_capture_screen(theme=theme, state="selected", is_bn=False)
    (MOCKUPS_DIR / f"scan_selected_{theme}.html").write_text(html_sel, encoding="utf-8")

# 2.5 Analyzing Progress State (Light & Dark)
for theme in ["light", "dark"]:
    html_ana = build_capture_screen(theme=theme, state="analyzing", is_bn=False)
    (MOCKUPS_DIR / f"scan_analyzing_{theme}.html").write_text(html_ana, encoding="utf-8")


# ==============================================================================
# 3. SPLASH & ONBOARDING
# ==============================================================================
def make_standard_screen(title, theme, content_html, app_bar_title="", app_bar_btn="", has_nav=True, active_tab="scan", back_btn=False, is_bn=False):
    app_bar_html = ""
    if app_bar_title:
        leading = '<button class="icon-btn"><svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg></button>' if back_btn else ""
        trailing = f'<button class="lang-badge">{app_bar_btn}</button>' if app_bar_btn else ""
        app_bar_html = f"""
        <div class="app-bar">
          <div class="app-bar-title">{leading} {app_bar_title}</div>
          {trailing}
        </div>
        """
    nav_html = make_bottom_nav(active_tab, is_bn) if has_nav else ""
    body = f"""
    <div class="status-bar">
      <span>12:00</span>
      <div class="status-icons"><span>5G</span><span>100%</span></div>
    </div>
    {app_bar_html}
    <div class="content">
      {content_html}
    </div>
    {nav_html}
    """
    return wrap_html(title, theme, body, is_bn=is_bn)

print("Generating Splash & Onboarding wireframes...")
for theme in ["light", "dark"]:
    splash_content = """
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; text-align: center;">
      <div style="width: 110px; height: 110px; border-radius: 28px; background: var(--primary-container); display: flex; align-items: center; justify-content: center;">
        <svg width="60" height="60" viewBox="0 0 24 24" fill="var(--primary)"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/></svg>
      </div>
      <div>
        <h1 class="title-lg" style="font-size: 24px; margin-bottom: 6px;">Rice Leaf Disease Detection</h1>
        <p class="body-md">Offline Agricultural Field Tool</p>
      </div>
      <div style="margin-top: 40px; width: 36px; height: 36px; border: 3px solid var(--surface-variant); border-top: 3px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
    </div>
    <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
    """
    (MOCKUPS_DIR / f"splash_{theme}.html").write_text(make_standard_screen(f"Splash ({theme})", theme, splash_content, has_nav=False), encoding="utf-8")

    onboarding_content = """
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div style="height: 180px; border-radius: 16px; background: var(--surface-variant); display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 8px;">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="var(--primary)"><path d="M4 4h3l2-2h6l2 2h3a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2zm8 3a5 5 0 100 10 5 5 0 000-10z"/></svg>
        <span class="body-sm" style="font-weight: 600;">Offline Field Leaf Scanner</span>
      </div>
      <div class="card card-tonal" style="border-left: 4px solid var(--primary);">
        <h3 class="title-md">Advisory Notice</h3>
        <p class="body-sm">This tool provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action.</p>
      </div>
      <div class="card card-tonal">
        <h4 class="title-md">Photo Guidelines</h4>
        <ul style="padding-left: 20px; font-size: 13px; color: var(--on-surface-variant); line-height: 1.6;">
          <li>Take photos in good natural daylight</li>
          <li>Focus clearly on the diseased leaf lesions</li>
          <li>Position the rice leaf in the frame center</li>
        </ul>
      </div>
      <button class="btn-primary" style="margin-top: 8px;">Get Started</button>
    </div>
    """
    (MOCKUPS_DIR / f"onboarding_{theme}.html").write_text(make_standard_screen(f"Onboarding ({theme})", theme, onboarding_content, app_bar_title="Welcome", app_bar_btn="বাংলা", has_nav=False), encoding="utf-8")


# ==============================================================================
# 4. RESULT CONFIDENT & RESULT UNCERTAIN (D-11 ENFORCED)
# ==============================================================================
print("Generating Result wireframes...")
for theme in ["light", "dark"]:
    # Confident EN
    res_conf_en = f"""
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <div class="leaf-svg">{generate_svg_leaf()}</div>
      <div class="card card-primary">
        <span class="body-sm" style="font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Likely Condition</span>
        <h2 class="title-lg" style="margin: 4px 0 2px 0;">Brown Spot</h2>
        <p class="body-sm" style="opacity: 0.9;">বাদামি দাগ রোগ</p>
        <div style="margin-top: 12px; background: rgba(0,0,0,0.1); border-radius: 6px; height: 8px; overflow: hidden;">
          <div style="background: var(--primary); width: 87.4%; height: 100%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 12px; font-weight: 600;">
          <span>Confidence: 87.4%</span>
          <span>Likely</span>
        </div>
      </div>
      <div class="card card-tonal">
        <h3 class="title-md">Field Advisory</h3>
        <p class="body-md">Apply balanced fertilizer (NPK); use certified disease-free seeds; ensure field drainage. Consult an agricultural extension officer before taking action.</p>
      </div>
      <div class="card card-tonal" style="border-left: 4px solid var(--primary); padding: 10px 14px;">
        <h4 class="title-md" style="font-size: 13px; margin-bottom: 2px;">Advisory Notice</h4>
        <p class="body-sm">This tool provides advisory identification only. Consult an agricultural expert before taking action.</p>
      </div>
      <button class="btn-outlined">Scan Another Leaf</button>
    </div>
    """
    (MOCKUPS_DIR / f"result_confident_{theme}_en.html").write_text(make_standard_screen(f"Result Confident (EN, {theme})", theme, res_conf_en, app_bar_title="Scan Result", has_nav=False, back_btn=True), encoding="utf-8")

    # Confident BN
    res_conf_bn = f"""
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <div class="leaf-svg">{generate_svg_leaf()}</div>
      <div class="card card-primary">
        <span class="body-sm" style="font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">সম্ভাব্য রোগ / লক্ষণ</span>
        <h2 class="title-lg" style="margin: 4px 0 2px 0;">বাদামি দাগ রোগ</h2>
        <p class="body-sm" style="opacity: 0.9;">Brown Spot</p>
        <div style="margin-top: 12px; background: rgba(0,0,0,0.1); border-radius: 6px; height: 8px; overflow: hidden;">
          <div style="background: var(--primary); width: 87.4%; height: 100%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 12px; font-weight: 600;">
          <span>নির্ভরযোগ্যতা: ৮৭.৪%</span>
          <span>সম্ভাব্য লক্ষণ</span>
        </div>
      </div>
      <div class="card card-tonal">
        <h3 class="title-md">মাঠ পর্যায়ের পরামর্শ</h3>
        <p class="body-md">সুষম সার (এনপিকে) প্রয়োগ করুন; বীজ শোধন করুন; জমিতে পরিমিত পানি নিষ্কাশন নিশ্চিত করুন। ব্যবস্থা নেওয়ার পূর্বে কৃষি কর্মকর্তার পরামর্শ নিন।</p>
      </div>
      <div class="card card-tonal" style="border-left: 4px solid var(--primary); padding: 10px 14px;">
        <h4 class="title-md" style="font-size: 13px; margin-bottom: 2px;">জরুরি সতর্কবার্তা</h4>
        <p class="body-sm">এই অ্যাপটি কেবল পরামর্শমূলক। ব্যবস্থা নেওয়ার আগে কৃষি কর্মকর্তার পরামর্শ নিন।</p>
      </div>
      <button class="btn-outlined">আরেকটি পাতা পরীক্ষা করুন</button>
    </div>
    """
    (MOCKUPS_DIR / f"result_confident_{theme}_bn.html").write_text(make_standard_screen(f"Result Confident (BN, {theme})", theme, res_conf_bn, app_bar_title="ফলাফল", has_nav=False, back_btn=True, is_bn=True), encoding="utf-8")

    # Uncertain EN
    res_unc_en = f"""
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <div class="leaf-svg">{generate_svg_leaf()}</div>
      <div class="card card-error">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
          <h2 class="title-lg" style="font-size: 18px;">Uncertain Result</h2>
        </div>
        <p class="body-md" style="color: var(--on-error-container);">Confidence is low. Please consult an agricultural expert for guidance.</p>
        <div style="margin-top: 10px; background: rgba(0,0,0,0.06); padding: 8px 12px; border-radius: 8px; font-size: 13px; font-weight: 600;">
          Possible condition: Brown Spot (52.0%)
        </div>
      </div>
      <!-- D-11 STRICT RULE: NO ADVISORY TEXT OR TREATMENT IS SHOWN -->
      <div class="card card-tonal">
        <h3 class="title-md">Recommended Next Step</h3>
        <p class="body-md">Take this leaf sample to your nearest Upazila Agriculture Office (DAE) for expert evaluation.</p>
      </div>
      <div class="card card-tonal" style="border-left: 4px solid var(--primary); padding: 10px 14px;">
        <h4 class="title-md" style="font-size: 13px; margin-bottom: 2px;">Advisory Notice</h4>
        <p class="body-sm">This tool provides advisory identification only. Consult an agricultural expert before taking action.</p>
      </div>
      <button class="btn-primary">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15.2a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>
        Retake Photo in Better Light
      </button>
      <button class="btn-outlined">Back to Scan</button>
    </div>
    """
    (MOCKUPS_DIR / f"result_uncertain_{theme}_en.html").write_text(make_standard_screen(f"Result Uncertain (EN, {theme})", theme, res_unc_en, app_bar_title="Scan Result", has_nav=False, back_btn=True), encoding="utf-8")

    # Uncertain BN
    res_unc_bn = f"""
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <div class="leaf-svg">{generate_svg_leaf()}</div>
      <div class="card card-error">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
          <h2 class="title-lg" style="font-size: 18px;">অনিশ্চিত ফলাফল</h2>
        </div>
        <p class="body-md" style="color: var(--on-error-container);">ফলাফলের নির্ভরযোগ্যতা কম। সঠিক তথ্যের জন্য একজন কৃষি বিশেষজ্ঞের পরামর্শ নিন।</p>
        <div style="margin-top: 10px; background: rgba(0,0,0,0.06); padding: 8px 12px; border-radius: 8px; font-size: 13px; font-weight: 600;">
          সম্ভাব্য লক্ষণ: বাদামি দাগ রোগ (৫২.০%)
        </div>
      </div>
      <!-- D-11 STRICT RULE: NO ADVISORY TEXT OR TREATMENT IS SHOWN -->
      <div class="card card-tonal">
        <h3 class="title-md">করণীয়</h3>
        <p class="body-md">পাতাটি আপনার নিকটস্থ উপজেলা কৃষি অফিসে (ডিএই) নিয়ে যান এবং কৃষি কর্মকর্তার পরামর্শ গ্রহণ করুন।</p>
      </div>
      <div class="card card-tonal" style="border-left: 4px solid var(--primary); padding: 10px 14px;">
        <h4 class="title-md" style="font-size: 13px; margin-bottom: 2px;">জরুরি সতর্কবার্তা</h4>
        <p class="body-sm">এই অ্যাপটি কেবল পরামর্শমূলক। ব্যবস্থা নেওয়ার আগে কৃষি কর্মকর্তার পরামর্শ নিন।</p>
      </div>
      <button class="btn-primary">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15.2a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>
        ভালো আলোতে পুনরায় ছবি তুলুন
      </button>
      <button class="btn-outlined">স্ক্যানে ফিরে যান</button>
    </div>
    """
    (MOCKUPS_DIR / f"result_uncertain_{theme}_bn.html").write_text(make_standard_screen(f"Result Uncertain (BN, {theme})", theme, res_unc_bn, app_bar_title="ফলাফল", has_nav=False, back_btn=True, is_bn=True), encoding="utf-8")


# ==============================================================================
# 5. HISTORY (Empty & List)
# ==============================================================================
print("Generating History wireframes...")
for theme in ["light", "dark"]:
    hist_empty = """
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 14px; padding: 20px;">
      <svg width="68" height="68" viewBox="0 0 24 24" fill="var(--outline)"><path d="M13 3a9 9 0 00-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0013 21a9 9 0 000-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
      <h3 class="title-md" style="font-size: 18px;">No past scans yet.</h3>
      <p class="body-md">Leaf scans you perform will appear here offline for future reference.</p>
      <button class="btn-primary" style="margin-top: 12px; width: auto; padding: 0 24px;">Start First Scan</button>
    </div>
    """
    (MOCKUPS_DIR / f"history_empty_{theme}.html").write_text(make_standard_screen(f"History Empty ({theme})", theme, hist_empty, app_bar_title="History", active_tab="history"), encoding="utf-8")

    hist_list = """
    <div style="display: flex; flex-direction: column; gap: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="body-sm" style="font-weight: 700; text-transform: uppercase;">Past Scans (3)</span>
        <span class="body-sm" style="color: var(--primary); font-weight: 600; cursor: pointer;">Clear All</span>
      </div>
      
      <div class="card" style="display: flex; gap: 12px; align-items: center; padding: 12px;">
        <div style="width: 52px; height: 52px; border-radius: 8px; background: var(--surface-variant); display: flex; align-items: center; justify-content: center;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="var(--primary)"><path d="M12 2C6.5 2 2 6.5 2 12c0 3.6 1.9 6.8 4.8 8.5L12 22l5.2-1.5C20.1 18.8 22 15.6 22 12c0-5.5-4.5-10-10-10z"/></svg>
        </div>
        <div style="flex: 1;">
          <h4 class="title-md" style="font-size: 15px; margin: 0;">Brown Spot</h4>
          <p class="body-sm">Today, 10:45 AM • 87.4% confidence</p>
        </div>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--outline)"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/></svg>
      </div>

      <div class="card" style="display: flex; gap: 12px; align-items: center; padding: 12px;">
        <div style="width: 52px; height: 52px; border-radius: 8px; background: var(--surface-variant); display: flex; align-items: center; justify-content: center;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="var(--primary)"><path d="M12 2C6.5 2 2 6.5 2 12c0 3.6 1.9 6.8 4.8 8.5L12 22l5.2-1.5C20.1 18.8 22 15.6 22 12c0-5.5-4.5-10-10-10z"/></svg>
        </div>
        <div style="flex: 1;">
          <h4 class="title-md" style="font-size: 15px; margin: 0;">Healthy Rice Leaf</h4>
          <p class="body-sm">Yesterday • 94.2% confidence</p>
        </div>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--outline)"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/></svg>
      </div>

      <div class="card" style="display: flex; gap: 12px; align-items: center; padding: 12px;">
        <div style="width: 52px; height: 52px; border-radius: 8px; background: var(--error-container); display: flex; align-items: center; justify-content: center;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="var(--error)"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
        </div>
        <div style="flex: 1;">
          <h4 class="title-md" style="font-size: 15px; margin: 0; color: var(--error);">Uncertain Scan</h4>
          <p class="body-sm">Nov 04 • 52.0% (Weak guess: Brown Spot)</p>
        </div>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--outline)"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/></svg>
      </div>
    </div>
    """
    (MOCKUPS_DIR / f"history_list_{theme}.html").write_text(make_standard_screen(f"History List ({theme})", theme, hist_list, app_bar_title="History", active_tab="history"), encoding="utf-8")


# ==============================================================================
# 6. ABOUT (D-29 Compliance)
# ==============================================================================
print("Generating About wireframes...")
for theme in ["light", "dark"]:
    about_content = """
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <div class="card card-primary">
        <h3 class="title-md" style="font-size: 17px; margin-bottom: 4px;">Rice Leaf Disease Detection</h3>
        <p class="body-sm">Version 1.0.0 (Build 1)</p>
        <p class="body-sm" style="margin-top: 6px;">Academic final-year project by Mehedi Hasan.</p>
      </div>

      <div class="card card-tonal">
        <h4 class="title-md">Software License</h4>
        <p class="body-sm">Released under the MIT License (D-01).</p>
      </div>

      <div class="card card-tonal">
        <h4 class="title-md">Dataset credit</h4>
        <p class="body-sm">Rice leaf images: Hasan, M. et al. (2023), Mendeley Data, DOI 10.17632/hx6f852hw4.2, licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" style="color: var(--primary); text-decoration: underline;">CC BY 4.0</a>.<br><br>Changes: images were re-oriented according to EXIF data and re-encoded for training.</p>
      </div>

      <div class="card card-tonal">
        <h4 class="title-md">Font License</h4>
        <p class="body-sm">Embedded font Noto Sans Bengali licensed under SIL Open Font License, Version 1.1 (OFL-1.1).</p>
      </div>

      <div class="card card-tonal">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <h4 class="title-md" style="margin: 0;">Privacy Policy</h4>
          <span style="font-size: 11px; font-weight: 700; background: var(--surface-color); color: var(--primary); padding: 2px 8px; border-radius: 8px; border: 1px solid var(--primary);">PROPOSED</span>
        </div>
        <p class="body-sm">100% offline application. Zero personal data, device identifiers, or leaf photos are collected, tracked, or shared.<br><br><a href="../privacy.html" style="color: var(--primary); text-decoration: underline;">Read Privacy Policy</a></p>
      </div>

      <div class="card card-tonal">
        <h4 class="title-md">Advisory Disclaimer</h4>
        <p class="body-sm">This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action.</p>
      </div>
    </div>
    """
    (MOCKUPS_DIR / f"about_{theme}.html").write_text(make_standard_screen(f"About ({theme})", theme, about_content, app_bar_title="About", active_tab="about"), encoding="utf-8")

print("All HTML mockups generated successfully.")


# ==============================================================================
# 7. RENDER PNGs VIA CHROME HEADLESS
# ==============================================================================
print("\nRendering screenshots via Chrome headless...")

# Explicit list of target screenshots to render
screenshots_to_render = [
    # Splash & Onboarding
    ("splash_light.html", "splash_light.png", 412, 892),
    ("splash_dark.html", "splash_dark.png", 412, 892),
    ("onboarding_light.html", "onboarding_light.png", 412, 892),
    ("onboarding_dark.html", "onboarding_dark.png", 412, 892),
    # Capture Idle Portrait
    ("scan_idle_light_en.html", "scan_idle_light_en.png", 412, 892),
    ("scan_idle_dark_en.html", "scan_idle_dark_en.png", 412, 892),
    ("scan_idle_light_bn.html", "scan_idle_light_bn.png", 412, 892),
    ("scan_idle_dark_bn.html", "scan_idle_dark_bn.png", 412, 892),
    # Capture Landscape
    ("scan_landscape_light.html", "scan_landscape_light.png", 892, 412),
    ("scan_landscape_dark.html", "scan_landscape_dark.png", 892, 412),
    # Capture States
    ("scan_permission_light.html", "scan_permission_light.png", 412, 892),
    ("scan_permission_dark.html", "scan_permission_dark.png", 412, 892),
    ("scan_selected_light.html", "scan_selected_light.png", 412, 892),
    ("scan_selected_dark.html", "scan_selected_dark.png", 412, 892),
    ("scan_analyzing_light.html", "scan_analyzing_light.png", 412, 892),
    ("scan_analyzing_dark.html", "scan_analyzing_dark.png", 412, 892),
    # Result Confident
    ("result_confident_light_en.html", "result_confident_light_en.png", 412, 892),
    ("result_confident_dark_en.html", "result_confident_dark_en.png", 412, 892),
    ("result_confident_light_bn.html", "result_confident_light_bn.png", 412, 892),
    ("result_confident_dark_bn.html", "result_confident_dark_bn.png", 412, 892),
    # Result Uncertain
    ("result_uncertain_light_en.html", "result_uncertain_light_en.png", 412, 892),
    ("result_uncertain_dark_en.html", "result_uncertain_dark_en.png", 412, 892),
    ("result_uncertain_light_bn.html", "result_uncertain_light_bn.png", 412, 892),
    ("result_uncertain_dark_bn.html", "result_uncertain_dark_bn.png", 412, 892),
    # History
    ("history_empty_light.html", "history_empty_light.png", 412, 892),
    ("history_empty_dark.html", "history_empty_dark.png", 412, 892),
    ("history_list_light.html", "history_list_light.png", 412, 892),
    ("history_list_dark.html", "history_list_dark.png", 412, 892),
    # About
    ("about_light.html", "about_light.png", 412, 892),
    ("about_dark.html", "about_dark.png", 412, 892),
]

for html_name, png_name, w, h in screenshots_to_render:
    html_path = MOCKUPS_DIR / html_name
    png_path = SCREENSHOTS_DIR / png_name
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
    size_kb = png_path.stat().st_size / 1024
    print(f"  - Rendered: {png_name} ({w}x{h}, {size_kb:.1f} KB)")

total_size_bytes = sum(f.stat().st_size for f in SCREENSHOTS_DIR.glob("*.png"))
total_size_mb = total_size_bytes / (1024 * 1024)
print(f"\nTotal screenshot folder size: {total_size_mb:.2f} MB ({total_size_bytes:,} bytes) [Limit <= 2.0 MB]")


# ==============================================================================
# 8. BUILD docs/design/index.html SHOWCASE
# ==============================================================================
print("\nBuilding docs/design/index.html showcase...")
sections = [
    ("Splash & Onboarding", [
        ("Splash (Light)", "splash_light"),
        ("Splash (Dark)", "splash_dark"),
        ("Onboarding (Light)", "onboarding_light"),
        ("Onboarding (Dark)", "onboarding_dark"),
    ]),
    ("Full-Bleed Capture Page (Idle Viewport)", [
        ("Capture Idle (Light, EN)", "scan_idle_light_en"),
        ("Capture Idle (Dark, EN)", "scan_idle_dark_en"),
        ("Capture Idle (Light, BN)", "scan_idle_light_bn"),
        ("Capture Idle (Dark, BN)", "scan_idle_dark_bn"),
    ]),
    ("Capture Page: Landscape Orientation (892×412)", [
        ("Capture Landscape (Light)", "scan_landscape_light"),
        ("Capture Landscape (Dark)", "scan_landscape_dark"),
    ]),
    ("Capture Page States (Permission, Selection, Analysis)", [
        ("Permission Denied (Light)", "scan_permission_light"),
        ("Permission Denied (Dark)", "scan_permission_dark"),
        ("Photo Selected (Light)", "scan_selected_light"),
        ("Photo Selected (Dark)", "scan_selected_dark"),
        ("Analyzing Leaf (Light)", "scan_analyzing_light"),
        ("Analyzing Leaf (Dark)", "scan_analyzing_dark"),
    ]),
    ("Result: Confident (>= 60%)", [
        ("Result Confident (Light, EN)", "result_confident_light_en"),
        ("Result Confident (Dark, EN)", "result_confident_dark_en"),
        ("Result Confident (Light, BN)", "result_confident_light_bn"),
        ("Result Confident (Dark, BN)", "result_confident_dark_bn"),
    ]),
    ("Result: Uncertain (< 60%, Rule D-11)", [
        ("Result Uncertain (Light, EN)", "result_uncertain_light_en"),
        ("Result Uncertain (Dark, EN)", "result_uncertain_dark_en"),
        ("Result Uncertain (Light, BN)", "result_uncertain_light_bn"),
        ("Result Uncertain (Dark, BN)", "result_uncertain_dark_bn"),
    ]),
    ("History Screen", [
        ("History Empty (Light)", "history_empty_light"),
        ("History Empty (Dark)", "history_empty_dark"),
        ("History List (Light)", "history_list_light"),
        ("History List (Dark)", "history_list_dark"),
    ]),
    ("About & Credits Screen (Decision D-29)", [
        ("About & Credits (Light)", "about_light"),
        ("About & Credits (Dark)", "about_dark"),
    ]),
]

cards_html = []
for sec_title, items in sections:
    cards = []
    for label, k in items:
        img_rel = f"../screenshots/design_proposal/{k}.png"
        html_rel = f"mockups/{k}.html"
        cards.append(f"""
        <div class="mockup-card">
          <div class="mockup-header">
            <span>{label}</span>
            <a href="{html_rel}" target="_blank">Open HTML ↗</a>
          </div>
          <div class="img-wrapper">
            <img src="{img_rel}" alt="{label}" loading="lazy"/>
          </div>
        </div>
        """)
    cards_html.append(f"""
    <section class="section">
      <h2 class="section-title">{sec_title}</h2>
      <div class="grid">
        {"".join(cards)}
      </div>
    </section>
    """)

index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>UI Design Proposal — Rice Leaf Disease Detection</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0e110e;
      color: #e1e3df;
      margin: 0;
      padding: 32px 24px;
    }}
    .header {{
      max-width: 1400px;
      margin: 0 auto 36px auto;
      border-bottom: 1px solid #283028;
      padding-bottom: 24px;
    }}
    h1 {{ font-size: 28px; color: #a7f3b3; margin-bottom: 8px; }}
    .subtitle {{ color: #a2a89e; font-size: 15px; line-height: 1.5; }}
    .spec-link {{
      display: inline-block;
      margin-top: 12px;
      color: #8cd699;
      text-decoration: none;
      font-weight: 600;
      padding: 6px 14px;
      background: #17381d;
      border-radius: 8px;
    }}
    .section {{
      max-width: 1400px;
      margin: 0 auto 40px auto;
    }}
    .section-title {{
      font-size: 20px;
      color: #e1e3df;
      margin-bottom: 16px;
      border-left: 4px solid #4caf50;
      padding-left: 10px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 24px;
    }}
    .mockup-card {{
      background: #1a1e1a;
      border: 1px solid #283028;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .mockup-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      background: #232823;
      font-size: 12px;
      font-weight: 600;
      color: #c2c8be;
    }}
    .mockup-header a {{
      color: #8cd699;
      text-decoration: none;
    }}
    .img-wrapper {{
      padding: 12px;
      background: #121512;
      display: flex;
      justify-content: center;
    }}
    .img-wrapper img {{
      width: 100%;
      height: auto;
      max-width: 260px;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Rice Leaf Disease Detection — UI Design Proposal (Revision 2)</h1>
    <p class="subtitle">Complete visual specification and interactive wireframes for task <strong>T-060b</strong>. Features full-bleed viewport capture layout with 72 dp circular shutter, 56 dp thumb-reachable gallery picker, expandable disclaimer strip (F-08), multi-state capture handling (idle, permission denied, photo selected, analyzing), landscape orientation (892×412 dp), and strict safety compliance (no "diagnosis" or "cure"; zero treatment advice in uncertain state per rule D-11; dataset credit restricted per D-29).</p>
    <a href="ui_spec.md" class="spec-link">View Detailed UI Specification (ui_spec.md) →</a>
    <a href="tokens.md" class="spec-link" style="margin-left: 10px; background: #224227;">View Design Tokens (tokens.md) →</a>
    <a href="review_checklist.md" class="spec-link" style="margin-left: 10px; background: #283526;">View Review Checklist (review_checklist.md) →</a>
  </div>
  {"".join(cards_html)}
</body>
</html>
"""

INDEX_HTML.write_text(index_content, encoding="utf-8")
print(f"Generated index showcase at: {INDEX_HTML}")
