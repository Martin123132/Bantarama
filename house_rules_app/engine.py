from __future__ import annotations

import hashlib
import html
import random
import time
from typing import Any


MODES = [
    "House Rules",
    "Cult Night",
    "Five-a-Side Incident",
    "Relic Trial",
    "Under The Stairs",
    "Chaos Council",
]

PRIMES = [11, 13, 17, 19, 23, 29, 31, 37]
DRIFTS = ["preserve", "fragment", "distort", "invert", "amplify", "misremember"]
COLLISIONS = ["accusation", "new_rule", "betrayal", "committee", "confession", "public_vote"]
SPECIAL_SCORE_LABELS = ["The House", "The Relic"]
TABLE_ACTIONS = [
    "The host reads the accusation once, then points at the accused without explaining.",
    "Everyone gets ten seconds to make the object sound guilty.",
    "The accused may defend themselves, but must include the phrase exactly once.",
    "The table may ask one yes-or-no question, then immediately ignore the answer.",
    "The quietest player delivers the official ruling.",
    "Someone must hold the relic while the vote happens.",
]
MODE_TABLE_ACTIONS = {
    "House Rules": [
        "Everyone proposes one loophole. The host accepts the shortest one and looks disappointed.",
        "{player} must read the house rule like it was discovered in a wall.",
        "{other} gets ten seconds to prove {relic} has been enforcing policy without consent.",
    ],
    "Cult Night": [
        "The table repeats '{phrase}' once, then votes on who sounded too comfortable.",
        "{other} invents a title for {relic}. Anyone laughing is counted as a follower.",
        "The host asks for a schism. Two players must disagree about biscuit doctrine immediately.",
    ],
    "Five-a-Side Incident": [
        "Two players recreate the goal with an invisible ball. The worst replay becomes official.",
        "{player} gives a post-match interview while holding {relic} like a trophy.",
        "{other} has five seconds to shout an appeal before the imaginary whistle goes.",
    ],
    "Relic Trial": [
        "{relic} is placed in the middle. Each player gives exactly one word of testimony.",
        "{player} must object to their own evidence, then explain why that helped.",
        "The host asks the room whether {relic} looks guilty from this angle.",
    ],
    "Under The Stairs": [
        "{player} gives one sincere sentence, then immediately ruins it with '{phrase}'.",
        "{other} plays the therapist for ten seconds and must blame the architecture.",
        "The room takes a deep breath. Whoever laughs first becomes the breakthrough.",
    ],
    "Chaos Council": [
        "{other} names a subcommittee. It must have a title and no useful powers.",
        "The table votes on whether {relic} is evidence, chairperson, or problem.",
        "{player} must make one motion. Someone else must make it worse.",
    ],
}
CALLBACK_FRAMES = [
    "This is now connected to {callback}, whether anyone likes that or not.",
    "The minutes note a previous incident involving {callback}.",
    "A smaller argument about {callback} breaks out and somehow helps.",
    "The room agrees not to mention {callback}, then mentions it immediately.",
]
HISTORY_CALLBACK_FRAMES = [
    "The previous incident, '{callback}', returns wearing a fake moustache and somehow counts as precedent.",
    "Someone says this is exactly like '{callback}'. Nobody agrees, but the room behaves as if they did.",
    "The host opens the old case file marked '{callback}' and immediately regrets having a system.",
    "'{callback}' is cited as precedent by the person least qualified to remember it.",
]
DRIFT_BEATS = {
    "preserve": [
        "The original claim is preserved perfectly, which is bad because it was nonsense in the first place.",
        "Nobody improves the story. They simply protect the first mistake with surprising tenderness.",
    ],
    "fragment": [
        "The story splits into three smaller accusations, each more confident and less useful.",
        "Every witness remembers a different half of the same sentence and all of them demand respect.",
    ],
    "distort": [
        "The room mishears one detail and builds an entire legal system around the wrong object.",
        "A tiny misunderstanding becomes load-bearing before anyone can stop it.",
    ],
    "invert": [
        "The defence accidentally proves the prosecution's point, then asks if that was strategy.",
        "The room reverses the blame so fast that {relic} appears briefly innocent.",
    ],
    "amplify": [
        "One quiet comment is repeated with ceremony until it sounds like policy.",
        "{other} says it louder, which is not evidence but does move the room emotionally.",
    ],
    "misremember": [
        "Someone remembers a version that could not have happened, but it has better pacing.",
        "The table collectively misremembers the start and treats the improved version as law.",
    ],
}
COLLISION_BEATS = {
    "accusation": [
        "The accusation lands with the confidence of a person pointing at the wrong cupboard.",
        "{player} is accused so directly that even {relic} looks embarrassed.",
    ],
    "new_rule": [
        "A new rule appears mid-argument and immediately acts older than everyone.",
        "The room invents a law, then pretends it had always been laminated.",
    ],
    "betrayal": [
        "{other} discovers they were betrayed by procedure, furniture, and possibly tone.",
        "Trust collapses in a small, localised way around {relic}.",
    ],
    "committee": [
        "A committee forms because nobody wants responsibility in a single-player format.",
        "The council creates a subcommittee, then loses moral control of it.",
    ],
    "confession": [
        "{player} says something that is not a confession but has confession lighting.",
        "The room hears a confession hiding inside a sentence about snacks.",
    ],
    "public_vote": [
        "The room skips fairness and goes straight to democratic theatre.",
        "A public vote is called before anyone understands the question, which improves turnout.",
    ],
}
VOTE_PROMPTS = {
    "accusation": [
        "Vote: {player} is guilty, {other} framed them, or {relic} has become too powerful.",
        "Vote who made the accusation feel true: {player}, {other}, or the suspicious object.",
        "Vote whether the real culprit is {player}, {other}, or the room's need for closure.",
    ],
    "new_rule": [
        "Vote whether this becomes law, with immediate effect: {house_rule}",
        "Vote whether the new law stands, gets rewritten, or is quietly blamed on {relic}.",
        "Vote who must enforce this terrible new rule until someone worse arrives.",
    ],
    "betrayal": [
        "Vote who was betrayed harder: {player}, {other}, or common sense.",
        "Vote who deserves compensation in the form of one point and no apology.",
        "Vote whether the betrayal was emotional, procedural, or mostly {relic}'s fault.",
    ],
    "committee": [
        "Vote who must chair the emergency committee about {relic}.",
        "Vote who gets trapped in the subcommittee and has to pretend this is governance.",
        "Vote whether the committee reports to {player}, {other}, or the nearest mug.",
    ],
    "confession": [
        "Vote who clearly confessed without using confession words.",
        "Vote whether {player}'s explanation was a defence, a confession, or performance art.",
        "Vote who should have stopped talking six seconds earlier.",
    ],
    "public_vote": [
        "Vote who wins this nonsense and gets one point.",
        "Vote who made the room believe harder than the facts allowed.",
        "Vote who gets the point, then make them explain why that was probably unfair.",
    ],
}

MODE_OPENERS = {
    "House Rules": [
        "{player} tries to tidy up and accidentally creates a constitutional crisis.",
        "The room discovers that {relic} has been enforcing a rule nobody voted for.",
        "{player} says '{phrase}' and everyone immediately behaves worse.",
    ],
    "Cult Night": [
        "{player} forms a small belief system around {relic}.",
        "A chant begins in {place}, mostly because {phrase}.",
        "{other} asks one reasonable question and is declared the first heretic.",
    ],
    "Five-a-Side Incident": [
        "{player} scores a goal with {relic}, which is brave and probably illegal.",
        "The match stops when {other} claims '{phrase}' counts as advantage.",
        "{place} becomes a pitch after two jumpers and one terrible decision.",
    ],
    "Relic Trial": [
        "{relic} is placed on trial after being found near {place}.",
        "{player} gives evidence, then remembers they were holding {relic}.",
        "The prosecution says '{phrase}' and rests for emotional reasons.",
    ],
    "Under The Stairs": [
        "{player} is called under the stairs for a short, unlicensed debrief.",
        "{relic} starts therapy in {place} and immediately blames {other}.",
        "{other} whispers '{phrase}', which the stairs accept as a breakthrough.",
    ],
    "Chaos Council": [
        "{player} calls a council because {relic} has gone too far.",
        "{place} elects a temporary chair, and somehow it is {other}.",
        "The agenda contains only '{phrase}' and a drawing of {relic}.",
    ],
}

MODE_EVIDENCE = {
    "House Rules": [
        "The minutes show {other} nodded near the exact moment everything became official.",
        "{relic} was warm, which everyone agrees is suspicious but not helpful.",
        "A witness heard '{phrase}' and saw {player} pretending not to understand doors.",
    ],
    "Cult Night": [
        "Three people hummed at once. That is how sects start.",
        "{relic} was discovered facing east, toward the snack table.",
        "{other} wrote the creed on a receipt and called it tradition.",
    ],
    "Five-a-Side Incident": [
        "The imaginary VAR check found vibes, intent, and a damp footprint.",
        "{player} celebrated before the ball had emotionally crossed the line.",
        "{other} appealed using only the phrase '{phrase}'.",
    ],
    "Relic Trial": [
        "The court accepts {relic} as both evidence and defendant.",
        "{other} objects on the grounds that the object has a face if you squint.",
        "A rulebook was opened to a page that simply said '{phrase}'.",
    ],
    "Under The Stairs": [
        "The stairs report a pattern of avoidance, crumbs, and theatrical sighing.",
        "{player} says the cupboard started it, which is classic cupboard projection.",
        "{other} brought {relic} for support, making support considerably worse.",
    ],
    "Chaos Council": [
        "The council notes that nobody denied it quickly enough.",
        "{relic} has been seen near too many decisions.",
        "{other} used the phrase '{phrase}' while looking procedural.",
    ],
}

MODE_STINGS = {
    "House Rules": [
        "The new law passes by a vote of everyone wanting this to end.",
        "The room applauds once, then pretends it was furniture.",
    ],
    "Cult Night": [
        "The cult splits immediately over biscuit doctrine.",
        "Membership rises to three, then falls to two and a mug.",
    ],
    "Five-a-Side Incident": [
        "Full time is declared by someone holding a spoon.",
        "The goal stands, but only in mythology.",
    ],
    "Relic Trial": [
        "The verdict is guilty, but only of having an atmosphere.",
        "Court is adjourned after the evidence starts looking smug.",
    ],
    "Under The Stairs": [
        "The stairs request a follow-up session and a better lamp.",
        "Everyone leaves with closure, except the object.",
    ],
    "Chaos Council": [
        "The council forms a subcommittee and loses it immediately.",
        "The minutes are sealed inside the least trustworthy cup.",
    ],
}


def readiness(state: dict[str, Any]) -> dict[str, Any]:
    ingredients = state.get("ingredients") or {}
    checks = {
        "players": _status(len(state.get("players") or []), 2, 4, "Add at least 2 players."),
        "phrases": _status(len(ingredients.get("phrases") or []), 2, 5, "Add 2 phrases."),
        "relics": _status(len(ingredients.get("relics") or []), 1, 3, "Add 1 object."),
        "places": _status(len(ingredients.get("places") or []), 1, 3, "Add 1 place."),
        "rules": _status(len(ingredients.get("rules") or []), 1, 3, "Add 1 rule."),
    }
    if any(item["level"] == "red" for item in checks.values()):
        overall = "red"
    elif any(item["level"] == "amber" for item in checks.values()):
        overall = "amber"
    else:
        overall = "green"
    return {
        "overall": overall,
        "checks": checks,
        "next_step": _next_step(checks, overall),
        "can_start": overall in {"amber", "green"},
    }


def generate_round(state: dict[str, Any], options: dict[str, Any] | None = None) -> dict[str, Any]:
    options = options or {}
    ready = readiness(state)
    if not ready["can_start"]:
        raise ValueError(ready["next_step"])

    settings = state.get("settings") or {}
    round_number = int(options.get("round_number") or len(state.get("history") or []) + 1)
    mode = str(options.get("mode") or settings.get("tone") or "House Rules")
    if mode == "Random" or mode not in MODES:
        mode = _rng_from_state(state, round_number, "mode").choice(MODES)
    weirdness = _clamp_int(options.get("weirdness", settings.get("weirdness", 62)), 0, 100)

    rng = _rng_from_state(state, round_number, mode, weirdness)
    players = _items(state.get("players"), ["Player One", "Player Two"])
    ingredients = state.get("ingredients") or {}
    phrases = _items(ingredients.get("phrases"), ["that counts as law"])
    relics = _items(ingredients.get("relics"), ["The Object"])
    places = _items(ingredients.get("places"), ["the room"])
    rules = _items(ingredients.get("rules"), ["The loudest explanation wins."])

    player = rng.choice(players)
    other = _choose_other(rng, players, player)
    phrase = rng.choice(phrases)
    relic = rng.choice(relics)
    place = rng.choice(places)
    house_rule = rng.choice(rules)
    prime = rng.choice(PRIMES)
    trace_seed = _stable_int(player, other, phrase, relic, round_number) % prime
    trace = prime_trace(trace_seed, prime, weirdness)
    drift = DRIFTS[(trace[-1] + weirdness + round_number) % len(DRIFTS)]
    collision = COLLISIONS[(sum(trace) + len(mode)) % len(COLLISIONS)]

    data = {
        "player": player,
        "other": other,
        "phrase": phrase,
        "relic": relic,
        "place": place,
    }
    opener = _format(rng.choice(MODE_OPENERS[mode]), data)
    evidence = _format(rng.choice(MODE_EVIDENCE[mode]), data)
    sting = _format(rng.choice(MODE_STINGS[mode]), data)
    escalation = _escalation(mode, rng, player, other, relic, phrase, drift, collision, weirdness)
    decision = _decision(rng, collision, player, other, relic, house_rule)
    if len(players) == 2:
        decision = _duel_decision(rng, collision, player, other, relic)
    callback, callback_kind = _callback_target(rng, state, player, other, relic, phrase)
    callback_line = _callback_line(rng, callback, callback_kind)
    table_action = _table_action(mode, rng, player, other, relic, phrase, collision)

    title = _title(mode, player, relic, phrase)
    lines = [
        title.upper(),
        "",
        f"Round {round_number} | {mode} | Weirdness {weirdness}",
        f"Location: {place}",
        f"Accused: {player}",
        "",
        "Setup:",
        opener,
        "",
        "Evidence:",
        evidence,
        "",
        "Escalation:",
        escalation,
        "",
        "Callback:",
        callback_line,
        "",
        "House Rule:",
        house_rule,
        "",
        "Table Action:",
        table_action,
        "",
        "Vote Prompt:",
        decision,
        "",
        "Closing Sting:",
        sting,
        "",
        "WHY THIS HAPPENED",
        f"Prime field: Z{prime}",
        f"Seven-step trace: {trace}",
        f"Drift: {drift}",
        f"Collision: {collision}",
    ]
    script = "\n".join(lines)
    round_id = f"round-{round_number}-{_stable_int(script) % 100000:05d}"
    read_aloud = [
        {"id": "setup", "label": "Setup", "body": opener},
        {"id": "evidence", "label": "Evidence", "body": evidence},
        {"id": "escalation", "label": "Escalation", "body": escalation},
        {"id": "callback", "label": "Callback", "body": callback_line},
        {"id": "rule", "label": "House Rule", "body": house_rule},
        {"id": "action", "label": "Table Action", "body": table_action},
        {"id": "vote", "label": "Vote Prompt", "body": decision},
        {"id": "sting", "label": "Closing Sting", "body": sting},
        {"id": "full", "label": "Full Script", "body": script},
    ]
    return {
        "id": round_id,
        "round_number": round_number,
        "mode": mode,
        "weirdness": weirdness,
        "title": title,
        "location": place,
        "accused": player,
        "supporting_cast": [other],
        "relic": relic,
        "phrase": phrase,
        "callback": callback,
        "house_rule": house_rule,
        "setup": opener,
        "evidence": evidence,
        "escalation": escalation,
        "callback_line": callback_line,
        "table_action": table_action,
        "vote_prompt": decision,
        "closing_sting": sting,
        "read_aloud": read_aloud,
        "prime": prime,
        "trace": trace,
        "drift": drift,
        "collision": collision,
        "script": script,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def generate_finale(state: dict[str, Any]) -> dict[str, Any]:
    scores = state.get("scores") or {}
    players = _items(state.get("players"), ["Nobody"])
    contenders = list(players)
    for name in SPECIAL_SCORE_LABELS:
        if int(scores.get(name, 0)) > 0:
            contenders.append(name)
    winner = max(contenders, key=lambda name: int(scores.get(name, 0)))
    low_score = min(int(scores.get(name, 0)) for name in players)
    cursed = [name for name in players if int(scores.get(name, 0)) == low_score]
    rng = _rng_from_state(state, "finale", len(state.get("history") or []))
    relic = rng.choice(_items((state.get("ingredients") or {}).get("relics"), ["The Object"]))
    law = rng.choice(_items((state.get("ingredients") or {}).get("rules"), ["The winner must explain nothing."]))
    if winner == "The House":
        title = f"The House Wins {relic} In The Divorce"
        prophecy = f"From this day, The House may interrupt any argument by creaking at {relic}."
    elif winner == "The Relic":
        title = f"{relic}, Object Of The Night"
        prophecy = f"From this day, {relic} is allowed one dramatic silence per argument."
    else:
        title = f"{winner}, Keeper of {relic}"
        prophecy = f"From this day, {winner} may interrupt any argument by pointing at {relic}."
    curse = f"{', '.join(cursed)} must keep the official minutes until someone invents a worse system."
    scoreboard = ", ".join(f"{name}: {int(scores.get(name, 0))}" for name in contenders)
    script = "\n".join([
        title.upper(),
        "",
        f"Winner: {winner}",
        f"Final Relic: {relic}",
        f"Final Damage: {scoreboard}",
        "",
        prophecy,
        curse,
        "",
        "Final House Law:",
        law,
    ])
    return {
        "title": title,
        "winner": winner,
        "relic": relic,
        "prophecy": prophecy,
        "curse": curse,
        "law": law,
        "scoreboard": scoreboard,
        "script": script,
    }


def prime_trace(seed: int, prime: int, weirdness: int) -> list[int]:
    value = seed % prime
    step = max(2, (weirdness % (prime - 2)) + 2)
    offset = (weirdness // 7) + 1
    trace = []
    for index in range(7):
        value = (value * step + offset + index * index) % prime
        trace.append(value)
    return trace


def round_to_text(round_data: dict[str, Any]) -> str:
    return str(round_data.get("script") or "")


def round_to_html(round_data: dict[str, Any]) -> str:
    title = html.escape(str(round_data.get("title") or "Bantarama Round"))
    body = html.escape(round_to_text(round_data))
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title></head><body><pre>{body}</pre></body></html>"


def _status(count: int, minimum: int, ideal: int, blocked: str) -> dict[str, Any]:
    if count < minimum:
        level = "red"
        label = blocked
    elif count < ideal:
        level = "amber"
        label = "Playable. Add more for better chaos."
    else:
        level = "green"
        label = "Ready."
    return {"level": level, "count": count, "minimum": minimum, "ideal": ideal, "label": label}


def _next_step(checks: dict[str, dict[str, Any]], overall: str) -> str:
    for key in ["players", "phrases", "relics", "places", "rules"]:
        if checks[key]["level"] == "red":
            return checks[key]["label"]
    if overall == "amber":
        return "Ready, but one more ingredient will make it sharper."
    return "Start Round."


def _rng_from_state(state: dict[str, Any], *parts: object) -> random.Random:
    base = str(state.get("game_seed") or "bantarama")
    return random.Random(_stable_int(base, *parts))


def _stable_int(*parts: object) -> int:
    text = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _items(value: Any, fallback: list[str]) -> list[str]:
    if not isinstance(value, list):
        return fallback
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    return cleaned or fallback


def _choose_other(rng: random.Random, players: list[str], player: str) -> str:
    choices = [item for item in players if item != player]
    return rng.choice(choices or players)


def _format(template: str, data: dict[str, str]) -> str:
    return template.format(**data)


def _clamp_int(value: Any, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = low
    return max(low, min(high, number))


def _escalation(
    mode: str,
    rng: random.Random,
    player: str,
    other: str,
    relic: str,
    phrase: str,
    drift: str,
    collision: str,
    weirdness: int,
) -> str:
    data = {"player": player, "other": other, "relic": relic, "phrase": phrase}
    drift_line = _format(rng.choice(DRIFT_BEATS[drift]), data)
    collision_line = _format(rng.choice(COLLISION_BEATS[collision]), data)
    if weirdness >= 80:
        return f"{drift_line} {collision_line} By now, '{phrase}' is being treated as both evidence and weather."
    if mode == "Five-a-Side Incident":
        return f"{other} demands a replay, but {player} insists the pitch has accepted the myth. {drift_line}"
    if mode == "Under The Stairs":
        return f"{player} tries emotional honesty and accidentally nominates {relic} as chair. {collision_line}"
    if mode == "Relic Trial":
        return f"{relic} refuses to testify unless {other} stops looking so procedural. {drift_line}"
    if mode == "Cult Night":
        return f"{drift_line} {other} starts nodding in a way that suggests pamphlets."
    if mode == "Chaos Council":
        return f"{collision_line} The agenda becomes sentient for roughly one item."
    return f"{drift_line} {collision_line}"


def _decision(rng: random.Random, collision: str, player: str, other: str, relic: str, house_rule: str) -> str:
    template = rng.choice(VOTE_PROMPTS.get(collision, VOTE_PROMPTS["public_vote"]))
    return _format(template, {"player": player, "other": other, "relic": relic, "house_rule": house_rule})


def _duel_decision(rng: random.Random, collision: str, player: str, other: str, relic: str) -> str:
    templates = {
        "accusation": [
            "Duel ruling: did {player} survive the accusation, did {other} make the case, or did {relic} clearly win?",
            "Duel ruling: point to the survivor, the accuser, The House, or the object that caused all this.",
        ],
        "new_rule": [
            "Duel ruling: does the new law reward {player}, {other}, The House, or {relic}?",
            "Duel ruling: award the point to whoever must enforce this rule without blinking.",
        ],
        "betrayal": [
            "Duel ruling: who was betrayed harder, {player}, {other}, The House, or common sense?",
            "Duel ruling: compensation may go to the accused, the accuser, Everyone, or The House itself.",
        ],
        "committee": [
            "Duel ruling: appoint {player}, {other}, The House, or {relic} as chair of the pointless committee.",
            "Duel ruling: the committee point can go to a person, the room, or the object causing proceedings.",
        ],
        "confession": [
            "Duel ruling: who accidentally confessed, who heard it best, or did The House force the moment?",
            "Duel ruling: reward the confession, the witness, The House, or the object with confession lighting.",
        ],
        "public_vote": [
            "Duel ruling: pick the accused, the accuser, Everyone, The House, or The Relic.",
            "Duel ruling: this is not about fairness. It is about which option makes the room laugh again.",
        ],
    }
    return _format(rng.choice(templates.get(collision, templates["public_vote"])), {"player": player, "other": other, "relic": relic})


def _callback_target(
    rng: random.Random,
    state: dict[str, Any],
    player: str,
    other: str,
    relic: str,
    phrase: str,
) -> tuple[str, str]:
    history = state.get("history") or []
    previous_titles = [
        str((item.get("round") or {}).get("title") or "").strip()
        for item in history
        if isinstance(item, dict)
    ]
    previous_titles = [title for title in previous_titles if title]
    if previous_titles and rng.random() < 0.58:
        return rng.choice(previous_titles[-3:]), "history"
    choices = [(player, "player"), (other, "player"), (relic, "relic"), (phrase, "phrase")]
    return rng.choice(choices)


def _callback_line(rng: random.Random, callback: str, callback_kind: str) -> str:
    frames = HISTORY_CALLBACK_FRAMES if callback_kind == "history" else CALLBACK_FRAMES
    return _format(rng.choice(frames), {"callback": callback})


def _table_action(mode: str, rng: random.Random, player: str, other: str, relic: str, phrase: str, collision: str) -> str:
    data = {"player": player, "other": other, "relic": relic, "phrase": phrase}
    if collision == "confession":
        return f"{player} must explain why '{phrase}' is not technically a confession."
    if collision == "committee":
        return f"{other} appoints a committee of one, then hands it {relic}."
    if collision == "new_rule":
        return f"The host asks if anyone objects. Anyone who objects must improve the rule."
    mode_actions = MODE_TABLE_ACTIONS.get(mode, TABLE_ACTIONS)
    return _format(rng.choice(mode_actions), data)


def _title(mode: str, player: str, relic: str, phrase: str) -> str:
    short_phrase = phrase[:34].rstrip()
    if mode == "Cult Night":
        return f"The Small Cult of {short_phrase}"
    if mode == "Five-a-Side Incident":
        return f"{player}'s Goal With {relic}"
    if mode == "Relic Trial":
        return f"The Trial of {relic}"
    if mode == "Under The Stairs":
        return f"{player} Goes Under The Stairs"
    if mode == "Chaos Council":
        return f"The Emergency Council of {relic}"
    return f"The Rule About {relic}"
