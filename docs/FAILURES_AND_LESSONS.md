# Failures and Lessons

This is not a verbatim archive of every incident. It distills recurring problems into patterns that may be useful to someone else.

## 1. Mistaking Engineering Progress for Economic Progress

Passing unit tests, reducing latency, completing a deployment, seeing an active service, or even recording real fills cannot by themselves establish positive expectancy. For too long, kaZe treated “more green checks” as if they meant “closer to profitability.” What was missing was a precommitted, complete population of untouched, after-cost outcomes.

What I would do now: define the research question, population, costs, censoring, and promotion rule before writing the execution engine.

## 2. Costs Overwhelming a Short-Horizon Signal

The observed G51 evidence made this especially clear. A hot path can be fast, but if the measured signal is tiny while round-trip fees, spread, slippage, and exit costs are materially larger, latency optimization cannot turn negative economics into positive economics.

What I would do now: compare models only on net EV per attempted action and net EV per unit of capital-time, with the cost contract frozen before training.

## 3. The Temptation to Treat Public Trades as Execution Evidence

Seeing the market trade at a quoted price does not prove that kaZe’s order reached the front of the queue, was still resting, escaped cancellation, or received any of that volume.

What I would do now: allow public trades to update a queue model or a hypothetical label only. An actual fill must come from an account or order event and link back to kaZe’s own order identity.

## 4. Cancel-First Maintenance Creating Zero-Order Gaps

The preserved G20 audit indicates that quotes were repeatedly removed, losing resting tenure, while synchronous networking and reconciliation consumed substantial time. The strategy often produced two-sided candidates, but both sides were simultaneously present in the market for far less time than the decision counts implied.

What I would do now: make time-weighted quote availability, queue tenure, cancel reason, replacement gap, and request budget first-class metrics.

## 5. Multiple “Truths” Making Strategy and Risk Fight Each Other

Market data, account data, orders, and the local ledger updated on different schedules. When position or open-order state lagged in one module, the system could oscillate between quoting and canceling, block valid actions, or leave inventory without resting orders able to manage it.

What I would do now: maintain one authoritative live state. Every snapshot would carry its timestamp, source, sequence, freshness, and reconciliation version.

## 6. Collapsing `sent`, `accepted`, `resting`, and `filled` into One Event

In a distributed system, a timeout produces an unknown outcome, not a proven failure. Blindly retrying a signed write can create a duplicate order; updating local position when an order is merely submitted rather than filled creates state drift.

What I would do now: permit only evidence-backed state transitions. Unknown outcomes go through reconciliation rather than guessing or synthesizing state.

## 7. Recovery Work Growing Without a Bound

Scanning an entire SQLite ledger, loading all history into memory, or performing too many remote queries at startup can stall a small instance, trigger timeouts, or compete with the strategy for request budget.

What I would do now: use checkpoints, reverse or streaming scans, explicit work limits, and an independent health-check budget. Test both long-history and empty-history cases.

## 8. Fail-Closed Behavior Is Not Free

Fail-closed behavior prevented actions when credentials, market freshness, or position state were uncertain. Some stop paths, however, also removed inventory-managing orders. The lesson is not to disable safety. It is that exposure-increasing actions and exposure-managing actions need separate, explicit, and tested policies.

What I would do now: let a risk gate restrict the action set without silently substituting a different trading policy and continuing to claim the original strategy’s evidence.

## 9. Replay Integrity Passing Without Usable Labels

G53 strict replay could verify hashes, references, causal clocks, and a no-write boundary while only a few activations had complete market follow-through and none had linked actual execution outcomes. Data integrity can succeed while the research question remains unanswerable.

What I would do now: track integrity, coverage, identifiability, sample size, and economic labels separately. If any required dimension is missing, return `UNAVAILABLE` explicitly.

## 10. AI-Assisted Development Causing Version and Intent Drift

Fast iteration made it easy for each conversation to add a parameter, gate, release, or “temporary” correction. When models, prompts, and context all change, it becomes difficult to identify which policy was tested and which one is running.

What I would do now:

- Define strategy identity with hashes over code, features, labels, costs, risk limits, residual-position policy, and execution semantics.
- Treat a change to any one of them as a new candidate.
- Separate research status, deployment status, and owner authorization.
- Allow AI to propose and implement changes only within an explicit scope; it must not alter an authorized policy without a separate human decision.

## 11. Manual Trading Breaking Simple Equity-Delta Attribution

An account-value change can simultaneously contain strategy trading, manual trading, funding, fees, transfers, and unrealized PnL. Beginning-to-end equity alone cannot determine how much a particular project iteration made or lost.

What I would do now: attribute performance through a decision/order/fill-level ledger and mark externally introduced positions or manual actions as inherited or external state.

## 12. Knowing When to Pause Is Part of the Research Process

The responsible conclusion at G53 was not “tune one more threshold.” Without trustworthy account/order state, complete outcomes, and stronger foundations, adding code would have added uncertainty. Pausing preserves an honest boundary and leaves open the possibility of returning later with better questions.
