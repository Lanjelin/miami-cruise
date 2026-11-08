/* Miami Cruise site: theme switch, copy buttons, app search. Everything degrades gracefully without JS. */
(function () {
  "use strict";
  var root = document.documentElement;

  function store(key, value) {
    try {
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, value);
    } catch (e) { /* storage blocked: the choice just lasts for this page */ }
  }

  // ---- Theme: auto follows the system; dark/light override and are remembered
  var seg = document.querySelectorAll("[data-set]");
  function currentTheme() { return root.getAttribute("data-theme") || "auto"; }
  function markTheme() {
    for (var i = 0; i < seg.length; i++) seg[i].setAttribute("aria-pressed", String(seg[i].getAttribute("data-set") === currentTheme()));
  }
  for (var i = 0; i < seg.length; i++) {
    seg[i].addEventListener("click", function () {
      var v = this.getAttribute("data-set");
      if (v === "auto") { root.removeAttribute("data-theme"); store("mc-theme", null); }
      else { root.setAttribute("data-theme", v); store("mc-theme", v); }
      markTheme();
    });
  }
  markTheme();

  // ---- Copy buttons (hidden until JS is known to work)
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); } finally { document.body.removeChild(ta); }
    });
  }
  function flash(btn, label) {
    var old = btn.getAttribute("data-label") || btn.textContent;
    btn.setAttribute("data-label", old);
    btn.textContent = label;
    clearTimeout(btn._t);
    btn._t = setTimeout(function () { btn.textContent = old; }, 1600);
  }
  var copies = document.querySelectorAll(".copy");
  for (var c = 0; c < copies.length; c++) {
    copies[c].hidden = false;
    copies[c].addEventListener("click", function () {
      var btn = this, pre = btn.parentNode.querySelector("pre");
      copyText(pre.textContent.replace(/\n$/, "")).then(function () { flash(btn, "Copied"); }, function () { flash(btn, "Press Ctrl+C"); });
    });
  }
  var sw = document.querySelectorAll("[data-hex]");
  for (var s = 0; s < sw.length; s++) {
    sw[s].addEventListener("click", function () {
      var el = this, hex = el.getAttribute("data-hex");
      copyText(hex).then(function () { var l = document.getElementById("copied"); if (l) l.textContent = "Copied " + hex; });
    });
  }

  // ---- Search apps (index page)
  var q = document.getElementById("q");
  if (q) {
    var cards = document.querySelectorAll("[data-card]");
    var grid = document.getElementById("apps");
    var count = document.getElementById("count");
    var empty = document.getElementById("empty");
    var apply = function () {
      var terms = q.value.toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
      for (var k = 0; k < cards.length; k++) {
        var hay = cards[k].getAttribute("data-search");
        var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
        cards[k].hidden = !ok;
        if (ok) shown++;
      }
      grid.hidden = shown === 0;
      empty.hidden = shown !== 0;
      count.textContent = terms.length ? shown + (shown === 1 ? " app matches" : " apps match") : "";
    };
    q.addEventListener("input", apply);
    q.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { q.value = ""; apply(); }
      if (e.key === "Enter") {
        for (var k = 0; k < cards.length; k++) if (!cards[k].hidden) { cards[k].querySelector("a").click(); break; }
      }
    });
    document.addEventListener("keydown", function (e) {
      var t = e.target && e.target.tagName;
      if (e.key === "/" && t !== "INPUT" && t !== "TEXTAREA" && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); q.focus(); }
    });
    var pre = new URLSearchParams(location.search).get("q");
    if (pre) { q.value = pre; apply(); }
  }

  // ---- Respect reduced motion: pause the animated hero scene
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var svgs = document.querySelectorAll(".scene svg");
    for (var v = 0; v < svgs.length; v++) if (svgs[v].pauseAnimations) svgs[v].pauseAnimations();
  }
})();
