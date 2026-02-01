#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 METALLIC PURPLE SHEETS DESIGNER + PLANTAGEN
Premium Google Sheets Design mit Chrome/Öleffekt + Ananas-Plantagen Tab

Author: xPerpleXz
Version: 2.2.0 - Metallic Purple Edition + Ananas-Plantagen
License: MIT

Features:
- Metallic Purple Farbpalette
- Chrome/Öl Effekt Styling
- 5 Premium Tabs (Logs, Dashboard, Auszahlungen, Archiv, Plantagen)
- Bedingte Formatierung
- Live-Formeln & Dashboard
- Dropdown-Menüs
- Plantagen-Tracking
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from dotenv import load_dotenv
import time

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# 🎨 METALLIC PURPLE COLOR PALETTE (RGB 0-1 Format für Google Sheets API)
COLORS = {
    # Primary Colors
    'primary': {'red': 0.416, 'green': 0.051, 'blue': 0.678},        # #6A0DAD Classic Purple
    'secondary': {'red': 0.239, 'green': 0.000, 'blue': 0.400},      # #3D0066 Dark Chrome
    'accent': {'red': 0.780, 'green': 0.490, 'blue': 1.000},         # #C77DFF Metallic Lilac
    
    # Functional
    'success': {'red': 0.616, 'green': 0.306, 'blue': 0.867},        # #9D4EDD Purple Success
    'warning': {'red': 0.878, 'green': 0.251, 'blue': 0.984},        # #E040FB Magenta
    'danger': {'red': 0.667, 'green': 0.000, 'blue': 1.000},         # #AA00FF Vivid Purple
    
    # Neutral
    'white': {'red': 1.000, 'green': 1.000, 'blue': 1.000},
    'light': {'red': 0.965, 'green': 0.949, 'blue': 0.980},          # #F7F2FA Light Purple
    'light_alt': {'red': 0.929, 'green': 0.898, 'blue': 0.961},      # #EDE5F5 Alt Light
    'dark': {'red': 0.118, 'green': 0.000, 'blue': 0.200},           # #1E0033 Very Dark
    
    # Chrome Effects
    'chrome_1': {'red': 0.482, 'green': 0.173, 'blue': 0.749},       # #7B2CBF Gradient 1
    'chrome_2': {'red': 0.878, 'green': 0.667, 'blue': 1.000},       # #E0AAFF Gradient 2
    'gold': {'red': 1.000, 'green': 0.843, 'blue': 0.000},           # #FFD700 Gold
    
    # Plantagen
    'green': {'red': 0.000, 'green': 0.800, 'blue': 0.000},          # #00CC00 Green
    'green_light': {'red': 0.800, 'green': 1.000, 'blue': 0.800},    # #CCFFCC Light Green
}


def init_sheets():
    """Initialize Google Sheets Service"""
    try:
        if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
            import base64
            print("📦 Verwende Base64 Credentials...")
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


def get_or_create_sheets(service):
    """Hole existierende Sheets oder erstelle neue"""
    print("\n📄 Überprüfe Tabs...")
    
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        existing_sheets = {sheet['properties']['title']: sheet['properties']['sheetId'] 
                          for sheet in spreadsheet.get('sheets', [])}
        
        print(f"   Existierende Tabs: {list(existing_sheets.keys())}")
        
        # Tabs die erstellt werden müssen
        required_tabs = {
            'Logs': {'color': COLORS['primary'], 'cols': 8, 'rows': 1000},
            '📊 Dashboard': {'color': COLORS['success'], 'cols': 12, 'rows': 50},
            'Auszahlungen': {'color': COLORS['gold'], 'cols': 8, 'rows': 1000},
            'Archiv': {'color': COLORS['secondary'], 'cols': 9, 'rows': 5000},
            '🌱 Plantagen': {'color': COLORS['green'], 'cols': 9, 'rows': 1000}  # NEU
        }
        
        requests = []
        
        for tab_name, config in required_tabs.items():
            if tab_name not in existing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': tab_name,
                            'gridProperties': {
                                'rowCount': config['rows'],
                                'columnCount': config['cols']
                            },
                            'tabColor': config['color']
                        }
                    }
                })
                print(f"   ➕ Erstelle: {tab_name}")
        
        if requests:
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
            print("✅ Tabs erstellt!")
            
            # Neu laden für aktuelle Sheet IDs
            time.sleep(1)
            spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
            existing_sheets = {sheet['properties']['title']: sheet['properties']['sheetId'] 
                              for sheet in spreadsheet.get('sheets', [])}
        
        return existing_sheets
        
    except HttpError as e:
        print(f"❌ Fehler: {e}")
        return {}


def design_logs_tab(service, sheet_id):
    """Premium Design für Logs Tab"""
    print("\n🎨 Designe Logs Tab...")
    
    # Header eintragen
    headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Aktion', 'Beschreibung', 'Betrag', 'Bild-URL']]
    
    body = {'values': headers}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Logs!A1:H1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    requests = []
    
    # 1. Header Styling - Metallic Purple
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 8},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': COLORS['primary'],
                    'textFormat': {
                        'foregroundColor': COLORS['white'],
                        'fontSize': 11,
                        'bold': True,
                        'fontFamily': 'Roboto'
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE',
                    'padding': {'top': 8, 'bottom': 8, 'left': 4, 'right': 4}
                }
            },
            'fields': 'userEnteredFormat'
        }
    })
    
    # 2. Zebra Striping mit Purple-Tönen
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 0, 'endColumnIndex': 8}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=0'}]
                    },
                    'format': {'backgroundColor': COLORS['light']}
                }
            },
            'index': 0
        }
    })
    
    # 3. Ungerade Zeilen
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 0, 'endColumnIndex': 8}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=1'}]
                    },
                    'format': {'backgroundColor': COLORS['light_alt']}
                }
            },
            'index': 1
        }
    })
    
    # 4. Betrag Highlighting (>10€ = Gold)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'NUMBER_GREATER', 'values': [{'userEnteredValue': '10'}]},
                    'format': {
                        'backgroundColor': {'red': 1.0, 'green': 0.95, 'blue': 0.8},
                        'textFormat': {'foregroundColor': {'red': 0.6, 'green': 0.4, 'blue': 0.0}, 'bold': True}
                    }
                }
            },
            'index': 2
        }
    })
    
    # 5. Aktion-spezifische Farben
    # Düngen = Grün-Lila
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 4, 'endColumnIndex': 5, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Düngen'}]},
                    'format': {
                        'textFormat': {'foregroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.4}, 'bold': True}
                    }
                }
            },
            'index': 3
        }
    })
    
    # Reparieren = Orange-Lila
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 4, 'endColumnIndex': 5, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Reparieren'}]},
                    'format': {
                        'textFormat': {'foregroundColor': {'red': 0.8, 'green': 0.4, 'blue': 0.0}, 'bold': True}
                    }
                }
            },
            'index': 4
        }
    })
    
    # Panel = Purple
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 4, 'endColumnIndex': 5, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Panel'}]},
                    'format': {
                        'textFormat': {'foregroundColor': COLORS['primary'], 'bold': True}
                    }
                }
            },
            'index': 5
        }
    })
    
    # Plantage = Grün
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 4, 'endColumnIndex': 5, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Plantage'}]},
                    'format': {
                        'textFormat': {'foregroundColor': COLORS['green'], 'bold': True}
                    }
                }
            },
            'index': 6
        }
    })
    
    # 6. Column Widths
    widths = [160, 100, 140, 150, 150, 300, 100, 350]
    for i, width in enumerate(widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })
    
    # 7. Row Height für Header
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1},
            'properties': {'pixelSize': 40},
            'fields': 'pixelSize'
        }
    })
    
    # 8. Freeze Header
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    
    # 9. Betrag als Währung formatieren
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 1000},
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {'type': 'CURRENCY', 'pattern': '#,##0.00 €'}
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
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


def design_dashboard_tab(service, sheet_id):
    """Premium Dashboard mit Live-Formeln"""
    print("\n📊 Erstelle Dashboard...")
    
    # Dashboard Daten
    dashboard_data = [
        # Row 1: Title
        ['💜 STATISTIK DASHBOARD - METALLIC PURPLE EDITION + PLANTAGEN', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 2: Empty
        ['', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 3: Section Headers
        ['📊 GESAMTÜBERSICHT', '', '', '📅 DIESE WOCHE', '', '', '📆 HEUTE', '', '', '', '', ''],
        # Row 4: Stats
        ['Gesamt Logs:', '=COUNTA(Logs!A:A)-1', '', 'Woche Logs:', '=COUNTIF(Logs!B:B,"KW"&WEEKNUM(TODAY())&"/"&YEAR(TODAY()))', '', 'Heute:', '=SUMPRODUCT((TEXT(Logs!A:A,"DD.MM.YYYY")=TEXT(TODAY(),"DD.MM.YYYY"))*1)', '', '', '', ''],
        # Row 5: Money
        ['Gesamt €:', '=SUM(Logs!G:G)', '', 'Woche €:', '=SUMIF(Logs!B:B,"KW"&WEEKNUM(TODAY())&"/"&YEAR(TODAY()),Logs!G:G)', '', 'Heute €:', '=SUMPRODUCT((TEXT(Logs!A:A,"DD.MM.YYYY")=TEXT(TODAY(),"DD.MM.YYYY"))*Logs!G:G)', '', '', '', ''],
        # Row 6: Average
        ['Ø pro Log:', '=IFERROR(AVERAGE(Logs!G:G),0)', '', 'Ø Woche:', '=IFERROR(AVERAGEIF(Logs!B:B,"KW"&WEEKNUM(TODAY())&"/"&YEAR(TODAY()),Logs!G:G),0)', '', '', '', '', '', '', ''],
        # Row 7: Empty
        ['', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 8: Section
        ['═══════════════════════════════════════════════════════', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 9: Actions Header
        ['🎯 AKTIONEN BREAKDOWN', '', '', '', '', '', '💰 AUSZAHLUNGEN', '', '', '', '', ''],
        # Row 10: Table Header
        ['Aktion', 'Anzahl', 'Gesamt €', 'Ø €', '', '', 'Gesamt ausgezahlt:', '=SUM(Auszahlungen!E:E)', '', '', '', ''],
        # Row 11: Düngen
        ['🌱 Düngen', '=COUNTIF(Logs!E:E,"Düngen")', '=SUMIF(Logs!E:E,"Düngen",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Düngen",Logs!G:G),0)', '', '', 'Anzahl Auszahlungen:', '=COUNTA(Auszahlungen!A:A)-1', '', '', '', ''],
        # Row 12: Reparieren
        ['🔧 Reparieren', '=COUNTIF(Logs!E:E,"Reparieren")', '=SUMIF(Logs!E:E,"Reparieren",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Reparieren",Logs!G:G),0)', '', '', 'Im Archiv:', '=COUNTA(Archiv!A:A)-1', '', '', '', ''],
        # Row 13: Panel
        ['⚡ Panel platziert', '=COUNTIF(Logs!E:E,"Panel platziert")', '=SUMIF(Logs!E:E,"Panel platziert",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Panel platziert",Logs!G:G),0)', '', '', '', '', '', '', '', ''],
        # Row 14: Plantage gesät
        ['🌾 Plantage gesät', '=COUNTIF(Logs!E:E,"Plantage gesät")', '=SUMIF(Logs!E:E,"Plantage gesät",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Plantage gesät",Logs!G:G),0)', '', '', '', '', '', '', '', ''],
        # Row 15: Plantage geerntet
        ['🌱 Plantage geerntet', '=COUNTIF(Logs!E:E,"Plantage geerntet")', '=SUMIF(Logs!E:E,"Plantage geerntet",Logs!G:G)', '=IFERROR(AVERAGEIF(Logs!E:E,"Plantage geerntet",Logs!G:G),0)', '', '', '', '', '', '', '', ''],
        # Row 16: Empty
        ['', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 17: Section
        ['═══════════════════════════════════════════════════════', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 18: Plantagen Header
        ['🌱 AKTIVE PLANTAGEN', '', '', '', '', '', '', '', '', '', '', ''],
        # Row 19: Plantagen Stats
        ['Aktive Plantagen:', '=COUNTIF(\'🌱 Plantagen\'!G:G,"Aktiv")', '', 'Fertige Plantagen:', '=COUNTIF(\'🌱 Plantagen\'!G:G,"Fertig")', '', 'Geerntete Plantagen:', '=COUNTIF(\'🌱 Plantagen\'!G:G,"Geerntet")', '', '', '', ''],
    ]
    
    try:
        body = {'values': dashboard_data}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='📊 Dashboard!A1:L19',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print("✅ Dashboard Daten eingefügt!")
        
        # Styling
        requests = []
        
        # Title Row - Gradient Effect
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 12},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': COLORS['primary'],
                        'textFormat': {
                            'foregroundColor': COLORS['white'],
                            'fontSize': 14,
                            'bold': True,
                            'fontFamily': 'Roboto'
                        },
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat'
            }
        })
        
        # Merge Title
        requests.append({
            'mergeCells': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 12},
                'mergeType': 'MERGE_ALL'
            }
        })
        
        # Section Headers (Row 3, 9, 18)
        for row in [2, 8, 17]:
            requests.append({
                'repeatCell': {
                    'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row+1, 'startColumnIndex': 0, 'endColumnIndex': 12},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': COLORS['chrome_1'],
                            'textFormat': {
                                'foregroundColor': COLORS['white'],
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat'
                }
            })
        
        # Table Headers (Row 10)
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 9, 'endRowIndex': 10, 'startColumnIndex': 0, 'endColumnIndex': 6},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': COLORS['accent'],
                        'textFormat': {
                            'foregroundColor': COLORS['dark'],
                            'fontSize': 10,
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        })
        
        # Werte-Zellen Styling
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 3, 'endRowIndex': 6, 'startColumnIndex': 1, 'endColumnIndex': 2},
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'foregroundColor': COLORS['primary'],
                            'fontSize': 12,
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        })
        
        # Row Heights
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1},
                'properties': {'pixelSize': 50},
                'fields': 'pixelSize'
            }
        })
        
        # Column Widths
        widths = [180, 120, 120, 100, 20, 20, 180, 120, 100, 100, 100, 100]
        for i, width in enumerate(widths):
            requests.append({
                'updateDimensionProperties': {
                    'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                    'properties': {'pixelSize': width},
                    'fields': 'pixelSize'
                }
            })
        
        # Freeze first row
        requests.append({
            'updateSheetProperties': {
                'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
                'fields': 'gridProperties.frozenRowCount'
            }
        })
        
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        
        print("✅ Dashboard gestylt!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def design_auszahlungen_tab(service, sheet_id):
    """Premium Design für Auszahlungen Tab"""
    print("\n💰 Designe Auszahlungen Tab...")
    
    # Header
    headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Betrag', 'Anzahl Logs', 'Status', 'Admin']]
    
    body = {'values': headers}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Auszahlungen!A1:H1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    requests = []
    
    # Header Styling - Gold Theme
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 8},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': COLORS['gold'],
                    'textFormat': {
                        'foregroundColor': COLORS['dark'],
                        'fontSize': 11,
                        'bold': True,
                        'fontFamily': 'Roboto'
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }
            },
            'fields': 'userEnteredFormat'
        }
    })
    
    # Zebra Striping
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 0, 'endColumnIndex': 8}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=0'}]
                    },
                    'format': {'backgroundColor': {'red': 1.0, 'green': 0.98, 'blue': 0.9}}
                }
            },
            'index': 0
        }
    })
    
    # Status Highlighting
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Ausgezahlt'}]},
                    'format': {
                        'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 0.8},
                        'textFormat': {'foregroundColor': {'red': 0.0, 'green': 0.5, 'blue': 0.0}, 'bold': True}
                    }
                }
            },
            'index': 1
        }
    })
    
    # Column Widths
    widths = [160, 100, 140, 150, 100, 100, 100, 140]
    for i, width in enumerate(widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })
    
    # Betrag Währungsformat
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startColumnIndex': 4, 'endColumnIndex': 5, 'startRowIndex': 1, 'endRowIndex': 1000},
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {'type': 'CURRENCY', 'pattern': '#,##0.00 €'}
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    })
    
    # Freeze Header
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    
    # Row Height für Header
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1},
            'properties': {'pixelSize': 40},
            'fields': 'pixelSize'
        }
    })
    
    try:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Auszahlungen Tab gestylt!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def design_archiv_tab(service, sheet_id):
    """Premium Design für Archiv Tab"""
    print("\n📁 Designe Archiv Tab...")
    
    # Header
    headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Aktion', 'Beschreibung', 'Betrag', 'Bild-URL', 'Archiviert am']]
    
    body = {'values': headers}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Archiv!A1:I1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    requests = []
    
    # Header Styling - Dark Chrome Theme
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 9},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': COLORS['secondary'],
                    'textFormat': {
                        'foregroundColor': COLORS['chrome_2'],
                        'fontSize': 11,
                        'bold': True,
                        'fontFamily': 'Roboto'
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }
            },
            'fields': 'userEnteredFormat'
        }
    })
    
    # Zebra Striping mit dunklerem Theme
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 5000, 'startColumnIndex': 0, 'endColumnIndex': 9}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=0'}]
                    },
                    'format': {'backgroundColor': {'red': 0.95, 'green': 0.93, 'blue': 0.98}}
                }
            },
            'index': 0
        }
    })
    
    # "Archiviert am" Spalte hervorheben
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startColumnIndex': 8, 'endColumnIndex': 9, 'startRowIndex': 1, 'endRowIndex': 5000},
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {
                        'foregroundColor': COLORS['secondary'],
                        'italic': True
                    }
                }
            },
            'fields': 'userEnteredFormat.textFormat'
        }
    })
    
    # Column Widths
    widths = [160, 100, 140, 150, 130, 280, 100, 320, 160]
    for i, width in enumerate(widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })
    
    # Betrag Währungsformat
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 5000},
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {'type': 'CURRENCY', 'pattern': '#,##0.00 €'}
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    })
    
    # Freeze Header
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    
    # Row Height für Header
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1},
            'properties': {'pixelSize': 40},
            'fields': 'pixelSize'
        }
    })
    
    try:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Archiv Tab gestylt!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def design_plantagen_tab(service, sheet_id):
    """Premium Design für Plantagen Tab - NEU"""
    print("\n🌱 Designe Plantagen Tab...")
    
    # Header
    headers = [['User-ID', 'Username', 'Gestartet am', 'Countdown (Sek)', 'Letzter Check', 'Letztes Düngen', 'Status', 'Fertig am', 'Nächstes Düngen']]
    
    body = {'values': headers}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='🌱 Plantagen!A1:I1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    requests = []
    
    # Header Styling - Green Theme
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 9},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': COLORS['green'],
                    'textFormat': {
                        'foregroundColor': COLORS['white'],
                        'fontSize': 11,
                        'bold': True,
                        'fontFamily': 'Roboto'
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }
            },
            'fields': 'userEnteredFormat'
        }
    })
    
    # Zebra Striping mit grünen Tönen
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 0, 'endColumnIndex': 9}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=0'}]
                    },
                    'format': {'backgroundColor': COLORS['green_light']}
                }
            },
            'index': 0
        }
    })
    
    # Status Highlighting
    # Aktiv = Grün
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Aktiv'}]},
                    'format': {
                        'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 0.8},
                        'textFormat': {'foregroundColor': {'red': 0.0, 'green': 0.6, 'blue': 0.0}, 'bold': True}
                    }
                }
            },
            'index': 1
        }
    })
    
    # Fertig = Gold
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Fertig'}]},
                    'format': {
                        'backgroundColor': {'red': 1.0, 'green': 0.95, 'blue': 0.6},
                        'textFormat': {'foregroundColor': {'red': 0.6, 'green': 0.4, 'blue': 0.0}, 'bold': True}
                    }
                }
            },
            'index': 2
        }
    })
    
    # Geerntet = Purple
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startColumnIndex': 6, 'endColumnIndex': 7, 'startRowIndex': 1, 'endRowIndex': 1000}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_CONTAINS', 'values': [{'userEnteredValue': 'Geerntet'}]},
                    'format': {
                        'backgroundColor': COLORS['light'],
                        'textFormat': {'foregroundColor': COLORS['primary'], 'bold': True}
                    }
                }
            },
            'index': 3
        }
    })
    
    # Column Widths
    widths = [150, 140, 160, 120, 160, 160, 100, 160, 160]
    for i, width in enumerate(widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })
    
    # Freeze Header
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    
    # Row Height für Header
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1},
            'properties': {'pixelSize': 40},
            'fields': 'pixelSize'
        }
    })
    
    try:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Plantagen Tab gestylt!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def add_data_validation(service, sheets):
    """Füge Dropdown-Menüs und Validierung hinzu"""
    print("\n🔧 Füge Data Validation hinzu...")
    
    logs_id = sheets.get('Logs')
    plantagen_id = sheets.get('🌱 Plantagen')
    
    if not logs_id:
        return False
    
    requests = []
    
    # Aktion Dropdown in Logs Tab
    requests.append({
        'setDataValidation': {
            'range': {
                'sheetId': logs_id,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 4,
                'endColumnIndex': 5
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [
                        {'userEnteredValue': 'Düngen'},
                        {'userEnteredValue': 'Reparieren'},
                        {'userEnteredValue': 'Panel platziert'},
                        {'userEnteredValue': 'Plantage gesät'},
                        {'userEnteredValue': 'Plantage geerntet'}
                    ]
                },
                'showCustomUi': True,
                'strict': True
            }
        }
    })
    
    # Status Dropdown in Plantagen Tab
    if plantagen_id:
        requests.append({
            'setDataValidation': {
                'range': {
                    'sheetId': plantagen_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 6,
                    'endColumnIndex': 7
                },
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [
                            {'userEnteredValue': 'Aktiv'},
                            {'userEnteredValue': 'Fertig'},
                            {'userEnteredValue': 'Geerntet'}
                        ]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            }
        })
    
    try:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Data Validation hinzugefügt!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def main():
    """Main function"""
    print("\n" + "="*70)
    print("  💜 METALLIC PURPLE SHEETS DESIGNER v2.2.0")
    print("  Classic Purple • Dark Chrome • Metallic Lilac • Ananas-Plantagen")
    print("="*70 + "\n")
    
    service = init_sheets()
    if not service:
        print("\n❌ Konnte nicht mit Google Sheets verbinden!")
        return
    
    print(f"✅ Verbunden mit Sheet: {SPREADSHEET_ID[:20]}...")
    
    # Get or create sheets
    sheets = get_or_create_sheets(service)
    if not sheets:
        print("❌ Fehler beim Erstellen der Tabs!")
        return
    
    time.sleep(1)
    
    # Design each tab
    if 'Logs' in sheets:
        design_logs_tab(service, sheets['Logs'])
        time.sleep(0.5)
    
    if '📊 Dashboard' in sheets:
        design_dashboard_tab(service, sheets['📊 Dashboard'])
        time.sleep(0.5)
    
    if 'Auszahlungen' in sheets:
        design_auszahlungen_tab(service, sheets['Auszahlungen'])
        time.sleep(0.5)
    
    if 'Archiv' in sheets:
        design_archiv_tab(service, sheets['Archiv'])
        time.sleep(0.5)
    
    if '🌱 Plantagen' in sheets:
        design_plantagen_tab(service, sheets['🌱 Plantagen'])
        time.sleep(0.5)
    
    # Add data validation
    add_data_validation(service, sheets)
    
    # Summary
    print("\n" + "="*70)
    print("  🎉 METALLIC PURPLE + PLANTAGEN DESIGN KOMPLETT!")
    print("="*70)
    print("\n  ✨ Dein Google Sheet erstrahlt jetzt in Metallic Purple!\n")
    print("  📋 Tabs erstellt/gestylt:")
    print("     • Logs (Premium Purple Design + Plantagen)")
    print("     • 📊 Dashboard (Live-Formeln & Statistiken + Plantagen-Stats)")
    print("     • Auszahlungen (Gold Theme)")
    print("     • Archiv (Dark Chrome Theme)")
    print("     • 🌱 Plantagen (Green Theme) ← NEU!")
    print("\n  🎨 Features:")
    print("     • Metallic Purple Farbpalette")
    print("     • Chrome/Öl Effekt Styling")
    print("     • Bedingte Formatierung")
    print("     • Automatische Währungsformate")
    print("     • Dropdown-Menüs")
    print("     • Zebra Striping")
    print("     • Frozen Headers")
    print("     • Plantagen-Tracking ← NEU!")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Abgebrochen.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
