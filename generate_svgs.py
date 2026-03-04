import os

colors = {
    "green": "#66BB6A",
    "light_green": "#A5D6A7",
    "bg_green": "#E8F5E9",
    "yellow": "#FFCA28",
    "light_yellow": "#FFE082",
    "dark": "#333333",
    "grey": "#E0E0E0",
    "white": "#FFFFFF"
}

base_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.1"/>
    </filter>
  </defs>
  <circle cx="100" cy="100" r="95" fill="{bg_green}" />
  {content}
</svg>"""

pipette = """
  <!-- Pipette -->
  <path d="M100 20 L115 20 L110 50 L105 80 L95 80 L90 50 Z" fill="{grey}" stroke="{dark}" stroke-width="2"/>
  <rect x="95" y="10" width="10" height="10" fill="{dark}"/>
"""

tube = """
  <!-- Eppendorf Tube -->
  <path d="M80 120 L85 170 Q100 180 115 170 L120 120 Z" fill="{white}" stroke="{dark}" stroke-width="3" filter="url(#shadow)"/>
  <rect x="75" y="110" width="50" height="10" fill="{grey}" stroke="{dark}" stroke-width="2"/>
"""

svgs = {}

# Step 1: Milk (pipette + drop + tube)
svgs["step1_milk.svg"] = base_svg.format(**colors, content=tube.format(**colors) + pipette.format(**colors) + """
  <path d="M100 90 Q105 105 100 110 Q95 105 100 90 Z" fill="{white}" stroke="{dark}" stroke-width="1.5"/>
  <text x="100" y="160" font-family="sans-serif" font-size="14" font-weight="bold" fill="{dark}" text-anchor="middle">Lait</text>
""".format(**colors))

# Step 2: Nano (pipette + yellow drop + tube with some liquid)
svgs["step2_nano.svg"] = base_svg.format(**colors, content=tube.format(**colors) + """
  <path d="M82 150 L118 150 L115 170 Q100 180 85 170 Z" fill="{white}" opacity="0.8"/>
""" + pipette.format(**colors) + """
  <path d="M100 90 Q105 105 100 110 Q95 105 100 90 Z" fill="{yellow}" stroke="{dark}" stroke-width="1.5"/>
  <text x="100" y="160" font-family="sans-serif" font-size="14" font-weight="bold" fill="{dark}" text-anchor="middle">Nano</text>
""".format(**colors))

# Step 3: Buffer & Mix (closed tube, motion lines, "8x")
svgs["step3_buffer.svg"] = base_svg.format(**colors, content=tube.format(**colors) + """
  <path d="M82 140 L118 140 L115 170 Q100 180 85 170 Z" fill="{light_green}" opacity="0.6"/>
  <rect x="75" y="100" width="50" height="10" fill="{green}" stroke="{dark}" stroke-width="2"/>
  <!-- Motion Lines -->
  <path d="M60 130 Q50 140 60 150 M140 130 Q150 140 140 150" fill="none" stroke="{dark}" stroke-width="3" stroke-linecap="round"/>
  <!-- Buffer drops text -->
  <text x="100" y="60" font-family="sans-serif" font-size="28" font-weight="bold" fill="{green}" text-anchor="middle">+ 8 gouttes</text>
  <text x="100" y="80" font-family="sans-serif" font-size="14" font-weight="bold" fill="{dark}" text-anchor="middle">Tampon</text>
""".format(**colors))

# Step 4: Migration (tube + strip + clock)
svgs["step4_strip.svg"] = base_svg.format(**colors, content=tube.format(**colors) + """
  <path d="M82 140 L118 140 L115 170 Q100 180 85 170 Z" fill="{light_green}" opacity="0.6"/>
  <!-- LFA Strip -->
  <rect x="90" y="60" width="20" height="90" fill="{white}" stroke="{dark}" stroke-width="2"/>
  <rect x="95" y="110" width="10" height="5" fill="{green}" opacity="0.3"/>
  <!-- Clock -->
  <circle cx="150" cy="70" r="25" fill="{white}" stroke="{dark}" stroke-width="3"/>
  <path d="M150 70 L150 55 M150 70 L160 70" fill="none" stroke="{green}" stroke-width="3" stroke-linecap="round"/>
  <text x="150" y="115" font-family="sans-serif" font-size="14" font-weight="bold" fill="{dark}" text-anchor="middle">15 min</text>
""".format(**colors))

# Step 5: Capture (box + strip + phone outline)
svgs["step5_photo.svg"] = base_svg.format(**colors, content="""
  <!-- Box -->
  <rect x="50" y="110" width="100" height="40" fill="{grey}" stroke="{dark}" stroke-width="3" rx="5"/>
  <rect x="60" y="120" width="80" height="20" fill="{white}" stroke="{dark}" stroke-width="2"/>
  <!-- Phone outline above -->
  <rect x="70" y="30" width="60" height="100" fill="none" stroke="{dark}" stroke-width="4" rx="8"/>
  <circle cx="100" cy="80" r="10" fill="none" stroke="{green}" stroke-width="3"/>
  <path d="M90 80 L110 80 M100 70 L100 90" stroke="{green}" stroke-width="2"/>
  <circle cx="100" cy="120" r="4" fill="{dark}"/>
""".format(**colors))

# Step 6: Interpretation (two strips, pos/neg)
svgs["step6_result.svg"] = base_svg.format(**colors, content="""
  <!-- Strip 1: Negatif (Intense) -->
  <rect x="60" y="40" width="25" height="100" fill="{white}" stroke="{dark}" stroke-width="3" rx="4"/>
  <rect x="64" y="90" width="17" height="8" fill="{dark}"/>
  <text x="72.5" y="165" font-family="sans-serif" font-size="16" font-weight="bold" fill="{dark}" text-anchor="middle">Négatif</text>
  <text x="72.5" y="180" font-family="sans-serif" font-size="12" fill="{green}" text-anchor="middle">Intense</text>
  
  <!-- Strip 2: Positif (Claire) -->
  <rect x="115" y="40" width="25" height="100" fill="{white}" stroke="{dark}" stroke-width="3" rx="4"/>
  <rect x="119" y="90" width="17" height="8" fill="{dark}" opacity="0.15"/>
  <text x="127.5" y="165" font-family="sans-serif" font-size="16" font-weight="bold" fill="{dark}" text-anchor="middle">Positif</text>
  <text x="127.5" y="180" font-family="sans-serif" font-size="12" fill="{yellow}" text-anchor="middle">Clair</text>
""".format(**colors))

os.makedirs("c:/Users/natha/OneDrive/Bureau/chimie/static", exist_ok=True)
for name, svg in svgs.items():
    with open(f"c:/Users/natha/OneDrive/Bureau/chimie/static/{name}", "w", encoding="utf-8") as f:
        f.write(svg)

print("SVGs generated successfully.")
