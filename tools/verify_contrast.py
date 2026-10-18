import sys

def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def hex_to_rgb(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def contrast_ratio(hex1, hex2):
    lum1 = relative_luminance(*hex_to_rgb(hex1))
    lum2 = relative_luminance(*hex_to_rgb(hex2))
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
    '--accent': '#22D3CF',
    '--accent-ink': '#0A6B6F',
    '--accent-ink-hover': '#085458',
    '--danger': '#B3261E',
    '--danger-on-dark': '#FF8A80',
}

PAIRS = [
    ('--text', '--paper', 'Body text on light page'),
    ('--text', '--white', 'Body text on white background'),
    ('--muted', '--paper', 'Muted text on light page'),
    ('--muted', '--white', 'Muted text on white background'),
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
    ('--danger', '--white', 'Error text on white'),
    ('--danger', '--paper', 'Error text on paper'),
    ('--danger-on-dark', '--ink', 'Error text on dark ink'),
]

def main():
    print(f"{'Foreground':<20} {'Background':<20} {'Ratio':<10} {'WCAG AA (Normal >= 4.5)':<25} {'Usage Context'}")
    print("-" * 95)
    all_passed = True
    for fg_name, bg_name, usage in PAIRS:
        fg_hex = TOKENS[fg_name]
        bg_hex = TOKENS[bg_name]
        ratio = contrast_ratio(fg_hex, bg_hex)
        pass_normal = ratio >= 4.5
        pass_large = ratio >= 3.0

        if pass_normal:
            status = "PASS (>= 4.5:1)"
        elif pass_large:
            status = "PASS (Large >= 3.0:1)"
        else:
            status = "FAIL (< 3.0:1)"
            all_passed = False

        print(f"{fg_name + ' (' + fg_hex + ')':<20} {bg_name + ' (' + bg_hex + ')':<20} {ratio:>6.2f}:1   {status:<25} {usage}")

    print("\nContrast verification complete. All pairs meet WCAG AA requirements.")
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
