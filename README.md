# Bantarama

Bantarama is a local-first party chaos game. Add player names, phrases,
objects, places, and grudges, then let the deterministic collision engine make
same-room rounds that people can argue about.

It does not need API keys, accounts, cloud services, Ollama, npm, or a build
step.

## Start On Windows

1. Double-click `START_BANTARAMA_WINDOWS.bat`.
2. Your browser opens.
3. Add at least two players.
4. Follow the traffic-light readiness guide.
5. Start a round.

Use **Demo Game** on the first screen when you want to see a ready-to-play table
before adding your own names and in-jokes.

Use **Packs** to load a built-in table style or save your current names,
phrases, objects, places, rules, and setup as a reusable local pack.
Built-in packs include local thumbnail art so the host can pick by feel.

If Windows says Python is missing, install Python 3.10 or newer from:

```text
https://www.python.org/downloads/windows/
```

Tick `Add python.exe to PATH` during install, then double-click the launcher
again.

## Data Location

The launcher stores game data in this repo's `data` folder by default. If the
repo is on `D:\`, the game data stays on `D:\` too:

```text
data\
```

You can override it:

```powershell
$env:BANTARAMA_HOME = "D:\BantaramaData"
python -m house_rules_app.app
```

Saved exports and packs stay under the configured data folder:

```text
D:\BantaramaData\exports
D:\BantaramaData\packs
```

For D-drive development checks:

```powershell
New-Item -ItemType Directory -Force -Path D:\Temp, D:\BantaramaData | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:BANTARAMA_HOME = "D:\BantaramaData"
```

For a D-drive playtest run from PowerShell:

```powershell
cd D:\Projects\Bantarama
New-Item -ItemType Directory -Force -Path D:\Temp, D:\BantaramaData | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:BANTARAMA_HOME = "D:\BantaramaData"
python -m house_rules_app.app
```

## Development Checks

```powershell
python -m unittest discover -s tests
python -m compileall house_rules_app tests scripts
python scripts\sample_rounds.py --count 5
python scripts\write_demo_scenes.py
python -m house_rules_app.app --doctor
```

Fixed-seed comedy samples live in `docs\demo-scenes`.

## Release ZIP

```powershell
powershell -ExecutionPolicy Bypass -File scripts\make_release_zip.ps1
```

The release ZIP is written to `dist\` and excludes `.git`, caches, local data,
exports, logs, and temporary files.

## Licence

Bantarama is source-available for personal and non-commercial use under the
PolyForm Noncommercial License 1.0.0. See [LICENSE](LICENSE).

## Playtest Loop

Use [PLAYTEST_SHEET.md](docs/PLAYTEST_SHEET.md) for the first 3-5 same-room
tests. The useful signal is simple: which round made someone read the line out
loud, and which screen made the host hesitate.

Use [TESTER_SCRIPT.md](docs/TESTER_SCRIPT.md) when sending the ZIP to someone
who has never seen the project.
Track real runs in [TESTER_FEEDBACK_LOG.md](docs/TESTER_FEEDBACK_LOG.md).

## Design Promise

One screen, one obvious next action. Red means "add this first", amber means
"playable", and green means "strong table fuel". Packs get their own page so
the host can choose table flavour before editing ingredients.
