# 🤖 Discord Log-Bot mit Google Sheets Integration

Ein professioneller Discord Bot, der Mitglieder-Logs erfasst, in Google Sheets speichert und automatische Auszahlungen berechnet.

## ✨ Features

- 🎯 **3 Aktionstypen**: Düngen, Reparieren, Panel platziert
- 💰 **Automatische Berechnung**: Unterschiedliche Auszahlungsbeträge pro Aktion
- 📸 **Bildverifikation**: Jeder Log benötigt einen Bildbeweis
- 📊 **Persönliche Statistiken**: Mitglieder können ihre Stats abfragen
- 📈 **Wöchentliche Berichte**: Automatische Reports mit Top-Verdienern
- 🔒 **Sicher**: Alle Daten in Google Sheets gespeichert
- ⚡ **Modern**: Button-basierte Interaktion (Discord UI)

## 📋 Voraussetzungen

- Python 3.11 oder höher
- Discord Bot Account
- Google Cloud Account (kostenlos)
- Google Sheets

## 🚀 Installation

### Schritt 1: Repository klonen

```bash
git clone <dein-repo>
cd discord_log_bot
```

### Schritt 2: Virtuelle Umgebung erstellen (empfohlen)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Schritt 3: Dependencies installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Discord Bot erstellen

1. Gehe zu https://discord.com/developers/applications
2. Klicke "New Application"
3. Gib deinem Bot einen Namen
4. Gehe zu "Bot" → "Add Bot"
5. **Wichtig**: Aktiviere unter "Privileged Gateway Intents":
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Kopiere den Bot Token (klicke "Reset Token" falls nötig)
7. Gehe zu "OAuth2" → "URL Generator"
8. Wähle:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: 
     - `Send Messages`
     - `Embed Links`
     - `Attach Files`
     - `Read Message History`
     - `Use Slash Commands`
9. Kopiere die generierte URL und lade den Bot auf deinen Server ein

### Schritt 5: Google Sheets API einrichten

1. Gehe zu https://console.cloud.google.com/
2. Erstelle ein neues Projekt oder wähle ein bestehendes
3. Aktiviere die **Google Sheets API**:
   - Gehe zu "APIs & Services" → "Enable APIs and Services"
   - Suche nach "Google Sheets API"
   - Klicke "Enable"

4. **Service Account erstellen**:
   - Gehe zu "APIs & Services" → "Credentials"
   - Klicke "Create Credentials" → "Service Account"
   - Name: `discord-log-bot`
   - Rolle: `Editor`
   - Klicke "Done"

5. **JSON Key erstellen**:
   - Klicke auf den erstellten Service Account
   - Gehe zu "Keys" → "Add Key" → "Create new key"
   - Wähle "JSON"
   - Die Datei wird heruntergeladen
   - **Benenne die Datei um zu `credentials.json`**
   - **Verschiebe sie in den `discord_log_bot` Ordner**

6. **Google Sheet erstellen**:
   - Gehe zu https://docs.google.com/spreadsheets/
   - Erstelle ein neues Sheet
   - Benenne es z.B. "Discord Logs"
   - Kopiere die ID aus der URL:
     ```
     https://docs.google.com/spreadsheets/d/DEINE_SHEET_ID_HIER/edit
     ```
   - **Wichtig**: Teile das Sheet mit der Service Account Email!
     - Die Email findest du in der `credentials.json` unter `client_email`
     - Format: `discord-log-bot@projekt-name.iam.gserviceaccount.com`
     - Gehe zum Sheet → Teilen → Füge die Email hinzu mit "Editor" Rechten

### Schritt 6: Konfiguration

1. Kopiere `.env.example` zu `.env`:
```bash
cp .env.example .env
```

2. Öffne `.env` und füge deine Daten ein:

```env
DISCORD_TOKEN=dein_bot_token_von_discord
SPREADSHEET_ID=deine_google_sheets_id
LOG_CHANNEL_ID=channel_id_für_öffentliche_logs
REPORT_CHANNEL_ID=channel_id_für_wöchentliche_reports
```

**Channel IDs finden:**
- Discord Developer Mode aktivieren: Einstellungen → App-Einstellungen → Erweitert → Entwicklermodus
- Rechtsklick auf einen Channel → "ID kopieren"

### Schritt 7: Bot starten

```bash
python bot.py
```

**Wenn alles funktioniert, siehst du:**
```
✅ Google Sheets verbunden
Bot bereit: DeinBotName#1234
```

### Schritt 8: Sheet einrichten

Im Discord, führe den Befehl aus:
```
/setup
```
Dies erstellt die Spalten im Google Sheet automatisch.

## 🎮 Verwendung

### Für Mitglieder:

1. **Log einreichen**: `/log`
   - Wähle eine Aktion aus dem Dropdown
   - Fülle die Beschreibung aus
   - Lade ein Bild als Beweis hoch

2. **Statistiken anzeigen**: Klicke auf "Meine Statistiken" Button
   - Zeigt deine wöchentlichen Aktivitäten
   - Zeigt deinen Gesamtverdienst

### Für Admins:

1. **Manueller Wochenbericht**: `/wochenbericht`
   - Zeigt Top 10 Verdiener
   - Aktionsstatistiken
   - Gesamtauszahlung

2. **Sheet Setup**: `/setup`
   - Nur einmal beim ersten Start ausführen

## 💰 Auszahlungsbeträge anpassen

Öffne `bot.py` und ändere die Beträge in Zeile 24-28:

```python
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,        # ← Hier anpassen
    'Reparieren': 8.00,    # ← Hier anpassen
    'Panel platziert': 12.00  # ← Hier anpassen
}
```

Speichern und Bot neu starten.

## 📊 Google Sheets Aufbau

Das Sheet enthält folgende Spalten:

| Zeitstempel | KW | Username | User-ID | Aktion | Beschreibung | Betrag | Bild-URL |
|-------------|-------|----------|---------|--------|--------------|--------|----------|
| 23.12.2024 14:30 | KW51/2024 | User123 | 123456789 | Düngen | ... | 5.00 | https://... |

Du kannst daraus Pivot-Tabellen, Charts etc. erstellen!

## 🚂 Railway Deployment

### Voraussetzungen:
- Railway Account (https://railway.app/)
- GitHub Repository

### Setup:

1. **Erstelle `Procfile`** (schon vorhanden):
```
worker: python bot.py
```

2. **Erstelle `railway.json`** (schon vorhanden)

3. **Push zu GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <dein-github-repo>
git push -u origin main
```

4. **Railway Projekt erstellen**:
   - Gehe zu https://railway.app/
   - "New Project" → "Deploy from GitHub repo"
   - Wähle dein Repository
   - Railway erkennt automatisch Python

5. **Environment Variables setzen**:
   - Im Railway Dashboard → Variables
   - Füge hinzu:
     ```
     DISCORD_TOKEN=...
     SPREADSHEET_ID=...
     LOG_CHANNEL_ID=...
     REPORT_CHANNEL_ID=...
     ```

6. **credentials.json hochladen**:
   - Railway Dashboard → Settings → Volumes
   - Oder: Konvertiere `credentials.json` zu einer Umgebungsvariable:
   
   ```bash
   # credentials.json Inhalt als Base64
   cat credentials.json | base64
   ```
   
   Füge in Railway hinzu:
   ```
   GOOGLE_CREDENTIALS_BASE64=<base64_string>
   ```
   
   Dann in `bot.py` anpassen:
   ```python
   import base64
   import json
   
   # In init_google_sheets():
   if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
       creds_json = base64.b64decode(os.getenv('GOOGLE_CREDENTIALS_BASE64'))
       creds_dict = json.loads(creds_json)
       creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
   else:
       creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
   ```

7. **Deploy!**
   - Railway deployed automatisch
   - Check die Logs: Railway Dashboard → Deployments → View Logs

## 🔧 Troubleshooting

### Bot startet nicht:
```
❌ DISCORD_TOKEN fehlt in der .env Datei!
```
**Lösung**: Überprüfe, ob `.env` existiert und den Token enthält.

### Google Sheets Fehler:
```
❌ Google Sheets Fehler: 403 Forbidden
```
**Lösung**: 
- Sheet mit Service Account Email geteilt?
- Google Sheets API aktiviert?
- `credentials.json` im richtigen Ordner?

### Slash Commands werden nicht angezeigt:
**Lösung**: 
- Warte 1 Stunde (Discord sync)
- Oder kicke und lade den Bot neu ein
- Stelle sicher, dass `applications.commands` Scope aktiv ist

### Bilder werden nicht gespeichert:
**Lösung**: Überprüfe Discord Permissions:
- Bot braucht "Attach Files" Permission
- Bot muss Nachrichten im Channel lesen können

## 📁 Projekt-Struktur

```
discord_log_bot/
│
├── bot.py                 # Hauptbot-Code
├── requirements.txt       # Python Dependencies
├── .env                   # Konfiguration (nicht in Git!)
├── .env.example          # Beispiel-Konfiguration
├── credentials.json      # Google Service Account (nicht in Git!)
├── Procfile              # Railway/Heroku Deployment
├── railway.json          # Railway Konfiguration
├── .gitignore           # Git Ignore Regeln
└── README.md            # Diese Datei
```

## 🔐 Sicherheit

**WICHTIG - NIEMALS committen:**
- ❌ `.env` Datei
- ❌ `credentials.json`
- ❌ Bot Tokens

Die `.gitignore` schützt diese Dateien automatisch.

## 🆘 Support

Bei Problemen:
1. Überprüfe die Logs im Terminal
2. Stelle sicher, alle Schritte befolgt zu haben
3. Überprüfe Discord & Google Permissions

## 📝 Lizenz

Dieses Projekt ist für private Zwecke frei nutzbar.

## 🎯 Anpassungen

### Mehr Aktionen hinzufügen:

In `bot.py`, Zeile 24:
```python
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,
    'Reparieren': 8.00,
    'Panel platziert': 12.00,
    'Neue Aktion': 15.00,  # ← Hinzufügen
}
```

Dann in `ActionSelect` (Zeile 58) die Options erweitern.

### Wochenbericht-Intervall ändern:

Zeile 43 in `bot.py`:
```python
@tasks.loop(hours=168)  # 168 = 7 Tage, 24 = täglich
```

---

**Viel Erfolg! 🚀**
