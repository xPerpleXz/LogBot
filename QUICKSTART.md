# ⚡ QUICK START GUIDE

**Zeitbedarf: ~15 Minuten**

Dieser Guide führt dich Schritt-für-Schritt zur Installation. Keine Vorkenntnisse nötig!

---

## 📦 Schritt 1: Downloads (5 Min)

### Python installieren
1. Gehe zu: https://www.python.org/downloads/
2. Lade Python 3.11+ herunter
3. ⚠️ **WICHTIG**: Häkchen bei "Add Python to PATH" setzen!
4. Installation durchführen

**Test:**
```bash
python --version
# Sollte zeigen: Python 3.11.x oder höher
```

### Git installieren (optional)
1. Gehe zu: https://git-scm.com/downloads
2. Installiere mit Standard-Einstellungen

---

## 🤖 Schritt 2: Discord Bot erstellen (3 Min)

1. **Developer Portal öffnen**
   - Gehe zu: https://discord.com/developers/applications
   - Login mit deinem Discord Account

2. **Application erstellen**
   - Klicke "New Application"
   - Name: "Log Bot" (oder beliebig)
   - Klicke "Create"

3. **Bot hinzufügen**
   - Links: "Bot"
   - Klicke "Add Bot" → "Yes, do it!"
   
4. **Bot konfigurieren**
   - Scrolle zu "Privileged Gateway Intents"
   - ✅ Aktiviere: "Presence Intent"
   - ✅ Aktiviere: "Server Members Intent"
   - ✅ Aktiviere: "Message Content Intent"
   - Klicke "Save Changes"

5. **Token kopieren**
   - Klicke "Reset Token"
   - Kopiere den Token (speichere ihn sicher!)
   - ⚠️ **WICHTIG**: Token NIEMALS teilen!

6. **Bot einladen**
   - Links: "OAuth2" → "URL Generator"
   - Scopes: ✅ `bot` ✅ `applications.commands`
   - Bot Permissions: ✅ "Administrator" (einfachste Option)
   - Kopiere die URL unten
   - Öffne URL im Browser
   - Wähle deinen Server
   - Klicke "Authorize"

---

## ☁️ Schritt 3: Google Sheets Setup (5 Min)

### Google Cloud Projekt

1. **Console öffnen**
   - Gehe zu: https://console.cloud.google.com/

2. **Neues Projekt**
   - Oben: "Select a project" → "New Project"
   - Name: "Discord Bot"
   - Klicke "Create"

3. **API aktivieren**
   - Suche oben: "Google Sheets API"
   - Klicke darauf → "Enable"

4. **Service Account**
   - Links: "APIs & Services" → "Credentials"
   - "Create Credentials" → "Service Account"
   - Name: `discord-log-bot`
   - Klicke "Create and Continue"
   - Role: "Editor"
   - Klicke "Done"

5. **Key erstellen**
   - Klicke auf den erstellten Service Account
   - Oben: "Keys" → "Add Key" → "Create new key"
   - Type: "JSON"
   - Klicke "Create"
   - **Datei wird heruntergeladen!**

### Google Sheet erstellen

1. **Sheet erstellen**
   - Gehe zu: https://docs.google.com/spreadsheets/
   - "Blank" → Neues Sheet
   - Name: "Discord Logs"

2. **Sheet teilen**
   - ⚠️ **SEHR WICHTIG!**
   - Öffne die heruntergeladene JSON-Datei
   - Suche nach `"client_email"`
   - Kopiere die Email (endet mit `@...iam.gserviceaccount.com`)
   - Im Sheet: Klicke "Share" (oben rechts)
   - Füge die Email ein
   - Role: "Editor"
   - Klicke "Send"

3. **Sheet-ID kopieren**
   - Aus der URL:
   ```
   https://docs.google.com/spreadsheets/d/DEINE_SHEET_ID_HIER/edit
   ```
   - Kopiere nur den Teil zwischen `/d/` und `/edit`

---

## 💾 Schritt 4: Bot installieren (2 Min)

### Dateien vorbereiten

1. **Bot-Dateien entpacken**
   ```bash
   # In einen Ordner entpacken, z.B.:
   C:\Discord_Bot\
   # oder
   ~/discord_bot/
   ```

2. **Terminal öffnen**
   - Windows: Win+R → `cmd` → Enter
   - Mac: Command+Space → "Terminal"
   - Linux: Ctrl+Alt+T

3. **In Ordner navigieren**
   ```bash
   cd C:\Discord_Bot\
   # oder
   cd ~/discord_bot/
   ```

4. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Wenn Fehler auftreten:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Konfiguration

1. **JSON-Datei umbenennen**
   - Die heruntergeladene Google JSON-Datei
   - Umbenennen zu: `credentials.json`
   - Verschieben in den Bot-Ordner

2. **.env Datei erstellen**
   ```bash
   # Windows (PowerShell)
   copy .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```

3. **.env bearbeiten**
   - Öffne `.env` mit Notepad oder einem Editor
   - Füge ein:
   ```
   DISCORD_TOKEN=dein_bot_token_hier
   SPREADSHEET_ID=deine_sheet_id_hier
   LOG_CHANNEL_ID=
   REPORT_CHANNEL_ID=
   ```

4. **Channel IDs finden (optional)**
   - Discord: Einstellungen → App-Einstellungen → Erweitert
   - ✅ "Entwicklermodus" aktivieren
   - Rechtsklick auf Channel → "ID kopieren"
   - In `.env` einfügen

---

## 🚀 Schritt 5: Bot starten!

```bash
python bot.py
```

**Wenn alles klappt, siehst du:**
```
✅ Google Sheets verbunden
Bot bereit: DeinBotName#1234
```

**Bei Fehlern:**
- Überprüfe `.env` Datei
- Überprüfe `credentials.json`
- Stelle sicher, Sheet geteilt ist

---

## 🎯 Schritt 6: Erste Schritte

### Im Discord:

1. **Setup ausführen**
   ```
   /setup
   ```
   - Erstellt die Struktur im Google Sheet

2. **Log einreichen**
   ```
   /log
   ```
   - Wähle eine Aktion
   - Fülle Details aus
   - Lade Bild hoch

3. **Statistiken checken**
   - Klicke "Meine Statistiken" Button

4. **Wochenbericht (Admins)**
   ```
   /wochenbericht
   ```

---

## 🔧 Troubleshooting

### "No module named 'discord'"
```bash
pip install discord.py
```

### "DISCORD_TOKEN fehlt"
- Überprüfe `.env` Datei
- Stelle sicher, Token ohne Leerzeichen eingefügt ist

### "Google Sheets Fehler: 403"
- Sheet mit Service Account Email geteilt?
- Email richtig kopiert? (aus credentials.json)
- Google Sheets API aktiviert?

### Bot reagiert nicht auf /commands
- Warte 1 Stunde (Discord sync)
- Oder: Bot vom Server kicken und neu einladen

### "credentials.json not found"
- Datei im richtigen Ordner?
- Richtig benannt? (genau `credentials.json`)

---

## 📱 Optional: 24/7 Hosting

### Railway (Empfohlen)
1. Siehe: `RAILWAY_GUIDE.md`
2. ~$7/Monat für 24/7

### Eigener Server
1. Raspberry Pi
2. VPS (Hetzner, DigitalOcean)
3. Siehe: `DOCKER_GUIDE.md`

---

## 🎓 Nächste Schritte

1. **Auszahlungsbeträge anpassen**
   - Öffne `bot.py`
   - Zeile 24-28 ändern
   - Bot neu starten

2. **Mehr Features**
   - Admin Tools: `python admin_tools.py`
   - CSV Backups erstellen
   - Custom Statistics

3. **Anpassen**
   - Neue Aktionen hinzufügen
   - Farben ändern
   - Emojis anpassen

---

## 📞 Hilfe

**Bei Problemen:**
1. Lies die README.md
2. Check die Error Message
3. Google die Fehlermeldung
4. Frag in Discord Entwickler-Communities

---

## ✅ Checkliste

- [ ] Python 3.11+ installiert
- [ ] Discord Bot erstellt
- [ ] Bot Token kopiert
- [ ] Google Cloud Projekt erstellt
- [ ] Google Sheets API aktiviert
- [ ] Service Account erstellt
- [ ] credentials.json heruntergeladen
- [ ] Google Sheet erstellt
- [ ] Sheet mit Service Account geteilt
- [ ] Sheet-ID kopiert
- [ ] Bot-Dateien entpackt
- [ ] Dependencies installiert
- [ ] credentials.json platziert
- [ ] .env erstellt und konfiguriert
- [ ] Bot gestartet
- [ ] /setup ausgeführt
- [ ] Erster Test-Log erstellt

---

**Herzlichen Glückwunsch! 🎉**

Dein Bot läuft! Du bist awesome! 🚀
