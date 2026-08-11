/* Zero-dependency step-through visualizer.
 *
 * Page embeds <div class="viz"> with a child
 *   <script type="application/json" class="viz-data"> { ...trace... }
 * produced by the problem's trace.py (mirrors the verified solution).
 *
 * Trace shape (all fields optional except player + frames):
 *   player   "linear" | "tree"
 *   title    string
 *   acts     [labels]                       -> stage chips
 *   code     { blockName: [source lines] }  -> code panel
 *   legend   [[markClass, label]]           -> color key
 *   frames   [ frame ]
 * frame:
 *   act n | note s | banner s
 *   intro s (first frame of an act: "what to watch for")
 *   invariant s (what stays true this act)
 *   code "blockName", line n               -> highlight that source line
 *   state [[label, value]]                 -> live HUD
 *   linear: cells[], labels[], pointers{name:idx}, marks{idx:class},
 *           window[a,b], arc[a,b], sidebar{title,rows:[[k,v]]}
 *   tree:   nodes[{id,val,x,y}], edges[[a,b]], active[id], done{id:val}
 * A frame carrying cells/nodes rebuilds the scene, so a later act can run on a
 * different input (an edge case).
 */
(function () {
  "use strict";
  function el(t, c, p) { var e = document.createElement(t); if (c) e.className = c; if (p) p.appendChild(e); return e; }
  function svgEl(t) { return document.createElementNS("http://www.w3.org/2000/svg", t); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  var CELL = 52, GAP = 8, PAD = 16, ROW_Y = 78;

  function LinearRenderer(host) {
    var stage = el("div", "viz-stage", host);
    var svgWrap = el("div", "viz-svg-wrap", stage);
    var svg = svgEl("svg"); svg.setAttribute("class", "viz-svg"); svgWrap.appendChild(svg);
    var arc = svgEl("path"); arc.setAttribute("class", "viz-arc"); arc.style.opacity = 0; svg.appendChild(arc);
    var winRect = svgEl("rect"); winRect.setAttribute("class", "viz-window"); winRect.setAttribute("rx", 8); winRect.style.opacity = 0; svg.appendChild(winRect);
    var cellsG = svgEl("g"); svg.appendChild(cellsG);
    var ptrsG = svgEl("g"); svg.appendChild(ptrsG);
    var rail = el("div", "viz-rail", stage);
    var stateEl = el("div", "viz-state", rail);
    var sidebar = el("div", "viz-sidebar", rail);

    var n = 0, cellEls = [], key = "", ptrs = {}, ptrOrder = {};
    function cx(i) { return PAD + i * (CELL + GAP); }
    function mid(i) { return cx(i) + CELL / 2; }

    function buildRow(cells, labels) {
      var k = JSON.stringify([cells, labels || null]); if (k === key) return;
      key = k; n = cells.length;
      while (cellsG.firstChild) cellsG.removeChild(cellsG.firstChild);
      while (ptrsG.firstChild) ptrsG.removeChild(ptrsG.firstChild);
      ptrs = {}; ptrOrder = {}; cellEls = [];
      var width = PAD * 2 + n * CELL + Math.max(0, n - 1) * GAP;
      svg.setAttribute("viewBox", "0 -46 " + Math.max(width, 320) + " 210");
      for (var i = 0; i < n; i++) {
        var r = svgEl("rect");
        r.setAttribute("x", cx(i)); r.setAttribute("y", ROW_Y);
        r.setAttribute("width", CELL); r.setAttribute("height", CELL);
        r.setAttribute("rx", 8); r.setAttribute("class", "viz-cell");
        var t = svgEl("text"); t.setAttribute("x", mid(i)); t.setAttribute("y", ROW_Y + CELL / 2 + 6);
        t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "viz-cell-val"); t.textContent = cells[i];
        var lab = svgEl("text"); lab.setAttribute("x", mid(i)); lab.setAttribute("y", ROW_Y + CELL + 18);
        lab.setAttribute("text-anchor", "middle"); lab.setAttribute("class", "viz-cell-idx");
        lab.textContent = (labels && labels[i] != null) ? labels[i] : i;
        cellsG.appendChild(r); cellsG.appendChild(t); cellsG.appendChild(lab);
        cellEls.push(r);
      }
      winRect.setAttribute("y", ROW_Y - 6); winRect.setAttribute("height", CELL + 12);
    }
    function ptr(name) {
      if (ptrs[name]) return ptrs[name];
      var slot = Object.keys(ptrOrder).length; ptrOrder[name] = slot;
      var g = svgEl("g"); g.setAttribute("class", "viz-ptr");
      var nm = svgEl("text"); nm.setAttribute("x", CELL / 2); nm.setAttribute("y", -6 - slot * 13);
      nm.setAttribute("text-anchor", "middle"); nm.setAttribute("class", "viz-ptr-name"); nm.textContent = name;
      var tri = svgEl("path"); tri.setAttribute("d", "M " + (CELL / 2 - 7) + " 0 L " + (CELL / 2 + 7) + " 0 L " + (CELL / 2) + " 11 Z");
      tri.setAttribute("class", "viz-ptr-tri");
      g.appendChild(nm); g.appendChild(tri);
      g.setAttribute("transform", "translate(" + cx(0) + "," + (ROW_Y - 14) + ")");
      ptrsG.appendChild(g); ptrs[name] = g; return g;
    }

    return { render: function (f) {
      if (f.cells) buildRow(f.cells, f.labels || null);
      for (var i = 0; i < n; i++) cellEls[i].setAttribute("class", "viz-cell");
      var marks = f.marks || {};
      Object.keys(marks).forEach(function (k) { var idx = +k; if (cellEls[idx]) cellEls[idx].setAttribute("class", "viz-cell m-" + marks[k]); });
      var p = f.pointers || {}, seen = {};
      Object.keys(p).forEach(function (name) { seen[name] = 1; var g = ptr(name); g.style.opacity = 1; g.setAttribute("transform", "translate(" + cx(p[name]) + "," + (ROW_Y - 14) + ")"); });
      Object.keys(ptrs).forEach(function (name) { if (!seen[name]) ptrs[name].style.opacity = 0; });
      if (f.window && f.window.length === 2) {
        winRect.setAttribute("x", cx(f.window[0]) - 6);
        winRect.setAttribute("width", (cx(f.window[1]) + CELL) - cx(f.window[0]) + 12);
        winRect.style.opacity = 1;
      } else winRect.style.opacity = 0;
      if (f.arc && f.arc.length === 2) {
        var a = mid(f.arc[0]), b = mid(f.arc[1]), apex = ROW_Y - 40;
        arc.setAttribute("d", "M " + a + " " + (ROW_Y - 2) + " Q " + ((a + b) / 2) + " " + apex + " " + b + " " + (ROW_Y - 2));
        arc.style.opacity = 1;
      } else arc.style.opacity = 0;
      // rail: state HUD + map sidebar
      if (f.state && f.state.length) {
        stateEl.innerHTML = f.state.map(function (kv) {
          var isC = /count|comparison|work|checks/i.test(kv[0]);
          return '<div class="viz-state-row' + (isC ? ' work' : '') + '"><span>' + esc(kv[0]) + '</span><b>' + esc(kv[1]) + "</b></div>";
        }).join("");
        stateEl.style.display = "block";
      } else stateEl.style.display = "none";
      if (f.sidebar) {
        var rows = (f.sidebar.rows || []).map(function (r) { return "<tr><td>" + esc(r[0]) + "</td><td>" + esc(r[1]) + "</td></tr>"; }).join("");
        sidebar.innerHTML = '<div class="viz-sb-title">' + esc(f.sidebar.title || "") + "</div><table>" + rows + "</table>";
        sidebar.style.display = "block";
      } else sidebar.style.display = "none";
    }};
  }

  function TreeRenderer(host) {
    var stage = el("div", "viz-stage", host);
    var svgWrap = el("div", "viz-svg-wrap", stage);
    var svg = svgEl("svg"); svg.setAttribute("class", "viz-svg"); svgWrap.appendChild(svg);
    var edgesG = svgEl("g"); svg.appendChild(edgesG);
    var nodesG = svgEl("g"); svg.appendChild(nodesG);
    var rail = el("div", "viz-rail", stage);
    var stateEl = el("div", "viz-state", rail);
    var key = "", circEls = {}, badgeEls = {}, nodeList = [];
    function build(nodes, edges) {
      var k = JSON.stringify([nodes, edges]); if (k === key) return; key = k; nodeList = nodes;
      while (edgesG.firstChild) edgesG.removeChild(edgesG.firstChild);
      while (nodesG.firstChild) nodesG.removeChild(nodesG.firstChild);
      circEls = {}; badgeEls = {};
      var byId = {}; nodes.forEach(function (nd) { byId[nd.id] = nd; });
      var mX = 0, mY = 0; nodes.forEach(function (nd) { mX = Math.max(mX, nd.x); mY = Math.max(mY, nd.y); });
      svg.setAttribute("viewBox", "0 0 " + (mX + 60) + " " + (mY + 70));
      (edges || []).forEach(function (e) { var a = byId[e[0]], b = byId[e[1]]; var ln = svgEl("line"); ln.setAttribute("x1", a.x + 30); ln.setAttribute("y1", a.y + 30); ln.setAttribute("x2", b.x + 30); ln.setAttribute("y2", b.y + 30); ln.setAttribute("class", "viz-edge"); edgesG.appendChild(ln); });
      nodes.forEach(function (nd) {
        var c = svgEl("circle"); c.setAttribute("cx", nd.x + 30); c.setAttribute("cy", nd.y + 30); c.setAttribute("r", 22); c.setAttribute("class", "viz-node");
        var t = svgEl("text"); t.setAttribute("x", nd.x + 30); t.setAttribute("y", nd.y + 36); t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "viz-node-val"); t.textContent = nd.val;
        var badge = svgEl("text"); badge.setAttribute("x", nd.x + 56); badge.setAttribute("y", nd.y + 20); badge.setAttribute("text-anchor", "middle"); badge.setAttribute("class", "viz-node-badge");
        nodesG.appendChild(c); nodesG.appendChild(t); nodesG.appendChild(badge); circEls[nd.id] = c; badgeEls[nd.id] = badge;
      });
    }
    return { render: function (f) {
      if (f.nodes) build(f.nodes, f.edges || []);
      nodeList.forEach(function (nd) { circEls[nd.id].setAttribute("class", "viz-node"); });
      var active = f.active || [];
      active.forEach(function (id) { if (circEls[id]) circEls[id].setAttribute("class", "viz-node active"); });
      var done = f.done || {};
      nodeList.forEach(function (nd) { var v = done[nd.id]; badgeEls[nd.id].textContent = (v == null) ? "" : v; if (v != null && active.indexOf(nd.id) === -1) circEls[nd.id].setAttribute("class", "viz-node resolved"); });
      if (f.state && f.state.length) {
        stateEl.innerHTML = f.state.map(function (kv) { return '<div class="viz-state-row"><span>' + esc(kv[0]) + "</span><b>" + esc(kv[1]) + "</b></div>"; }).join("");
        stateEl.style.display = "block";
      } else stateEl.style.display = "none";
    }};
  }

  function build(mount) {
    var dataEl = mount.querySelector("script.viz-data"); if (!dataEl) return;
    var trace; try { trace = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var frames = trace.frames || []; if (!frames.length) return;

    if (trace.title) el("div", "viz-title", mount).textContent = trace.title;
    var actEls = [];
    if (trace.acts && trace.acts.length) {
      var bar = el("div", "viz-acts", mount);
      trace.acts.forEach(function (label, i) { var s = el("span", "viz-act", bar); s.textContent = (i + 1) + ". " + label; actEls.push(s); });
    }
    var intro = el("div", "viz-intro", mount); intro.style.display = "none";
    var invar = el("div", "viz-invariant", mount); invar.style.display = "none";

    var cols = el("div", "viz-cols", mount);
    var left = el("div", "viz-left", cols);
    var host = el("div", "viz-host", left);
    var render = (trace.player === "tree") ? TreeRenderer(host) : LinearRenderer(host);
    var note = el("div", "viz-note", left);
    var banner = el("div", "viz-banner", left); banner.style.display = "none";
    var codeEl = el("pre", "viz-code", cols); codeEl.style.display = "none";

    if (trace.legend && trace.legend.length) {
      var lg = el("div", "viz-legend", mount);
      trace.legend.forEach(function (pair) { var s = el("span", "viz-legend-item", lg); s.innerHTML = '<i class="sw m-' + pair[0] + '"></i>' + esc(pair[1]); });
    }

    // precompute per-act intro / invariant (first occurrence carries the act)
    var introByAct = {}, invByAct = {};
    frames.forEach(function (f) { var a = f.act || 0; if (f.intro && introByAct[a] == null) introByAct[a] = f.intro; if (f.invariant && invByAct[a] == null) invByAct[a] = f.invariant; });

    var controls = el("div", "viz-controls", mount);
    var back = el("button", "viz-btn", controls); back.textContent = "◀";
    var play = el("button", "viz-btn viz-play", controls); play.textContent = "▶ Play";
    var fwd = el("button", "viz-btn", controls); fwd.textContent = "▶";
    var speed = el("select", "viz-speed", controls);
    [["0.5", "0.5×"], ["1", "1×"], ["1.5", "1.5×"], ["2", "2×"]].forEach(function (o) { var op = el("option", null, speed); op.value = o[0]; op.textContent = o[1]; if (o[0] === "1") op.selected = true; });
    var scrub = el("input", "viz-scrub", controls); scrub.type = "range"; scrub.min = 0; scrub.max = frames.length - 1; scrub.value = 0;
    var counter = el("span", "viz-counter", controls);

    function renderCode(f) {
      if (f.code && trace.code && trace.code[f.code]) {
        codeEl.innerHTML = trace.code[f.code].map(function (ln, i) { return '<span class="viz-code-line' + (i === f.line ? " active" : "") + '">' + (esc(ln) || " ") + "</span>"; }).join("");
        codeEl.style.display = "block";
      } else codeEl.style.display = "none";
    }

    var idx = 0, timer = null;
    function show(i) {
      idx = Math.max(0, Math.min(frames.length - 1, i));
      var f = frames[idx], act = f.act || 0;
      render.render(f);
      note.textContent = f.note || "";
      if (f.banner) { banner.textContent = f.banner; banner.style.display = "block"; } else banner.style.display = "none";
      renderCode(f);
      if (introByAct[act] != null) { intro.textContent = "Watch for: " + introByAct[act]; intro.style.display = "block"; } else intro.style.display = "none";
      if (invByAct[act] != null) { invar.innerHTML = "<b>Always true here:</b> " + esc(invByAct[act]); invar.style.display = "block"; } else invar.style.display = "none";
      actEls.forEach(function (s, k) { s.className = "viz-act" + (k === act ? " active" : (k < act ? " done" : "")); });
      scrub.value = idx; counter.textContent = (idx + 1) + " / " + frames.length;
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } play.textContent = "▶ Play"; }
    function start() {
      if (idx >= frames.length - 1) show(0);
      play.textContent = "⏸ Pause";
      var ms = 1250 / parseFloat(speed.value);
      timer = setInterval(function () { if (idx >= frames.length - 1) { stop(); return; } show(idx + 1); }, ms);
    }
    play.onclick = function () { timer ? stop() : start(); };
    back.onclick = function () { stop(); show(idx - 1); };
    fwd.onclick = function () { stop(); show(idx + 1); };
    speed.onchange = function () { if (timer) { stop(); start(); } };
    scrub.oninput = function () { stop(); show(+scrub.value); };
    show(0);
  }

  function init() { var m = document.querySelectorAll(".viz"); for (var i = 0; i < m.length; i++) build(m[i]); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
