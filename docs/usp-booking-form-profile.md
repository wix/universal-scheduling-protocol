# USP Booking Form Profile

**Version:** 1.0 (for USP 2026-02-21)  
**Status:** Draft

---

## 1. Normative References

This profile normatively references:

- **USP Specification** — [Universal Scheduling Protocol](../specification.md), Sections 3 (Service Catalog), 4 (Availability), 5 (Booking Lifecycle)
- **A2UI Protocol v0.8** — [A2UI Specification](https://a2ui.org/specification/v0.8-a2ui/), [Standard Catalog](https://a2ui.org/specification/v0_8/standard_catalog_definition.json)

---

## 2. Overview

### 2.1 Purpose

The USP Booking Form Profile defines how AI agent platforms derive and render booking form fields when building booking UIs. It specifies:

1. **Field derivation rules** — Which form fields to show based on the service, slot, and business context
2. **A2UI component mapping** — How to express those fields as A2UI components for progressive, platform-agnostic rendering

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
| **Selected slot** | USP §4.1 (Time Slot) | `id`, `start`, `end`, `resources`, `location` |
| **Business profile** | USP §7.2 or §6.2 | `locations[]` for multi-location businesses |

### 3.2 Derivation Rules

| Rule | Condition | Derived Field | Source |
|------|-----------|---------------|--------|
| **D1** | Always | `buyer` | `first_name`, `last_name`, `email`, `phone_number` per USP Buyer schema (§5.2) |
| **D2** | Platform supports "book for someone else" | `recipient` | Same schema as buyer; optional |
| **D3** | `service.type` ∈ `{group, reservation}` OR `pricing.model` = `per_person` | `party_size` | Integer; min/max from slot `capacity` or service policies if present |
| **D4** | For each `r` in `service.resources` where `r.selectable === true` | Resource picker | Options from `r.options`, filtered by `slot.resources` when present (§3.8, §4.1) |
| **D5** | Business has `locations[]` and availability was queried with `location_id` OR slot has `location` | `location` | Usually pre-selected via slot; show only if user must choose among locations |
| **D6** | Always (optional) | `notes` | Free text |

### 3.3 Field Ordering

Recommended order: resource selection (D4) → party_size (D3) → buyer (D1) → recipient (D2) → notes (D6). Location (D5) is typically chosen before the form.

### 3.4 Edge Cases

- **Multiple selectable resources:** One field per resource type (e.g. staff + room).
- **Slot-specific resources:** Use `slot.resources` to restrict options when present.
- **Appointment with `party_size` 1:** Omit party_size field; default to 1.

---

## 4. A2UI Component Mapping

### 4.1 Catalog

The profile targets the **A2UI Standard Catalog v0.8** (`https://a2ui.org/specification/v0_8/standard_catalog_definition.json`). Platforms may extend with custom components.

### 4.2 Field → Component Mapping

| USP-derived Field | A2UI Component | Key Properties | Data Model Path |
|-------------------|----------------|----------------|-----------------|
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

### 4.3 Submit Button

The submit button **MUST** use the `Button` component with:

- **Label:** "Book"
- `action.name`: `"usp_create_booking"`
- `action.context`: data model paths for `/booking/*` so the agent receives the full form state

### 4.4 Data Model Schema

```
/booking/
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
```

---

## 5. Example: Minimal JSONL Stream

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

- **Profile version** is tied to the USP specification version it targets (e.g. "Profile 1.0 for USP 2026-02-21").
- **A2UI catalog** is explicitly referenced (v0.8). Future profile versions may target newer A2UI catalogs.

---

## Appendix A: Mapping to create_booking Request

Form data from the `usp_create_booking` userAction context maps to the USP `POST /bookings` request as follows:

| Form Path | Request Field | Notes |
|-----------|---------------|-------|
| `/booking/buyer/*` | `buyer` | Direct mapping |
| `/booking/recipient/*` | `recipient` | Omit if `recipient_enabled` is false |
| `/booking/party_size` | `party_size` | Default 1 if omitted |
| `/booking/resources/{type}` | `resource_id` | Single resource: use value. Multiple: extend to `resource_ids` or equivalent per USP evolution |
| `/booking/location_id` | (slot already has location) | Usually from slot; include in availability query if needed |
| `/booking/notes` | `notes` | Direct mapping |

The agent **MUST** supply `service_id`, `slot_id`, and `hold_id` from its context (not from the form). The form collects buyer-facing inputs only.
