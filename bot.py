#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Log Bot - PREMIUM EDITION
Professional Log Management System with Payment Integration

Author: xPerpleXz
License: MIT
Version: 2.0.0 - Premium Edition
Repository: https://github.com/xPerpleXz/discord-log-bot
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional, Dict, List
import io

# Google Sheets imports
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

__author__ = "xPerpleXz"
__version__ = "2.0.0"
__license__ = "MIT"

# ==================== KONFIGURATION ====================

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Auszahlungsbeträge (anpassbar)
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,
    'Reparieren': 8.00,
    'Panel platziert': 12.00
}

# 🎨 PREMIUM COLORS für Embeds
COLORS = {
    'primary': 0x4285F4,      # Google Blue
    'success': 0x4CAF50,      # Green
    'warning': 0xFFC107,      # Amber
    'danger': 0xF44336,       # Red
    'info': 0x2196F3,         # Light Blue
    'gold': 0xFFD700,         # Gold
    'purple': 0x9C27B0        # Purple
}

# ==================== BOT CLASS ====================

class LogBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
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
        
        # Google Sheets verbinden
        self.sheets_service = self.init_google_sheets()
        
        # Automatische wöchentliche Berichte starten
        if not self.weekly_report.is_running():
            self.weekly_report.start()
    
    def init_google_sheets(self):
        """Google Sheets API initialisieren - mit Base64 Support"""
        try:
            # Option 1: Base64 credentials (Railway/Cloud)
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
    
    @tasks.loop(hours=168)  # 7 Tage = 168 Stunden
    async def weekly_report(self):
        """Wöchentlicher automatischer Bericht"""
        channel_id = int(os.getenv('REPORT_CHANNEL_ID', 0))
        if channel_id:
            channel = self.get_channel(channel_id)
            if channel:
                embed = await generate_weekly_stats()
                await channel.send(embed=embed)


# Bot Instanz
bot = LogBot()

# ==================== HELPER FUNCTIONS ====================

async def get_total_log_count() -> int:
    """Hole die Gesamtanzahl aller Logs"""
    if not bot.sheets_service:
        return 0
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A2:A'
        ).execute()
        
        values = result.get('values', [])
        return len(values)
        
    except Exception as e:
        print(f"❌ Fehler beim Zählen der Logs: {e}")
        return 0


def create_progress_bar(current: int, target: int, length: int = 20) -> str:
    """
    Erstellt eine visuelle Progress Bar
    
    Args:
        current: Aktueller Fortschritt
        target: Ziel-Wert
        length: Länge der Bar in Zeichen
        
    Returns:
        Progress Bar String (z.B. "▰▰▰▰▰▰▱▱▱▱")
    """
    if target == 0:
        return "▱" * length
    
    percentage = min(current / target, 1.0)
    filled = int(length * percentage)
    empty = length - filled
    
    # Unicode Block Characters für smooth bar
    bar = "▰" * filled + "▱" * empty
    
    return bar


async def get_user_week_earnings(user_id: int) -> Dict[str, any]:
    """
    Hole detaillierte Wochen-Statistiken für einen User
    
    Returns:
        {
            'total': float,
            'logs': int,
            'breakdown': {'Düngen': count, ...},
            'week': 'KW52/2024'
        }
    """
    if not bot.sheets_service:
        return {'total': 0, 'logs': 0, 'breakdown': {}, 'week': ''}
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        
        # Aktuelle Kalenderwoche
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        week_key = f"KW{current_week}/{current_year}"
        
        # Alle Logs abrufen
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A2:H'
        ).execute()
        
        values = result.get('values', [])
        
        # Statistiken berechnen
        total_earnings = 0
        log_count = 0
        breakdown = {action: 0 for action in PAYMENT_AMOUNTS.keys()}
        
        for row in values:
            if len(row) >= 7:
                if row[1] == week_key and row[3] == str(user_id):
                    action = row[4]
                    amount = float(row[6])
                    
                    total_earnings += amount
                    log_count += 1
                    
                    if action in breakdown:
                        breakdown[action] += 1
        
        return {
            'total': total_earnings,
            'logs': log_count,
            'breakdown': breakdown,
            'week': week_key
        }
        
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Earnings: {e}")
        return {'total': 0, 'logs': 0, 'breakdown': {}, 'week': ''}


async def save_log(user: discord.Member, action_type: str, description: str, image_url: str) -> bool:
    """Speichere Log in Google Sheets"""
    if not bot.sheets_service:
        return False
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        
        # Aktuelle Zeit
        now = datetime.now()
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
        week_number = now.isocalendar()[1]
        year = now.year
        
        # Betrag berechnen
        amount = PAYMENT_AMOUNTS.get(action_type, 0)
        
        # Daten vorbereiten
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
        
        # In Sheet eintragen
        result = sheet.values().append(
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


async def save_payout(user: discord.Member, amount: float, week: str, log_count: int) -> bool:
    """
    Speichere Auszahlung in Google Sheets (Auszahlungen Tab)
    
    Args:
        user: Discord Member
        amount: Auszahlungsbetrag
        week: Kalenderwoche (z.B. "KW52/2024")
        log_count: Anzahl Logs
        
    Returns:
        True wenn erfolgreich
    """
    if not bot.sheets_service:
        return False
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        
        # Timestamp
        now = datetime.now()
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
        
        # Daten vorbereiten
        values = [[
            timestamp,
            week,
            user.name,
            str(user.id),
            amount,
            log_count,
            "Ausgezahlt"
        ]]
        
        body = {'values': values}
        
        # In Auszahlungen Tab eintragen
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Auszahlungen!A:G',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ Auszahlung gespeichert: {user.name} - {amount}€")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Auszahlung: {e}")
        return False


async def reset_user_week_earnings(user_id: int) -> bool:
    """
    Setzt das Wochen-Guthaben eines Users zurück
    WICHTIG: Logs bleiben erhalten, nur für Tracking
    
    Args:
        user_id: Discord User ID
        
    Returns:
        True wenn erfolgreich
    """
    # In diesem System bleiben Logs erhalten
    # Reset wird nur im Tracking-Tab gemacht
    # Diese Funktion ist ein Platzhalter für zukünftige Features
    print(f"ℹ️ User {user_id} Guthaben logisch zurückgesetzt (Logs bleiben)")
    return True


async def get_user_stats(user_id: int) -> dict:
    """Hole Statistiken für einen User (aktuelle Woche)"""
    if not bot.sheets_service:
        return {}
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        
        # Aktuelle Kalenderwoche
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        week_key = f"KW{current_week}/{current_year}"
        
        # Alle Logs abrufen
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A2:H'
        ).execute()
        
        values = result.get('values', [])
        
        # Statistiken berechnen
        stats = {action: 0 for action in PAYMENT_AMOUNTS.keys()}
        
        for row in values:
            if len(row) >= 5:
                if row[1] == week_key and row[3] == str(user_id):
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
        
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A2:H'
        ).execute()
        
        values = result.get('values', [])
        
        # Statistiken sammeln
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
        
        # 🎨 PREMIUM EMBED
        embed = discord.Embed(
            title="",
            color=COLORS['gold'],
            timestamp=datetime.utcnow()
        )
        
        embed.set_author(
            name=f"📊 Wöchentlicher Bericht - {week_key}",
            icon_url=bot.user.display_avatar.url
        )
        
        # Top Earners
        sorted_users = sorted(user_earnings.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_users:
            top_10 = sorted_users[:10]
            
            # Medals für Top 3
            medals = ["🥇", "🥈", "🥉"]
            
            top_earners_text = ""
            for i, (user, amount) in enumerate(top_10):
                medal = medals[i] if i < 3 else f"`{i+1}.`"
                top_earners_text += f"{medal} **{user}**: `{amount:.2f}€`\n"
            
            embed.add_field(
                name="💰 Top 10 Verdiener",
                value=top_earners_text,
                inline=False
            )
        
        # Aktionsstatistiken mit Emojis
        action_emojis = {
            'Düngen': '🌱',
            'Reparieren': '🔧',
            'Panel platziert': '⚡'
        }
        
        action_stats = ""
        for action, count in action_counts.items():
            emoji = action_emojis.get(action, '📌')
            action_stats += f"{emoji} **{action}**: `{count}x`\n"
        
        embed.add_field(
            name="📋 Aktionen Breakdown",
            value=action_stats if action_stats else "Keine Aktionen",
            inline=True
        )
        
        # Gesamtsumme
        total = sum(user_earnings.values())
        total_logs = sum(action_counts.values())
        
        summary = f"💵 **{total:.2f}€**\n📊 **{total_logs}** Logs"
        
        embed.add_field(
            name="💼 Gesamt",
            value=summary,
            inline=True
        )
        
        # Footer
        embed.set_footer(
            text=f"Generiert am {datetime.now().strftime('%d.%m.%Y um %H:%M')} Uhr"
        )
        
        return embed
        
    except Exception as e:
        print(f"❌ Fehler beim Generieren des Berichts: {e}")
        return discord.Embed(
            title="❌ Fehler",
            description=str(e),
            color=COLORS['danger']
        )

# ==================== UI COMPONENTS ====================

class ActionSelect(discord.ui.Select):
    """Dropdown für Aktionsauswahl"""
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Düngen",
                description=f"Auszahlung: {PAYMENT_AMOUNTS['Düngen']}€",
                emoji="🌱"
            ),
            discord.SelectOption(
                label="Reparieren",
                description=f"Auszahlung: {PAYMENT_AMOUNTS['Reparieren']}€",
                emoji="🔧"
            ),
            discord.SelectOption(
                label="Panel platziert",
                description=f"Auszahlung: {PAYMENT_AMOUNTS['Panel platziert']}€",
                emoji="⚡"
            )
        ]
        super().__init__(
            placeholder="Wähle eine Aktion...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            LogModal(action_type=self.values[0])
        )


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
        
        # Warte auf Bildanhang
        embed = discord.Embed(
            title="📸 Bitte Bild hochladen",
            description=f"**Aktion:** {self.action_type}\n"
                       f"**Beschreibung:** {self.description.value}\n\n"
                       f"Bitte lade jetzt ein Bild als Beweis hoch.\n"
                       f"Du hast 60 Sekunden Zeit.",
            color=COLORS['info']
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Auf Bild warten
        def check(m):
            return (m.author.id == interaction.user.id and 
                   len(m.attachments) > 0 and
                   m.channel.id == interaction.channel.id)
        
        try:
            message = await bot.wait_for('message', timeout=60.0, check=check)
            image_url = message.attachments[0].url
            
            # Log speichern
            success = await save_log(
                user=interaction.user,
                action_type=self.action_type,
                description=self.description.value,
                image_url=image_url
            )
            
            if success:
                amount = PAYMENT_AMOUNTS[self.action_type]
                
                # 🎨 PREMIUM CONFIRMATION EMBED
                confirmation = discord.Embed(
                    title="",
                    color=COLORS['success'],
                    timestamp=datetime.utcnow()
                )
                
                confirmation.set_author(
                    name="✅ Log erfolgreich eingetragen",
                    icon_url=interaction.user.display_avatar.url
                )
                
                confirmation.add_field(
                    name="🎯 Aktion",
                    value=f"**{self.action_type}**",
                    inline=True
                )
                
                confirmation.add_field(
                    name="💰 Auszahlung",
                    value=f"**{amount:.2f}€**",
                    inline=True
                )
                
                confirmation.add_field(
                    name="\u200b",
                    value="\u200b",
                    inline=True
                )
                
                confirmation.add_field(
                    name="📝 Beschreibung",
                    value=f"```{self.description.value}```",
                    inline=False
                )
                
                confirmation.set_thumbnail(url=image_url)
                confirmation.set_footer(text=f"Eingereicht von {interaction.user.name}")
                
                await interaction.followup.send(embed=confirmation, ephemeral=True)
                
                # 🎨 PREMIUM OUTPUT CHANNEL
                output_channel_id = os.getenv('LOG_OUTPUT_CHANNEL_ID', '')
                
                if output_channel_id:
                    output_channel = bot.get_channel(int(output_channel_id))
                    
                    if output_channel:
                        # Action Emojis
                        action_emojis = {
                            'Düngen': '🌱',
                            'Reparieren': '🔧',
                            'Panel platziert': '⚡'
                        }
                        
                        # 💎 PREMIUM PUBLIC EMBED
                        premium_embed = discord.Embed(
                            title="",
                            color=COLORS['primary'],
                            timestamp=datetime.utcnow()
                        )
                        
                        premium_embed.set_author(
                            name="📋 Neuer Log-Eintrag",
                            icon_url=bot.user.display_avatar.url
                        )
                        
                        # Main Content
                        premium_embed.add_field(
                            name="👤 Mitglied",
                            value=f"{interaction.user.mention}\n`{interaction.user.name}`",
                            inline=True
                        )
                        
                        action_emoji = action_emojis.get(self.action_type, '📌')
                        premium_embed.add_field(
                            name="🎯 Aktion",
                            value=f"{action_emoji} **{self.action_type}**",
                            inline=True
                        )
                        
                        premium_embed.add_field(
                            name="💰 Auszahlung",
                            value=f"**{amount:.2f}€**",
                            inline=True
                        )
                        
                        # Beschreibung
                        premium_embed.add_field(
                            name="📝 Beschreibung",
                            value=f"```\n{self.description.value}\n```",
                            inline=False
                        )
                        
                        # Zeit & KW
                        now = datetime.now()
                        week_number = now.isocalendar()[1]
                        
                        premium_embed.add_field(
                            name="📅 Kalenderwoche",
                            value=f"KW {week_number}/{now.year}",
                            inline=True
                        )
                        
                        premium_embed.add_field(
                            name="🕐 Uhrzeit",
                            value=now.strftime("%H:%M:%S"),
                            inline=True
                        )
                        
                        premium_embed.add_field(name="\u200b", value="\u200b", inline=True)
                        
                        # Progress Bar
                        user_stats = await get_user_week_earnings(interaction.user.id)
                        total_logs = user_stats['logs']
                        
                        if total_logs > 0:
                            progress_bar = create_progress_bar(total_logs, 50)
                            premium_embed.add_field(
                                name="📊 Wochen-Fortschritt (Ziel: 50 Logs)",
                                value=f"{progress_bar} `{total_logs}/50`",
                                inline=False
                            )
                        
                        # Thumbnails & Images
                        premium_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                        premium_embed.set_image(url=image_url)
                        
                        # Footer mit Log Count
                        log_count = await get_total_log_count()
                        premium_embed.set_footer(
                            text=f"Log #{log_count} • Discord Log Bot Premium",
                            icon_url=bot.user.display_avatar.url
                        )
                        
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
    
    @discord.ui.button(
        label="Meine Statistiken",
        style=discord.ButtonStyle.primary,
        emoji="📊",
        custom_id="stats_button"
    )
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Zeige persönliche Statistiken"""
        await interaction.response.defer(ephemeral=True)
        
        # Hole detaillierte Stats
        user_stats = await get_user_week_earnings(interaction.user.id)
        
        # 🎨 PREMIUM STATS EMBED
        embed = discord.Embed(
            title="",
            color=COLORS['purple'],
            timestamp=datetime.utcnow()
        )
        
        embed.set_author(
            name=f"📊 Deine Statistiken - {user_stats['week']}",
            icon_url=interaction.user.display_avatar.url
        )
        
        # Breakdown
        action_emojis = {
            'Düngen': '🌱',
            'Reparieren': '🔧',
            'Panel platziert': '⚡'
        }
        
        for action, count in user_stats['breakdown'].items():
            if count > 0 and action in PAYMENT_AMOUNTS:
                emoji = action_emojis.get(action, '📌')
                earnings = count * PAYMENT_AMOUNTS[action]
                
                embed.add_field(
                    name=f"{emoji} {action}",
                    value=f"Anzahl: **{count}**\nVerdienst: **{earnings:.2f}€**",
                    inline=True
                )
        
        # Gesamtverdienst
        embed.add_field(
            name="💰 Gesamtverdienst (diese Woche)",
            value=f"**{user_stats['total']:.2f}€**",
            inline=False
        )
        
        # Progress Bar
        if user_stats['logs'] > 0:
            progress = create_progress_bar(user_stats['logs'], 50)
            embed.add_field(
                name="📊 Fortschritt (Ziel: 50 Logs)",
                value=f"{progress} `{user_stats['logs']}/50`",
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Statistiken werden live aktualisiert")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="log", description="Öffne das Log-System")
async def log_command(interaction: discord.Interaction):
    """Hauptcommand zum Einreichen von Logs"""
    embed = discord.Embed(
        title="",
        color=COLORS['primary']
    )
    
    embed.set_author(
        name="📝 Log-System",
        icon_url=bot.user.display_avatar.url
    )
    
    embed.description = (
        "Wähle eine Aktion aus und reiche deinen Log ein!\n\n"
        "**Verfügbare Aktionen:**\n"
        f"🌱 Düngen - **{PAYMENT_AMOUNTS['Düngen']:.2f}€**\n"
        f"🔧 Reparieren - **{PAYMENT_AMOUNTS['Reparieren']:.2f}€**\n"
        f"⚡ Panel platziert - **{PAYMENT_AMOUNTS['Panel platziert']:.2f}€**"
    )
    
    view = LogView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@bot.tree.command(name="auszahlung", description="Zahle einem Mitglied sein Wochenguthaben aus (Admin)")
@app_commands.describe(
    mitglied="Das Mitglied das ausgezahlt werden soll"
)
@app_commands.checks.has_permissions(administrator=True)
async def payout_command(interaction: discord.Interaction, mitglied: discord.Member):
    """
    💰 AUSZAHLUNGS-COMMAND
    
    Funktion:
    1. Berechnet Wochenguthaben des Users
    2. Sendet detaillierte DM an User
    3. Speichert Auszahlung in Google Sheets
    4. Postet Bestätigung im Channel
    """
    await interaction.response.defer(ephemeral=True)
    
    # Hole User Earnings
    user_earnings = await get_user_week_earnings(mitglied.id)
    
    if user_earnings['total'] == 0:
        await interaction.followup.send(
            f"❌ {mitglied.mention} hat keine offenen Beträge diese Woche.",
            ephemeral=True
        )
        return
    
    # 💌 SENDE DM AN USER
    try:
        # 🎨 PREMIUM DM EMBED
        dm_embed = discord.Embed(
            title="",
            color=COLORS['gold'],
            timestamp=datetime.utcnow()
        )
        
        dm_embed.set_author(
            name="💰 AUSZAHLUNG ERFOLGREICH",
            icon_url=bot.user.display_avatar.url
        )
        
        dm_embed.description = f"Hallo **{mitglied.display_name}**!\n\nDeine Auszahlung wurde veranlasst:"
        
        # Zeitraum & Betrag
        dm_embed.add_field(
            name="📅 Zeitraum",
            value=f"**{user_earnings['week']}**",
            inline=True
        )
        
        dm_embed.add_field(
            name="💵 Betrag",
            value=f"**{user_earnings['total']:.2f}€**",
            inline=True
        )
        
        dm_embed.add_field(
            name="📋 Logs gesamt",
            value=f"**{user_earnings['logs']}**",
            inline=True
        )
        
        # Breakdown
        action_emojis = {
            'Düngen': '🌱',
            'Reparieren': '🔧',
            'Panel platziert': '⚡'
        }
        
        breakdown_text = ""
        for action, count in user_earnings['breakdown'].items():
            if count > 0:
                emoji = action_emojis.get(action, '📌')
                earnings = count * PAYMENT_AMOUNTS[action]
                breakdown_text += f"{emoji} **{action}**: {count}x (**{earnings:.2f}€**)\n"
        
        if breakdown_text:
            dm_embed.add_field(
                name="📊 Breakdown",
                value=breakdown_text,
                inline=False
            )
        
        # Motivational Message
        dm_embed.add_field(
            name="🎉 Status",
            value="Dein Guthaben wurde zurückgesetzt.\n**Viel Erfolg in der neuen Woche!** 🚀",
            inline=False
        )
        
        dm_embed.set_thumbnail(url=mitglied.display_avatar.url)
        dm_embed.set_footer(text="Discord Log Bot Premium • Auszahlung")
        
        await mitglied.send(embed=dm_embed)
        
    except discord.Forbidden:
        await interaction.followup.send(
            f"⚠️ Konnte {mitglied.mention} keine DM senden (DMs deaktiviert).",
            ephemeral=True
        )
        return
    
    # 💾 SPEICHERE AUSZAHLUNG
    success = await save_payout(
        user=mitglied,
        amount=user_earnings['total'],
        week=user_earnings['week'],
        log_count=user_earnings['logs']
    )
    
    if not success:
        await interaction.followup.send(
            "❌ Fehler beim Speichern der Auszahlung in Google Sheets.",
            ephemeral=True
        )
        return
    
    # RESET User Guthaben (logisch)
    await reset_user_week_earnings(mitglied.id)
    
    # ✅ BESTÄTIGUNG AN ADMIN
    confirmation = discord.Embed(
        title="✅ Auszahlung durchgeführt",
        description=f"**{mitglied.mention}** wurde **{user_earnings['total']:.2f}€** ausgezahlt.",
        color=COLORS['success']
    )
    
    confirmation.add_field(
        name="📋 Details",
        value=f"Zeitraum: {user_earnings['week']}\nLogs: {user_earnings['logs']}",
        inline=False
    )
    
    await interaction.followup.send(embed=confirmation, ephemeral=True)
    
    # 📢 ÖFFENTLICHE NOTIFICATION (optional)
    output_channel_id = os.getenv('LOG_OUTPUT_CHANNEL_ID', '')
    if output_channel_id:
        output_channel = bot.get_channel(int(output_channel_id))
        if output_channel:
            public_embed = discord.Embed(
                title="💰 Auszahlung durchgeführt",
                description=f"**{mitglied.display_name}** wurde **{user_earnings['total']:.2f}€** ausgezahlt!",
                color=COLORS['gold'],
                timestamp=datetime.utcnow()
            )
            public_embed.set_thumbnail(url=mitglied.display_avatar.url)
            await output_channel.send(embed=public_embed)


@bot.tree.command(name="wochenbericht", description="Zeige den aktuellen Wochenbericht")
@app_commands.checks.has_permissions(administrator=True)
async def weekly_report_command(interaction: discord.Interaction):
    """Manueller Wochenbericht (nur für Admins)"""
    await interaction.response.defer()
    embed = await generate_weekly_stats()
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="setup", description="Erstelle das Google Sheet (nur einmal ausführen)")
@app_commands.checks.has_permissions(administrator=True)
async def setup_command(interaction: discord.Interaction):
    """Erstelle die Sheets-Struktur"""
    await interaction.response.defer(ephemeral=True)
    
    if not bot.sheets_service:
        await interaction.followup.send("❌ Keine Verbindung zu Google Sheets!", ephemeral=True)
        return
    
    try:
        sheet = bot.sheets_service.spreadsheets()
        
        # 1. LOGS TAB
        logs_headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Aktion', 'Beschreibung', 'Betrag', 'Bild-URL']]
        
        body = {'values': logs_headers}
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A1:H1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # 2. AUSZAHLUNGEN TAB
        payout_headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Betrag', 'Anzahl Logs', 'Status']]
        
        body = {'values': payout_headers}
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='Auszahlungen!A1:G1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Formatierung
        requests = [
            # Logs Header
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.26, 'green': 0.52, 'blue': 0.96},
                            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }
        ]
        
        body = {'requests': requests}
        sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        
        await interaction.followup.send(
            "✅ Sheet erfolgreich eingerichtet!\n"
            "📋 Tabs erstellt: Logs, Auszahlungen",
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.followup.send(f"❌ Fehler: {e}", ephemeral=True)


@bot.tree.command(name="hilfe", description="Zeige alle verfügbaren Befehle")
async def help_command(interaction: discord.Interaction):
    """Hilfe-Command"""
    embed = discord.Embed(
        title="",
        color=COLORS['info']
    )
    
    embed.set_author(
        name="🤖 Bot Befehle",
        icon_url=bot.user.display_avatar.url
    )
    
    embed.add_field(
        name="/log",
        value="Öffne das Log-System zum Einreichen von Aktionen",
        inline=False
    )
    
    embed.add_field(
        name="/auszahlung @user",
        value="Zahle einem Mitglied sein Wochenguthaben aus (nur Admins)",
        inline=False
    )
    
    embed.add_field(
        name="/wochenbericht",
        value="Zeige den aktuellen Wochenbericht (nur Admins)",
        inline=False
    )
    
    embed.add_field(
        name="/setup",
        value="Richte das Google Sheet ein (nur einmal, nur Admins)",
        inline=False
    )
    
    embed.add_field(
        name="📊 Button: Meine Statistiken",
        value="Klicke auf den Button im Log-System um deine persönlichen Stats zu sehen",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================== BOT START ====================

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ DISCORD_TOKEN fehlt in der .env Datei!")
    else:
        print("\n" + "="*60)
        print("🎨 DISCORD LOG BOT - PREMIUM EDITION")
        print("="*60)
        print(f"Version: {__version__}")
        print(f"Author: {__author__}")
        print("="*60 + "\n")
        bot.run(TOKEN)
