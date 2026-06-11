import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
excel = BASE_DIR.parent / "data" / "Book.xlsx"

skills = pd.read_excel(excel, sheet_name=0)

excel = r"data/Book.xlsx"

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

<style>
body {{
    margin:0;
    background:#000;
    color:#fff;
    font-family:Arial, sans-serif;
    overflow:hidden;
}}
.slide {{
    width:100vw;
    height:100vh;
    display:none;
    padding:30px;
    box-sizing:border-box;
}}
.slide.active {{
    display:block;
}}
h1 {{
    text-align:center;
}}
.chart {{
    width:100%;
    height:80vh;
}}
.nav {{
    position:fixed;
    right:20px;
    bottom:20px;
    font-size:40px;
    cursor:pointer;
    border:1px solid white;
    border-radius:50%;
    width:60px;
    height:60px;
    display:flex;
    align-items:center;
    justify-content:center;
}}
.prev {{
    left:20px;
    right:auto;
}}
</style>
</head>
<body>

<div id="s1" class="slide active">
<h1>Cumulative time with skills in years</h1>
<div id="chart1" class="chart"></div>
</div>

<div id="s2" class="slide">
<h1>Promotions Timeline</h1>
<div id="chart2" class="chart"></div>
</div>

<div id="s3" class="slide">
<h1>Experience by Category</h1>
<div id="chart3" class="chart"></div>
</div>

<div class="nav prev" onclick="move(-1)">&#8592;</div>
<div class="nav" onclick="move(1)">&#8594;</div>

<script>

const slides = [...document.querySelectorAll('.slide')];
let current = 0;

function move(step){{
  slides[current].classList.remove('active');
  current = (current + step + slides.length) % slides.length;
  slides[current].classList.add('active');
}}

// Slide 1
Plotly.newPlot('chart1', [{{
    type:'bar',
    x:{json.dumps(skills["Habilidad"].tolist())},
    y:{json.dumps(skills["Time"].fillna(0).tolist())}
}}], {{
    paper_bgcolor:'black',
    plot_bgcolor:'black',
    font:{{color:'white'}}
}});

// Slide 2 (waterfall)
Plotly.newPlot('chart2', [{{
    type:'waterfall',
    x:{json.dumps(promotions["Puesto"].astype(str).tolist())},
    y:{json.dumps(promotions["Tiempo_puesto"].fillna(0).tolist())}
}}], {{
    paper_bgcolor:'black',
    plot_bgcolor:'black',
    font:{{color:'white'}}
}});

// Slide 3
Plotly.newPlot('chart3', [{{
    type:'bar',
    orientation:'h',
    y:{json.dumps(list(cat_values.keys()))},
    x:{json.dumps(list(cat_values.values()))}
}}], {{
    paper_bgcolor:'black',
    plot_bgcolor:'black',
    font:{{color:'white'}}
}});

</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generado")
