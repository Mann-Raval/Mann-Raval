"""Sample a portrait into text for the code-native SVG (requires Pillow)."""
import json
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))
source = ROOT / config['photo']
# Tighten the supplied portrait around the face and shoulders for legible ASCII.
with Image.open(source) as image:
    image = ImageOps.exif_transpose(image)
    width, height = image.size
    crop = config.get('portrait_crop', [.12, .13, .88, .79])
    image = image.crop((width * crop[0], height * crop[1], width * crop[2], height * crop[3]))
    # Dense sampling and separate brightness prevent every glyph becoming the
    # same neon stripe. Keep the original photo untouched; output text only.
    columns, rows = 144, 112
    pixels = image.convert('RGB').resize((columns, rows), Image.Resampling.LANCZOS)
    luminance = ImageOps.autocontrast(pixels.convert('L'))
    background = config.get('portrait_background')
    ramp = '.:;=+*#%@'
    lines, tones = [], []
    for y in range(rows):
        chars, shades = [], []
        for x in range(columns):
            rgb = pixels.getpixel((x, y))
            distance = sum((rgb[i]-background[i])**2 for i in range(3))**.5 if background else 999
            if distance < 38:
                chars.append(' ')
                shades.append('0')
                continue
            value = (luminance.getpixel((x, y))/255)**.72
            chars.append(ramp[min(len(ramp)-1, int(value * len(ramp)))])
            shades.append(format(max(1, min(15, round(value*15))), 'x'))
        lines.append(''.join(chars))
        tones.append(''.join(shades))
(ROOT / 'assets/portrait.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
(ROOT / 'assets/portrait-tones.json').write_text(json.dumps(tones), encoding='utf-8')
print('Prepared ASCII text grid; original photo unchanged.')
