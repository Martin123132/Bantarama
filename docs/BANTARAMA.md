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
6. Read the beat buttons out loud.
7. Vote, or in a two-player game choose how the duel ruling lands.

Use **Demo Game** on the first screen when you want to see a ready-to-play table
before adding your own names and in-jokes.

Use **Packs** to load a built-in table style or save your current names,
phrases, objects, places, rules, and setup as a reusable local pack.

Two-player games use **Duel Rulings**. The point can go to the accused, the
accuser, Everyone, The House, or The Relic, which keeps awkward votes funny
instead of forced.

After a round, use reaction buttons to nudge the next one: **Too Normal**,
**Too Much**, **Again But Harsher**, or **This Energy Works**.

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

For D-drive development checks:

```powershell
New-Item -ItemType Directory -Force -Path D:\Temp, D:\BantaramaData | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:BANTARAMA_HOME = "D:\BantaramaData"
```

Exports and packs are saved under the configured data folder.

```text
D:\BantaramaData\exports
D:\BantaramaData\packs
```

## Design Promise

One screen, one obvious next action. Red means "add this first", amber means
"playable", and green means "strong table fuel". Packs get their own page so
the host can choose table flavour before editing ingredients.
