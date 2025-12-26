# 📜 CHANGELOG

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert.

---

## [2.1.0] - 2024-12-25 🎄

### 💜 METALLIC PURPLE EDITION

**Das große Design-Update mit komplett neuem Look und interaktivem Auszahlungs-Panel!**

### ✨ NEU - Features

#### 🎨 Komplett neues Design
- **Metallic Purple Farbpalette**
  - Primary: `#6A0DAD` Classic Purple
  - Secondary: `#3D0066` Dark Chrome
  - Accent: `#C77DFF` Metallic Lilac
- Modernes, elegantes Design ohne saisonale Elemente
- Chrome/Öl-Effekt Styling in allen Embeds
- Neue Progress Bars mit Metallic-Look

#### 💎 Interaktives Auszahlungs-Panel (`/panel`)
- **Dropdown-Auswahl** für einzelne User
- **"Alle Auszahlen"** Button mit Bestätigungs-Dialog
- Live-Übersicht aller User mit offenem Guthaben
- Sortiert nach Verdienst
- Echtzeit-Aktualisierung
- Progress-Tracking während Massenoperationen

#### 📁 Archiv-System
- Neuer **Archiv-Tab** in Google Sheets
- Logs werden nach Auszahlung automatisch archiviert
- Vollständige Nachverfolgbarkeit aller Transaktionen
- "Archiviert am" Timestamp für jede Zeile
- Dark Chrome Theme für den Archiv-Tab

#### 🔐 Rollen-Konfiguration
- **Konfigurierbare Berechtigungen** für Auszahlungen
- Zwei Konfigurationsmethoden:
  1. `.env` Datei: `PAYOUT_ROLE_IDS=123,456,789`
  2. Discord Command: `/config add-role @Rolle`
- Admins haben IMMER Zugriff
- Persistente Speicherung in `config.json`

#### 📊 Verbessertes Dashboard
- Live-Formeln für alle Statistiken
- Archiv-Counter im Dashboard
- Auszahlungs-Übersicht
- Neue Farbgebung passend zum Theme

### 🔧 VERBESSERT

- **Auszahlungs-Flow**: 
  - Automatische DM an User mit detailliertem Breakdown
  - Admin-Name wird in Sheets gespeichert
  - Bestätigungs-Dialoge für alle kritischen Aktionen
  
- **Google Sheets Design**:
  - Zebra Striping mit Purple-Tönen
  - Bedingte Formatierung für Aktionen
  - Währungsformatierung (€)
  - Frozen Headers
  - Dropdown-Validierung

- **Error Handling**:
  - Bessere Fehlermeldungen
  - Graceful Degradation wenn DMs nicht möglich
  - Rate Limiting bei Massenoperationen

### 📝 NEUE COMMANDS

| Command | Beschreibung | Berechtigung |
|---------|--------------|--------------|
| `/panel` | Interaktives Auszahlungs-Panel | Konfigurierbar |
| `/config` | Berechtigungs-Konfiguration | Admin only |
| `/config add-role` | Rolle hinzufügen | Admin only |
| `/config remove-role` | Rolle entfernen | Admin only |
| `/config list` | Berechtigte Rollen anzeigen | Admin only |

### 📁 NEUE DATEIEN

- `config.json` - Persistente Rollen-Konfiguration (wird automatisch erstellt)
- Archiv-Tab in Google Sheets

### ⚠️ BREAKING CHANGES

- Auszahlungen-Tab hat jetzt 8 Spalten (+ Admin-Spalte)
- Neuer Archiv-Tab muss erstellt werden
- `/setup` erstellt jetzt auch den Archiv-Tab

### 🔄 MIGRATION VON v2.0.0

1. **Bot aktualisieren**:
   ```bash
   # Neue Dateien ersetzen
   cp bot.py /pfad/zu/deinem/bot/
   cp premium_sheets_designer.py /pfad/zu/deinem/bot/
   ```

2. **Google Sheets aktualisieren**:
   ```bash
   python premium_sheets_designer.py
   ```
   
3. **Optional: Rollen konfigurieren**:
   ```
   /config add-role @Moderator
   ```

---

## [2.0.0] - 2024-12 

### 🎨 PREMIUM EDITION

- Premium Discord Embeds
- Automatisches Auszahlungs-System
- Live Dashboard mit Formeln
- Progress Tracking
- Corporate Design
- `/auszahlung @user` Command
- Premium Output Channel

---

## [1.0.0] - 2024-11

### 🚀 INITIAL RELEASE

- Basis Log-System
- Google Sheets Integration
- 3 Aktionstypen (Düngen, Reparieren, Panel)
- Wöchentliche Reports
- Admin Tools (CLI)
- Multi-Platform Deployment Support

---

## Legende

- ✨ **NEU** - Neue Features
- 🔧 **VERBESSERT** - Verbesserungen an bestehenden Features
- 🐛 **BEHOBEN** - Bug Fixes
- ⚠️ **BREAKING** - Änderungen die Migration erfordern
- 🗑️ **ENTFERNT** - Entfernte Features

---

**Maintainer:** [xPerpleXz](https://github.com/xPerpleXz)

**Fragen?** Erstelle ein [GitHub Issue](https://github.com/xPerpleXz/discord-log-bot/issues)
