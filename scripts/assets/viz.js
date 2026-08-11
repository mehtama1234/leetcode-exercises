/* Zero-dependency step-through visualizer.
 *
 * Each problem page embeds <div class="viz"> whose child
 * <script type="application/json" class="viz-data"> holds a trace:
 *   { player:"linear"|"tree", title, acts:[labels], frames:[ {act, note, ...} ] }
 * The trace is produced by the problem's trace.py, which mirrors the verified
 * solution — so what you watch is what the code does.
 *
 * A frame may carry a new SCENE (linear: cells/labels; tree: nodes/edges); when
 * it changes, the structure is rebuilt — this lets a later act run the same idea
 * on a different input (e.g. an edge case). Otherwise a frame only nudges
 * positions/classes, so moves animate via CSS transitions.
 * "acts" drives the labeled stage chips (Brute force -> The waste -> Fast -> ...).
 */
(function () {
  "use strict";

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }
  function svgEl(tag) { return document.createElementNS("http://www.w3.org/2000/svg", tag); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  var CELL = 52, GAP = 8, PAD = 16, ROW_Y = 70;

  // ---------- linear renderer: array / pointers / window / sidebar ----------
  function LinearRenderer(host) {
    var stage = el("div", "viz-stage", host);
    var svgWrap = el("div", "viz-svg-wrap", stage);
    var svg = svgEl("svg"); svg.setAttribute("class", "viz-svg"); svgWrap.appendChild(svg);
    var winRect = svgEl("rect");
    winRect.setAttribute("class", "viz-window"); winRect.setAttribute("rx", 8);
    winRect.style.opacity = 0; svg.appendChild(winRect);
    var cellsG = svgEl("g"); svg.appendChild(cellsG);
    var ptrsG = svgEl("g"); svg.appendChild(ptrsG);
    var sidebar = el("div", "viz-sidebar", stage);

    var n = 0, cellEls = [], key = "", ptrs = {}, ptrOrder = {};
    function cx(i) { return PAD + i * (CELL + GAP); }

    function buildRow(cells, labels) {
      var k = JSON.stringify([cells, labels || null]);
      if (k === key) return;
      key = k; n = cells.length;
      while (cellsG.firstChild) cellsG.removeChild(cellsG.firstChild);
      while (ptrsG.firstChild) ptrsG.removeChild(ptrsG.firstChild);
      ptrs = {}; ptrOrder = {}; cellEls = [];
      var width = PAD * 2 + n * CELL + Math.max(0, n - 1) * GAP;
      svg.setAttribute("viewBox", "0 0 " + Math.max(width, 320) + " 152");
      for (var i = 0; i < n; i++) {
        var r = svgEl("rect");
        r.setAttribute("x", cx(i)); r.setAttribute("y", ROW_Y);
        r.setAttribute("width", CELL); r.setAttribute("height", CELL);
        r.setAttribute("rx", 8); r.setAttribute("class", "viz-cell");
        var t = svgEl("text");
        t.setAttribute("x", cx(i) + CELL / 2); t.setAttribute("y", ROW_Y + CELL / 2 + 6);
        t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "viz-cell-val");
        t.textContent = cells[i];
        var lab = svgEl("text");
        lab.setAttribute("x", cx(i) + CELL / 2); lab.setAttribute("y", ROW_Y + CELL + 18);
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
      var nm = svgEl("text");
      nm.setAttribute("x", CELL / 2); nm.setAttribute("y", -6 - slot * 13);
      nm.setAttribute("text-anchor", "middle"); nm.setAttribute("class", "viz-ptr-name");
      nm.textContent = name;
      var tri = svgEl("path");
      tri.setAttribute("d", "M " + (CELL / 2 - 7) + " 0 L " + (CELL / 2 + 7) + " 0 L " + (CELL / 2) + " 11 Z");
      tri.setAttribute("class", "viz-ptr-tri");
      g.appendChild(nm); g.appendChild(tri);
      g.setAttribute("transform", "translate(" + cx(0) + "," + (ROW_Y - 14) + ")");
      ptrsG.appendChild(g); ptrs[name] = g;
      return g;
    }

    return { render: function (f) {
      if (f.cells) buildRow(f.cells, f.labels || null);
      for (var i = 0; i < n; i++) cellEls[i].setAttribute("class", "viz-cell");
      var marks = f.marks || {};
      Object.keys(marks).forEach(function (k) {
        var idx = +k; if (cellEls[idx]) cellEls[idx].setAttribute("class", "viz-cell m-" + marks[k]);
      });
      var p = f.pointers || {}, seen = {};
      Object.keys(p).forEach(function (name) {
        seen[name] = 1; var g = ptr(name); g.style.opacity = 1;
        g.setAttribute("transform", "translate(" + cx(p[name]) + "," + (ROW_Y - 14) + ")");
      });
      Object.keys(ptrs).forEach(function (name) { if (!seen[name]) ptrs[name].style.opacity = 0; });
      if (f.window && f.window.length === 2) {
        var a = f.window[0], b = f.window[1];
        winRect.setAttribute("x", cx(a) - 6);
        winRect.setAttribute("width", (cx(b) + CELL) - cx(a) + 12);
        winRect.style.opacity = 1;
      } else { winRect.style.opacity = 0; }
      if (f.sidebar) {
        var rows = (f.sidebar.rows || []).map(function (r) {
          return "<tr><td>" + esc(r[0]) + "</td><td>" + esc(r[1]) + "</td></tr>";
        }).join("");
        sidebar.innerHTML = '<div class="viz-sb-title">' + esc(f.sidebar.title || "") +
          "</div><table>" + rows + "</table>";
        sidebar.style.display = "block";
      } else { sidebar.style.display = "none"; }
    }};
  }

  // ---------------- tree renderer: nodes at x,y; active + resolved ----------------
  function TreeRenderer(host) {
    var stage = el("div", "viz-stage", host);
    var svgWrap = el("div", "viz-svg-wrap", stage);
    var svg = svgEl("svg"); svg.setAttribute("class", "viz-svg"); svgWrap.appendChild(svg);
    var edgesG = svgEl("g"); svg.appendChild(edgesG);
    var nodesG = svgEl("g"); svg.appendChild(nodesG);
    var key = "", circEls = {}, badgeEls = {}, nodeList = [];

    function build(nodes, edges) {
      var k = JSON.stringify([nodes, edges]);
      if (k === key) return;
      key = k; nodeList = nodes;
      while (edgesG.firstChild) edgesG.removeChild(edgesG.firstChild);
      while (nodesG.firstChild) nodesG.removeChild(nodesG.firstChild);
      circEls = {}; badgeEls = {};
      var byId = {}; nodes.forEach(function (nd) { byId[nd.id] = nd; });
      var maxX = 0, maxY = 0;
      nodes.forEach(function (nd) { maxX = Math.max(maxX, nd.x); maxY = Math.max(maxY, nd.y); });
      svg.setAttribute("viewBox", "0 0 " + (maxX + 60) + " " + (maxY + 70));
      (edges || []).forEach(function (e) {
        var a = byId[e[0]], b = byId[e[1]];
        var ln = svgEl("line");
        ln.setAttribute("x1", a.x + 30); ln.setAttribute("y1", a.y + 30);
        ln.setAttribute("x2", b.x + 30); ln.setAttribute("y2", b.y + 30);
        ln.setAttribute("class", "viz-edge"); edgesG.appendChild(ln);
      });
      nodes.forEach(function (nd) {
        var c = svgEl("circle");
        c.setAttribute("cx", nd.x + 30); c.setAttribute("cy", nd.y + 30);
        c.setAttribute("r", 22); c.setAttribute("class", "viz-node");
        var t = svgEl("text");
        t.setAttribute("x", nd.x + 30); t.setAttribute("y", nd.y + 36);
        t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "viz-node-val");
        t.textContent = nd.val;
        var badge = svgEl("text");
        badge.setAttribute("x", nd.x + 56); badge.setAttribute("y", nd.y + 20);
        badge.setAttribute("text-anchor", "middle"); badge.setAttribute("class", "viz-node-badge");
        nodesG.appendChild(c); nodesG.appendChild(t); nodesG.appendChild(badge);
        circEls[nd.id] = c; badgeEls[nd.id] = badge;
      });
    }

    return { render: function (f) {
      if (f.nodes) build(f.nodes, f.edges || []);
      nodeList.forEach(function (nd) { circEls[nd.id].setAttribute("class", "viz-node"); });
      var active = f.active || [];
      active.forEach(function (id) { if (circEls[id]) circEls[id].setAttribute("class", "viz-node active"); });
      var done = f.done || {};
      nodeList.forEach(function (nd) {
        var v = done[nd.id];
        badgeEls[nd.id].textContent = (v === undefined || v === null) ? "" : v;
        if (v !== undefined && v !== null && active.indexOf(nd.id) === -1) {
          circEls[nd.id].setAttribute("class", "viz-node resolved");
        }
      });
    }};
  }

  function build(mount) {
    var dataEl = mount.querySelector("script.viz-data");
    if (!dataEl) return;
    var trace;
    try { trace = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var frames = trace.frames || [];
    if (!frames.length) return;

    if (trace.title) el("div", "viz-title", mount).textContent = trace.title;

    var actEls = [];
    if (trace.acts && trace.acts.length) {
      var bar = el("div", "viz-acts", mount);
      trace.acts.forEach(function (label, i) {
        var s = el("span", "viz-act", bar);
        s.textContent = (i + 1) + ". " + label;
        actEls.push(s);
      });
    }

    var host = el("div", "viz-host", mount);
    var render = (trace.player === "tree") ? TreeRenderer(host) : LinearRenderer(host);
    var note = el("div", "viz-note", mount);
    var banner = el("div", "viz-banner", mount); banner.style.display = "none";

    var controls = el("div", "viz-controls", mount);
    var back = el("button", "viz-btn", controls); back.textContent = "◀";
    var play = el("button", "viz-btn viz-play", controls); play.textContent = "▶ Play";
    var fwd = el("button", "viz-btn", controls); fwd.textContent = "▶";
    var scrub = el("input", "viz-scrub", controls);
    scrub.type = "range"; scrub.min = 0; scrub.max = frames.length - 1; scrub.value = 0;
    var counter = el("span", "viz-counter", controls);

    var idx = 0, timer = null;
    function show(i) {
      idx = Math.max(0, Math.min(frames.length - 1, i));
      var f = frames[idx];
      render.render(f);
      note.textContent = f.note || "";
      if (f.banner) { banner.textContent = f.banner; banner.style.display = "block"; }
      else { banner.style.display = "none"; }
      var act = f.act || 0;
      actEls.forEach(function (s, k) {
        s.className = "viz-act" + (k === act ? " active" : (k < act ? " done" : ""));
      });
      scrub.value = idx;
      counter.textContent = (idx + 1) + " / " + frames.length;
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } play.textContent = "▶ Play"; }
    function start() {
      if (idx >= frames.length - 1) show(0);
      play.textContent = "⏸ Pause";
      timer = setInterval(function () {
        if (idx >= frames.length - 1) { stop(); return; }
        show(idx + 1);
      }, 1150);
    }
    play.onclick = function () { timer ? stop() : start(); };
    back.onclick = function () { stop(); show(idx - 1); };
    fwd.onclick = function () { stop(); show(idx + 1); };
    scrub.oninput = function () { stop(); show(+scrub.value); };
    show(0);
  }

  function init() {
    var mounts = document.querySelectorAll(".viz");
    for (var i = 0; i < mounts.length; i++) build(mounts[i]);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
