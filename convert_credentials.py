#!/usr/bin/env python3
"""
Konvertiert credentials.json zu Base64 für Railway Deployment
"""

import base64
import json
from pathlib import Path

def convert_credentials():
    """Konvertiere credentials.json zu Base64"""
    
    # Check ob credentials.json existiert
    if not Path('credentials.json').exists():
        print("❌ credentials.json nicht gefunden!")
        print("   Stelle sicher, dass die Datei im gleichen Ordner liegt.")
        return False
    
    try:
        # Lese credentials.json
        with open('credentials.json', 'r', encoding='utf-8') as f:
            creds_data = f.read()
        
        # Validiere JSON
        json.loads(creds_data)
        
        # Konvertiere zu Base64
        base64_encoded = base64.b64encode(creds_data.encode('utf-8')).decode('utf-8')
        
        # Speichere in Datei
        with open('credentials_base64.txt', 'w', encoding='utf-8') as f:
            f.write(base64_encoded)
        
        print("✅ Erfolgreich konvertiert!")
        print("\n" + "="*60)
        print("Base64 String wurde gespeichert in: credentials_base64.txt")
        print("="*60 + "\n")
        
        print("📋 Nächste Schritte:")
        print("\n1. Kopiere den Inhalt von credentials_base64.txt")
        print("\n2. Für Railway:")
        print("   railway variables set GOOGLE_CREDENTIALS_BASE64=\"<inhalt>\"")
        print("\n3. Oder im Railway Dashboard:")
        print("   Variables → New Variable → GOOGLE_CREDENTIALS_BASE64")
        print("\n" + "="*60)
        
        # Zeige ersten und letzten Teil
        preview_start = base64_encoded[:50]
        preview_end = base64_encoded[-50:]
        print(f"\nVorschau: {preview_start}...{preview_end}")
        print(f"Länge: {len(base64_encoded)} Zeichen")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json ist keine gültige JSON-Datei!")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def verify_base64():
    """Verifiziere Base64 String"""
    
    if not Path('credentials_base64.txt').exists():
        print("❌ credentials_base64.txt nicht gefunden!")
        return False
    
    try:
        # Lese Base64
        with open('credentials_base64.txt', 'r', encoding='utf-8') as f:
            base64_data = f.read().strip()
        
        # Dekodiere
        decoded = base64.b64decode(base64_data)
        
        # Parse als JSON
        creds = json.loads(decoded)
        
        print("✅ Base64 String ist valide!")
        print(f"\nService Account Email: {creds.get('client_email', 'N/A')}")
        print(f"Project ID: {creds.get('project_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Verifikation: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("\n" + "="*60)
    print("🔐 CREDENTIALS.JSON → BASE64 KONVERTER")
    print("="*60 + "\n")
    
    print("Optionen:")
    print("1. credentials.json zu Base64 konvertieren")
    print("2. Base64 String verifizieren")
    print("3. Beides\n")
    
    choice = input("Wähle Option (1-3): ").strip()
    
    if choice == '1':
        convert_credentials()
    elif choice == '2':
        verify_base64()
    elif choice == '3':
        if convert_credentials():
            print("\n" + "="*60)
            verify_base64()
    else:
        print("❌ Ungültige Auswahl!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
