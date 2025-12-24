#!/usr/bin/env python3
"""
Admin Tools für Discord Log Bot
Erweiterte Verwaltungsfunktionen
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Lade Umgebungsvariablen
load_dotenv()

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def init_sheets():
    """Google Sheets Service initialisieren"""
    try:
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Fehler beim Verbinden: {e}")
        return None

def get_all_logs():
    """Alle Logs abrufen"""
    service = init_sheets()
    if not service:
        return None
    
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A2:H'
        ).execute()
        
        return result.get('values', [])
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None

def stats_overall():
    """Gesamtstatistiken"""
    print("\n" + "="*60)
    print("📊 GESAMTSTATISTIKEN")
    print("="*60 + "\n")
    
    logs = get_all_logs()
    if not logs:
        print("Keine Logs gefunden.")
        return
    
    total_logs = len(logs)
    total_payout = 0
    action_counts = {}
    user_counts = {}
    
    for row in logs:
        if len(row) >= 7:
            action = row[4]
            username = row[2]
            amount = float(row[6])
            
            total_payout += amount
            
            if action not in action_counts:
                action_counts[action] = 0
            action_counts[action] += 1
            
            if username not in user_counts:
                user_counts[username] = {'count': 0, 'payout': 0}
            user_counts[username]['count'] += 1
            user_counts[username]['payout'] += amount
    
    print(f"Gesamtanzahl Logs: {total_logs}")
    print(f"Gesamtauszahlung: {total_payout:.2f}€\n")
    
    print("Aktionen:")
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {action}: {count}x")
    
    print("\nTop 10 Mitglieder (nach Verdienst):")
    top_users = sorted(user_counts.items(), key=lambda x: x[1]['payout'], reverse=True)[:10]
    for i, (user, data) in enumerate(top_users, 1):
        print(f"  {i}. {user}: {data['payout']:.2f}€ ({data['count']} Logs)")

def stats_weekly():
    """Wöchentliche Statistiken"""
    print("\n" + "="*60)
    print("📅 WÖCHENTLICHE STATISTIKEN")
    print("="*60 + "\n")
    
    logs = get_all_logs()
    if not logs:
        print("Keine Logs gefunden.")
        return
    
    current_week = datetime.now().isocalendar()[1]
    current_year = datetime.now().year
    week_key = f"KW{current_week}/{current_year}"
    
    weekly_logs = [row for row in logs if len(row) >= 2 and row[1] == week_key]
    
    if not weekly_logs:
        print(f"Keine Logs für {week_key} gefunden.")
        return
    
    total_payout = sum(float(row[6]) for row in weekly_logs if len(row) >= 7)
    
    print(f"Kalenderwoche: {week_key}")
    print(f"Anzahl Logs: {len(weekly_logs)}")
    print(f"Gesamtauszahlung: {total_payout:.2f}€")

def export_user_stats(username=None):
    """Exportiere Statistiken für einen User"""
    logs = get_all_logs()
    if not logs:
        print("Keine Logs gefunden.")
        return
    
    if username:
        user_logs = [row for row in logs if len(row) >= 3 and row[2].lower() == username.lower()]
    else:
        username = input("Username eingeben: ").strip()
        user_logs = [row for row in logs if len(row) >= 3 and row[2].lower() == username.lower()]
    
    if not user_logs:
        print(f"Keine Logs für User '{username}' gefunden.")
        return
    
    print(f"\n📊 Statistiken für: {username}")
    print("="*60 + "\n")
    
    total_payout = 0
    action_counts = {}
    
    for row in user_logs:
        if len(row) >= 7:
            action = row[4]
            amount = float(row[6])
            total_payout += amount
            
            if action not in action_counts:
                action_counts[action] = 0
            action_counts[action] += 1
    
    print(f"Gesamtlogs: {len(user_logs)}")
    print(f"Gesamtverdienst: {total_payout:.2f}€\n")
    
    print("Aktionen:")
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {action}: {count}x")

def backup_to_csv():
    """Backup als CSV exportieren"""
    logs = get_all_logs()
    if not logs:
        print("Keine Logs zum Exportieren.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.csv"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("Zeitstempel,KW,Username,User-ID,Aktion,Beschreibung,Betrag,Bild-URL\n")
            
            # Daten
            for row in logs:
                f.write(','.join(f'"{cell}"' for cell in row) + '\n')
        
        print(f"✅ Backup erstellt: {filename}")
    except Exception as e:
        print(f"❌ Fehler beim Backup: {e}")

def delete_logs_before_date():
    """Lösche Logs vor bestimmtem Datum (Admin-Funktion)"""
    print("\n⚠️  WARNUNG: Diese Funktion löscht unwiderruflich Daten!")
    confirm = input("Fortfahren? (JA zum Bestätigen): ")
    
    if confirm != "JA":
        print("Abgebrochen.")
        return
    
    date_str = input("Datum (TT.MM.JJJJ): ")
    try:
        cutoff_date = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        print("❌ Ungültiges Datumsformat!")
        return
    
    service = init_sheets()
    if not service:
        return
    
    logs = get_all_logs()
    if not logs:
        print("Keine Logs gefunden.")
        return
    
    # Filter logs nach Datum
    kept_logs = []
    deleted_count = 0
    
    for row in logs:
        if len(row) >= 1:
            try:
                log_date = datetime.strptime(row[0], "%d.%m.%Y %H:%M:%S")
                if log_date >= cutoff_date:
                    kept_logs.append(row)
                else:
                    deleted_count += 1
            except ValueError:
                kept_logs.append(row)  # Bei Fehler behalten
    
    if deleted_count == 0:
        print("Keine Logs zum Löschen gefunden.")
        return
    
    print(f"\n{deleted_count} Logs würden gelöscht werden.")
    final_confirm = input("Wirklich löschen? (JA zum Bestätigen): ")
    
    if final_confirm != "JA":
        print("Abgebrochen.")
        return
    
    # Sheet leeren und neu schreiben
    try:
        sheet = service.spreadsheets()
        
        # Leeren
        sheet.values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A2:H'
        ).execute()
        
        # Neu schreiben
        if kept_logs:
            body = {'values': kept_logs}
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='Logs!A2:H',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
        
        print(f"✅ {deleted_count} Logs gelöscht.")
    except Exception as e:
        print(f"❌ Fehler: {e}")

def menu():
    """Hauptmenü"""
    while True:
        print("\n" + "="*60)
        print("🔧 ADMIN TOOLS")
        print("="*60)
        print("\n1. Gesamtstatistiken")
        print("2. Wöchentliche Statistiken")
        print("3. User-Statistiken")
        print("4. CSV Backup erstellen")
        print("5. Alte Logs löschen (VORSICHT!)")
        print("0. Beenden\n")
        
        choice = input("Wähle eine Option: ").strip()
        
        if choice == '1':
            stats_overall()
        elif choice == '2':
            stats_weekly()
        elif choice == '3':
            export_user_stats()
        elif choice == '4':
            backup_to_csv()
        elif choice == '5':
            delete_logs_before_date()
        elif choice == '0':
            print("Auf Wiedersehen!")
            break
        else:
            print("❌ Ungültige Auswahl!")

if __name__ == "__main__":
    if not SPREADSHEET_ID:
        print("❌ SPREADSHEET_ID nicht in .env gefunden!")
        sys.exit(1)
    
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\nProgramm beendet.")
