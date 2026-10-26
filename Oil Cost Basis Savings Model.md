# Oil Cost-Basis Savings Model — Realized Trim Credit

> **Hypothetical paper-model accounting view only.** This report does not represent verified brokerage executions, an account return, or a recommendation. Costs, commissions, financing, spread, and execution effects are not modeled.

## Method and scope

At the user's direction, realized PnL from each 10U Manual-Automatic target trim is credited against the combined open exposure for that ticker: the original tagged 40U residual plus its separate 10U manual replenishment entry. The entry/exit records remain intact. The credit is a **reclassification of PnL already recognized**, not an additional gain; the model's total PnL must not increase a second time because of the credit.

Because model `1U` is a fixed $10,000 entry-notional tranche, not a fixed number of barrels, the effective price basis is computed using the model-implied exposure quantity: `Q = Σ(entry notional ÷ entry price)`. The derived unadjusted effective basis is `combined open notional ÷ Q`; the cost-credited effective basis is `(combined open notional − realized trim PnL) ÷ Q`. These are blended, PnL-equivalent prices—not logged entry prices or fills. For BRENT the actual open lots are 40U at $111.412 and 10U at $115.792; a simple unit-count average would be $112.288, while the ratio-equivalent blended basis is $112.261289. The distinction occurs because the model's 1U is not a fixed barrel quantity. At any later supplied mark, the credit reclassifies already-realized trim PnL into a lower effective basis while preserving total realized-plus-unrealized PnL. The target-to-rebuy price gap is shown only as a quote difference, not a dollar-savings estimate.

| Core ticker | Original Manual-Automatic entry | 10U target trim | Realized PnL credited | 10U replenishment entry | Open lot combination | Gross open notional | Net cost basis after credit | Derived unadjusted effective basis (not trade price) | Cost-credited basis | Basis reduction per exposure unit | Target-to-rebuy quote gap |
|---|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| BRENT | $111.412 (50U) | 10U at $117.000 on 2026-10-23 | $5,015.62 | 10U at $115.792 on 2026-10-25 | 40U residual + 10U new lot | $500,000.00 | $494,984.38 | $112.261289 | $111.135170 | $1.126119 | $1.208 |
| USOIL (internal ticker OIL) | $99.040 (50U) | 10U at $102.000 on 2026-10-23 | $2,988.69 | 10U at $101.740 on 2026-10-25 | 40U residual + 10U new lot | $500,000.00 | $497,011.31 | $99.568474 | $98.973315 | $0.595159 | $0.260 |

The realized trim credit is $8,004.31 per full two-ticker core book, already included in ordinary realized PnL. The same credit maps to each of THE ONE MODEL's 32 independent core-based portfolios; across all 32 the reclassified amount is $256,137.89, **not additional portfolio PnL**. It applies only to these tagged core lots, not the original 1U ticker lots or the separate daily energy/1U sidecars.

## Portfolio propagation and current cutoff

The CSV maps each ticker's basis credit to all 32 THE ONE MODEL portfolio IDs and their core variants. Each core variant appears 8 times; its position basis is the same for this specific oil cycle because the variant differences do not change these logged long entries or tagged trims. The basis credit is applied once per ticker within each independently funded portfolio; it is not multiplied again on top of the core PnL.

The current EOD model ends on **2026-10-23**. The replenishment entries for BRENT, USOIL (internal ticker OIL) are after that mark cutoff, and there are no post-entry marks with which to update the reported portfolio PnL, deployed-notional ratios, or drawdowns. The new entries are recorded and their effective basis is calculated here; current core and 32-portfolio results remain through the existing cutoff and unchanged. On a future refresh with subsequent marks, total PnL should be computed as either (a) separate-lot realized plus unrealized PnL, or (b) the equivalent cost-credited basis view—not both added together.

Machine-readable portfolio mapping: [`oil_cost_basis_savings_v1.csv`](data/oil_cost_basis_savings_v1.csv) (64 ticker/portfolio rows). See [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md) and [`Hypothetical Securities Offering Briefing.md`](Hypothetical%20Securities%20Offering%20Briefing.md) for the current mark window and total-PnL scope.
