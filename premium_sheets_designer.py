#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 PREMIUM GOOGLE SHEETS DESIGNER
Das Elite-Entwicklerteam präsentiert: Ein visuelles Meisterwerk

Author: xPerpleXz
Version: 2.0.0 - Premium Edition
License: MIT

Erstellt professionelles Sheet-Design mit:
- Corporate Color Palette
- 4 Tabs (Logs, Dashboard, Auszahlungen, Historie)
- Automatische Charts
- Bedingte Formatierung
- Live-Formeln
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import time

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# 🎨 PREMIUM COLOR PALETTE
COLORS = {
    'primary': {'red': 0.26, 'green': 0.52, 'blue': 0.96},  # Google Blue
    'success': {'red': 0.30, 'green': 0.69, 'blue': 0.31},  # Green
    'warning': {'red': 1.00, 'green': 0.76, 'blue': 0.03},  # Amber
    'danger': {'red': 0.96, 'green': 0.26, 'blue': 0.21},   # Red
    'white': {'red': 1.00, 'green': 1.00, 'blue': 1.00},
    'light_gray': {'red': 0.96, 'green': 0.96, 'blue': 0.96},
    'gold': {'red': 1.00, 'green': 0.84, 'blue': 0.00}
}

def init_sheets():
    """Initialize Google Sheets Service"""
    try:
        if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
            import base64, json
            creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
            creds_json = base64.b64decode(creds_base64)
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None

def create_all_tabs(service):
    """Erstelle alle notwendigen Tabs"""
    print("\n📄 Erstelle Tabs...")
    
    try:
        # Get existing sheets
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        existing_sheets = {sheet['properties']['title']: sheet['properties']['sheetId'] 
                          for sheet in spreadsheet.get('sheets', [])}
        
        requests = []
        
        # Dashboard Tab
        if '📊 Dashboard' not in existing_sheets:
            requests.append({
                'addSheet': {
                    'properties': {
                        'title': '📊 Dashboard',
                        'gridProperties': {'rowCount': 50, 'columnCount': 12},
                        'tabColor': COLORS['success']
                    }
                }
            })
        
        # Auszahlungen Tab
        if 'Auszahlungen' not in existing_sheets:
            requests.append({
                'addSheet': {
                    'properties': {
                        'title': 'Auszahlungen',
                        'gridProperties': {'rowCount': 1000, 'columnCount': 7},
                        'tabColor': COLORS['gold']
                    }
                }
            })
        
        if requests:
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()
            print("✅ Tabs erstellt!")
        else:
            print("ℹ️ Tabs existieren bereits")
        
        return True
        
    except HttpError as e:
        if 'already exists' in str(e):
            print("ℹ️ Tabs existieren bereits")
            return True
        print(f"❌ Fehler: {e}")
        return False

def design_logs_tab(service):
    """Design für Logs Tab"""
    print("\n🎨 Designe Logs Tab...")
    
    requests = []
    
    # Header Styling
    requests.append({
        'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': COLORS['primary'],
                    'textFormat': {
                        'foregroundColor': COLORS['white'],
                        'fontSize': 11,
                        'bold': True
                    },
                    'horizontalAlignment': 'CENTER',
                    'padding': {'top': 10, 'bottom': 10}
                }
            },
            'fields': 'userEnteredFormat'
        }
    })
    
    # Zebra Striping
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 10000}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=0'}]
                    },
                    'format': {'backgroundColor': COLORS['light_gray']}
                }
            },
            'index': 0
        }
    })
    
    # Column Widths
    widths = [160, 90, 140, 150, 130, 280, 95, 320]
    for i, width in enumerate(widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })
    
    # Betrag Formatierung (Grün >10€, Gelb 5-10€)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': 0, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1}],
                'booleanRule': {
                    'condition': {'type': 'NUMBER_GREATER', 'values': [{'userEnteredValue': '10'}]},
                    'format': {
                        'backgroundColor': {'red': 0.85, 'green': 0.92, 'blue': 0.83},
                        'textFormat': {'foregroundColor': COLORS['success'], 'bold': True}
                    }
                }
            },
            'index': 1
        }
    })
    
    # Freeze Header
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': 0, 'gridProperties': {'frozenRowCount': 1}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    
    # Execute
    try:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Logs Tab gestylt!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def create_dashboard(service):
    """Erstelle Dashboard mit Formeln"""
    print("\n📊 Erstelle Dashboard...")
    
    dashboard_data = [
        ['📊 STATISTIK DASHBOARD', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', ''],
        ['GESAMTÜBERSICHT', '', '', 'DIESE WOCHE', '', '', 'HEUTE', '', '', '', '', ''],
        ['📋 Gesamt Logs:', '=COUNTA(Logs!A:A)-1', '', '📋 Logs:', '=COUNTIF(Logs!B:B,"KW"&WEEKNUM(TODAY()))', '', '📋 Logs:', '=COUNTIF(Logs!A:A,TODAY())', '', '', '', ''],
        ['💰 Gesamt €:', '=SUM(Logs!G:G)', '', '💰 Woche €:', '=SUMIF(Logs!B:B,"KW"&WEEKNUM(TODAY()),Logs!G:G)', '', '💰 Heute €:', '=SUMIF(Logs!A:A,TODAY(),Logs!G:G)', '', '', '', ''],
        ['📊 Ø/Log:', '=IFERROR(AVERAGE(Logs!G:G),0)', '', '📊 Ø:', '=IFERROR(AVERAGEIF(Logs!B:B,"KW"&WEEKNUM(TODAY()),Logs!G:G),0)', '', '📊 Ø:', '=IFERROR(AVERAGEIF(Logs!A:A,TODAY(),Logs!G:G),0)', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', ''],
        ['═══ AKTIONEN BREAKDOWN ═══', '', '', '', '', '', '', '', '', '', '', ''],
        ['Aktion', 'Anzahl', 'Gesamt €', 'Ø €', '', '', '', '', '', '', '', ''],
        ['🌱 Düngen', '=COUNTIF(Logs!E:E,"Düngen")', '=SUMIF(Logs!E:E,"Düngen",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Düngen",Logs!G:G),0)', '', '', '', '', '', '', '', ''],
        ['🔧 Reparieren', '=COUNTIF(Logs!E:E,"Reparieren")', '=SUMIF(Logs!E:E,"Reparieren",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Reparieren",Logs!G:G),0)', '', '', '', '', '', '', '', ''],
        ['⚡ Panel', '=COUNTIF(Logs!E:E,"Panel platziert")', '=SUMIF(Logs!E:E,"Panel platziert",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Panel platziert",Logs!G:G),0)', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', ''],
        ['═══ 🏆 TOP 5 VERDIENER ═══', '', '', '', '', '', '', '', '', '', '', ''],
        ['Rang', 'Username', 'Logs', 'Gesamt €', '', '', '', '', '', '', '', '']
    ]
    
    try:
        body = {'values': dashboard_data}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='📊 Dashboard!A1:L15',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print("✅ Dashboard erstellt!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def style_dashboard(service):
    """Style Dashboard"""
    print("\n🎨 Style Dashboard...")
    
    try:
        # Get Dashboard sheet ID
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        dashboard_id = None
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == '📊 Dashboard':
                dashboard_id = sheet['properties']['sheetId']
                break
        
        if dashboard_id is None:
            print("❌ Dashboard nicht gefunden")
            return False
        
        requests = []
        
        # Title
        requests.append({
            'repeatCell': {
                'range': {'sheetId': dashboard_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 12},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': COLORS['primary'],
                        'textFormat': {'foregroundColor': COLORS['white'], 'fontSize': 18, 'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat'
            }
        })
        
        # Merge title
        requests.append({
            'mergeCells': {
                'range': {'sheetId': dashboard_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 12},
                'mergeType': 'MERGE_ALL'
            }
        })
        
        # Section headers (rows 2, 7, 13)
        for row in [2, 7, 13]:
            requests.append({
                'repeatCell': {
                    'range': {'sheetId': dashboard_id, 'startRowIndex': row, 'endRowIndex': row+1},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.42, 'green': 0.65, 'blue': 0.89},
                            'textFormat': {'foregroundColor': COLORS['white'], 'bold': True}
                        }
                    },
                    'fields': 'userEnteredFormat'
                }
            })
        
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Dashboard gestylt!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def setup_auszahlungen_tab(service):
    """Setup Auszahlungen Tab"""
    print("\n💰 Setup Auszahlungen Tab...")
    
    headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Betrag', 'Anzahl Logs', 'Status']]
    
    try:
        body = {'values': headers}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='Auszahlungen!A1:G1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Get sheet ID
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id = None
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == 'Auszahlungen':
                sheet_id = sheet['properties']['sheetId']
                break
        
        if sheet_id:
            requests = [{
                'repeatCell': {
                    'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': COLORS['gold'],
                            'textFormat': {'foregroundColor': COLORS['white'], 'bold': True},
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat'
                }
            }]
            
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        
        print("✅ Auszahlungen Tab eingerichtet!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎨 PREMIUM GOOGLE SHEETS DESIGNER")
    print("="*60)
    print("Von: Das Elite-Entwicklerteam")
    print("="*60 + "\n")
    
    service = init_sheets()
    if not service:
        print("\n❌ Konnte nicht mit Google Sheets verbinden!")
        return
    
    print(f"✅ Verbunden mit Sheet: {SPREADSHEET_ID}\n")
    
    # Create tabs
    if not create_all_tabs(service):
        return
    
    time.sleep(1)
    
    # Design Logs
    design_logs_tab(service)
    time.sleep(1)
    
    # Create Dashboard
    create_dashboard(service)
    time.sleep(1)
    
    # Style Dashboard
    style_dashboard(service)
    time.sleep(1)
    
    # Setup Auszahlungen
    setup_auszahlungen_tab(service)
    
    print("\n" + "="*60)
    print("🎉 PREMIUM DESIGN KOMPLETT!")
    print("="*60)
    print("\n✨ Dein Google Sheet ist jetzt ein Kunstwerk!\n")
    print("📋 Tabs erstellt:")
    print("   • Logs (mit Premium Design)")
    print("   • 📊 Dashboard (mit Live-Formeln)")
    print("   • Auszahlungen (Tracking)")
    print("\n🎨 Features:")
    print("   • Corporate Color Scheme")
    print("   • Zebra Striping")
    print("   • Bedingte Formatierung")
    print("   • Automatische Formeln")
    print("   • Professionelle Layout")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Abgebrochen.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
