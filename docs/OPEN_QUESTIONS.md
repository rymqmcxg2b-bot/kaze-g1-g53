# Questions I Still Want to Understand

Pausing the project does not mean abandoning its questions. These are things I still do not know and genuinely want to understand. If you know one of these areas, please open an Issue, recommend a resource, or help me state the question more precisely.

## Market Microstructure

1. Without a venue-provided queue-position feed, what bounds on maker fill probability are actually identifiable?
2. How should queue depletion, cancel/reinsert tenure, and adverse selection be combined in a survival or competing-risks model?
3. When public trades are used to create hypothetical maker labels, which assumptions most often make results too optimistic?

## Experiments and Statistics

1. When attempted actions contain many no-trades, no-fills, and right-censored outcomes, how should a lower confidence bound on after-cost EV be constructed?
2. If a policy is recalibrated every two weeks, how can repeated testing be controlled so that chance findings are not relabeled as “positive expectancy”?
3. With few regimes, dependent samples, and non-stationarity, which block-bootstrap or sequential-testing designs are defensible?

## Execution and Distributed State

1. When an account stream conflicts with a REST snapshot, which version and event rules should govern live state while preserving both low latency and auditability?
2. After a signed request times out, how should a no-blind-retry order-reconciliation state machine work?
3. When inventory already exists but account/order freshness is inadequate, how should a system distinguish “do not increase risk” from “continue managing existing risk”?

## RL and ML

1. How can RL be limited to execution decisions while preserving interpretable, reviewed quote-formation and risk logic?
2. Should the action space contain only join/improve/widen/cancel/hold, or should size and inventory skew also be delegated to the model?
3. When fill outcomes are partially observed and counterfactuals are not, which offline-RL evaluation methods avoid pretending to know the reward of an unexecuted action?

## Constrained Resources

1. On a small instance, how should CPU and I/O budgets be divided among market ingestion, account reconciliation, the strategy loop, the audit ledger, and health checks?
2. Which data must remain online, and which can be rotated append-only into cold storage without breaking reproducibility?

I especially value feedback showing that the question itself was wrong. Feedback does not need to defend kaZe; demonstrating that an assumption is false is equally valuable.
