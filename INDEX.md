# 📚 DOKUMENTATIONS-INDEX

Willkommen beim Discord Log Bot! Diese Seite führt dich zur richtigen Dokumentation.

---

## 🚀 Für Einsteiger

**Neu hier? Starte hier:**

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡
   - Schritt-für-Schritt Installation (15 Min)
   - Keine Vorkenntnisse nötig
   - Perfekt für Anfänger

2. **[README.md](README.md)** 📖
   - Vollständige Projektdokumentation
   - Feature-Übersicht
   - Detaillierte Setup-Anleitung

3. **[FAQ.md](FAQ.md)** ❓
   - Häufige Probleme & Lösungen
   - Troubleshooting Guide
   - Tipps & Tricks

---

## 🔧 Installation & Setup

### Basis Installation
- **[QUICKSTART.md](QUICKSTART.md)** - Schnellstart für Anfänger
- **[README.md](README.md)** - Detaillierte Installation
- `setup.py` - Automatisches Setup-Script

### Tools & Scripts
```bash
python setup.py              # Interaktiver Setup-Assistent
python convert_credentials.py # credentials.json → Base64
python admin_tools.py        # Admin & Statistik Tools
```

---

## ☁️ Deployment

### Cloud Hosting

1. **[RAILWAY_GUIDE.md](RAILWAY_GUIDE.md)** 🚂
   - Railway Deployment (empfohlen)
   - Base64 Credentials Setup
   - ~$7/Monat für 24/7

2. **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** 🐳
   - Docker Container Setup
   - Docker Compose
   - Kubernetes
   - Production-ready

### Hosting-Vergleich

| Platform | Preis | Schwierigkeit | Empfehlung |
|----------|-------|---------------|------------|
| Railway | $7/mo | ⭐ Einfach | ✅ Anfänger |
| Docker Local | Kostenlos | ⭐⭐ Mittel | ✅ Hobbyisten |
| VPS + Docker | $5+/mo | ⭐⭐⭐ Schwer | ✅ Profis |
| Raspberry Pi | Einmalig | ⭐⭐ Mittel | ✅ Tüftler |

---

## 📊 Features & Nutzung

### Kern-Features
- **3 Aktionstypen**: Düngen, Reparieren, Panel platziert
- **Bildverifikation**: Jeder Log mit Beweis
- **Automatische Berechnung**: Individuelle Auszahlungsbeträge
- **Wöchentliche Reports**: Automatisch oder manuell
- **Persönliche Stats**: Jederzeit abrufbar

### Discord Commands

```
/log              - Log einreichen
/wochenbericht    - Wochenbericht anzeigen (Admin)
/setup            - Sheet initialisieren (einmalig, Admin)
/hilfe            - Befehlsübersicht
```

### Admin Tools

```bash
python admin_tools.py
```

**Funktionen:**
- Gesamtstatistiken
- Wöchentliche Statistiken
- User-Statistiken
- CSV Backup erstellen
- Alte Logs löschen

---

## 🛠️ Anpassungen

### Auszahlungsbeträge ändern
**Datei:** `bot.py`, Zeile 24-28
```python
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,
    'Reparieren': 8.00,
    'Panel platziert': 12.00
}
```

### Neue Aktionen hinzufügen
1. In `PAYMENT_AMOUNTS` hinzufügen
2. In `ActionSelect` Class neue Option erstellen
3. Bot neu starten

### Wochenbericht-Intervall
**Datei:** `bot.py`, Zeile 43
```python
@tasks.loop(hours=168)  # 168 = 7 Tage
```

---

## 🔐 Sicherheit & Datenschutz

### Wichtige Dateien (NIEMALS teilen!)
- ❌ `.env` - Enthält Bot Token
- ❌ `credentials.json` - Google API Credentials
- ❌ `credentials_base64.txt` - Base64 Version

### Geschützt durch .gitignore
Die `.gitignore` schützt automatisch:
- Environment Variables
- Credentials
- Logs
- Cache

### Best Practices
1. Token regelmäßig rotieren
2. Service Account mit minimalen Rechten
3. Sheet nicht öffentlich machen
4. Regelmäßige Backups
5. DSGVO beachten (bei EU-Usern)

---

## 📦 Projekt-Struktur

```
discord_log_bot/
│
├── 📄 bot.py                    # Haupt-Bot Code
├── 📄 admin_tools.py            # Admin Tools
├── 📄 setup.py                  # Setup-Assistent
├── 📄 convert_credentials.py    # Base64 Konverter
│
├── 📋 requirements.txt          # Python Dependencies
├── 🔒 .env                      # Konfiguration (nicht in Git!)
├── 🔒 credentials.json          # Google Creds (nicht in Git!)
├── 📝 .env.example             # Beispiel-Konfiguration
│
├── 🚂 Procfile                  # Railway/Heroku
├── 🚂 railway.json              # Railway Config
├── 🐳 Dockerfile                # Docker Container
├── 🐳 docker-compose.yml        # Docker Compose
├── 🐍 runtime.txt               # Python Version
├── 🚫 .gitignore                # Git Ignore Regeln
│
├── 📖 README.md                 # Haupt-Dokumentation
├── ⚡ QUICKSTART.md             # Schnellstart Guide
├── 🚂 RAILWAY_GUIDE.md          # Railway Deployment
├── 🐳 DOCKER_GUIDE.md           # Docker Deployment
├── ❓ FAQ.md                    # Häufige Fragen
└── 📚 INDEX.md                  # Diese Datei
```

---

## 🎓 Lernpfade

### Absolute Anfänger
1. Lies [QUICKSTART.md](QUICKSTART.md)
2. Folge Schritt-für-Schritt
3. Bei Problemen: [FAQ.md](FAQ.md)

### Erfahrene Entwickler
1. Überblick: [README.md](README.md)
2. Deployment: [RAILWAY_GUIDE.md](RAILWAY_GUIDE.md) oder [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
3. Code verstehen: `bot.py` durchlesen

### System-Admins
1. [DOCKER_GUIDE.md](DOCKER_GUIDE.md) für Container
2. Production Best Practices
3. Monitoring & Logging Setup

---

## 🆘 Hilfe & Support

### 1. Dokumentation durchsuchen
- **Installation**: [QUICKSTART.md](QUICKSTART.md)
- **Probleme**: [FAQ.md](FAQ.md)
- **Deployment**: [RAILWAY_GUIDE.md](RAILWAY_GUIDE.md)

### 2. Fehlersuche
```bash
# Bot Logs checken
python bot.py

# Admin Tools für Diagnostics
python admin_tools.py
```

### 3. Community Support
- Discord Entwickler-Communities
- GitHub Issues (falls public)
- Stack Overflow

### 4. Häufigste Probleme
| Problem | Lösung | Link |
|---------|--------|------|
| Bot startet nicht | Token prüfen | [FAQ](FAQ.md#bot-startet-nicht) |
| Sheets Fehler | Service Account teilen | [FAQ](FAQ.md#google-sheets) |
| Commands fehlen | 1h warten oder neu einladen | [FAQ](FAQ.md#slash-commands) |

---

## 🔄 Updates & Wartung

### Code Updates
```bash
# Änderungen pullen
git pull

# Dependencies updaten
pip install -r requirements.txt --upgrade

# Bot neu starten
python bot.py
```

### Backup Strategie
1. **Wöchentlich**: CSV Export via `admin_tools.py`
2. **Monatlich**: Komplettes Backup
3. **Bei Updates**: Vor Code-Änderungen

### Monitoring
- Railway: Dashboard → Metrics
- Docker: `docker stats discord-log-bot`
- Lokal: Terminal Output

---

## 📊 Beispiel-Workflows

### Täglicher Betrieb
1. Bot läuft 24/7
2. User reichen Logs ein
3. Automatische Speicherung
4. Wöchentlicher Report (automatisch)

### Monatliche Auszahlung
1. Admin: `/wochenbericht` × 4 (für alle Wochen)
2. Google Sheet: Summen berechnen
3. Auszahlungen durchführen
4. Alte Logs archivieren (optional)

### Backup & Restore
```bash
# Backup erstellen
python admin_tools.py  # Option 4

# Bei Datenverlust
# → CSV in Google Sheet importieren
```

---

## 🎯 Erweiterte Topics

### Performance-Optimierung
- Caching implementieren
- Database statt Sheets (für >10k Logs)
- Rate Limiting

### Multi-Server Support
- Separate Bot-Instanzen
- Oder: Shared Database

### Custom Features
- Notifications (Discord Webhooks)
- Auto-Auszahlung (PayPal API)
- Dashboard (Web Interface)

---

## 📞 Kontakt

**Bei technischen Fragen:**
1. Erst diese Docs durchsuchen
2. FAQ checken
3. GitHub Issues erstellen

**Bei Feature Requests:**
- GitHub Issues mit "enhancement" Label

**Bei Bugs:**
- GitHub Issues mit:
  - Fehlermeldung
  - Schritte zur Reproduktion
  - Environment (OS, Python Version)

---

## 📜 Lizenz & Credits

**Lizenz:** MIT (oder deine Wahl)

**Verwendete Technologien:**
- discord.py
- Google Sheets API
- Python 3.11+

**Credits:**
- Discord.py Community
- Google Cloud Platform
- Railway.app

---

## 🚀 Schnellstart-Links

**Ich will:**
- ⚡ **Sofort starten** → [QUICKSTART.md](QUICKSTART.md)
- 📖 **Alles verstehen** → [README.md](README.md)
- ☁️ **Online hosten** → [RAILWAY_GUIDE.md](RAILWAY_GUIDE.md)
- 🐳 **Mit Docker** → [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- ❓ **Problem lösen** → [FAQ.md](FAQ.md)

---

**Viel Erfolg mit deinem Bot! 🎉**
