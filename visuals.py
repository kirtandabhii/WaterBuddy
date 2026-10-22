"""
visuals.py - Draws Boondi the mascot and the water bottle.

Both pictures are SVG (Scalable Vector Graphics): plain text that
describes shapes - circles, lines and paths. Python builds that text
with f-strings and the browser draws it. This is our browser-friendly
replacement for Turtle graphics, which needs a desktop window and would
crash on Streamlit Cloud.

Small CSS animations make Boondi bob, wave and bounce, and make the
water rise from the old level to the new level.
"""

import base64

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

INK = "#0B3B4A"         # outlines, eyes and mouth
CHEEK = "#F9A8D4"       # pink blush
WATER_LIGHT = "#7DD3FC"
WATER_DEEP = "#0891B2"

# Body colours (top of gradient, bottom of gradient) for every mood.
# Boondi looks pale and dry when thirsty and bright when hydrated.
BODY_COLOURS = {
    "thirsty": ("#E2F2F5", "#A9CBD4"),
    "waking": ("#C7ECFA", "#6CC4DD"),
    "smiling": ("#A5E4FA", "#2BB3D3"),
    "happy": ("#8EDCFA", "#16A6C9"),
    "excited": ("#7DD3FC", "#0EA5C6"),
    "celebrating": ("#67E8F9", "#0891B2"),
    "overflowing": ("#7DD3FC", "#0E7490"),
}

# Which animation Boondi's whole body uses in each mood.
BODY_ANIMATION = {
    "thirsty": "wb-sway 3s ease-in-out infinite",
    "waking": "wb-bob 3s ease-in-out infinite",
    "smiling": "wb-bob 2.4s ease-in-out infinite",
    "happy": "wb-bob 1.8s ease-in-out infinite",
    "excited": "wb-bob 1.2s ease-in-out infinite",
    "celebrating": "wb-bounce 1s ease-in-out infinite",
    "overflowing": "wb-bob 3.5s ease-in-out infinite",
}

# CSS animations used inside the pictures.
ANIMATION_CSS = """
@keyframes wb-bob    { 0%,100% { transform: translateY(0); }   50% { transform: translateY(-6px); } }
@keyframes wb-sway   { 0%,100% { transform: rotate(-2deg); }   50% { transform: rotate(2deg); } }
@keyframes wb-bounce { 0%,100% { transform: translateY(0); }   30% { transform: translateY(-16px); }
                       55% { transform: translateY(0); }       75% { transform: translateY(-6px); } }
@keyframes wb-wave   { 0%,100% { transform: rotate(-14deg); }  50% { transform: rotate(20deg); } }
@keyframes wb-fall   { 0% { transform: translateY(-30px); opacity: 0; } 15% { opacity: 1; }
                       100% { transform: translateY(230px); opacity: 0; } }
@keyframes wb-rise-bubble { 0% { transform: translateY(0); opacity: 0; } 20% { opacity: .8; }
                            100% { transform: translateY(-70px); opacity: 0; } }
@keyframes wb-twinkle { 0%,100% { opacity: .2; transform: scale(.7); } 50% { opacity: 1; transform: scale(1); } }
@keyframes wb-slide  { from { transform: translateX(0); } to { transform: translateX(-70px); } }
.wb-body  { transform-box: fill-box; transform-origin: center bottom; }
.wb-arm-l { transform-box: fill-box; transform-origin: right bottom; }
.wb-arm-r { transform-box: fill-box; transform-origin: left bottom; }
.wb-spark { transform-box: fill-box; transform-origin: center; }
"""


# ---------------------------------------------------------------------------
# Boondi the mascot - each part is its own small function
# ---------------------------------------------------------------------------

def _droplet_body(mood):
    """The droplet shape with a gradient fill and a shiny highlight."""
    top, bottom = BODY_COLOURS[mood]
    return f"""
    <defs>
      <linearGradient id="wb-body-{mood}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{top}"/>
        <stop offset="100%" stop-color="{bottom}"/>
      </linearGradient>
    </defs>
    <path d="M100 18 C100 18 32 100 32 148 A68 68 0 0 0 168 148 C168 100 100 18 100 18 Z"
          fill="url(#wb-body-{mood})" stroke="{INK}" stroke-width="3"/>
    <ellipse cx="70" cy="112" rx="10" ry="18" fill="white" opacity="0.55"
             transform="rotate(25 70 112)"/>
    """


def _eyes(mood):
    """Eyes change shape with the mood."""
    if mood == "thirsty":
        # tired, half-closed eyes
        return f"""
        <path d="M68 144 L86 148" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
        <path d="M114 148 L132 144" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>"""
    if mood == "celebrating":
        # closed, happy "^ ^" eyes
        return f"""
        <path d="M68 150 Q77 136 86 150" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>
        <path d="M114 150 Q123 136 132 150" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>"""
    if mood == "overflowing":
        # relaxed, content eyes
        return f"""
        <path d="M68 145 Q77 152 86 145" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>
        <path d="M114 145 Q123 152 132 145" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>"""

    # open round eyes - bigger when happier
    sizes = {"waking": 6, "smiling": 7.5, "happy": 8.5, "excited": 9.5}
    r = sizes[mood]
    return f"""
    <circle cx="77" cy="145" r="{r}" fill="{INK}"/>
    <circle cx="123" cy="145" r="{r}" fill="{INK}"/>
    <circle cx="80" cy="142" r="{r / 3}" fill="white"/>
    <circle cx="126" cy="142" r="{r / 3}" fill="white"/>"""


def _mouth(mood):
    """Mouth goes from a wobbly line (thirsty) to a big open grin."""
    shapes = {
        "thirsty": f'<path d="M88 180 Q94 175 100 180 Q106 185 112 180" stroke="{INK}" '
                   f'stroke-width="3.5" fill="none" stroke-linecap="round"/>',
        "waking": f'<path d="M91 175 Q100 181 109 175" stroke="{INK}" stroke-width="3.5" '
                  f'fill="none" stroke-linecap="round"/>',
        "smiling": f'<path d="M87 172 Q100 186 113 172" stroke="{INK}" stroke-width="4" '
                   f'fill="none" stroke-linecap="round"/>',
        "happy": f'<path d="M86 170 Q100 192 114 170 Z" fill="{INK}"/>',
        "excited": f'<path d="M83 168 Q100 198 117 168 Z" fill="{INK}"/>'
                   f'<ellipse cx="100" cy="183" rx="7" ry="4" fill="#FB7185"/>',
        "celebrating": f'<path d="M82 166 Q100 202 118 166 Z" fill="{INK}"/>'
                       f'<ellipse cx="100" cy="186" rx="8" ry="5" fill="#FB7185"/>',
        "overflowing": f'<path d="M92 175 Q100 181 108 175" stroke="{INK}" stroke-width="3.5" '
                       f'fill="none" stroke-linecap="round"/>',
    }
    return shapes[mood]


def _cheeks(mood):
    """Rosy cheeks appear once Boondi is feeling good."""
    if mood in ("thirsty", "waking"):
        return ""
    return f"""
    <ellipse cx="60" cy="166" rx="9" ry="5" fill="{CHEEK}" opacity="0.8"/>
    <ellipse cx="140" cy="166" rx="9" ry="5" fill="{CHEEK}" opacity="0.8"/>"""


def _arm(mood, path, css_class="", animation=""):
    """
    One arm: a dark outline with a watery colour inside, so it is
    visible on both light and dark backgrounds.
    """
    colour = BODY_COLOURS[mood][1]
    return f"""
    <g class="{css_class}" style="animation: {animation}">
      <path d="{path}" stroke="{INK}" stroke-width="9" stroke-linecap="round" fill="none"/>
      <path d="{path}" stroke="{colour}" stroke-width="4.5" stroke-linecap="round" fill="none"/>
    </g>"""


def _arms(mood):
    """Arms droop when thirsty, wave when happy, both wave when celebrating."""
    if mood == "thirsty":
        return (_arm(mood, "M38 168 Q28 182 26 198") +
                _arm(mood, "M162 168 Q172 182 174 198"))
    if mood in ("waking", "smiling", "overflowing"):
        return (_arm(mood, "M36 160 Q22 168 20 180") +
                _arm(mood, "M164 160 Q178 168 180 180"))
    if mood in ("happy", "excited"):
        speed = "1.2s" if mood == "happy" else "0.7s"
        return (_arm(mood, "M36 160 Q22 168 20 180") +
                _arm(mood, "M164 158 Q180 146 184 126", "wb-arm-r",
                     f"wb-wave {speed} ease-in-out infinite"))
    # celebrating: both arms up and waving
    return (_arm(mood, "M36 158 Q20 146 16 126", "wb-arm-l",
                 "wb-wave 0.6s ease-in-out infinite reverse") +
            _arm(mood, "M164 158 Q180 146 184 126", "wb-arm-r",
                 "wb-wave 0.6s ease-in-out infinite"))


def _extras(mood):
    """Little extras: a sweat drop, sparkles, a party hat, bubbles."""
    if mood == "thirsty":
        return """
        <path d="M156 92 C156 92 146 106 146 112 A10 10 0 0 0 166 112 C166 106 156 92 156 92 Z"
              fill="#BAE6FD" stroke="#0B3B4A" stroke-width="2"/>"""
    if mood == "excited":
        sparkle = ('<path class="wb-spark" style="animation: wb-twinkle {d}s ease-in-out infinite" '
                   'd="M{x} {y1} L{x2} {y} L{x} {y2} L{x0} {y} Z" fill="#FACC15"/>')
        stars = ""
        for x, y, d in [(30, 60, 1.1), (172, 70, 1.4), (182, 200, 0.9)]:
            stars += sparkle.format(x=x, y=y, y1=y - 9, y2=y + 9, x2=x + 4, x0=x - 4, d=d)
        return stars
    if mood == "celebrating":
        hat = """
        <path d="M100 0 L84 34 L116 34 Z" fill="#F472B6" stroke="#0B3B4A" stroke-width="2.5"/>
        <circle cx="100" cy="0" r="5" fill="#FACC15"/>"""
        confetti = ""
        pieces = [(20, "#F472B6", 0.0), (55, "#FACC15", 0.4), (150, "#34D399", 0.2),
                  (180, "#A78BFA", 0.6), (120, "#FB923C", 0.9), (80, "#38BDF8", 1.2)]
        for x, colour, delay in pieces:
            confetti += (f'<rect x="{x}" y="0" width="6" height="10" rx="1" fill="{colour}" '
                         f'style="animation: wb-fall 2.2s linear {delay}s infinite"/>')
        return hat + confetti
    if mood == "overflowing":
        bubbles = ""
        for x, r, delay in [(28, 6, 0), (176, 5, 0.8), (160, 4, 1.6)]:
            bubbles += (f'<circle cx="{x}" cy="120" r="{r}" fill="none" stroke="#38BDF8" '
                        f'stroke-width="2" style="animation: wb-rise-bubble 2.4s ease-in {delay}s infinite"/>')
        return bubbles
    return ""


def mascot_svg(mood):
    """Put all of Boondi's parts together into one SVG picture."""
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -10 210 245" width="210" height="245">
      <style>{ANIMATION_CSS}</style>
      <g class="wb-body" style="animation: {BODY_ANIMATION[mood]}">
        {_arms(mood)}
        {_droplet_body(mood)}
        {_cheeks(mood)}
        {_eyes(mood)}
        {_mouth(mood)}
      </g>
      {_extras(mood)}
    </svg>"""


# ---------------------------------------------------------------------------
# The water bottle
# ---------------------------------------------------------------------------

BOTTLE_BOTTOM_Y = 228   # y position of the inside bottom of the bottle
BOTTLE_FILL_HEIGHT = 168  # how many SVG units tall the fillable part is


def water_level_y(percent):
    """Convert a percentage (0-100+) into the y position of the water."""
    fraction = min(max(percent, 0), 100) / 100
    return BOTTLE_BOTTOM_Y - BOTTLE_FILL_HEIGHT * fraction


def bottle_svg(percent, previous_percent):
    """
    A bottle whose water rises from `previous_percent` to `percent`.
    The keyframe name includes both numbers so the animation replays
    every time the level changes.
    """
    start_y = water_level_y(previous_percent)
    end_y = water_level_y(percent)
    rise_name = f"wb-rise-{int(previous_percent * 10)}-{int(percent * 10)}"
    water_opacity = 0 if percent <= 0 else 1

    # Tick marks for the 25 / 50 / 75 / 100 % milestones.
    ticks = ""
    for mark in (25, 50, 75, 100):
        y = water_level_y(mark)
        ticks += (f'<line x1="112" y1="{y}" x2="124" y2="{y}" stroke="#0E7490" '
                  f'stroke-width="2" opacity="0.6"/>'
                  f'<text x="128" y="{y + 4}" font-size="11" fill="#0E7490" '
                  f'font-family="sans-serif">{mark}%</text>')

    body = ("M44 30 H96 V48 Q96 56 106 64 Q122 76 122 104 V204 Q122 228 98 228 "
            "H42 Q18 228 18 204 V104 Q18 76 34 64 Q44 56 44 48 Z")

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 240" width="160" height="240">
      <style>
        {ANIMATION_CSS}
        @keyframes {rise_name} {{ from {{ transform: translateY({start_y}px); }}
                                 to   {{ transform: translateY({end_y}px); }} }}
      </style>
      <defs>
        <clipPath id="wb-bottle-clip"><path d="{body}"/></clipPath>
        <linearGradient id="wb-water" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{WATER_LIGHT}"/>
          <stop offset="100%" stop-color="{WATER_DEEP}"/>
        </linearGradient>
      </defs>
      <rect x="50" y="8" width="40" height="22" rx="5" fill="#0E7490"/>
      <path d="{body}" fill="rgba(14,165,198,0.07)"/>
      <g clip-path="url(#wb-bottle-clip)" opacity="{water_opacity}">
        <g style="transform: translateY({end_y}px);
                  animation: {rise_name} 1.1s cubic-bezier(.3,1.3,.5,1) both">
          <g style="animation: wb-slide 2.5s linear infinite">
            <path d="M0 0 q17.5 -7 35 0 t35 0 t35 0 t35 0 t35 0 t35 0 t35 0 V260 H0 Z"
                  fill="url(#wb-water)"/>
          </g>
        </g>
      </g>
      <path d="{body}" fill="none" stroke="#0E7490" stroke-width="3.5"/>
      <rect x="30" y="96" width="7" height="90" rx="3.5" fill="white" opacity="0.45"/>
      {ticks}
    </svg>"""


# ---------------------------------------------------------------------------
# Turning SVG text into an image the page can show
# ---------------------------------------------------------------------------

def svg_as_img(svg_text, width_px, description):
    """
    Wrap SVG text in an <img> tag using a base64 "data URI".
    Streamlit's st.html removes raw <svg> tags for safety, but an image
    is allowed, and the animations inside the SVG still play.
    """
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    return (f'<img src="data:image/svg+xml;base64,{encoded}" width="{width_px}" '
            f'alt="{description}" style="max-width:48%; height:auto;">')


# ---------------------------------------------------------------------------
# The "hero" card: Boondi + bottle + speech bubble
# ---------------------------------------------------------------------------

def hero_html(mood, percent, previous_percent, message, mascot_name):
    """Combine mascot, bottle and message into one block of HTML."""
    mascot = svg_as_img(mascot_svg(mood), 180, f"{mascot_name} the water drop looks {mood}")
    bottle = svg_as_img(bottle_svg(percent, previous_percent), 140,
                        f"Water bottle {min(percent, 100):.0f} percent full")
    html = f"""
    <div style="display:flex; flex-direction:column; align-items:center; gap:10px;
                font-family: Nunito, sans-serif;">
      <div style="display:flex; align-items:flex-end; justify-content:center; gap:6px;
                  flex-wrap:nowrap;">
        {mascot}
        {bottle}
      </div>
      <div style="position:relative; max-width:440px; width:100%; box-sizing:border-box;
                  background:rgba(14,165,198,0.12); border:2px solid rgba(14,165,198,0.35);
                  border-radius:18px; padding:12px 16px; font-size:1.05rem;
                  line-height:1.45; text-align:center;">
        <b>{mascot_name}:</b> {message}
      </div>
    </div>"""
    # st.markdown treats indented lines as code and blank lines as the end
    # of the HTML, so squeeze everything onto one line before returning.
    return "".join(line.strip() for line in html.splitlines())
