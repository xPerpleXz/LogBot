import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional
import io

# Google Sheets imports
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Konfiguration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')  # Wird in .env gesetzt

# Auszahlungsbeträge (anpassbar)
PAYMENT_AMOUNTS = {
    'Düngen': 5.00,
    'Reparieren': 8.00,
    'Panel platziert': 12.00
}

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
        """Bot initialisierung"""
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
    
    @tasks.loop(hours=168)  # 7 Tage = 168 Stunden
    async def weekly_report(self):
        """Wöchentlicher automatischer Bericht"""
        channel_id = int(os.getenv('REPORT_CHANNEL_ID', 0))
        if channel_id:
            channel = self.get_channel(channel_id)
            if channel:
                embed = await self.generate_weekly_stats()
                await channel.send(embed=embed)


# Bot Instanz
bot = LogBot()


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
            color=discord.Color.blue()
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
                confirmation = discord.Embed(
                    title="✅ Log erfolgreich eingetragen",
                    description=f"**Aktion:** {self.action_type}\n"
                               f"**Auszahlung:** {amount}€\n"
                               f"**Beschreibung:** {self.description.value}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                confirmation.set_thumbnail(url=image_url)
                confirmation.set_footer(text=f"Eingereicht von {interaction.user.name}")
                
                await interaction.followup.send(embed=confirmation, ephemeral=True)
                
# Öffentliche Benachrichtigung in MEHREREN Log-Channels
log_channel_ids = os.getenv('LOG_CHANNEL_IDS', '')
if log_channel_ids:
    # Split IDs (Komma-getrennt)
    channel_ids = [int(id.strip()) for id in log_channel_ids.split(',') if id.strip()]
    
    # Embed erstellen
    public_embed = discord.Embed(
        title="📋 Neuer Log-Eintrag",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    public_embed.add_field(name="Mitglied", value=interaction.user.mention, inline=True)
    public_embed.add_field(name="Aktion", value=self.action_type, inline=True)
    public_embed.add_field(name="Betrag", value=f"{amount}€", inline=True)
    public_embed.set_image(url=image_url)
    
    # In ALLE konfigurierten Channels posten
    for channel_id in channel_ids:
        log_channel = bot.get_channel(channel_id)
        if log_channel:
            try:
                await log_channel.send(embed=public_embed)
                print(f"✅ Log gepostet in: {log_channel.name}")
            except Exception as e:
                print(f"❌ Fehler beim Posten in Channel {channel_id}: {e}")
            else:
                error_embed = discord.Embed(
                    title="❌ Fehler",
                    description="Log konnte nicht gespeichert werden. Bitte kontaktiere einen Admin.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏱️ Zeit abgelaufen",
                description="Du hast zu lange gebraucht. Bitte versuche es erneut.",
                color=discord.Color.red()
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
        stats = await get_user_stats(interaction.user.id)
        
        embed = discord.Embed(
            title=f"📊 Statistiken für {interaction.user.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        total_earnings = 0
        for action, count in stats.items():
            if action in PAYMENT_AMOUNTS:
                earnings = count * PAYMENT_AMOUNTS[action]
                total_earnings += earnings
                embed.add_field(
                    name=action,
                    value=f"Anzahl: {count}\nVerdienst: {earnings}€",
                    inline=True
                )
        
        embed.add_field(
            name="💰 Gesamtverdienst (diese Woche)",
            value=f"**{total_earnings:.2f}€**",
            inline=False
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)


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
        
        # Embed erstellen
        embed = discord.Embed(
            title=f"📊 Wöchentlicher Bericht - {week_key}",
            description=f"Zeitraum: {week_key}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        # Top Earners
        sorted_users = sorted(user_earnings.items(), key=lambda x: x[1], reverse=True)
        top_earners = "\n".join([f"{i+1}. **{user}**: {amount:.2f}€" 
                                for i, (user, amount) in enumerate(sorted_users[:10])])
        
        if top_earners:
            embed.add_field(name="💰 Top 10 Verdiener", value=top_earners, inline=False)
        
        # Aktionsstatistiken
        action_stats = "\n".join([f"**{action}**: {count}x" 
                                 for action, count in action_counts.items()])
        embed.add_field(name="📋 Aktionen", value=action_stats, inline=True)
        
        # Gesamtsumme
        total = sum(user_earnings.values())
        embed.add_field(name="💵 Gesamtauszahlung", value=f"**{total:.2f}€**", inline=True)
        
        return embed
        
    except Exception as e:
        print(f"❌ Fehler beim Generieren des Berichts: {e}")
        return discord.Embed(title="Fehler", description=str(e))


# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="log", description="Öffne das Log-System")
async def log_command(interaction: discord.Interaction):
    """Hauptcommand zum Einreichen von Logs"""
    embed = discord.Embed(
        title="📝 Log-System",
        description="Wähle eine Aktion aus und reiche deinen Log ein!\n\n"
                   "**Verfügbare Aktionen:**\n"
                   f"🌱 Düngen - {PAYMENT_AMOUNTS['Düngen']}€\n"
                   f"🔧 Reparieren - {PAYMENT_AMOUNTS['Reparieren']}€\n"
                   f"⚡ Panel platziert - {PAYMENT_AMOUNTS['Panel platziert']}€",
        color=discord.Color.blue()
    )
    
    view = LogView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


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
        
        # Header erstellen
        headers = [['Zeitstempel', 'KW', 'Username', 'User-ID', 'Aktion', 'Beschreibung', 'Betrag', 'Bild-URL']]
        
        body = {'values': headers}
        
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='Logs!A1:H1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Formatierung
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }
        ]
        
        body = {'requests': requests}
        sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        
        await interaction.followup.send("✅ Sheet erfolgreich eingerichtet!", ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Fehler: {e}", ephemeral=True)


@bot.tree.command(name="hilfe", description="Zeige alle verfügbaren Befehle")
async def help_command(interaction: discord.Interaction):
    """Hilfe-Command"""
    embed = discord.Embed(
        title="🤖 Bot Befehle",
        description="Hier sind alle verfügbaren Befehle:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="/log",
        value="Öffne das Log-System zum Einreichen von Aktionen",
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


# Bot starten
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ DISCORD_TOKEN fehlt in der .env Datei!")
    else:
        bot.run(TOKEN)
