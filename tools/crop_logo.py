import os
from PIL import Image

orig_path = 'assets/logo/HireHR-Logo.original.png'
orig = Image.open(orig_path)
print(f"Original size: {orig.size}, format: {orig.format}, mode: {orig.mode}")

# Opaque box for visible flame: x in [138, 607], y in [54, 995]
min_x, max_x = 138, 607
min_y, max_y = 54, 995
w = max_x - min_x + 1  # 470
h = max_y - min_y + 1  # 942

# 2% safe margin
safe_x = round(w * 0.02)  # 9 px
safe_y = round(h * 0.02)  # 19 px

left = max(0, min_x - safe_x)     # 129
top = max(0, min_y - safe_y)      # 35
right = min(orig.width, max_x + 1 + safe_x)   # 617
bottom = min(orig.height, max_y + 1 + safe_y) # 1002 (clamped to original height)

print(f"Crop box: left={left}, top={top}, right={right}, bottom={bottom}")
cropped = orig.crop((left, top, right, bottom))
print(f"Cropped dimensions: {cropped.size} (aspect ratio: {cropped.width / cropped.height:.4f})")

# Target 1x: display height 44px
h_1x = 44
w_1x = round(h_1x * cropped.width / cropped.height)  # 22 px
logo_1x = cropped.resize((w_1x, h_1x), Image.Resampling.LANCZOS)

# Target 2x: display height 88px
h_2x = 88
w_2x = round(h_2x * cropped.width / cropped.height)  # 44 or 45 px
# If w_1x * 2 is desired for pixel-perfect 2x ratio:
if abs((w_1x * 2) - w_2x) <= 1:
    w_2x = w_1x * 2  # exactly 44 px for perfect integer scaling
logo_2x = cropped.resize((w_2x, h_2x), Image.Resampling.LANCZOS)

print(f"1x dimensions: {logo_1x.size}")
print(f"2x dimensions: {logo_2x.size}")

# Save derivatives
logo_1x_path = 'assets/logo/hirehr-logo.png'
logo_2x_path = 'assets/logo/hirehr-logo-2x.png'

logo_1x.save(logo_1x_path, 'PNG', optimize=True)
logo_2x.save(logo_2x_path, 'PNG', optimize=True)

print(f"Saved {logo_1x_path} ({os.path.getsize(logo_1x_path)} bytes)")
print(f"Saved {logo_2x_path} ({os.path.getsize(logo_2x_path)} bytes)")
