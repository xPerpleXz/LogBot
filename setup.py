#!/usr/bin/env python3
"""
Setup-Skript für Discord Log Bot
Hilft beim initialen Setup und der Konfiguration
"""

import os
import sys
import json
from pathlib import Path

def print_header(text):
    """Drucke formatierten Header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Überprüfe Python Version"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 oder höher wird benötigt!")
        print(f"   Deine Version: {sys.version}")
        return False
    print(f"✅ Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_files():
    """Überprüfe ob alle notwendigen Dateien existieren"""
    print_header("Datei-Check")
    
    required_files = [
        'bot.py',
        'requirements.txt',
        '.env.example',
        'README.md'
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} fehlt!")
            all_good = False
    
    return all_good

def create_env_file():
    """Erstelle .env Datei interaktiv"""
    print_header(".env Datei erstellen")
    
    if Path('.env').exists():
        overwrite = input("⚠️  .env existiert bereits. Überschreiben? (j/n): ")
        if overwrite.lower() != 'j':
            print("Übersprungen.")
            return
    
    print("Bitte gib die folgenden Informationen ein:\n")
    
    discord_token = input("Discord Bot Token: ").strip()
    spreadsheet_id = input("Google Sheets ID: ").strip()
    log_channel = input("Log Channel ID (optional): ").strip()
    report_channel = input("Report Channel ID (optional): ").strip()
    
    env_content = f"""# Discord Bot Token
DISCORD_TOKEN={discord_token}

# Google Sheets ID
SPREADSHEET_ID={spreadsheet_id}

# Discord Channel IDs (optional)
LOG_CHANNEL_ID={log_channel if log_channel else ''}
REPORT_CHANNEL_ID={report_channel if report_channel else ''}

# Timezone
TZ=Europe/Berlin
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ .env Datei erstellt!")

def check_credentials():
    """Überprüfe credentials.json"""
    print_header("Google Credentials Check")
    
    if not Path('credentials.json').exists():
        print("⚠️  credentials.json nicht gefunden!")
        print("\nBitte befolge diese Schritte:")
        print("1. Gehe zu https://console.cloud.google.com/")
        print("2. Erstelle einen Service Account")
        print("3. Lade die JSON-Datei herunter")
        print("4. Benenne sie um zu 'credentials.json'")
        print("5. Lege sie in diesen Ordner")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        if 'client_email' in creds:
            print(f"✅ credentials.json gefunden")
            print(f"📧 Service Account Email: {creds['client_email']}")
            print("\n⚠️  WICHTIG: Teile dein Google Sheet mit dieser Email!")
            return True
        else:
            print("❌ Ungültige credentials.json")
            return False
    except json.JSONDecodeError:
        print("❌ credentials.json ist keine gültige JSON-Datei")
        return False

def install_dependencies():
    """Installiere Python Dependencies"""
    print_header("Dependencies installieren")
    
    install = input("Dependencies jetzt installieren? (j/n): ")
    if install.lower() == 'j':
        print("\nInstalliere...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
        print("\n✅ Dependencies installiert!")
    else:
        print("Übersprungen. Führe später aus: pip install -r requirements.txt")

def final_checklist():
    """Finale Checkliste"""
    print_header("Finale Checkliste")
    
    checklist = [
        ("Discord Bot erstellt", "https://discord.com/developers/applications"),
        ("Bot auf Server eingeladen", "OAuth2 URL Generator verwenden"),
        ("Google Cloud Projekt erstellt", "https://console.cloud.google.com/"),
        ("Google Sheets API aktiviert", "APIs & Services aktivieren"),
        ("Service Account erstellt", "credentials.json heruntergeladen"),
        ("Google Sheet erstellt", "Sheet mit Service Account geteilt"),
        (".env Datei konfiguriert", "Discord Token & Sheet ID eingefügt"),
        ("Dependencies installiert", "pip install -r requirements.txt")
    ]
    
    print("Bitte stelle sicher, dass du folgendes erledigt hast:\n")
    for i, (item, hint) in enumerate(checklist, 1):
        print(f"{i}. ☐ {item}")
        print(f"   💡 {hint}\n")
    
    print("\n" + "="*60)
    print("Bereit zum Start? Führe aus: python bot.py")
    print("="*60 + "\n")

def main():
    """Haupt-Setup-Funktion"""
    print("\n" + "🤖 " + "="*54 + " 🤖")
    print("   DISCORD LOG BOT - SETUP ASSISTENT")
    print("🤖 " + "="*54 + " 🤖\n")
    
    # Python Version check
    if not check_python_version():
        return
    
    # Dateien checken
    if not check_files():
        print("\n❌ Einige Dateien fehlen. Bitte überprüfe das Repository.")
        return
    
    # .env erstellen
    create_env_file()
    
    # Credentials checken
    check_credentials()
    
    # Dependencies installieren
    install_dependencies()
    
    # Finale Checkliste
    final_checklist()
    
    print("\n✨ Setup abgeschlossen! Viel Erfolg mit deinem Bot!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup abgebrochen.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
