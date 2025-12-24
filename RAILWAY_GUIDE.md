# 🚂 Railway Deployment Guide

## Schnellstart

### Option 1: Mit credentials.json File

1. **Railway Projekt erstellen**
   ```bash
   # Installiere Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Neues Projekt
   railway init
   ```

2. **Environment Variables setzen**
   ```bash
   railway variables set DISCORD_TOKEN="dein_token"
   railway variables set SPREADSHEET_ID="deine_sheet_id"
   railway variables set LOG_CHANNEL_ID="channel_id"
   railway variables set REPORT_CHANNEL_ID="channel_id"
   ```

3. **credentials.json hochladen**
   - Railway Dashboard öffnen
   - Settings → Volumes
   - Neue Volume erstellen: `/app/credentials.json`
   - Inhalt der credentials.json einfügen

4. **Deployen**
   ```bash
   railway up
   ```

### Option 2: credentials.json als Base64 (EMPFOHLEN)

**Vorteile:**
- Einfacher zu verwalten
- Keine Volume nötig
- Funktioniert überall

**Schritte:**

1. **credentials.json zu Base64 konvertieren**
   
   **Linux/Mac:**
   ```bash
   cat credentials.json | base64 -w 0 > credentials_base64.txt
   ```
   
   **Windows (PowerShell):**
   ```powershell
   $content = Get-Content credentials.json -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
   $base64 = [Convert]::ToBase64String($bytes)
   $base64 | Out-File credentials_base64.txt
   ```
   
   **Python (funktioniert überall):**
   ```bash
   python convert_credentials.py
   ```

2. **Base64 String als Environment Variable setzen**
   ```bash
   railway variables set GOOGLE_CREDENTIALS_BASE64="<inhalt_von_credentials_base64.txt>"
   ```

3. **bot.py anpassen** (siehe unten)

4. **Deployen**
   ```bash
   railway up
   ```

## bot.py Anpassung für Base64

Ändere die `init_google_sheets()` Methode in `bot.py`:

```python
def init_google_sheets(self):
    """Google Sheets API initialisieren"""
    try:
        # Option 1: Base64 credentials (Railway)
        if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
            import base64
            import json
            
            creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
            creds_json = base64.b64decode(creds_base64)
            creds_dict = json.loads(creds_json)
            
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=SCOPES
            )
            print("✅ Google Sheets verbunden (Base64)")
        
        # Option 2: Local credentials.json
        else:
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=SCOPES
            )
            print("✅ Google Sheets verbunden (File)")
        
        service = build('sheets', 'v4', credentials=creds)
        return service
        
    except Exception as e:
        print(f"❌ Google Sheets Fehler: {e}")
        return None
```

## Railway CLI Befehle

```bash
# Status checken
railway status

# Logs ansehen
railway logs

# Environment Variables anzeigen
railway variables

# Projekt verbinden
railway link

# Deploy
railway up

# Lokaler Dev Server
railway run python bot.py
```

## Railway Dashboard

Im Web Interface (railway.app):
1. **Deployments**: Siehe alle Deployments und Logs
2. **Variables**: Manage Environment Variables
3. **Settings**: 
   - Change region (Europa empfohlen)
   - Restart policies
   - Custom domains
4. **Metrics**: CPU/RAM Nutzung

## Troubleshooting

### Bot startet nicht
```bash
# Logs ansehen
railway logs --tail 100

# Häufige Fehler:
# - DISCORD_TOKEN fehlt
# - SPREADSHEET_ID falsch
# - credentials.json Base64 fehlerhaft
```

### Base64 dekodieren funktioniert nicht
```python
# Teste lokal:
python3 << EOF
import base64
import os

b64 = os.getenv('GOOGLE_CREDENTIALS_BASE64', '')
if b64:
    try:
        decoded = base64.b64decode(b64)
        print("✅ Base64 valide")
        print(decoded[:100])  # Erste 100 Bytes
    except Exception as e:
        print(f"❌ Fehler: {e}")
else:
    print("❌ Variable nicht gesetzt")
EOF
```

### Memory Issues
Railway Free Tier: 512MB RAM

Wenn der Bot zu viel RAM braucht:
```python
# In bot.py, reduziere Cache:
@tasks.loop(hours=1)  # Öfter aufräumen
async def cleanup_cache(self):
    import gc
    gc.collect()
```

### Zeit/Timezone Probleme
```bash
# Setze Timezone
railway variables set TZ="Europe/Berlin"
```

## GitHub Integration

**Auto-Deploy bei Push:**

1. Push zu GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/user/repo.git
   git push -u origin main
   ```

2. Railway mit GitHub verbinden:
   - Railway Dashboard → New Project
   - "Deploy from GitHub repo"
   - Repository auswählen
   - Auto-deploys aktiviert!

**Jeder Push zu `main` deployt automatisch!**

## Kosten

**Railway Pricing:**
- Hobby Plan: $5/Monat
- 500 Stunden Laufzeit inkludiert
- Danach: $0.000463/GB-hour

**Für 24/7 Bot (~720h/Monat):**
- Mit 512MB: ~$1.68 + $5 = $6.68/Monat

## Alternative: Replit

Wenn Railway zu teuer:
1. Gehe zu replit.com
2. Import from GitHub
3. Setze Secrets (Environment Variables)
4. Run!

**Kostenlos mit "Always On" für $7/Monat**

## Best Practices

1. **Secrets Management**
   - Niemals Tokens in Code
   - Immer Environment Variables
   - credentials.json als Base64

2. **Monitoring**
   - Railway Logs regelmäßig checken
   - Health Checks einrichten
   - Error Notifications per Discord Webhook

3. **Updates**
   ```bash
   # Lokal testen
   git pull
   python bot.py
   
   # Wenn OK, push zu Railway
   git push origin main
   ```

4. **Backups**
   - Google Sheets automatisch gesichert
   - Zusätzlich: Wöchentliche CSV Exports
   - Via admin_tools.py: Backup erstellen

---

**Bei Fragen:** Siehe Railway Docs oder Discord Support!
