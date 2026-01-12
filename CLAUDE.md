# Kapoptimering

Webapp för optimering av kapning av rör/stänger för att minimera spill.

## Samarbete
- **Hyllteknik** - Industrikunskap
- **AI Empower Labs** - AI och optimeringsalgoritmer

## Tech Stack
- **Backend:** Python Flask
- **Frontend:** Vanilla HTML/CSS/JS
- **Deployment:** Vercel (auto-deploy från GitHub)

## GitHub
- **Repo:** https://github.com/johansalo-create/kapoptimering.git
- **Användare:** johansalo-create
- **Branch:** main

Innan push, kör: `gh auth switch -u johansalo-create`

## Vercel
- **Team:** aiempowerlabs
- **Projekt:** kapoptimering
- **Auto-deploy:** Ja, från GitHub main-branch
- **URL:** https://kapoptimering-aiempowerlabs.vercel.app (eller liknande)

## Lokal utveckling
```bash
cd /Users/johansalo/projects/kapoptimering
source venv/bin/activate
python app.py
```
Appen körs på http://localhost:5050

## Kortkommandon i appen
- **Ctrl+E** - Fyll i exempeldata
- **Enter** - Hoppa till nästa inputfält (skapar ny rad i kaplängder)

## Filer
- `app.py` - Flask-backend med optimeringsalgoritm
- `templates/index.html` - Frontend (allt i en fil)
- `static/` - Loggor och assets
- `vercel.json` - Vercel-konfiguration

## Design
- VD:n vill ha loggorna tydligt synliga
- Tvåradig header: loggor överst (centrerade), appnamn + nav under
- Industriell, professionell känsla för B2B verkstadsindustri
