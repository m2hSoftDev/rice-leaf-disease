"""
scripts/build_mockups.py

Generates 22 standalone Material 3 HTML wireframes in docs/design/mockups/,
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
  --on-surface: #191C19;
  --on-surface-variant: #424940;
  --primary: #236A34;
  --primary-container: #A7F3B3;
  --on-primary: #FFFFFF;
  --on-primary-container: #00210A;
  --outline: #72796F;
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
  --on-surface: #E1E3DF;
  --on-surface-variant: #C2C8BE;
  --primary: #8CD699;
  --primary-container: #055320;
  --on-primary: #003914;
  --on-primary-container: #A7F3B3;
  --outline: #8C9388;
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
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
}
.app-bar-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--on-surface);
  display: flex;
  align-items: center;
  gap: 12px;
}
.app-bar-btn {
  background: transparent;
  border: none;
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid var(--primary);
}

/* Content Area */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Cards */
.card {
  background: var(--surface-color);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid var(--card-border);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.card-tonal {
  background: var(--surface-variant);
  border: none;
}
.card-primary {
  background: var(--primary-container);
  color: var(--on-primary-container);
  border: none;
}
.card-error {
  background: var(--error-container);
  color: var(--on-error-container);
  border: none;
}

/* Typography */
.title-lg { font-size: 20px; font-weight: 700; line-height: 1.3; }
.title-md { font-size: 16px; font-weight: 600; line-height: 1.3; margin-bottom: 6px; }
.body-md { font-size: 14px; line-height: 1.45; color: var(--on-surface-variant); }
.body-sm { font-size: 12px; line-height: 1.4; color: var(--on-surface-variant); }

/* Buttons */
.btn-primary {
  background: var(--primary);
  color: var(--on-primary);
  border: none;
  height: 52px;
  border-radius: 26px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  width: 100%;
}
.btn-outlined {
  background: transparent;
  color: var(--primary);
  border: 1.5px solid var(--outline);
  height: 50px;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  width: 100%;
}

/* Bottom Navigation */
.bottom-nav {
  height: 80px;
  background: var(--nav-bg);
  display: flex;
  justify-content: space-around;
  align-items: center;
  border-top: 1px solid var(--card-border);
  flex-shrink: 0;
  padding-bottom: 8px;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--on-surface-variant);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
.nav-item.active {
  color: var(--on-surface);
  font-weight: 700;
}
.nav-pill {
  width: 64px;
  height: 32px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-item.active .nav-pill {
  background: var(--primary-container);
  color: var(--on-primary-container);
}

/* Leaf SVG illustration */
.leaf-svg {
  width: 100%;
  height: 190px;
  background: var(--surface-variant);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}
"""

def generate_svg_leaf():
    return """
    <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 100 C 40 40, 80 20, 100 20 C 100 40, 80 80, 20 100 Z" fill="#4CAF50" fill-opacity="0.8"/>
      <path d="M20 100 Q 60 60 100 20" stroke="#2E7D32" stroke-width="2.5" stroke-linecap="round"/>
      <ellipse cx="65" cy="50" rx="9" ry="5" fill="#8D6E63" stroke="#4E342E" stroke-width="1.5"/>
      <ellipse cx="48" cy="72" rx="7" ry="4" fill="#8D6E63" stroke="#4E342E" stroke-width="1.5"/>
    </svg>
    <div style="font-size: 11px; font-weight: 600; opacity: 0.7; margin-top: 4px;">[Synthetic Leaf Preview — 224x224]</div>
    """

def generate_html(title, theme, content_html, has_app_bar=True, app_bar_title="", app_bar_btn="", has_nav=True, active_tab="scan", is_bn=False, back_btn=False):
    nav_html = ""
    if has_nav:
        scan_label = "স্ক্যান" if is_bn else "Scan"
        history_label = "হিস্ট্রি" if is_bn else "History"
        about_label = "সম্পর্কে" if is_bn else "About"

        nav_html = f"""
        <div class="bottom-nav">
          <div class="nav-item {'active' if active_tab == 'scan' else ''}">
            <div class="nav-pill">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15.2a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>
            </div>
            <span>{scan_label}</span>
          </div>
          <div class="nav-item {'active' if active_tab == 'history' else ''}">
            <div class="nav-pill">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M13 3a9 9 0 00-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0013 21a9 9 0 000-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
            </div>
            <span>{history_label}</span>
          </div>
          <div class="nav-item {'active' if active_tab == 'about' else ''}">
            <div class="nav-pill">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
            </div>
            <span>{about_label}</span>
          </div>
        </div>
        """

    app_bar_html = ""
    if has_app_bar:
        back_svg = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style="cursor:pointer;"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>' if back_btn else ''
        btn_markup = f'<button class="app-bar-btn">{app_bar_btn}</button>' if app_bar_btn else ''
        app_bar_html = f"""
        <div class="app-bar">
          <div class="app-bar-title">{back_svg} {app_bar_title}</div>
          {btn_markup}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="{'bn' if is_bn else 'en'}" data-theme="{theme}">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>{CSS_BASE}</style>
</head>
<body>
  <div class="status-bar">
    <span>12:00</span>
    <div class="status-icons">
      <span>5G</span>
      <span>100%</span>
    </div>
  </div>
  {app_bar_html}
  <div class="content">
    {content_html}
  </div>
  {nav_html}
</body>
</html>"""

print("Generating 20 wireframe HTML files...")

# ==============================================================================
# 1. SPLASH (Light & Dark)
# ==============================================================================
for theme in ["light", "dark"]:
    splash_content = """
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 20px;">
      <div style="width: 110px; height: 110px; border-radius: 28px; background: var(--primary-container); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="var(--primary)"><path d="M12 2C6.5 2 2 6.5 2 12c0 3.6 1.9 6.8 4.8 8.5L12 22l5.2-1.5C20.1 18.8 22 15.6 22 12c0-5.5-4.5-10-10-10zm0 18c-4.4 0-8-3.6-8-8 0-3.3 2-6.2 5-7.4V14c0 1.7 1.3 3 3 3s3-1.3 3-3V4.6c3 1.2 5 4.1 5 7.4 0 4.4-3.6 8-8 8z"/></svg>
      </div>
      <div>
        <h1 class="title-lg" style="font-size: 24px;">Rice Leaf Disease<br>Detection</h1>
        <p class="body-md" style="margin-top: 8px;">Offline Agricultural Field Tool</p>
      </div>
      <div style="margin-top: 40px; display: flex; gap: 8px;">
        <div style="width: 10px; height: 10px; border-radius: 50%; background: var(--primary);"></div>
        <div style="width: 10px; height: 10px; border-radius: 50%; background: var(--primary); opacity: 0.5;"></div>
        <div style="width: 10px; height: 10px; border-radius: 50%; background: var(--primary); opacity: 0.2;"></div>
      </div>
    </div>
    """
    html = generate_html(f"Splash ({theme})", theme, splash_content, has_app_bar=False, has_nav=False)
    (MOCKUPS_DIR / f"splash_{theme}.html").write_text(html, encoding="utf-8")

# ==============================================================================
# 2. ONBOARDING (Light & Dark)
# ==============================================================================
for theme in ["light", "dark"]:
    onboarding_content = """
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div style="height: 180px; background: var(--surface-variant); border-radius: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;">
        <svg width="60" height="60" viewBox="0 0 24 24" fill="var(--primary)"><path d="M12 3L2 12h3v8h14v-8h3L12 3zm0 12.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        <span class="body-sm" style="font-weight: 600;">Welcome to Offline Crop Care</span>
      </div>
      <div class="card card-tonal">
        <h3 class="title-md">Advisory Notice</h3>
        <p class="body-md">This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action.</p>
      </div>
      <div class="card card-tonal">
        <h3 class="title-md">Photo Guidelines</h3>
        <ul style="padding-left: 18px;" class="body-md">
          <li>Take photos in clear natural daylight.</li>
          <li>Focus closely on the affected leaf area.</li>
          <li>Ensure the leaf is centered in the camera frame.</li>
        </ul>
      </div>
      <div style="margin-top: 8px;">
        <button class="btn-primary">Get Started</button>
      </div>
    </div>
    """
    html = generate_html(f"Onboarding ({theme})", theme, onboarding_content, has_app_bar=True, app_bar_title="Welcome", app_bar_btn="বাংলায় দেখুন", has_nav=False)
    (MOCKUPS_DIR / f"onboarding_{theme}.html").write_text(html, encoding="utf-8")

# ==============================================================================
# 3. SCAN (Light/Dark x EN/BN)
# ==============================================================================
for theme in ["light", "dark"]:
    # EN
    scan_en = f"""
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div style="height: 250px; border: 2px dashed var(--outline); border-radius: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: var(--surface-color);">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="var(--outline)"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54-1.96-2.36L6.5 17h11l-3.54-4.71z"/></svg>
        <span class="body-md" style="font-weight: 500;">Position diseased rice leaf in center</span>
      </div>
      <button class="btn-primary">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15.2a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>
        Take Photo
      </button>
      <button class="btn-outlined">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
        Choose from Gallery
      </button>
      <div class="card card-tonal">
        <h4 class="title-md" style="font-size: 14px;">Advisory Notice</h4>
        <p class="body-sm">This tool provides leaf condition identification from photos. It does not replace professional agricultural advice. Consult an agricultural extension officer before taking action.</p>
      </div>
    </div>
    """
    html_en = generate_html(f"Scan (EN, {theme})", theme, scan_en, app_bar_title="Rice Leaf Disease", app_bar_btn="বাংলায় দেখুন", active_tab="scan", is_bn=False)
    (MOCKUPS_DIR / f"scan_{theme}_en.html").write_text(html_en, encoding="utf-8")

    # BN
    scan_bn = f"""
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div style="height: 250px; border: 2px dashed var(--outline); border-radius: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: var(--surface-color);">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="var(--outline)"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54-1.96-2.36L6.5 17h11l-3.54-4.71z"/></svg>
        <span class="body-md" style="font-weight: 500;">পাতার আক্রান্ত অংশটি ফ্রেমের মাঝে রাখুন</span>
      </div>
      <button class="btn-primary">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15.2a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>
        ছবি তুলুন
      </button>
      <button class="btn-outlined">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
        গ্যালারি থেকে বাছাই করুন
      </button>
      <div class="card card-tonal">
        <h4 class="title-md" style="font-size: 14px;">জরুরি সতর্কবার্তা</h4>
        <p class="body-sm">এই অ্যাপটি কেবল তথ্য ও পরামর্শের জন্য তৈরি। এটি কোনো চূড়ান্ত সিদ্ধান্ত নয়। যেকোনো ব্যবস্থা নেওয়ার আগে স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।</p>
      </div>
    </div>
    """
    html_bn = generate_html(f"Scan (BN, {theme})", theme, scan_bn, app_bar_title="ধানের পাতার রোগ শনাক্তকরণ", app_bar_btn="View in English", active_tab="scan", is_bn=True)
    (MOCKUPS_DIR / f"scan_{theme}_bn.html").write_text(html_bn, encoding="utf-8")

# ==============================================================================
# 4. RESULT CONFIDENT (Light/Dark x EN/BN)
# ==============================================================================
for theme in ["light", "dark"]:
    # EN
    result_conf_en = f"""
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
    html_conf_en = generate_html(f"Result Confident (EN, {theme})", theme, result_conf_en, app_bar_title="Scan Result", has_nav=False, back_btn=True, is_bn=False)
    (MOCKUPS_DIR / f"result_confident_{theme}_en.html").write_text(html_conf_en, encoding="utf-8")

    # BN
    result_conf_bn = f"""
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
    html_conf_bn = generate_html(f"Result Confident (BN, {theme})", theme, result_conf_bn, app_bar_title="ফলাফল", has_nav=False, back_btn=True, is_bn=True)
    (MOCKUPS_DIR / f"result_confident_{theme}_bn.html").write_text(html_conf_bn, encoding="utf-8")

# ==============================================================================
# 5. RESULT UNCERTAIN (Light/Dark x EN/BN) - D-11 Rule Enforced
# ==============================================================================
for theme in ["light", "dark"]:
    # EN
    result_unc_en = f"""
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
    html_unc_en = generate_html(f"Result Uncertain (EN, {theme})", theme, result_unc_en, app_bar_title="Scan Result", has_nav=False, back_btn=True, is_bn=False)
    (MOCKUPS_DIR / f"result_uncertain_{theme}_en.html").write_text(html_unc_en, encoding="utf-8")

    # BN
    result_unc_bn = f"""
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
    html_unc_bn = generate_html(f"Result Uncertain (BN, {theme})", theme, result_unc_bn, app_bar_title="ফলাফল", has_nav=False, back_btn=True, is_bn=True)
    (MOCKUPS_DIR / f"result_uncertain_{theme}_bn.html").write_text(html_unc_bn, encoding="utf-8")

# ==============================================================================
# 6. HISTORY EMPTY (Light & Dark)
# ==============================================================================
for theme in ["light", "dark"]:
    history_empty_content = """
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 14px; padding: 20px;">
      <svg width="68" height="68" viewBox="0 0 24 24" fill="var(--outline)"><path d="M13 3a9 9 0 00-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0013 21a9 9 0 000-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
      <h3 class="title-md" style="font-size: 18px;">No past scans yet.</h3>
      <p class="body-md">Leaf scans you perform will appear here offline for future reference.</p>
      <button class="btn-primary" style="margin-top: 12px; width: auto; padding: 0 24px;">Start First Scan</button>
    </div>
    """
    html = generate_html(f"History Empty ({theme})", theme, history_empty_content, app_bar_title="Scan History", active_tab="history")
    (MOCKUPS_DIR / f"history_empty_{theme}.html").write_text(html, encoding="utf-8")

# ==============================================================================
# 7. HISTORY LIST (Light & Dark)
# ==============================================================================
for theme in ["light", "dark"]:
    history_list_content = """
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
    html = generate_html(f"History List ({theme})", theme, history_list_content, app_bar_title="Scan History", active_tab="history")
    (MOCKUPS_DIR / f"history_list_{theme}.html").write_text(html, encoding="utf-8")

# ==============================================================================
# 8. ABOUT (Light & Dark)
# ==============================================================================
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
        <h4 class="title-md">Advisory Disclaimer</h4>
        <p class="body-sm">This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action.</p>
      </div>
    </div>
    """
    html = generate_html(f"About ({theme})", theme, about_content, app_bar_title="About & Credits", active_tab="about")
    (MOCKUPS_DIR / f"about_{theme}.html").write_text(html, encoding="utf-8")

print(f"All 22 HTML files generated successfully in {MOCKUPS_DIR}")

# ==============================================================================
# 9. RENDER PNGs VIA CHROME HEADLESS
# ==============================================================================
print("\nRendering screenshots via Chrome headless...")
html_files = sorted(list(MOCKUPS_DIR.glob("*.html")))

for html_file in html_files:
    png_name = html_file.stem + ".png"
    png_path = SCREENSHOTS_DIR / png_name
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size=412,892",
        f"--screenshot={png_path}",
        str(html_file.resolve().as_uri())
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    
    # Optimize PNG using Pillow
    with Image.open(png_path) as img:
        img.save(png_path, "PNG", optimize=True)
    
    size_kb = png_path.stat().st_size / 1024
    print(f"  - Rendered: {png_name} ({size_kb:.1f} KB)")

total_size_bytes = sum(f.stat().st_size for f in SCREENSHOTS_DIR.glob("*.png"))
total_size_mb = total_size_bytes / (1024 * 1024)
print(f"\nTotal screenshot folder size: {total_size_mb:.2f} MB ({total_size_bytes:,} bytes) [Limit <= 2.0 MB]")

# ==============================================================================
# 10. BUILD docs/design/index.html
# ==============================================================================
print("\nBuilding docs/design/index.html showcase...")
sections = [
    ("Splash & Onboarding", ["splash_light", "splash_dark", "onboarding_light", "onboarding_dark"]),
    ("Scan Screen (Home)", ["scan_light_en", "scan_dark_en", "scan_light_bn", "scan_dark_bn"]),
    ("Result: Confident (>= 60%)", ["result_confident_light_en", "result_confident_dark_en", "result_confident_light_bn", "result_confident_dark_bn"]),
    ("Result: Uncertain (< 60%, D-11)", ["result_uncertain_light_en", "result_uncertain_dark_en", "result_uncertain_light_bn", "result_uncertain_dark_bn"]),
    ("History Screen", ["history_empty_light", "history_empty_dark", "history_list_light", "history_list_dark"]),
    ("About & Credits Screen", ["about_light", "about_dark"]),
]

cards_html = []
for sec_title, keys in sections:
    items = []
    for k in keys:
        img_rel = f"../screenshots/design_proposal/{k}.png"
        html_rel = f"mockups/{k}.html"
        label = k.replace("_", " ").title()
        items.append(f"""
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
        {"".join(items)}
      </div>
    </section>
    """)

index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>UI Design Proposal — Rice Leaf Disease Detection</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f130f;
      color: #e1e3df;
      margin: 0;
      padding: 32px 24px;
    }}
    .header {{
      max-width: 1400px;
      margin: 0 auto 32px auto;
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
    <h1>Rice Leaf Disease Detection — UI Design Proposal</h1>
    <p class="subtitle">Complete visual specification and interactive wireframes for task <strong>T-060b</strong>. Covers all screens in Light & Dark modes, with dedicated Bangla localizations for Scan and Result states. Complies strictly with safety rules (no "diagnosis" or "cure"; no treatment advice in uncertain state per rule D-11).</p>
    <a href="ui_spec.md" class="spec-link">View Detailed UI Specification (ui_spec.md) →</a>
    <a href="review_checklist.md" class="spec-link" style="margin-left: 10px; background: #283526;">View Review Checklist (review_checklist.md) →</a>
  </div>
  {"".join(cards_html)}
</body>
</html>
"""

INDEX_HTML.write_text(index_content, encoding="utf-8")
print(f"Generated index showcase at: {INDEX_HTML}")
