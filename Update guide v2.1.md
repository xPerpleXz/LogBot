# 💜 UPDATE GUIDE: v2.1.0 METALLIC PURPLE EDITION

## 🚀 Schnell-Update (5 Minuten)

### Schritt 1: Dateien ersetzen

```bash
# Ersetze diese Dateien in deinem Bot-Ordner:
# - bot.py
# - premium_sheets_designer.py
# - .env.example (optional, für Referenz)
```

### Schritt 2: Google Sheets Design anwenden

```bash
python premium_sheets_designer.py
```

### Schritt 3: Bot neu starten

```bash
# Strg+C zum Stoppen, dann:
python bot.py
```

**Fertig! 🎉**

---

## 📋 Was ist neu?

### 💜 Neues Design
- **Metallic Purple Farbpalette** statt blau/grün
- Eleganter Chrome/Öl-Effekt
- Moderne, zeitlose Ästhetik

### 💎 Interaktives Auszahlungs-Panel

```
/panel
```

Öffnet ein interaktives Panel mit:
- 📋 Dropdown zur User-Auswahl
- 💰 "Alle Auszahlen" Button
- 🔄 Aktualisieren Button
- Bestätigungs-Dialoge

### 📁 Archiv-System
- Ausgezahlte Logs werden automatisch ins **Archiv** verschoben
- Logs bleiben für immer nachvollziehbar
- Logs-Tab bleibt clean

### 🔐 Rollen-Konfiguration

```
/config add-role @Moderator
/config remove-role @Helper  
/config list
```

Oder in `.env`:
```env
PAYOUT_ROLE_IDS=123456789,987654321
```

---

## ⚙️ Neue Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `/panel` | Interaktives Auszahlungs-Panel |
| `/config add-role @Rolle` | Rolle für Auszahlungen berechtigen |
| `/config remove-role @Rolle` | Berechtigung entfernen |
| `/config list` | Alle berechtigten Rollen anzeigen |

---

## 📊 Google Sheets Struktur

Nach dem Update hast du 4 Tabs:

| Tab | Zweck |
|-----|-------|
| **Logs** | Aktive, offene Logs |
| **📊 Dashboard** | Live-Statistiken mit Formeln |
| **Auszahlungen** | Alle durchgeführten Auszahlungen |
| **Archiv** | Ausgezahlte Logs (archiviert) |

---

## 🎨 Farbpalette

```
Primary:   #6A0DAD (Classic Purple)
Secondary: #3D0066 (Dark Chrome)  
Accent:    #C77DFF (Metallic Lilac)
```

---

## ❓ Häufige Fragen

### Muss ich meine alten Logs migrieren?
**Nein!** Alle bestehenden Logs bleiben erhalten. Der Designer fügt nur das neue Styling hinzu.

### Was passiert mit bereits ausgezahlten Logs?
Logs die VOR dem Update ausgezahlt wurden, bleiben im Logs-Tab. Ab jetzt werden neue Auszahlungen automatisch archiviert.

### Muss ich den /setup Command nochmal ausführen?
**Nur wenn du den Archiv-Tab nicht manuell erstellt hast.** Der Sheets Designer erstellt ihn automatisch.

### Funktionieren die alten Commands noch?
**Ja!** Alle alten Commands funktionieren weiterhin. `/auszahlung @user` funktioniert parallel zum neuen `/panel`.

---

## 🆘 Probleme?

### "Archiv Tab nicht gefunden"
```bash
# Führe den Designer nochmal aus:
python premium_sheets_designer.py
```

### "Keine Berechtigung für /panel"
- Bist du Admin? → Sollte funktionieren
- Nicht Admin? → Ein Admin muss dich mit `/config add-role` berechtigen

### Design sieht komisch aus
```bash
# Sheets Designer nochmal ausführen:
python premium_sheets_designer.py
```

---

## 📞 Support

- **FAQ.md** durchlesen
- **GitHub Issues** erstellen
- Discord Community fragen

---

**Viel Spaß mit der Metallic Purple Edition! 💜**
