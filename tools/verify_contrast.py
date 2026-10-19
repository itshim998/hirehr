import sys
import re

def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def hex_to_rgb(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def parse_color(color_str, bg_rgb=(255, 255, 255)):
    color_str = color_str.strip()
    if color_str in TOKENS:
        return hex_to_rgb(TOKENS[color_str])
    if color_str.startswith('#'):
        return hex_to_rgb(color_str)
    rgba_m = re.match(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)', color_str)
    if rgba_m:
        r, g, b = int(rgba_m.group(1)), int(rgba_m.group(2)), int(rgba_m.group(3))
        a = float(rgba_m.group(4)) if rgba_m.group(4) is not None else 1.0
        # Alpha blend over bg_rgb
        comp_r = round(a * r + (1 - a) * bg_rgb[0])
        comp_g = round(a * g + (1 - a) * bg_rgb[1])
        comp_b = round(a * b + (1 - a) * bg_rgb[2])
        return (comp_r, comp_g, comp_b)
    raise ValueError(f"Unknown color format: {color_str}")

def contrast_ratio(rgb1, rgb2):
    lum1 = relative_luminance(*rgb1)
    lum2 = relative_luminance(*rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

TOKENS = {
    '--ink': '#0A1624',
    '--ink-2': '#102235',
    '--paper': '#F6F4EF',
    '--white': '#FFFFFF',
    '--text': '#1B2733',
    '--muted': '#5B6773',
    '--muted-on-dark': '#9AA7B4',
    '--accent': '#22D3CF',
    '--accent-ink': '#0A6B6F',
    '--accent-ink-hover': '#085458',
    '--danger': '#B3261E',
    '--danger-on-dark': '#FF8A80',
}

# Calculated composited background colors
# Worst-case hero overlay: white image (#FFFFFF) under 0.86 ink (#0A1624)
HERO_BG_LEFT = '#2C3743'
# Hero overlay at text max-width: 0.70 ink over white image
HERO_BG_TEXT_EDGE = '#545C66'
# Mobile hero overlay: uniform 0.62 ink + 0.55 bottom gradient (effective alpha 0.83 ink over white)
HERO_BG_MOBILE = '#333D48'

PAIRS = [
    # Core Design System Token Matrix
    ('--text', '--paper', 'Body text on light page surface'),
    ('--text', '--white', 'Body text on white background'),
    ('--muted', '--paper', 'Muted secondary text on light page'),
    ('--muted', '--white', 'Muted secondary text on white surface'),
    ('--muted-on-dark', '--ink', 'Muted text on primary dark ink'),
    ('--muted-on-dark', '--ink-2', 'Muted text on secondary dark surface'),
    ('--accent-ink', '--paper', 'Teal accent text/links on paper'),
    ('--accent-ink', '--white', 'Teal accent text/links on white'),
    ('--accent-ink-hover', '--paper', 'Teal accent hover on paper'),
    ('--accent-ink-hover', '--white', 'Teal accent hover on white'),
    ('--accent', '--ink', 'Teal accent on dark ink background'),
    ('--accent', '--ink-2', 'Teal accent on dark ink-2 background'),
    ('--white', '--ink', 'White text on dark ink background'),
    ('--white', '--ink-2', 'White text on dark ink-2 background'),
    ('--white', '--accent-ink', 'White text on teal ink button'),
    ('--ink', '--accent', 'Dark ink text on teal accent button'),
    ('--danger', '--white', 'Error text on white surface'),
    ('--danger', '--paper', 'Error text on paper surface'),
    ('--danger-on-dark', '--ink', 'Error text on dark ink surface'),

    # Header & Top Bar Actual Pairs
    ('rgba(255, 255, 255, 0.82)', '--ink', 'Top bar contact emails on dark ink'),
    ('--muted-on-dark', '--ink', 'Top bar social label on dark ink'),
    ('rgba(255, 255, 255, 0.85)', '--ink', 'Top bar LinkedIn icon on dark ink'),
    ('--text', '--paper', 'Nav links on solid paper header'),
    ('--accent-ink', '--paper', 'Active nav link on paper header'),

    # Mobile Navigation Overlay Actual Pairs
    ('--white', '--ink', 'Mobile overlay primary nav links on ink'),
    ('rgba(255, 255, 255, 0.85)', '--ink', 'Mobile overlay dropdown links on ink'),
    ('--accent', '--ink', 'Mobile overlay active nav link on ink'),

    # Footer Actual Pairs
    ('--accent', '--ink', 'Footer column eyebrow titles on ink'),
    ('rgba(255, 255, 255, 0.85)', '--ink', 'Footer contact text on ink'),
    ('rgba(255, 255, 255, 0.80)', '--ink', 'Footer contact list items on ink'),
    ('rgba(255, 255, 255, 0.75)', '--ink', 'Footer quick links on ink'),
    ('--muted-on-dark', '--ink', 'Footer contact SVG icons on ink'),
    ('--muted-on-dark', '--ink', 'Footer copyright line on ink'),

    # Form on Ink (Section 6) Actual Pairs
    ('rgba(255, 255, 255, 0.75)', '--ink', 'Form labels (eyebrow style) on ink'),
    ('rgba(255, 255, 255, 0.60)', '--ink', 'Form input placeholders on ink'),
    ('--white', '--ink', 'Form input text on ink'),
    ('--accent', '--ink', 'Form required field asterisks on ink'),
    ('--ink', '--accent', 'Form submit button text on teal accent'),
    ('--danger-on-dark', '--ink', 'Form status error message on ink'),
    ('--accent', '--ink', 'Form status success message on ink'),

    # Hero Slider Actual Pairs (over composited image + overlay gradient)
    ('--white', HERO_BG_LEFT, 'Hero slide title (left) over overlay on white image'),
    ('--white', HERO_BG_TEXT_EDGE, 'Hero slide title (edge) over overlay on white image'),
    ('rgba(255, 255, 255, 0.82)', HERO_BG_LEFT, 'Hero slide subtitle over overlay on white image'),
    ('--white', HERO_BG_MOBILE, 'Hero slide title on mobile overlay (<768px)'),
]

def main():
    print(f"{'Foreground':<28} {'Background':<16} {'Ratio':<10} {'WCAG AA Status':<25} {'Usage Context'}")
    print("-" * 115)
    all_passed = True
    for fg_name, bg_name, usage in PAIRS:
        bg_rgb = parse_color(bg_name)
        fg_rgb = parse_color(fg_name, bg_rgb)
        ratio = contrast_ratio(fg_rgb, bg_rgb)
        pass_normal = ratio >= 4.5
        pass_large = ratio >= 3.0

        if pass_normal:
            status = "PASS (>= 4.5:1)"
        elif pass_large:
            status = "PASS (Large >= 3.0:1)"
        else:
            status = "FAIL (< 3.0:1)"
            all_passed = False

        bg_display = bg_name if bg_name.startswith('--') or bg_name.startswith('#') else bg_name
        fg_display = fg_name
        print(f"{fg_display:<28} {bg_display:<16} {ratio:>6.2f}:1   {status:<25} {usage}")

    print("-" * 115)
    if all_passed:
        print("Contrast verification complete. ALL pairs meet WCAG AA requirements.")
        return 0
    else:
        print("Contrast verification FAILED. One or more pairs do not meet WCAG AA.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
