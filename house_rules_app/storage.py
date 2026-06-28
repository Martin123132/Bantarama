from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

from .engine import generate_finale, round_to_html, round_to_text


APP_NAME = "Bantarama"
PACK_KEYS = ("phrases", "relics", "places", "rules")
SPECIAL_SCORE_LABELS = ("The House", "The Relic")

BUILTIN_PACKS: list[dict[str, Any]] = [
    {
        "id": "builtin-family-chaos",
        "source": "built-in",
        "name": "Family Chaos",
        "description": "Low-barrier nonsense for kitchens, cousins, and ancient grudges.",
        "players": [],
        "settings": {"round_count": 7, "tone": "House Rules", "weirdness": 54},
        "ingredients": {
            "phrases": ["who moved the good mug", "that was not my job", "we said normal plates", "ask the group chat"],
            "relics": ["the good mug", "a charger nobody owns", "the emergency biscuit tin", "the chair with history"],
            "places": ["the kitchen doorway", "next to the recycling", "the sofa tribunal", "the cupboard of blame"],
            "rules": ["Anyone who says it was like that already loses one argument.", "The oldest grudge speaks first."],
        },
    },
    {
        "id": "builtin-pub-table",
        "source": "built-in",
        "name": "Pub Table",
        "description": "For loud rulings, shaky evidence, and a table that believes it is a court.",
        "players": [],
        "settings": {"round_count": 7, "tone": "Chaos Council", "weirdness": 66},
        "ingredients": {
            "phrases": ["put that on the minutes", "absolute scenes", "I was nowhere near it", "that counts as evidence"],
            "relics": ["the wet coaster", "a heroic crisp packet", "the disputed receipt", "the ceremonial glass"],
            "places": ["the corner table", "outside by the bins", "the quiz machine", "the sticky bit of the bar"],
            "rules": ["A confident accusation outranks a careful memory.", "Any ruling made while standing is legally dramatic."],
        },
    },
    {
        "id": "builtin-office-nonsense",
        "source": "built-in",
        "name": "Office Nonsense",
        "description": "Meeting-room mythology without touching anyone's real HR department.",
        "players": [],
        "settings": {"round_count": 5, "tone": "Relic Trial", "weirdness": 48},
        "ingredients": {
            "phrases": ["circle back to the incident", "per my last panic", "the spreadsheet knows", "let us take this offline"],
            "relics": ["the haunted stapler", "an unlabelled cable", "the urgent marker pen", "the last decent chair"],
            "places": ["Meeting Room 3", "the printer queue", "the tea station", "beside the broken whiteboard"],
            "rules": ["A meeting becomes official if three people sigh at once.", "The printer may be blamed once per round."],
        },
    },
    {
        "id": "builtin-tabletop-quest",
        "source": "built-in",
        "name": "Tabletop Quest",
        "description": "A quest pack for dice nights, heroic excuses, and deeply suspicious props.",
        "players": [],
        "settings": {"round_count": 9, "tone": "Cult Night", "weirdness": 74},
        "ingredients": {
            "phrases": ["I check for traps emotionally", "the prophecy was laminated", "roll for dignity", "the map disagrees"],
            "relics": ["the cracked token", "a suspiciously important spoon", "the forbidden notebook", "the velvet dice bag"],
            "places": ["the cardboard tavern", "the hallway of bad choices", "the sacred snack zone", "behind the screen"],
            "rules": ["Any object given a capital letter becomes a relic.", "The loudest prophecy is not automatically correct."],
        },
    },
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def app_data_dir() -> Path:
    override = os.getenv("BANTARAMA_HOME") or os.getenv("HOUSE_RULES_HOME")
    root = Path(override).expanduser() if override else repo_root() / "data"
    root.mkdir(parents=True, exist_ok=True)
    return root


def exports_dir() -> Path:
    path = app_data_dir() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def packs_dir() -> Path:
    path = app_data_dir() / "packs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_state_path() -> Path:
    return repo_root() / "house_rules_app" / "seeds" / "default_party.json"


def user_state_path() -> Path:
    return app_data_dir() / "game.json"


def load_default_state() -> dict[str, Any]:
    state = _read_json(default_state_path(), fallback={})
    if not isinstance(state, dict):
        state = {}
    state.setdefault("game_seed", f"game-{int(time.time())}")
    return normalize_state(state)


def load_state() -> dict[str, Any]:
    path = user_state_path()
    if not path.exists():
        state = load_default_state()
        save_state(state)
        return state
    state = _read_json(path, fallback=None)
    if not isinstance(state, dict):
        broken = path.with_suffix(f".broken-{int(time.time())}.json")
        try:
            shutil.copy2(path, broken)
        except OSError:
            pass
        state = load_default_state()
        save_state(state)
    return normalize_state(state)


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_state(state)
    _write_json(user_state_path(), normalized)
    return normalized


def new_game() -> dict[str, Any]:
    state = load_default_state()
    state["game_seed"] = f"game-{int(time.time() * 1000)}"
    state["scores"] = {}
    state["history"] = []
    save_state(state)
    return state


def add_round(round_data: dict[str, Any], replace_round_id: str | None = None) -> dict[str, Any]:
    state = load_state()
    history = list(state.get("history") or [])
    if replace_round_id:
        for index, item in enumerate(history):
            if (item.get("round") or {}).get("id") == replace_round_id and not item.get("winner"):
                history[index] = {"round": round_data, "winner": None}
                break
        else:
            history.append({"round": round_data, "winner": None})
    else:
        history.append({"round": round_data, "winner": None})
    state["history"] = history
    return save_state(state)


def award_round(round_id: str, winner: str, points: int = 1) -> dict[str, Any]:
    state = load_state()
    players = [str(player) for player in state.get("players") or []]
    if winner not in players and winner != "Everyone" and winner not in SPECIAL_SCORE_LABELS:
        raise ValueError("Winner must be a current player, Everyone, The House, or The Relic.")
    scores = dict(state.get("scores") or {})
    if winner == "Everyone":
        for player in players:
            scores[player] = int(scores.get(player, 0)) + points
    else:
        scores[winner] = int(scores.get(winner, 0)) + points
    for item in state.get("history") or []:
        if (item.get("round") or {}).get("id") == round_id:
            item["winner"] = winner
            break
    state["scores"] = scores
    return save_state(state)


def export_game(export_format: str = "txt") -> dict[str, Any]:
    state = load_state()
    export_format = "html" if str(export_format).lower() == "html" else "txt"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = exports_dir() / f"{stamp}-bantarama.{export_format}"
    finale = generate_finale(state) if state.get("history") else None
    rounds = [(item.get("round") or {}) for item in state.get("history") or []]
    if export_format == "html":
        body = "\n<hr>\n".join(round_to_html(item) for item in rounds)
        if finale:
            body += "\n<hr>\n" + round_to_html(finale)
        path.write_text(body, encoding="utf-8")
    else:
        body = "\n\n" + ("=" * 72) + "\n\n"
        text = body.join(round_to_text(item) for item in rounds)
        if finale:
            text += body + str(finale.get("script") or "")
        path.write_text(text, encoding="utf-8")
    return {"path": str(path), "format": export_format}


def open_exports_folder() -> dict[str, Any]:
    path = exports_dir().resolve()
    root = app_data_dir().resolve()
    if path != root and root not in path.parents:
        raise ValueError("Exports folder must stay inside the Bantarama data folder.")
    opened = _launch_folder(path)
    return {"path": str(path), "opened": opened, "supported": opened}


def list_packs() -> list[dict[str, Any]]:
    packs = [_pack_summary(pack) for pack in BUILTIN_PACKS]
    for path in sorted(packs_dir().glob("*.json")):
        pack = _read_json(path, fallback=None)
        if isinstance(pack, dict):
            packs.append(_pack_summary(_normalize_pack(pack, pack_id=f"user-{path.stem}", source="user")))
    return packs


def save_pack(name: str, state: dict[str, Any]) -> dict[str, Any]:
    clean_name = str(name or "").strip()
    if not clean_name:
        raise ValueError("Pack name is required.")
    normalized = normalize_state(state)
    slug = _slug(clean_name)
    pack = _normalize_pack(
        {
            "id": f"user-{slug}",
            "source": "user",
            "name": clean_name,
            "description": "Saved from this table.",
            "created_at": int(time.time()),
            "players": normalized.get("players") or [],
            "settings": normalized.get("settings") or {},
            "ingredients": normalized.get("ingredients") or {},
        },
        pack_id=f"user-{slug}",
        source="user",
    )
    _write_json(packs_dir() / f"{slug}.json", pack)
    return _pack_summary(pack)


def apply_pack(pack_id: str) -> dict[str, Any]:
    pack = _find_pack(pack_id)
    state = load_state()
    players = _clean_list(pack.get("players"))
    if players:
        state["players"] = players
    state["ingredients"] = _normalize_ingredients(pack.get("ingredients"))
    settings = pack.get("settings") if isinstance(pack.get("settings"), dict) else {}
    state["settings"] = {
        "round_count": _clamp_int(settings.get("round_count", 7), 3, 15),
        "tone": str(settings.get("tone") or "House Rules"),
        "weirdness": _clamp_int(settings.get("weirdness", 62), 0, 100),
    }
    state["scores"] = {player: 0 for player in state.get("players") or []}
    state["history"] = []
    state["game_seed"] = f"pack-{_slug(str(pack.get('name') or 'pack'))}-{int(time.time() * 1000)}"
    return save_state(state)


def doctor() -> dict[str, Any]:
    state = load_state()
    return {
        "data_dir": str(app_data_dir()),
        "state_path": str(user_state_path()),
        "exports_dir": str(exports_dir()),
        "packs_dir": str(packs_dir()),
        "pack_count": len(list_packs()),
        "player_count": len(state.get("players") or []),
        "round_count": len(state.get("history") or []),
        "state_ok": isinstance(state.get("ingredients"), dict),
    }


def normalize_state(state: dict[str, Any]) -> dict[str, Any]:
    default = _read_json(default_state_path(), fallback={})
    normalized = dict(default if isinstance(default, dict) else {})
    normalized.update(state if isinstance(state, dict) else {})
    normalized["version"] = int(normalized.get("version") or 1)
    normalized["game_name"] = str(normalized.get("game_name") or "Bantarama")
    normalized["players"] = _clean_list(normalized.get("players"))
    normalized["game_seed"] = str(normalized.get("game_seed") or "bantarama")
    settings = normalized.get("settings") if isinstance(normalized.get("settings"), dict) else {}
    normalized["settings"] = {
        "round_count": _clamp_int(settings.get("round_count", 7), 3, 15),
        "tone": str(settings.get("tone") or "House Rules"),
        "weirdness": _clamp_int(settings.get("weirdness", 62), 0, 100),
    }
    ingredients = normalized.get("ingredients") if isinstance(normalized.get("ingredients"), dict) else {}
    default_ingredients = default.get("ingredients", {}) if isinstance(default, dict) else {}
    normalized["ingredients"] = _normalize_ingredients(ingredients, default_ingredients)
    scores = normalized.get("scores") if isinstance(normalized.get("scores"), dict) else {}
    normalized["scores"] = {str(key): int(value or 0) for key, value in scores.items()}
    history = normalized.get("history") if isinstance(normalized.get("history"), list) else []
    normalized["history"] = history
    return normalized


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _normalize_pack(pack: dict[str, Any], pack_id: str, source: str) -> dict[str, Any]:
    settings = pack.get("settings") if isinstance(pack.get("settings"), dict) else {}
    return {
        "id": str(pack.get("id") or pack_id),
        "source": str(pack.get("source") or source),
        "name": str(pack.get("name") or "Untitled Pack"),
        "description": str(pack.get("description") or ""),
        "created_at": int(pack.get("created_at") or 0),
        "players": _clean_list(pack.get("players")),
        "settings": {
            "round_count": _clamp_int(settings.get("round_count", 7), 3, 15),
            "tone": str(settings.get("tone") or "House Rules"),
            "weirdness": _clamp_int(settings.get("weirdness", 62), 0, 100),
        },
        "ingredients": _normalize_ingredients(pack.get("ingredients")),
    }


def _pack_summary(pack: dict[str, Any]) -> dict[str, Any]:
    ingredients = _normalize_ingredients(pack.get("ingredients"))
    return {
        "id": str(pack.get("id") or ""),
        "source": str(pack.get("source") or "user"),
        "name": str(pack.get("name") or "Untitled Pack"),
        "description": str(pack.get("description") or ""),
        "players": _clean_list(pack.get("players")),
        "settings": pack.get("settings") if isinstance(pack.get("settings"), dict) else {},
        "counts": {key: len(ingredients[key]) for key in PACK_KEYS},
    }


def _find_pack(pack_id: str) -> dict[str, Any]:
    wanted = str(pack_id or "")
    for pack in BUILTIN_PACKS:
        if pack["id"] == wanted:
            return _normalize_pack(pack, pack_id=wanted, source="built-in")
    if wanted.startswith("user-"):
        path = packs_dir() / f"{wanted.removeprefix('user-')}.json"
        pack = _read_json(path, fallback=None)
        if isinstance(pack, dict):
            return _normalize_pack(pack, pack_id=wanted, source="user")
    raise ValueError("Pack not found.")


def _normalize_ingredients(value: Any, fallback: Any | None = None) -> dict[str, list[str]]:
    ingredients = value if isinstance(value, dict) else {}
    fallback_ingredients = fallback if isinstance(fallback, dict) else {}
    return {key: _clean_list(ingredients.get(key) or fallback_ingredients.get(key)) for key in PACK_KEYS}


def _launch_folder(path: Path) -> bool:
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
            return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
            return True
        opener = shutil.which("xdg-open")
        if opener:
            subprocess.Popen([opener, str(path)])
            return True
    except OSError:
        return False
    return False


def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    seen = set()
    cleaned = []
    for item in value:
        text = str(item).strip()
        if text and text.lower() not in seen:
            cleaned.append(text)
            seen.add(text.lower())
    return cleaned


def _slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif cleaned and cleaned[-1] != "-":
            cleaned.append("-")
    slug = "".join(cleaned).strip("-")
    return slug[:60] or "pack"


def _clamp_int(value: Any, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = low
    return max(low, min(high, number))
