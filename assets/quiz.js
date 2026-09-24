/* quiz.js — one question at a time, click or number key.
   Classic script → window.TEACH.quiz(stage, opts) → {stop}.

   opts.items: [{ id, prompt, choices: [string, ...], answer: index, why }]
   answer is the index into choices. ids are stable; never rename one.
   Claims TEACH._active while open so another trainer can take the keyboard.
*/
(function () {
  var TEACH = (window.TEACH = window.TEACH || {});

  TEACH.quiz = function (stage, opts) {
    var items = (opts && opts.items) || [];
    var token = {};
    var i = 0;
    var locked = false;
    var onKey = null;

    function mine() { return TEACH._active === token; }

    function stop() {
      if (TEACH._active === token) TEACH._active = null;
      if (onKey) document.removeEventListener("keydown", onKey);
      onKey = null;
    }

    function finish() {
      stop();
      stage.innerHTML = "";
      var p = document.createElement("p");
      p.className = "why good";
      p.textContent = "Done. " + items.length + " checked.";
      stage.appendChild(p);
    }

    function render() {
      if (i >= items.length) return finish();
      var item = items[i];
      locked = false;
      stage.innerHTML = "";

      var prog = document.createElement("p");
      prog.className = "progress";
      prog.textContent = (i + 1) + " of " + items.length;
      stage.appendChild(prog);

      var prompt = document.createElement("p");
      prompt.className = "prompt";
      prompt.textContent = item.prompt;
      stage.appendChild(prompt);

      item.choices.forEach(function (text, n) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "choice";
        b.textContent = (n + 1) + ". " + text;
        b.addEventListener("click", function () { choose(n); });
        stage.appendChild(b);
      });
    }

    function choose(n) {
      if (!mine() || locked || i >= items.length) return;
      locked = true;
      var item = items[i];
      var buttons = stage.querySelectorAll("button");
      var right = n === item.answer;
      if (buttons[n]) buttons[n].className = "choice " + (right ? "good" : "bad");
      if (!right && buttons[item.answer]) buttons[item.answer].className = "choice good";
      var why = document.createElement("p");
      why.className = "why " + (right ? "good" : "bad");
      why.textContent = (right ? "Yes. " : "No. ") + item.why;
      stage.appendChild(why);
      var next = document.createElement("button");
      next.type = "button";
      next.className = "choice";
      next.textContent = i + 1 >= items.length ? "Finish" : "Next";
      next.addEventListener("click", function () { i += 1; render(); });
      stage.appendChild(next);
    }

    onKey = function (e) {
      if (!mine()) return;
      if (e.key >= "1" && e.key <= "9") {
        var n = Number(e.key) - 1;
        if (n < items[i].choices.length) choose(n);
      }
    };

    TEACH._active = token;
    document.addEventListener("keydown", onKey);
    render();
    return { stop: stop };
  };
})();
