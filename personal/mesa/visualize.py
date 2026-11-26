"""Generate a standalone interactive HTML view of a Mesa run."""

import json
from pathlib import Path
from typing import Any


def _script_json(data: dict[str, Any]) -> str:
  return (
    json.dumps(data, ensure_ascii=False)
    .replace("&", "\\u0026")
    .replace("<", "\\u003c")
    .replace(">", "\\u003e")
    .replace("\u2028", "\\u2028")
    .replace("\u2029", "\\u2029")
  )


def render_html(data: dict[str, Any]) -> str:
  if not isinstance(data.get("mode"), str) or data["mode"] not in {
    "subjective", "objective",
  }:
    raise ValueError("output JSON must include mode as 'subjective' or 'objective'")

  embedded_data = _script_json(data)
  return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Opinion dynamics</title>
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['\\\\(', '\\\\)'], ['$', '$']],
        displayMath: [['\\\\[', '\\\\]'], ['$$', '$$']]
      },
      options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }
    };
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
  <style>
    :root {
      color-scheme: light;
      font: 16px/1.5 system-ui, sans-serif;
      color: #202124;
      background: #f7f8fa;
    }
    * { box-sizing: border-box; }
    body { max-width: 1200px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }
    h1 { margin: 0 0 2.5rem; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.1; }
    h2 { margin: 2rem 0 1rem; }
    h3 { margin-top: 0; }
    .panel { padding: 1.25rem; border: 1px solid #dfe1e5; border-radius: 12px; background: white; }
    button { font: inherit; }
    .legend { display: flex; gap: .6rem 1.2rem; flex-wrap: wrap; margin: .75rem 0 1rem; }
    .legend span { display: inline-flex; align-items: center; gap: .4rem; }
    .swatch { display: inline-block; width: 1rem; height: 1rem; border: 1px solid #777; border-radius: 3px; }
    .edge-swatch { display: inline-block; width: 1.25rem; border-top-width: 3px; border-top-style: solid; }
    .edge-swatch.concordant { border-top-color: #218739; }
    .edge-swatch.discordant { border-top-color: #c62828; border-top-style: dotted; }
    .heatmap-scroll { overflow-x: auto; padding-bottom: .5rem; }
    .heatmap-layout { display: grid; grid-template-columns: 250px max-content; gap: .75rem; width: max-content; }
    .network-heading { height: 48px; display: flex; align-items: center; font-weight: 650; font-size: .9rem; }
    #network { display: block; width: 250px; }
    .network-edge, .network-node { transition: opacity .12s, stroke-width .12s, r .12s; }
    .network-edge { cursor: pointer; pointer-events: stroke; }
    .network-node { cursor: crosshair; }
    table { border-collapse: collapse; table-layout: fixed; }
    th, td { height: 48px; padding: .25rem; text-align: center; border: 1px solid #e1e3e6; }
    thead th { background: #f1f3f4; font-weight: 650; }
    th.agent-heading, td.agent-label { width: 120px; }
    th.step-heading, td.spin-cell { width: 76px; }
    td.agent-label { padding: .2rem .5rem; text-align: left; background: white; }
    .agent-label button { border: 0; padding: .35rem .45rem; color: #174ea6; background: transparent; text-decoration: underline; cursor: pointer; }
    .spin-cell { font-weight: 650; }
    .neutral { color: #555; background: #eee; }
    .persona-panel { margin-top: 1rem; }
    .persona-panel header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
    .persona-panel h3 { margin: 0; }
    .persona-text { white-space: pre-wrap; overflow-wrap: anywhere; }
    .persona-text mjx-container[display="true"] { max-width: 100%; overflow-x: auto; overflow-y: hidden; }
    .timeline-controls { display: flex; align-items: center; gap: 1rem; }
    #step-slider { flex: 1; min-width: 120px; }
    #message-list { display: grid; gap: .75rem; margin-top: 1rem; }
    .message-card { padding: .9rem 1rem; border-left: 4px solid #8ab4f8; border-radius: 4px; background: #f8fafd; }
    .message-card h3 { margin: 0 0 .4rem; font-size: 1rem; }
    .message-card p { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
    .muted { color: #5f6368; }
    @media (max-width: 600px) {
      body { padding: 1.25rem .75rem 3rem; }
      .panel { padding: .85rem; }
    }
  </style>
</head>
<body>
  <main>
    <header><h1 id="question"></h1></header>
    <header><h3 id="choices"></h3></header>
    <section aria-labelledby="dynamics-heading">
      <h2 id="dynamics-heading">Opinion Dynamics</h2>
      <div class="panel">
        <div id="legend" class="legend" aria-label="Heatmap legend"></div>
        <div class="heatmap-scroll">
          <div class="heatmap-layout">
            <div>
              <div id="network-heading" class="network-heading">Connections · hover to trace</div>
              <svg id="network" role="img" aria-label="Agent connection graph"></svg>
            </div>
            <table aria-label="Agent opinions by step">
              <thead id="heatmap-head"></thead>
              <tbody id="heatmap-body"></tbody>
            </table>
          </div>
        </div>
        <aside id="persona-panel" class="persona-panel panel" hidden>
          <header>
            <h3 id="persona-title"></h3>
            <button id="persona-close" type="button">Close</button>
          </header>
          <p id="persona-text" class="persona-text"></p>
        </aside>
      </div>
    </section>
    <section aria-labelledby="timeline-heading">
      <h2 id="timeline-heading">Message Timeline</h2>
      <div class="panel">
        <div class="timeline-controls">
          <button id="previous-step" type="button" aria-label="Previous step">&larr;</button>
          <label id="timeline-label" for="step-slider">Step 1</label>
          <input id="step-slider" type="range" min="1" max="1" value="1">
          <button id="next-step" type="button" aria-label="Next step">&rarr;</button>
        </div>
        <div id="message-list" aria-live="polite"></div>
      </div>
    </section>
  </main>
  <script>
    const data = __RUN_DATA__;
    const agents = Array.isArray(data.agents) ? data.agents : [];
    const matrix = Array.isArray(data.J) ? data.J : [];
    const mode = data.mode;
    const spinSteps = agents.reduce(
      (max, agent) => Math.max(
        max,
        Array.isArray(agent.spins) ? agent.spins.length : 0
      ),
      0
    );
    const messageSteps = agents.reduce(
      (max, agent) => Math.max(
        max,
        Array.isArray(agent.messages) ? agent.messages.length : 0
      ),
      0
    );
    const hasInitialSpin = spinSteps === messageSteps + 1;
    const head = document.getElementById("heatmap-head");
    const body = document.getElementById("heatmap-body");
    const network = document.getElementById("network");
    const rowHeight = 48;
    const graphWidth = 250;
    const svgNS = "http://www.w3.org/2000/svg";
    let highlightConnections = () => {};
    let resetConnections = () => {};

    document.getElementById("question").textContent = data.question || "Opinion dynamics";
    const choices = Object.entries(data.choices || {});
    const choicesHeading = document.getElementById("choices");
    choicesHeading.hidden = choices.length === 0;
    if (choices.length) {
      choicesHeading.textContent =
        "Choices: " + choices.map(([key, value]) => `${key}: ${value}`).join(" | ");
    }

    
    function addLegend() {
      const entries = mode === "objective"
        ? [["#cfe5ff", "Option A"], ["#fff0a6", "Option B"]]
        : [["#ccebd3", "Agree"], ["#f5cccc", "Disagree"]];
      const legend = document.getElementById("legend");
      legend.replaceChildren();
      for (const [color, label] of entries) {
        const item = document.createElement("span");
        const swatch = document.createElement("i");
        swatch.className = "swatch";
        swatch.style.backgroundColor = color;
        item.append(swatch, document.createTextNode(label));
        legend.append(item);
      }
      const noOpinion = document.createElement("span");
      const neutralSwatch = document.createElement("i");
      neutralSwatch.className = "swatch";
      neutralSwatch.style.backgroundColor = "#eee";
      noOpinion.append(neutralSwatch, document.createTextNode("No Opinion"));
      legend.append(noOpinion);

      for (const [color, label] of [
        ["concordant", "Concordant link"],
        ["discordant", "Discordant link"]
      ]) {
        const item = document.createElement("span");
        const swatch = document.createElement("i");
        swatch.className = `edge-swatch ${color}`;
        item.append(swatch, document.createTextNode(label));
        legend.append(item);
      }
    }

    function makeSvgElement(name, attributes) {
      const element = document.createElementNS(svgNS, name);
      for (const [key, value] of Object.entries(attributes)) {
        element.setAttribute(key, value);
      }
      return element;
    }

    function renderNetwork() {
      const height = agents.length * rowHeight;
      network.replaceChildren();
      network.setAttribute("viewBox", `0 0 ${graphWidth} ${height || rowHeight}`);
      network.setAttribute("height", String(height || rowHeight));
      const heading = document.getElementById("network-heading");

      function resetHighlight() {
        heading.textContent = "Connections · hover to trace";
        heading.title = "Hover an edge or agent label to trace its links.";
        for (const edge of network.querySelectorAll(".network-edge")) {
          edge.style.opacity = "0.75";
          edge.style.strokeWidth = "2";
        }
        for (const node of network.querySelectorAll(".network-node")) {
          node.setAttribute("fill", "white");
          node.setAttribute("r", "7");
        }
      }

      function highlightAgent(position) {
        const agent = agents[position];
        const linked = [];
        for (let other = 0; other < agents.length; other++) {
          if (other !== position && Number(matrix[position]?.[other] || 0) !== 0) {
            linked.push(agents[other].index);
          }
        }
        heading.textContent = linked.length
          ? `agent ${agent.index}: ${linked.length} links highlighted`
          : `agent ${agent.index} has no links`;
        heading.title = linked.length
          ? `agent ${agent.index} linked to ${linked.map((index) => `agent ${index}`).join(", ")}`
          : heading.textContent;
        for (const edge of network.querySelectorAll(".network-edge")) {
          const incident =
            edge.dataset.source === String(agent.index) ||
            edge.dataset.target === String(agent.index);
          edge.style.opacity = incident ? "1" : "0.08";
          edge.style.strokeWidth = incident ? "3.5" : "1.5";
        }
        for (const node of network.querySelectorAll(".network-node")) {
          const selected = node.dataset.agent === String(agent.index);
          node.setAttribute("fill", selected ? "#fbbc04" : "white");
          node.setAttribute("r", selected ? "9" : "7");
        }
      }

      function highlightEdge(edge, source, target) {
        heading.textContent = `agent ${source} linked to agent ${target}`;
        heading.title = heading.textContent;
        for (const candidate of network.querySelectorAll(".network-edge")) {
          const active = candidate === edge;
          candidate.style.opacity = active ? "1" : "0.08";
          candidate.style.strokeWidth = active ? "4" : "1.5";
        }
      }
      highlightConnections = highlightAgent;
      resetConnections = resetHighlight;

      for (let i = 0; i < agents.length; i++) {
        for (let j = i + 1; j < agents.length; j++) {
          const value = Number(matrix[i]?.[j] || 0);
          if (value === 0) continue;
          const x1 = i % 2 === 0 ? 36 : graphWidth - 36;
          const x2 = j % 2 === 0 ? 36 : graphWidth - 36;
          const y1 = (i + 0.5) * rowHeight;
          const y2 = (j + 0.5) * rowHeight;
          const lane = 24 + ((i * agents.length + j) / (agents.length ** 2)) * (graphWidth - 48);
          const edge = makeSvgElement("path", {
            d: `M ${x1} ${y1} Q ${lane} ${(y1 + y2) / 2} ${x2} ${y2}`,
            class: "network-edge",
            "data-source": agents[i].index,
            "data-target": agents[j].index,
            fill: "none",
            stroke: value > 0 ? "#218739" : "#c62828",
            "stroke-width": "2",
            "stroke-opacity": "0.75",
            "stroke-dasharray": value < 0 ? "1 5" : "none",
            "stroke-linecap": "round",
            "stroke-linejoin": "round"
          });
          const title = makeSvgElement("title", {});
          title.textContent = `agent ${agents[i].index} ↔ agent ${agents[j].index}: J = ${value}`;
          edge.append(title);
          edge.addEventListener("pointerenter", () => {
            highlightEdge(edge, agents[i].index, agents[j].index);
          });
          edge.addEventListener("pointerleave", resetHighlight);
          network.append(edge);
        }
      }
      for (let i = 0; i < agents.length; i++) {
        const circle = makeSvgElement("circle", {
          class: "network-node",
          "data-agent": agents[i].index,
          cx: i % 2 === 0 ? 36 : graphWidth - 36,
          cy: (i + 0.5) * rowHeight,
          r: "7",
          fill: "white",
          stroke: "#3c4043",
          "stroke-width": "2"
        });
        const title = makeSvgElement("title", {});
        title.textContent = `agent ${agents[i].index}`;
        circle.append(title);
        circle.addEventListener("pointerenter", () => highlightAgent(i));
        circle.addEventListener("pointerleave", resetHighlight);
        network.append(circle);
      }
      resetHighlight();
    }

    function renderHeatmap() {
      addLegend();
      head.replaceChildren();
      body.replaceChildren();

      const headerRow = document.createElement("tr");
      const agentHeading = document.createElement("th");
      agentHeading.className = "agent-heading";
      agentHeading.scope = "col";
      agentHeading.textContent = "Agent";
      headerRow.append(agentHeading);
      for (let step = 0; step < spinSteps; step++) {
        const th = document.createElement("th");
        th.className = "step-heading";
        th.scope = "col";
        th.textContent = hasInitialSpin && step === 0
          ? "Initial"
          : `Step ${hasInitialSpin ? step : step + 1}`;
        headerRow.append(th);
      }
      head.append(headerRow);

      for (const agent of agents) {
        const row = document.createElement("tr");
        const label = document.createElement("td");
        label.className = "agent-label";
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = `agent ${agent.index}`;
        button.addEventListener("click", () => showPersona(agent));
        button.addEventListener("pointerenter", () => {
          highlightConnections(agents.indexOf(agent));
        });
        button.addEventListener("pointerleave", resetConnections);
        button.addEventListener("focus", () => {
          highlightConnections(agents.indexOf(agent));
        });
        button.addEventListener("blur", resetConnections);
        label.append(button);
        row.append(label);

        for (let step = 0; step < spinSteps; step++) {
          const spin = agent.spins?.[step];
          const cell = document.createElement("td");
          cell.className = "spin-cell";
          if (spin === 1 || spin === -1) {
            if (mode === "objective") {
              cell.textContent = spin === 1 ? "A" : "B";
              cell.style.backgroundColor = spin === 1 ? "#cfe5ff" : "#fff0a6";
            } else {
              cell.textContent = spin === 1 ? "Agree" : "Disagree";
              cell.style.backgroundColor = spin === 1 ? "#ccebd3" : "#f5cccc";
            }
          } else {
            cell.classList.add("neutral");
            cell.textContent = spin === 0 ? "Undecided" : "—";
          }
          const timeLabel = hasInitialSpin && step === 0
            ? "initial"
            : `step ${hasInitialSpin ? step : step + 1}`;
          cell.title = `agent ${agent.index}, ${timeLabel}: ${cell.textContent}`;
          row.append(cell);
        }
        body.append(row);
      }
    }

    const personaPanel = document.getElementById("persona-panel");
    function clearMath(element) {
      if (window.MathJax?.typesetClear) {
        window.MathJax.typesetClear([element]);
      }
    }
    function typesetMath(element) {
      if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise([element]);
      }
    }
    function showPersona(agent) {
      document.getElementById("persona-title").textContent = `agent ${agent.index}`;
      const personaText = document.getElementById("persona-text");
      clearMath(personaText);
      personaText.textContent = agent.persona || "";
      personaPanel.hidden = false;
      typesetMath(personaText);
    }
    window.addEventListener("load", () => {
      const personaText = document.getElementById("persona-text");
      if (!personaPanel.hidden) typesetMath(personaText);
      typesetMath(messageList);
    });
    document.getElementById("persona-close").addEventListener("click", () => {
      personaPanel.hidden = true;
    });

    const slider = document.getElementById("step-slider");
    const timelineLabel = document.getElementById("timeline-label");
    const messageList = document.getElementById("message-list");
    slider.max = String(Math.max(messageSteps, 1));
    slider.disabled = messageSteps === 0;

    function renderMessages() {
      const step = Number(slider.value) - 1;
      timelineLabel.textContent = messageSteps ? `Step ${step + 1}` : "No messages";
      clearMath(messageList);
      messageList.replaceChildren();
      if (!messageSteps) {
        messageList.textContent = "No message history is available.";
        return;
      }
      for (const agent of agents) {
        const message = agent.messages?.[step];
        if (message === undefined) continue;
        const card = document.createElement("article");
        card.className = "message-card";
        const title = document.createElement("h3");
        title.textContent = `agent ${agent.index}`;
        const text = document.createElement("p");
        text.textContent = message;
        card.append(title, text);
        messageList.append(card);
      }
      if (!messageList.childElementCount) {
        messageList.textContent = "No messages were recorded for this step.";
      }
      typesetMath(messageList);
    }

    slider.addEventListener("input", renderMessages);
    document.getElementById("previous-step").addEventListener("click", () => {
      slider.value = String(Math.max(1, Number(slider.value) - 1));
      renderMessages();
    });
    document.getElementById("next-step").addEventListener("click", () => {
      slider.value = String(Math.min(messageSteps, Number(slider.value) + 1));
      renderMessages();
    });
    renderNetwork();
    renderHeatmap();
    renderMessages();
  </script>
</body>
</html>
""".replace("__RUN_DATA__", embedded_data)


def write_html_report(data: dict[str, Any], output_path: Path) -> None:
  output_path.write_text(render_html(data), encoding="utf-8")


def main() -> None:
  output_path = Path(__file__).with_name("output.json")
  with output_path.open(encoding="utf-8") as file:
    data = json.load(file)
  write_html_report(data, output_path.with_suffix(".html"))


if __name__ == "__main__":
  main()
