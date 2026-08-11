/* Zero-dependency step-through visualizer.
 *
 * Each problem page embeds a <div class="viz"> whose child
 * <script type="application/json" class="viz-data"> holds a trace:
 *   { player: "linear"|"tree", title, ...structure, frames: [ {note, ...} ] }
 * The trace is produced by the problem's trace.py, which mirrors the verified
 * solution — so what you watch is what the code does.
 *
 * Structure is drawn once; each frame only updates positions/classes, so moves
 * animate via CSS transitions. Controls: play/pause, step, scrub, speed.
 */
(function () {
  "use strict";

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }
  function svgEl(tag) {
    return document.createElementNS("http://www.w3.org/2000/svg", tag);
  }

  var CELL = 52, GAP = 8, PAD = 16, ROW_Y = 70;

  // ---- linear renderer: array / pointers / window / key-value sidebar ----
  function LinearRenderer(mount, trace) {
    var cells = trace.cells || [];
    var n = cells.length;
    var width = PAD * 2 + n * CELL + (n - 1) * GAP;
    var stage = el("div", "viz-stage", mount);
    var svgWrap = el("div", "viz-svg-wrap", stage);
    var svg = svgEl("svg");
    svg.setAttribute("viewBox", "0 0 " + Math.max(width, 320) + " 150");
    svg.setAttribute("class", "viz-svg");
    svgWrap.appendChild(svg);

    function cx(i) { return PAD + i * (CELL + GAP); }

    // window highlight (behind cells)
    var win = svgEl("rect");
    win.setAttribute("class", "viz-window");
    win.setAttribute("y", ROW_Y - 6);
    win.setAttribute("height", CELL + 12);
    win.setAttribute("rx", 8);
    win.style.opacity = 0;
    svg.appendChild(win);

    var cellEls = [], labelEls = [];
    for (var i = 0; i < n; i++) {
      var g = svgEl("g");
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
      lab.textContent = (trace.labels && trace.labels[i] != null) ? trace.labels[i] : i;
      g.appendChild(r); g.appendChild(t); g.appendChild(lab);
      svg.appendChild(g);
      cellEls.push(r); labelEls.push(t);
    }

    // pointer markers (arrows above cells), created lazily per name
    var ptrs = {};
    function ptr(name) {
      if (ptrs[name]) return ptrs[name];
      var g = svgEl("g"); g.setAttribute("class", "viz-ptr");
      var tri = svgEl("path");
      tri.setAttribute("d", "M " + (CELL / 2 - 7) + " 0 L " + (CELL / 2 + 7) + " 0 L " + (CELL / 2) + " 11 Z");
      tri.setAttribute("class", "viz-ptr-tri");
      var nm = svgEl("text");
      nm.setAttribute("x", CELL / 2); nm.setAttribute("y", -6);
      nm.setAttribute("text-anchor", "middle"); nm.setAttribute("class", "viz-ptr-name");
      nm.textContent = name;
      g.appendChild(nm); g.appendChild(tri);
      g.setAttribute("transform", "translate(" + cx(0) + "," + (ROW_Y - 14) + ")");
      svg.appendChild(g);
      ptrs[name] = g;
      return g;
    }

    var sidebar = el("div", "viz-sidebar", stage);
    var banner = el("div", "viz-banner", mount);
    banner.style.display = "none";

    return function render(f) {
      for (var i = 0; i < n; i++) cellEls[i].setAttribute("class", "viz-cell");
      var marks = f.marks || {};
      Object.keys(marks).forEach(function (k) {
        var idx = +k;
        if (cellEls[idx]) cellEls[idx].setAttribute("class", "viz-cell m-" + marks[k]);
      });
      // pointers
      var seen = {};
      var p = f.pointers || {};
      Object.keys(p).forEach(function (name) {
        seen[name] = 1;
        var g = ptr(name);
        g.style.opacity = 1;
        g.setAttribute("transform", "translate(" + cx(p[name]) + "," + (ROW_Y - 14) + ")");
      });
      Object.keys(ptrs).forEach(function (name) {
        if (!seen[name]) ptrs[name].style.opacity = 0;
      });
      // window
      if (f.window && f.window.length === 2) {
        var a = f.window[0], b = f.window[1];
        win.setAttribute("x", cx(a) - 6);
        win.setAttribute("width", (cx(b) + CELL) - (cx(a)) + 12);
        win.style.opacity = 1;
      } else { win.style.opacity = 0; }
      // sidebar
      if (f.sidebar) {
        var rows = (f.sidebar.rows || []).map(function (r) {
          return "<tr><td>" + esc(r[0]) + "</td><td>" + esc(r[1]) + "</td></tr>";
        }).join("");
        sidebar.innerHTML = '<div class="viz-sb-title">' + esc(f.sidebar.title || "") +
          "</div><table>" + rows + "</table>";
        sidebar.style.display = rows ? "block" : "none";
      } else { sidebar.style.display = "none"; }
      // banner
      if (f.banner) { banner.textContent = f.banner; banner.style.display = "block"; }
      else { banner.style.display = "none"; }
    };
  }

  // ---- tree renderer: nodes at precomputed x,y; active + returned values ----
  function TreeRenderer(mount, trace) {
    var nodes = trace.nodes || [];
    var byId = {}; nodes.forEach(function (nd) { byId[nd.id] = nd; });
    var maxX = 0, maxY = 0;
    nodes.forEach(function (nd) { maxX = Math.max(maxX, nd.x); maxY = Math.max(maxY, nd.y); });
    var W = maxX + 60, H = maxY + 70;
    var stage = el("div", "viz-stage", mount);
    var svgWrap = el("div", "viz-svg-wrap", stage);
    var svg = svgEl("svg");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("class", "viz-svg");
    svgWrap.appendChild(svg);

    (trace.edges || []).forEach(function (e) {
      var a = byId[e[0]], b = byId[e[1]];
      var ln = svgEl("line");
      ln.setAttribute("x1", a.x + 30); ln.setAttribute("y1", a.y + 30);
      ln.setAttribute("x2", b.x + 30); ln.setAttribute("y2", b.y + 30);
      ln.setAttribute("class", "viz-edge");
      svg.appendChild(ln);
    });
    var circEls = {}, badgeEls = {};
    nodes.forEach(function (nd) {
      var g = svgEl("g");
      var c = svgEl("circle");
      c.setAttribute("cx", nd.x + 30); c.setAttribute("cy", nd.y + 30);
      c.setAttribute("r", 22); c.setAttribute("class", "viz-node");
      var t = svgEl("text");
      t.setAttribute("x", nd.x + 30); t.setAttribute("y", nd.y + 36);
      t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "viz-node-val");
      t.textContent = nd.val;
      var badge = svgEl("text");
      badge.setAttribute("x", nd.x + 58); badge.setAttribute("y", nd.y + 22);
      badge.setAttribute("text-anchor", "middle"); badge.setAttribute("class", "viz-node-badge");
      badge.textContent = "";
      g.appendChild(c); g.appendChild(t); g.appendChild(badge);
      svg.appendChild(g);
      circEls[nd.id] = c; badgeEls[nd.id] = badge;
    });

    return function render(f) {
      nodes.forEach(function (nd) { circEls[nd.id].setAttribute("class", "viz-node"); });
      (f.active || []).forEach(function (id) {
        if (circEls[id]) circEls[id].setAttribute("class", "viz-node active");
      });
      var done = f.done || {};
      nodes.forEach(function (nd) {
        var v = done[nd.id];
        badgeEls[nd.id].textContent = (v === undefined || v === null) ? "" : v;
        if (v !== undefined && v !== null && !(f.active || []).includes(nd.id)) {
          circEls[nd.id].setAttribute("class", "viz-node resolved");
        }
      });
    };
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function build(mount) {
    var dataEl = mount.querySelector("script.viz-data");
    if (!dataEl) return;
    var trace;
    try { trace = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var frames = trace.frames || [];
    if (!frames.length) return;

    if (trace.title) el("div", "viz-title", mount).textContent = trace.title;
    var render = (trace.player === "tree")
      ? TreeRenderer(mount, trace) : LinearRenderer(mount, trace);

    var note = el("div", "viz-note", mount);
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
      render(frames[idx]);
      note.textContent = frames[idx].note || "";
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
      }, 1100);
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
