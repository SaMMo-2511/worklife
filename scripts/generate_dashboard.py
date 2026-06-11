import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
excel = BASE_DIR.parent / "data" / "Book.xlsx"


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
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skills Dashboard | Data Analyst</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --bg: #050508;
    --card-bg: rgba(255, 255, 255, 0.03);
    --accent: #00d1ff;
    --accent-dim: rgba(0, 209, 255, 0.15);
    --accent2: #7c3aed;
    --text: #f0f2f5;
    --muted: #8892b0;
    --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    overflow: hidden;
    height: 100vh;
    width: 100vw;
    background-image: 
        radial-gradient(circle at 20% 30%, rgba(124, 58, 237, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(0, 209, 255, 0.05) 0%, transparent 40%);
  }}

  .slide {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 40px 60px 140px;
    opacity: 0;
    pointer-events: none;
    transform: translateY(20px);
    transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
  }}

  .slide.active {{
    opacity: 1;
    pointer-events: all;
    transform: translateY(0);
  }}

  h1 {{
    text-align: left;
    font-size: clamp(1.2rem, 3vw, 1.6rem);
    font-weight: 300;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 20px;
    width: 100%;
    max-width: 1100px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 10px;
  }}

  .chart-wrap {{
    width: 100%;
    max-width: 1100px;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    margin-bottom: 80px;
  }}

  .chart {{
    width: 100%;
    height: 100%;
  }}

  .measure-badge {{
    position: absolute;
    top: 10px;
    right: 10px;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    color: var(--accent);
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    z-index: 10;
  }}

  .footer-desc {{
    position: absolute;
    bottom: 95px;
    width: calc(100% - 120px);
    max-width: 1100px;
    background: var(--card-bg);
    border-left: 3px solid var(--accent);
    padding: 15px 25px;
    font-size: 0.95rem;
    color: var(--muted);
    line-height: 1.6;
    border-radius: 0 4px 4px 0;
    backdrop-filter: blur(5px);
  }}

  .linkedin-container {{
    width: 100%;
    max-width: 800px;
    background: #fff;
    color: #000;
    border-radius: 8px;
    padding: 25px;
    overflow-y: auto;
    max-height: 50vh;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    margin-top: 20px;
  }}
  .linkedin-container ul {{ list-style: none; }}
  .linkedin-container .t-bold {{ font-weight: 700; color: #000; }}
  .linkedin-container .EntityPhoto-circle-3 {{ border-radius: 50%; object-fit: cover; }}
  .linkedin-container img {{ margin-right: 15px; }}
  .linkedin-container p {{ color: #333; line-height: 1.5; }}

  .text-slide-body {{
    max-width: 800px;
    width: 100%;
    line-height: 1.8;
    font-size: 1.1rem;
    color: var(--text);
    padding: 40px;
    background: var(--card-bg);
    border-radius: 8px;
    margin-top: 20px;
  }}

  .nav-area {{
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 20px;
    z-index: 100;
  }}

  .nav-btn {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.2);
    color: var(--text);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
  }}

  .nav-btn:hover {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
    transform: scale(1.1);
  }}

  .nav-btn.hidden {{ opacity: 0; pointer-events: none; }}

  .slide-counter {{
    position: fixed;
    bottom: 42px;
    right: 40px;
    font-size: 0.8rem;
    color: var(--muted);
    font-family: monospace;
  }}
</style>
</head>
<body>

<div id="s1" class="slide active">
  <h1>Dominio Técnico</h1>
  <div class="chart-wrap">
    <div class="measure-badge">Medida: Tiempo en Años</div>
    <div id="chart1" class="chart"></div>
  </div>
  <div class="footer-desc">Tiempo de trabajo dedicado a cada una de las herramientas y habilidades necesarias para un analista de datos. Solo se muestran el TOP respecto al tiempo dedicado.</div>
</div>

<div id="s2" class="slide">
  <h1>Evolución de Carrera</h1>
  <div class="chart-wrap">
    <div class="measure-badge">Medida: Tiempo en Meses</div> <div id="chart2" class="chart"></div>
  </div>
  <div class="footer-desc">Cronología de promociones y responsabilidades. Durante mi vida laboral las promociones han sido continuas, frecuentes y en tiempos cortos debido a la confianza de mis responsables en mis habilidades.</div>
</div>

<div id="s3" class="slide">
  <h1>Especialización por Proyectos</h1>
  <div class="chart-wrap">
    <div id="chart3" class="chart"></div>
  </div>
  <div class="footer-desc">En mi vida laboral he estado en proyectos que permitian la gestion de personas, proyectos donde gestionaba a cliente y proyectos donde el foco era la habilidad técnica.</div>
</div>

<div id="s-li" class="slide">
  <h1>Recomendaciones de mi Red</h1>
  <div class="chart-wrap">
    <div class="linkedin-container">
        <ul class="mqxZYhUgxJzWocAgTaRZgscFyxcVymDOeKAOU">
            <li class="artdeco-list__item" style="border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 20px;">
                <div style="display:flex; align-items:start;">
                    <img width="48" height="48" src="https://media.licdn.com/dms/image/v2/C4D03AQGXwPrMzj3--g/profile-displayphoto-shrink_100_100/profile-displayphoto-shrink_100_100/0/1639737583749?e=1782950400&amp;v=beta&amp;t=QDyAnqvgFIn_-9cfFkFhhT5c7PVBwOjj9588tz_Ds6Q" class="EntityPhoto-circle-3">
                    <div>
                        <div class="t-bold">Manuel Moreno Martin</div>
                        <div style="font-size:0.85rem; color:#666; margin-bottom: 8px;">Data Scientist at T-Systems Iberia</div>
                        <p style="font-style:italic;">"Espectacular como compañero y persona. Se puede destacar su brillantez y su gran capacidad en la resolución de problemas, adaptándose a los cambios continuos que pudieran surgir, todo ello, junto con los conocimiento de aspectos técnicos, matemáticos y estadísticos, nos sirvió de gran ayuda a la hora de solventar las adversidades con facilidad.<br><br>Simplemente espectacular, un compañero diez."</p>
                    </div>
                </div>
            </li>
            <li class="artdeco-list__item">
                <div style="display:flex; align-items:start;">
                    <img width="48" height="48" src="https://media.licdn.com/dms/image/v2/D4D03AQHBr7WVQWzCDA/profile-displayphoto-shrink_100_100/profile-displayphoto-shrink_100_100/0/1720692941845?e=1782950400&amp;v=beta&amp;t=VVJT1mxFaG8kDpB7FzLKk5qU5saml85G4vOyqjEgVOs" class="EntityPhoto-circle-3">
                    <div>
                        <div class="t-bold">Pablo Rodríguez Díaz</div>
                        <div style="font-size:0.85rem; color:#666; margin-bottom: 8px;">Data Engineer and Chapter Lead at T-Systems Iberia</div>
                        <p style="font-style:italic;">"Samuel es un trabajador excepcional. Aprende y se adapta extraordinariamente rápido, es muy resolutivo, y tiene el don de transmitir su conocimiento de forma brillante. Personalmente, me ha conseguido ayudar incluso con tecnologías que no eran su especialidad. Ojalá pueda volver a trabajar con él en un futuro."</p>
                    </div>
                </div>
            </li>
        </ul>
    </div>
  </div>
  <div class="footer-desc">Feedback directo de colegas y responsables técnicos. A un trabajador lo define el aspecto técnico tanto como el aspecto humano.</div>
</div>

<div id="s4" class="slide">
  <h1>Visión Analítica</h1>
  <div class="chart-wrap">
    <div class="text-slide-body">
    La historia que acabas de ver resume mi camino como analista de datos y de negocio.
    En esencia, mi trabajo consiste en eso: convertir datos en información de valor.
    
    Crear un análisis basado en LinkedIn ha sido un desafío ideal para mostrar en detalle la metodología que precisa un analista de datos: ¿Cómo medir el talento y la experiencia de forma cuantitativa? ¿Qué datos filtrar para no saturar a la audiencia? Y, sobre todo, ¿cómo mantener el factor humano dentro de la analítica?
    
    Cada una de las pestañas anteriores ha sido diseñada pensando en resolver estas dudas desde la perspectiva más importante: la de usted, el cliente final. 
    </div>
  </div>
  <div class="footer-desc">Gracias por llegar hasta el final.</div>
</div>

<div class="nav-area">
  <button class="nav-btn hidden" id="btn-prev" onclick="move(-1)">←</button>
  <button class="nav-btn" id="btn-next" onclick="move(1)">→</button>
</div>
<div class="slide-counter" id="counter">1 / 5</div>

<script>
const slides = [...document.querySelectorAll('.slide')];
const total  = slides.length;
let current  = 0;

const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');
const counter = document.getElementById('counter');

function updateNav() {{
  btnPrev.classList.toggle('hidden', current === 0);
  btnNext.classList.toggle('hidden', current === total - 1);
  counter.textContent = (current + 1) + ' / ' + total;
}}

function move(step) {{
  const next = current + step;
  if (next < 0 || next >= total) return;

  slides[current].classList.remove('active');
  slides[next].classList.add('active');
  current = next;
  updateNav();

  if (current === 0) animateChart1();
  if (current === 1) animateChart2();
  if (current === 2) animateChart3();
}}

document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') move(1);
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')  move(-1);
}});

// Estilos limpios globales (Sin rejillas de fondo)
const BGCOLOR   = 'rgba(0,0,0,0)';
const FONTFAM   = "'Inter', sans-serif";
const ACCENT    = '#00d1ff';

const baseLayout = {{
  paper_bgcolor: BGCOLOR,
  plot_bgcolor:  BGCOLOR,
  font: {{ color: '#8892b0', family: FONTFAM, size: 11 }},
  margin: {{ t: 30, b: 50, l: 40, r: 50 }},
  xaxis: {{ 
    showgrid: false,       // <-- QUITA LAS LÍNEAS VERTICALES POR COMPLETO
    linecolor: 'rgba(255,255,255,0.1)', 
    zeroline: false,
    tickfont: {{ color: '#8892b0', size: 11 }}
  }},
  yaxis: {{ 
    visible: false, 
    showgrid: false,
    zeroline: false
  }},
  showlegend: false,
}};

const cfg = {{ displayModeBar: false, responsive: true }};

// Datos puros de Python
const xSkills = {json.dumps(skills["Habilidad"].tolist())};
const ySkills = {json.dumps(skills["Time"].fillna(0).tolist())};
const xPromo  = {json.dumps(promotions["Puesto"].astype(str).tolist())};
const yPromo  = {json.dumps(promotions["Tiempo_puesto"].fillna(0).tolist())};
const yCat    = {json.dumps(list(cat_values.keys()))};
const xCat    = {json.dumps(list(cat_values.values()))};

// Lógica de cálculo estricta para ejes máximos
const yMaxCalculated1 = Math.max(...ySkills) * 1.30;

// Para el Waterfall (Gráfica 2), el eje correcto debe basarse en la suma total acumulada
const totalWaterfall = yPromo.reduce((a, b) => a + b, 0);
const yMaxCalculated2 = totalWaterfall * 1.25; 

const xMaxCalculated3 = Math.max(...xCat) * 1.30;

// Inicialización de Gráfica 1
Plotly.newPlot('chart1', [{{
  type: 'bar', x: xSkills, y: ySkills.map(() => 0),
  text: ySkills.map(v => v.toFixed(1)),
  textposition: 'outside',
  textfont: {{ color: ACCENT, font: FONTFAM, size: 11 }},
  marker: {{ color: ACCENT, opacity: 0.6, line: {{color: ACCENT, width: 1}} }}
}}], {{
  ...baseLayout,
  yaxis: {{ ...baseLayout.yaxis, range: [0, yMaxCalculated1] }}
}}, cfg);

function animateChart1() {{
  Plotly.animate('chart1', {{ data: [{{ y: ySkills }}], traces: [0] }}, 
    {{ transition: {{ duration: 700, easing: 'cubic-in-out' }}, frame: {{ duration: 700 }} }}
  );
  setTimeout(() => {{
    Plotly.relayout('chart1', {{ 'yaxis.range': [0, yMaxCalculated1] }});
  }}, 720);
}}

// Inicialización de Gráfica 2 (Eje Waterfall Corregido al Valor Acumulado Completo)
Plotly.newPlot('chart2', [{{
  type: 'waterfall', x: xPromo, y: yPromo.map(() => 0),
  connector: {{ line: {{ color: 'rgba(255,255,255,0.1)' }} }},
  increasing: {{ marker: {{ color: ACCENT }} }},
  totals: {{ marker: {{ color: '#7c3aed' }} }}
}}], {{
  ...baseLayout,
  yaxis: {{ ...baseLayout.yaxis, range: [0, yMaxCalculated2] }}
}}, cfg);

function animateChart2() {{
  Plotly.animate('chart2', {{ data: [{{ y: yPromo }}], traces: [0] }}, 
    {{ transition: {{ duration: 700, easing: 'cubic-in-out' }}, frame: {{ duration: 700 }} }}
  );
  setTimeout(() => {{
    Plotly.relayout('chart2', {{ 'yaxis.range': [0, yMaxCalculated2] }});
  }}, 720);
}}

// Inicialización de Gráfica 3 (Completamente limpia de cuadrículas)
Plotly.newPlot('chart3', [{{
  type: 'bar', orientation: 'h', y: yCat, x: xCat.map(() => 0),
  text: xCat.map(v => v.toFixed(1)),
  textposition: 'outside',
  textfont: {{ color: '#fff', size: 11 }},
  marker: {{ color: '#7c3aed', opacity: 0.6 }}
}}], {{ 
  ...baseLayout, 
  margin: {{ l: 160, r: 60, t: 30, b: 50 }}, 
  yaxis: {{ 
    visible: true, 
    showgrid: false, 
    linecolor: 'none', 
    tickfont: {{ color: '#fff', size: 11 }} 
  }},
  xaxis: {{ 
    visible: true, 
    showgrid: false,       // <-- Adiós líneas verticales también en la gráfica 3
    linecolor: 'rgba(255,255,255,0.1)', 
    range: [0, xMaxCalculated3] 
  }}
}}, cfg);

function animateChart3() {{
  Plotly.animate('chart3', {{ data: [{{ x: xCat }}], traces: [0] }}, 
    {{ transition: {{ duration: 700, easing: 'cubic-in-out' }}, frame: {{ duration: 700 }} }}
  );
  setTimeout(() => {{
    Plotly.relayout('chart3', {{ 'xaxis.range': [0, xMaxCalculated3] }});
  }}, 720);
}}

// Carga Inicial
updateNav();
setTimeout(animateChart1, 500);
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
#   :root {{
#     --bg: #0a0a0f;
#     --accent: #00e5ff;
#     --accent2: #7c3aed;
#     --text: #e8eaf0;
#     --muted: #555577;
#   }}
#   * {{ box-sizing: border-box; margin: 0; padding: 0; }}
#   @font-face {{
#     font-family: 'CambriaMath';
#     src: local('Cambria Math'), local('CambriaMath');
#   }}
#   body {{
#     background: var(--bg);
#     color: var(--text);
#     font-family: 'Cambria Math', Georgia, serif;
#     overflow: hidden;
#     height: 100vh;
#     width: 100vw;
#   }}
#   .slide {{
#     position: absolute;
#     inset: 0;
#     display: flex;
#     flex-direction: column;
#     align-items: center;
#     justify-content: flex-start;
#     padding: 36px 48px 80px;
#     opacity: 0;
#     pointer-events: none;
#     transform: translateX(60px);
#     transition: opacity 0.45s ease, transform 0.45s ease;
#   }}
#   .slide.active {{
#     opacity: 1;
#     pointer-events: all;
#     transform: translateX(0);
#   }}
#   .slide.exit-left {{
#     opacity: 0;
#     transform: translateX(-60px);
#     pointer-events: none;
#   }}
#   h1 {{
#     text-align: center;
#     font-size: clamp(1.1rem, 2.5vw, 1.8rem);
#     font-weight: 400;
#     letter-spacing: 0.18em;
#     text-transform: uppercase;
#     color: var(--accent);
#     text-shadow: 0 0 18px rgba(0,229,255,0.35);
#     margin-bottom: 20px;
#     width: 100%;
#   }}
#   .text-slide-body {{
#     max-width: 760px;
#     width: 100%;
#     margin-top: 16px;
#     line-height: 1.85;
#     font-size: clamp(0.95rem, 1.8vw, 1.15rem);
#     color: var(--text);
#     border-left: 2px solid var(--accent);
#     padding-left: 28px;
#     white-space: pre-wrap;
#   }}
#   .chart-wrap {{
#     width: 100%;
#     max-width: 1100px;
#     flex: 1;
#     display: flex;
#     align-items: center;
#     justify-content: center;
#   }}
#   .chart {{
#     width: 100%;
#     height: 68vh;
#   }}
#   .nav-area {{
#     position: fixed;
#     bottom: 22px;
#     left: 50%;
#     transform: translateX(-50%);
#     display: flex;
#     gap: 16px;
#     z-index: 100;
#   }}
#   .nav-btn {{
#     width: 52px;
#     height: 52px;
#     border-radius: 50%;
#     background: transparent;
#     border: 1.5px solid var(--accent);
#     color: var(--accent);
#     font-size: 22px;
#     cursor: pointer;
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     transition: background 0.25s, box-shadow 0.25s, transform 0.15s;
#     box-shadow: 0 0 10px rgba(0,229,255,0.15);
#   }}
#   .nav-btn:hover {{
#     background: rgba(0,229,255,0.12);
#     box-shadow: 0 0 22px rgba(0,229,255,0.45);
#     transform: scale(1.08);
#   }}
#   .nav-btn:active {{ transform: scale(0.96); }}
#   .nav-btn.hidden {{ visibility: hidden; pointer-events: none; }}
#   .slide-counter {{
#     position: fixed;
#     bottom: 28px;
#     right: 30px;
#     font-size: 0.78rem;
#     letter-spacing: 0.12em;
#     color: var(--muted);
#   }}
#   body::after {{
#     content:'';
#     position:fixed;
#     inset:0;
#     pointer-events:none;
#     background: repeating-linear-gradient(
#       0deg, transparent, transparent 3px,
#       rgba(0,0,0,0.06) 3px, rgba(0,0,0,0.06) 4px
#     );
#     z-index:9999;
#   }}
# </style>
# </head>
# <body>

# <div id="s1" class="slide active">
#   <h1>Tiempo acumulado en habilidades</h1>
#   <div class="chart-wrap"><div id="chart1" class="chart"></div></div>
# </div>

# <div id="s2" class="slide">
#   <h1>Promociones</h1>
#   <div class="chart-wrap"><div id="chart2" class="chart"></div></div>
# </div>

# <div id="s3" class="slide">
#   <h1>Experiencia en tipo de proyectos</h1>
#   <div class="chart-wrap"><div id="chart3" class="chart"></div></div>
# </div>

# <div id="s4" class="slide">
#   <h1>Analista de Datos</h1>
#   <div class="text-slide-body">
# La historia que acabas de ver resume mi camino como analista de datos y de negocio.
# En esencia, mi trabajo consiste en eso: convertir datos en información de valor.

# Crear un análisis basado en LinkedIn ha sido un desafío ideal para mostrar en detalle la metodología que precisa un analista de datos: ¿Cómo medir el talento y la experiencia de forma cuantitativa? ¿Qué datos filtrar para no saturar a la audiencia? Y, sobre todo, ¿cómo mantener el factor humano dentro de la analítica?

# Cada una de las pestañas anteriores ha sido diseñada pensando en resolver estas dudas desde la perspectiva más importante: la de usted, el cliente final. </div>
# </div>

# <div class="nav-area">
#   <button class="nav-btn hidden" id="btn-prev" onclick="move(-1)">&#8592;</button>
#   <button class="nav-btn" id="btn-next" onclick="move(1)">&#8594;</button>
# </div>
# <div class="slide-counter" id="counter">1 / 4</div>

# <script>
# const slides = [...document.querySelectorAll('.slide')];
# const total  = slides.length;
# let current  = 0;

# const btnPrev = document.getElementById('btn-prev');
# const btnNext = document.getElementById('btn-next');
# const counter = document.getElementById('counter');

# function updateNav() {{
#   btnPrev.classList.toggle('hidden', current === 0);
#   btnNext.classList.toggle('hidden', current === total - 1);
#   counter.textContent = (current + 1) + ' / ' + total;
# }}

# function move(step) {{
#   const next = current + step;
#   if (next < 0 || next >= total) return;

#   slides[current].classList.add('exit-left');
#   slides[current].classList.remove('active');
#   slides[next].classList.add('active');
#   current = next;
#   updateNav();

#   // Clean up exit-left after transition
#   setTimeout(() => {{
#     slides.forEach(s => s.classList.remove('exit-left'));
#   }}, 500);

#   // Trigger bar fill animation on chart slides
#   if (current === 0) animateChart1();
#   if (current === 1) animateChart2();
#   if (current === 2) animateChart3();
# }}

# document.addEventListener('keydown', e => {{
#   if (e.key === 'ArrowRight' || e.key === 'ArrowDown') move(1);
#   if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   move(-1);
# }});

# // ── Shared Plotly config ──────────────────────────────────
# const BGCOLOR   = '#0a0a0f';
# const GRIDCOLOR = '#1e1e2e';
# const FONTFAM   = 'Cambria Math, Georgia, serif';
# const PALETTE   = ['#00e5ff','#7c3aed','#f0f','#00ff9f','#ff6b35',
#                    '#ffd600','#4fc3f7','#b388ff','#ff80ab','#69f0ae'];

# const baseLayout = {{
#   paper_bgcolor: BGCOLOR,
#   plot_bgcolor:  BGCOLOR,
#   font: {{ color: '#e8eaf0', family: FONTFAM, size: 13 }},
#   margin: {{ t: 20, b: 90, l: 70, r: 40 }},
#   xaxis: {{ gridcolor: GRIDCOLOR, linecolor: GRIDCOLOR, zeroline: false,
#             tickfont: {{ family: FONTFAM }} }},
#   yaxis: {{ gridcolor: GRIDCOLOR, linecolor: GRIDCOLOR, zeroline: false,
#             tickfont: {{ family: FONTFAM }} }},
#   showlegend: false,
# }};
# const cfg = {{ displayModeBar: false, responsive: true }};

# // ── Data from Python ──────────────────────────────────────
# const xSkills = {json.dumps(skills["Habilidad"].tolist())};
# const ySkills = {json.dumps(skills["Time"].fillna(0).tolist())};

# const xPromo  = {json.dumps(promotions["Puesto"].astype(str).tolist())};
# const yPromo  = {json.dumps(promotions["Tiempo_puesto"].fillna(0).tolist())};

# const yCat    = {json.dumps(list(cat_values.keys()))};
# const xCat    = {json.dumps(list(cat_values.values()))};

# // ── Chart 1 – vertical bars ───────────────────────────────
# const yMax1 = Math.max(...ySkills) * 1.15;
# Plotly.newPlot('chart1', [{{
#   type: 'bar', x: xSkills, y: ySkills.map(() => 0),
#   text: ySkills.map(v => v > 0 ? v.toFixed(1) : ''),
#   textposition: 'outside', cliponaxis: false,
#   textfont: {{ color: '#00e5ff', family: FONTFAM, size: 12 }},
#   marker: {{ color: ySkills.map((_, i) => PALETTE[i % PALETTE.length]),
#              opacity: 0.9, line: {{ color: 'rgba(0,229,255,0.3)', width: 1 }} }}
# }}], {{
#   ...baseLayout,
#   yaxis: {{ ...baseLayout.yaxis, range: [0, yMax1],
#             title: {{ text: 'Years', font: {{ family: FONTFAM }} }} }},
# }}, cfg);

# function animateChart1() {{
#   const FRAMES = 30, MS = 600 / FRAMES;
#   let f = 0;
#   const t = setInterval(() => {{
#     f++;
#     const p = f / FRAMES;
#     const e = p < 0.5 ? 2*p*p : -1+(4-2*p)*p;
#     Plotly.restyle('chart1', {{ y: [ySkills.map(v => v * e)] }});
#     if (f >= FRAMES) clearInterval(t);
#   }}, MS);
# }}

# // ── Chart 2 – waterfall ───────────────────────────────────
# // Waterfall doesn't support restyle animation well; use Plotly.animate instead
# const yMax2 = Math.max(...yPromo.map(Math.abs)) * 1.15;
# Plotly.newPlot('chart2', [{{
#   type: 'waterfall', x: xPromo, y: yPromo,
#   text: yPromo.map(v => v !== 0 ? Math.abs(v).toFixed(1) : ''),
#   textposition: 'outside', cliponaxis: false,
#   textfont: {{ color: '#e8eaf0', family: FONTFAM, size: 12 }},
#   connector: {{ line: {{ color: '#7c3aed', width: 1.5 }} }},
#   increasing: {{ marker: {{ color: '#00e5ff', line: {{ color: '#00e5ff', width: 1 }} }} }},
#   decreasing: {{ marker: {{ color: '#f0f',   line: {{ color: '#f0f',   width: 1 }} }} }},
#   totals:     {{ marker: {{ color: '#7c3aed',line: {{ color: '#7c3aed',width: 1 }} }} }},
# }}], {{
#   ...baseLayout,
#   yaxis: {{ ...baseLayout.yaxis,
#             title: {{ text: 'Years', font: {{ family: FONTFAM }} }} }},
# }}, cfg);

# // Waterfall: animate by scaling values from 0
# function animateChart2() {{
#   const FRAMES = 30, MS = 600 / FRAMES;
#   let f = 0;
#   const t = setInterval(() => {{
#     f++;
#     const p = f / FRAMES;
#     const e = p < 0.5 ? 2*p*p : -1+(4-2*p)*p;
#     Plotly.restyle('chart2', {{ y: [yPromo.map(v => v * e)] }});
#     if (f >= FRAMES) clearInterval(t);
#   }}, MS);
# }}

# // ── Chart 3 – horizontal bars ─────────────────────────────
# const xMax3 = Math.max(...xCat) * 1.15;
# Plotly.newPlot('chart3', [{{
#   type: 'bar', orientation: 'h', y: yCat, x: xCat.map(() => 0),
#   text: xCat.map(v => v > 0 ? v.toFixed(1) : ''),
#   textposition: 'outside', cliponaxis: false,
#   textfont: {{ color: '#7c3aed', family: FONTFAM, size: 12 }},
#   marker: {{ color: yCat.map((_, i) => PALETTE[i % PALETTE.length]),
#              opacity: 0.9, line: {{ color: 'rgba(124,58,237,0.3)', width: 1 }} }}
# }}], {{
#   ...baseLayout,
#   margin: {{ ...baseLayout.margin, l: 140 }},
#   xaxis: {{ ...baseLayout.xaxis, range: [0, xMax3],
#             title: {{ text: 'Years', font: {{ family: FONTFAM }} }} }},
# }}, cfg);

# function animateChart3() {{
#   const FRAMES = 30, MS = 600 / FRAMES;
#   let f = 0;
#   const t = setInterval(() => {{
#     f++;
#     const p = f / FRAMES;
#     const e = p < 0.5 ? 2*p*p : -1+(4-2*p)*p;
#     Plotly.restyle('chart3', {{ x: [xCat.map(v => v * e)] }});
#     if (f >= FRAMES) clearInterval(t);
#   }}, MS);
# }}

# // ── Init ──────────────────────────────────────────────────
# updateNav();
# setTimeout(animateChart1, 300);
# </script>
# </body>
# </html>
# """

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