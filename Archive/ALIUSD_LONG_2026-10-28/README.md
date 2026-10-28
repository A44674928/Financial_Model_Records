# ALIUSD LONG source artifacts

## TradingView chart screenshot

- **User-supplied file:** `ALUMINUM_2026-10-28_10-20-33.png`
- **Chart label:** Aluminum (ALIUSD), 1D, Capital.com, TradingView
- **Chart creation timestamp shown:** 2026-10-28 10:20 UTC−7; this is not the position/order timestamp
- **Displayed price:** $3,066.10; retained as earlier chart context, not used for the position export snapshot calculation
- **SHA-256:** `90ac1a6855268b81291e00c2706c9a246eaa955e2829ed04fa557e470d414526`

## Paper-trading positions export

- **User-supplied file:** `paper-trading-positions-2026-10-28T17_41_25.410Z.csv`
- **Export timestamp in filename:** `2026-10-28T17:41:25.410Z`; provenance only, not the position entry/order timestamp
- **Recorded position specifics:** `CAPITALCOM:ALUMINUM`, Long, quantity 15,546,506, CSV average fill $3,008.70, last-price snapshot $3,070.60
- **User correction:** use $2,999.99 as the modeled entry price. The corrected entry notional and conditional snapshot PnL are recomputed in the position report/ledger.
- **Leverage and margin:** CSV lists 50x and $954,742,026.47; the user clarified leverage is not used and these are bookkeeping mechanics only.
- **SHA-256:** `eb6b800911916d4e989231ef6cc39dd6a3681e50be9c7b2068c2dabae9e67576`

Neither source artifact verifies a brokerage order or fill. See [`reports/ALIUSD User-Directed LONG Position.md`](../../reports/ALIUSD%20User-Directed%20LONG%20Position.md).
