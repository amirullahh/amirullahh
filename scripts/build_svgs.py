#!/usr/bin/env python3
"""Build the animated profile SVGs (hero, about, stack, id-dashboard, connect).

Everything is self-contained: fonts and icons are inlined, animation is
CSS/SMIL only (GitHub strips JavaScript from READMEs). Every element's static
attributes describe the *finished* state, so a renderer that ignores animation
still shows a complete card.

Usage:  python3 scripts/build_svgs.py
Edit the PROFILE dict below, re-run, then bump ?v= in README.md.
"""
import base64
import json
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ----------------------------------------------------------------- profile ---
PROFILE = {
    "name": "Amirullah Hidayat",
    "first": "Amirullah",
    "handle": "amirullahh",
    "location": "Jakarta, ID",
    "school": "Informatics @ UBSI",
    "repos": 30,
    "roles": [
        "DevOps & Cloud Engineer",
        "AWS Certified Cloud Practitioner",
        "CI/CD · Docker · Automation",
        "MLOps with MLflow",
    ],
    "pitch": [
        "10+ years in sales taught me to ship on time and document",
        "everything. Now I build cloud infra the same way.",
    ],
    # repo counts per primary language (public repos, Nov 2026)
    "languages": [("TypeScript", 8), ("JavaScript", 7), ("Python", 6),
                  ("Jupyter", 3), ("HTML", 2), ("Other", 4)],
    "now": [
        ("Learning", "Kubernetes & Terraform"),
        ("Building", "CI/CD pipelines for ML"),
        ("Seeking", "DevOps / Cloud roles"),
    ],
}

# ------------------------------------------------------------------ tokens ---
BG = "#0d0e16"
CARD = "#12131f"
CARD2 = "#171829"
LINE = "#262842"
TEXT = "#e8eaf4"
MUTED = "#9aa0bd"
DIM = "#5f6485"
CYAN = "#22d3ee"
VIOLET = "#a78bfa"
PINK = "#f472b6"
GREEN = "#34d399"
GOLD = "#f5c451"


def b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def font_css():
    f = ASSETS / "fonts"
    faces = [
        ("Display", 500, "space-grotesk-latin-500-normal.woff2"),
        ("Display", 700, "space-grotesk-latin-700-normal.woff2"),
        ("Mono", 400, "jetbrains-mono-latin-400-normal.woff2"),
        ("Mono", 700, "jetbrains-mono-latin-700-normal.woff2"),
    ]
    out = []
    for fam, w, file in faces:
        out.append(
            "@font-face{font-family:'%s';font-weight:%d;font-style:normal;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}" % (fam, w, b64(f / file))
        )
    out.append(
        ".d{font-family:'Display',system-ui,sans-serif}"
        ".m{font-family:'Mono',ui-monospace,monospace}"
    )
    return "".join(out)


ICON_META = json.loads((ASSETS / "icons" / "meta.json").read_text())


def icon_path(slug):
    svg = (ASSETS / "icons" / f"{slug}.svg").read_text()
    return re.search(r'<path d="([^"]+)"', svg).group(1)


def lum(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def icon_color(slug):
    h = ICON_META[slug]["hex"]
    return TEXT if lum(h) < 0.07 else "#" + h


def icon(slug, cx, cy, size, color=None):
    """Brand icon centred at (cx, cy)."""
    s = size / 24
    c = color or icon_color(slug)
    return (f'<g transform="translate({cx - size / 2:.2f} {cy - size / 2:.2f}) scale({s:.4f})">'
            f'<path d="{icon_path(slug)}" fill="{c}"/></g>')


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def common_defs(p):
    """Shared defs, namespaced with prefix p."""
    return f"""
<linearGradient id="{p}aur" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
</linearGradient>
<linearGradient id="{p}hair" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{CYAN}" stop-opacity=".55"/>
  <stop offset=".45" stop-color="{LINE}" stop-opacity=".9"/>
  <stop offset="1" stop-color="{PINK}" stop-opacity=".45"/>
</linearGradient>
<linearGradient id="{p}glass" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{CARD2}"/><stop offset="1" stop-color="{CARD}"/>
</linearGradient>
<pattern id="{p}dots" width="14" height="14" patternUnits="userSpaceOnUse">
  <circle cx="1.5" cy="1.5" r="1" fill="#ffffff" fill-opacity=".045"/>
</pattern>
<filter id="{p}glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>"""


def card(p, x, y, w, h, r=18):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{p}glass)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{p}dots)"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" '
            f'stroke="url(#{p}hair)" stroke-width="1"/>')


def fade_in(delay, dur=0.6, total=None, dy=0):
    """Entrance that starts at 0s and uses keyTimes for the delay (fill freeze)."""
    total = total or (delay + dur)
    k = delay / total
    out = (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" '
           f'dur="{total:.2f}s" begin="0s" fill="freeze"/>')
    if dy:
        out += (f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 {dy};0 {dy};0 0" keyTimes="0;{k:.3f};1" calcMode="spline" '
                f'keySplines="0 0 1 1;.2 .8 .2 1" dur="{total:.2f}s" begin="0s" fill="freeze"/>')
    return out


def svg_doc(w, h, title, defs, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>{font_css()}</style>
<defs>{defs}</defs>
{body}
</svg>
"""


# ================================================================== HERO ====
def build_hero():
    p = "h-"
    W, H = 1000, 380
    name = PROFILE["name"]
    defs = common_defs(p) + f"""
<linearGradient id="{p}name" x1="0" y1="0" x2="600" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;600 0" dur="6s" begin="0s" repeatCount="indefinite"/>
</linearGradient>
<clipPath id="{p}nameclip"><rect x="40" y="108" width="580" height="80">
  <animate attributeName="y" values="190;190;108" keyTimes="0;.45;1" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" dur="1.6s" begin="0s" fill="freeze"/>
</rect></clipPath>
<radialGradient id="{p}aura" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="{p}scan" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".18"/>
</linearGradient>
<clipPath id="{p}vf"><rect x="622" y="34" width="346" height="312" rx="14"/></clipPath>
"""
    b = [f'<rect width="{W}" height="{H}" rx="22" fill="{BG}"/>',
         f'<rect width="{W}" height="{H}" rx="22" fill="url(#{p}dots)"/>',
         f'<circle cx="790" cy="190" r="260" fill="url(#{p}aura)"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="url(#{p}hair)"/>']

    # open-to pill
    b.append(f"""<g>{fade_in(0.1, 0.5)}
<rect x="48" y="40" width="262" height="30" rx="15" fill="{GREEN}" fill-opacity=".08" stroke="{GREEN}" stroke-opacity=".45"/>
<circle cx="66" cy="55" r="4" fill="{GREEN}"/>
<circle cx="66" cy="55" r="4" fill="none" stroke="{GREEN}" stroke-width="2">
  <animate attributeName="r" values="4;11" dur="1.8s" begin="0s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".9;0" dur="1.8s" begin="0s" repeatCount="indefinite"/>
</circle>
<text x="80" y="59.5" class="m" font-size="11.5" font-weight="700" fill="{GREEN}" letter-spacing="1.2">OPEN TO DEVOPS / CLOUD ROLES</text>
</g>""")

    # typed greeting
    greet = "Hi there, I'm"
    cw = 18 * 0.6
    steps = [f"{cw * i:.1f}" for i in range(len(greet) + 1)]
    n = len(steps)
    kt = ";".join(f"{0.2 + 0.8 * i / (n - 1):.3f}" if i else "0" for i in range(n))
    b.append(f"""<clipPath id="{p}type"><rect x="48" y="80" height="30" width="{cw * len(greet):.1f}">
  <animate attributeName="width" values="0;{';'.join(steps[1:])}" keyTimes="{kt}" calcMode="discrete" dur="1.3s" begin="0s" fill="freeze"/>
</rect></clipPath>
<text x="48" y="102" class="m" font-size="18" fill="{CYAN}" clip-path="url(#{p}type)">{esc(greet)}</text>
<rect x="{48 + cw * len(greet) + 4:.1f}" y="87" width="9" height="19" fill="{CYAN}">
  <animate attributeName="opacity" values="1;0;1" dur="1s" begin="0s" repeatCount="indefinite"/>
</rect>""")

    # name
    b.append(f'<g clip-path="url(#{p}nameclip)"><text x="46" y="170" class="d" font-size="58" '
             f'font-weight="700" fill="url(#{p}name)" letter-spacing="-1">{esc(name)}</text></g>')

    # cycling roles
    roles = PROFILE["roles"]
    T = 3.0 * len(roles)
    for i, r in enumerate(roles):
        s, e = i / len(roles), (i + 1) / len(roles)
        f = 0.025
        if i == 0:
            vals, kts = "1;1;0;0;1", f"0;{e - f:.3f};{e:.3f};{1 - f:.3f};1"
        elif i == len(roles) - 1:
            vals, kts = "0;0;1;1;0", f"0;{s - f:.3f};{s:.3f};{1 - f:.3f};1"
        else:
            vals, kts = "0;0;1;1;0;0", f"0;{s - f:.3f};{s:.3f};{e - f:.3f};{e:.3f};1"
        b.append(f"""<g opacity="{1 if i == 0 else 0}"><animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="{T}s" begin="0s" repeatCount="indefinite"/>
<text x="48" y="212" class="m" font-size="17" fill="{TEXT}"><tspan fill="{VIOLET}" font-weight="700">&gt; </tspan>{esc(r)}</text></g>""")

    # pitch
    b.append(f'<g>{fade_in(1.2, 0.7, dy=8)}<text x="48" y="252" class="d" font-size="16" font-weight="500" fill="{MUTED}">'
             + "".join(f'<tspan x="48" dy="{0 if i == 0 else 23}">{esc(t)}</tspan>' for i, t in enumerate(PROFILE["pitch"]))
             + "</text></g>")

    # meta row with drawn icons
    pin = f'<path d="M0 -7a5 5 0 0 1 5 5c0 4-5 9-5 9s-5-5-5-9a5 5 0 0 1 5-5z" fill="none" stroke="{CYAN}" stroke-width="1.6"/><circle cx="0" cy="-2" r="1.6" fill="{CYAN}"/>'
    cap = f'<path d="M-8 -2l8-4 8 4-8 4z M-5 0v4c3 2 7 2 10 0v-4" fill="none" stroke="{VIOLET}" stroke-width="1.6" stroke-linejoin="round"/>'
    repo = f'<rect x="-6" y="-7" width="12" height="14" rx="2" fill="none" stroke="{PINK}" stroke-width="1.6"/><path d="M-3 -3h6M-3 1h6" stroke="{PINK}" stroke-width="1.6"/>'
    metas = [(pin, PROFILE["location"]), (cap, PROFILE["school"]), (repo, f'{PROFILE["repos"]}+ public repos')]
    x = 56
    row = []
    for ic, t in metas:
        row.append(f'<g transform="translate({x} 324)">{ic}</g><text x="{x + 16}" y="328.5" class="m" font-size="13" fill="{MUTED}">{esc(t)}</text>')
        x += 16 + len(t) * 7.8 + 34
    b.append(f'<g>{fade_in(1.6, 0.6)}' + "".join(row) + "</g>")

    # viewfinder (right)
    vx, vy, vw, vh = 622, 34, 346, 312
    b.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="14" fill="#090a12" fill-opacity=".85"/>')
    b.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="14" fill="url(#{p}dots)"/>')
    # scanner line
    b.append(f"""<g clip-path="url(#{p}vf)"><rect x="{vx}" y="{vy - 60}" width="{vw}" height="60" fill="url(#{p}scan)">
<animateTransform attributeName="transform" type="translate" values="0 0;0 {vh + 60}" dur="4s" begin="0s" repeatCount="indefinite"/></rect></g>""")
    # corner brackets draw in
    L = 26
    corners = [
        (vx, vy + L, vx, vy, vx + L, vy),
        (vx + vw - L, vy, vx + vw, vy, vx + vw, vy + L),
        (vx + vw, vy + vh - L, vx + vw, vy + vh, vx + vw - L, vy + vh),
        (vx + L, vy + vh, vx, vy + vh, vx, vy + vh - L),
    ]
    for c in corners:
        b.append(f'<path d="M{c[0]} {c[1]}L{c[2]} {c[3]}L{c[4]} {c[5]}" fill="none" stroke="{TEXT}" stroke-width="2.5" '
                 f'stroke-linecap="round" stroke-dasharray="{2 * L}" stroke-dashoffset="0">'
                 f'<animate attributeName="stroke-dashoffset" values="{2 * L};{2 * L};0" keyTimes="0;.3;1" dur="1s" begin="0s" fill="freeze"/></path>')
    # REC + filename
    b.append(f"""<circle cx="{vx + 24}" cy="{vy + 26}" r="5" fill="#ef4444"><animate attributeName="opacity" values="1;1;.15;.15" keyTimes="0;.5;.5;1" dur="1.2s" begin="0s" repeatCount="indefinite"/></circle>
<text x="{vx + 36}" y="{vy + 30}" class="m" font-size="11" font-weight="700" fill="{TEXT}" letter-spacing="1">REC</text>
<text x="{vx + vw - 20}" y="{vy + 30}" text-anchor="end" class="m" font-size="11" fill="{DIM}">deploy_pipeline.log</text>""")

    # terminal log
    lines = [
        (DIM, "$", TEXT, "git push origin main"),
        (CYAN, "[run ]", TEXT, "GitHub Actions: build + test"),
        (CYAN, "[run ]", TEXT, "docker build -t api:1.4.2 ."),
        (GREEN, "[ ok ]", TEXT, "image pushed to Amazon ECR"),
        (CYAN, "[run ]", TEXT, "rolling deploy -> ECS service"),
        (GREEN, "[ ok ]", TEXT, "health check 200 · 3/3 tasks"),
        (GREEN, "[ ok ]", VIOLET, "deployed in 2m 41s"),
    ]
    LOOP = 8.0
    for i, (tc, tag, c, t) in enumerate(lines):
        k = 0.06 + i * 0.085
        y = vy + 70 + i * 30
        b.append(f'<g><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k:.3f};{k + 0.015:.3f};.88;.95;1" dur="{LOOP}s" begin="0s" repeatCount="indefinite"/>'
                 f'<text x="{vx + 24}" y="{y}" class="m" font-size="12.5"><tspan fill="{tc}" font-weight="700">{esc(tag)}</tspan>'
                 f'<tspan fill="{c}"> {esc(t)}</tspan></text></g>')
    cy_ = vy + 70 + len(lines) * 30 - 12
    b.append(f'<rect x="{vx + 24}" y="{cy_}" width="8" height="15" fill="{CYAN}"><animate attributeName="opacity" values="1;0;1" dur="1s" begin="0s" repeatCount="indefinite"/></rect>')
    # scrubber
    sx, sy, sw = vx + 24, vy + vh - 26, vw - 100
    b.append(f"""<rect x="{sx}" y="{sy}" width="{sw}" height="4" rx="2" fill="{LINE}"/>
<rect x="{sx}" y="{sy}" width="{sw}" height="4" rx="2" fill="url(#{p}aur)"><animate attributeName="width" values="0;{sw}" dur="{LOOP}s" begin="0s" repeatCount="indefinite"/></rect>
<circle cx="{sx + sw}" cy="{sy + 2}" r="5" fill="{TEXT}"><animate attributeName="cx" values="{sx};{sx + sw}" dur="{LOOP}s" begin="0s" repeatCount="indefinite"/></circle>
<text x="{vx + vw - 20}" y="{sy + 6}" text-anchor="end" class="m" font-size="11" fill="{DIM}">00:08</text>""")

    return svg_doc(W, H, f"{name} — DevOps & Cloud Engineer", defs, "\n".join(b))


# ================================================================= ABOUT ====
def build_about():
    p = "a-"
    W, H = 1000, 420
    defs = common_defs(p)
    b = []
    # ---- left card: what I build
    b.append(card(p, 0, 0, 490, H))
    b.append(f'<text x="28" y="40" class="m" font-size="11" font-weight="700" fill="{CYAN}" letter-spacing="2">WHAT I BUILD</text>')
    b.append(f'<text x="28" y="70" class="d" font-size="22" font-weight="700" fill="{TEXT}">Cloud infra that just works</text>')
    # browser window
    bx, by, bw, bh = 28, 88, 434, 160
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="#0a0b13" stroke="{LINE}"/>')
    b.append(f'<path d="M{bx} {by + 12}a12 12 0 0 1 12 -12h{bw - 24}a12 12 0 0 1 12 12v18h-{bw}z" fill="{CARD2}"/>')
    for i, c in enumerate(["#f87171", "#fbbf24", "#34d399"]):
        b.append(f'<circle cx="{bx + 16 + i * 14}" cy="{by + 15}" r="4" fill="{c}"/>')
    url = "aws://ap-southeast-3/vpc-prod"
    b.append(f'<rect x="{bx + 64}" y="{by + 6}" width="{bw - 80}" height="18" rx="9" fill="#0a0b13"/>')
    b.append(f'<text x="{bx + 76}" y="{by + 19}" class="m" font-size="10.5" fill="{MUTED}">{url}</text>')
    b.append(f'<rect x="{bx + 78 + len(url) * 6.3:.1f}" y="{by + 9}" width="1.5" height="12" fill="{CYAN}"><animate attributeName="opacity" values="1;0;1" dur="1s" begin="0s" repeatCount="indefinite"/></rect>')
    # architecture diagram inside
    oy = by + 40

    def node(x, y, w, label, slug=None, col=TEXT):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="8" fill="{CARD}" stroke="{LINE}"/>'
        if slug:
            s += icon(slug, x + 17, y + 17, 16)
            s += f'<text x="{x + 31}" y="{y + 21}" class="m" font-size="10.5" fill="{col}">{label}</text>'
        else:
            s += f'<text x="{x + w / 2}" y="{y + 21}" text-anchor="middle" class="m" font-size="10.5" fill="{col}">{label}</text>'
        return s
    # VPC boundary
    b.append(f'<rect x="{bx + 120}" y="{oy + 8}" width="190" height="104" rx="10" fill="none" stroke="{VIOLET}" stroke-opacity=".5" stroke-dasharray="4 4"/>')
    b.append(f'<text x="{bx + 130}" y="{oy + 22}" class="m" font-size="9" fill="{VIOLET}">VPC · private subnets</text>')
    b.append(node(bx + 14, oy + 43, 86, "users"))
    b.append(node(bx + 132, oy + 30, 78, "ECS", "docker"))
    b.append(node(bx + 132, oy + 72, 78, "EC2", "linux"))
    b.append(node(bx + 222, oy + 51, 78, "API", "fastapi"))
    b.append(node(bx + 328, oy + 30, 90, "S3", "amazonwebservices"))
    b.append(node(bx + 328, oy + 72, 90, "Mongo", "mongodb"))
    flows = [
        f"M{bx + 100} {oy + 60}H{bx + 132}",
        f"M{bx + 210} {oy + 47}H{bx + 216}V{oy + 68}H{bx + 222}",
        f"M{bx + 210} {oy + 89}H{bx + 216}V{oy + 68}H{bx + 222}",
        f"M{bx + 300} {oy + 64}H{bx + 314}V{oy + 47}H{bx + 328}",
        f"M{bx + 300} {oy + 72}H{bx + 314}V{oy + 89}H{bx + 328}",
    ]
    for i, d in enumerate(flows):
        b.append(f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-opacity=".7" stroke-width="1.4" stroke-dasharray="3 4">'
                 f'<animate attributeName="stroke-dashoffset" values="14;0" dur="0.8s" begin="0s" repeatCount="indefinite"/></path>')
    b.append(f'<circle r="3" fill="{PINK}" filter="url(#{p}glow)"><animateMotion path="M{bx + 100} {oy + 60}H{bx + 216}V{oy + 68}H{bx + 314}V{oy + 47}H{bx + 328}" dur="2.4s" begin="0s" repeatCount="indefinite"/></circle>')
    # capability rows
    caps = [
        ("amazonwebservices", "Cloud infrastructure", "VPC, EC2, S3, IAM — HA multi-tier designs"),
        ("githubactions", "CI/CD & automation", "GitHub Actions, Docker, Bash, Cloud Build"),
        ("mlflow", "MLOps & applied AI", "MLflow tracking, FastAPI serving, NLP"),
    ]
    for i, (slug, t, s) in enumerate(caps):
        y = 272 + i * 48
        b.append(f'<g>{fade_in(0.3 + i * 0.2, 0.5, dy=10)}'
                 f'<rect x="28" y="{y}" width="38" height="38" rx="10" fill="{CARD2}" stroke="url(#{p}hair)"/>'
                 f'{icon(slug, 47, y + 19, 20)}'
                 f'<text x="80" y="{y + 16}" class="d" font-size="15" font-weight="700" fill="{TEXT}">{esc(t)}</text>'
                 f'<text x="80" y="{y + 33}" class="m" font-size="11" fill="{MUTED}">{esc(s)}</text></g>')

    # ---- right card: journey carousel
    X = 510
    b.append(card(p, X, 0, 490, H))
    b.append(f'<text x="{X + 28}" y="40" class="m" font-size="11" font-weight="700" fill="{PINK}" letter-spacing="2">JOURNEY</text>')
    slides = [
        ("CERT", "amazonwebservices", "AWS Certified", "Cloud Practitioner",
         ["IAM, VPC, billing, shared", "responsibility — the fundamentals."]),
        ("COURSE", "amazonwebservices", "AWS Academy", "Cloud Architecting",
         ["Designed highly available,", "multi-tier architectures in labs."]),
        ("PROJECT", "mlflow", "CI/CD for ML", "GitHub Actions + MLflow",
         ["Pipelines that retrain, track", "and ship models automatically."]),
        ("BACKGROUND", None, "10+ years", "Sales & BizDev",
         ["Where I learned clear docs,", "steady delivery, calm under fire."]),
    ]
    n = len(slides)
    SL = 4.0
    T = SL * n
    segw = (490 - 56 - (n - 1) * 6) / n
    for i in range(n):
        x = X + 28 + i * (segw + 6)
        s, e = i / n, (i + 1) / n
        b.append(f'<rect x="{x:.1f}" y="58" width="{segw:.1f}" height="3" rx="1.5" fill="{LINE}"/>')
        b.append(f'<rect x="{x:.1f}" y="58" width="{segw if i == 0 else 0:.1f}" height="3" rx="1.5" fill="{TEXT}">'
                 f'<animate attributeName="width" values="0;0;{segw:.1f};{segw:.1f}" keyTimes="0;{s:.3f};{e:.3f};1" dur="{T}s" begin="0s" repeatCount="indefinite"/></rect>')
    f = 0.02
    for i, (tag, slug, t1, t2, cap) in enumerate(slides):
        s, e = i / n, (i + 1) / n
        if i == 0:
            vals, kts = "1;1;0;0;1", f"0;{e - f:.3f};{e:.3f};{1 - f:.3f};1"
        elif i == n - 1:
            vals, kts = "0;0;1;1;0", f"0;{s - f:.3f};{s:.3f};{1 - f:.3f};1"
        else:
            vals, kts = "0;0;1;1;0;0", f"0;{s - f:.3f};{s:.3f};{e - f:.3f};{e:.3f};1"
        cx = X + 28
        art = (icon(slug, cx + 46, 136, 46) if slug else
               f'<text x="{cx + 46}" y="152" text-anchor="middle" class="d" font-size="38" font-weight="700" fill="url(#{p}aur)">10+</text>')
        b.append(f"""<g opacity="{1 if i == 0 else 0}"><animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="{T}s" begin="0s" repeatCount="indefinite"/>
<rect x="{cx}" y="90" width="92" height="92" rx="20" fill="{CARD2}" stroke="url(#{p}hair)"/>
{art}
<rect x="{cx + 112}" y="94" width="{len(tag) * 7.2 + 18:.0f}" height="20" rx="10" fill="{VIOLET}" fill-opacity=".14"/>
<text x="{cx + 121}" y="108" class="m" font-size="10" font-weight="700" fill="{VIOLET}" letter-spacing="1.2">{tag}</text>
<text x="{cx + 112}" y="142" class="d" font-size="22" font-weight="700" fill="{TEXT}">{esc(t1)}</text>
<text x="{cx + 112}" y="168" class="d" font-size="17" font-weight="500" fill="{MUTED}">{esc(t2)}</text>
<text x="{cx}" y="216" class="d" font-size="15" font-weight="500" fill="{MUTED}"><tspan x="{cx}">{esc(cap[0])}</tspan><tspan x="{cx}" dy="22">{esc(cap[1])}</tspan></text>
</g>""")
    # dots indicator
    # daily rings
    b.append(f'<line x1="{X + 28}" y1="272" x2="{X + 462}" y2="272" stroke="{LINE}"/>')
    b.append(f'<text x="{X + 28}" y="298" class="m" font-size="11" font-weight="700" fill="{DIM}" letter-spacing="2">DAILY RINGS</text>')
    rings = [("Build", CYAN, .82), ("Learn", VIOLET, .95), ("Ship", PINK, .7)]
    R = 26
    C = 2 * math.pi * R
    for i, (lbl, col, pct) in enumerate(rings):
        cx, cy = X + 70 + i * 145, 354
        off = C * (1 - pct)
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{col}" stroke-opacity=".15" stroke-width="7"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{col}" stroke-width="7" stroke-linecap="round" '
                 f'stroke-dasharray="{C:.1f}" stroke-dashoffset="{off:.1f}" transform="rotate(-90 {cx} {cy})">'
                 f'<animate attributeName="stroke-dashoffset" values="{C:.1f};{C:.1f};{off:.1f};{off:.1f};{C:.1f}" keyTimes="0;{.05 + i * .05:.2f};{.35 + i * .05:.2f};.92;1" '
                 f'calcMode="spline" keySplines="0 0 1 1;.3 .7 .3 1;0 0 1 1;.5 0 .5 1" dur="6s" begin="0s" repeatCount="indefinite"/></circle>')
        b.append(f'<text x="{cx + R + 16}" y="{cy - 3}" class="d" font-size="15" font-weight="700" fill="{TEXT}">{lbl}</text>')
        b.append(f'<text x="{cx + R + 16}" y="{cy + 15}" class="m" font-size="11" fill="{MUTED}">{int(pct * 100)}%</text>')
    return svg_doc(W, H, "What I build and my journey", defs, "\n".join(b))


# ================================================================= STACK ====
def ellipse_path(cx, cy, rx, ry, tilt, steps=96):
    t = math.radians(tilt)
    pts = []
    for i in range(steps + 1):
        a = 2 * math.pi * i / steps
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t)))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z", pts


def build_stack():
    p = "s-"
    W, H = 1000, 470
    defs = common_defs(p) + f"""
<radialGradient id="{p}core" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{VIOLET}" stop-opacity=".9"/><stop offset=".55" stop-color="{CYAN}" stop-opacity=".25"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
</radialGradient>"""
    b = [card(p, 0, 0, W, H)]
    b.append(f'<text x="28" y="40" class="m" font-size="11" font-weight="700" fill="{CYAN}" letter-spacing="2">TECH ORBIT</text>')
    cx, cy = 262, 250
    # core
    b.append(f'<circle cx="{cx}" cy="{cy}" r="70" fill="url(#{p}core)"><animate attributeName="r" values="62;74;62" dur="3s" begin="0s" repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{BG}" stroke="url(#{p}hair)" stroke-width="1.5"/>')
    inf = (f"M{cx} {cy}C{cx + 8} {cy - 12} {cx + 22} {cy - 12} {cx + 22} {cy}S{cx + 8} {cy + 12} {cx} {cy}"
           f"S{cx - 22} {cy - 12} {cx - 22} {cy}S{cx - 8} {cy + 12} {cx} {cy}")
    b.append(f'<path d="{inf}" fill="none" stroke="{LINE}" stroke-width="3"/>')
    b.append(f'<path d="{inf}" fill="none" stroke="url(#{p}aur)" stroke-width="3" stroke-linecap="round" stroke-dasharray="30 70" pathLength="100">'
             f'<animate attributeName="stroke-dashoffset" values="100;0" dur="2.4s" begin="0s" repeatCount="indefinite"/></path>')

    orbits = [
        (238, 96, -16, 34, ["amazonwebservices", "googlecloud", "linux", "mongodb", "typescript"]),
        (182, 100, 32, 26, ["docker", "python", "gnubash", "git"]),
        (128, 74, 96, 20, ["githubactions", "fastapi", "vuedotjs"]),
    ]
    tiles = []
    for (rx, ry, tilt, dur, slugs) in orbits:
        d, pts = ellipse_path(cx, cy, rx, ry, tilt)
        b.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.2"/>')
        b.append(f'<path d="{d}" fill="none" stroke="url(#{p}aur)" stroke-opacity=".5" stroke-width="1.2" stroke-dasharray="40 600" pathLength="640">'
                 f'<animate attributeName="stroke-dashoffset" values="640;0" dur="{dur / 2}s" begin="0s" repeatCount="indefinite"/></path>')
        for j, slug in enumerate(slugs):
            ph = j / len(slugs)
            sx, sy = pts[int(ph * (len(pts) - 1))]
            kp = f"{ph:.4f};1;0;{ph:.4f}" if ph > 0 else "0;1"
            kt = f"0;{1 - ph:.4f};{1 - ph:.4f};1" if ph > 0 else "0;1"
            moons = ""
            if slug == "docker":
                mr = 34
                ms = []
                for k, (ms_slug, a0) in enumerate([("prometheus", 0), ("grafana", 180)]):
                    mx, my = mr * math.cos(math.radians(a0)), mr * math.sin(math.radians(a0))
                    ms.append(f'<g transform="translate({mx:.1f} {my:.1f})"><g><animateTransform attributeName="transform" type="rotate" values="0;-360" dur="5s" begin="0s" repeatCount="indefinite"/>'
                              f'<circle r="11" fill="{CARD2}" stroke="{LINE}"/>{icon(ms_slug, 0, 0, 12)}</g></g>')
                moons = (f'<circle r="{mr}" fill="none" stroke="{LINE}" stroke-dasharray="2 4"/>'
                         f'<g><animateTransform attributeName="transform" type="rotate" values="0;360" dur="5s" begin="0s" repeatCount="indefinite"/>{"".join(ms)}</g>')
            tiles.append(f"""<g transform="translate({sx:.1f} {sy:.1f})"><animateTransform attributeName="transform" type="translate" values="0 0" dur="0.01s" begin="0s" fill="freeze"/>
<g><animateMotion path="{d}" keyPoints="{kp}" keyTimes="{kt}" calcMode="linear" dur="{dur}s" begin="0s" repeatCount="indefinite"/>
{moons}<circle r="20" fill="{CARD2}" stroke="url(#{p}hair)"/>{icon(slug, 0, 0, 20)}</g></g>""")
    b.extend(tiles)

    # chip grid
    groups = [
        ("CLOUD & INFRA", ["amazonwebservices", "googlecloud", "huawei", "linux", "docker"]),
        ("CI/CD & AUTOMATION", ["githubactions", "git", "gnubash", "github"]),
        ("DATA & OBSERVABILITY", ["mongodb", "prometheus", "grafana"]),
        ("AI & BACKEND", ["python", "fastapi", "mlflow", "nodedotjs", "vuedotjs"]),
    ]
    short = {"amazonwebservices": "AWS", "googlecloud": "GCP", "huawei": "Huawei", "gnubash": "Bash",
             "githubactions": "Actions", "nodedotjs": "Node.js", "vuedotjs": "Vue"}
    gx, gy = 530, 92
    all_chips = []
    y = gy
    for title, slugs in groups:
        b.append(f'<text x="{gx}" y="{y}" class="m" font-size="10.5" font-weight="700" fill="{DIM}" letter-spacing="1.8">{esc(title)}</text>')
        x = gx
        y += 14
        for slug in slugs:
            lbl = short.get(slug, ICON_META[slug]["title"])
            w = 36 + len(lbl) * 7.6
            if x + w > W - 28:
                x = gx
                y += 40
            all_chips.append((x, y, w, slug, lbl))
            x += w + 8
        y += 40 + 34
    N = len(all_chips)
    T = N * 0.35
    for i, (x, y, w, slug, lbl) in enumerate(all_chips):
        k = i / N
        k2 = min(k + 1.6 / N, 1)
        col = icon_color(slug)
        b.append(f'<g>{fade_in(0.1 + i * 0.05, 0.4)}<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="{CARD2}" stroke="{LINE}"/>'
                 f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="none" stroke="{col}" stroke-width="1.4" opacity="0">'
                 f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k:.3f};{(k + k2) / 2:.3f};{k2:.3f};1" dur="{T:.1f}s" begin="0s" repeatCount="indefinite"/></rect>'
                 f'{icon(slug, x + 17, y + 15, 14)}<text x="{x + 30:.1f}" y="{y + 19.5}" class="m" font-size="12" fill="{TEXT}">{esc(lbl)}</text></g>')
    return svg_doc(W, H, "Tech stack orbit", defs, "\n".join(b))


# ========================================================== ID DASHBOARD ====
def build_id_dashboard():
    p = "i-"
    W, H = 1000, 500
    defs = common_defs(p) + f"""
<linearGradient id="{p}metal" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#e5e7eb"/><stop offset=".5" stop-color="#6b7280"/><stop offset="1" stop-color="#d1d5db"/>
</linearGradient>
<linearGradient id="{p}gold" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fde68a"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="#b7791f"/>
</linearGradient>
<linearGradient id="{p}foil" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".42" stop-color="{CYAN}" stop-opacity=".0"/>
  <stop offset=".48" stop-color="{CYAN}" stop-opacity=".22"/>
  <stop offset=".52" stop-color="{PINK}" stop-opacity=".22"/>
  <stop offset=".58" stop-color="{VIOLET}" stop-opacity="0"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<linearGradient id="{p}strap" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#3b2f8f"/><stop offset=".5" stop-color="#5b45c9"/><stop offset="1" stop-color="#3b2f8f"/>
</linearGradient>
<linearGradient id="{p}avbg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1e3a5f"/><stop offset="1" stop-color="#3b1f5c"/>
</linearGradient>
<clipPath id="{p}cardclip"><rect x="62" y="132" width="236" height="342" rx="18"/></clipPath>
<clipPath id="{p}avclip"><rect x="122" y="196" width="116" height="116" rx="16"/></clipPath>
"""
    b = [f'<rect width="{W}" height="{H}" rx="22" fill="{BG}"/>', f'<rect width="{W}" height="{H}" rx="22" fill="url(#{p}dots)"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="url(#{p}hair)"/>']
    px, py = 180, -6
    badge = []
    # strap
    badge.append(f'<path d="M160 -10L166 112H194L200 -10Z" fill="url(#{p}strap)"/>')
    badge.append(f'<text transform="translate(184 4) rotate(90)" class="m" font-size="9" font-weight="700" fill="#c7bfff" letter-spacing="2.2">AMIRULLAH</text>')
    # clasp
    badge.append(f'<rect x="164" y="104" width="32" height="18" rx="5" fill="url(#{p}metal)"/>')
    badge.append(f'<rect x="168" y="118" width="24" height="22" rx="8" fill="none" stroke="url(#{p}metal)" stroke-width="4"/>')
    # card
    cx0, cy0, cw, ch = 62, 132, 236, 342
    badge.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="18" fill="url(#{p}glass)" stroke="url(#{p}hair)" stroke-width="1.5"/>')
    badge.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="18" fill="url(#{p}dots)"/>')
    badge.append(f'<rect x="166" y="144" width="28" height="7" rx="3.5" fill="{BG}" stroke="{LINE}"/>')
    badge.append(f'<text x="80" y="178" class="m" font-size="9.5" font-weight="700" fill="{CYAN}" letter-spacing="2">ID · CLOUD OPS</text>')
    badge.append(f'<text x="280" y="178" text-anchor="end" class="m" font-size="9.5" fill="{DIM}">No. 0399</text>')
    # avatar (abstract portrait + monogram)
    badge.append(f'<g clip-path="url(#{p}avclip)"><rect x="122" y="196" width="116" height="116" fill="url(#{p}avbg)"/>'
                 f'<circle cx="180" cy="242" r="24" fill="#c9a27e"/>'
                 f'<path d="M154 236c0-22 14-32 28-32s26 10 26 30c-6-8-16-12-30-12s-18 6-24 14z" fill="#1b1b24"/>'
                 f'<rect x="162" y="232" width="16" height="9" rx="3" fill="none" stroke="#1b1b24" stroke-width="2.5"/>'
                 f'<rect x="182" y="232" width="16" height="9" rx="3" fill="none" stroke="#1b1b24" stroke-width="2.5"/>'
                 f'<path d="M178 236h4" stroke="#1b1b24" stroke-width="2"/>'
                 f'<path d="M136 312c4-28 22-42 44-42s40 14 44 42z" fill="#e8eaf4"/>'
                 f'<path d="M168 272l12 14 12-14" fill="none" stroke="{GOLD}" stroke-width="3"/></g>')
    badge.append(f'<rect x="122" y="196" width="116" height="116" rx="16" fill="none" stroke="{LINE}" stroke-width="2"/>')
    badge.append(f'<rect x="122" y="196" width="116" height="116" rx="16" fill="none" stroke="url(#{p}aur)" stroke-width="2.5" '
                 f'stroke-linecap="round" pathLength="100" stroke-dasharray="18 82">'
                 f'<animate attributeName="stroke-dashoffset" values="100;0" dur="3s" begin="0s" repeatCount="indefinite"/></rect>')
    badge.append(f'<text x="180" y="342" text-anchor="middle" class="d" font-size="20" font-weight="700" fill="{TEXT}">{esc(PROFILE["name"])}</text>')
    badge.append(f'<text x="180" y="362" text-anchor="middle" class="m" font-size="10.5" fill="{MUTED}">DevOps &amp; Cloud Engineer</text>')
    # gold chip
    badge.append(f'<rect x="82" y="384" width="38" height="28" rx="5" fill="url(#{p}gold)"/>'
                 f'<path d="M82 394h12M82 402h12M108 394h12M108 402h12M94 384v28M108 384v28" stroke="#8a5a12" stroke-width="1" opacity=".7"/>')
    badge.append(f'<text x="132" y="396" class="m" font-size="9" fill="{DIM}">CERTIFIED</text>'
                 f'<text x="132" y="410" class="m" font-size="11" font-weight="700" fill="{GOLD}">AWS · CCP</text>')
    # barcode
    rnd = random.Random(399)
    x = 82
    bars = []
    while x < 278:
        w = rnd.choice([1, 1, 2, 3])
        bars.append(f'<rect x="{x}" y="428" width="{w}" height="26" fill="{TEXT}" fill-opacity=".75"/>')
        x += w + rnd.choice([1, 2, 2, 3])
    badge.append("".join(bars))
    # foil sweep
    badge.append(f'<g clip-path="url(#{p}cardclip)"><rect x="-200" y="100" width="340" height="420" fill="url(#{p}foil)">'
                 f'<animateTransform attributeName="transform" type="translate" values="-60 0;460 0;460 0" keyTimes="0;.6;1" dur="4.5s" begin="0s" repeatCount="indefinite"/></rect></g>')

    swing = ";".join(f"{a} {px} {py}" for a in [0, 0, 9, -6, 4, -2.5, 1.2, 0])
    b.append(f"""<g><animateTransform attributeName="transform" type="translate" values="0 -480;0 -480;0 0" keyTimes="0;.15;1" calcMode="spline" keySplines="0 0 1 1;.3 1.2 .5 1" dur="1.2s" begin="0s" fill="freeze"/>
<g><animateTransform attributeName="transform" type="rotate" values="{swing}" keyTimes="0;.18;.32;.46;.6;.74;.88;1" calcMode="spline" keySplines="{';'.join(['.4 0 .6 1'] * 7)}" dur="4.5s" begin="0s" fill="freeze"/>
<g><animateTransform attributeName="transform" type="rotate" values="0 {px} {py};1.2 {px} {py};0 {px} {py};-1.2 {px} {py};0 {px} {py}" dur="6s" begin="0s" repeatCount="indefinite"/>
{''.join(badge)}
</g></g></g>""")

    # ---- dashboard
    DX = 352
    b.append(f'<text x="{DX}" y="44" class="m" font-size="11" font-weight="700" fill="{VIOLET}" letter-spacing="2">DASHBOARD</text>')
    kpis = [(PROFILE["repos"], "+", "public repos"), (10, "+", "yrs in sales & BD"), (3, "", "clouds explored"), (8, "", "languages used")]
    tw = (W - DX - 28 - 3 * 12) / 4
    for i, (val, suf, lbl) in enumerate(kpis):
        x = DX + i * (tw + 12)
        b.append(card(p, x, 60, tw, 96, 14))
        frames = sorted(set([round(val * k / 6) for k in range(7)]))
        nfr = len(frames)
        st, en = 0.15 + i * 0.1, 1.0 + i * 0.1
        tot = en + 0.05
        for j, v in enumerate(frames):
            a = (st + (en - st) * j / nfr) / tot
            bb = (st + (en - st) * (j + 1) / nfr) / tot
            if j == nfr - 1:
                anim = f'<animate attributeName="opacity" values="0;1" keyTimes="0;{a:.3f}" calcMode="discrete" dur="{tot:.2f}s" begin="0s" fill="freeze"/>'
            else:
                anim = f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{a:.3f};{bb:.3f}" calcMode="discrete" dur="{tot:.2f}s" begin="0s" fill="freeze"/>'
            b.append(f'<text x="{x + 18:.1f}" y="112" class="d" font-size="34" font-weight="700" fill="{TEXT}" opacity="{1 if j == nfr - 1 else 0}">{anim}{v}<tspan fill="{CYAN}">{suf}</tspan></text>')
        b.append(f'<text x="{x + 18:.1f}" y="138" class="m" font-size="10.5" fill="{MUTED}">{esc(lbl)}</text>')

    # bar chart
    by0 = 176
    chw = 380
    b.append(card(p, DX, by0, chw, 300, 14))
    b.append(f'<text x="{DX + 20}" y="{by0 + 32}" class="d" font-size="15" font-weight="700" fill="{TEXT}">Repos by language</text>')
    b.append(f'<text x="{DX + 20}" y="{by0 + 50}" class="m" font-size="10.5" fill="{DIM}">{sum(v for _, v in PROFILE["languages"])} public repositories</text>')
    mx = max(v for _, v in PROFILE["languages"])
    barmax = chw - 150
    for i, (lang, v) in enumerate(PROFILE["languages"]):
        y = by0 + 74 + i * 36
        w = barmax * v / mx
        op = 1 - i * 0.12
        b.append(f'<text x="{DX + 20}" y="{y + 14}" class="m" font-size="11.5" fill="{MUTED}">{lang}</text>')
        b.append(f'<rect x="{DX + 110}" y="{y}" width="{barmax}" height="18" rx="5" fill="{LINE}" fill-opacity=".5"/>')
        b.append(f'<rect x="{DX + 110}" y="{y}" width="{w:.1f}" height="18" rx="5" fill="{CYAN}" fill-opacity="{op:.2f}">'
                 f'<animate attributeName="width" values="0;0;{w:.1f}" keyTimes="0;{(0.3 + i * 0.1) / 1.6:.3f};1" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" dur="1.6s" begin="0s" fill="freeze"/></rect>')
        b.append(f'<text x="{DX + 110 + w + 8:.1f}" y="{y + 13.5}" class="m" font-size="11.5" font-weight="700" fill="{TEXT}">{fade_in(1.2 + i * 0.05, 0.3)}{v}</text>')

    # now panel
    nx = DX + chw + 12
    nw = W - 28 - nx
    b.append(card(p, nx, by0, nw, 300, 14))
    b.append(f'<text x="{nx + 20}" y="{by0 + 32}" class="d" font-size="15" font-weight="700" fill="{TEXT}">Now</text>')
    b.append(f'<circle cx="{nx + nw - 70}" cy="{by0 + 28}" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" begin="0s" repeatCount="indefinite"/></circle>'
             f'<text x="{nx + nw - 20}" y="{by0 + 32}" text-anchor="end" class="m" font-size="10.5" fill="{GREEN}">online</text>')
    cols = [CYAN, VIOLET, PINK]
    for i, (k, v) in enumerate(PROFILE["now"]):
        y = by0 + 70 + i * 74
        b.append(f'<g>{fade_in(0.6 + i * 0.25, 0.5, dy=8)}<rect x="{nx + 20}" y="{y}" width="3" height="44" rx="1.5" fill="{cols[i]}"/>'
                 f'<text x="{nx + 34}" y="{y + 15}" class="m" font-size="10" font-weight="700" fill="{cols[i]}" letter-spacing="1.6">{k.upper()}</text>'
                 f'<text x="{nx + 34}" y="{y + 37}" class="d" font-size="15" font-weight="500" fill="{TEXT}">{esc(v)}</text></g>')
    return svg_doc(W, H, "ID badge and dashboard", defs, "\n".join(b))


# =============================================================== CONNECT ====
def build_connect():
    p = "c-"
    W, H = 1000, 250
    defs = common_defs(p)
    b = [card(p, 0, 0, W, H)]
    # terminal
    tx, ty, tw, th = 24, 24, 380, 202
    b.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="#0a0b13" stroke="{LINE}"/>')
    for i, c in enumerate(["#f87171", "#fbbf24", "#34d399"]):
        b.append(f'<circle cx="{tx + 18 + i * 14}" cy="{ty + 17}" r="4" fill="{c}"/>')
    b.append(f'<text x="{tx + tw / 2}" y="{ty + 21}" text-anchor="middle" class="m" font-size="10.5" fill="{DIM}">~/connect</text>')
    lines = [
        (f'<tspan fill="{GREEN}">$</tspan> whoami', 0.2),
        (f'<tspan fill="{TEXT}">amirullah — devops &amp; cloud</tspan>', 0.5),
        (f'<tspan fill="{GREEN}">$</tspan> ping amirullah', 0.9),
        (f'<tspan fill="{MUTED}">reply: usually within </tspan><tspan fill="{CYAN}">24h</tspan>', 1.2),
        (f'<tspan fill="{GREEN}">$</tspan> ./say-hi.sh <tspan fill="{VIOLET}">--channel</tspan>', 1.6),
    ]
    for i, (t, d) in enumerate(lines):
        b.append(f'<g>{fade_in(d, 0.25)}<text x="{tx + 20}" y="{ty + 56 + i * 27}" class="m" font-size="13" fill="{TEXT}">{t}</text></g>')
    b.append(f'<rect x="{tx + 268}" y="{ty + 56 + 4 * 27 - 12}" width="8" height="15" fill="{CYAN}"><animate attributeName="opacity" values="1;0;1" dur="1s" begin="0s" repeatCount="indefinite"/></rect>')
    # pointing arrow
    b.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;8 0;0 0" dur="1.4s" begin="0s" repeatCount="indefinite"/>'
             f'<path d="M418 125h30m-10 -10l10 10-10 10" fill="none" stroke="url(#{p}aur)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>')
    # link cards
    links = [("linkedin", "LinkedIn", "in/amir-399b0057"), ("gmail", "Email", "amirullahhidayat12"), ("credly", "Credly", "AWS badges")]
    cx = 470
    cw = (W - 24 - cx - 2 * 14) / 3
    for i, (slug, t, s) in enumerate(links):
        x = cx + i * (cw + 14)
        b.append(f'<g>{fade_in(0.4 + i * 0.15, 0.5, dy=10)}{card(p, x, 46, cw, 158, 16)}'
                 f'<rect x="{x + 20}" y="66" width="44" height="44" rx="12" fill="#{ICON_META[slug]["hex"]}" fill-opacity=".14"/>'
                 f'{icon(slug, x + 42, 88, 22)}'
                 f'<text x="{x + 20}" y="146" class="d" font-size="18" font-weight="700" fill="{TEXT}">{t}</text>'
                 f'<text x="{x + 20}" y="168" class="m" font-size="10.5" fill="{MUTED}">{esc(s)}</text>'
                 f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;5 -5;0 0" keyTimes="0;{.3 + i * .15:.2f};{.45 + i * .15:.2f};1" dur="2.4s" begin="0s" repeatCount="indefinite"/>'
                 f'<path d="M{x + cw - 38} 92l12 -12m-9 0h9v9" fill="none" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    return svg_doc(W, H, "Connect with Amirullah", defs, "\n".join(b))


def main():
    outputs = {
        "hero.svg": build_hero(),
        "about.svg": build_about(),
        "stack.svg": build_stack(),
        "id-dashboard.svg": build_id_dashboard(),
        "connect.svg": build_connect(),
    }
    for name, svg in outputs.items():
        (ROOT / name).write_text(svg, encoding="utf-8")
        print(f"wrote {name} ({len(svg) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
