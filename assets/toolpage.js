/* ============================================================
   toolpage.js — the skill-page helper, shared by every subject.
   Classic script → window.TEACH. Styles: teach.css (.t-trainer).

   A skill page gathers every trainer for one skill. Each trainer
   is one call, written NEWEST FIRST (call order is page order):

   TEACH.trainer(containerElOrId, {
     id: "l13-speed",          // DOM id AND the #hash deep link —
                               // unique, and STABLE once published
     title: "The fifteen · beat the clock",
     origin: { label: "Lesson 13 · The Circle Closes",
               href:  "../lessons/0013-circle-of-fifths.html" },
     blurb: "one line of HTML",          // optional
     mount: function (stage) {           // called ONCE, on first open
       return TEACH.speedDrill(stage, { ... });
     }
   })

   Rules the helper enforces, and why:

   · Lazy. A trainer is built the first time it is opened, so a page
     of nine is a short menu on a phone rather than nine audio and
     keyboard widgets alive at once.
   · One at a time. Opening a trainer closes the others.
   · Closed means stopped. `mount` returns {stop} if the trainer
     holds timers, loops or document-level key listeners — every
     TEACH engine does. Closing a trainer calls it. Without this a
     hidden speed drill keeps timing out (recording misses into the
     deck), hidden Enter handlers keep firing, and a hidden loop
     keeps playing.
   Together: at most one trainer on a page is ever live, so they
   cannot fight over the keyboard — including the subject-specific
   ones that know nothing about TEACH._active.

   A page with a single trainer opens it; #<id> opens that trainer.

   Optional, in the page markup:
     <nav class="t-back" hidden><a href="../index.html#tools">← All tools</a></nav>
   The subject page it points at exists only on the built site, so
   the helper reveals it everywhere except file://.
   ============================================================ */
(function () {
  var TEACH = (window.TEACH = window.TEACH || {});
  var registry = [];

  TEACH.trainer = function (containerElOrId, o) {
    var host = typeof containerElOrId === "string" ? document.getElementById(containerElOrId) : containerElOrId;
    if (!host || !o || typeof o.mount !== "function") return;

    var el = document.createElement("details");
    el.className = "t-trainer";
    if (o.id) el.id = o.id;

    var summary = document.createElement("summary");
    var title = document.createElement("span");
    title.className = "t-trainer-title";
    title.textContent = o.title || o.id || "Trainer";
    summary.appendChild(title);
    if (o.origin && o.origin.label) {
      // Plain text here, the link lives in the body: a link inside a
      // <summary> is a mis-tap waiting to happen on a phone.
      var from = document.createElement("span");
      from.className = "t-trainer-origin";
      from.textContent = o.origin.label;
      summary.appendChild(from);
    }
    el.appendChild(summary);

    var body = document.createElement("div");
    body.className = "t-trainer-body";
    if (o.blurb) {
      var blurb = document.createElement("p");
      blurb.className = "t-trainer-blurb";
      blurb.innerHTML = o.blurb;
      body.appendChild(blurb);
    }
    if (o.origin && o.origin.href) {
      var p = document.createElement("p");
      p.className = "t-trainer-from";
      var a = document.createElement("a");
      a.href = o.origin.href;
      a.textContent = "From " + (o.origin.label || "the lesson") + " →";
      p.appendChild(a);
      body.appendChild(p);
    }
    var stage = document.createElement("div");
    stage.className = "t-stage";
    body.appendChild(stage);
    el.appendChild(body);
    host.appendChild(el);

    var entry = { el: el, handle: null, mounted: false };
    registry.push(entry);

    function mountOnce() {
      if (entry.mounted) return;
      entry.mounted = true;
      try {
        entry.handle = o.mount(stage) || null;
      } catch (err) {
        // No console on the phone — say so on the page.
        stage.innerHTML = '<p class="t-trainer-error">This trainer failed to start.</p>';
        if (window.console && console.error) console.error(err);
      }
    }

    // `toggle` is async and coalesced: trust el.open, not the event count.
    el.addEventListener("toggle", function () {
      if (el.open) {
        mountOnce();
        registry.forEach(function (other) { if (other !== entry && other.el.open) other.el.open = false; });
        // A focused <summary> toggles on Space/Enter — the same keys the
        // trainers use. Let go of it.
        if (document.activeElement === summary) summary.blur();
      } else if (entry.handle && typeof entry.handle.stop === "function") {
        entry.handle.stop();
      }
    });

    var api = { el: el, open: function () { mountOnce(); el.open = true; } };
    entry.api = api;
    return api;
  };

  function byHash() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    if (!id) return null;
    for (var i = 0; i < registry.length; i++) {
      if (registry[i].el.id === id) return registry[i];
    }
    return null;
  }

  function openFromHash(scroll) {
    var hit = byHash();
    if (!hit) return false;
    hit.api.open();
    if (scroll && hit.el.scrollIntoView) hit.el.scrollIntoView();
    return true;
  }

  function ready() {
    if (!openFromHash(true) && registry.length === 1) registry[0].api.open();
    if (location.protocol !== "file:") {
      var back = document.querySelectorAll(".t-back[hidden]");
      for (var i = 0; i < back.length; i++) back[i].hidden = false;
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();
  window.addEventListener("hashchange", function () { openFromHash(true); });
})();
