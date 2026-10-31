# USP Booking Form Profile

**Version:** 1.2 (for USP 2026-08-20)
**Status:** Draft

---

## 1. Normative References

This profile normatively references:

- **USP Specification**: [Universal Scheduling Protocol](../specification.md), Sections 3 (Service Catalog), 4 (Availability), 5 (Booking Lifecycle), and 11.4 (Booking Questions Extension) when that extension is negotiated
- **A2UI Protocol v0.8** — [A2UI Specification](https://a2ui.org/specification/v0.8-a2ui/), [Standard Catalog](https://a2ui.org/specification/v0_8/standard_catalog_definition.json)

---

## 2. Overview

### 2.1 Purpose

The USP Booking Form Profile defines how AI agent platforms derive and render booking form fields when building booking UIs. It specifies:

1. **Field derivation rules** — Which form fields to show based on the service, slot, and business context
2. **A2UI component mapping** — How to express those fields as A2UI components for progressive, platform-agnostic rendering
3. **Unified form support** — Slot selection as part of the form (pre-fetched or date-first flow)

### 2.2 Relationship to USP

This profile is a **separate spec** that references USP schemas normatively. It does not modify USP; it defines a recommended UI layer for platforms that implement USP.

### 2.3 Audience

AI agent platforms (A2A/MCP) that orchestrate booking flows and need to render a booking form in their own UI (e.g., chat, embedded widget).

---

## 3. Field Derivation Rules

### 3.1 Inputs

The form is derived from:

| Input | Source | Description |
|-------|--------|-------------|
| **Service object** | USP §3 (Service Catalog) | `type`, `resources`, `pricing`, `channel`, etc. |
| **Selected slot** | USP §4.1 (Time Slot) | `id`, `start`, `end`, `resources`, `location` — **optional** when slot selection is in the form |
| **Slots** | USP §4 (availability response) | Array of time slots — **optional**; present when pre-fetched |
| **Flow mode** | Platform/agent | `pre_fetched` or `date_first` — determines whether to show slot picker or date picker first |
| **Business profile** | USP §7.2 or §6.2 | `locations[]` for multi-location businesses |

### 3.2 Derivation Rules

| Rule | Condition | Derived Field | Source |
|------|-----------|---------------|--------|
| **D0a** | `flow_mode` = `pre_fetched` AND `slots[]` is non-empty | Slot picker | Options from `slots[]`; each option: `value` = `slot.id`, `label` = formatted `slot.start`; `maxAllowedSelections: 1` |
| **D0b** | `flow_mode` = `date_first` AND no date selected yet | Date picker | Single date; triggers `usp_select_date` on selection |
| **D0c** | `flow_mode` = `date_first` AND date selected AND `slots[]` from subsequent query is non-empty | Slot picker | Same as D0a |
| **D1** | Always | `buyer` | `first_name`, `last_name`, `email`, `phone_number` per USP Buyer schema (§5.2) |
| **D2** | Platform supports "book for someone else" | `recipient` | Same schema as buyer; optional |
| **D3** | `service.type` ∈ `{group, reservation}` OR `pricing.model` = `per_person` | `party_size` | Integer; min/max from slot `capacity` or service policies if present |
| **D4** | For each `r` in `service.resources` where `r.selectable === true` | Resource picker | Options from `r.options`, filtered by `slot.resources` when present (§3.8, §4.1) |
| **D5** | Business has `locations[]` and availability was queried with `location_id` OR slot has `location` | `location` | Usually pre-selected via slot; show only if user must choose among locations |
| **D6** | Always (optional) | `notes` | Free text |

#### 3.2.1 When Slot Not Yet Selected

When slot selection is in the form and no slot is selected yet:

| Rule | No slot selected | Slot selected |
|------|------------------|---------------|
| **D3** (party_size) | Use `service.capacity` or `service.policies` for min/max; omit if service is `appointment` and default is 1 | Use `slot.capacity` or service policies |
| **D4** (resource picker) | Options from `service.resources` (all options) | Options filtered by `slot.resources` when present |
| **D5** (location) | Show if business has `locations[]` and user must choose | Usually pre-selected from `slot.location`; show only if user still needs to choose |

### 3.3 Field Ordering

Recommended order: **slot/date selection (D0)** → resource selection (D4) → party_size (D3) → buyer (D1) → recipient (D2) → notes (D6). Location (D5) is typically chosen before the form.

With booking questions, the preflight form (Q0) comes before D0, and the `before_confirmation` groups (Q1) follow recipient (D2) in set order. A recap of every non-sensitive answer precedes the submit button.

### 3.4 Edge Cases

- **Multiple selectable resources:** One field per resource type (e.g. staff + room).
- **Slot-specific resources:** Use `slot.resources` to restrict options when present.
- **Appointment with `party_size` 1:** Omit party_size field; default to 1.

### 3.5 Booking Questions

These rules apply only when the booking questions extension (USP §11.4) is negotiated and the service publishes `booking_question_sets[]` or `required_buyer_fields[]`. They never relax a USP requirement; where this profile and §11.4 differ, §11.4 governs.

| Rule | Condition | Derived Field | Source |
|------|-----------|---------------|--------|
| **Q0** | A set with `completion_timing: preflight` applies | Preflight form, shown **before** D0 | Items of every applicable `eligibility` and `configuration` set. Submit with `usp_booking_questions_check_eligibility`; render slots only after the business returns `eligible`, and pass the returned token on the availability query and on create. |
| **Q1** | A set with `completion_timing: before_confirmation` applies | One field group per set | Items in set order and item order. A `section` item becomes a titled group; a `notice` item becomes read-only text. |
| **Q2** | Item is a `question` with `collection` `in_band` or `platform_surface` | One field per question | Component chosen by answer type (§4.2); `label.plain` and option `title` quoted exactly. |
| **Q3** | Item is an `external_task`, or a question with `collection: business_surface` | Link to the business surface | Opens the session-specific `continue_url` the business returns; never a file, signature, or drawing control in the form. |
| **Q4** | `required_buyer_fields[]` names a `Buyer` member | D1 field marked required | For example `phone_number`. |
| **Q5** | A question carries `maps_to: notes` | Replaces D6 | The platform does not render the separate `notes` field. |
| **Q6** | A question or section carries `when` | Shown only while the condition holds | Re-evaluate on every change to an earlier answer; clear answers that become inapplicable. |

Questions with `subject: recipient` bind to the recipient when D2 is in use, otherwise to the buyer. `before_service` sets are not part of the booking form; they are completed after confirmation through `booking_question_state[].continue_url` or a later update.

Every applicable required question is required in the form. No acknowledgment control (`{"type": "boolean", "const": true}`) and no marketing-consent control (`consent_purpose: marketing`) is ever preselected, and `default` values are shown as editable suggestions. A question marked `sensitive` uses an obscured or non-echoing input where the catalog offers one, and its value is never repeated in the recap beyond "provided".

---

## 4. A2UI Component Mapping

### 4.1 Catalog

The profile targets the **A2UI Standard Catalog v0.8** (`https://a2ui.org/specification/v0_8/standard_catalog_definition.json`). Platforms may extend with custom components.

### 4.2 Field → Component Mapping

| USP-derived Field | A2UI Component | Key Properties | Data Model Path |
|-------------------|----------------|----------------|-----------------|
| **Slot picker** (D0a, D0c) | `MultipleChoice` | `options` from `slots[]` (value = `slot.id`, label = formatted `slot.start`); `maxAllowedSelections: 1`; `variant: "chips"` or `"dropdown"` | `/booking/slot_id` |
| **Date picker** (D0b) | `DatePicker` or `TextField` | If A2UI catalog has `DatePicker`: use it. Otherwise `TextField` with `textFieldType: "date"` or equivalent | `/booking/selected_date` |
| **buyer.first_name** | `TextField` | `label: "First name"`, `textFieldType: "shortText"` | `/booking/buyer/first_name` |
| **buyer.last_name** | `TextField` | `label: "Last name"`, `textFieldType: "shortText"` | `/booking/buyer/last_name` |
| **buyer.email** | `TextField` | `label: "Email"`, `textFieldType: "shortText"` | `/booking/buyer/email` |
| **buyer.phone_number** | `TextField` | `label: "Phone"`, `textFieldType: "shortText"` | `/booking/buyer/phone_number` |
| **recipient** (optional) | `CheckBox` + `Column` | Checkbox "Book for someone else"; when checked, show recipient fields | `/booking/recipient_enabled` |
| **recipient.first_name** | `TextField` | Same as buyer | `/booking/recipient/first_name` |
| **recipient.last_name** | `TextField` | Same as buyer | `/booking/recipient/last_name` |
| **party_size** | `TextField` or `Slider` | `textFieldType: "number"`; or `Slider` with `minValue`/`maxValue` from slot capacity | `/booking/party_size` |
| **Resource picker** (per selectable resource) | `MultipleChoice` | `options` from `resource.options` (filtered by `slot.resources`); `maxAllowedSelections: 1`; `variant: "chips"` or default | `/booking/resources/{resource_type}` |
| **location** | `MultipleChoice` | `options` from `business.locations`; single selection | `/booking/location_id` |
| **notes** | `TextField` | `label: "Special requests"`, `textFieldType: "longText"` | `/booking/notes` |

**Booking question fields** (§3.5):

| Answer schema | A2UI Component | Key Properties | Data Model Path |
|---------------|----------------|----------------|-----------------|
| Text (`type: string`, no `format`) | `TextField` | `textFieldType: "shortText"`, or `"longText"` when `rendering: textarea` or `maxLength` exceeds 300 | `/booking/questions/{set_id}/{question_id}` |
| `format: email`, `uri`, `phone` | `TextField` | `textFieldType: "shortText"`; the business validates the format | same |
| `format: date`, `time`, `date-time` | `DateTimeInput` | `enableDate` / `enableTime` per format; `TextField` fallback | same |
| Number (`integer`, `number`) | `TextField` or `Slider` | `textFieldType: "number"`; `Slider` only when both `minimum` and `maximum` are present | same |
| Boolean | `MultipleChoice` | Two explicit options (yes, no), nothing selected initially | same |
| Acknowledgment (`const: true`) | `CheckBox` | Unchecked initially; label is the verbatim `label.plain` | same |
| Single choice (`oneOf`) | `MultipleChoice` | `maxAllowedSelections: 1`; option `value` = `const`, `label` = `title` | same |
| Multiple choice (`items.anyOf`) | `MultipleChoice` | `maxAllowedSelections` from `maxItems`; an `exclusive` option clears the others when selected | same |
| `notice` item | `Text` | Full `content`, never truncated | (none) |
| `external_task` item | `Button` | Opens the business `continue_url` | (none) |

Slot label formatting: Use RFC 3339 `slot.start` to produce a human-readable label (e.g. 'Mon, Mar 15, 9:00 AM'). Timezone from availability query or business profile. Profile does not mandate a specific format.

### 4.3 Actions

#### 4.3.1 Date Selection Action

When the user selects a date in the date-first flow:

- **Trigger:** User selects a date in the date picker (or clicks a "Check availability" button bound to the date field)
- **Action name:** `usp_select_date`
- **Action context:** `{ "selected_date": "<path>/booking/selected_date" }` or equivalent so the agent receives the selected date
- **Agent behavior:** Call `POST /availability/query` with `start_date` and `end_date` derived from the selected date, then re-render the form with the slot picker and remaining fields

#### 4.3.2 Submit Button

The submit button **MUST** use the `Button` component with:

- **Label:** "Book"
- `action.name`: `"usp_create_booking"`
- `action.context`: data model paths for `/booking/*` so the agent receives the full form state. When slot selection is in the form, `action.context` includes `/booking/slot_id`.

#### 4.3.3 Preflight Eligibility Action

- **Action name:** `usp_booking_questions_check_eligibility`
- **Action context:** `{ "questions": "<path>/booking/questions" }`
- **Agent behavior:** Call `POST /services/{service_id}/eligibility-checks` with the preflight answers. On `eligible`, keep the assessment token and continue to D0. On `requires_input`, re-render only the indicated sets. On `ineligible`, show the business's message and alternatives and stop; never change an answer to retry.

#### 4.3.4 Buyer-Input Action Rendering

When a booking or checkout response carries a `dev.usp-protocol.services.booking_questions.buyer_input` Action and the platform renders it as a form, the form **MUST** follow the Action contract (USP §11.4.8):

- Render exactly the items named by `config.sets` and `config.item_ids`, at the named revisions, with the business text verbatim. Disclosures stay adjacent to the control they qualify.
- Never preselect an acknowledgment; the submit control stays disabled until the buyer has responded to every required item.
- Submit the buyer's response through Update Booking (or Update Checkout) with `action_id` set to the Action `id`.
- Treat the Action as resolved only when the business's next response says so; closing the surface or a successful transport response resolves nothing.

A platform that cannot meet every part of the contract opens the Action's `continue_url` instead of rendering the form.

### 4.4 Data Model Schema

```
/booking/
  slot_id (string, optional)        # Selected slot; present when D0 slot picker is shown
  selected_date (string, optional) # YYYY-MM-DD; present when D0b date picker is shown
  buyer/
    first_name (string)
    last_name (string)
    email (string)
    phone_number (string)
  recipient_enabled (boolean)
  recipient/
    first_name (string)
    last_name (string)
  party_size (number)
  resources/
    {resource_type}: selected option id (string)
  location_id (string, optional)
  notes (string)
  questions/                        # Booking questions extension only
    {set_id}/
      {question_id}: answer value (string, number, boolean, or array of option ids)
```

---

## 5. Examples

### 5.1 Pre-fetched Slots (Unified Form)

Service with one selectable staff resource (stylist). Slots already fetched. Form includes slot picker + buyer + notes.

```jsonl
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"root","component":{"Column":{"children":{"explicitList":["slot_choice","stylist_choice","buyer_section","notes_field","book_btn"]}}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"slot_choice","component":{"MultipleChoice":{"label":{"literalString":"Time"},"selections":{"path":"/booking/slot_id"},"options":[{"label":{"literalString":"Mon, Mar 15, 9:00 AM"},"value":"slot_20260315_0900"},{"label":{"literalString":"Mon, Mar 15, 10:30 AM"},"value":"slot_20260315_1030"}],"maxAllowedSelections":1}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"stylist_choice","component":{"MultipleChoice":{"label":{"literalString":"Stylist"},"selections":{"path":"/booking/resources/staff"},"options":[{"label":{"literalString":"Jane Smith"},"value":"staff_jane"},{"label":{"literalString":"Alex Johnson"},"value":"staff_alex"}],"maxAllowedSelections":1}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"buyer_section","component":{"Column":{"children":{"explicitList":["first_name","last_name","email","phone"]}}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"first_name","component":{"TextField":{"label":{"literalString":"First name"},"text":{"path":"/booking/buyer/first_name"},"textFieldType":"shortText"}}},{"id":"last_name","component":{"TextField":{"label":{"literalString":"Last name"},"text":{"path":"/booking/buyer/last_name"},"textFieldType":"shortText"}}},{"id":"email","component":{"TextField":{"label":{"literalString":"Email"},"text":{"path":"/booking/buyer/email"},"textFieldType":"shortText"}}},{"id":"phone","component":{"TextField":{"label":{"literalString":"Phone"},"text":{"path":"/booking/buyer/phone_number"},"textFieldType":"shortText"}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"notes_field","component":{"TextField":{"label":{"literalString":"Special requests"},"text":{"path":"/booking/notes"},"textFieldType":"longText"}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"book_btn_text","component":{"Text":{"text":{"literalString":"Book"}}}},{"id":"book_btn","component":{"Button":{"child":"book_btn_text","action":{"name":"usp_create_booking","context":[{"key":"booking","value":{"path":"/booking"}}]}}}}]}}
{"dataModelUpdate":{"surfaceId":"booking_form","contents":[{"key":"booking","valueMap":[{"key":"slot_id","valueString":""},{"key":"buyer","valueMap":[{"key":"first_name","valueString":""},{"key":"last_name","valueString":""},{"key":"email","valueString":""},{"key":"phone_number","valueString":""}]},{"key":"resources","valueMap":[{"key":"staff","valueString":""}]},{"key":"notes","valueString":""}]}]}}
{"beginRendering":{"surfaceId":"booking_form","root":"root"}}
```

### 5.2 Date-First Flow (Phase 1)

Initial form with date picker only; slot picker appears after `usp_select_date`.

```jsonl
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"root","component":{"Column":{"children":{"explicitList":["date_picker","check_btn"]}}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"date_picker","component":{"TextField":{"label":{"literalString":"Date"},"text":{"path":"/booking/selected_date"},"textFieldType":"shortText"}}},{"id":"check_btn_text","component":{"Text":{"text":{"literalString":"Check availability"}}}},{"id":"check_btn","component":{"Button":{"child":"check_btn_text","action":{"name":"usp_select_date","context":[{"key":"selected_date","value":{"path":"/booking/selected_date"}}]}}}}]}}
{"dataModelUpdate":{"surfaceId":"booking_form","contents":[{"key":"booking","valueMap":[{"key":"selected_date","valueString":""}]}]}}
{"beginRendering":{"surfaceId":"booking_form","root":"root"}}
```

*Note: If the A2UI catalog has a `DatePicker` component, use it instead of `TextField`. The "Check availability" button triggers `usp_select_date`; the agent fetches slots and re-renders with the full form (slot picker + buyer + notes + Book).*

### 5.3 Slot Already Selected (Original Flow)

Service with one selectable staff resource (stylist). Slot already selected.

```jsonl
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"root","component":{"Column":{"children":{"explicitList":["stylist_choice","buyer_section","notes_field","book_btn"]}}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"stylist_choice","component":{"MultipleChoice":{"label":{"literalString":"Stylist"},"selections":{"path":"/booking/resources/staff"},"options":[{"label":{"literalString":"Jane Smith"},"value":"staff_jane"},{"label":{"literalString":"Alex Johnson"},"value":"staff_alex"}],"maxAllowedSelections":1}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"buyer_section","component":{"Column":{"children":{"explicitList":["first_name","last_name","email","phone"]}}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"first_name","component":{"TextField":{"label":{"literalString":"First name"},"text":{"path":"/booking/buyer/first_name"},"textFieldType":"shortText"}}},{"id":"last_name","component":{"TextField":{"label":{"literalString":"Last name"},"text":{"path":"/booking/buyer/last_name"},"textFieldType":"shortText"}}},{"id":"email","component":{"TextField":{"label":{"literalString":"Email"},"text":{"path":"/booking/buyer/email"},"textFieldType":"shortText"}}},{"id":"phone","component":{"TextField":{"label":{"literalString":"Phone"},"text":{"path":"/booking/buyer/phone_number"},"textFieldType":"shortText"}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"notes_field","component":{"TextField":{"label":{"literalString":"Special requests"},"text":{"path":"/booking/notes"},"textFieldType":"longText"}}}]}}
{"surfaceUpdate":{"surfaceId":"booking_form","components":[{"id":"book_btn_text","component":{"Text":{"text":{"literalString":"Book"}}}},{"id":"book_btn","component":{"Button":{"child":"book_btn_text","action":{"name":"usp_create_booking","context":[{"key":"booking","value":{"path":"/booking"}}]}}}}]}}
{"dataModelUpdate":{"surfaceId":"booking_form","contents":[{"key":"booking","valueMap":[{"key":"buyer","valueMap":[{"key":"first_name","valueString":""},{"key":"last_name","valueString":""},{"key":"email","valueString":""},{"key":"phone_number","valueString":""}]},{"key":"resources","valueMap":[{"key":"staff","valueString":""}]},{"key":"notes","valueString":""}]}]}}
{"beginRendering":{"surfaceId":"booking_form","root":"root"}}
```

---

## 6. Versioning & USP Compatibility

- **Profile version** is tied to the USP specification version it targets (e.g. "Profile 1.1 for USP 2026-08-20").
- **A2UI catalog** is explicitly referenced (v0.8). Future profile versions may target newer A2UI catalogs.

---

## Appendix A: Mapping to create_booking Request

Form data from the `usp_create_booking` userAction context maps to the USP `POST /bookings` request as follows:

| Form Path | Request Field | Notes |
|-----------|---------------|-------|
| `/booking/slot_id` | `slot_id` | Use when slot selection is in the form. Agent supplies from context when slot was pre-selected. |
| `/booking/buyer/*` | `buyer` | Direct mapping |
| `/booking/recipient/*` | `recipient` | Omit if `recipient_enabled` is false |
| `/booking/party_size` | `party_size` | Default 1 if omitted |
| `/booking/resources/{type}` | `resource_id` | Single resource: use value. Multiple: extend to `resource_ids` or equivalent per USP evolution |
| `/booking/location_id` | (slot already has location) | Usually from slot; include in availability query if needed |
| `/booking/notes` | `notes` | Direct mapping. Omitted when a `maps_to: notes` question is rendered (Q5). |
| `/booking/questions/{set_id}/*` | `booking_question_submissions[]` | One entry per set: `{set_id, revision, answers}` with the set's live `revision`. Only applicable answers are sent. |
| (preflight result) | `booking_question_assessment_token` | Token from the last `eligible` decision, when a preflight set applies. |

The agent **MUST** supply `service_id` and `hold_id` from its context. When slot is pre-selected (current flow), the agent also supplies `slot_id`. When slot selection is in the form, `slot_id` comes from `/booking/slot_id`.
