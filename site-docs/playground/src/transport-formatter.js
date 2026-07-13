/**
 * transport-formatter.js — Converts a REST-centric step configuration into
 * the display format for MCP, A2A, or ESP transport bindings.
 *
 * Each formatter returns { display: string, language: string } where `display`
 * is the pretty-printed text to show in the code pane.
 */

// ---------------------------------------------------------------------------
// REST method+path to MCP tool-name mapping
// ---------------------------------------------------------------------------

const MCP_TOOL_MAP = {
  'GET /.well-known/usp':                    'usp_profile_get',
  'GET /.well-known/ucp':                    'ucp_profile_get',
  'POST /services/list':                     'usp_catalog_list',
  'GET /services/{service_id}':              'usp_catalog_get',
  'POST /services/lookup':                   'usp_catalog_lookup',
  'POST /availability/query':                'usp_availability_query',
  'POST /availability/hold':                 'usp_availability_hold',
  'DELETE /availability/holds/{hold_id}':    'usp_availability_release',
  'POST /bookings':                          'usp_booking_create',
  'GET /bookings/{booking_id}':              'usp_booking_get',
  'PATCH /bookings/{booking_id}':            'usp_booking_update',
  'POST /bookings/{booking_id}/cancel':      'usp_booking_cancel',
  'POST /bookings/{booking_id}/reschedule':  'usp_booking_reschedule',
  'POST /bookings/{booking_id}/confirm':     'usp_booking_confirm',
  'POST /bookings/{booking_id}/confirm-payment': 'usp_booking_confirm_payment',
  'POST /waitlist':                          'usp_waitlist_join',
  'POST /waitlist/{entry_id}/accept':        'usp_waitlist_accept',
  'POST /waitlist/{entry_id}/decline':       'usp_waitlist_decline',
  'DELETE /waitlist/{entry_id}':             'usp_waitlist_leave',
  'POST /waitlist/list':                     'usp_waitlist_list',
};

// ---------------------------------------------------------------------------
// REST method+path to A2A operation type mapping
// ---------------------------------------------------------------------------

const A2A_TYPE_MAP = {
  'GET /.well-known/usp':                    'usp.profile.get',
  'GET /.well-known/ucp':                    'ucp.profile.get',
  'POST /services/list':                     'usp.catalog.list',
  'POST /availability/query':                'usp.availability.query',
  'POST /availability/hold':                 'usp.availability.hold',
  'POST /bookings':                          'usp.booking.create',
  'GET /bookings/{booking_id}':              'usp.booking.get',
  'PATCH /bookings/{booking_id}':            'usp.booking.update',
  'POST /bookings/{booking_id}/cancel':      'usp.booking.cancel',
  'POST /bookings/{booking_id}/reschedule':  'usp.booking.reschedule',
  'POST /bookings/{booking_id}/confirm':     'usp.booking.confirm',
  'POST /bookings/{booking_id}/confirm-payment': 'usp.booking.confirm_payment',
  'POST /waitlist':                          'usp.waitlist.join',
  'POST /waitlist/{entry_id}/accept':        'usp.waitlist.accept',
};

// ---------------------------------------------------------------------------
// State-modifying methods that need idempotency keys
// ---------------------------------------------------------------------------

const STATE_MODIFYING_METHODS = new Set([
  'POST', 'PUT', 'PATCH', 'DELETE',
]);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

let _mcpIdCounter = 1;
function nextMcpId() { return _mcpIdCounter++; }

let _a2aTaskCounter = 1;
function nextA2aTaskId() {
  return `task_${String(_a2aTaskCounter++).padStart(3, '0')}`;
}

function randomIdempotencyKey() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let key = 'idk_';
  for (let i = 0; i < 12; i++) {
    key += chars[Math.floor(Math.random() * chars.length)];
  }
  return key;
}

// ---------------------------------------------------------------------------
// Formatters
// ---------------------------------------------------------------------------

/**
 * Format a step request for the REST transport.
 *
 * @param {object} stepConfig - { method, path, headers? }
 * @param {object|null} requestBody
 * @returns {{ display: string, language: string }}
 */
function formatRest(stepConfig, requestBody) {
  const { method, path } = stepConfig;
  const headers = {
    Host: 'api.business.example.com',
    'Content-Type': 'application/json',
    Authorization: 'Bearer {token}',
    ...(STATE_MODIFYING_METHODS.has(method) ? { 'Idempotency-Key': randomIdempotencyKey() } : {}),
    ...(stepConfig.headers || {}),
  };

  let lines = [`${method} ${path} HTTP/1.1`];
  for (const [k, v] of Object.entries(headers)) {
    lines.push(`${k}: ${v}`);
  }

  if (requestBody && method !== 'GET') {
    lines.push('');
    lines.push(JSON.stringify(requestBody, null, 2));
  }

  return { display: lines.join('\n'), language: 'http' };
}

/**
 * Format a step request for the MCP (JSON-RPC 2.0) transport.
 */
function formatMcp(stepConfig, requestBody) {
  const { method, path } = stepConfig;
  const toolKey = `${method} ${path}`;
  const toolName = MCP_TOOL_MAP[toolKey] || `usp_${path.replace(/[/{}-]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '')}`;

  const envelope = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: toolName,
      arguments: requestBody || {},
      _meta: {
        usp: {
          profile: 'https://business.example.com/.well-known/usp',
          ...(STATE_MODIFYING_METHODS.has(method) ? { idempotency_key: randomIdempotencyKey() } : {}),
        },
      },
    },
    id: nextMcpId(),
  };

  return {
    display: JSON.stringify(envelope, null, 2),
    language: 'json',
  };
}

/**
 * Format a step request for the A2A (Agent-to-Agent) transport.
 */
function formatA2a(stepConfig, requestBody) {
  const { method, path } = stepConfig;
  const typeKey = `${method} ${path}`;
  const operationType = A2A_TYPE_MAP[typeKey] || `usp.${path.replace(/[/{}-]/g, '.').replace(/\.+/g, '.').replace(/^\.|\.$/g, '')}`;

  const envelope = {
    jsonrpc: '2.0',
    method: 'tasks/send',
    params: {
      id: nextA2aTaskId(),
      message: {
        role: 'user',
        parts: [
          {
            type: 'data',
            data: {
              type: operationType,
              ...(requestBody || {}),
            },
          },
        ],
      },
    },
  };

  return {
    display: JSON.stringify(envelope, null, 2),
    language: 'json',
  };
}

/**
 * Format a step request for the ESP (Embedded Scheduling Provider) transport.
 * Returns an iframe embed snippet with postMessage protocol description.
 */
function formatEsp(stepConfig, requestBody) {
  const { method, path } = stepConfig;

  const snippet = `<!-- ESP Embedded Widget -->
<iframe
  id="usp-widget"
  src="https://business.example.com/embed/schedule"
  style="width: 100%; height: 600px; border: none;"
  allow="payment"
></iframe>

<script>
  // Listen for scheduling events from the embedded widget
  window.addEventListener('message', (event) => {
    if (event.origin !== 'https://business.example.com') return;

    const { type, data } = event.data;

    switch (type) {
      case 'esp.ready':
        // Widget loaded — send configuration
        document.getElementById('usp-widget').contentWindow.postMessage({
          type: 'esp.configure',
          data: {
            operation: '${method} ${path}',
            locale: 'en-US',
            theme: 'light',
            payload: ${JSON.stringify(requestBody || {}, null, 6).split('\n').join('\n            ')}
          }
        }, 'https://business.example.com');
        break;

      case 'esp.booking.created':
        console.log('Booking created:', data.booking_id);
        break;

      case 'esp.booking.canceled':
        console.log('Booking canceled:', data.booking_id);
        break;

      case 'esp.error':
        console.error('ESP error:', data.code, data.message);
        break;

      case 'esp.cancel':
        console.log('User closed the widget');
        break;
    }
  });
</script>`;

  return { display: snippet, language: 'html' };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Convert a REST step configuration + request body to the specified transport
 * format.
 *
 * @param {object} stepConfig  - { method: string, path: string, headers?: object }
 * @param {object|null} requestBody - The JSON request body (REST-centric).
 * @param {'rest'|'mcp'|'a2a'|'esp'} transport
 * @returns {{ display: string, language: string }}
 */
export function formatForTransport(stepConfig, requestBody, transport) {
  switch (transport) {
    case 'mcp': return formatMcp(stepConfig, requestBody);
    case 'a2a': return formatA2a(stepConfig, requestBody);
    case 'esp': return formatEsp(stepConfig, requestBody);
    case 'rest':
    default:
      return formatRest(stepConfig, requestBody);
  }
}

export { MCP_TOOL_MAP, A2A_TYPE_MAP };
