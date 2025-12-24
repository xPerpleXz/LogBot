# 🤖 Discord Log Bot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Maintained](https://img.shields.io/badge/maintained-yes-green.svg)

**Ein professioneller Discord Bot für Log-Management mit Google Sheets Integration**

Automatische Auszahlungsberechnung • Wöchentliche Reports • Bildverifikation

[Features](#-features) •
[Quick Start](QUICKSTART.md) •
[Dokumentation](#-dokumentation) •
[Deployment](#-deployment-optionen) •
[Contributing](CONTRIBUTING.md) •
[Lizenz](#-lizenz)

</div>

---

## 📖 Über dieses Projekt

> **Erstellt von:** [xPerpleXz](https://github.com/xPerpleXz)  
> **Lizenz:** MIT  
> **Version:** 1.0.0  
> **Sprache:** Python 3.11+

Dieser Discord Bot wurde entwickelt, um Mitglieder-Aktivitäten professionell zu tracken, Logs zu verwalten und automatische Auszahlungen zu berechnen - alles mit einer modernen, benutzerfreundlichen Discord UI.

---

## ✨ Features

### Core Funktionen
- 🎯 **3 Aktionstypen**: Düngen, Reparieren, Panel platziert (anpassbar)
- 💰 **Automatische Berechnung**: Individuelle Auszahlungsbeträge pro Aktion
- 📸 **Bildverifikation**: Jeder Log benötigt einen Bildbeweis
- 📊 **Persönliche Statistiken**: Mitglieder können ihre Stats in Echtzeit abfragen
- 📈 **Wöchentliche Berichte**: Automatische Reports mit Top 10 Verdienern
- 🔒 **Sicher**: Alle Daten verschlüsselt in Google Sheets
- ⚡ **Modern**: Button-basierte Interaktion mit Discord UI

### Discord Commands
```
/log              - Log einreichen mit Dropdown & Modal
/wochenbericht    - Wöchentlicher Report (nur Admins)
/setup            - Sheet Initialisierung (einmalig, Admins)
/hilfe            - Befehlsübersicht
```

### Admin Features
- 📊 Gesamtstatistiken (All-Time)
- 📅 Wöchentliche Statistiken
- 👤 User-spezifische Statistiken
- 💾 CSV Backup Export
- 🗑️ Alte Logs löschen
- 🔄 Automatische Reports

### Technische Highlights
- ✅ Base64 Credentials Support (Cloud-ready)
- ✅ Railway/Render/Docker/Oracle Cloud kompatibel
- ✅ Async/Await für Performance
- ✅ Fehlerbehandlung & Logging
- ✅ Type Hints & Docstrings
- ✅ Production-ready Code

---

## 🚀 Quick Start

### Option 1: Schnellstart (15 Minuten)
```bash
# 1. Repository klonen
git clone https://github.com/xPerpleXz/discord-log-bot.git
cd discord-log-bot

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Konfiguration
cp .env.example .env
# .env bearbeiten mit deinen Credentials

# 4. Bot starten
python bot.py
```

**Siehe [QUICKSTART.md](QUICKSTART.md) für detaillierte Anleitung!**

### Option 2: Cloud Deployment
- **Railway:** [RAILWAY_GUIDE.md](RAILWAY_GUIDE.md) - $5/Monat
- **Render:** [RENDER_GUIDE.md](RENDER_GUIDE.md) - Kostenlos
- **Oracle Cloud:** [ORACLE_CLOUD_GUIDE.md](ORACLE_CLOUD_GUIDE.md) - Kostenlos 24/7
- **Docker:** [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Flexibel

---

## 📋 Voraussetzungen

- Python 3.11 oder höher
- Discord Bot Account ([Developer Portal](https://discord.com/developers/applications))
- Google Cloud Account (kostenlos)
- Google Sheets API aktiviert

**Detaillierte Setup-Anleitung:** [README.md - Installation](#installation)

---

## 📚 Dokumentation

### Hauptdokumentation
| Dokument | Beschreibung | Für wen? |
|----------|--------------|----------|
| [START_HIER.md](START_HIER.md) | Projekt-Übersicht | Alle |
| [QUICKSTART.md](QUICKSTART.md) | 15-Min Schnellstart | Anfänger |
| [README.md](README.md) | Vollständige Docs | Alle |
| [INDEX.md](INDEX.md) | Dokumentations-Index | Navigation |
| [FAQ.md](FAQ.md) | 30+ häufige Fragen | Troubleshooting |

### Deployment Guides
| Guide | Platform | Kosten | Schwierigkeit |
|-------|----------|--------|---------------|
| [RAILWAY_GUIDE.md](RAILWAY_GUIDE.md) | Railway | $5/mo | ⭐ Einfach |
| [RENDER_GUIDE.md](RENDER_GUIDE.md) | Render.com | Free | ⭐ Einfach |
| [ORACLE_CLOUD_GUIDE.md](ORACLE_CLOUD_GUIDE.md) | Oracle | Free 24/7 | ⭐⭐⭐ Mittel |
| [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Docker | Variabel | ⭐⭐ Mittel |
| [KOSTENLOSE_HOSTING_OPTIONEN.md](KOSTENLOSE_HOSTING_OPTIONEN.md) | Vergleich | Alle | Info |

### Entwickler Docs
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution Guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community Regeln
- [SECURITY.md](SECURITY.md) - Security Policy
- [CHANGELOG.md](CHANGELOG.md) - Versionshistorie
- [CONTRIBUTORS.md](CONTRIBUTORS.md) - Hall of Fame

---

## 💻 Installation

### 1. Discord Bot erstellen
1. [Discord Developer Portal](https://discord.com/developers/applications)
2. "New Application" → Bot Token kopieren
3. Privileged Gateway Intents aktivieren
4. OAuth2 URL generieren & Bot einladen

### 2. Google Sheets Setup
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Neues Projekt erstellen
3. Google Sheets API aktivieren
4. Service Account erstellen
5. JSON Key downloaden → `credentials.json`

### 3. Bot konfigurieren
```bash
# .env erstellen
cp .env.example .env

# .env bearbeiten:
DISCORD_TOKEN=dein_bot_token
SPREADSHEET_ID=deine_sheet_id
LOG_CHANNEL_IDS=channel1,channel2
REPORT_CHANNEL_ID=report_channel
```

### 4. Dependencies & Start
```bash
pip install -r requirements.txt
python bot.py
```

**✅ Bot ist online!**

**Vollständige Anleitung:** [QUICKSTART.md](QUICKSTART.md)

---

## 🎯 Verwendung

### Für Mitglieder

**Log einreichen:**
```
1. /log im Discord
2. Aktion aus Dropdown wählen
3. Beschreibung eingeben
4. Bild hochladen als Beweis
5. ✅ Fertig! Log wird gespeichert
```

**Statistiken ansehen:**
- Button "Meine Statistiken" im `/log` Modal

### Für Admins

**Setup (einmalig):**
```
/setup
```
Erstellt Sheet-Struktur automatisch.

**Wochenbericht:**
```
/wochenbericht
```
Zeigt Top 10, Statistiken, Gesamtauszahlung.

**Admin Tools (CLI):**
```bash
python admin_tools.py
```
Für Backups, Statistiken, Daten-Management.

---

## 🛠️ Anpassungen

### Auszahlungsbeträge ändern

**In `bot.py`, Zeile 24-28:**
```python
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,        # ← Hier anpassen
    'Reparieren': 8.00,    # ← Hier anpassen
    'Panel platziert': 12.00  # ← Hier anpassen
}
```

Speichern → Bot neu starten → Fertig!

### Neue Aktionen hinzufügen

1. In `PAYMENT_AMOUNTS` hinzufügen
2. In `ActionSelect` Class neue Option erstellen
3. Bot neu starten

**Detaillierte Anleitung:** [README.md - Anpassungen](README.md#anpassungen)

---

## ☁️ Deployment-Optionen

| Platform | Kosten | Uptime | Setup | Empfehlung |
|----------|--------|--------|-------|------------|
| **Oracle Cloud** | 0€ | 24/7 | 30 Min | 🏆 Beste für 24/7 |
| **Render.com** | 0€ | ~750h | 5 Min | ⭐ Einfachste |
| **Railway** | $5/mo | 24/7 | 10 Min | ✅ Production |
| **Docker** | Variabel | 24/7 | 20 Min | 🔧 Flexibel |
| **Raspberry Pi** | ~50€ | 24/7 | 2h | 🏠 Zuhause |

**Vollständiger Vergleich:** [KOSTENLOSE_HOSTING_OPTIONEN.md](KOSTENLOSE_HOSTING_OPTIONEN.md)

---

## 🤝 Contributing

Contributions sind willkommen! 🎉

### Wie kann ich beitragen?

1. **Fork** das Repository
2. **Clone** dein Fork
3. **Branch** erstellen: `git checkout -b feature/deine-feature`
4. **Commit** Änderungen: `git commit -m 'feat: Add feature'`
5. **Push** zu Branch: `git push origin feature/deine-feature`
6. **Pull Request** erstellen

**Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details!**

### Code of Conduct

Wir folgen einem [Code of Conduct](CODE_OF_CONDUCT.md). Bitte lies ihn bevor du beiträgst.

---

## 🐛 Bug Reports & Feature Requests

- **Bug gefunden?** [Issue erstellen](https://github.com/xPerpleXz/discord-log-bot/issues/new?template=bug_report.md)
- **Feature Idee?** [Feature Request](https://github.com/xPerpleXz/discord-log-bot/issues/new?template=feature_request.md)
- **Fragen?** [FAQ.md](FAQ.md) checken oder [Discussion starten](https://github.com/xPerpleXz/discord-log-bot/discussions)

---

## 📊 Projekt-Status

![GitHub issues](https://img.shields.io/github/issues/xPerpleXz/discord-log-bot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/xPerpleXz/discord-log-bot)
![GitHub last commit](https://img.shields.io/github/last-commit/xPerpleXz/discord-log-bot)
![GitHub repo size](https://img.shields.io/github/repo-size/xPerpleXz/discord-log-bot)

- **Version:** 1.0.0 (Stable)
- **Status:** Aktiv entwickelt
- **Letzte Aktualisierung:** Dezember 2024
- **Python Version:** 3.11+
- **Discord.py:** 2.3.2

---

## 🏆 Credits & Danksagungen

### Creator
**[xPerpleXz](https://github.com/xPerpleXz)**
- 💻 Lead Developer
- 📖 Documentation
- 🎨 Project Design

### Built With
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API Wrapper
- [Google Sheets API](https://developers.google.com/sheets/api) - Data Storage
- [Python](https://www.python.org/) - Programming Language

### Hosting Partners
- [Railway.app](https://railway.app/) - Cloud Hosting
- [Oracle Cloud](https://www.oracle.com/cloud/) - Free Tier
- [Render.com](https://render.com/) - Free Hosting

### Special Thanks
- Discord.py Community
- Google Cloud Platform
- Alle Contributors & Beta Tester

**Siehe [CONTRIBUTORS.md](CONTRIBUTORS.md) für vollständige Liste!**

---

## 📜 Lizenz

Dieses Projekt ist unter der **MIT License** lizenziert.

```
MIT License

Copyright (c) 2024 xPerpleXz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

**Siehe [LICENSE](LICENSE) für vollständigen Text.**

### Was bedeutet das?

✅ Kommerzielle Nutzung  
✅ Modifikation  
✅ Distribution  
✅ Private Nutzung  

❗ Keine Garantie  
❗ Keine Haftung  

---

## 🔒 Security

Sicherheit wird ernst genommen!

- **Vulnerability?** Siehe [SECURITY.md](SECURITY.md)
- **Best Practices:** Dokumentiert in Guides
- **Updates:** Regelmäßige Security Patches

---

## 📞 Support & Community

### Hilfe benötigt?

1. **Dokumentation:** [INDEX.md](INDEX.md) - Alle Guides
2. **FAQ:** [FAQ.md](FAQ.md) - 30+ Antworten
3. **Issues:** [GitHub Issues](https://github.com/xPerpleXz/discord-log-bot/issues)
4. **Discussions:** [GitHub Discussions](https://github.com/xPerpleXz/discord-log-bot/discussions)

### Stay Updated

- 🌟 **Star** das Projekt
- 👁️ **Watch** für Updates
- 🍴 **Fork** zum Experimentieren

---

## 📈 Roadmap

### v1.1.0 (Q1 2025)
- [ ] Multi-Channel Support
- [ ] Custom Aktionstypen
- [ ] Excel Export
- [ ] Erweiterte Charts

### v1.2.0 (Q2 2025)
- [ ] Web Dashboard
- [ ] REST API
- [ ] Multi-Language
- [ ] Mobile App

### v2.0.0 (Q3 2025)
- [ ] TypeScript Rewrite
- [ ] PostgreSQL Support
- [ ] Plugin System
- [ ] GraphQL API

**Siehe [CHANGELOG.md](CHANGELOG.md) für Details!**

---

## 📊 Stats

```
📝 Lines of Code:    ~1,500+ Python
📄 Documentation:    ~5,000+ Lines
⏱️ Development Time: 100+ Hours
💰 Value:            Priceless
🌟 Stars:            [Your Stars Here]
🍴 Forks:            [Your Forks Here]
```

---

## 🎉 Danke fürs Lesen!

Made with ❤️ by **[xPerpleXz](https://github.com/xPerpleXz)**

**Gefällt dir das Projekt?**
- ⭐ **Star** auf GitHub
- 🍴 **Fork** und experimentiere
- 🐛 **Contribute** mit PRs
- 📢 **Teile** mit anderen

---

<div align="center">

**[⬆ Back to Top](#-discord-log-bot)**

![Footer](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)
![Footer](https://img.shields.io/badge/Powered%20by-Discord.py-7289DA?style=for-the-badge&logo=discord)

</div>
