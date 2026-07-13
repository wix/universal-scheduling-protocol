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

document.addEventListener("DOMContentLoaded", function () {
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
