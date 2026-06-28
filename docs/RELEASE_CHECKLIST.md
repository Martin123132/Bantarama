# Bantarama Release Checklist

Use this before sharing a ZIP with testers.

## Local Setup

```powershell
cd D:\Projects\Bantarama
New-Item -ItemType Directory -Force -Path D:\Temp, D:\BantaramaData | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:BANTARAMA_HOME = "D:\BantaramaData"
```

## Automated Checks

```powershell
python -m unittest discover -s tests
python -m compileall house_rules_app tests scripts
python scripts\write_demo_scenes.py
python scripts\sample_rounds.py --count 6
python -m house_rules_app.app --doctor
```

## Manual Flow

- Fresh unzip on Windows.
- Double-click `START_BANTARAMA_WINDOWS.bat`.
- Browser opens.
- Press **Demo Game**.
- Open **Packs** and load one built-in pack.
- Start a round.
- Vote for a player.
- Open **Scores**.
- Export TXT.
- Export HTML.
- Use **Open Exports Folder**.
- Close the app command window.
- Confirm no `house_rules_app.app` process is still running.

## Python Missing Case

- Temporarily test on a machine without Python, or ask a tester who does not
  have Python installed.
- Confirm the launcher explains Python 3.10+ in plain English.
- Confirm it says to tick `Add python.exe to PATH`.

## Release ZIP

```powershell
powershell -ExecutionPolicy Bypass -File scripts\make_release_zip.ps1
```

The ZIP should not contain `.git`, `__pycache__`, `data`, `exports`, `dist`,
logs, temporary files, or local runtime state.

## Release Notes

- Version:
- ZIP path:
- Screenshot path:
- Known limitation: Python 3.10+ required.
- Tester ask: download ZIP, unzip, double-click, press Demo Game, start round,
  vote, export.
- Feedback tracker: `docs\TESTER_FEEDBACK_LOG.md`.
- Licence file included and mentions Bantarama.
