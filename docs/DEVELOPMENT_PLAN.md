# Bantarama Development Plan

## V0.1

- Keep same-room, one-device play.
- Make the guided page flow obvious without a manual.
- Tune round output from real playtest notes.
- Keep storage local and D-drive friendly during development.
- Keep export recovery friendly: the host should be able to open the exports
  folder from the app after saving.
- Keep first-run teaching visible: traffic lights, page separation, host guide,
  and Demo Game should get a new player to a round without reading docs.

## V0.2

- Add local pack save/load so a table can reuse its own names, phrases, objects,
  places, rules, and setup.
- Keep packs in the configured data folder under `packs`.
- Include built-in starter packs for family, pub, office, and tabletop play.
- Loading a pack should reset scores/history so the host starts clean.
- Give built-in packs local thumbnail art so the Packs page feels like choosing
  a game flavour, not filling out a form.

## V0.3

- Tune deterministic comedy beats before adding new UI features.
- Improve callbacks, table actions, vote prompts, and mode-specific escalation.
- Keep demo proof under `docs/demo-scenes` with fixed seeds so engine changes
  can be judged without API calls.
- Add release prep docs and a clean ZIP script before wider tester sharing.

## V0.4.1 Trial Patch

- Make two-player games feel intentional with duel voting instead of awkward
  "pick the winner" scoring.
- Let The House and The Relic take points when the funniest answer is not a
  player.
- Add read-aloud beat controls so the host can reveal a round one section at a
  time.
- Add local reaction buttons for quick playtest tuning: too normal, too much,
  again but harsher, and this energy works.
- Keep the patch local-first: no telemetry, no accounts, no API calls.

## D-Drive Development Setup

Use this before checks or manual browser runs when you want runtime output away
from `C:\`:

```powershell
cd D:\Projects\Bantarama
New-Item -ItemType Directory -Force -Path D:\Temp, D:\BantaramaData | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:BANTARAMA_HOME = "D:\BantaramaData"
```

## V0.1 Release Gate

- Fresh unzip and double-click works on Windows.
- 3-5 people can play five rounds without the host reading docs.
- At least two rounds make someone read a line out loud.
- Exports work and stay inside the configured Bantarama data folder.
- The Open Exports Folder button appears after export and opens only that
  configured exports folder.
- Built-in packs load, custom packs save under `BANTARAMA_HOME\packs`, and
  loading a pack resets the game history.
- Demo scenes regenerate with `python scripts\write_demo_scenes.py` and all
  demo seeds render valid scripts.
- `scripts\make_release_zip.ps1` creates a clean ZIP without runtime state.
- `docs\RELEASE_CHECKLIST.md` and `docs\TESTER_SCRIPT.md` are current.
- `docs\TESTER_FEEDBACK_LOG.md` tracks the first 3-5 outside runs.
- Unit tests, compile, doctor, and browser smoke pass.

## Later

- Phone join mode.
- Pack import/export files.
- Shareable final prophecy cards.
