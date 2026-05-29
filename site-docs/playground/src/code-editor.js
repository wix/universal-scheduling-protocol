/**
 * code-editor.js — Lightweight JSON code display with syntax highlighting.
 *
 * Renders pretty-printed JSON into a <pre><code> element with CSS-class-based
 * syntax colouring.  The element is optionally contentEditable so the user can
 * tweak request payloads before hitting "Run Request".
 *
 * Zero external dependencies — highlighting is pure regex token replacement.
 */

const TOKEN_PATTERNS = [
  // Order matters: strings first (they can contain numbers/booleans)
  { regex: /("(?:[^"\\]|\\.)*")(\s*:)/g, cls: 'pg-tok-key',  replace: (_, k, colon) => `<span class="pg-tok-key">${escapeHtml(k)}</span>${colon}` },
  { regex: /("(?:[^"\\]|\\.)*")/g,       cls: 'pg-tok-str',  replace: (_, s) => `<span class="pg-tok-str">${escapeHtml(s)}</span>` },
  { regex: /\b(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b/g, cls: 'pg-tok-num', replace: (_, n) => `<span class="pg-tok-num">${n}</span>` },
  { regex: /\b(true|false)\b/g,          cls: 'pg-tok-bool', replace: (_, b) => `<span class="pg-tok-bool">${b}</span>` },
  { regex: /\b(null)\b/g,                cls: 'pg-tok-null', replace: (_, n) => `<span class="pg-tok-null">${n}</span>` },
];

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Apply regex-based syntax highlighting to a JSON string.
 * Returns an HTML string with <span class="pg-tok-*"> wrappers.
 */
function highlightJson(json) {
  // We process tokens in two passes to avoid double-wrapping.
  // Pass 1: mark key-colon pairs (before generic strings consume them).
  // Pass 2: mark remaining strings, numbers, booleans, null.

  // Use placeholder tokens to avoid nested replacements.
  const placeholders = [];
  function placeholder(html) {
    const idx = placeholders.length;
    placeholders.push(html);
    return `\x00PH${idx}\x00`;
  }

  let out = json;

  // Pass 1 — keys (string followed by colon)
  out = out.replace(/("(?:[^"\\]|\\.)*")(\s*:)/g, (_, k, colon) => {
    return placeholder(`<span class="pg-tok-key">${escapeHtml(k)}</span>`) + colon;
  });

  // Pass 2 — plain strings
  out = out.replace(/("(?:[^"\\]|\\.)*")/g, (_, s) => {
    return placeholder(`<span class="pg-tok-str">${escapeHtml(s)}</span>`);
  });

  // Pass 3 — numbers
  out = out.replace(/\b(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b/g, (_, n) => {
    return placeholder(`<span class="pg-tok-num">${n}</span>`);
  });

  // Pass 4 — booleans
  out = out.replace(/\b(true|false)\b/g, (_, b) => {
    return placeholder(`<span class="pg-tok-bool">${b}</span>`);
  });

  // Pass 5 — null
  out = out.replace(/\b(null)\b/g, (_, n) => {
    return placeholder(`<span class="pg-tok-null">${n}</span>`);
  });

  // Escape any remaining HTML-special characters that are NOT inside placeholders
  out = out.replace(/[^]*?/g, (match) => {
    // Only escape segments between placeholders
    return match;
  });

  // Restore placeholders
  out = out.replace(/\x00PH(\d+)\x00/g, (_, idx) => placeholders[Number(idx)]);

  return out;
}

/**
 * CodeEditor — manages a <pre><code> element for JSON display/editing.
 */
export class CodeEditor {
  /**
   * @param {HTMLElement} codeEl - The <code> element inside a <pre>.
   * @param {object|string} content - JSON object or string to display.
   * @param {object} [opts]
   * @param {boolean} [opts.editable=false] - Make the block contentEditable.
   * @param {number}  [opts.indent=2]       - JSON.stringify indentation.
   */
  constructor(codeEl, content, opts = {}) {
    this._codeEl = codeEl;
    this._indent = opts.indent ?? 2;
    this._editable = opts.editable ?? false;
    this._rawJson = '';

    if (this._editable) {
      codeEl.setAttribute('contenteditable', 'true');
      codeEl.setAttribute('spellcheck', 'false');
      codeEl.classList.add('pg-code-editable');
    }

    this.setContent(content);
  }

  /**
   * Replace the displayed content.
   * @param {object|string} content
   */
  setContent(content) {
    if (content === null || content === undefined) {
      this._rawJson = '';
      this._codeEl.innerHTML = '';
      return;
    }
    this._rawJson = typeof content === 'string'
      ? content
      : JSON.stringify(content, null, this._indent);

    this._codeEl.innerHTML = highlightJson(this._rawJson);
  }

  /**
   * Read the current (potentially edited) content as a parsed object.
   * Returns null if the content is not valid JSON.
   * @returns {object|null}
   */
  getValue() {
    const text = this._codeEl.textContent || '';
    try {
      return JSON.parse(text);
    } catch {
      return null;
    }
  }

  /**
   * Read the raw text content (even if not valid JSON).
   * @returns {string}
   */
  getRawText() {
    return this._codeEl.textContent || '';
  }

  /**
   * Copy the current text content to the clipboard.
   * @returns {Promise<boolean>} true if copy succeeded.
   */
  async copyToClipboard() {
    const text = this._codeEl.textContent || '';
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fallback for older browsers / insecure contexts
      return this._fallbackCopy(text);
    }
  }

  /**
   * Fallback copy using a temporary textarea.
   * @param {string} text
   * @returns {boolean}
   */
  _fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try {
      ok = document.execCommand('copy');
    } catch {
      // ignore
    }
    document.body.removeChild(ta);
    return ok;
  }
}

export { highlightJson, escapeHtml };
