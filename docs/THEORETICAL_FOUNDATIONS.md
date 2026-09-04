# Theoretical Foundations and Research Classification

## Formal Descriptive Research Title

**kaZe G1–G53: An Exploratory Systems Study of Inventory-Aware Maker Quoting, Execution-State Reconciliation, and After-Cost Evaluation in a BTC Perpetual Limit-Order Book**

The shortest accurate classification is:

> **Inventory-aware, signal-conditioned limit-order-book market making with event-driven feedback control.**

This is a classification of the problem kaZe attempted to study. It is not a claim of optimality, positive expectancy, production readiness, or faithful implementation of any single canonical model.

## 1. Inventory-Based Market Making

The economic core of kaZe was passive liquidity provision: post maker quotes, seek compensation through the spread, and change quote prices or sizes as inventory and market conditions change.

That places the project in the broad intellectual lineage of:

- Ho–Stoll dealer inventory models, which balance spread capture against inventory risk;
- Avellaneda–Stoikov market making, which expresses inventory pressure through a reservation price and quote offsets under stochastic-control assumptions; and
- later inventory-constrained formulations associated with Guéant and related work.

kaZe used the vocabulary and engineering shape of this family—reservation price, inventory skew, dynamic spread, and side-specific sizing—but it was not a canonical implementation. It did not solve a Hamilton–Jacobi–Bellman equation, estimate the canonical Poisson arrival model, or establish that its policy was optimal.

## 2. Limit-Order-Book Microstructure and Adverse Selection

The maker policy combined several short-horizon market features:

- microprice deviation;
- bid/ask depth imbalance;
- signed trade-flow imbalance;
- top-of-book spread;
- realized volatility; and
- regime and adverse-selection controls.

This connects the project to limit-order-book microstructure, order-flow-imbalance research, and the Glosten–Milgrom view that a market maker must be compensated for trading against better-informed flow. In kaZe, strong directional pressure could widen, shrink, or suppress the exposed side of a quote. That was an engineering guard, not a calibrated structural estimate of informed trading.

## 3. Selected Equations from One Reviewed Historical Quote Configuration

One reviewed historical configuration normalized and clipped the three signal inputs before combining them:

```text
z_micro = clip(microprice_deviation_bps / 2.0, -5, 5)
z_depth = clip(depth_imbalance / 0.25, -5, 5)
z_trade = clip(trade_flow_imbalance / 0.25, -5, 5)

signal_score =
    0.45 * z_micro
  + 0.40 * z_depth
  + 0.15 * z_trade
```

The quote center then combined the signal with an inventory penalty:

```text
signal_shift_bps = 1.5 * signal_score
inventory_shift_bps = -8.0 * inventory_ratio * regime_inventory_multiplier
reservation_shift_bps = signal_shift_bps + inventory_shift_bps
reservation_price = mid * (1 + reservation_shift_bps / 10,000)
```

Its half-spread used a floor plus regime, volatility, and signal-uncertainty terms:

```text
base_half_spread_bps = max(4.0, 3.0, top_of_book_spread_bps / 2)

half_spread_bps = clip(
    base_half_spread_bps * regime_spread_multiplier
    + 0.25 * realized_vol_bps
    + 0.75 * abs(signal_score),
    4.0,
    50.0,
)
```

These are selected core pricing equations rather than the complete policy. Side suppression and sizing, price rounding, touch rules, notional caps, and risk gates also affected the resulting action. The equations document one historical rule-based configuration; they are not recommended parameters, do not describe every G1–G53 generation or deployment, and did not establish a profitable edge.

## 4. Feedback Control Under Partial Observability

The intended decision structure can be written as:

```text
S(t) = market state + account state + order state + execution state + provenance
A(t) = policy(S(t))
```

The action is only an intent. Exchange ACK, fill, cancel, reject, and reconciliation evidence feed back into the next state. This is naturally viewed as a constrained stochastic feedback-control problem.

Real trading state is partially observed: messages can be delayed, dropped, reordered, or contradicted by a later snapshot. That makes partial observability a useful analytical lens. kaZe did not, however, formulate a belief state or solve a partially observable Markov decision process.

## 5. Execution as a Distributed State Machine

Execution was not treated as a boolean `order sent` event. The intended lifecycle distinguished states such as:

```text
INTENT → SUBMITTED
             ├─→ REJECTED
             ├─→ UNKNOWN → RECONCILE
             └─→ ACKNOWLEDGED → RESTING
                                      ├─→ PARTIAL_FILL → FILLED
                                      └─→ CANCEL_PENDING → CANCELED
```

This part of the project belongs as much to distributed systems as to quantitative finance: event-driven architecture, state machines, provenance, freshness, idempotency, append-only evidence, and reconciliation all change the realized economics of a maker strategy.

## 6. After-Cost Evaluation and Experimental Design

kaZe eventually treated a credible strategy result as a complete causal chain:

```text
decision → attempted action → ACK/no-ACK → fill/no-fill → inventory
         → exit/funding/fees/slippage → after-cost outcome
```

Public trades, service uptime, decision counts, or an account-level equity change cannot substitute for that chain. No-trades, no-fills, partial fills, right-censored observations, capital time, manual trading, and policy changes all matter to inference.

## 7. Relationship to ML and Reinforcement Learning

ML and reinforcement learning were considered as possible future execution layers with a deliberately bounded action space, such as join, improve, widen, hold, cancel, or reprice. The interpretable quote-formation and risk logic was intended to remain outside that learned layer.

G53 did not select, train, or validate an RL or ML policy for live trading. It is therefore inaccurate to describe kaZe as an RL trading system. G51 was also a distinct low-latency taker experiment; it was not the theoretical core of the G53 maker design.

## What This Name Does and Does Not Mean

The formal title accurately names the subjects preserved in the archive:

- inventory-aware maker quoting;
- order-book signals and adverse selection;
- execution-state reconciliation;
- after-cost empirical evaluation; and
- constrained real-time systems engineering.

It does not imply canonical Avellaneda–Stoikov implementation, high-frequency-trading capability, a valid fill model, a trained RL policy, or positive expected returns. Those boundaries are part of the research result.

## Primary Literature Behind the Classification

These works identify the intellectual lineages named above; citing them does not imply that kaZe reproduced or validated their models.

- Thomas Ho and Hans R. Stoll, ["Optimal Dealer Pricing Under Transactions and Return Uncertainty"](https://doi.org/10.1016/0304-405X(81)90020-9), *Journal of Financial Economics* 9(1), 1981.
- Marco Avellaneda and Sasha Stoikov, ["High-frequency Trading in a Limit Order Book"](https://doi.org/10.1080/14697680701381228), *Quantitative Finance* 8(3), 2008.
- Olivier Guéant, Charles-Albert Lehalle, and Joaquin Fernandez-Tapia, ["Dealing with the Inventory Risk: A Solution to the Market Making Problem"](https://arxiv.org/abs/1105.3115), 2011.
- Lawrence R. Glosten and Paul R. Milgrom, ["Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders"](https://doi.org/10.1016/0304-405X(85)90044-3), *Journal of Financial Economics* 14(1), 1985.
- Rama Cont, Arseniy Kukanov, and Sasha Stoikov, ["The Price Impact of Order Book Events"](https://doi.org/10.1093/jjfinec/nbt003), *Journal of Financial Econometrics* 12(1), 2014.
