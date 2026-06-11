import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent
# excel = BASE_DIR.parent / "data" / "Book.xlsx"

excel = r"C:\Users\Samuel\Desktop\Python\Worklife\data\Book.xlsx"

skills = pd.read_excel(excel, sheet_name=0)
promotions = pd.read_excel(excel, sheet_name="Promotions")

skills['End Date'] = pd.to_datetime(skills['End Date'])

mask = skills['End Date'] == pd.Timestamp('2026-06-11')

skills.loc[mask, 'End Date'] = pd.Timestamp.today().normalize()

# skills['End Date'] = np.where(skills['End Date']=='11/06/2026',datetime.today().strftime('%d-%m-%Y'),skills['End Date'])
skills['Start date '] = pd.to_datetime(skills['Start date '])
skills['End Date'] = pd.to_datetime(skills['End Date'])
skills['Time'] = (skills['End Date']-skills['Start date ']).dt.days/365


promotions['End Date'] = pd.to_datetime(skills['End Date'])

mask = promotions['End Date'] == pd.Timestamp('2026-06-11')

promotions.loc[mask, 'End Date'] = pd.Timestamp.today().normalize()

# promotions['Termine'] = np.where(promotions['Termine']=='11/06/2026',datetime.today().strftime('%d-%m-%Y'),promotions['End Date'])
promotions['Empece '] = pd.to_datetime(promotions['Empece '])
promotions['Termine'] = pd.to_datetime(promotions['Termine'])
promotions['Tiempo_puesto'] = (promotions['Termine']-promotions['Empece ']).dt.days/30

promotions.rename(columns = {'Tecnico':'Caracter Tecnico'}, inplace = True)

skills["Time"] = pd.to_numeric(skills["Time"], errors="coerce")
skills = skills.sort_values("Time", ascending=False)

cats = ["Gestion Equipos", "Gestion Proyectos", "Caracter Tecnico"]
cat_values = {
    c: promotions.loc[promotions[c].fillna(0) > 0, "Tiempo_puesto"].sum()
    for c in cats
}


html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skills Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+DW+Pica&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0a0a0f;
    --surface: #12121a;
    --accent: #00e5ff;
    --accent2: #7c3aed;
    --accent3: #f0f;
    --text: #e8eaf0;
    --muted: #555577;
    --bar1: #00e5ff;
    --bar2: #7c3aed;
    --bar3: #f0f;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  @font-face {{
    font-family: 'CambriaMath';
    src: local('Cambria Math'), local('CambriaMath');
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Cambria Math', 'IM Fell DW Pica', 'Georgia', serif;
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }}

  /* ── Slides ── */
  .slide {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 36px 48px 80px;
    opacity: 0;
    pointer-events: none;
    transform: translateX(60px);
    transition: opacity 0.55s cubic-bezier(.4,0,.2,1),
                transform 0.55s cubic-bezier(.4,0,.2,1);
  }}
  .slide.active {{
    opacity: 1;
    pointer-events: all;
    transform: translateX(0);
  }}
  .slide.exit-left {{
    opacity: 0;
    transform: translateX(-60px);
    pointer-events: none;
  }}

  /* ── Title ── */
  h1 {{
    text-align: center;
    font-size: clamp(1.2rem, 2.8vw, 2rem);
    font-weight: 400;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    text-shadow: 0 0 18px rgba(0,229,255,0.35);
    margin-bottom: 24px;
    width: 100%;
  }}

  /* ── Free text slide ── */
  .text-slide-body {{
    max-width: 760px;
    width: 100%;
    margin-top: 16px;
    line-height: 1.85;
    font-size: clamp(0.95rem, 1.8vw, 1.15rem);
    color: var(--text);
    border-left: 2px solid var(--accent);
    padding-left: 28px;
    white-space: pre-wrap;
  }}

  /* ── Chart wrapper (centres Plotly) ── */
  .chart-wrap {{
    width: 100%;
    max-width: 1100px;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .chart {{
    width: 100%;
    height: 68vh;
  }}

  /* ── Nav buttons ── */
  .nav-area {{
    position: fixed;
    bottom: 22px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 16px;
    z-index: 100;
  }}
  .nav-btn {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: transparent;
    border: 1.5px solid var(--accent);
    color: var(--accent);
    font-size: 22px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.25s, box-shadow 0.25s, transform 0.15s;
    box-shadow: 0 0 10px rgba(0,229,255,0.15);
  }}
  .nav-btn:hover {{
    background: rgba(0,229,255,0.12);
    box-shadow: 0 0 22px rgba(0,229,255,0.45);
    transform: scale(1.08);
  }}
  .nav-btn:active {{ transform: scale(0.96); }}
  .nav-btn[disabled], .nav-btn.hidden {{
    visibility: hidden;
    pointer-events: none;
  }}

  /* ── Slide counter ── */
  .slide-counter {{
    position: fixed;
    bottom: 28px;
    right: 30px;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    color: var(--muted);
  }}

  /* ── Scan-line ambient ── */
  body::after {{
    content:'';
    position:fixed;
    inset:0;
    pointer-events:none;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 3px,
      rgba(0,0,0,0.06) 3px,
      rgba(0,0,0,0.06) 4px
    );
    z-index:9999;
  }}
</style>
</head>
<body>

<!-- SLIDE 1: Cumulative time -->
<div id="s1" class="slide active">
  <h1>Cumulative time with skills in years</h1>
  <div class="chart-wrap">
    <div id="chart1" class="chart"></div>
  </div>
</div>

<!-- SLIDE 2: Promotions -->
<div id="s2" class="slide">
  <h1>Promotions Timeline</h1>
  <div class="chart-wrap">
    <div id="chart2" class="chart"></div>
  </div>
</div>

<!-- SLIDE 3: Category -->
<div id="s3" class="slide">
  <h1>Experience by Category</h1>
  <div class="chart-wrap">
    <div id="chart3" class="chart"></div>
  </div>
</div>

<!-- SLIDE 4: Free text -->
<div id="s4" class="slide">
  <h1>Notes &amp; Observations</h1>
  <div class="text-slide-body" id="free-text-body">
Edit this section from Python by changing the freetext_title and freetext_body variables.

You can write multiple paragraphs here. The layout will preserve
line breaks automatically, and the left accent border keeps it
visually tied to the rest of the deck.
  </div>
</div>

<!-- Navigation -->
<div class="nav-area">
  <button class="nav-btn hidden" id="btn-prev" onclick="move(-1)" aria-label="Previous">&#8592;</button>
  <button class="nav-btn" id="btn-next" onclick="move(1)" aria-label="Next">&#8594;</button>
</div>
<div class="slide-counter" id="counter">1 / 4</div>

<script>
// ── State ──────────────────────────────────────────────────
const slides = [...document.querySelectorAll('.slide')];
const total = slides.length;
let current = 0;
let animating = false;

const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');
const counter = document.getElementById('counter');

function updateNav() {{
  btnPrev.classList.toggle('hidden', current === 0);
  btnNext.classList.toggle('hidden', current === total - 1);
  counter.textContent = `${{current + 1}} / ${{total}}`;
}}

function move(step) {{
  if (animating) return;
  const next = current + step;
  if (next < 0 || next >= total) return;
  animating = true;

  slides[current].classList.add('exit-left');
  slides[current].classList.remove('active');

  setTimeout(() => {{
    slides[current].classList.remove('exit-left');
    current = next;
    slides[current].classList.add('active');
    updateNav();
    // Trigger bar animation on chart slides
    if (current < 3) animateChart(current);
    setTimeout(() => {{ animating = false; }}, 560);
  }}, 280);
}}

// Keyboard navigation
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') move(1);
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   move(-1);
}});

// ── Plotly shared config ───────────────────────────────────
const BGCOLOR  = '#0a0a0f';
const GRIDCOLOR = '#1e1e2e';
const FONTCOLOR = '#e8eaf0';
const FONTFAMILY = 'Cambria Math, Georgia, serif';

const baseLayout = {{
  paper_bgcolor: BGCOLOR,
  plot_bgcolor:  BGCOLOR,
  font: {{ color: FONTCOLOR, family: FONTFAMILY, size: 13 }},
  margin: {{ t: 20, b: 90, l: 70, r: 30 }},
  xaxis: {{ gridcolor: GRIDCOLOR, linecolor: GRIDCOLOR, tickfont: {{ family: FONTFAMILY }}, zeroline: false }},
  yaxis: {{ gridcolor: GRIDCOLOR, linecolor: GRIDCOLOR, tickfont: {{ family: FONTFAMILY }}, zeroline: false }},
  showlegend: false,
}};

const baseConfig = {{
  displayModeBar: false,  // removes Plotly toolbar
  responsive: true,
}};

// ── Bar animation helper ───────────────────────────────────
// Animates bars from 0 → final value in ~700 ms
function animateChart(idx) {{
  const ids   = ['chart1', 'chart2', 'chart3'];
  const final = [finalY1, finalY2, finalY3];
  const id    = ids[idx];
  const yFull = final[idx];
  const frames = 30;
  let f = 0;
  const timer = setInterval(() => {{
    f++;
    const t = f / frames;
    const ease = t < 0.5 ? 2*t*t : -1+(4-2*t)*t; // ease-in-out
    const yNow = yFull.map(v => v * ease);
    Plotly.restyle(id, {{ y: [yNow] }});
    if (f >= frames) clearInterval(timer);
  }}, 700 / frames);
}}

// ── Chart data (injected by Python) ───────────────────────
const COLORS_PALETTE = [
  '#00e5ff','#7c3aed','#f0f','#00ff9f','#ff6b35',
  '#ffd600','#4fc3f7','#b388ff','#ff80ab','#69f0ae'
];

// Chart 1 – vertical bars (skills vs time)
const xSkills = {json.dumps(skills["Habilidad"].tolist())};
const ySkills = {json.dumps(skills["Time"].fillna(0).tolist())};
const finalY1 = ySkills;

Plotly.newPlot('chart1', [{{
  type: 'bar',
  x: xSkills,
  y: ySkills.map(() => 0),   // start at 0; animated on load
  text: ySkills.map(v => v > 0 ? v.toFixed(1) : ''),
  textposition: 'outside',
  textfont: {{ color: '#00e5ff', family: FONTFAMILY, size: 12 }},
  cliponaxis: false,
  marker: {{
    color: ySkills.map((_, i) => COLORS_PALETTE[i % COLORS_PALETTE.length]),
    opacity: 0.9,
    line: {{ color: 'rgba(0,229,255,0.3)', width: 1 }}
  }}
}}], {{
  ...baseLayout,
  yaxis: {{ ...baseLayout.yaxis, title: {{ text: 'Years', font: {{ family: FONTFAMILY }} }} }},
}}, baseConfig);

// Chart 2 – waterfall (promotions)
const xPromo = {json.dumps(promotions["Puesto"].astype(str).tolist())};
const yPromo = {json.dumps(promotions["Tiempo_puesto"].fillna(0).tolist())};
const finalY2 = yPromo;

Plotly.newPlot('chart2', [{{
  type: 'waterfall',
  x: xPromo,
  y: yPromo.map(() => 0),
  text: yPromo.map(v => v > 0 ? v.toFixed(1) : ''),
  textposition: 'outside',
  textfont: {{ color: '#e8eaf0', family: FONTFAMILY, size: 12 }},
  cliponaxis: false,
  connector: {{ line: {{ color: '#7c3aed', width: 1.5 }} }},
  increasing: {{ marker: {{ color: '#00e5ff', line: {{ color: '#00e5ff', width: 1 }} }} }},
  decreasing: {{ marker: {{ color: '#f0f',   line: {{ color: '#f0f',   width: 1 }} }} }},
  totals:     {{ marker: {{ color: '#7c3aed',line: {{ color: '#7c3aed',width: 1 }} }} }},
}}], {{
  ...baseLayout,
  yaxis: {{ ...baseLayout.yaxis, title: {{ text: 'Years', font: {{ family: FONTFAMILY }} }} }},
}}, baseConfig);

// Chart 3 – horizontal bars (category)
const yCat = {json.dumps(list(cat_values.keys()))};
const xCat = {json.dumps(list(cat_values.values()))};
const finalY3 = xCat;   // for horizontal bars, values are on X axis

Plotly.newPlot('chart3', [{{
  type: 'bar',
  orientation: 'h',
  y: yCat,
  x: xCat.map(() => 0),
  text: xCat.map(v => v > 0 ? v.toFixed(1) : ''),
  textposition: 'outside',
  textfont: {{ color: '#7c3aed', family: FONTFAMILY, size: 12 }},
  cliponaxis: false,
  marker: {{
    color: yCat.map((_, i) => COLORS_PALETTE[i % COLORS_PALETTE.length]),
    opacity: 0.9,
    line: {{ color: 'rgba(124,58,237,0.3)', width: 1 }}
  }}
}}], {{
  ...baseLayout,
  margin: {{ ...baseLayout.margin, l: 140 }},
  xaxis: {{ ...baseLayout.xaxis, title: {{ text: 'Years', font: {{ family: FONTFAMILY }} }} }},
}}, baseConfig);

// Restyle chart3 to use X values (horizontal)
// Override animateChart for chart3 (horizontal bars animate X, not Y)
const _origAnimate = animateChart;
function animateChart(idx) {{
  if (idx === 2) {{
    const frames = 30;
    let f = 0;
    const timer = setInterval(() => {{
      f++;
      const t = f / frames;
      const ease = t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
      Plotly.restyle('chart3', {{ x: [xCat.map(v => v * ease)] }});
      if (f >= frames) clearInterval(timer);
    }}, 700 / frames);
  }} else {{
    _origAnimate(idx);
  }}
}}

// Animate chart1 on initial load
setTimeout(() => animateChart(0), 400);

updateNav();
</script>
</body>
</html>
"""




with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generado")


# html = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="utf-8">
# <meta name="viewport" content="width=device-width, initial-scale=1">
# <title>Skills Dashboard</title>

# <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

# <style>
# body {{
#     margin:0;
#     background:#000;
#     color:#fff;
#     font-family:Arial, sans-serif;
#     overflow:hidden;
# }}
# .slide {{
#     width:100vw;
#     height:100vh;
#     display:none;
#     padding:30px;
#     box-sizing:border-box;
# }}
# .slide.active {{
#     display:block;
# }}
# h1 {{
#     text-align:center;
# }}
# .chart {{
#     width:100%;
#     height:80vh;
# }}
# .nav {{
#     position:fixed;
#     right:20px;
#     bottom:20px;
#     font-size:40px;
#     cursor:pointer;
#     border:1px solid white;
#     border-radius:50%;
#     width:60px;
#     height:60px;
#     display:flex;
#     align-items:center;
#     justify-content:center;
# }}
# .prev {{
#     left:20px;
#     right:auto;
# }}
# </style>
# </head>
# <body>

# <div id="s1" class="slide active">
# <h1>Cumulative time with skills in years</h1>
# <div id="chart1" class="chart"></div>
# </div>

# <div id="s2" class="slide">
# <h1>Promotions Timeline</h1>
# <div id="chart2" class="chart"></div>
# </div>

# <div id="s3" class="slide">
# <h1>Experience by Category</h1>
# <div id="chart3" class="chart"></div>
# </div>

# <div class="nav prev" onclick="move(-1)">&#8592;</div>
# <div class="nav" onclick="move(1)">&#8594;</div>

# <script>

# const slides = [...document.querySelectorAll('.slide')];
# let current = 0;

# function move(step){{
#   slides[current].classList.remove('active');
#   current = (current + step + slides.length) % slides.length;
#   slides[current].classList.add('active');
# }}

# // Slide 1
# Plotly.newPlot('chart1', [{{
#     type:'bar',
#     x:{json.dumps(skills["Habilidad"].tolist())},
#     y:{json.dumps(skills["Time"].fillna(0).tolist())}
# }}], {{
#     paper_bgcolor:'black',
#     plot_bgcolor:'black',
#     font:{{color:'white'}}
# }});

# // Slide 2 (waterfall)
# Plotly.newPlot('chart2', [{{
#     type:'waterfall',
#     x:{json.dumps(promotions["Puesto"].astype(str).tolist())},
#     y:{json.dumps(promotions["Tiempo_puesto"].fillna(0).tolist())}
# }}], {{
#     paper_bgcolor:'black',
#     plot_bgcolor:'black',
#     font:{{color:'white'}}
# }});

# // Slide 3
# Plotly.newPlot('chart3', [{{
#     type:'bar',
#     orientation:'h',
#     y:{json.dumps(list(cat_values.keys()))},
#     x:{json.dumps(list(cat_values.values()))}
# }}], {{
#     paper_bgcolor:'black',
#     plot_bgcolor:'black',
#     font:{{color:'white'}}
# }});

# </script>
# </body>
# </html>
# """