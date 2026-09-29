"""Code-native SVG terminal animation; the portrait is a grid of text glyphs."""
import html
import json
from itertools import groupby
from pathlib import Path


def render(config, stats, assets):
    escape = html.escape
    def text(x, y, value, size=16, color="#d0d0d0", anchor="start"):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>'

    def section(y, title):
        start = 379 + len(title) * 9.6 + 14
        return (text(363, y, '─', 14, '#475058') + text(379, y, title, 16, '#6cb6ff')
                + f'<path d="M{start} {y-5}H922" stroke="#394047"/>')

    def row(y, label, value, x=366, end=922, size=15, value_color='#d0d0d0'):
        # Reserve exactly the glyph widths for each end of the dotted leader.
        left = x + (len(label) + 2) * size * .6 + 8
        right = end - len(str(value)) * size * .6 - 10
        dots = f'<path d="M{left} {y-4}H{right}" stroke="#475058" stroke-width="2" stroke-linecap="round" stroke-dasharray="1 7"/>' if right > left else ''
        return (dots + text(x, y, '· ' + label + ':', size, '#efa45d')
                + text(end, y, value, size, value_color, 'end'))

    portrait = assets / "portrait.txt"
    lines = portrait.read_text(encoding="utf-8").splitlines() if portrait.exists() and config.get("photo") else []
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600" viewBox="0 0 960 600" role="img" aria-labelledby="title desc">
<title id="title">Animated developer terminal</title>
<desc id="desc">A green ASCII portrait reveals from top to bottom alongside profile information and public repository statistics.</desc>
<style>
text {font-family:Consolas,"Courier New",monospace}
.reveal {animation:print 8s linear infinite}
.caret {animation:blink 1s steps(2,start) infinite}
@keyframes print {0%,5%{height:0} 55%,99.9%{height:286px} 100%{height:0}}
@keyframes blink {to{opacity:0}}
@media(prefers-reduced-motion:reduce){.reveal,.caret{animation:none}}
</style>
<defs><clipPath id="portrait"><rect class="reveal" x="30" y="154" width="288" height="286"/></clipPath></defs>
<rect width="960" height="600" fill="#fff"/>
<path d="M0 0H960V110H0Z M350 128H960V460H350Z M0 478H960V600H0Z" fill="#060706"/>
<rect x="16" y="128" width="316" height="332" rx="10" fill="#0b0e12"/>
<path d="M16 152H332 M16 429H332" stroke="#22282d"/>
<circle cx="30" cy="140" r="4" fill="#ff5f57"/><circle cx="44" cy="140" r="4" fill="#febc2e"/><circle cx="58" cy="140" r="4" fill="#28c840"/>
''']
    parts += [text(12, 19, "+", 13, "#b5f327"), text(939, 19, "+", 13, "#b5f327"),
              text(30, 54, config['name'], 30), text(30, 87, '@' + config['username'], 16, '#b5f327'),
              text(74, 143, config['username'] + '@github: ~$ ./portrait.sh', 7.5, '#8b949e')]
    tone_path = assets / 'portrait-tones.json'
    tones = json.loads(tone_path.read_text()) if tone_path.exists() else []
    cell_width = 286 / max((len(line) for line in lines), default=144)
    line_height = 264 / max(len(lines), 1)
    parts.append(f'<g clip-path="url(#portrait)" font-size="{cell_width/0.6:.3f}" xml:space="preserve">')
    for i, line in enumerate(lines):
        shades = tones[i] if i < len(tones) and len(tones[i]) == len(line) else 'f' * len(line)
        for shade, run in groupby(enumerate(shades), key=lambda item: item[1]):
            indexes = [index for index, _ in run]
            segment = line[indexes[0]:indexes[-1]+1]
            if not segment.strip():
                continue
            brightness = int(shade, 16) / 15
            color = '#%02x%02x%02x' % (int(40+145*brightness), int(55+184*brightness), int(12+34*brightness))
            parts.append(f'<text x="{30+indexes[0]*cell_width:.3f}" y="{158+i*line_height:.3f}" fill="{color}" textLength="{len(segment)*cell_width:.3f}" lengthAdjust="spacingAndGlyphs">{escape(segment)}</text>')
    parts.append('</g>')
    parts += [text(30, 448, config['username'] + '@github:~$ whoami', 7.5, '#8b949e'), text(193, 448, config['name'], 9, '#b5f327'),
              '<rect class="caret" x="298" y="438" width="7" height="12" fill="#b5f327"/>']
    parts += [text(357, 149, '+', 12, '#b5f327'), text(945, 149, '+', 12, '#b5f327'),
              section(153, config['username'] + '@github'),
              row(179, 'Focus', 'Machine learning'),
              row(201, 'Building', 'Full-stack applications'),
              row(223, 'Languages', 'Python, TypeScript, SQL'),
              section(260, 'Contact')]
    for i, (label, url) in enumerate(config['links'].items()):
        parts.append(row(283 + i * 23, label, url.removeprefix("https://")))
    parts.append(section(343, 'GitHub Stats'))
    if stats:
        parts += [row(368, 'Repos', stats['repos'], end=616, value_color='#87bfff'),
                  row(368, 'Stars', stats['stars'], x=654, value_color='#87bfff'),
                  row(391, 'Followers', stats['followers'], end=616, value_color='#87bfff'),
                  row(391, 'Languages', len(stats['languages']), x=654, value_color='#87bfff'),
                  '<path d="M635 354V396" stroke="#394047"/>',
                  text(367, 432, 'Public snapshot · ' + stats['updated'] + ' UTC', 11, '#8b949e')]
    else:
        parts.append(text(367, 389, 'Run the workflow to load public stats.', 14))
    parts.append(text(25, 506, '[ PRIMARY LANGUAGES / REPOSITORY COUNT ]', 13, '#8b949e'))
    if stats and stats['languages']:
        langs = sorted(stats['languages'].items(), key=lambda x: -x[1])
        total = sum(count for _, count in langs)
        x = 25
        colors = ['#e8d44d', '#3576b9', '#b5f327', '#ba89eb', '#49bf91']
        for i, (name, count) in enumerate(langs):
            width = 910 * count / total
            color = colors[i % len(colors)]
            parts.append(f'<rect x="{x:.2f}" y="523" width="{width:.2f}" height="9" fill="{color}"/>')
            x += width
            if i < 3:
                parts.append(text(25 + i * 310, 559, f'● {name}: {count}', 14, color))
        parts.append(text(25, 584, 'Original public repos only · Counts describe projects, not proficiency', 11, '#8b949e'))
    parts.append('</svg>')
    (assets / 'terminal.svg').write_text('\n'.join(parts), encoding='utf-8')
