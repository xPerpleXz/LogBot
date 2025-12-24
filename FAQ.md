# ❓ Häufig gestellte Fragen (FAQ)

## Allgemein

### Ist der Bot kostenlos?
Ja! Der Bot selbst ist kostenlos. Kosten entstehen nur für:
- 24/7 Hosting (Railway: ~$7/Monat, optional)
- Eigener Server (VPS): ab $5/Monat
- Lokales Ausführen: 0€ (nur Strom)

### Brauche ich Programmierkenntnisse?
Nein! Der Quick Start Guide erklärt alles Schritt-für-Schritt.
Für Anpassungen: Python-Grundkenntnisse hilfreich.

### Wie viele Logs kann der Bot speichern?
Unbegrenzt! Google Sheets hat ein Limit von 10 Millionen Zellen.
Bei 8 Spalten = ~1,25 Millionen Logs.

---

## Installation

### "Python ist nicht erkannt" / "Python not found"
**Windows:**
1. Python erneut installieren
2. Häkchen bei "Add Python to PATH" setzen!
3. Computer neu starten

**Mac/Linux:**
```bash
# Python3 verwenden
python3 --version
python3 bot.py
```

### pip install funktioniert nicht
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Oder mit python3
python3 -m pip install --upgrade pip

# Dann erneut versuchen
pip install -r requirements.txt
```

### "Permission denied" beim Installieren
**Mac/Linux:**
```bash
# Mit sudo
sudo pip install -r requirements.txt

# Oder in virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
# PowerShell als Administrator öffnen
# Rechtsklick auf PowerShell → "Als Administrator ausführen"
```

---

## Discord Bot

### Bot erscheint offline
1. Überprüfe: Bot läuft? (`python bot.py`)
2. Check Terminal für Fehler
3. Discord Token korrekt?
4. Internet-Verbindung?

### Slash Commands werden nicht angezeigt
**Lösung 1: Warten**
- Discord sync dauert bis zu 1 Stunde
- Geduld haben!

**Lösung 2: Bot neu einladen**
1. Bot vom Server kicken
2. OAuth2 URL neu generieren
3. Bot erneut einladen
4. Commands sollten sofort da sein

**Lösung 3: Permissions checken**
- Bot braucht "applications.commands" Scope
- Im OAuth2 URL Generator auswählen

### Bot reagiert nicht auf /log
1. Commands sichtbar? (siehe oben)
2. Bot hat Permissions?
3. Check Logs: `python bot.py` Terminal
4. /setup ausgeführt?

### "Interaction failed" Fehler
- Bot offline?
- Webhook timeout (langsame Sheets API)
- Permissions fehlen
- Check Bot Logs

---

## Google Sheets

### "403 Forbidden" Fehler
**Checkliste:**
1. Google Sheets API aktiviert?
2. Service Account Email kopiert?
3. Sheet mit dieser Email geteilt?
4. Als "Editor" (nicht "Viewer") geteilt?

**Service Account Email finden:**
```bash
# In credentials.json:
"client_email": "discord-log-bot@...iam.gserviceaccount.com"
```

### Logs erscheinen nicht im Sheet
1. /setup ausgeführt?
2. Sheet-ID korrekt in .env?
3. credentials.json im richtigen Ordner?
4. Check Terminal für Fehler

### Sheet-ID finden
Aus der URL:
```
https://docs.google.com/spreadsheets/d/1a2B3c4D5E6F7/edit

Sheet-ID = 1a2B3c4D5E6F7
```

### credentials.json ist ungültig
1. Neu herunterladen von Google Cloud
2. Als JSON (nicht P12) downloaden
3. Richtig benannt? (genau: `credentials.json`)
4. Valides JSON? Check mit: https://jsonlint.com/

---

## Features

### Auszahlungsbeträge ändern
**In bot.py, Zeile 24-28:**
```python
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,        # ← Hier ändern
    'Reparieren': 8.00,    # ← Hier ändern
    'Panel platziert': 12.00  # ← Hier ändern
}
```

Speichern → Bot neu starten:
```bash
# Strg+C zum Stoppen
# Dann erneut:
python bot.py
```

### Neue Aktion hinzufügen
1. In `PAYMENT_AMOUNTS` hinzufügen (siehe oben)
2. In `ActionSelect` Class (Zeile ~58) Option hinzufügen:
```python
discord.SelectOption(
    label="Neue Aktion",
    description=f"Auszahlung: {PAYMENT_AMOUNTS['Neue Aktion']}€",
    emoji="🎯"
)
```

### Wochenbericht-Zeitpunkt ändern
**In bot.py, Zeile 43:**
```python
@tasks.loop(hours=168)  # 168 = 7 Tage

# Alternativen:
@tasks.loop(hours=24)   # Täglich
@tasks.loop(hours=72)   # Alle 3 Tage
```

### Statistiken exportieren
```bash
python admin_tools.py
# Option 4: CSV Backup
```

---

## Deployment

### Railway vs. eigener Server?
**Railway:**
- ✅ Einfach
- ✅ Kein Wartung
- ✅ Automatische Updates
- ❌ ~$7/Monat

**Eigener Server:**
- ✅ Einmalige Kosten (oder kostenlos)
- ✅ Volle Kontrolle
- ❌ Wartung nötig
- ❌ Technisches Wissen

**Empfehlung:** Railway für Anfänger, Server für Profis

### Railway: credentials.json hochladen?
**Option 1: Volume** (einfach)
1. Railway Dashboard → Settings → Volumes
2. Mount path: `/app/credentials.json`
3. Inhalt einfügen

**Option 2: Base64** (empfohlen)
1. Konvertieren: `python convert_credentials.py`
2. Als Environment Variable: `GOOGLE_CREDENTIALS_BASE64`
3. Siehe: `RAILWAY_GUIDE.md`

### Docker: Container startet nicht
```bash
# Logs ansehen
docker logs discord-log-bot

# Häufige Fehler:
# - .env fehlt
# - credentials.json nicht gemountet
# - Port-Konflikt

# Fix:
docker-compose down
docker-compose up -d --build
```

---

## Sicherheit

### Token wurde leaked!
**SOFORT:**
1. Discord Developer Portal
2. Dein Bot → Bot
3. "Reset Token"
4. Neuen Token in .env einfügen
5. Bot neu starten

**Prävention:**
- Niemals Token teilen
- Niemals in GitHub pushen
- .gitignore nutzen

### credentials.json wurde leaked!
**SOFORT:**
1. Google Cloud Console
2. Service Account löschen
3. Neuen erstellen
4. Neue credentials.json downloaden

### Sheet ist öffentlich?
1. Check: File → Share
2. "General access" sollte "Restricted" sein
3. Nur Service Account als Editor

---

## Performance

### Bot ist langsam
**Mögliche Ursachen:**
1. Schlechte Internet-Verbindung
2. Google Sheets API throttling
3. Zu viele Logs im Sheet

**Optimierungen:**
```python
# In bot.py, cache erhöhen:
@functools.lru_cache(maxsize=128)
def get_user_stats(user_id):
    ...
```

### Zu viel RAM/CPU
**Reduzieren:**
```python
# Garbage Collection öfter
@tasks.loop(hours=1)
async def cleanup():
    import gc
    gc.collect()
```

**Docker Limits:**
```yaml
deploy:
  resources:
    limits:
      memory: 256M
      cpus: '0.25'
```

---

## Erweiterte Features

### Multi-Server Support?
Aktuell: Ein Bot = Ein Server

**Für Multi-Server:**
1. Separate Bot-Instanz pro Server
2. Oder: Code anpassen (fortgeschritten)

### Datenbank statt Sheets?
Möglich! Erfordert Code-Anpassung.

**Mit SQLite:**
- Siehe: `ADVANCED.md` (coming soon)

**Mit PostgreSQL:**
- Bessere Performance
- Mehr Komplexität

### Notifications bei neuem Log?
**Discord Webhook:**
```python
# In save_log():
webhook = DiscordWebhook(url=WEBHOOK_URL)
embed = DiscordEmbed(...)
webhook.add_embed(embed)
webhook.execute()
```

### Auto-Auszahlung?
Nicht implementiert, aber möglich.

**Konzept:**
1. PayPal API Integration
2. Wöchentliche Auszahlung
3. Siehe: `EXTENSIONS.md` (coming soon)

---

## Backup & Recovery

### Backup erstellen
**Automatisch:**
```bash
python admin_tools.py
# Option 4: CSV Backup
```

**Manuell:**
- Google Sheets: File → Download → CSV

### Logs wiederherstellen
1. CSV in Google Sheets importieren
2. File → Import → Upload
3. "Replace spreadsheet"

### Bot-Dateien sichern
```bash
# Kompletter Ordner
tar -czf backup.tar.gz discord_log_bot/

# Oder mit Git
git init
git add .
git commit -m "Backup"
git remote add origin <github-repo>
git push
```

---

## Rechtliches

### Darf ich den Bot kommerziell nutzen?
Ja! Der Code ist frei verwendbar.

**Aber:**
- Discord ToS einhalten
- Google Terms beachten
- DSGVO/Privacy berücksichtigen

### Datenschutz (DSGVO)
**Was wird gespeichert:**
- Username
- User-ID
- Timestamps
- Beschreibungen
- Bild-URLs

**Empfehlungen:**
1. Datenschutzerklärung bereitstellen
2. User informieren
3. Löschmöglichkeit anbieten
4. Sheet nicht öffentlich machen

### Haftung
Der Bot wird "as-is" bereitgestellt.
Keine Garantie für Fehlerfreiheit.

---

## Community & Support

### Wo kann ich Hilfe bekommen?
1. Diese FAQ
2. README.md
3. Discord Entwickler-Communities
4. GitHub Issues (falls Public Repo)

### Feature Request?
Erstelle ein Issue auf GitHub oder kontaktiere den Entwickler.

### Bug gefunden?
1. Check: Liegt es am Setup?
2. Check: Bekanntes Problem in FAQ?
3. Melde Bug mit:
   - Fehlermeldung
   - Schritte zur Reproduktion
   - Bot Version

---

## Glossar

**Bot Token**: Geheimer Key für Discord API-Zugriff
**Service Account**: Google Cloud Bot-User für API-Zugriff
**Sheet-ID**: Eindeutige Kennung des Google Sheets
**Slash Command**: Discord Befehle mit `/` (z.B. `/log`)
**OAuth2**: Authentifizierungs-Protokoll
**API**: Application Programming Interface
**Environment Variable**: Konfigurationswert in `.env`

---

Frage nicht beantwortet? 
→ Erstelle ein GitHub Issue oder frag in der Discord Community!
