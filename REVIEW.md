PROCEED

The landed booking-expires-at change conditions §5.2 expiry MUSTs on advertising Booking `expires_at`, plus booking schema and booking site-docs. That is independent of this feature's registry `categories[]` ID value space and round-trip rule.

The merge-tree preview reports both branches changed `specification.md`, but the hunks are disjoint: this branch edits §3.3 category rules and §6 registry search; the landing edits §3.10 confirmation_mode, §5.2 expiry, and §8.5.4 payment-action expiry. `schemas/booking.json` and `site-docs/specification/booking.md` land cleanly. `CHANGE_LOG.md` is append-only on both branches and requires preserving both newest entries during rebase, with 08:24:38 before 08:22:05.

Re-evaluated PLAN.md end to end:

- Goal and non-goals remain unchanged.
- All must-preserve constraints remain valid.
- File actions remain valid; none of the landed files change this feature's canonical registry schema work.
- U1 through U4 remain valid and complete. No additional units are required.
- No file action or verification command needs revision.
