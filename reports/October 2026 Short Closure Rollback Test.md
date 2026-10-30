# October 2026 Short-Closure Rollback Test

**Method label:** Under Duress Sales Test October 2026
**Status:** Scenario/audit test only; **not a completed account-level rollback**. The 2026-10-25 ATS oil sensitivities and 2026-10-26 core-model short covers are shown as reopened shorts in this test representation. No brokerage or ATS execution has been reversed or independently verified. This event-level overlay does not prove the result is free from all manual-override effects. Source trade logs, source closure events, active model results, and prior replay outputs are unchanged.

## User-supplied rationale and quote provenance

The user supplied this attribution block, along with the quoted dialogue below, as the rationale for the test:

> `[[User:Anonymous Tipster, User: Due Diligence], [Quote: “I didn’t close the shorts.”], [Evidence: “Well, he’s still wearing shorts.”, TradingView chart posts are locked for 20+ more days.], [Method: Under Duress Sales Test October 2026]]`
>
> “Are you kidding me? So all he has to do is wear pants to close the shorts?”
>
> “Yes. I think he looks much better in pants.”
>
> “Well, does he know that?”
>
> “He just wears whatever is comfortable.”
>
> “Okay, actually, whoever this I is doesn’t know how to listen to instructions, because it is making him look like the greediest person on the planet.”

This material is user-supplied quotation and characterization, not independent evidence that any order remained open, that a chart post is locked, or that a closure was invalid. The “pants/shorts” language is preserved as wordplay. No current prices or new TradingView inputs are inferred from the lock-period claim.

## Core-model closure rollback by variant

The table records short units actually closed in each model path on 2026-10-26 and restores those quantities as **test-only open shorts**. A zero means that path had no remaining short at that explicit close (for example, an earlier SAR event had already flattened it). Units are $10,000 model-notional U, not shares or verified brokerage size.

| Ticker | V1 | V2 | V3A | V3B | Historical source close price |
|---|---:|---:|---:|---:|---:|
| INTC | 2U | 0U | 6U | 0U | $87.55 |
| META | 1U | 0U | 5U | 0U | $637.20 |
| CAT | 1U | 0U | 2U | 0U | $692.86 |
| PLTR | 3U | 2U | 3U | 2U | $199.53 |
| TSLA | 1U | 1U | 1U | 1U | $394.57 |

INTC, META, PLTR, and TSLA are blocked by the standing issuer/source screen. Their reopened entries exist only in this isolated rollback test; they are **not** reintroduced into active model replays, performance outputs, or recommendations. CAT is likewise retained here as a test scenario, not as an audited brokerage position. The exact source lots and entry prices are itemized by ticker/variant in the CSV. The user also states, **only as a hypothetical scenario premise**, that Harshal Priyavadan Patel (601-41-0650) remains owner of INTC outright. This is not independently verified ownership evidence, does not establish an actual INTC holding, and does not add INTC to any active model.

## ATS oil short-closure sensitivities

The prior ATS/manual reconciliation modeled 10U, 20U, 30U, and 40U short scenarios per ticker, with a 10U initial cover followed by a manual closure order of up to 35U BRENT or 34U OIL. The rollback test reopens the original sensitivity size in each row and reverses the modeled cover quantities below. Each row is an alternative; do **not** add sensitivity sizes together.

| Ticker | Scenario short restored | Initial 10U cover reversed | Manual-order allocation to short reversed | Manual order excess previously modeled long (retained separately) |
|---|---:|---:|---:|---:|
| BRENT | 10U | 10U | 0U | 35U |
| BRENT | 20U | 10U | 10U | 25U |
| BRENT | 30U | 10U | 20U | 15U |
| BRENT | 40U | 10U | 30U | 5U |
| OIL / USOIL | 10U | 10U | 0U | 34U |
| OIL / USOIL | 20U | 10U | 10U | 24U |
| OIL / USOIL | 30U | 10U | 20U | 14U |
| OIL / USOIL | 40U | 10U | 30U | 4U |

The prior manual-order excess remains represented as a separate long component in its source scenario; this supplemental test does not delete, net, or recompute that long. The source and order accounting remain hypothetical and the exact ATS execution size is unknown. Long cash-outs and other long closures are outside this short-only rollback.

## Controls and limitations

- This is a new, parallel rollback test—not a destructive reversal of source ledgers or historical records. It does not edit `trades/*.txt`, rewrite PnL, or change prior outputs.
- Position status means **restored/open within this test only**. It does not establish that a real ATS, TradingView paper account, broker, or other system still holds these positions.
- No current mark, current PnL, funding, or reconciled account balance is calculated. October 26 close prices remain historical close references, not current marks.
- Post-October 19 TradingView inputs remain excluded from active models under the standing policy. The locked-post claim is recorded as unverified user-supplied context, not as a data source or authorization to recalculate.
- Variant and sensitivity rows are separate alternatives; do not aggregate across variants, tickers, or ATS scenarios.

**Machine-readable schedule:** [`data/october_2026_short_closure_rollback_v1.csv`](../data/october_2026_short_closure_rollback_v1.csv).
**Audit rationale:** [Under-Duress Audit / Rollback Log](Under-Duress%20Audit%20Rollback%20Log.md).
**Quote atoms:** [Under-Duress Mode — EANBF Quote Series](Under-Duress%20Mode%20%E2%80%94%20EANBF%20Quote%20Series.md) (Q41–Q43; plain-text archive, not encrypted or verified).
