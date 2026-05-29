document.addEventListener("DOMContentLoaded", function () {
  var buttons = document.querySelectorAll(".usp-tabs__btn");
  var panels = document.querySelectorAll(".usp-tabs__panel");

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tab = btn.getAttribute("data-tab");

      buttons.forEach(function (b) { b.classList.remove("usp-tabs__btn--active"); });
      panels.forEach(function (p) { p.classList.remove("usp-tabs__panel--active"); });

      btn.classList.add("usp-tabs__btn--active");
      var target = document.querySelector('[data-panel="' + tab + '"]');
      if (target) target.classList.add("usp-tabs__panel--active");
    });
  });
});
