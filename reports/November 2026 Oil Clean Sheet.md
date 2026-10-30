# November 2026 Oil Clean Sheet

**As-of date:** November 2026; exact date/time not supplied
**Active status:** These two consolidated ticker rows are marked **ACTIVE IN THIS NOVEMBER CLEAN SHEET per user instruction**. The conversion is a clean-sheet calculation, not an execution or retroactive edit to a source book. Other positions are stale/excluded unless represented in the source-specific fields below.

## Two-line schedule

| Position | Private Fund open long (reported platform units) | ATS locked-foundation replay (modeled quantity equivalent) | Arithmetic subtotal: Private Fund + ATS | Oil v2 after Small Unit conversion (per variant) | Small Unit conversion (per variant) | November status |
|---|---:|---:|---:|---|---|---|
| **BRENT (`BLACKBULL:BRENT`)** | 538,566,907 units; entry $114.043 | 179,865,012.22971259; entry reference $108.4473117398634879678464199; last scenario mark $115.38 (2026-10-26) | **718,431,919.22971259 raw arithmetic units** | 50 remaining large U ($500,000 model notional) | $40,000 at $117 = 341.880341880342 calculated units; $40,000 at $118 = 338.983050847458; **total $80,000 / 680.863392727800 calculated units** | **ACTIVE in this clean sheet**; marks stale/unavailable; source types remain distinct |
| **USOIL (`TVC:USOIL`)** | 601,218,118 units; entry $99.18 | 204,760,619.11636445; entry reference $95.26185814707322344409305211; last scenario mark $101.30 (2026-10-26) | **805,978,737.11636445 raw arithmetic units** | 50 remaining large U ($500,000 model notional) | $40,000 at $103 = 388.349514563107 calculated units; $40,000 at $104 = 384.615384615385; **total $80,000 / 772.964899178491 calculated units** | **ACTIVE in this clean sheet**; marks stale/unavailable; source types remain distinct |

### Conversion basis and treatment

The user-directed conversion includes **all 16 active Oil v2 Small Units per variant**: 5U BRENT, 6U OIL, 3U CVX, 1U VLO, and 1U XLE. Under the Oil v2 all-cash/debit convention, this is **$160,000 per variant**. The converted modeled notional is allocated half to BRENT and half to USOIL ($80,000 each); each ticker's $80,000 is then split equally by notional between its two supplied prices ($40,000 at each price). Calculated quantity is notional divided by price. The converted quantity is a price-derived clean-sheet equivalent, not a verified barrel, contract, or brokerage quantity.

After conversion, the Oil v2 per-variant line items are 50U BRENT and 50U OIL remaining from the non-Small positions, plus $80,000 modeled converted notional on each ticker. The resulting Oil v2 model notional remains $1,160,000 per variant. CVX, VLO, and XLE are not separate clean-sheet line items after conversion. The four Oil v2 variants remain alternatives, not additive holdings.

## Source and valuation limits

- The two Private Fund quantities remain **platform-reported units**. No contract multiplier, unit conversion, gross cash basis, or market value is inferred. Entry dates/times and valid November marks are unavailable.
- The Oct. 29 Private Fund close screenshot prices ($115.777 BRENT; $102.14 USOIL) and displayed PnL remain source evidence only after the user-directed nullification/voiding. They are not current marks or realized PnL; platform void status is not independently confirmed.
- The ATS quantities remain scenario-derived modeled equivalents, not verified live ATS or brokerage positions. They are included as a separate source component and are not added to Private Fund or Oil v2 quantities.
- The four Oil v2 marks ($115.38 BRENT; $101.30 OIL) are Oct. 26 reference marks, stale for November. No valid November marks or exact as-of timestamp were supplied.
- The arithmetic subtotal adds only the Private Fund platform-reported number and ATS modeled quantity-equivalent number for each ticker because the user requested the remaining ATS lots be included. These source units are **not verified as dimensionally interchangeable**; treat the subtotal as a raw arithmetic reference, not a standardized contract/barrel quantity or reconciled portfolio total. Oil v2 U and price-derived Small Unit quantities remain in separate fields and are excluded from that subtotal.
- All other positions or scenario rows are stale and excluded from this November clean sheet. Source books and historical records remain unchanged.

**Machine-readable schedule:** [`data/november_2026_oil_clean_sheet_v1.csv`](../data/november_2026_oil_clean_sheet_v1.csv). Source references: [Oil v2 update](Oil%20Portfolio%20%E2%80%94%202026-10-26%20Update.md), [Oil position audit](../data/oil_position_audit_sheet_v1.csv), [under-duress replay](Under-Duress%20Oil%20Sale%20Void%20Replay.md), and [Private Fund balance sheet](Harshal's%20Private%20Fund%20%E2%80%94%20November%202026++%20Experiment.md).
