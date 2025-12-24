# Diese Datei zeigt die Anpassung für Railway Base64 Support
# Ersetze die init_google_sheets() Methode in bot.py mit dieser Version:

def init_google_sheets(self):
    """Google Sheets API initialisieren - mit Base64 Support für Railway"""
    try:
        # Option 1: Base64 credentials (Railway/Cloud Deployment)
        if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
            import base64
            import json
            
            print("📦 Verwende Base64 Credentials...")
            creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
            creds_json = base64.b64decode(creds_base64)
            creds_dict = json.loads(creds_json)
            
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=SCOPES
            )
            print("✅ Google Sheets verbunden (Base64)")
        
        # Option 2: Local credentials.json file
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

# ANLEITUNG:
# 1. Öffne bot.py
# 2. Suche nach der init_google_sheets() Methode (ca. Zeile 29)
# 3. Ersetze die Methode mit dem Code oben
# 4. Speichern und fertig!
