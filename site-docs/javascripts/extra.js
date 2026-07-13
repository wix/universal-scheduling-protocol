window.openTab = function (evtOrPaneId, paneId) {
  var targetId = paneId || evtOrPaneId;
  if (!targetId || typeof targetId !== "string") return;

  var pane = document.getElementById(targetId);
  if (!pane) return;

  var btn = null;
  if (evtOrPaneId && typeof evtOrPaneId === "object") {
    btn = evtOrPaneId.currentTarget || (evtOrPaneId.target && evtOrPaneId.target.closest(".tab-btn"));
  }

  var tabGroup = btn ? btn.closest(".carousel-tabs") : null;
  if (tabGroup) {
    tabGroup.querySelectorAll(".tab-btn").forEach(function (b) {
      b.classList.toggle("active", b === btn);
    });
  }

  var parent = pane.parentElement;
  if (parent) {
    parent.querySelectorAll(":scope > .tab-pane").forEach(function (p) {
      p.classList.toggle("active", p.id === targetId);
    });
  }
};

window.openSubTab = function (evtOrPaneId, paneId) {
  var targetId = paneId || evtOrPaneId;
  if (!targetId || typeof targetId !== "string") return;

  var pane = document.getElementById(targetId);
  if (!pane) return;

  var btn = null;
  if (evtOrPaneId && typeof evtOrPaneId === "object") {
    btn = evtOrPaneId.currentTarget || (evtOrPaneId.target && evtOrPaneId.target.closest(".sub-tab-btn"));
  }

  var tabGroup = btn ? btn.closest(".sub-action-tabs") : null;
  if (tabGroup) {
    tabGroup.querySelectorAll(".sub-tab-btn").forEach(function (b) {
      b.classList.toggle("active", b === btn);
    });
  }

  var content = pane.closest(".sub-tab-content");
  if (content) {
    content.querySelectorAll(":scope > .sub-tab-pane").forEach(function (p) {
      p.classList.toggle("active", p.id === targetId);
    });
  }
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
