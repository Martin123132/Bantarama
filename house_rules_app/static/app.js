const pages = ["start", "players", "packs", "ingredients", "setup", "round", "vote", "scoreboard", "finale"];
const ingredientLabels = {
  phrases: "phrase",
  relics: "object",
  places: "place",
  rules: "rule",
};
const packArtwork = {
  "builtin-family-chaos": "/static/media/packs/family-chaos.png",
  "builtin-pub-table": "/static/media/packs/pub-table.png",
  "builtin-office-nonsense": "/static/media/packs/office-nonsense.png",
  "builtin-tabletop-quest": "/static/media/packs/tabletop-quest.png",
};
const demoIngredients = {
  phrases: [
    "that is legally not a sandwich",
    "nobody check the cupboard",
    "the minutes have accepted this",
    "I object on furniture grounds",
  ],
  relics: [
    "The Emergency Chair",
    "A Damp Five-a-Side Bib",
    "Newton's suspicious notebook",
    "Pavarotti's ceremonial mug",
  ],
  places: [
    "under the stairs",
    "the five-a-side pitch",
    "the cupboard of public record",
    "the suspiciously formal sofa",
  ],
  rules: [
    "A phrase repeated three times becomes house law.",
    "Anyone holding the relic must speak first and regret it second.",
    "The accused may blame the furniture once.",
    "The host may demand a replay if the room points at them.",
  ],
};

let state = null;
let ready = null;
let currentPage = "start";
let currentIngredient = "phrases";
let currentRound = null;
let lastExport = null;
let packs = [];
let exportInProgress = false;

const el = (id) => document.getElementById(id);

async function api(path, payload = null) {
  const options = payload
    ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) }
    : {};
  const response = await fetch(path, options);
  const data = await response.json();
  if (!data.ok) {
    throw new Error(data.error || "Bantarama request failed");
  }
  return data;
}

async function loadState() {
  const data = await api("/api/state");
  state = data.state;
  ready = data.readiness;
  await loadPacks();
  el("doctorStatus").textContent = `Local only - v${data.version}`;
  syncControls();
  renderAll();
}

async function loadPacks() {
  const data = await api("/api/packs");
  packs = data.packs || [];
}

async function saveState() {
  const data = await api("/api/state", { state });
  state = data.state;
  ready = data.readiness;
  renderAll();
}

function setPage(page) {
  currentPage = page;
  for (const name of pages) {
    el(`page-${name}`).classList.toggle("active", name === page);
  }
  document.querySelectorAll(".step").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === page);
  });
  renderHostGuide();
}

function setMessage(text) {
  el("message").textContent = text || "";
}

function syncControls() {
  const settings = state.settings || {};
  el("toneSelect").value = settings.tone || "House Rules";
  el("roundCountInput").value = settings.round_count || 7;
  el("weirdnessInput").value = settings.weirdness || 62;
  el("weirdnessValue").textContent = settings.weirdness || 62;
}

function renderAll() {
  renderReadiness();
  renderPlayers();
  renderPacks();
  renderIngredients();
  renderSetup();
  renderScores();
  renderHistory();
  renderStartPreview();
  renderHostGuide();
}

function renderReadiness() {
  const checks = ready?.checks || {};
  const statusCopy = {
    red: "Add this",
    amber: "Playable",
    green: "Ready",
  };
  const labels = [
    ["players", "Players"],
    ["phrases", "Phrases"],
    ["relics", "Objects"],
    ["places", "Places"],
    ["rules", "Rules"],
  ];
  el("readinessStrip").innerHTML = labels
    .map(([key, label]) => {
      const item = checks[key] || { level: "red", count: 0, minimum: 1, label: "Missing" };
      const status = statusCopy[item.level] || item.level;
      return `<div class="light"><i class="dot ${item.level}"></i><div><strong>${label}: ${status}</strong><span>${item.count}/${item.minimum} minimum</span></div></div>`;
    })
    .join("");
}

function renderPlayers() {
  const players = state.players || [];
  const blocked = (ready?.checks?.players?.level || "red") === "red";
  el("playersList").innerHTML = players.length
    ? players.map((name) => `<div class="item"><strong>${escapeHtml(name)}</strong><button data-remove-player="${escapeHtml(name)}">Remove</button></div>`).join("")
    : `<div class="item"><span>Add at least 2 players.</span></div>`;
  el("playersNextButton").disabled = blocked;
  el("playersNextButton").textContent = blocked ? "Need 2 Players" : "Next";
  el("playersNextButton").title = blocked ? "Add at least two players before moving on." : "Go to chaos ingredients.";
}

function renderPacks() {
  const packGrid = el("packGrid");
  if (!packGrid) return;
  packGrid.innerHTML = packs.length
    ? packs
        .map((pack) => {
          const counts = pack.counts || {};
          const source = pack.source === "user" ? "Saved pack" : "Built-in";
          const players = (pack.players || []).length ? `${pack.players.length} players included` : "Keeps current players";
          const artwork = packArtwork[pack.id] || "/static/mark.svg";
          return `
            <article class="pack-card">
              <img class="pack-art" src="${artwork}" alt="" loading="lazy" />
              <div>
                <span>${escapeHtml(source)}</span>
                <h3>${escapeHtml(pack.name)}</h3>
                <p>${escapeHtml(pack.description || players)}</p>
              </div>
              <small>${players} | ${counts.phrases || 0} phrases | ${counts.relics || 0} objects | ${counts.places || 0} places | ${counts.rules || 0} rules</small>
              <button class="primary" data-apply-pack="${escapeHtml(pack.id)}">Load Pack</button>
            </article>
          `;
        })
        .join("")
    : `<div class="item"><span>No packs found yet.</span></div>`;
}

function renderIngredients() {
  const list = (state.ingredients && state.ingredients[currentIngredient]) || [];
  el("ingredientInput").placeholder = `Add ${ingredientLabels[currentIngredient]}`;
  el("ingredientsList").innerHTML = list.length
    ? list.map((text, index) => `<div class="item"><span>${escapeHtml(text)}</span><button data-remove-ingredient="${index}">Remove</button></div>`).join("")
    : `<div class="item"><span>Add one ${ingredientLabels[currentIngredient]}.</span></div>`;
}

function renderSetup() {
  const box = el("readyCallout");
  box.className = `ready-callout ${ready?.overall || "red"}`;
  box.textContent = ready?.next_step || "Add players.";
  const blocked = !ready?.can_start;
  el("startRoundButton").disabled = blocked;
  el("startRoundButton").textContent = blocked ? "Need More Fuel" : "Start Round";
  el("startRoundButton").title = blocked ? ready?.next_step || "Follow the red lights first." : "Generate the next round.";
}

function renderScores() {
  const players = state.players || [];
  const scores = state.scores || {};
  el("scoreboard").innerHTML = players.length
    ? players
        .map((name) => `<div class="score-card"><span>${escapeHtml(name)}</span><strong>${scores[name] || 0}</strong></div>`)
        .join("")
    : `<div class="score-card"><span>No players yet</span><strong>0</strong></div>`;
}

function renderHistory() {
  const history = state.history || [];
  el("historyList").innerHTML = history.length
    ? history
        .slice()
        .reverse()
        .map((item) => {
          const round = item.round || {};
          const winner = item.winner ? `Winner: ${escapeHtml(item.winner)}` : "No winner yet";
          return `<div class="history-item"><strong>${escapeHtml(round.title || "Round")}</strong><p>${winner}</p></div>`;
        })
        .join("")
    : `<div class="history-item"><strong>No rounds yet</strong><p>Start one when the lights are ready.</p></div>`;
}

function renderStartPreview() {
  const players = (state.players || []).length;
  const rounds = (state.history || []).length;
  el("startPreview").textContent = `${players} players | ${rounds} rounds played | ${ready?.next_step || "Ready when you are."}`;
}

function renderHostGuide() {
  if (!state || !ready) return;
  const checks = ready.checks || {};
  const players = state.players || [];
  const history = state.history || [];
  const missingIngredient = ["phrases", "relics", "places", "rules"].find((key) => (checks[key]?.level || "red") === "red");
  const pageText = {
    start: players.length
      ? ["amber", "Continue the table", "Carry on from the last game, or start fresh when you want a clean score."]
      : ["red", "Start with people", "Use New Game, then add at least two players. Demo Game fills the table instantly."],
    players: checks.players?.level === "red"
      ? ["red", "Add two players", "The game needs at least two names so it can accuse people properly."]
      : ["green", "Players are ready", "Move to Packs for a preset, or go on and tune the ingredients yourself."],
    packs: packs.length
      ? ["amber", "Pick or save a pack", "Load a built-in pack for fast table fuel, or save the current table as your own reusable pack."]
      : ["amber", "Pack library", "Built-in packs should appear here. You can still move on and edit ingredients by hand."],
    ingredients: missingIngredient
      ? ["red", `Add ${ingredientLabels[missingIngredient]}`, "Use the tabs here. One strong in-joke is better than ten bland ones."]
      : ["green", "The table has fuel", "Everything needed is lit. Move to Setup and choose the flavour of chaos."],
    setup: ready.can_start
      ? ["green", "Start the round", "Pick a mode, set weirdness, then press Start Round and read the result out loud."]
      : [ready.overall || "red", "Follow the red light", ready.next_step || "Add what is missing before the round starts."],
    round: currentRound
      ? ["green", "Read then vote", "Read the setup, evidence, callback, and table action. Then send everyone to Vote."]
      : ["amber", "No round yet", "Go back to Setup when the lights are ready."],
    vote: currentRound
      ? ["green", "Award the point", "Pick the player who deserves the point, or Everyone if the room was equally responsible."]
      : ["amber", "Vote after a round", "Generate a round first, then come back here."],
    scoreboard: history.length
      ? ["amber", "Keep or close", "Start another round, export the evidence, or finish with the Finale."]
      : ["amber", "No damage yet", "Play a round and vote before the scoreboard has anything useful to say."],
    finale: ["green", "Final house law", "Read this as the closing ruling, then start a new game when the room is ready."],
  };
  const [level, title, text] = pageText[currentPage] || ["amber", "Next best action", ready.next_step || "Keep following the lights."];
  el("hostGuide").className = `host-guide ${level}`;
  el("hostGuideDot").className = `dot ${level}`;
  el("hostGuideTitle").textContent = title;
  el("hostGuideText").textContent = text;
}

function renderRound(round) {
  currentRound = round;
  el("roundKicker").textContent = `Round ${round.round_number} | ${round.mode}`;
  el("roundTitle").textContent = round.title;
  el("roundScript").textContent = round.script;
  el("traceOutput").innerHTML = `
    <p>Prime field: Z${round.prime}</p>
    <p>Trace: ${round.trace.join(" -> ")}</p>
    <p>Drift: ${escapeHtml(round.drift)}</p>
    <p>Collision: ${escapeHtml(round.collision)}</p>
  `;
  renderVoteGrid();
  setPage("round");
}

function renderVoteGrid() {
  const players = state.players || [];
  el("voteGrid").innerHTML = players
    .map((name) => `<button data-vote="${escapeHtml(name)}"><strong>${escapeHtml(name)}</strong><br><span>Award 1 point</span></button>`)
    .join("");
}

function updateSettingsFromControls() {
  state.settings = {
    round_count: Number(el("roundCountInput").value || 7),
    tone: el("toneSelect").value,
    weirdness: Number(el("weirdnessInput").value || 62),
  };
}

async function startRound(regenerate = false) {
  updateSettingsFromControls();
  await saveState();
  const roundNumber = regenerate && currentRound ? currentRound.round_number : (state.history || []).length + 1;
  const data = await api("/api/round", {
    round_number: roundNumber,
    mode: state.settings.tone,
    weirdness: state.settings.weirdness,
    replace_round_id: regenerate && currentRound ? currentRound.id : "",
  });
  state = data.state;
  ready = data.readiness;
  renderAll();
  renderRound(data.round);
}

async function award(winner) {
  if (!currentRound) {
    setMessage("Start a round first.");
    return;
  }
  const data = await api("/api/award", { round_id: currentRound.id, winner, points: 1 });
  state = data.state;
  ready = data.readiness;
  renderAll();
  setPage("scoreboard");
}

async function showFinale() {
  const data = await api("/api/finale", {});
  el("finaleTitle").textContent = data.finale.title;
  el("finaleScript").textContent = data.finale.script;
  setPage("finale");
}

async function startDemoGame() {
  const data = await api("/api/new-game", {});
  state = data.state;
  state.players = ["Martin", "Newton", "Pavarotti", "Rocky"];
  state.scores = { Martin: 0, Newton: 0, Pavarotti: 0, Rocky: 0 };
  state.ingredients = demoIngredients;
  state.settings = { round_count: 7, tone: "House Rules", weirdness: 68 };
  const saved = await api("/api/state", { state });
  state = saved.state;
  ready = saved.readiness;
  currentRound = null;
  syncControls();
  renderAll();
  setMessage("Demo game loaded. Press Start Round when you are ready.");
  setPage("setup");
}

async function applyPack(packId) {
  const data = await api("/api/packs/apply", { pack_id: packId });
  state = data.state;
  ready = data.readiness;
  packs = data.packs || packs;
  currentRound = null;
  lastExport = null;
  syncControls();
  renderAll();
  setMessage("Pack loaded. You can tweak ingredients or start setup.");
  setPage("ingredients");
}

async function saveCurrentPack() {
  const name = el("packNameInput").value.trim();
  if (!name) {
    setMessage("Give the pack a name first.");
    return;
  }
  updateSettingsFromControls();
  const data = await api("/api/packs", { name, state });
  packs = data.packs || packs;
  el("packNameInput").value = "";
  renderPacks();
  setMessage(`Saved pack: ${data.pack.name}`);
}

async function exportGame(format) {
  if (exportInProgress) {
    setMessage("Export already running. Give it a second.");
    return;
  }
  exportInProgress = true;
  setExportButtons(true);
  try {
    const data = await api("/api/export", { format });
    lastExport = data.export;
    const savedFormat = String(data.export.format || format).toUpperCase();
    el("exportPanel").hidden = false;
    el("exportSummary").textContent = `Saved as ${savedFormat}. Use the folder button when you want to find it.`;
    el("exportPath").textContent = data.export.path;
    setMessage(`Export saved as ${savedFormat}.`);
  } finally {
    exportInProgress = false;
    setExportButtons(false);
  }
}

async function openExportsFolder() {
  const data = await api("/api/open-exports", {});
  if (data.open.opened) {
    setMessage(`Opened exports folder: ${data.open.path}`);
  } else {
    setMessage(`Could not open the folder automatically. Export folder: ${data.open.path}`);
  }
}

function setExportButtons(disabled) {
  el("exportTxtButton").disabled = disabled;
  el("exportHtmlButton").disabled = disabled;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

document.addEventListener("click", async (event) => {
  const target = event.target.closest("button");
  if (!target) return;

  if (target.dataset.page) setPage(target.dataset.page);
  if (target.dataset.removePlayer) {
    state.players = (state.players || []).filter((name) => name !== target.dataset.removePlayer);
    delete state.scores[target.dataset.removePlayer];
    await saveState();
  }
  if (target.dataset.removeIngredient !== undefined) {
    const index = Number(target.dataset.removeIngredient);
    state.ingredients[currentIngredient].splice(index, 1);
    await saveState();
  }
  if (target.dataset.ingredient) {
    currentIngredient = target.dataset.ingredient;
    document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.ingredient === currentIngredient));
    renderIngredients();
  }
  if (target.dataset.applyPack) await applyPack(target.dataset.applyPack);
  if (target.dataset.vote) await award(target.dataset.vote);
});

el("playerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = el("playerInput").value.trim();
  if (!name) return;
  state.players = [...(state.players || []), name];
  state.scores = { ...(state.scores || {}), [name]: state.scores?.[name] || 0 };
  el("playerInput").value = "";
  await saveState();
});

el("ingredientForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = el("ingredientInput").value.trim();
  if (!text) return;
  state.ingredients[currentIngredient] = [...(state.ingredients[currentIngredient] || []), text];
  el("ingredientInput").value = "";
  await saveState();
});

el("packForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  await saveCurrentPack().catch((error) => setMessage(error.message));
});

el("weirdnessInput").addEventListener("input", () => {
  el("weirdnessValue").textContent = el("weirdnessInput").value;
});

el("goPlayersButton").addEventListener("click", async () => {
  const data = await api("/api/new-game", {});
  state = data.state;
  ready = data.readiness;
  syncControls();
  renderAll();
  setPage("players");
});
el("continueButton").addEventListener("click", () => setPage("players"));
el("demoGameButton").addEventListener("click", () => startDemoGame().catch((error) => setMessage(error.message)));
el("playersBackButton").addEventListener("click", () => setPage("start"));
el("playersNextButton").addEventListener("click", () => setPage("packs"));
el("packsBackButton").addEventListener("click", () => setPage("players"));
el("packsNextButton").addEventListener("click", () => setPage("ingredients"));
el("ingredientsBackButton").addEventListener("click", () => setPage("packs"));
el("ingredientsNextButton").addEventListener("click", () => setPage("setup"));
el("setupBackButton").addEventListener("click", () => setPage("ingredients"));
el("startRoundButton").addEventListener("click", () => startRound(false).catch((error) => setMessage(error.message)));
el("regenerateRoundButton").addEventListener("click", () => startRound(true).catch((error) => setMessage(error.message)));
el("goVoteButton").addEventListener("click", () => setPage("vote"));
el("voteBackButton").addEventListener("click", () => setPage("round"));
el("everyoneButton").addEventListener("click", () => award("Everyone"));
el("nextRoundButton").addEventListener("click", () => setPage("setup"));
el("finaleButton").addEventListener("click", () => showFinale());
el("finaleScoresButton").addEventListener("click", () => setPage("scoreboard"));
el("newGameButton").addEventListener("click", async () => {
  const data = await api("/api/new-game", {});
  state = data.state;
  ready = data.readiness;
  currentRound = null;
  lastExport = null;
  el("exportPanel").hidden = true;
  syncControls();
  renderAll();
  setPage("players");
});
el("exportTxtButton").addEventListener("click", () => exportGame("txt"));
el("exportHtmlButton").addEventListener("click", () => exportGame("html"));
el("openExportsButton").addEventListener("click", () => openExportsFolder().catch((error) => setMessage(error.message)));

loadState().catch((error) => setMessage(error.message));
