window.openTab = function (mode) {
  document.querySelectorAll("[data-mode-tab]").forEach(function (btn) {
    var active = btn.getAttribute("data-mode-tab") === mode;
    btn.classList.toggle("usp-tabs__btn--active", active);
    btn.classList.toggle("active", active);
  });
  document.querySelectorAll("[data-mode-panel]").forEach(function (panel) {
    panel.classList.toggle("carousel-mode-panel--active", panel.getAttribute("data-mode-panel") === mode);
  });
};

window.openSubTab = function (mode, sub) {
  var modePanel = document.querySelector('[data-mode-panel="' + mode + '"]');
  if (!modePanel) return;
  modePanel.querySelectorAll("[data-sub-tab]").forEach(function (btn) {
    var active = btn.getAttribute("data-sub-tab") === sub;
    btn.classList.toggle("usp-tabs__btn--active", active);
    btn.classList.toggle("active", active);
  });
  modePanel.querySelectorAll("[data-sub-panel]").forEach(function (panel) {
    panel.classList.toggle("carousel-sub-panel--active", panel.getAttribute("data-sub-panel") === sub);
  });
};

function openIndustryTab(industry) {
  document.querySelectorAll(".industry-tab").forEach(function (btn) {
    var active = btn.getAttribute("data-industry") === industry;
    btn.classList.toggle("usp-tabs__btn--active", active);
    btn.classList.toggle("active", active);
  });
  document.querySelectorAll(".industry-panel").forEach(function (panel) {
    panel.classList.toggle("industry-panel--active", panel.getAttribute("data-industry-panel") === industry);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  var industries = ["appointments", "group", "reservations", "rentals"];
  var industryIndex = 0;
  var industryAutoplay = null;

  function startIndustryAutoplay() {
    if (industryAutoplay) clearInterval(industryAutoplay);
    industryAutoplay = setInterval(function () {
      industryIndex = (industryIndex + 1) % industries.length;
      openIndustryTab(industries[industryIndex]);
    }, 3000);
  }

  document.querySelectorAll(".industry-tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      industryIndex = industries.indexOf(btn.getAttribute("data-industry"));
      if (industryIndex < 0) industryIndex = 0;
      openIndustryTab(btn.getAttribute("data-industry"));
      if (industryAutoplay) clearInterval(industryAutoplay);
    });
  });

  var partnersSection = document.querySelector(".partners-section");
  if (partnersSection && document.querySelector(".industry-tabs")) {
    startIndustryAutoplay();
    partnersSection.addEventListener("mouseenter", function () {
      if (industryAutoplay) clearInterval(industryAutoplay);
    });
    partnersSection.addEventListener("mouseleave", function () {
      startIndustryAutoplay();
    });
  }

  var announceBanner = document.getElementById("usp-announce-banner");
  var announceClose = document.getElementById("usp-announce-close");
  if (announceBanner && announceClose) {
    if (localStorage.getItem("usp-announce-dismissed") === "1") {
      announceBanner.style.display = "none";
    }
    announceClose.addEventListener("click", function () {
      announceBanner.style.display = "none";
      localStorage.setItem("usp-announce-dismissed", "1");
    });
  }
});
