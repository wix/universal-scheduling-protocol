/**
 * playground-controller.js — Lightweight controller for the USP Playground.
 * Handles step switching, scenario selection, mock request execution,
 * and code display. Works on pre-rendered HTML from playground.html template.
 */

(function () {
  'use strict';

  // ── Syntax highlighting ──────────────────────────────────────────
  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function highlightJson(json) {
    var ph = [], idx = 0;
    function hold(html) { var i = idx++; ph.push(html); return '\x00' + i + '\x00'; }
    var out = json;
    out = out.replace(/("(?:[^"\\]|\\.)*")(\s*:)/g, function (_, k, c) {
      return hold('<span class="pg-tok-key">' + escapeHtml(k) + '</span>') + c;
    });
    out = out.replace(/("(?:[^"\\]|\\.)*")/g, function (_, s) {
      return hold('<span class="pg-tok-str">' + escapeHtml(s) + '</span>');
    });
    out = out.replace(/\b(-?\d+(?:\.\d+)?)\b/g, function (_, n) {
      return hold('<span class="pg-tok-num">' + n + '</span>');
    });
    out = out.replace(/\b(true|false)\b/g, function (_, b) {
      return hold('<span class="pg-tok-bool">' + b + '</span>');
    });
    out = out.replace(/\b(null)\b/g, function (_, n) {
      return hold('<span class="pg-tok-null">' + n + '</span>');
    });
    out = out.replace(/\x00(\d+)\x00/g, function (_, i) { return ph[Number(i)]; });
    return out;
  }

  function showJson(elId, obj) {
    var el = document.getElementById(elId);
    if (!el) return;
    var json = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
    el.innerHTML = highlightJson(json);
  }

  // ── Scenario data cache ──────────────────────────────────────────
  var cache = {};

  function loadScenario(file, key, cb) {
    if (cache[file]) {
      return cb(cache[file][key] || null);
    }
    var basePath = window.location.pathname.indexOf('/playground') >= 0 ? './' : 'playground/';
    fetch(basePath + 'scenarios/' + file + '.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        cache[file] = data;
        cb(data[key] || null);
      })
      .catch(function () { cb(null); });
  }

  // ── Step switching ───────────────────────────────────────────────
  var currentStep = 'discovery';

  function switchStep(stepId) {
    currentStep = stepId;
    document.querySelectorAll('.pg-step').forEach(function (s) {
      s.classList.toggle('pg-step-visible', s.getAttribute('data-step') === stepId);
    });
    document.querySelectorAll('.pg-step-pill').forEach(function (p) {
      p.classList.toggle('pg-step-pill-active', p.getAttribute('data-step') === stepId);
    });
  }

  // ── Step pill clicks ─────────────────────────────────────────────
  document.querySelectorAll('.pg-step-pill').forEach(function (pill) {
    pill.addEventListener('click', function () {
      switchStep(this.getAttribute('data-step'));
    });
  });

  // ── Next/Back buttons ────────────────────────────────────────────
  document.querySelectorAll('.pg-btn-next').forEach(function (btn) {
    btn.addEventListener('click', function () {
      switchStep(this.getAttribute('data-next'));
    });
  });
  document.querySelectorAll('.pg-btn-back').forEach(function (btn) {
    btn.addEventListener('click', function () {
      switchStep(this.getAttribute('data-prev'));
    });
  });

  // ── Copy buttons ─────────────────────────────────────────────────
  document.querySelectorAll('.pg-btn-copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = document.getElementById(this.getAttribute('data-target'));
      if (!target) return;
      var text = target.textContent || '';
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied!';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1500);
      });
    });
  });

  // ── Mode toggle ──────────────────────────────────────────────────
  document.querySelectorAll('#pg-mode-toggle .pg-toggle-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('#pg-mode-toggle .pg-toggle-btn').forEach(function (b) {
        b.classList.remove('pg-toggle-active');
      });
      this.classList.add('pg-toggle-active');
    });
  });

  // ── Transport toggle ─────────────────────────────────────────────
  document.querySelectorAll('#pg-transport-toggle .pg-toggle-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('#pg-transport-toggle .pg-toggle-btn').forEach(function (b) {
        b.classList.remove('pg-toggle-active');
      });
      this.classList.add('pg-toggle-active');
    });
  });

  // ── Scenario file map ────────────────────────────────────────────
  var stepFiles = {
    discovery:    'business-profile',
    negotiation:  'platform-profile',
    browse:       'services',
    availability: 'availability',
    hold:         'holds',
    book:         'bookings',
    payment:      'payment',
    manage:       'manage'
  };

  // ── Run button handlers ──────────────────────────────────────────

  function runStep(stepId) {
    var selectEl = document.getElementById('pg-' + stepId + '-scenario');
    var codeEl = document.getElementById('pg-' + stepId + '-code');
    var runBtn = document.getElementById('pg-' + stepId + '-run');
    if (!selectEl || !codeEl) return;

    var scenarioKey = selectEl.value;
    var file = stepFiles[stepId];
    if (!file) return;

    // Loading state
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.querySelector('.pg-btn-text').textContent = 'Loading...';
    }

    // Handle manage step - may need webhooks file
    var actualFile = file;
    if (stepId === 'manage' && scenarioKey.indexOf('booking_') === 0) {
      actualFile = 'webhooks';
    }

    loadScenario(actualFile, scenarioKey, function (data) {
      // Simulated delay
      setTimeout(function () {
        if (data) {
          var display;
          var status = 200;
          if (data.response && data.response.body) {
            display = data.response.body;
            status = data.response.status || 200;
          } else if (data.response) {
            display = data.response;
          } else if (data.payload) {
            display = data.payload;
          } else {
            display = data;
          }
          showJson(codeEl.id, display);

          var header = codeEl.closest('.pg-code-panel').querySelector('.pg-pane-header');
          var existingBadge = header.querySelector('.pg-status-badge');
          if (existingBadge) existingBadge.remove();
          var badge = document.createElement('span');
          badge.className = 'pg-status-badge ' + (status >= 400 ? 'pg-status-4xx' : 'pg-status-2xx');
          badge.textContent = status >= 400 ? status + ' Error' : status + ' OK';
          header.appendChild(badge);
        } else {
          showJson(codeEl.id, { error: 'Scenario not found', scenario: scenarioKey });
        }

        if (runBtn) {
          runBtn.disabled = false;
          runBtn.querySelector('.pg-btn-text').textContent = stepId === 'discovery' ? 'Fetch Profile' : 'Run Request';
          if (stepId === 'negotiation') runBtn.querySelector('.pg-btn-text').textContent = 'Run Negotiation';
        }
      }, 300 + Math.floor(Math.random() * 400));
    });
  }

  // Wire up all run buttons
  ['discovery', 'negotiation', 'browse', 'availability', 'hold', 'book', 'payment', 'manage'].forEach(function (stepId) {
    var btn = document.getElementById('pg-' + stepId + '-run');
    if (btn) {
      btn.addEventListener('click', function () { runStep(stepId); });
    }
  });

  // ── Manage step: update method/path on scenario change ───────────
  var manageOps = {
    view_booking:      { method: 'GET',   path: '/bookings/{booking_id}' },
    update_booking:    { method: 'PATCH', path: '/bookings/{booking_id}' },
    cancel_booking:    { method: 'POST',  path: '/bookings/{booking_id}/cancel' },
    reschedule_booking:{ method: 'POST',  path: '/bookings/{booking_id}/reschedule' },
    booking_confirmed: { method: 'POST',  path: '/webhooks (simulated)' },
    booking_canceled:  { method: 'POST',  path: '/webhooks (simulated)' }
  };

  var manageSelect = document.getElementById('pg-manage-scenario');
  if (manageSelect) {
    manageSelect.addEventListener('change', function () {
      var op = manageOps[this.value] || manageOps.view_booking;
      var methodEl = document.getElementById('pg-manage-method');
      var pathEl = document.getElementById('pg-manage-path');
      if (methodEl) {
        methodEl.textContent = op.method;
        methodEl.className = 'pg-method-badge pg-method-' + op.method.toLowerCase();
      }
      if (pathEl) pathEl.textContent = op.path;
    });
  }

  // ── Discovery description update ─────────────────────────────────
  var discoveryDescs = {
    standard: 'Supports core Catalog, Availability, and Bookings capabilities.',
    full: 'All capabilities including Holds, Waitlist extension, and signing keys.',
    minimal: 'Minimal appointment-only profile with no holds or extensions.'
  };
  var discoverySelect = document.getElementById('pg-discovery-scenario');
  if (discoverySelect) {
    discoverySelect.addEventListener('change', function () {
      var desc = document.getElementById('pg-discovery-desc');
      if (desc) desc.textContent = discoveryDescs[this.value] || '';
    });
  }

  // ── Auto-load the first step ─────────────────────────────────────
  runStep('discovery');

})();
