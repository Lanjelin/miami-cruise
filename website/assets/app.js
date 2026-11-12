/* Miami Cruise site: theme switch, copy buttons, app search. Everything degrades gracefully without JS. */
(function () {
  "use strict";
  var root = document.documentElement;

  // A failed logo reveals the same text fallback used for apps without artwork.
  document.querySelectorAll(".app-icon img").forEach(function (img) {
    img.addEventListener("error", function () { img.hidden = true; });
    if (img.complete && img.naturalWidth === 0) img.hidden = true;
  });

  function store(key, value) {
    try {
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, value);
    } catch (e) { /* storage blocked: the choice just lasts for this page */ }
  }

  // ---- Screenshot previews: native modal handles focus trapping and Escape.
  // Links still open the original image when JavaScript/dialog is unavailable.
  var previews = document.querySelectorAll("[data-zoom]");
  if (previews.length && typeof HTMLDialogElement !== "undefined" && HTMLDialogElement.prototype.showModal) {
    var viewer = document.createElement("dialog");
    viewer.className = "screenshot-dialog";
    viewer.setAttribute("aria-labelledby", "screenshot-caption");
    viewer.innerHTML = '<div class="zoom-toolbar"><p id="screenshot-caption"></p>' +
      '<div class="zoom-actions"><button type="button" class="btn ghost" data-actual aria-pressed="false">Actual size</button>' +
      '<a class="btn ghost" data-original>Open original</a>' +
      '<button type="button" class="btn ghost" data-close autofocus>Close</button></div></div>' +
      '<div class="zoom-stage"><img alt=""></div>';
    document.body.appendChild(viewer);
    var zoomImage = viewer.querySelector("img");
    var sizeButton = viewer.querySelector("[data-actual]");
    var stage = viewer.querySelector(".zoom-stage");
    var opener;
    previews.forEach(function (link) {
      link.addEventListener("click", function (event) {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = link;
        zoomImage.src = link.href;
        zoomImage.alt = link.querySelector("img").alt;
        viewer.querySelector("#screenshot-caption").textContent = zoomImage.alt;
        viewer.querySelector("[data-original]").href = link.href;
        viewer.classList.remove("zoom-actual");
        sizeButton.setAttribute("aria-pressed", "false");
        sizeButton.textContent = "Actual size";
        viewer.showModal();
        stage.scrollTo(0, 0);
      });
    });
    sizeButton.addEventListener("click", function () {
      var actual = viewer.classList.toggle("zoom-actual");
      sizeButton.setAttribute("aria-pressed", String(actual));
      sizeButton.textContent = actual ? "Fit to screen" : "Actual size";
      stage.scrollTo(0, 0);
    });
    viewer.querySelector("[data-close]").addEventListener("click", function () { viewer.close(); });
    viewer.addEventListener("click", function (event) {
      var rect = viewer.getBoundingClientRect();
      if (event.target === viewer && (event.clientX < rect.left || event.clientX > rect.right ||
          event.clientY < rect.top || event.clientY > rect.bottom)) viewer.close();
    });
    viewer.addEventListener("close", function () { if (opener) opener.focus({ preventScroll: true }); });
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

  // ---- Search and category filter (index page)
  var q = document.getElementById("q");
  if (q) {
    var cards = document.querySelectorAll("[data-card]");
    var grid = document.getElementById("app-groups");
    var groups = document.querySelectorAll("[data-group]");
    var count = document.getElementById("count");
    var empty = document.getElementById("empty");
    var chips = document.querySelectorAll("[data-cat-set]");
    var category = "";
    var apply = function () {
      var terms = q.value.toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
      for (var k = 0; k < cards.length; k++) {
        var hay = cards[k].getAttribute("data-search");
        var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; }) &&
          (category === "" || cards[k].getAttribute("data-cat") === category);
        cards[k].hidden = !ok;
        if (ok) shown++;
      }
      for (var g = 0; g < groups.length; g++) {
        groups[g].hidden = !groups[g].querySelector("[data-card]:not([hidden])");
      }
      grid.hidden = shown === 0;
      empty.hidden = shown !== 0;
      count.textContent = (terms.length || category) ? shown + (shown === 1 ? " app matches" : " apps match") : "";
    };
    var setCategory = function (value) {
      category = value;
      for (var c = 0; c < chips.length; c++) chips[c].setAttribute("aria-pressed", String(chips[c].getAttribute("data-cat-set") === value));
      apply();
    };
    for (var c = 0; c < chips.length; c++) {
      chips[c].addEventListener("click", function () { setCategory(this.getAttribute("data-cat-set")); });
    }
    q.addEventListener("input", apply);
    q.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { q.value = ""; setCategory(""); }
      if (e.key === "Enter") {
        for (var k = 0; k < cards.length; k++) if (!cards[k].hidden) { cards[k].querySelector("a").click(); break; }
      }
    });
    document.addEventListener("keydown", function (e) {
      var t = e.target && e.target.tagName;
      if (e.key === "/" && t !== "INPUT" && t !== "TEXTAREA" && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); q.focus(); }
    });
    var params = new URLSearchParams(location.search);
    if (params.get("q")) q.value = params.get("q");
    if (params.get("cat")) { setCategory(params.get("cat")); } else { apply(); }
  }

  // ---- Respect reduced motion: pause the animated hero scene
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var svgs = document.querySelectorAll(".scene svg");
    for (var v = 0; v < svgs.length; v++) if (svgs[v].pauseAnimations) svgs[v].pauseAnimations();
  }
})();
