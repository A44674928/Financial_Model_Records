# Under-Duress Audit / Rollback Log

**Scope:** Scenario-only audit notes for the versioned [Under-Duress Oil Sale Void Replay](Under-Duress%20Oil%20Sale%20Void%20Replay.md). This log preserves user-supplied reasons and scope distinctions; it is not an ATS audit export, brokerage statement, legal finding, or assertion that an external system actually reversed an order.

## 2026-10-29 — public-portfolio ATS manual-review rationale

**User-reported standing instruction:** “buy a few more barrels every couple dollars”.

The user reports that, for the **public portfolio**, the ATS flagged sell orders for manual review because of this standing buy/add instruction. The user says the required risk-management protocols were not satisfied and directs that the affected sell orders be undone in the public-portfolio replay. The replay records that direction for the listed scenario events; the exact ATS order-to-book mapping has not been supplied, and the original source events remain preserved.

**Evidence boundary:** No ATS alert, review ticket, policy checklist, order IDs, timestamps, or order-to-book mapping for this review was supplied in the repository. The rationale and protocol outcome above are user-reported and have not been independently verified. The replay therefore records a scenario instruction, not an authenticated ATS rejection, broker cancellation, or legal conclusion. Exact public-portfolio events to which this rationale maps should be reconciled against the ATS audit trail if it becomes available.

## Portfolio boundary: public versus private

The user distinguishes the **public portfolio** from the **private portfolio**. The public-portfolio manual-review rationale must not be generalized to the private portfolio. The user says the private portfolio is managed entirely by ATS, with no human interaction beyond chart posting. The user also notes that personalized ATS configurations can generate different sell/buy requests, including ATS sales not logged in these books; those unrecorded or differently personalized decisions are outside this replay unless separately sourced and mapped.

The October 29 rows labeled “Private fund / TradingView Paper Trading” remain included in the earlier replay because of the prior broad user selection of oil closes. Their inclusion is a separate what-if treatment; this public-portfolio manual-review note is **not** evidence that the public review protocol applied to those rows, nor does it reconstruct private ATS activity that is absent from the repository.

## 2026-10-29 — short nullification follow-up

Per the user's later instruction, the modeled ATS short-opening and related cover/closure lifecycle in the 10U/20U/30U/40U sensitivities is nullified. The current replay has no restored open short positions. The original sensitivity and historical entries remain in the event register for auditability.

## Related hypothetical funding

The LCID $4.2B buyout consideration is carried only as an unallocated hypothetical restoration-funding pool in the replay: $2.2B cash plus $2.0B non-cash share/equity value. No actual transaction, receipt, or deployment is asserted.
