"""Generate a GitHub-compatible profile using Python's standard library only."""
import argparse
import html
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from terminal_dashboard import render

ROOT = Path(__file__).resolve().parents[1]


def text(x, y, value, size=16, color="#e6edf3", weight="400"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" font-family="Consolas,monospace">'
            f'{html.escape(str(value))}</text>')


def svg(body, height, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" '
            f'viewBox="0 0 960 {height}" role="img" aria-label="{html.escape(title, quote=True)}">'
            f'<title>{html.escape(title)}</title>'
            f'<rect width="960" height="{height}" rx="4" fill="#080b0d"/>' + body + '</svg>\n')


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-dashboard"}
    if os.getenv("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
        return json.load(response)


def fetch_stats(username):
    user = api(f"users/{username}")
    repos = []
    page = 1
    while True:
        batch = api(f"users/{username}/repos?per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    original = [r for r in repos if not r["fork"]]
    return {"username": username, "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "repos": user["public_repos"], "followers": user["followers"],
            "stars": sum(r["stargazers_count"] for r in original),
            "languages": dict(Counter(r["language"] for r in original if r["language"]))}


def build(config, stats):
    username = config["username"]
    base = f"https://github.com/{username}"
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    render(config, stats, assets)
    banner = '''<style>
      .typing { animation: reveal 8s steps(52,end) infinite; }
      .cursor { animation: blink 1s steps(2,start) infinite; }
      @keyframes reveal { 0%,8% {width:0} 65%,95%,100% {width:870px} }
      @keyframes blink { to {opacity:0} }
      @media (prefers-reduced-motion:reduce) { .typing,.cursor {animation:none} }
      </style><defs><clipPath id="typing"><rect class="typing" x="32" y="148" width="870" height="36"/></clipPath></defs>
      <path d="M16 28h928" stroke="#293139"/>
      <circle cx="25" cy="14" r="4" fill="#ff5f57"/><circle cx="41" cy="14" r="4" fill="#febc2e"/><circle cx="57" cy="14" r="4" fill="#28c840"/>'''
    banner += text(78, 18, f"{username}@github: ~ / profile.sh", 11, "#8b949e")
    banner += text(32, 90, config["name"], 40, "#e6edf3", "700")
    banner += text(32, 124, "@" + username + "  /  build. learn. repeat.", 17, "#b5f327")
    banner += '<g clip-path="url(#typing)">' + text(32, 173, "$ " + config["tagline"], 19, "#b5f327") + '</g>'
    banner += '<rect class="cursor" x="914" y="156" width="10" height="20" fill="#b5f327"/>'
    (assets / "header.svg").write_text(svg(banner, 205, config["name"] + " — " + config["tagline"]), encoding="utf-8")
    body = text(32, 42, "GITHUB / PUBLIC SNAPSHOT", 14, "#67e8f9", "600")
    if stats:
        for x, label, value in [(32, "Public repositories", stats["repos"]), (352, "Stars on original repos", stats["stars"]), (672, "Followers", stats["followers"])]:
            body += text(x, 104, value, 42, weight="700") + text(x, 136, label, 16, "#9aafc7")
        languages = sorted(stats["languages"].items(), key=lambda pair: (-pair[1], pair[0]))
        body += text(32, 187, "Primary repo languages: " + " · ".join(f"{k} ({v})" for k, v in languages[:4]), 14, "#b9c9dc")
        body += text(32, 220, f"Updated {stats['updated']} UTC · Public data · Forks excluded from stars and languages", 12, "#8ca5bf")
    else:
        body += text(32, 108, "Your next chapter starts with a commit.", 28, weight="600")
        body += text(32, 157, "Run the profile workflow to load your public GitHub stats.", 17, "#9aafc7")
    (assets / "stats.svg").write_text(svg(body, 250, "Public GitHub statistics"), encoding="utf-8")
    esc = html.escape
    badges = []
    for group in config["stack_groups"]:
        images = []
        for label, logo, color in group["items"]:
            query = urlencode({"style": "for-the-badge", "logo": logo, "logoColor": "white", "label": "", "message": label, "color": color})
            images.append(f'<img alt="{esc(label)}" src="https://img.shields.io/static/v1?{esc(query, quote=True)}" />')
        badges.append(f'<h3 align="center">{esc(group["name"])}</h3>\n<p align="center">' + '\n'.join(images) + '</p>')
    links = " &nbsp; / &nbsp; ".join(f'<a href="{esc(url, quote=True)}">{esc(label)}</a>' for label, url in config["links"].items())
    photo = config.get("photo")
    intro = f'<img align="right" src="{esc(photo, quote=True)}" width="155" alt="Portrait of {esc(config["name"], quote=True)}" />\n\n' if photo else ""
    rows = []
    for i in range(0, len(config["projects"]), 2):
        cells = []
        for p in config["projects"][i:i + 2]:
            cells.append(f'<td width="50%" valign="top">\n<sub>{esc(p["category"])}</sub>\n<h3><a href="{base}/{p["repo"]}">{esc(p["name"])}</a></h3>\n<p>{esc(p["description"])}</p>\n<sub>{esc(p["stack"])}</sub>\n</td>')
        rows.append('<tr>\n' + '\n'.join(cells) + '\n</tr>')
    readme = f'''<!-- Generated from profile.json by scripts/build_profile.py. Edit the config, then rebuild. -->
<p align="center">
  <img src="assets/terminal.svg" width="100%" alt="{esc(config['name'])}: animated ASCII portrait, developer profile, and public GitHub statistics" />
</p>

<p align="center">{links} &nbsp; / &nbsp; <a href="{base}?tab=repositories">Explore my work ↗</a></p>

---

### Hey, I'm {esc(config['name'])} 👋

{esc(config['about'])}

**A few things you'll find here**

- Experiments with data and machine learning.
- Projects that connect models to usable interfaces.
- Web applications built around practical workflows.

<br clear="both" />

## 🛠️ Tech stack

{'\n'.join(badges)}

## 🐍 Watch my contributions get eaten

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/github-snake-dark.svg" />
  <img alt="Animated snake eating {username}'s GitHub contribution graph" src="assets/github-snake.svg" width="100%" />
</picture>

## 🚀 Selected work

<table>
{'\n'.join(rows)}
</table>

<p><a href="{base}?tab=repositories">Browse all repositories →</a></p>

## 📊 GitHub statistics

<a href="{base}?tab=repositories"><img src="assets/stats.svg" width="100%" alt="Public GitHub statistics for {username}" /></a>

## 🤝 Let's connect

Explore my projects, follow along on GitHub, or find my data science work on Kaggle.

{links}

---

<p align="center"><sub>Curiosity → experiments → useful software.</sub><br/><sub>Like this layout? <a href="docs/SETUP.md">Make it yours.</a></sub></p>
'''
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Refresh public statistics from GitHub")
    args = parser.parse_args()
    config = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", config["username"]):
        raise ValueError("Invalid GitHub username")
    cache = ROOT / "assets" / "stats.json"
    stats = None
    if args.fetch:
        stats = fetch_stats(config["username"])
        cache.parent.mkdir(exist_ok=True)
        cache.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    elif cache.exists():
        stats = json.loads(cache.read_text(encoding="utf-8"))
        if stats.get("username") != config["username"]:
            stats = None
    build(config, stats)
    print("Generated README.md, assets/header.svg, and assets/stats.svg")


if __name__ == "__main__":
    main()
