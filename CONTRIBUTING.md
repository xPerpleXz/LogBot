# Contributing to Discord Log Bot

Danke, dass du zu diesem Projekt beitragen möchtest! 🎉

## 🤝 Wie kann ich beitragen?

### Bug Reports 🐛

Wenn du einen Bug findest:

1. **Check ob der Bug schon gemeldet wurde** in den Issues
2. **Erstelle ein neues Issue** mit:
   - Klare Beschreibung des Problems
   - Schritte zur Reproduktion
   - Erwartetes vs. tatsächliches Verhalten
   - Screenshots wenn möglich
   - Deine Umgebung (OS, Python Version, etc.)

### Feature Requests 💡

Hast du eine Idee für ein neues Feature?

1. **Check ob es schon vorgeschlagen wurde** in den Issues
2. **Erstelle ein neues Issue** mit:
   - Beschreibung des Features
   - Warum ist es nützlich?
   - Beispiele für die Verwendung
   - Optional: Wie würdest du es implementieren?

### Pull Requests 🔧

Möchtest du Code beitragen?

#### Vorbereitung

1. **Fork das Repository**
2. **Erstelle einen Branch:**
   ```bash
   git checkout -b feature/deine-feature-name
   # oder
   git checkout -b fix/dein-bugfix-name
   ```

3. **Mache deine Änderungen:**
   - Folge dem bestehenden Code-Stil
   - Kommentiere komplexe Logik
   - Teste deine Änderungen lokal

4. **Commit mit aussagekräftiger Message:**
   ```bash
   git commit -m "feat: Add multi-channel support"
   # oder
   git commit -m "fix: Resolve Google Sheets 403 error"
   ```

5. **Push zu deinem Fork:**
   ```bash
   git push origin feature/deine-feature-name
   ```

6. **Erstelle einen Pull Request**

#### Code-Stil

- **Python:** PEP 8 Standard
- **Einrückung:** 4 Leerzeichen
- **Docstrings:** Für alle Funktionen/Klassen
- **Type Hints:** Wo möglich

Beispiel:
```python
async def save_log(user: discord.Member, action: str) -> bool:
    """
    Speichert einen Log-Eintrag in Google Sheets.
    
    Args:
        user: Discord Member Objekt
        action: Typ der Aktion
        
    Returns:
        True wenn erfolgreich, False sonst
    """
    try:
        # Code hier
        return True
    except Exception as e:
        print(f"Fehler: {e}")
        return False
```

#### Testing

Bevor du einen PR erstellst:

```bash
# Lokal testen
python bot.py

# Dependencies checken
pip install -r requirements.txt

# Keine Syntax-Fehler?
python -m py_compile bot.py
```

#### PR Guidelines

- **Ein PR = Eine Funktion/Fix**
  - Nicht mehrere unabhängige Änderungen in einem PR

- **Beschreibung:**
  - Was wurde geändert?
  - Warum wurde es geändert?
  - Wie wurde es getestet?

- **Screenshots/GIFs** wenn UI-Änderungen

- **Breaking Changes** deutlich markieren

#### Review-Prozess

1. **Automated Checks** müssen grün sein
2. **Code Review** durch Maintainer
3. **Änderungen** wenn nötig
4. **Merge** wenn alles OK!

## 📝 Commit Message Format

Wir nutzen [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add feature XYZ
fix: Resolve issue with ABC
docs: Update README
style: Format code
refactor: Restructure function XYZ
test: Add tests for feature ABC
chore: Update dependencies
```

**Beispiele:**

```bash
git commit -m "feat: Add support for multiple log channels"
git commit -m "fix: Resolve Google Sheets authentication error"
git commit -m "docs: Add deployment guide for Render.com"
git commit -m "refactor: Improve error handling in save_log()"
```

## 🐛 Debug Tipps

### Logs ansehen

```bash
# Lokal
python bot.py

# Railway
Railway Dashboard → Logs

# Docker
docker logs -f discord-log-bot
```

### Häufige Probleme

**Import Errors:**
```bash
pip install -r requirements.txt --upgrade
```

**Discord API Errors:**
- Check Bot Token
- Check Permissions
- Check Intents

**Google Sheets Errors:**
- Check credentials.json
- Check Sheet Permissions
- Check Spreadsheet ID

## 🌟 Arten von Contributions

### Code
- Bug Fixes
- Neue Features
- Performance Verbesserungen
- Code Refactoring

### Dokumentation
- README Verbesserungen
- Guide Erweiterungen
- Code Kommentare
- Übersetzungen

### Community
- Issues beantworten
- Anderen helfen
- Feedback geben
- Tests durchführen

## 📊 Projekt-Struktur

```
discord_log_bot/
├── bot.py              # Haupt-Bot Code
├── admin_tools.py      # Admin Funktionen
├── setup.py            # Setup-Assistent
├── requirements.txt    # Dependencies
├── README.md          # Hauptdokumentation
├── LICENSE            # MIT Lizenz
└── docs/              # Zusätzliche Guides
```

## ⚖️ Lizenz

Durch deine Contribution stimmst du zu, dass deine Arbeit unter der **MIT License** lizenziert wird.

## 🙏 Danke!

Jede Contribution hilft, dieses Projekt besser zu machen!

**Besonderer Dank an:**
- Alle Contributors
- Die discord.py Community
- Google Cloud Platform
- Railway.app

## 📞 Kontakt

Bei Fragen:
- **Issues:** Erstelle ein GitHub Issue
- **Diskussionen:** GitHub Discussions (wenn aktiviert)
- **Email:** [Bei Bedarf hinzufügen]

---

**Viel Erfolg beim Contributen! 🚀**

Made with ❤️ by xPerpleXz and contributors
