/**
 * playground-controller.js — USP Playground (UCP-style request/response panes + transport formatting).
 */

import { formatForTransport } from './transport-formatter.js';
import { highlightJson, escapeHtml } from './code-editor.js';

function showJson(elId, obj) {
  var el = document.getElementById(elId);
  if (!el) return;
  var json = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
  el.innerHTML = highlightJson(json);
}

function showText(elId, text) {
  var el = document.getElementById(elId);
  if (!el) return;
  el.textContent = text;
}

function showFormattedRequest(elId, formatted) {
  if (formatted.language === 'json') {
    try {
      showJson(elId, JSON.parse(formatted.display));
    } catch {
      showText(elId, formatted.display);
    }
  } else {
    showText(elId, formatted.display);
  }
}

function setStatus(stepId, status) {
  var badge = document.getElementById('pg-' + stepId + '-status');
  if (!badge) return;
  badge.style.display = 'inline-flex';
  badge.className = 'pg-status-badge ' + (status >= 400 ? 'pg-status-4xx' : 'pg-status-2xx');
  badge.textContent = status >= 400 ? status + ' Error' : status + ' OK';
}

var cache = {};
var stepState = {};

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

var currentStep = 'discovery';
var currentMode = 'standalone';
var currentTransport = 'rest';

var stepFiles = {
  discovery: 'business-profile',
  negotiation: 'platform-profile',
  browse: 'services',
  availability: 'availability',
  hold: 'holds',
  book: 'bookings',
  payment: 'payment',
  manage: 'manage'
};

var negotiationKeys = {
  'full-match': 'standard',
  'partial-match': 'full',
  'incompatible': 'standard'
};

var manageOps = {
  view_booking: { method: 'GET', path: '/services/svc_massage_001/bookings/bkg_7f3a2b1c8d9e' },
  update_booking: { method: 'PATCH', path: '/services/svc_massage_001/bookings/bkg_7f3a2b1c8d9e' },
  cancel_booking: { method: 'POST', path: '/services/svc_massage_001/bookings/bkg_7f3a2b1c8d9e/cancel' },
  reschedule_booking: { method: 'POST', path: '/services/svc_massage_001/bookings/bkg_7f3a2b1c8d9e/reschedule' },
  booking_confirmed: { method: 'POST', path: '/webhooks (simulated)' },
  booking_canceled: { method: 'POST', path: '/webhooks (simulated)' }
};

function businessProfileKey(scenarioKey, negotiationScenario) {
  if (negotiationScenario === 'partial-match') return 'full';
  if (scenarioKey === 'full') return 'full';
  if (scenarioKey === 'minimal') return 'minimal';
  return 'standard';
}

function intersectProfiles(businessBody, platformBody, options) {
  options = options || {};
  var result = JSON.parse(JSON.stringify(platformBody));
  var bizCaps = (businessBody.usp && businessBody.usp.capabilities) || {};
  var platCaps = (platformBody.usp && platformBody.usp.capabilities) || {};
  var negotiated = {};
  Object.keys(platCaps).forEach(function (key) {
    if (bizCaps[key]) {
      negotiated[key] = JSON.parse(JSON.stringify(platCaps[key]));
    }
  });
  if (options.stripHolds && negotiated['dev.usp.services.availability']) {
    negotiated['dev.usp.services.availability'].forEach(function (entry) {
      delete entry.holds;
    });
  }
  result.usp.capabilities = negotiated;
  return result;
}

function updatePaneHeaders(stepId, config) {
  var methodEl = document.getElementById('pg-' + stepId + '-method');
  var pathEl = document.getElementById('pg-' + stepId + '-path');
  if (!methodEl || !pathEl) return;
  var method = config.method || 'GET';
  methodEl.textContent = method;
  methodEl.className = 'pg-method-badge pg-method-' + method.toLowerCase();
  var path = config.path || '/';
  if (config.query && typeof config.query === 'object' && Object.keys(config.query).length > 0) {
    path += '?' + new URLSearchParams(config.query).toString();
  }
  pathEl.textContent = path;
}

function capabilityNames(profile) {
  var caps = profile && profile.usp && profile.usp.capabilities;
  if (!caps) return [];
  return Object.keys(caps);
}

function renderNegotiationGrid(businessCaps, negotiatedCaps) {
  var grid = document.getElementById('pg-negotiation-grid');
  var businessEl = document.getElementById('pg-negotiation-business');
  var intersectionEl = document.getElementById('pg-negotiation-intersection');
  if (!grid || !businessEl || !intersectionEl) return;

  businessEl.innerHTML = businessCaps.map(function (c) {
    return '<li>' + escapeHtml(c) + '</li>';
  }).join('');
  intersectionEl.innerHTML = negotiatedCaps.map(function (c) {
    return '<li>' + escapeHtml(c) + '</li>';
  }).join('');
  grid.classList.remove('pg-hidden');
}

function updateDiscoveryPath() {
  var pathEl = document.getElementById('pg-discovery-path');
  if (pathEl) {
    pathEl.textContent = currentMode === 'ucp-native' ? '/.well-known/ucp' : '/.well-known/usp';
  }
}

function requestBodyFromScenario(data) {
  if (!data || !data.request) return null;
  if (data.request.body) return data.request.body;
  return null;
}

function stepConfigFromScenario(data, stepId, scenarioKey) {
  if (stepId === 'discovery') {
    var path = currentMode === 'ucp-native' ? '/.well-known/ucp' : '/.well-known/usp';
    return { method: 'GET', path: path };
  }
  if (stepId === 'negotiation') {
    return { method: 'POST', path: '/capability-negotiation' };
  }
  if (stepId === 'manage' && scenarioKey && scenarioKey.indexOf('booking_') === 0) {
    return manageOps[scenarioKey] || manageOps.booking_confirmed;
  }
  if (data && data.request) {
    return {
      method: data.request.method,
      path: data.request.path,
      query: data.request.query
    };
  }
  if (stepId === 'manage') {
    return manageOps[scenarioKey] || manageOps.view_booking;
  }
  return { method: 'GET', path: '/' };
}

function negotiationProfilePayload(data) {
  if (data.response && data.response.body) return data.response.body;
  if (data.response) return data.response;
  return data;
}

function renderRequestPane(stepId, data, scenarioKey) {
  var requestEl = document.getElementById('pg-' + stepId + '-request');
  if (!requestEl || !data) return;

  var config = stepConfigFromScenario(data, stepId, scenarioKey);
  var body = stepId === 'negotiation'
    ? negotiationProfilePayload(data)
    : requestBodyFromScenario(data);

  var formatted = formatForTransport(config, body, currentTransport);
  showFormattedRequest(requestEl.id, formatted);
  updatePaneHeaders(stepId, config);
}

function refreshCurrentStepRequest() {
  var state = stepState[currentStep];
  if (state) renderRequestPane(currentStep, state.data, state.scenarioKey);
}

function runStep(stepId) {
  var selectEl = document.getElementById('pg-' + stepId + '-scenario');
  var responseEl = document.getElementById('pg-' + stepId + '-response');
  var runBtn = document.getElementById('pg-' + stepId + '-run');
  if (!selectEl || !responseEl) return;

  var scenarioKey = selectEl.value;
  var file = stepFiles[stepId];
  if (!file) return;

  if (runBtn) {
    runBtn.disabled = true;
    var label = runBtn.querySelector('.pg-btn-text');
    if (label) label.textContent = 'Loading...';
  }

  var actualFile = file;
  var actualKey = scenarioKey;
  if (stepId === 'manage' && scenarioKey.indexOf('booking_') === 0) {
    actualFile = 'webhooks';
  }
  if (stepId === 'negotiation') {
    actualKey = negotiationKeys[scenarioKey] || 'standard';
  }

  loadScenario(actualFile, actualKey, function (data) {
    setTimeout(function () {
      if (data) {
        stepState[stepId] = { data: data, scenarioKey: scenarioKey };
        renderRequestPane(stepId, data, scenarioKey);

        var display;
        var status = 200;
        if (stepId === 'negotiation') {
          var discoveryKey = stepState.discovery ? stepState.discovery.scenarioKey : 'standard';
          var bizKey = businessProfileKey(discoveryKey, scenarioKey);

          if (scenarioKey === 'incompatible') {
            status = 409;
            display = { error: 'No overlapping capabilities between platform and business profiles' };
            showJson(responseEl.id, display);
            setStatus(stepId, status);
            loadScenario('business-profile', bizKey, function (biz) {
              var bizBody = biz && biz.response ? biz.response : biz;
              renderNegotiationGrid(capabilityNames(bizBody), []);
            });
          } else {
            loadScenario('business-profile', bizKey, function (bizData) {
              var bizBody = bizData && bizData.response ? bizData.response : bizData;
              var platBody = negotiationProfilePayload(data);
              display = intersectProfiles(
                bizBody,
                platBody,
                scenarioKey === 'partial-match' ? { stripHolds: true } : {}
              );
              showJson(responseEl.id, display);
              setStatus(stepId, 200);
              renderNegotiationGrid(capabilityNames(bizBody), capabilityNames(display));
            });
          }
        } else if (data.response && data.response.body) {
          display = data.response.body;
          status = data.response.status || 200;
          showJson(responseEl.id, display);
          setStatus(stepId, status);
        } else if (data.response) {
          display = data.response;
          status = data.response.status || 200;
          showJson(responseEl.id, display);
          setStatus(stepId, status);
        } else if (data.payload) {
          display = data.payload;
          showJson(responseEl.id, display);
          setStatus(stepId, status);
        } else {
          display = data;
          showJson(responseEl.id, display);
          setStatus(stepId, status);
        }
      } else {
        showJson(responseEl.id, { error: 'Scenario not found', scenario: scenarioKey });
        setStatus(stepId, 404);
      }

      if (runBtn) {
        runBtn.disabled = false;
        var text = runBtn.querySelector('.pg-btn-text');
        if (!text) return;
        if (stepId === 'discovery') text.textContent = 'Fetch Profile';
        else if (stepId === 'negotiation') text.textContent = 'Run Negotiation';
        else text.textContent = 'Run Request';
      }
    }, 300 + Math.floor(Math.random() * 400));
  });
}

function switchStep(stepId) {
  currentStep = stepId;
  document.querySelectorAll('.pg-step').forEach(function (s) {
    var visible = s.getAttribute('data-step') === stepId;
    s.classList.toggle('pg-step-visible', visible);
    if (visible) {
      s.classList.remove('pg-fade-in');
      void s.offsetWidth;
      s.classList.add('pg-fade-in');
    }
  });
  document.querySelectorAll('.pg-step-pill').forEach(function (p) {
    p.classList.toggle('pg-step-pill-active', p.getAttribute('data-step') === stepId);
  });
  if (stepId === 'discovery' || stepId === 'negotiation') {
    runStep(stepId);
  } else if (stepState[stepId]) {
    renderRequestPane(stepId, stepState[stepId].data, stepState[stepId].scenarioKey);
  }
}

document.querySelectorAll('.pg-step-pill').forEach(function (pill) {
  pill.addEventListener('click', function () {
    switchStep(this.getAttribute('data-step'));
  });
});

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

document.querySelectorAll('.pg-btn-copy').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var target = document.getElementById(this.getAttribute('data-target'));
    if (!target) return;
    navigator.clipboard.writeText(target.textContent || '').then(function () {
      btn.textContent = 'Copied!';
      setTimeout(function () { btn.textContent = 'Copy'; }, 1500);
    });
  });
});

document.querySelectorAll('#pg-mode-toggle .pg-toggle-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('#pg-mode-toggle .pg-toggle-btn').forEach(function (b) {
      b.classList.remove('pg-toggle-active');
    });
    this.classList.add('pg-toggle-active');
    currentMode = this.getAttribute('data-mode') || 'standalone';
    updateDiscoveryPath();
    if (currentStep === 'discovery' && stepState.discovery) {
      renderRequestPane('discovery', stepState.discovery.data, stepState.discovery.scenarioKey);
    } else if (currentStep === 'discovery') {
      runStep('discovery');
    }
  });
});

document.querySelectorAll('#pg-transport-toggle .pg-toggle-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('#pg-transport-toggle .pg-toggle-btn').forEach(function (b) {
      b.classList.remove('pg-toggle-active');
    });
    this.classList.add('pg-toggle-active');
    currentTransport = this.getAttribute('data-transport') || 'rest';
    refreshCurrentStepRequest();
  });
});

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
    if (stepState.manage) {
      stepState.manage.scenarioKey = this.value;
      renderRequestPane('manage', stepState.manage.data, this.value);
    }
  });
}

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
    runStep('discovery');
  });
}

['discovery', 'negotiation', 'browse', 'availability', 'hold', 'book', 'payment', 'manage'].forEach(function (stepId) {
  var btn = document.getElementById('pg-' + stepId + '-run');
  if (btn) btn.addEventListener('click', function () { runStep(stepId); });
});

updateDiscoveryPath();
runStep('discovery');
