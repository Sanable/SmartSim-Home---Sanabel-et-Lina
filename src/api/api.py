# src/api/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.maison import MaisonIntelligente
import os

app = FastAPI()

maison = MaisonIntelligente()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route pour le dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    # Chemin vers le fichier HTML
    html_path = os.path.join(os.path.dirname(__file__), '..', 'interface', 'dashboard.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard non trouvé</h1>", status_code=404)

@app.get("/api/etat")
def etat():
    return maison.get_etat_api()

@app.get("/api/historique")
def historique():
    return {"history": maison.historique_actions[-10:]}

@app.post("/api/controle/{device}")
def controle(device: str, payload: dict):
    if device in maison.actionneurs:
        actionneur = maison.actionneurs[device]
        if payload.get("action") == "toggle":
            actionneur.toggle()
    return {"ok": True}

@app.post("/api/mode/{mode}")
def mode(mode: str):
    if mode == "vacation":
        maison.mode_vacances = not maison.mode_vacances
    return {"ok": True}