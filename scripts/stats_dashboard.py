"""Render repository-owned cards with explicit scopes and no synthetic ranks."""
from collections import Counter
from datetime import date
from html import escape

COLORS = ['#e87509', '#3572a5', '#3178c6', '#82c760', '#e65b55', '#a98ade']
LANGUAGE_COLORS = {'Jupyter Notebook': '#e87509', 'Python': '#3572a5',
                   'TypeScript': '#3178c6', 'CSS': '#82c760', 'HTML': '#e65b55'}


def text(x, y, value, size=16, color='#c9d1d9', anchor='start', weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(value))}</text>'


def card(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0c1117" stroke="#30363d"/>'


def top_values(values, limit=5):
    items = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    if len(items) > limit:
        items = items[:limit] + [('Other', sum(value for _, value in items[limit:]))]
    return items


def render_stats_dashboard(config, stats, assets):
    s = stats or {}
    a = s.get('contributions', {})
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="892" viewBox="0 0 960 892" role="img" aria-labelledby="title desc">',
             '<title id="title">GitHub activity dashboard</title>',
             '<desc id="desc">Public repository statistics, languages by code size, contribution streaks, monthly contributions, languages by repository count, and contributions by weekday. Streaks and activity cover the displayed calendar period.</desc>',
             '<style>text{font-family:Segoe UI,Arial,sans-serif}</style>']
    parts += [card(1, 1, 474, 206), card(485, 1, 474, 206),
              text(25, 33, config['name'] + "'s GitHub Stats", 21, '#58a6ff', weight=600)]
    for i, (label, value) in enumerate([
        ('Stars earned · original repos', s.get('stars', '—')),
        ('Public repositories', s.get('repos', '—')),
        ('Followers', s.get('followers', '—')),
        ('Contributions · calendar period', a.get('total', '—')),
    ]):
        parts += [text(26, 72 + i*31, label, 16), text(442, 72+i*31, value, 19, '#58d4f4', 'end', 600)]
    parts.append(text(509, 33, 'Most Used Languages', 21, '#58a6ff', weight=600))
    langs = top_values(s.get('language_bytes', {}))
    total = sum(n for _, n in langs)
    x = 509
    for i, (name, count) in enumerate(langs):
        color = LANGUAGE_COLORS.get(name, COLORS[i])
        percentage = '<0.1%' if 0 < count/total < .001 else f'{count/total:.1%}'
        width = 426 * count / total
        parts.append(f'<rect x="{x:.2f}" y="55" width="{width:.2f}" height="9" fill="{color}"/>')
        x += width
        px, py = 509 + (i % 2)*219, 91 + (i//2)*30
        parts += [f'<circle cx="{px+4}" cy="{py-5}" r="4" fill="{color}"/>',
                  text(px+15, py, f'{name} {percentage}', 12)]
    parts.append(text(509, 189, 'By code bytes · original public repos', 12, '#7d93a5'))
    if not langs:
        parts.append(text(509, 105, 'Refresh to load language data.', 16))

    parts += [card(120, 221, 720, 225),
              '<path d="M360 253V408 M600 253V408" stroke="#46515e"/>',
              '<circle cx="480" cy="302" r="44" fill="none" stroke="#22b5ee" stroke-width="5"/>',
              text(240, 299, a.get('total', '—'), 38, '#58d4f4', 'middle', 700),
              text(480, 314, a.get('current', '—'), 34, '#a78bfa', 'middle', 700),
              text(720, 299, a.get('longest', '—'), 38, '#58d4f4', 'middle', 700),
              text(240, 348, 'Total Contributions', 17, '#58d4f4', 'middle'),
              text(480, 373, 'Current Streak', 17, '#58a6ff', 'middle', 600),
              text(720, 348, 'Longest Streak', 17, '#58d4f4', 'middle'),
              text(240, 375, 'Within calendar period', 12, '#8b949e', 'middle'),
              text(480, 394, 'consecutive days', 12, '#8b949e', 'middle'),
              text(720, 375, 'Days · within period', 12, '#8b949e', 'middle'),
              text(480, 429, f"{a.get('start', '—')} — {a.get('end', '—')} · Today may still be in progress", 12, '#8b949e', 'middle')]

    parts += [card(1, 460, 958, 216), text(25, 496, '@' + config['username'], 26, '#58a6ff'),
              text(25, 537, str(a.get('total', '—')) + ' contributions in period', 17, '#8da9ba'),
              text(25, 569, str(s.get('repos', '—')) + ' public repositories', 17, '#8da9ba'),
              text(25, 601, 'Joined ' + s.get('joined', '—'), 17, '#8da9ba'),
              text(405, 486, 'Monthly contributions · calendar period', 13, '#8da9ba')]
    days = a.get('days', [])
    monthly = Counter()
    weekday = [0]*7
    for day in days:
        monthly[day['date'][:7]] += day['count']
        weekday[date.fromisoformat(day['date']).weekday()] += day['count']
    months = sorted(monthly)
    peak = max(monthly.values(), default=0) or 1
    points = [(405 + i*520/max(len(months)-1, 1), 632-monthly[m]*125/peak) for i, m in enumerate(months)]
    for fraction in [0, .5, 1]:
        y = 632 - fraction*125
        parts += [f'<path d="M405 {y}H925" stroke="#202b35"/>', text(932, y+4, round(peak*fraction), 10, '#7d93a5')]
    if points:
        path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        parts += [f'<polygon points="405,632 {path} {points[-1][0]:.2f},632" fill="#39c766" fill-opacity="0.75"/>',
                  f'<polyline points="{path}" fill="none" stroke="#42d472" stroke-width="2"/>']
        for i, month in enumerate(months):
            if i % 3 == 0 or i == len(months)-1:
                parts.append(text(points[i][0], 653, month[2:], 11, '#7d93a5', 'middle'))
    else:
        parts.append(text(405, 550, 'Refresh to load contribution history.', 16))

    parts += [card(1, 690, 474, 201), card(485, 690, 474, 201),
              text(25, 724, 'Top Languages by Repo', 22, '#58a6ff'),
              text(509, 724, 'Contributions by Weekday', 22, '#58a6ff')]
    counts = top_values(s.get('languages', {}))
    count_total = sum(n for _, n in counts)
    offset = 0
    for i, (name, count) in enumerate(counts):
        color = LANGUAGE_COLORS.get(name, COLORS[i])
        portion = count/count_total*100
        parts += [f'<circle cx="365" cy="805" r="49" pathLength="100" fill="none" stroke="{color}" stroke-width="23" stroke-dasharray="{portion:.4f} {100-portion:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 365 805)"/>',
                  f'<rect x="25" y="{746+i*20}" width="10" height="10" fill="{color}"/>',
                  text(43, 756+i*20, f'{name} · {count}', 13)]
        offset += portion
    maximum = max(weekday) or 1
    for i, (label, count) in enumerate(zip(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], weekday)):
        x, h = 523+i*58, count/maximum*102
        parts += [f'<rect x="{x}" y="{856-h:.2f}" width="31" height="{h:.2f}" fill="#39c766"/>',
                  text(x+15, 850-h, count, 11, '#8da9ba', 'middle'),
                  text(x+15, 875, label, 11, '#8da9ba', 'middle')]
    parts.append('</svg>')
    (assets / 'dashboard.svg').write_text('\n'.join(parts), encoding='utf-8')
