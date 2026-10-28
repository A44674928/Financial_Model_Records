# ALIUSD User-Directed LONG Position

> **User-directed paper scenario, not a verified brokerage position.** The user specified a LONG at **$2,999.99** and selected the attached paper-trading export's **15,546,506 quantity** as authoritative. This supersedes the earlier $20B notional sizing for this same position. The exported `50x` leverage and margin are bookkeeping fields only; **no leverage, borrowing, or financing is modeled**.

| Field | Recorded value |
|---|---:|
| Instrument | `CAPITALCOM:ALUMINUM` / ALIUSD |
| Direction | LONG — explicitly specified by the user |
| Exported platform quantity | 15,546,506 |
| Corrected modeled entry price | $2,999.99 — user-corrected; replaces CSV avg. fill of $3,008.70 |
| Recomputed all-cash entry gross notional | **$46,639,362,534.94** |
| CSV last-price snapshot | $3,070.60 |
| Snapshot market value | $47,737,101,323.60 |
| Conditional snapshot price-only change | **+$1,097,738,788.66 (+2.353675%)** |
| CSV leverage / margin fields | 50x / $954,742,026.47 — bookkeeping metadata only; not applied |
| Position/order date and time | Not supplied |
| Execution status | User-directed paper scenario; no verified fill |
| Take profit / stop loss / expiration | Not supplied in export |

The position size is taken from the user-supplied export, not recomputed from the former $20B notional. Under the repo's all-cash convention, the modeled gross debit is the full **$46,639,362,534.94** entry notional; the CSV margin figure is **not** the funded-capital basis. Funding and brokerage execution are not independently verified.

The export itself lists average fill **$3,008.70**, trade value **$46,774,772,602.20**, and unrealized PnL **$962,328,721.40**; those source fields are retained in the machine-readable record but are not used as the corrected entry basis or corrected PnL. The conditional snapshot figures above instead use the user's corrected $2,999.99 entry and the export's $3,070.60 last price. They are price-only arithmetic, not verified account PnL.

## Source timing and mark boundary

The attached CSV filename carries an export timestamp of **2026-10-28T17:41:25.410Z**. It has no position-entry date/time; the export timestamp is provenance only. The accompanying TradingView screenshot identifies **Aluminum (ALIUSD), 1D, Capital.com**, created **2026-10-28 10:20 UTC−7**, and displays **$3,066.10**. That earlier chart value is preserved as source context and is not used for the conditional calculation above. Neither timestamp is treated as a trade time.

The CSV quantity is preserved as reported, but the instrument's contract multiplier/quantity convention was not supplied. Accordingly, the raw platform quantity is not re-described as shares, contracts, or metric tons.

![User-supplied ALIUSD TradingView chart](../Archive/ALIUSD_LONG_2026-10-28/ALUMINUM_2026-10-28_10-20-33.png)

Source files and hashes are recorded in [`Archive/ALIUSD_LONG_2026-10-28/`](../Archive/ALIUSD_LONG_2026-10-28/). This ALIUSD scenario remains separate from the historical 31-symbol core replay and existing oil/pool allocations; no funding source or combined account total is inferred.

Machine-readable record: [`data/aliusd_user_directed_position_v1.csv`](../data/aliusd_user_directed_position_v1.csv).
