/**
 * playground.js — Core engine for the USP Playground.
 *
 * Manages the 8-step scheduling lifecycle simulation: step state machine,
 * scenario loading, mock request execution, mode/transport toggles,
 * navigation, and full DOM rendering.
 *
 * Usage:
 *   const pg = new USPPlayground('playground-root');
 */

import { CodeEditor } from './code-editor.js';
import { ResponseViewer } from './response-viewer.js';
import { formatForTransport } from './transport-formatter.js';

// ---------------------------------------------------------------------------
// Step definitions
// ---------------------------------------------------------------------------

const STEPS = [
  { id: 'discovery',     title: 'Discovery',     subtitle: 'Fetch the business profile',   icon: '1' },
  { id: 'negotiation',   title: 'Negotiate',      subtitle: 'Intersect capabilities',       icon: '2' },
  { id: 'browse',        title: 'Browse',         subtitle: 'Query the service catalog',    icon: '3' },
  { id: 'availability',  title: 'Availability',   subtitle: 'Check time slots',             icon: '4' },
  { id: 'hold',          title: 'Hold',           subtitle: 'Reserve a slot',               icon: '5', optional: true, requires: 'holds' },
  { id: 'book',          title: 'Book',           subtitle: 'Create a booking',             icon: '6' },
  { id: 'payment',       title: 'Payment',        subtitle: 'Complete payment',             icon: '7', modeOnly: 'standalone' },
  { id: 'manage',        title: 'Manage',         subtitle: 'Lifecycle operations',         icon: '8' },
  { id: 'waitlist',      title: 'Waitlist',       subtitle: 'Extension flow',               icon: '★', optional: true, requires: 'waitlist' },
];

// Circled digit characters for the stepper dots
const CIRCLED = {
  '1': '①', '2': '②', '3': '③', '4': '④',
  '5': '⑤', '6': '⑥', '7': '⑦', '8': '⑧',
  '★': '★',
};

// ---------------------------------------------------------------------------
// Per-step request/response configuration (REST-centric)
// ---------------------------------------------------------------------------

const STEP_CONFIGS = {
  discovery: {
    method: 'GET',
    path: '/.well-known/usp',
    hasRequestBody: false,
    scenarios: ['standard', 'full', 'minimal'],
    scenarioLabels: { standard: 'Standard Profile', full: 'Full Profile', minimal: 'Minimal Profile' },
    scenarioFile: 'business-profile',
  },
  negotiation: {
    method: null,
    path: null,
    hasRequestBody: false,
    isComputed: true,
    scenarios: ['full-match', 'partial-match', 'version-mismatch', 'incompatible'],
    scenarioLabels: {
      'full-match': 'Full Match',
      'partial-match': 'Partial Match',
      'version-mismatch': 'Version Mismatch',
      'incompatible': 'Incompatible',
    },
    scenarioFile: 'platform-profile',
  },
  browse: {
    method: 'POST',
    path: '/services/list',
    hasRequestBody: true,
    scenarios: ['happy_path', 'filtered_wellness', 'search_massage', 'empty_results'],
    scenarioLabels: { happy_path: 'Happy Path', filtered_wellness: 'Filtered by Category', search_massage: 'Free-text Search', empty_results: 'Empty Results' },
    scenarioFile: 'services',
    defaultRequest: {
      filters: { category: 'wellness' },
      context: { language: 'en', currency: 'USD' },
      pagination: { limit: 10 },
    },
  },
  availability: {
    method: 'POST',
    path: '/availability/query',
    hasRequestBody: true,
    scenarios: ['available_slots', 'limited_availability', 'resource_specific', 'no_availability', 'range_too_wide'],
    scenarioLabels: {
      available_slots: 'Available Slots',
      limited_availability: 'Limited Availability',
      resource_specific: 'Resource-specific',
      no_availability: 'No Availability',
      range_too_wide: 'Range Too Wide (Error)',
    },
    scenarioFile: 'availability',
    defaultRequest: {
      service_id: 'svc_massage_001',
      start_date: '2026-03-15',
      end_date: '2026-03-17',
      party_size: 1,
    },
  },
  hold: {
    method: 'POST',
    path: '/availability/hold',
    hasRequestBody: true,
    scenarios: ['hold_granted', 'slot_unavailable', 'hold_limit_exceeded'],
    scenarioLabels: { hold_granted: 'Hold Granted', slot_unavailable: 'Slot Unavailable', hold_limit_exceeded: 'Hold Limit Exceeded' },
    scenarioFile: 'holds',
    defaultRequest: {
      slot_id: 'slot_0315_0900',
      service_id: 'svc_massage_001',
      spots: 1,
    },
  },
  book: {
    method: 'POST',
    path: '/bookings',
    hasRequestBody: true,
    scenarios: ['instant_confirmation', 'payment_required', 'manual_confirmation', 'validation_error', 'slot_expired'],
    scenarioLabels: {
      instant_confirmation: 'Instant Confirmation',
      payment_required: 'Payment Required',
      manual_confirmation: 'Manual Confirmation',
      validation_error: 'Validation Error',
      slot_expired: 'Slot Expired',
    },
    scenarioFile: 'bookings',
    defaultRequest: {
      service_id: 'svc_massage_001',
      slot_id: 'slot_0315_0900',
      hold_id: 'hold_abc123',
      buyer: {
        first_name: 'Jane',
        last_name: 'Doe',
        email: 'jane@example.com',
        phone_number: '+1-555-0100',
      },
      party_size: 1,
      notes: 'First visit, prefer firm pressure',
    },
  },
  payment: {
    method: 'POST',
    path: '/bookings/{booking_id}/confirm-payment',
    hasRequestBody: true,
    scenarios: ['payment_success', 'payment_failed', 'deposit_flow'],
    scenarioLabels: {
      payment_success: 'Payment Success',
      payment_failed: 'Payment Failed',
      deposit_flow: 'Deposit Flow',
    },
    scenarioFile: 'payment',
    defaultRequest: {
      transaction_id: 'txn_psp_98765',
      order_reference: 'ord_abc123',
    },
  },
  manage: {
    method: 'GET',
    path: '/bookings/{booking_id}',
    hasRequestBody: false,
    scenarios: ['view_booking', 'update_booking', 'cancel_booking', 'reschedule_booking', 'webhooks'],
    scenarioLabels: {
      view_booking: 'View Booking',
      update_booking: 'Update Booking',
      cancel_booking: 'Cancel Booking',
      reschedule_booking: 'Reschedule',
      webhooks: 'Webhook Events',
    },
    scenarioFile: 'manage',
    subSteps: {
      view_booking:       { method: 'GET',   path: '/bookings/{booking_id}',             hasRequestBody: false },
      update_booking:     { method: 'PATCH', path: '/bookings/{booking_id}',             hasRequestBody: true,
        defaultRequest: { buyer: { phone_number: '+1-555-0199' }, notes: 'Updated: extra firm pressure' } },
      cancel_booking:     { method: 'POST',  path: '/bookings/{booking_id}/cancel',      hasRequestBody: true,
        defaultRequest: { reason: 'Schedule conflict', canceled_by: 'buyer' } },
      reschedule_booking: { method: 'POST',  path: '/bookings/{booking_id}/reschedule',  hasRequestBody: true,
        defaultRequest: { new_slot_id: 'slot_0316_1400' } },
      webhooks:   { method: 'POST',  path: '/webhooks (simulated)',              hasRequestBody: false },
    },
  },
  waitlist: {
    method: 'POST',
    path: '/waitlist',
    hasRequestBody: true,
    scenarios: ['join_waitlist', 'offer_received', 'accept_offer', 'decline_offer'],
    scenarioLabels: {
      join_waitlist: 'Join Waitlist',
      offer_received: 'Offer Received',
      accept_offer: 'Accept Offer',
      decline_offer: 'Decline Offer',
    },
    scenarioFile: 'waitlist',
    defaultRequest: {
      service_id: 'svc_massage_001',
      buyer: {
        first_name: 'Jane',
        last_name: 'Doe',
        email: 'jane@example.com',
      },
      preferred_slots: [
        { date: '2026-03-15', time_of_day: 'morning' },
        { date: '2026-03-16', time_of_day: 'any' },
      ],
    },
  },
};

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'className') { node.className = v; }
    else if (k === 'textContent') { node.textContent = v; }
    else if (k === 'innerHTML') { node.innerHTML = v; }
    else if (k.startsWith('on')) { node.addEventListener(k.slice(2).toLowerCase(), v); }
    else if (k === 'style' && typeof v === 'object') { Object.assign(node.style, v); }
    else { node.setAttribute(k, v); }
  }
  for (const child of children) {
    if (typeof child === 'string') { node.appendChild(document.createTextNode(child)); }
    else if (child) { node.appendChild(child); }
  }
  return node;
}

function randomDelay() {
  return 200 + Math.floor(Math.random() * 600);
}

// ---------------------------------------------------------------------------
// USPPlayground class
// ---------------------------------------------------------------------------

export class USPPlayground {
  /**
   * @param {string} containerId - ID of the mount-point element.
   */
  constructor(containerId) {
    this._root = document.getElementById(containerId);
    if (!this._root) throw new Error(`Element #${containerId} not found`);

    // State
    this._step = 0;
    this._mode = 'standalone';     // 'standalone' | 'ucp-native'
    this._transport = 'rest';      // 'rest' | 'mcp' | 'a2a' | 'esp'
    this._scenario = {};           // per-step selected scenario key
    this._completedSteps = new Set();
    this._scenarioCache = {};      // scenarioFile -> fetched JSON
    this._running = false;

    // Sub-step for the manage step
    this._manageTab = 'view_booking';

    // Feature flags derived from profile (defaults assume full profile)
    this._features = { holds: true, waitlist: true };

    // DOM references (set during render)
    this._els = {};

    // Component instances
    this._requestEditor = null;
    this._responseViewer = null;

    this._render();
    this._goToStep(0);
  }

  // -----------------------------------------------------------------------
  // Public API
  // -----------------------------------------------------------------------

  goToStep(n)            { this._goToStep(n); }
  runRequest()           { this._runRequest(); }
  setScenario(name)      { this._setScenarioForStep(this._step, name); this._refreshStepContent(); }
  setMode(mode)          { this._mode = mode; this._refreshAll(); }
  setTransport(transport){ this._transport = transport; this._refreshStepContent(); }

  // -----------------------------------------------------------------------
  // Rendering — builds the full playground DOM
  // -----------------------------------------------------------------------

  _render() {
    this._root.innerHTML = '';
    this._root.className = 'pg-playground';

    // Header
    const header = el('div', { className: 'pg-header' }, [
      this._buildModeToggle(),
      el('h2', { textContent: 'USP Playground' }),
      this._buildTransportToggle(),
    ]);
    this._root.appendChild(header);

    // Stepper
    this._els.stepper = el('div', { className: 'pg-stepper' });
    this._root.appendChild(this._els.stepper);
    this._renderStepper();

    // Content area
    this._els.content = el('div', { className: 'pg-content' });
    this._root.appendChild(this._els.content);
  }

  // -- Mode toggle --------------------------------------------------------

  _buildModeToggle() {
    const wrap = el('div', { className: 'pg-mode-toggle' });
    const modes = [
      { value: 'standalone',  label: 'Standalone' },
      { value: 'ucp-native',  label: 'UCP-Native' },
    ];
    modes.forEach(({ value, label }) => {
      const btn = el('button', {
        className: `pg-toggle-btn${this._mode === value ? ' pg-toggle-active' : ''}`,
        textContent: label,
        'data-mode': value,
        onClick: () => {
          this._mode = value;
          this._refreshAll();
        },
      });
      wrap.appendChild(btn);
    });
    this._els.modeToggle = wrap;
    return wrap;
  }

  // -- Transport toggle ---------------------------------------------------

  _buildTransportToggle() {
    const wrap = el('div', { className: 'pg-transport-toggle' });
    const transports = ['REST', 'MCP', 'A2A', 'ESP'];
    transports.forEach(t => {
      const val = t.toLowerCase();
      const btn = el('button', {
        className: `pg-toggle-btn${this._transport === val ? ' pg-toggle-active' : ''}`,
        textContent: t,
        'data-transport': val,
        onClick: () => {
          this._transport = val;
          this._refreshTransportToggle();
          this._refreshStepContent();
        },
      });
      wrap.appendChild(btn);
    });
    this._els.transportToggle = wrap;
    return wrap;
  }

  _refreshTransportToggle() {
    if (!this._els.transportToggle) return;
    this._els.transportToggle.querySelectorAll('.pg-toggle-btn').forEach(btn => {
      btn.classList.toggle('pg-toggle-active', btn.dataset.transport === this._transport);
    });
  }

  // -- Stepper dots -------------------------------------------------------

  _renderStepper() {
    const stepper = this._els.stepper;
    stepper.innerHTML = '';

    this._visibleSteps().forEach((stepDef, visIdx) => {
      const realIdx = STEPS.indexOf(stepDef);
      const dot = el('div', {
        className: this._stepDotClass(realIdx),
        'data-step': String(realIdx),
        title: `${stepDef.title}: ${stepDef.subtitle}`,
        onClick: () => this._goToStep(realIdx),
      }, [
        el('span', { className: 'pg-dot-icon', textContent: CIRCLED[stepDef.icon] || stepDef.icon }),
        el('span', { className: 'pg-dot-label', textContent: stepDef.title }),
      ]);
      stepper.appendChild(dot);
    });
  }

  _stepDotClass(idx) {
    let cls = 'pg-step-dot';
    if (idx === this._step) cls += ' pg-step-active';
    if (this._completedSteps.has(idx)) cls += ' pg-step-done';
    const def = STEPS[idx];
    if (def.optional) cls += ' pg-step-optional';
    return cls;
  }

  // -- Visible steps (filtered by mode/features) -------------------------

  _visibleSteps() {
    return STEPS.filter(s => {
      if (s.modeOnly && s.modeOnly !== this._mode) return false;
      if (s.requires === 'holds' && !this._features.holds) return false;
      if (s.requires === 'waitlist' && !this._features.waitlist) return false;
      return true;
    });
  }

  _isStepVisible(idx) {
    return this._visibleSteps().includes(STEPS[idx]);
  }

  // -- Navigation ---------------------------------------------------------

  _goToStep(n) {
    if (n < 0 || n >= STEPS.length) return;
    // Skip invisible steps
    if (!this._isStepVisible(n)) {
      // Try next
      if (n > this._step) {
        this._goToStep(n + 1);
      } else {
        this._goToStep(n - 1);
      }
      return;
    }
    this._step = n;
    this._renderStepper();
    this._refreshStepContent();
  }

  _nextVisibleStep() {
    for (let i = this._step + 1; i < STEPS.length; i++) {
      if (this._isStepVisible(i)) return i;
    }
    return -1;
  }

  _prevVisibleStep() {
    for (let i = this._step - 1; i >= 0; i--) {
      if (this._isStepVisible(i)) return i;
    }
    return -1;
  }

  // -----------------------------------------------------------------------
  // Step content rendering
  // -----------------------------------------------------------------------

  _refreshAll() {
    // Re-render mode toggle active states
    if (this._els.modeToggle) {
      this._els.modeToggle.querySelectorAll('.pg-toggle-btn').forEach(btn => {
        btn.classList.toggle('pg-toggle-active', btn.dataset.mode === this._mode);
      });
    }
    this._renderStepper();
    // If current step is now invisible, move to nearest visible
    if (!this._isStepVisible(this._step)) {
      const prev = this._prevVisibleStep();
      const next = this._nextVisibleStep();
      this._goToStep(prev >= 0 ? prev : (next >= 0 ? next : 0));
      return;
    }
    this._refreshStepContent();
  }

  _refreshStepContent() {
    const content = this._els.content;
    content.innerHTML = '';

    const stepDef = STEPS[this._step];
    const config = STEP_CONFIGS[stepDef.id];
    const scenarioKey = this._scenario[stepDef.id] || config.scenarios[0];

    // -- Step header ------------------------------------------------------
    const stepHeader = el('div', { className: 'pg-step-header' }, [
      el('h3', { textContent: `Step ${stepDef.icon}: ${stepDef.title}` }),
      el('p', { textContent: stepDef.subtitle }),
    ]);

    // Scenario selector
    if (config.scenarios.length > 1) {
      const select = el('select', {
        className: 'pg-scenario-select-input',
        onChange: (e) => {
          this._setScenarioForStep(this._step, e.target.value);
          this._refreshStepContent();
        },
      });
      config.scenarios.forEach(s => {
        const opt = el('option', { value: s, textContent: config.scenarioLabels[s] || s });
        if (s === scenarioKey) opt.selected = true;
        select.appendChild(opt);
      });
      const scenarioWrap = el('div', { className: 'pg-scenario-select' }, [
        el('label', { textContent: 'Scenario: ' }),
        select,
      ]);
      stepHeader.appendChild(scenarioWrap);
    }

    // Manage sub-tabs
    if (stepDef.id === 'manage' && config.subSteps) {
      const tabBar = el('div', { className: 'pg-tab-bar' });
      for (const key of Object.keys(config.subSteps)) {
        const label = config.scenarioLabels[key] || key;
        const btn = el('button', {
          className: `pg-tab-btn${this._manageTab === key ? ' pg-tab-active' : ''}`,
          textContent: label,
          onClick: () => { this._manageTab = key; this._refreshStepContent(); },
        });
        tabBar.appendChild(btn);
      }
      stepHeader.appendChild(tabBar);
    }

    content.appendChild(stepHeader);

    // -- Determine effective config (manage sub-steps override) -----------
    let effectiveConfig = config;
    let effectiveRequest = config.defaultRequest || null;
    if (stepDef.id === 'manage' && config.subSteps) {
      const sub = config.subSteps[this._manageTab];
      if (sub) {
        effectiveConfig = { ...config, ...sub };
        effectiveRequest = sub.defaultRequest || null;
      }
    }

    // -- Special: negotiation step (no HTTP request) ----------------------
    if (stepDef.id === 'negotiation') {
      this._renderNegotiationStep(content, scenarioKey);
      this._renderNavFooter(content);
      return;
    }

    // -- Request pane -----------------------------------------------------
    if (effectiveConfig.method) {
      const requestPane = el('div', { className: 'pg-request-pane' });

      // Pane header
      const paneHeader = el('div', { className: 'pg-pane-header' }, [
        el('span', { className: 'pg-method-badge', textContent: effectiveConfig.method }),
        el('span', { className: 'pg-path', textContent: effectiveConfig.path }),
      ]);
      requestPane.appendChild(paneHeader);

      // Format for current transport
      const formatted = formatForTransport(
        { method: effectiveConfig.method, path: effectiveConfig.path },
        effectiveRequest,
        this._transport
      );

      // Code block
      const pre = el('pre', { className: 'pg-code' });
      const code = el('code');
      pre.appendChild(code);
      requestPane.appendChild(pre);

      // Use CodeEditor for editable request, or just set innerHTML for non-REST
      if (this._transport === 'rest') {
        // For REST, show raw HTTP which is not JSON — just escape and display
        code.textContent = formatted.display;
        if (effectiveConfig.hasRequestBody && effectiveRequest) {
          pre.classList.add('pg-code-editable');
          code.setAttribute('contenteditable', 'true');
          code.setAttribute('spellcheck', 'false');
        }
      } else {
        // For MCP/A2A, use CodeEditor with highlighting
        this._requestEditor = new CodeEditor(code, formatted.display, { editable: false });
        // Override: set raw display since it may be JSON
        if (formatted.language === 'json') {
          try {
            const parsed = JSON.parse(formatted.display);
            this._requestEditor = new CodeEditor(code, parsed, { editable: false });
          } catch { /* use as-is */ }
        }
      }

      content.appendChild(requestPane);
    }

    // -- Actions row ------------------------------------------------------
    const actions = el('div', { className: 'pg-actions' });

    const prevIdx = this._prevVisibleStep();
    if (prevIdx >= 0) {
      actions.appendChild(el('button', {
        className: 'pg-btn pg-btn-back',
        textContent: '◀ Back',
        onClick: () => this._goToStep(prevIdx),
      }));
    } else {
      actions.appendChild(el('span')); // spacer
    }

    if (effectiveConfig.method) {
      const runBtn = el('button', {
        className: 'pg-btn pg-btn-run',
        textContent: 'Run Request ▶',
        onClick: () => this._runRequest(),
      });
      this._els.runBtn = runBtn;
      actions.appendChild(runBtn);
    }

    content.appendChild(actions);

    // -- Response pane (hidden until run) ----------------------------------
    const responsePane = el('div', { className: 'pg-response-pane', style: { display: 'none' } });
    content.appendChild(responsePane);
    this._responseViewer = new ResponseViewer(responsePane);

    // -- Validation placeholder -------------------------------------------
    this._els.validation = el('div', { className: 'pg-validation', style: { display: 'none' } });
    content.appendChild(this._els.validation);

    // -- Nav footer -------------------------------------------------------
    this._renderNavFooter(content);
  }

  // -- Negotiation (special step) -----------------------------------------

  _renderNegotiationStep(content, scenarioKey) {
    const info = el('div', { className: 'pg-negotiation' });

    info.appendChild(el('p', {
      className: 'pg-negotiation-desc',
      textContent: 'Capability negotiation intersects the platform profile with the business profile to determine the active capability set for this session.',
    }));

    // Side by side boxes
    const columns = el('div', { className: 'pg-negotiation-columns' });

    // Platform side
    const platformBox = el('div', { className: 'pg-negotiation-box' });
    platformBox.appendChild(el('h4', { textContent: 'Platform Capabilities' }));
    const platformPre = el('pre', { className: 'pg-code' });
    const platformCode = el('code');
    platformPre.appendChild(platformCode);
    new CodeEditor(platformCode, {
      capabilities: {
          'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }],
          'dev.usp-protocol.services.availability': [{ version: '2026-08-20', holds: true }],
          'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }],
          'dev.usp-protocol.services.waitlist': [{ version: '2026-08-20' }]
        },
    });
    platformBox.appendChild(platformPre);
    columns.appendChild(platformBox);

    // Business side
    const businessBox = el('div', { className: 'pg-negotiation-box' });
    businessBox.appendChild(el('h4', { textContent: 'Business Capabilities' }));
    const businessPre = el('pre', { className: 'pg-code' });
    const businessCode = el('code');
    businessPre.appendChild(businessCode);

    const businessCaps = {
      'full-match': {
        'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }],
        'dev.usp-protocol.services.availability': [{ version: '2026-08-20', holds: true }],
        'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }],
        'dev.usp-protocol.services.waitlist': [{ version: '2026-08-20' }],
      },
      'partial-match': {
        'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }],
        'dev.usp-protocol.services.availability': [{ version: '2026-08-20', holds: false }],
        'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }],
      },
      'version-mismatch': {
        'dev.usp-protocol.services.catalog': [{ version: '2026-02-21' }],
        'dev.usp-protocol.services.availability': [{ version: '2026-02-21' }],
        'dev.usp-protocol.services.bookings': [{ version: '2026-02-21' }],
      },
      'incompatible': {},
    };
    new CodeEditor(businessCode, { capabilities: businessCaps[scenarioKey] || businessCaps['full-match'] });
    businessBox.appendChild(businessPre);
    columns.appendChild(businessBox);

    info.appendChild(columns);

    // Result
    const resultBox = el('div', { className: 'pg-negotiation-result' });
    resultBox.appendChild(el('h4', { textContent: 'Negotiated Result' }));

    const resultMessages = {
      'full-match': { status: 'success', text: 'Full capability match. All features active including holds and waitlist.' },
      'partial-match': { status: 'success', text: 'Partial match. Holds disabled (business does not support). Waitlist pruned (no business support).' },
      'version-mismatch': { status: 'warning', text: 'Version mismatch. Compatible older version selected (2026-02-21). Some features may be unavailable.' },
      'incompatible': { status: 'error', text: 'Empty intersection. No compatible capabilities found. Error: capabilities_incompatible' },
    };

    const result = resultMessages[scenarioKey] || resultMessages['full-match'];
    const badge = el('span', {
      className: `pg-negotiation-badge pg-negotiation-${result.status}`,
      textContent: result.status === 'success' ? '✓' : result.status === 'warning' ? '⚠' : '✗',
    });
    resultBox.appendChild(el('p', {}, [badge, document.createTextNode(' ' + result.text)]));
    info.appendChild(resultBox);

    content.appendChild(info);
  }

  // -- Nav footer ---------------------------------------------------------

  _renderNavFooter(content) {
    const footer = el('div', { className: 'pg-nav-footer' });
    const prevIdx = this._prevVisibleStep();
    const nextIdx = this._nextVisibleStep();

    if (prevIdx >= 0) {
      footer.appendChild(el('a', {
        className: 'pg-prev-link',
        textContent: `◀ Previous: ${STEPS[prevIdx].title}`,
        href: '#',
        onClick: (e) => { e.preventDefault(); this._goToStep(prevIdx); },
      }));
    } else {
      footer.appendChild(el('span'));
    }

    if (nextIdx >= 0) {
      footer.appendChild(el('a', {
        className: 'pg-next-link',
        textContent: `Next: ${STEPS[nextIdx].title} ▶`,
        href: '#',
        onClick: (e) => { e.preventDefault(); this._goToStep(nextIdx); },
      }));
    } else {
      footer.appendChild(el('span'));
    }

    content.appendChild(footer);
  }

  // -----------------------------------------------------------------------
  // Mock request execution
  // -----------------------------------------------------------------------

  async _runRequest() {
    if (this._running) return;
    this._running = true;

    const runBtn = this._els.runBtn;
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.textContent = 'Running...';
    }

    const stepDef = STEPS[this._step];
    const config = STEP_CONFIGS[stepDef.id];
    const scenarioKey = this._scenario[stepDef.id] || config.scenarios[0];

    // Simulate network latency
    const delay = randomDelay();
    await new Promise(resolve => setTimeout(resolve, delay));

    // Try to fetch scenario data, fall back to inline mock
    let responseData;
    try {
      responseData = await this._loadScenario(config.scenarioFile, scenarioKey);
    } catch {
      responseData = this._inlineMockResponse(stepDef.id, scenarioKey);
    }

    // Determine status code
    const status = responseData._status || 200;
    const body = { ...responseData };
    delete body._status;

    // Show response
    this._responseViewer.show({ status, timing: delay, body });

    // Show validation
    this._showValidation(status);

    // Mark step complete on success
    if (status >= 200 && status < 300) {
      this._completedSteps.add(this._step);
      this._renderStepper();
    }

    if (runBtn) {
      runBtn.disabled = false;
      runBtn.textContent = 'Run Request ▶';
    }
    this._running = false;
  }

  _showValidation(status) {
    const v = this._els.validation;
    if (!v) return;
    v.style.display = '';
    if (status >= 200 && status < 300) {
      v.innerHTML = '<span class="pg-validation-ok">✓ Response valid</span>';
    } else {
      v.innerHTML = '<span class="pg-validation-err">✗ Error response</span>';
    }
  }

  // -----------------------------------------------------------------------
  // Scenario loading
  // -----------------------------------------------------------------------

  async _loadScenario(file, key) {
    const cacheKey = `${file}`;
    if (!this._scenarioCache[cacheKey]) {
      const basePath = this._detectBasePath();
      const url = `${basePath}scenarios/${file}.json`;
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`Failed to load ${url}: ${resp.status}`);
      this._scenarioCache[cacheKey] = await resp.json();
    }
    const data = this._scenarioCache[cacheKey];
    const scenario = data[key];
    if (!scenario) return null;
    // Scenario files use { description, request, response: { status, body } }
    // Normalize to the { _status, ...body } format the runner expects
    if (scenario.response) {
      const status = scenario.response.status || 200;
      const body = scenario.response.body || {};
      return { _status: status, ...body };
    }
    return scenario;
  }

  _detectBasePath() {
    // Try common paths for MkDocs-served playground files
    const candidates = [
      'playground/',
      '../playground/',
      './playground/',
    ];
    // If the URL contains /playground/, assets are siblings
    if (window.location.pathname.includes('/playground')) {
      return 'playground/';
    }
    return 'playground/';
  }

  _setScenarioForStep(stepIdx, key) {
    const stepDef = STEPS[stepIdx];
    this._scenario[stepDef.id] = key;
  }

  // -----------------------------------------------------------------------
  // Inline mock responses (used when scenario files are not available)
  // -----------------------------------------------------------------------

  _inlineMockResponse(stepId, scenario) {
    const mocks = {
      discovery: {
        standard: {
          _status: 200,
          usp: {
            version: '2026-08-20',
            capabilities: {
              'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }],
              'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }],
              'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }],
            },
          },
          business: {
            id: 'biz_downtown_spa',
            name: 'Downtown Wellness Spa',
            timezone: 'America/New_York',
          },
          services: [
            { path: '/services', methods: ['GET', 'POST'] },
            { path: '/availability', methods: ['POST'] },
            { path: '/bookings', methods: ['GET', 'POST', 'PATCH'] },
          ],
        },
        full: {
          _status: 200,
          usp: {
            version: '2026-08-20',
            capabilities: {
              'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }],
              'dev.usp-protocol.services.availability': [{ version: '2026-08-20', holds: true }],
              'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }],
              'dev.usp-protocol.services.waitlist': [{ version: '2026-08-20' }],
            },
          },
          business: {
            id: 'biz_downtown_spa',
            name: 'Downtown Wellness Spa',
            timezone: 'America/New_York',
          },
          signing_keys: [{ kid: 'key-2026-01', kty: 'EC', crv: 'P-256' }],
        },
        minimal: {
          _status: 200,
          usp: {
            version: '2026-08-20',
            capabilities: {
              'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }],
              'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }],
              'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }],
            },
          },
          business: {
            id: 'biz_downtown_spa',
            name: 'Downtown Wellness Spa',
            timezone: 'America/New_York',
          },
        },
      },
      browse: {
        happy: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }] } },
          services: [
            { id: 'svc_massage_001', name: 'Swedish Massage', type: 'appointment', duration: { fixed: 'PT60M' }, pricing: { model: 'fixed', amount: 12000, currency: 'USD' } },
            { id: 'svc_yoga_001', name: 'Morning Yoga', type: 'group', duration: { fixed: 'PT75M' }, pricing: { model: 'per_person', amount: 2500, currency: 'USD' }, capacity: { max: 20 } },
            { id: 'svc_suite_001', name: 'Spa Suite Experience', type: 'reservation', duration: { fixed: 'PT120M' }, pricing: { model: 'fixed', amount: 35000, currency: 'USD' } },
            { id: 'svc_kayak_001', name: 'Kayak Rental', type: 'rental', duration: { range: { min: 60, max: 480 } }, pricing: { model: 'hourly', amount: 4500, currency: 'USD' } },
          ],
          pagination: { has_more: false },
        },
        filtered: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }] } },
          services: [
            { id: 'svc_massage_001', name: 'Swedish Massage', type: 'appointment', duration: { fixed: 'PT60M' }, pricing: { model: 'fixed', amount: 12000, currency: 'USD' } },
          ],
          pagination: { has_more: false },
        },
        search: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }] } },
          services: [
            { id: 'svc_massage_001', name: 'Swedish Massage', type: 'appointment', duration: { fixed: 'PT60M' }, pricing: { model: 'fixed', amount: 12000, currency: 'USD' } },
          ],
          pagination: { has_more: false },
        },
        empty: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.catalog': [{ version: '2026-08-20' }] } },
          services: [],
          pagination: { has_more: false },
          messages: [{ type: 'info', content: 'No services match the provided filters.' }],
        },
      },
      availability: {
        available: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }] } },
          slots: [
            { id: 'slot_0315_0900', start: '2026-03-15T09:00:00-04:00', end: '2026-03-15T10:00:00-04:00', capacity: { total: 1, remaining: 1 }, resources: [{ type: 'staff', name: 'Sarah' }] },
            { id: 'slot_0315_1100', start: '2026-03-15T11:00:00-04:00', end: '2026-03-15T12:00:00-04:00', capacity: { total: 1, remaining: 1 }, resources: [{ type: 'staff', name: 'Mike' }] },
            { id: 'slot_0316_1400', start: '2026-03-16T14:00:00-04:00', end: '2026-03-16T15:00:00-04:00', capacity: { total: 1, remaining: 1 }, resources: [{ type: 'staff', name: 'Sarah' }] },
          ],
          opening_hours: [
            { day_of_week: 'monday', opens: '09:00', closes: '18:00' },
            { day_of_week: 'tuesday', opens: '09:00', closes: '18:00' },
          ],
        },
        limited: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }] } },
          slots: [
            { id: 'slot_0315_1800', start: '2026-03-15T18:00:00-04:00', end: '2026-03-15T19:15:00-04:00', capacity: { total: 20, remaining: 2 }, resources: [{ type: 'staff', name: 'Emma' }] },
          ],
          messages: [{ type: 'warning', content: 'Limited spots remaining for this class.' }],
        },
        'resource-specific': {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }] } },
          slots: [
            { id: 'slot_0315_0900', start: '2026-03-15T09:00:00-04:00', end: '2026-03-15T10:00:00-04:00', capacity: { total: 1, remaining: 1 }, resources: [{ type: 'staff', name: 'Sarah' }] },
            { id: 'slot_0316_1400', start: '2026-03-16T14:00:00-04:00', end: '2026-03-16T15:00:00-04:00', capacity: { total: 1, remaining: 1 }, resources: [{ type: 'staff', name: 'Sarah' }] },
          ],
        },
        none: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }] } },
          slots: [],
          messages: [{ type: 'info', content: 'No availability in the requested date range. Consider joining the waitlist.' }],
        },
        'range-too-wide': {
          _status: 422,
          type: 'https://usp-protocol.dev/errors/range-too-wide',
          title: 'Date range too wide',
          status: 422,
          detail: 'Query range exceeds the maximum of 7 calendar days.',
          code: 'range_too_wide',
        },
      },
      hold: {
        granted: {
          _status: 201,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.availability': [{ version: '2026-08-20' }] } },
          hold: {
            id: 'hold_abc123',
            slot_id: 'slot_0315_0900',
            service_id: 'svc_massage_001',
            spots: 1,
            status: 'active',
            expires_at: '2026-03-15T08:55:00-04:00',
          },
        },
        unavailable: {
          _status: 409,
          type: 'https://usp-protocol.dev/errors/slot-unavailable',
          title: 'Slot unavailable',
          status: 409,
          detail: 'The requested slot is no longer available.',
          code: 'slot_unavailable',
        },
        'limit-exceeded': {
          _status: 409,
          type: 'https://usp-protocol.dev/errors/hold-limit-exceeded',
          title: 'Hold limit exceeded',
          status: 409,
          detail: 'Maximum one concurrent hold per appointment-type service.',
          code: 'hold_limit_exceeded',
        },
      },
      book: {
        instant: {
          _status: 201,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_001',
            service_id: 'svc_massage_001',
            status: 'confirmed',
            slot: { id: 'slot_0315_0900', start: '2026-03-15T09:00:00-04:00', end: '2026-03-15T10:00:00-04:00' },
            buyer: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com' },
            actions: [],
            created_at: '2026-03-14T15:30:00-04:00',
          },
        },
        'payment-required': {
          _status: 201,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_002',
            service_id: 'svc_massage_001',
            status: 'requires_action',
            slot: { id: 'slot_0315_0900', start: '2026-03-15T09:00:00-04:00', end: '2026-03-15T10:00:00-04:00' },
            buyer: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com' },
            actions: [
              { type: 'payment', status: 'pending', continue_url: 'https://business.example.com/pay/bkg_002', expires_at: '2026-03-14T16:00:00-04:00',
                payment_context: { amount_due: 12000, currency: 'USD', description: 'Swedish Massage - 60min' } },
            ],
            created_at: '2026-03-14T15:30:00-04:00',
          },
        },
        manual: {
          _status: 201,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_003',
            service_id: 'svc_massage_001',
            status: 'pending',
            confirmation_mode: 'manual',
            slot: { id: 'slot_0315_0900', start: '2026-03-15T09:00:00-04:00', end: '2026-03-15T10:00:00-04:00' },
            buyer: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com' },
            actions: [],
            messages: [{ type: 'info', content: 'Your booking is pending manual confirmation by the business.' }],
            created_at: '2026-03-14T15:30:00-04:00',
          },
        },
        'validation-error': {
          _status: 422,
          type: 'https://usp-protocol.dev/errors/validation-error',
          title: 'Validation Error',
          status: 422,
          detail: 'Missing required buyer fields.',
          code: 'validation_error',
          errors: [
            { field: 'buyer.email', message: 'Email is required.' },
            { field: 'buyer.first_name', message: 'First name is required.' },
          ],
        },
        'slot-expired': {
          _status: 409,
          type: 'https://usp-protocol.dev/errors/slot-unavailable',
          title: 'Hold expired',
          status: 409,
          detail: 'The hold on this slot has expired. Please check availability again.',
          code: 'slot_unavailable',
        },
      },
      payment: {
        success: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_002',
            status: 'confirmed',
            payment: { status: 'paid', amount: 12000, currency: 'USD', transaction_id: 'txn_psp_98765', order_reference: 'ord_abc123' },
            actions: [{ type: 'payment', status: 'completed' }],
          },
        },
        failed: {
          _status: 422,
          type: 'https://usp-protocol.dev/errors/payment-failed',
          title: 'Payment failed',
          status: 422,
          detail: 'The payment processor declined the transaction.',
          code: 'payment_failed',
        },
        'actions-pending': {
          _status: 422,
          type: 'https://usp-protocol.dev/errors/actions-pending',
          title: 'Actions pending',
          status: 422,
          detail: 'Non-payment actions are still pending. Complete them before confirming payment.',
          code: 'actions_pending',
        },
        deposit: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_004',
            status: 'confirmed',
            payment: { status: 'partially_paid', amount: 35000, currency: 'USD', deposit_amount: 10000, transaction_id: 'txn_psp_11111' },
            actions: [{ type: 'payment', status: 'completed' }],
          },
        },
      },
      manage: {
        view: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_001',
            service_id: 'svc_massage_001',
            status: 'confirmed',
            slot: { id: 'slot_0315_0900', start: '2026-03-15T09:00:00-04:00', end: '2026-03-15T10:00:00-04:00' },
            buyer: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com', phone_number: '+1-555-0100' },
            resources: [{ type: 'staff', name: 'Sarah' }],
            payment: { status: 'paid', amount: 12000, currency: 'USD' },
            notes: 'First visit, prefer firm pressure',
            created_at: '2026-03-14T15:30:00-04:00',
            updated_at: '2026-03-14T15:30:00-04:00',
          },
        },
        update: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_001',
            status: 'confirmed',
            buyer: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com', phone_number: '+1-555-0199' },
            notes: 'Updated: extra firm pressure',
            updated_at: '2026-03-14T16:00:00-04:00',
          },
        },
        cancel: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_001',
            status: 'canceled',
            cancellation: { reason: 'Schedule conflict', canceled_by: 'buyer', canceled_at: '2026-03-14T16:10:00-04:00' },
            payment: { status: 'refunded', amount: 12000, currency: 'USD' },
          },
        },
        reschedule: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.bookings': [{ version: '2026-08-20' }] } },
          booking: {
            id: 'bkg_001',
            status: 'confirmed',
            slot: { id: 'slot_0316_1400', start: '2026-03-16T14:00:00-04:00', end: '2026-03-16T15:00:00-04:00' },
            updated_at: '2026-03-14T16:15:00-04:00',
          },
        },
        webhooks: {
          _status: 200,
          event: 'booking.confirmed',
          event_id: 'evt_abc123',
          timestamp: '2026-03-15T09:00:05-04:00',
          data: {
            booking_id: 'bkg_001',
            service_id: 'svc_massage_001',
            status: 'confirmed',
          },
        },
      },
      waitlist: {
        join: {
          _status: 201,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.waitlist': [{ version: '2026-08-20' }] } },
          entry: {
            id: 'wl_001',
            service_id: 'svc_massage_001',
            status: 'waiting',
            position: 3,
            created_at: '2026-03-14T16:30:00-04:00',
          },
        },
        offered: {
          _status: 200,
          event: 'waitlist.offered',
          event_id: 'evt_wl_001',
          data: {
            entry_id: 'wl_001',
            offered_slot: { id: 'slot_0317_1000', start: '2026-03-17T10:00:00-04:00', end: '2026-03-17T11:00:00-04:00' },
            expires_at: '2026-03-14T17:00:00-04:00',
          },
        },
        accept: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.waitlist': [{ version: '2026-08-20' }] } },
          entry: { id: 'wl_001', status: 'accepted' },
          booking: {
            id: 'bkg_005',
            service_id: 'svc_massage_001',
            status: 'confirmed',
            slot: { id: 'slot_0317_1000', start: '2026-03-17T10:00:00-04:00', end: '2026-03-17T11:00:00-04:00' },
          },
        },
        decline: {
          _status: 200,
          usp: { version: '2026-08-20', capabilities: { 'dev.usp-protocol.services.waitlist': [{ version: '2026-08-20' }] } },
          entry: { id: 'wl_001', status: 'waiting', position: 3 },
        },
        expired: {
          _status: 200,
          event: 'waitlist.expired',
          event_id: 'evt_wl_002',
          data: {
            entry_id: 'wl_001',
            expired_slot: { id: 'slot_0317_1000' },
          },
        },
      },
    };

    const stepMocks = mocks[stepId];
    if (!stepMocks) return { _status: 200, message: 'Mock not available for this step.' };

    // For manage step, use the manage sub-tab as scenario key
    if (stepId === 'manage') {
      return stepMocks[this._manageTab] || stepMocks.view;
    }

    return stepMocks[scenario] || stepMocks[Object.keys(stepMocks)[0]];
  }
}
