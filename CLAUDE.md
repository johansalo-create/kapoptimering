# Kapoptimering

## Vid uppstart
Läs senaste sessionsloggen i `claude-logs/` för kontext från tidigare arbete.

---

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
- **Preview URL:** https://kapoptimering-aiempowerlabs.vercel.app

## Custom Domain
- **Domän:** kapoptimering.hyllteknik.se
- **Status:** Tillagd i Vercel, väntar på DNS
- **DNS-leverantör:** ilait.se (Hylltekniks webbleverantör)

**DNS-inställning som behövs:**
| Typ | Namn | Värde |
|-----|------|-------|
| A | kapoptimering | 76.76.21.21 |

**Kontakt:** Hylltekniks marknadsavdelning

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
