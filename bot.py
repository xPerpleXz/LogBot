#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Log Bot - METALLIC PURPLE EDITION + ANANAS-PLANTAGEN
Professional Log Management System with Premium Payment Panel & Plantation System

Author: xPerpleXz
License: MIT
Version: 2.2.0 - Metallic Purple Edition + Ananas-Plantagen
Repository: https://github.com/xPerpleXz/discord-log-bot
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional, Dict, List, Tuple
import json
import re

# Google Sheets imports
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Environment
from dotenv import load_dotenv
load_dotenv()

__author__ = "xPerpleXz"
__version__ = "2.2.0"
__license__ = "MIT"

# ==================== KONFIGURATION ====================

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Auszahlungsbeträge (anpassbar)
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,
    'Reparieren': 8.00,
    'Panel platziert': 12.00,
    'Plantage gesät': 15.00
}

# 🌱 PLANTAGEN KONFIGURATION
PLANTATION_DURATION = 8 * 60 * 60  # 8 Stunden in Sekunden
FERTILIZE_WINDOW = 30 * 60  # 30 Minuten Fenster (X:30 bis X+1:00)
PLANTATION_HARVEST_REWARD = 50.00  # Bonus bei Ernte

# 🎨 METALLIC PURPLE COLOR PALETTE
COLORS = {
    'primary': 0x6A0DAD,
    'secondary': 0x3D0066,
    'accent': 0xC77DFF,
    'success': 0x9D4EDD,
    'warning': 0xE040FB,
    'danger': 0xAA00FF,
    'info': 0xB388FF,
    'gold': 0xFFD700,
    'platinum': 0xE5E4E2,
    'chrome': 0x8A2BE2,
    'green': 0x00FF00,
    'gradient_start': 0x7B2CBF,
    'gradient_end': 0xE0AAFF,
}

# Rollen-Konfiguration
PAYOUT_ROLE_IDS = []
CONFIG_FILE = 'config.json'

def load_config():
    """Lade Konfiguration aus Datei und .env"""
    global PAYOUT_ROLE_IDS
    env_roles = os.getenv('PAYOUT_ROLE_IDS', '')
    if env_roles:
        PAYOUT_ROLE_IDS = [int(r.strip()) for r in env_roles.split(',') if r.strip()]
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'payout_roles' in config:
                    PAYOUT_ROLE_IDS = config['payout_roles']
        except:
            pass
    return PAYOUT_ROLE_IDS

def save_config():
    """Speichere Konfiguration in Datei"""
    config = {'payout_roles': PAYOUT_ROLE_IDS}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

load_config()

# ==================== BOT CLASS ====================

class LogBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.sheets_service = None
        
    async def setup_hook(self):
        """Bot Initialisierung"""
        await self.tree.sync()
        print(f'Bot bereit: {self.user}')
        
        self.sheets_service = self.init_google_sheets()
        
        if not self.weekly_report.is_running():
            self.weekly_report.start()
        
        if not self.plantation_update_loop.is_running():
            self.plantation_update_loop.start()
    
    def init_google_sheets(self):
        """Google Sheets API initialisieren - mit Base64 Support"""
        try:
            if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
                import base64
                print("📦 Verwende Base64 Credentials...")
                creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
                creds_json = base64.b64decode(creds_base64)
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                print("✅ Google Sheets verbunden (Base64)")
            else:
                creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
                print("✅ Google Sheets verbunden (File)")
            
            service = build('sheets', 'v4', credentials=creds)
            return service
        except Exception as e:
            print(f"❌ Google Sheets Fehler: {e}")
            return None
    
    @tasks.loop(hours=168)
    async def weekly_report(self):
        """Wöchentlicher automatischer Bericht"""
        channel_id = int(os.getenv('REPORT_CHANNEL_ID', 0))
        if channel_id:
            channel = self.get_channel(channel_id)
            if channel:
                embed = await generate_weekly_stats()
                await channel.send(embed=embed)
    
    @tasks.loop(minutes=5)
    async def plantation_update_loop(self):
        """Update Plantagen Status alle 5 Minuten"""
        await self.update_all_plantations()

bot = LogBot()

# ==================== PERMISSION CHECK ====================

def has_payout_permission():
    """Check ob User Auszahlungs-Berechtigung hat"""
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        user_role_ids = [role.id for role in interaction.user.roles]
        for role_id in PAYOUT_ROLE_IDS:
            if role_id in user_role_ids:
                return True
        return False
    return app_commands.check(predicate)

# ==================== PLANTAGEN HELPER FUNCTIONS ====================

async def create_plantation(user_id: int, username: str) -> bool:
    """Erstelle neue Plantage in Sheets"""
    if not bot.sheets_service:
        return False
    
    try:
        existing = await get_user_plantation(user_id)
        if existing and existing['status'] == 'Aktiv':
            return False
        
        sheet = bot.sheets_service.spreadsheets()
        now = datetime.now()
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
        next_fertilize = calculate_next_fertilize_window(now)
        
        values = [[
            str(user_id),
            username,
            timestamp,
            PLANTATION_DURATION,
            timestamp,
            timestamp,
            'Aktiv',
            '',
            next_fertilize.strftime("%d.%m.%Y %H:%M")
        ]]
        
        body = {'values': values}
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='🌱 Plantagen!A:I',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ Plantage erstellt: {username}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Plantage: {e}")
        return False

def calculate_next_fertilize_window(from_time: datetime) -> datetime:
    """Berechne nächstes Düngen-Fenster (X:30)"""
    minute = from_time.minute
    if minute < 30:
        next_window = from_time.replace(minute=30, second=0, microsecond=0)
    else:
        next_hour = from_time + timedelta(hours=1)
        next_window = next_hour.replace(minute=30, second=0, microsecond=0)
    return next_window

def is_in_fertilize_window(now: datetime) -> bool:
    """Check ob JETZT im Düngen-Fenster (X:30 bis X+1:00 = 30min)"""
    minute = now.minute
    return 30 <= minute < 60

async def get_user_plantation(user_id: int) -> Optional[Dict]:
    """Hole aktive Plantage eines Users"""
    if not bot.sheets_service:
        return None
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='🌱 Plantagen!A2:I'
        ).execute()
        
        values = result.get('values', [])
        
        for i, row in enumerate(values):
            if len(row) >= 7:
                if row[0] == str(user_id) and row[6] == 'Aktiv':
                    return {
                        'row_index': i + 2,
                        'user_id': row[0],
                        'username': row[1],
                        'started_at': row[2],
                        'countdown': int(row[3]) if row[3] else PLANTATION_DURATION,
                        'last_check': row[4],
                        'last_fertilize': row[5],
                        'status': row[6],
                        'finished_at': row[7] if len(row) > 7 else '',
                        'next_fertilize': row[8] if len(row) > 8 else ''
                    }
        return None
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Plantage: {e}")
        return None

async def update_plantation_countdown(plantation: Dict, fertilized: bool = False) -> bool:
    """Update Plantagen-Countdown"""
    if not bot.sheets_service:
        return False
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        now = datetime.now()
        last_check = datetime.strptime(plantation['last_check'], "%d.%m.%Y %H:%M:%S")
        last_fertilize = datetime.strptime(plantation['last_fertilize'], "%d.%m.%Y %H:%M:%S")
        
        elapsed = (now - last_check).total_seconds()
        current_countdown = plantation['countdown']
        
        # Letzte volle Stunde berechnen
        last_full_hour = last_fertilize.replace(minute=0, second=0, microsecond=0)
        if last_fertilize.minute >= 30:
            last_full_hour += timedelta(hours=1)
        
        # Check ob gedüngt werden musste
        hours_since_last_fertilize = (now - last_fertilize).total_seconds() / 3600
        
        if fertilized or hours_since_last_fertilize < 1:
            # Countdown läuft normal
            new_countdown = max(0, current_countdown - int(elapsed))
        else:
            # Countdown bleibt bei letzter voller Stunde
            time_to_last_hour = (last_full_hour - datetime.strptime(plantation['started_at'], "%d.%m.%Y %H:%M:%S")).total_seconds()
            new_countdown = max(0, PLANTATION_DURATION - int(time_to_last_hour))
        
        # Update in Sheets
        update_data = [[
            new_countdown,
            now.strftime("%d.%m.%Y %H:%M:%S"),
            plantation['last_fertilize'] if not fertilized else now.strftime("%d.%m.%Y %H:%M:%S"),
            'Aktiv' if new_countdown > 0 else 'Fertig',
            '' if new_countdown > 0 else now.strftime("%d.%m.%Y %H:%M:%S"),
            calculate_next_fertilize_window(now).strftime("%d.%m.%Y %H:%M")
        ]]
        
        body = {'values': update_data}
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'🌱 Plantagen!D{plantation["row_index"]}:I{plantation["row_index"]}',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        if new_countdown <= 0:
            await send_harvest_notification(plantation)
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Update: {e}")
        return False

async def fertilize_plantation(user_id: int) -> Tuple[bool, str]:
    """Dünge Plantage - nur im richtigen Zeitfenster"""
    plantation = await get_user_plantation(user_id)
    
    if not plantation:
        return False, "Du hast keine aktive Plantage!"
    
    now = datetime.now()
    
    if not is_in_fertilize_window(now):
        next_window = calculate_next_fertilize_window(now)
        return False, f"🕐 Düngen nur von X:30 bis X+1:00 möglich!\nNächstes Fenster: {next_window.strftime('%H:%M')}"
    
    success = await update_plantation_countdown(plantation, fertilized=True)
    
    if success:
        return True, "✅ Plantage gedüngt! Countdown läuft weiter."
    else:
        return False, "❌ Fehler beim Düngen."

async def send_harvest_notification(plantation: Dict):
    """Sende @here Nachricht wenn Plantage fertig"""
    channel_id = int(os.getenv('PLANTAGEN_ERNTE_CHANNEL_ID', 0))
    if not channel_id:
        return
    
    channel = bot.get_channel(channel_id)
    if not channel:
        return
    
    embed = discord.Embed(
        title="🌱 PLANTAGE FERTIG!",
        description=f"**{plantation['username']}** kann jetzt ernten! 🎉",
        color=COLORS['green']
    )
    
    embed.add_field(name="👤 Farmer", value=f"<@{plantation['user_id']}>", inline=True)
    embed.add_field(name="⏱️ Dauer", value="8 Stunden", inline=True)
    embed.add_field(name="💰 Bonus", value=f"**{PLANTATION_HARVEST_REWARD:.2f}€**", inline=True)
    embed.add_field(
        name="📋 Nächste Schritte",
        value="1️⃣ Reagiere mit ✅\n2️⃣ Ernte + Flieg\n3️⃣ Warte auf Auszahlung",
        inline=False
    )
    embed.set_footer(text="Metallic Purple Edition • Ananas-Plantagen")
    
    msg = await channel.send("@here", embed=embed)
    await msg.add_reaction("✅")

async def update_all_plantations():
    """Update alle aktiven Plantagen"""
    if not bot.sheets_service:
        return
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='🌱 Plantagen!A2:I'
        ).execute()
        
        values = result.get('values', [])
        
        for i, row in enumerate(values):
            if len(row) >= 7 and row[6] == 'Aktiv':
                plantation = {
                    'row_index': i + 2,
                    'user_id': row[0],
                    'username': row[1],
                    'started_at': row[2],
                    'countdown': int(row[3]) if row[3] else PLANTATION_DURATION,
                    'last_check': row[4],
                    'last_fertilize': row[5],
                    'status': row[6],
                    'finished_at': row[7] if len(row) > 7 else '',
                    'next_fertilize': row[8] if len(row) > 8 else ''
                }
                await update_plantation_countdown(plantation, fertilized=False)
    except Exception as e:
        print(f"❌ Fehler beim Plantagen-Update: {e}")

def format_countdown(seconds: int) -> str:
    """Formatiere Sekunden zu lesbarem Countdown"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# ==================== STANDARD HELPER FUNCTIONS ====================

async def get_total_log_count() -> int:
    """Hole die Gesamtanzahl aller Logs"""
    if not bot.sheets_service:
        return 0
    try:
        sheet = bot.sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Logs!A2:A').execute()
        values = result.get('values', [])
        return len(values)
    except Exception as e:
        print(f"❌ Fehler beim Zählen der Logs: {e}")
        return 0

def create_progress_bar(current: int, target: int, length: int = 20) -> str:
    """Erstellt eine visuelle Progress Bar"""
    if target == 0:
        return "░" * length
    percentage = min(current / target, 1.0)
    filled = int(length * percentage)
    empty = length - filled
    return "▓" * filled + "░" * empty

async def get_all_users_with_earnings() -> List[Dict]:
    """Hole alle User mit offenen Guthaben für diese Woche"""
    if not bot.sheets_service:
        return []
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        week_key = f"KW{current_week}/{current_year}"
        
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Logs!A2:H').execute()
        values = result.get('values', [])
        
        user_stats = {}
        
        for row in values:
            if len(row) >= 7 and row[1] == week_key:
                user_id = row[3]
                username = row[2]
                action = row[4]
                amount = float(row[6])
                
                if user_id not in user_stats:
                    user_stats[user_id] = {
                        'user_id': user_id,
                        'username': username,
                        'total': 0,
                        'logs': 0,
                        'breakdown': {a: 0 for a in PAYMENT_AMOUNTS.keys()}
                    }
                
                user_stats[user_id]['total'] += amount
                user_stats[user_id]['logs'] += 1
                if action in user_stats[user_id]['breakdown']:
                    user_stats[user_id]['breakdown'][action] += 1
        
        users = list(user_stats.values())
        users.sort(key=lambda x: x['total'], reverse=True)
        return users
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der User-Earnings: {e}")
        return []

async def get_user_week_earnings(user_id: int) -> Dict:
    """Hole detaillierte Wochen-Statistiken für einen User"""
    if not bot.sheets_service:
        return {'total': 0, 'logs': 0, 'breakdown': {}, 'week': '', 'row_indices': []}
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        week_key = f"KW{current_week}/{current_year}"
        
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Logs!A2:H').execute()
        values = result.get('values', [])
        
        total_earnings = 0
        log_count = 0
        breakdown = {action: 0 for action in PAYMENT_AMOUNTS.keys()}
        row_indices = []
        
        for i, row in enumerate(values):
            if len(row) >= 7 and row[1] == week_key and row[3] == str(user_id):
                action = row[4]
                amount = float(row[6])
                total_earnings += amount
                log_count += 1
                row_indices.append(i + 2)
                if action in breakdown:
                    breakdown[action] += 1
        
        return {
            'total': total_earnings,
            'logs': log_count,
            'breakdown': breakdown,
            'week': week_key,
            'row_indices': row_indices
        }
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Earnings: {e}")
        return {'total': 0, 'logs': 0, 'breakdown': {}, 'week': '', 'row_indices': []}

async def save_log(user: discord.Member, action_type: str, description: str, image_url: str) -> bool:
    """Speichere Log in Google Sheets"""
    if not bot.sheets_service:
        return False
    
    try:
        if action_type == 'Plantage gesät':
            success = await create_plantation(user.id, user.name)
            if not success:
                return False
        
        if action_type == 'Düngen':
            plantation = await get_user_plantation(user.id)
            if plantation:
                fertilize_success, msg = await fertilize_plantation(user.id)
        
        sheet = bot.sheets_service.spreadsheets()
        now = datetime.now()
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
        week_number = now.isocalendar()[1]
        year = now.year
        amount = PAYMENT_AMOUNTS.get(action_type, 0)
        
        values = [[
            timestamp,
            f"KW{week_number}/{year}",
            user.name,
            str(user.id),
            action_type,
            description,
            amount,
            image_url
        ]]
        
        body = {'values': values}
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A:H',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ Log gespeichert: {user.name} - {action_type}")
        return True
    except HttpError as error:
        print(f"❌ Google Sheets Fehler: {error}")
        return False

async def save_payout(user_id: str, username: str, amount: float, week: str, log_count: int, admin_name: str) -> bool:
    """Speichere Auszahlung in Google Sheets"""
    if not bot.sheets_service:
        return False
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        now = datetime.now()
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
        
        values = [[timestamp, week, username, str(user_id), amount, log_count, "Ausgezahlt", admin_name]]
        body = {'values': values}
        
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Auszahlungen!A:H',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ Auszahlung gespeichert: {username} - {amount}€")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Auszahlung: {e}")
        return False

async def archive_user_logs(user_id: int, week: str) -> bool:
    """Verschiebe User-Logs ins Archiv"""
    if not bot.sheets_service:
        return False
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Logs!A2:H').execute()
        values = result.get('values', [])
        
        logs_to_archive = []
        rows_to_delete = []
        
        for i, row in enumerate(values):
            if len(row) >= 7 and row[1] == week and row[3] == str(user_id):
                archived_row = row + [datetime.now().strftime("%d.%m.%Y %H:%M:%S")]
                logs_to_archive.append(archived_row)
                rows_to_delete.append(i + 2)
        
        if not logs_to_archive:
            return True
        
        body = {'values': logs_to_archive}
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Archiv!A:I',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        rows_to_delete.sort(reverse=True)
        
        spreadsheet = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        logs_sheet_id = None
        for s in spreadsheet.get('sheets', []):
            if s['properties']['title'] == 'Logs':
                logs_sheet_id = s['properties']['sheetId']
                break
        
        if logs_sheet_id is not None:
            requests = []
            for row_idx in rows_to_delete:
                requests.append({
                    'deleteDimension': {
                        'range': {
                            'sheetId': logs_sheet_id,
                            'dimension': 'ROWS',
                            'startIndex': row_idx - 1,
                            'endIndex': row_idx
                        }
                    }
                })
            
            if requests:
                body = {'requests': requests}
                sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        
        print(f"✅ {len(logs_to_archive)} Logs archiviert für User {user_id}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Archivieren: {e}")
        return False

async def get_user_stats(user_id: int) -> dict:
    """Hole Statistiken für einen User (aktuelle Woche)"""
    if not bot.sheets_service:
        return {}
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        week_key = f"KW{current_week}/{current_year}"
        
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Logs!A2:H').execute()
        values = result.get('values', [])
        
        stats = {action: 0 for action in PAYMENT_AMOUNTS.keys()}
        
        for row in values:
            if len(row) >= 5 and row[1] == week_key and row[3] == str(user_id):
                action = row[4]
                if action in stats:
                    stats[action] += 1
        
        return stats
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Stats: {e}")
        return {}

async def generate_weekly_stats() -> discord.Embed:
    """Generiere wöchentlichen Gesamtbericht"""
    if not bot.sheets_service:
        return discord.Embed(title="Fehler", description="Keine Verbindung zu Sheets")
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        week_key = f"KW{current_week}/{current_year}"
        
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Logs!A2:H').execute()
        values = result.get('values', [])
        
        user_earnings = {}
        action_counts = {action: 0 for action in PAYMENT_AMOUNTS.keys()}
        
        for row in values:
            if len(row) >= 7 and row[1] == week_key:
                username = row[2]
                action = row[4]
                amount = float(row[6])
                
                if username not in user_earnings:
                    user_earnings[username] = 0
                user_earnings[username] += amount
                
                if action in action_counts:
                    action_counts[action] += 1
        
        embed = discord.Embed(
            title="",
            color=COLORS['primary'],
            timestamp=datetime.utcnow()
        )
        
        embed.set_author(
            name=f"📊 Wöchentlicher Bericht - {week_key}",
            icon_url=bot.user.display_avatar.url
        )
        
        sorted_users = sorted(user_earnings.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_users:
            top_10 = sorted_users[:10]
            medals = ["🥇", "🥈", "🥉"]
            top_earners_text = ""
            for i, (user, amount) in enumerate(top_10):
                medal = medals[i] if i < 3 else f"`{i+1}.`"
                top_earners_text += f"{medal} **{user}**: `{amount:.2f}€`\n"
            
            embed.add_field(name="💎 Top 10 Verdiener", value=top_earners_text, inline=False)
        
        action_emojis = {
            'Düngen': '🌱',
            'Reparieren': '🔧',
            'Panel platziert': '⚡',
            'Plantage gesät': '🌾'
        }
        
        action_stats = ""
        for action, count in action_counts.items():
            emoji = action_emojis.get(action, '📌')
            action_stats += f"{emoji} **{action}**: `{count}x`\n"
        
        embed.add_field(name="📋 Aktionen Breakdown", value=action_stats if action_stats else "Keine Aktionen", inline=True)
        
        total = sum(user_earnings.values())
        total_logs = sum(action_counts.values())
        summary = f"💵 **{total:.2f}€**\n📊 **{total_logs}** Logs"
        embed.add_field(name="💼 Gesamt", value=summary, inline=True)
        
        embed.set_footer(text=f"Generiert am {datetime.now().strftime('%d.%m.%Y um %H:%M')} Uhr • Metallic Purple Edition + Plantagen")
        
        return embed
    except Exception as e:
        print(f"❌ Fehler beim Generieren des Berichts: {e}")
        return discord.Embed(title="❌ Fehler", description=str(e), color=COLORS['danger'])

# ==================== UI COMPONENTS ====================

class ActionSelect(discord.ui.Select):
    """Dropdown für Aktionsauswahl"""
    def __init__(self):
        options = [
            discord.SelectOption(label="Düngen", description=f"Auszahlung: {PAYMENT_AMOUNTS['Düngen']}€", emoji="🌱"),
            discord.SelectOption(label="Reparieren", description=f"Auszahlung: {PAYMENT_AMOUNTS['Reparieren']}€", emoji="🔧"),
            discord.SelectOption(label="Panel platziert", description=f"Auszahlung: {PAYMENT_AMOUNTS['Panel platziert']}€", emoji="⚡"),
            discord.SelectOption(label="Plantage gesät", description=f"Auszahlung: {PAYMENT_AMOUNTS['Plantage gesät']}€ + 8h Countdown", emoji="🌾")
        ]
        super().__init__(placeholder="💜 Wähle eine Aktion...", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        action = self.values[0]
        
        if action == 'Plantage gesät':
            existing = await get_user_plantation(interaction.user.id)
            if existing and existing['status'] == 'Aktiv':
                await interaction.response.send_message("❌ Du hast bereits eine aktive Plantage!", ephemeral=True)
                return
        
        await interaction.response.send_modal(LogModal(action_type=action))

class LogModal(discord.ui.Modal):
    """Modal für Log-Details und Bildbeweis"""
    def __init__(self, action_type: str):
        super().__init__(title=f"Log: {action_type}")
        self.action_type = action_type
        
        self.description = discord.ui.TextInput(
            label="Beschreibung",
            placeholder="Kurze Beschreibung der durchgeführten Aktion...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Wenn Modal abgeschickt wird"""
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="📸 Bitte Bild hochladen",
            description=f"**Aktion:** {self.action_type}\n"
                       f"**Beschreibung:** {self.description.value}\n\n"
                       f"Bitte lade jetzt ein Bild als Beweis hoch.\n"
                       f"Du hast 60 Sekunden Zeit.",
            color=COLORS['accent']
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        def check(m):
            return (m.author.id == interaction.user.id and len(m.attachments) > 0 and m.channel.id == interaction.channel.id)
        
        try:
            message = await bot.wait_for('message', timeout=60.0, check=check)
            image_url = message.attachments[0].url
            
            success = await save_log(
                user=interaction.user,
                action_type=self.action_type,
                description=self.description.value,
                image_url=image_url
            )
            
            if success:
                amount = PAYMENT_AMOUNTS[self.action_type]
                
                confirmation = discord.Embed(title="", color=COLORS['success'], timestamp=datetime.utcnow())
                confirmation.set_author(name="✅ Log erfolgreich eingetragen", icon_url=interaction.user.display_avatar.url)
                confirmation.add_field(name="🎯 Aktion", value=f"**{self.action_type}**", inline=True)
                confirmation.add_field(name="💎 Auszahlung", value=f"**{amount:.2f}€**", inline=True)
                confirmation.add_field(name="\u200b", value="\u200b", inline=True)
                confirmation.add_field(name="📝 Beschreibung", value=f"```{self.description.value}```", inline=False)
                
                if self.action_type == 'Plantage gesät':
                    confirmation.add_field(
                        name="🌱 Plantagen-Info",
                        value="⏱️ 8 Stunden Countdown gestartet!\n🌾 Dünge jede halbe Stunde (X:30-X+1:00)\n💰 Bonus bei Ernte: 50€",
                        inline=False
                    )
                
                confirmation.set_thumbnail(url=image_url)
                confirmation.set_footer(text=f"Eingereicht von {interaction.user.name} • Metallic Purple Edition")
                
                await interaction.followup.send(embed=confirmation, ephemeral=True)
                
                # OUTPUT CHANNEL
                output_channel_id = os.getenv('LOG_OUTPUT_CHANNEL_ID', '')
                if output_channel_id:
                    output_channel = bot.get_channel(int(output_channel_id))
                    if output_channel:
                        action_emojis = {'Düngen': '🌱', 'Reparieren': '🔧', 'Panel platziert': '⚡', 'Plantage gesät': '🌾'}
                        
                        premium_embed = discord.Embed(title="", color=COLORS['primary'], timestamp=datetime.utcnow())
                        premium_embed.set_author(name="📋 Neuer Log-Eintrag", icon_url=bot.user.display_avatar.url)
                        premium_embed.add_field(name="👤 Mitglied", value=f"{interaction.user.mention}\n`{interaction.user.name}`", inline=True)
                        
                        action_emoji = action_emojis.get(self.action_type, '📌')
                        premium_embed.add_field(name="🎯 Aktion", value=f"{action_emoji} **{self.action_type}**", inline=True)
                        premium_embed.add_field(name="💎 Auszahlung", value=f"**{amount:.2f}€**", inline=True)
                        premium_embed.add_field(name="📝 Beschreibung", value=f"```\n{self.description.value}\n```", inline=False)
                        
                        now = datetime.now()
                        week_number = now.isocalendar()[1]
                        premium_embed.add_field(name="📅 Kalenderwoche", value=f"KW {week_number}/{now.year}", inline=True)
                        premium_embed.add_field(name="🕐 Uhrzeit", value=now.strftime("%H:%M:%S"), inline=True)
                        premium_embed.add_field(name="\u200b", value="\u200b", inline=True)
                        
                        user_stats = await get_user_week_earnings(interaction.user.id)
                        total_logs = user_stats['logs']
                        if total_logs > 0:
                            progress_bar = create_progress_bar(total_logs, 50)
                            premium_embed.add_field(name="📊 Wochen-Fortschritt (Ziel: 50 Logs)", value=f"{progress_bar} `{total_logs}/50`", inline=False)
                        
                        premium_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                        premium_embed.set_image(url=image_url)
                        
                        log_count = await get_total_log_count()
                        premium_embed.set_footer(text=f"Log #{log_count} • Metallic Purple Edition + Plantagen", icon_url=bot.user.display_avatar.url)
                        
                        await output_channel.send(embed=premium_embed)
                        print(f"✅ Premium Log gepostet in: {output_channel.name}")
            else:
                error_embed = discord.Embed(
                    title="❌ Fehler",
                    description="Log konnte nicht gespeichert werden. Bitte kontaktiere einen Admin.",
                    color=COLORS['danger']
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏱️ Zeit abgelaufen",
                description="Du hast zu lange gebraucht. Bitte versuche es erneut.",
                color=COLORS['warning']
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)

class LogView(discord.ui.View):
    """Hauptansicht mit Buttons"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ActionSelect())
    
    @discord.ui.button(label="Meine Statistiken", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="stats_button")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Zeige persönliche Statistiken"""
        await interaction.response.defer(ephemeral=True)
        
        user_stats = await get_user_week_earnings(interaction.user.id)
        
        embed = discord.Embed(title="", color=COLORS['chrome'], timestamp=datetime.utcnow())
        embed.set_author(name=f"📊 Deine Statistiken - {user_stats['week']}", icon_url=interaction.user.display_avatar.url)
        
        action_emojis = {'Düngen': '🌱', 'Reparieren': '🔧', 'Panel platziert': '⚡', 'Plantage gesät': '🌾'}
        
        for action, count in user_stats['breakdown'].items():
            if count > 0 and action in PAYMENT_AMOUNTS:
                emoji = action_emojis.get(action, '📌')
                earnings = count * PAYMENT_AMOUNTS[action]
                embed.add_field(name=f"{emoji} {action}", value=f"Anzahl: **{count}**\nVerdienst: **{earnings:.2f}€**", inline=True)
        
        embed.add_field(name="💎 Gesamtverdienst (diese Woche)", value=f"**{user_stats['total']:.2f}€**", inline=False)
        
        if user_stats['logs'] > 0:
            progress = create_progress_bar(user_stats['logs'], 50)
            embed.add_field(name="📊 Fortschritt (Ziel: 50 Logs)", value=f"{progress} `{user_stats['logs']}/50`", inline=False)
        
        plantation = await get_user_plantation(interaction.user.id)
        if plantation:
            countdown = plantation['countdown']
            hours = countdown // 3600
            minutes = (countdown % 3600) // 60
            embed.add_field(
                name="🌱 Aktive Plantage",
                value=f"⏱️ **{hours}h {minutes}m** verbleibend\n🕐 Nächstes Düngen: {plantation.get('next_fertilize', 'Berechne...')}",
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Statistiken werden live aktualisiert • Metallic Purple Edition")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

# ==================== PAYOUT PANEL COMPONENTS ====================

class PayoutUserSelect(discord.ui.Select):
    """Dropdown für User-Auswahl im Auszahlungs-Panel"""
    def __init__(self, users: List[Dict]):
        self.users_data = users
        
        options = []
        for user in users[:25]:
            options.append(
                discord.SelectOption(
                    label=f"{user['username']}",
                    description=f"💎 {user['total']:.2f}€ • {user['logs']} Logs",
                    value=user['user_id'],
                    emoji="👤"
                )
            )
        
        if not options:
            options.append(discord.SelectOption(label="Keine User verfügbar", value="none"))
        
        super().__init__(placeholder="👤 User für Auszahlung auswählen...", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("❌ Keine User verfügbar.", ephemeral=True)
            return
        
        user_id = self.values[0]
        user_data = next((u for u in self.users_data if u['user_id'] == user_id), None)
        
        if not user_data:
            await interaction.response.send_message("❌ User nicht gefunden.", ephemeral=True)
            return
        
        view = PayoutConfirmView(user_data, interaction.user)
        
        embed = discord.Embed(
            title="💎 Auszahlung bestätigen",
            description=f"Möchtest du **{user_data['username']}** auszahlen?",
            color=COLORS['accent']
        )
        
        embed.add_field(name="💰 Betrag", value=f"**{user_data['total']:.2f}€**", inline=True)
        embed.add_field(name="📊 Logs", value=f"**{user_data['logs']}**", inline=True)
        
        action_emojis = {'Düngen': '🌱', 'Reparieren': '🔧', 'Panel platziert': '⚡', 'Plantage gesät': '🌾'}
        breakdown_text = ""
        for action, count in user_data['breakdown'].items():
            if count > 0:
                emoji = action_emojis.get(action, '📌')
                breakdown_text += f"{emoji} {action}: **{count}x**\n"
        
        if breakdown_text:
            embed.add_field(name="📋 Breakdown", value=breakdown_text, inline=False)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PayoutConfirmView(discord.ui.View):
    """Bestätigungs-View für Einzelauszahlung"""
    def __init__(self, user_data: Dict, admin: discord.Member):
        super().__init__(timeout=60)
        self.user_data = user_data
        self.admin = admin
    
    @discord.ui.button(label="✅ Auszahlen", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        success = await process_single_payout(self.user_data, interaction.guild, self.admin)
        
        if success:
            embed = discord.Embed(
                title="✅ Auszahlung erfolgreich!",
                description=f"**{self.user_data['username']}** wurde **{self.user_data['total']:.2f}€** ausgezahlt.",
                color=COLORS['success']
            )
            embed.add_field(name="📊 Logs archiviert", value=f"**{self.user_data['logs']}**", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Fehler bei der Auszahlung.", ephemeral=True)
        
        self.stop()
    
    @discord.ui.button(label="❌ Abbrechen", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Auszahlung abgebrochen.", ephemeral=True)
        self.stop()

class PayoutAllConfirmView(discord.ui.View):
    """Bestätigungs-View für Alle Auszahlen"""
    def __init__(self, users: List[Dict], admin: discord.Member, guild: discord.Guild):
        super().__init__(timeout=120)
        self.users = users
        self.admin = admin
        self.guild = guild
    
    @discord.ui.button(label="✅ JA, ALLE AUSZAHLEN", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        total_amount = sum(u['total'] for u in self.users)
        total_users = len(self.users)
        
        progress_embed = discord.Embed(
            title="⏳ Auszahlungen werden verarbeitet...",
            description=f"0 / {total_users} User",
            color=COLORS['accent']
        )
        progress_msg = await interaction.followup.send(embed=progress_embed, ephemeral=True)
        
        success_count = 0
        failed_count = 0
        
        for i, user_data in enumerate(self.users):
            success = await process_single_payout(user_data, self.guild, self.admin)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            if (i + 1) % 3 == 0 or i == total_users - 1:
                progress_embed.description = f"{i + 1} / {total_users} User verarbeitet..."
                await progress_msg.edit(embed=progress_embed)
            
            await asyncio.sleep(0.5)
        
        final_embed = discord.Embed(title="✅ Alle Auszahlungen abgeschlossen!", color=COLORS['success'], timestamp=datetime.utcnow())
        final_embed.add_field(name="✅ Erfolgreich", value=f"**{success_count}**", inline=True)
        final_embed.add_field(name="❌ Fehlgeschlagen", value=f"**{failed_count}**", inline=True)
        final_embed.add_field(name="💎 Gesamtbetrag", value=f"**{total_amount:.2f}€**", inline=True)
        
        await progress_msg.edit(embed=final_embed)
        self.stop()
    
    @discord.ui.button(label="❌ ABBRECHEN", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Auszahlung abgebrochen.", ephemeral=True)
        self.stop()

class PayoutPanelView(discord.ui.View):
    """Hauptansicht für das Auszahlungs-Panel"""
    def __init__(self, users: List[Dict]):
        super().__init__(timeout=300)
        self.users = users
        if users:
            self.add_item(PayoutUserSelect(users))
    
    @discord.ui.button(label="💎 Alle Auszahlen", style=discord.ButtonStyle.primary, emoji="💰", row=1)
    async def payout_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.users:
            await interaction.response.send_message("❌ Keine User mit offenem Guthaben.", ephemeral=True)
            return
        
        total_amount = sum(u['total'] for u in self.users)
        total_users = len(self.users)
        
        embed = discord.Embed(
            title="⚠️ ALLE AUSZAHLEN - BESTÄTIGUNG",
            description=(
                f"Du bist dabei, **{total_users} User** auszuzahlen.\n\n"
                f"💎 **Gesamtbetrag:** {total_amount:.2f}€\n\n"
                f"Diese Aktion kann nicht rückgängig gemacht werden!\n"
                f"Alle Logs werden ins Archiv verschoben."
            ),
            color=COLORS['warning']
        )
        
        view = PayoutAllConfirmView(self.users, interaction.user, interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🔄 Aktualisieren", style=discord.ButtonStyle.secondary, emoji="🔄", row=1)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        users = await get_all_users_with_earnings()
        
        if not users:
            embed = discord.Embed(
                title="💜 Auszahlungs-Panel",
                description="✅ Keine offenen Auszahlungen vorhanden.",
                color=COLORS['primary']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = create_payout_panel_embed(users)
        view = PayoutPanelView(users)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="❌ Schließen", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Panel geschlossen.", ephemeral=True)
        self.stop()

async def process_single_payout(user_data: Dict, guild: discord.Guild, admin: discord.Member) -> bool:
    """Führe eine einzelne Auszahlung durch"""
    try:
        user_id = int(user_data['user_id'])
        week = user_data.get('week', f"KW{datetime.now().isocalendar()[1]}/{datetime.now().year}")
        
        member = guild.get_member(user_id)
        
        if member:
            try:
                dm_embed = discord.Embed(title="", color=COLORS['gold'], timestamp=datetime.utcnow())
                dm_embed.set_author(name="💎 AUSZAHLUNG ERFOLGREICH", icon_url=guild.icon.url if guild.icon else None)
                dm_embed.description = f"Hallo **{member.display_name}**!\n\nDeine Auszahlung wurde veranlasst:"
                dm_embed.add_field(name="📅 Zeitraum", value=f"**{week}**", inline=True)
                dm_embed.add_field(name="💎 Betrag", value=f"**{user_data['total']:.2f}€**", inline=True)
                dm_embed.add_field(name="📋 Logs", value=f"**{user_data['logs']}**", inline=True)
                
                action_emojis = {'Düngen': '🌱', 'Reparieren': '🔧', 'Panel platziert': '⚡', 'Plantage gesät': '🌾'}
                breakdown_text = ""
                for action, count in user_data['breakdown'].items():
                    if count > 0:
                        emoji = action_emojis.get(action, '📌')
                        earnings = count * PAYMENT_AMOUNTS.get(action, 0)
                        breakdown_text += f"{emoji} **{action}**: {count}x (**{earnings:.2f}€**)\n"
                
                if breakdown_text:
                    dm_embed.add_field(name="📊 Breakdown", value=breakdown_text, inline=False)
                
                dm_embed.add_field(
                    name="🎉 Status",
                    value="Dein Guthaben wurde zurückgesetzt.\n**Viel Erfolg in der neuen Woche!** 🚀",
                    inline=False
                )
                
                dm_embed.set_thumbnail(url=member.display_avatar.url)
                dm_embed.set_footer(text="Metallic Purple Edition • Auszahlung")
                
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                print(f"⚠️ Konnte DM nicht senden an {user_data['username']}")
        
        await save_payout(
            user_id=user_data['user_id'],
            username=user_data['username'],
            amount=user_data['total'],
            week=week,
            log_count=user_data['logs'],
            admin_name=admin.name
        )
        
        await archive_user_logs(user_id, week)
        
        return True
    except Exception as e:
        print(f"❌ Fehler bei Auszahlung für {user_data['username']}: {e}")
        return False

def create_payout_panel_embed(users: List[Dict]) -> discord.Embed:
    """Erstelle das Auszahlungs-Panel Embed"""
    current_week = datetime.now().isocalendar()[1]
    current_year = datetime.now().year
    week_key = f"KW{current_week}/{current_year}"
    
    embed = discord.Embed(title="", color=COLORS['primary'], timestamp=datetime.utcnow())
    embed.set_author(name=f"💎 AUSZAHLUNGS-PANEL • {week_key}", icon_url=bot.user.display_avatar.url)
    
    if not users:
        embed.description = "✅ Keine offenen Auszahlungen vorhanden."
        return embed
    
    user_list = ""
    total_amount = 0
    total_logs = 0
    
    for i, user in enumerate(users[:10], 1):
        medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"`{i}.`"))
        user_list += f"{medal} **{user['username']}** │ {user['logs']} Logs │ **{user['total']:.2f}€**\n"
        total_amount += user['total']
        total_logs += user['logs']
    
    if len(users) > 10:
        user_list += f"\n*... und {len(users) - 10} weitere User*"
    
    embed.add_field(name="👥 User mit offenem Guthaben", value=user_list if user_list else "Keine", inline=False)
    embed.add_field(name="👥 Gesamt User", value=f"**{len(users)}**", inline=True)
    embed.add_field(name="📊 Gesamt Logs", value=f"**{total_logs}**", inline=True)
    embed.add_field(name="💎 Gesamt Betrag", value=f"**{total_amount:.2f}€**", inline=True)
    
    embed.set_footer(text="Wähle einen User aus oder zahle alle auf einmal aus • Metallic Purple Edition")
    
    return embed

# ==================== PLANTAGEN COMMANDS ====================

@bot.tree.command(name="plantage", description="Plantagen-Verwaltung")
@app_commands.describe(aktion="Was möchtest du tun?")
@app_commands.choices(aktion=[
    app_commands.Choice(name="📊 Status anzeigen", value="status"),
    app_commands.Choice(name="📋 Alle Plantagen (Admin)", value="liste")
])
async def plantage_command(interaction: discord.Interaction, aktion: str):
    """Plantagen-Management"""
    
    if aktion == "status":
        await interaction.response.defer(ephemeral=True)
        
        plantation = await get_user_plantation(interaction.user.id)
        
        if not plantation:
            await interaction.followup.send(
                "❌ Du hast keine aktive Plantage!\n💡 Nutze `/log` → 'Plantage gesät' um eine zu starten.",
                ephemeral=True
            )
            return
        
        countdown = plantation['countdown']
        hours = countdown // 3600
        minutes = (countdown % 3600) // 60
        seconds = countdown % 60
        
        embed = discord.Embed(title="🌱 Deine Ananas-Plantage", color=COLORS['green'])
        embed.add_field(name="⏱️ Verbleibende Zeit", value=f"**{hours:02d}:{minutes:02d}:{seconds:02d}**", inline=True)
        embed.add_field(name="🕐 Nächstes Düngen", value=plantation.get('next_fertilize', 'Berechne...'), inline=True)
        embed.add_field(name="📅 Gestartet am", value=plantation['started_at'], inline=True)
        
        progress = create_progress_bar(PLANTATION_DURATION - countdown, PLANTATION_DURATION, 30)
        embed.add_field(name="📊 Fortschritt", value=f"{progress}", inline=False)
        
        embed.add_field(
            name="ℹ️ Info",
            value="🌾 Dünge alle halbe Stunde (X:30-X+1:00)\n⏸️ Countdown pausiert wenn nicht gedüngt\n"
                  f"💰 Bonus bei Ernte: **{PLANTATION_HARVEST_REWARD:.2f}€**",
            inline=False
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Metallic Purple Edition • Ananas-Plantagen")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    elif aktion == "liste":
        # Check Berechtigung (Admin + konfigurierte Rollen)
        has_permission = interaction.user.guild_permissions.administrator
        if not has_permission:
            user_role_ids = [role.id for role in interaction.user.roles]
            for role_id in PAYOUT_ROLE_IDS:
                if role_id in user_role_ids:
                    has_permission = True
                    break
        
        if not has_permission:
            await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        if not bot.sheets_service:
            await interaction.followup.send("❌ Keine Sheets-Verbindung!", ephemeral=True)
            return
        
        try:
            sheet = bot.sheets_service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='🌱 Plantagen!A2:I').execute()
            values = result.get('values', [])
            
            active_plantations = [row for row in values if len(row) >= 7 and row[6] == 'Aktiv']
            
            if not active_plantations:
                await interaction.followup.send("✅ Keine aktiven Plantagen.", ephemeral=True)
                return
            
            embed = discord.Embed(title="🌱 Alle aktiven Plantagen", color=COLORS['green'])
            
            for row in active_plantations[:10]:
                username = row[1]
                countdown = int(row[3]) if row[3] else 0
                hours = countdown // 3600
                minutes = (countdown % 3600) // 60
                
                embed.add_field(
                    name=f"👤 {username}",
                    value=f"⏱️ **{hours}h {minutes}m**\n🕐 Nächstes Düngen: {row[8] if len(row) > 8 else 'N/A'}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Fehler: {e}", ephemeral=True)

# ==================== EVENT HANDLER ====================

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Handle Ernte-Reaktionen"""
    if payload.emoji.name != "✅":
        return
    
    ernte_channel_id = int(os.getenv('PLANTAGEN_ERNTE_CHANNEL_ID', 0))
    if payload.channel_id != ernte_channel_id:
        return
    
    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return
    
    try:
        message = await channel.fetch_message(payload.message_id)
        
        if not message.embeds or message.author.id != bot.user.id:
            return
        
        embed = message.embeds[0]
        if not embed.description:
            return
        
        match = re.search(r'<@(\d+)>', embed.description)
        if not match:
            return
        
        user_id = int(match.group(1))
        
        if payload.user_id != user_id:
            return
        
        plantation = await get_user_plantation(user_id)
        if not plantation or plantation['status'] != 'Fertig':
            return
        
        sheet = bot.sheets_service.spreadsheets()
        update_data = [['Geerntet']]
        body = {'values': update_data}
        
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'🌱 Plantagen!G{plantation["row_index"]}',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        user = await bot.fetch_user(user_id)
        now = datetime.now()
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
        week_number = now.isocalendar()[1]
        year = now.year
        
        values = [[
            timestamp,
            f"KW{week_number}/{year}",
            user.name,
            str(user_id),
            "Plantage geerntet",
            "8h Plantage erfolgreich abgeschlossen",
            PLANTATION_HARVEST_REWARD,
            ""
        ]]
        
        body = {'values': values}
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A:H',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        await message.edit(embed=discord.Embed(
            title="✅ PLANTAGE GEERNTET!",
            description=f"**{plantation['username']}** hat erfolgreich geerntet! 🎉\n\n"
                       f"💰 Log erstellt: **{PLANTATION_HARVEST_REWARD:.2f}€**\n"
                       f"⏳ Warte auf Auszahlung durch Admin/Rang",
            color=COLORS['success']
        ))
        
        print(f"✅ Plantage geerntet: {plantation['username']}")
    except Exception as e:
        print(f"❌ Fehler bei Ernte: {e}")

# ==================== STANDARD COMMANDS ====================

@bot.tree.command(name="log", description="Öffne das Log-System")
async def log_command(interaction: discord.Interaction):
    """Hauptcommand zum Einreichen von Logs"""
    embed = discord.Embed(title="", color=COLORS['primary'])
    embed.set_author(name="💜 Log-System + 🌱 Plantagen", icon_url=bot.user.display_avatar.url)
    embed.description = (
        "Wähle eine Aktion aus und reiche deinen Log ein!\n\n"
        "**Verfügbare Aktionen:**\n"
        f"🌱 Düngen - **{PAYMENT_AMOUNTS['Düngen']:.2f}€**\n"
        f"🔧 Reparieren - **{PAYMENT_AMOUNTS['Reparieren']:.2f}€**\n"
        f"⚡ Panel platziert - **{PAYMENT_AMOUNTS['Panel platziert']:.2f}€**\n"
        f"🌾 Plantage gesät - **{PAYMENT_AMOUNTS['Plantage gesät']:.2f}€** + 8h Countdown"
    )
    embed.set_footer(text="Metallic Purple Edition + Ananas-Plantagen")
    
    view = LogView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="panel", description="Öffne das Auszahlungs-Panel")
@has_payout_permission()
async def panel_command(interaction: discord.Interaction):
    """Interaktives Auszahlungs-Panel"""
    await interaction.response.defer(ephemeral=True)
    
    users = await get_all_users_with_earnings()
    
    current_week = datetime.now().isocalendar()[1]
    current_year = datetime.now().year
    week_key = f"KW{current_week}/{current_year}"
    
    for user in users:
        user['week'] = week_key
    
    embed = create_payout_panel_embed(users)
    view = PayoutPanelView(users)
    
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="auszahlung", description="Zahle einem Mitglied sein Wochenguthaben aus")
@app_commands.describe(mitglied="Das Mitglied das ausgezahlt werden soll")
@has_payout_permission()
async def payout_command(interaction: discord.Interaction, mitglied: discord.Member):
    """Schnelle Einzelauszahlung"""
    await interaction.response.defer(ephemeral=True)
    
    user_earnings = await get_user_week_earnings(mitglied.id)
    
    if user_earnings['total'] == 0:
        await interaction.followup.send(f"❌ {mitglied.mention} hat keine offenen Beträge diese Woche.", ephemeral=True)
        return
    
    user_data = {
        'user_id': str(mitglied.id),
        'username': mitglied.name,
        'total': user_earnings['total'],
        'logs': user_earnings['logs'],
        'breakdown': user_earnings['breakdown'],
        'week': user_earnings['week']
    }
    
    view = PayoutConfirmView(user_data, interaction.user)
    
    embed = discord.Embed(
        title="💎 Auszahlung bestätigen",
        description=f"Möchtest du **{mitglied.mention}** auszahlen?",
        color=COLORS['accent']
    )
    
    embed.add_field(name="💰 Betrag", value=f"**{user_earnings['total']:.2f}€**", inline=True)
    embed.add_field(name="📊 Logs", value=f"**{user_earnings['logs']}**", inline=True)
    embed.add_field(name="📅 Woche", value=f"**{user_earnings['week']}**", inline=True)
    
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="config", description="Konfiguriere Auszahlungs-Berechtigungen")
@app_commands.describe(aktion="Was möchtest du tun?", rolle="Die Rolle die hinzugefügt/entfernt werden soll")
@app_commands.choices(aktion=[
    app_commands.Choice(name="➕ Rolle hinzufügen", value="add"),
    app_commands.Choice(name="➖ Rolle entfernen", value="remove"),
    app_commands.Choice(name="📋 Rollen anzeigen", value="list")
])
@app_commands.checks.has_permissions(administrator=True)
async def config_command(interaction: discord.Interaction, aktion: str, rolle: Optional[discord.Role] = None):
    """Konfiguriere berechtigte Rollen"""
    global PAYOUT_ROLE_IDS
    
    if aktion == "list":
        if not PAYOUT_ROLE_IDS:
            await interaction.response.send_message("📋 Keine Rollen konfiguriert. Nur Admins können auszahlen.", ephemeral=True)
            return
        
        roles_text = ""
        for role_id in PAYOUT_ROLE_IDS:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_text += f"• {role.mention}\n"
            else:
                roles_text += f"• `{role_id}` (nicht gefunden)\n"
        
        embed = discord.Embed(title="🔐 Berechtigte Rollen", description=roles_text, color=COLORS['primary'])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not rolle:
        await interaction.response.send_message("❌ Bitte gib eine Rolle an.", ephemeral=True)
        return
    
    if aktion == "add":
        if rolle.id not in PAYOUT_ROLE_IDS:
            PAYOUT_ROLE_IDS.append(rolle.id)
            save_config()
            await interaction.response.send_message(f"✅ {rolle.mention} kann jetzt Auszahlungen durchführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ {rolle.mention} hat bereits Berechtigung.", ephemeral=True)
    
    elif aktion == "remove":
        if rolle.id in PAYOUT_ROLE_IDS:
            PAYOUT_ROLE_IDS.remove(rolle.id)
            save_config()
            await interaction.response.send_message(f"✅ {rolle.mention} kann keine Auszahlungen mehr durchführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ {rolle.mention} hatte keine Berechtigung.", ephemeral=True)

@bot.tree.command(name="wochenbericht", description="Zeige den aktuellen Wochenbericht")
@has_payout_permission()
async def weekly_report_command(interaction: discord.Interaction):
    """Manueller Wochenbericht"""
    await interaction.response.defer()
    embed = await generate_weekly_stats()
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="setup", description="Erstelle das Google Sheet (nur einmal ausführen)")
@app_commands.checks.has_permissions(administrator=True)
async def setup_command(interaction: discord.Interaction):
    """Erstelle die Sheets-Struktur inkl. Archiv + Plantagen"""
    await interaction.response.defer(ephemeral=True)
    
    if not bot.sheets_service:
        await interaction.followup.send("❌ Keine Verbindung zu Google Sheets!", ephemeral=True)
        return
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        
        # 1. LOGS TAB
        logs_headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Aktion', 'Beschreibung', 'Betrag', 'Bild-URL']]
        body = {'values': logs_headers}
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, range='Logs!A1:H1', valueInputOption='RAW', body=body).execute()
        
        # 2. AUSZAHLUNGEN TAB
        payout_headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Betrag', 'Anzahl Logs', 'Status', 'Admin']]
        body = {'values': payout_headers}
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, range='Auszahlungen!A1:H1', valueInputOption='RAW', body=body).execute()
        
        # 3. ARCHIV TAB
        archiv_headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Aktion', 'Beschreibung', 'Betrag', 'Bild-URL', 'Archiviert am']]
        body = {'values': archiv_headers}
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, range='Archiv!A1:I1', valueInputOption='RAW', body=body).execute()
        
        # 4. PLANTAGEN TAB (NEU)
        plantagen_headers = [['User-ID', 'Username', 'Gestartet am', 'Countdown (Sek)', 'Letzter Check', 'Letztes Düngen', 'Status', 'Fertig am', 'Nächstes Düngen']]
        body = {'values': plantagen_headers}
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, range='🌱 Plantagen!A1:I1', valueInputOption='RAW', body=body).execute()
        
        await interaction.followup.send(
            "✅ Sheet erfolgreich eingerichtet!\n"
            "📋 Tabs erstellt: Logs, Auszahlungen, Archiv, 🌱 Plantagen\n\n"
            "💡 Tipp: Führe `python premium_sheets_designer.py` aus für Premium-Design!",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Fehler: {e}", ephemeral=True)

@bot.tree.command(name="hilfe", description="Zeige alle verfügbaren Befehle")
async def help_command(interaction: discord.Interaction):
    """Hilfe-Command"""
    embed = discord.Embed(title="", color=COLORS['primary'])
    embed.set_author(name="💜 Bot Befehle + 🌱 Plantagen", icon_url=bot.user.display_avatar.url)
    
    embed.add_field(name="📝 `/log`", value="Öffne das Log-System zum Einreichen von Aktionen", inline=False)
    embed.add_field(name="🌱 `/plantage status`", value="Zeige deine aktive Plantage", inline=False)
    embed.add_field(name="🌾 `/plantage liste`", value="Alle aktiven Plantagen (Berechtigung nötig)", inline=False)
    embed.add_field(name="💎 `/panel`", value="Öffne das interaktive Auszahlungs-Panel (Berechtigung nötig)", inline=False)
    embed.add_field(name="💰 `/auszahlung @user`", value="Schnelle Einzelauszahlung (Berechtigung nötig)", inline=False)
    embed.add_field(name="🔐 `/config`", value="Konfiguriere berechtigte Rollen (nur Admins)", inline=False)
    embed.add_field(name="📊 `/wochenbericht`", value="Zeige den aktuellen Wochenbericht (Berechtigung nötig)", inline=False)
    embed.add_field(name="⚙️ `/setup`", value="Richte das Google Sheet ein (nur einmal, nur Admins)", inline=False)
    
    embed.set_footer(text="Metallic Purple Edition v2.2.0 + Ananas-Plantagen")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== ERROR HANDLER ====================

@panel_command.error
@payout_command.error
@weekly_report_command.error
async def payout_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        embed = discord.Embed(
            title="🔒 Keine Berechtigung",
            description="Du hast keine Berechtigung für diesen Befehl.\n\nBenötigt: Administrator oder konfigurierte Rolle",
            color=COLORS['danger']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        raise error

# ==================== BOT START ====================

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ DISCORD_TOKEN fehlt in der .env Datei!")
    else:
        print("\n" + "="*60)
        print("💜 DISCORD LOG BOT - METALLIC PURPLE EDITION + PLANTAGEN")
        print("="*60)
        print(f"Version: {__version__}")
        print(f"Author: {__author__}")
        print(f"Features: Logs • Auszahlungen • Ananas-Plantagen")
        print("="*60 + "\n")
        bot.run(TOKEN)
