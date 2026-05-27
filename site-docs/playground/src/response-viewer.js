/**
 * response-viewer.js — Read-only response display with status badge,
 * simulated timing, collapsible sections, and copy button.
 *
 * Builds on the same highlighting engine as code-editor.js.
 */

import { highlightJson } from './code-editor.js';

/**
 * Determine the CSS modifier class for an HTTP status code.
 * @param {number} status
 * @returns {string}
 */
function statusClass(status) {
  if (status >= 200 && status < 300) return 'pg-status-2xx';
  if (status >= 300 && status < 400) return 'pg-status-3xx';
  if (status >= 400 && status < 500) return 'pg-status-4xx';
  return 'pg-status-5xx';
}

/**
 * Friendly label for an HTTP status code.
 * @param {number} status
 * @returns {string}
 */
function statusLabel(status) {
  const labels = {
    200: '200 OK',
    201: '201 Created',
    204: '204 No Content',
    400: '400 Bad Request',
    401: '401 Unauthorized',
    403: '403 Forbidden',
    404: '404 Not Found',
    409: '409 Conflict',
    422: '422 Unprocessable Entity',
    424: '424 Failed Dependency',
    429: '429 Too Many Requests',
    500: '500 Internal Server Error',
    503: '503 Service Unavailable',
  };
  return labels[status] || `${status}`;
}

const COLLAPSE_THRESHOLD = 30; // lines before offering collapse

/**
 * ResponseViewer — manages the response display pane.
 */
export class ResponseViewer {
  /**
   * @param {HTMLElement} container - The .pg-response-pane element.
   */
  constructor(container) {
    this._container = container;
    this._headerEl = null;
    this._codeEl = null;
    this._rawJson = '';
    this._build();
  }

  /** Build the internal DOM structure. */
  _build() {
    this._container.innerHTML = '';

    // Header row: status badge + timing + copy button
    this._headerEl = document.createElement('div');
    this._headerEl.className = 'pg-pane-header';
    this._container.appendChild(this._headerEl);

    this._statusBadge = document.createElement('span');
    this._statusBadge.className = 'pg-status-badge';
    this._headerEl.appendChild(this._statusBadge);

    this._timingEl = document.createElement('span');
    this._timingEl.className = 'pg-timing';
    this._headerEl.appendChild(this._timingEl);

    // Spacer
    const spacer = document.createElement('span');
    spacer.style.flex = '1';
    this._headerEl.appendChild(spacer);

    // Copy button
    this._copyBtn = document.createElement('button');
    this._copyBtn.className = 'pg-btn pg-btn-copy';
    this._copyBtn.textContent = 'Copy';
    this._copyBtn.addEventListener('click', () => this._handleCopy());
    this._headerEl.appendChild(this._copyBtn);

    // Toggle expand/collapse button (hidden until needed)
    this._toggleBtn = document.createElement('button');
    this._toggleBtn.className = 'pg-btn pg-btn-toggle';
    this._toggleBtn.textContent = 'Expand';
    this._toggleBtn.style.display = 'none';
    this._toggleBtn.addEventListener('click', () => this._handleToggle());
    this._headerEl.appendChild(this._toggleBtn);

    // Code block
    const pre = document.createElement('pre');
    pre.className = 'pg-code pg-code-response';
    this._codeEl = document.createElement('code');
    pre.appendChild(this._codeEl);
    this._container.appendChild(pre);

    this._preEl = pre;
    this._expanded = false;
  }

  /**
   * Display a response.
   * @param {object} opts
   * @param {number} opts.status   - HTTP status code.
   * @param {number} opts.timing   - Simulated latency in ms.
   * @param {object|string} opts.body - Response body (JSON).
   */
  show({ status, timing, body }) {
    this._container.style.display = '';

    // Status badge
    this._statusBadge.textContent = statusLabel(status);
    this._statusBadge.className = `pg-status-badge ${statusClass(status)}`;

    // Timing
    this._timingEl.textContent = `${timing}ms`;

    // Body
    this._rawJson = typeof body === 'string'
      ? body
      : JSON.stringify(body, null, 2);

    this._codeEl.innerHTML = highlightJson(this._rawJson);

    // Collapsible logic
    const lineCount = this._rawJson.split('\n').length;
    if (lineCount > COLLAPSE_THRESHOLD) {
      this._toggleBtn.style.display = '';
      this._collapse();
    } else {
      this._toggleBtn.style.display = 'none';
      this._preEl.style.maxHeight = '';
      this._preEl.classList.remove('pg-collapsed');
    }
  }

  /** Hide the response pane. */
  hide() {
    this._container.style.display = 'none';
  }

  /** Collapse the code block to a fixed height. */
  _collapse() {
    this._expanded = false;
    this._preEl.style.maxHeight = '320px';
    this._preEl.classList.add('pg-collapsed');
    this._toggleBtn.textContent = 'Expand';
  }

  /** Expand the code block to full height. */
  _expand() {
    this._expanded = true;
    this._preEl.style.maxHeight = '';
    this._preEl.classList.remove('pg-collapsed');
    this._toggleBtn.textContent = 'Collapse';
  }

  _handleToggle() {
    if (this._expanded) {
      this._collapse();
    } else {
      this._expand();
    }
  }

  async _handleCopy() {
    const text = this._codeEl.textContent || '';
    try {
      await navigator.clipboard.writeText(text);
      this._flashCopyButton('Copied!');
    } catch {
      this._fallbackCopy(text);
    }
  }

  _flashCopyButton(label) {
    const original = this._copyBtn.textContent;
    this._copyBtn.textContent = label;
    setTimeout(() => { this._copyBtn.textContent = original; }, 1500);
  }

  _fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      this._flashCopyButton('Copied!');
    } catch {
      this._flashCopyButton('Failed');
    }
    document.body.removeChild(ta);
  }
}

export { statusClass, statusLabel };
