# Public Example Errata and Corrections

This record preserves three code defects and one documentation contradiction found in the public revision [`7c6f248821ed1d138e1d3090986c9f5d14e7495f`](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/tree/7c6f248821ed1d138e1d3090986c9f5d14e7495f). The baseline links below remain fixed so readers can inspect the original behavior after corrections are published.

**Scope:** These findings apply to the rewritten, no-network educational example in this public repository. They do not establish that the private historical trading runtime had the same defects. The archive's older commits remain available; documenting a correction does not rewrite the historical record or establish execution safety or profitability.

**Status:** Corrected in this edition. Local validation passed all 33 invariant and regression tests, the no-network demonstration, and the public-safety scans before publication. These checks cover the public example, not live trading.

| ID | Finding in the baseline | Corrected rule |
|---|---|---|
| [ERR-001](#err-001--local-intent-was-counted-as-an-exchange-open-order) | An unsent local intent was counted as an exchange open order. | Keep local and unresolved actions separate from confirmed open orders. |
| [ERR-002](#err-002--terminal-orders-could-reopen-and-cumulative-fills-could-decrease) | A newer timestamp could reopen a filled order and erase recorded fills. | Validate status transitions and preserve cumulative fill invariants. |
| [ERR-003](#err-003--future-timestamps-passed-freshness-checks) | A negative data age passed the freshness check. | Require `0 <= age <= max_age` and a nonnegative freshness budget. |
| [DOC-001](#doc-001--every-transition-requires-exchange-evidence) | Documentation said every transition required exchange evidence, including local intent creation. | Use local evidence for local actions and exchange evidence for exchange outcomes. |

## ERR-001 — Local Intent Was Counted as an Exchange Open Order

**Affected baseline:** [`StateSnapshot.open_orders`, lines 97–104](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/src/kaze_archive/live_state.py#L97-L104) and [reconciliation, lines 182–184](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/src/kaze_archive/live_state.py#L182-L184).

**Old behavior:** The example defined open orders as every order whose status was not `FILLED`, `CANCELED`, or `REJECTED`. Consequently, `INTENT`, `SUBMITTED`, and `UNKNOWN` were all treated as open. Creating an intent without sending anything, then comparing it with an empty authoritative open-order set, produced `OPEN_ORDER_SET_MISMATCH` even when the recorded position matched.

The [old reconciliation test](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/tests/test_live_state.py#L70-L84) expected that incorrect mismatch. All five original tests passed despite these defects. That test now uses a genuinely confirmed open order absent from the authoritative set, and separate regression tests cover unsent intents.

**Correct behavior:** A local intent records a proposed action. It neither predicts position nor establishes an exchange order. Reconciliation compares confirmed open orders with the authoritative open-order set. Submission and unknown outcomes remain explicitly unresolved; excluding them from confirmed open orders must not silently turn uncertainty into a clean reconciliation. Pending cancellation also requires care because requesting cancellation does not prove that an accepted order has closed.

The corrected snapshot exposes `pending_new` (`INTENT`, `SUBMITTED`, `ACKNOWLEDGED`), `open_orders` (`RESTING`, `PARTIAL_FILL`, `CANCEL_PENDING`), and `unknown_orders` (`UNKNOWN`). Reconciliation separately reports `PENDING_ORDER_CONFIRMATION` for submitted or acknowledged records and `ORDER_STATE_UNKNOWN` for unknown outcomes. An optional `OrderEvent.intent_id` links a venue `order_id` to its local intent so valid exchange evidence can retire the pending record without assuming the IDs are identical; rebinding and later updates under the retired local alias are rejected. A local `UNKNOWN` outcome can be resolved by explicitly linked venue evidence, but `UNKNOWN` alone cannot establish a new venue identity.

**Regression checks:** An unsent intent leaves the confirmed-open set empty and produces no open-order mismatch against an empty exchange set. An actual confirmed open order does produce a mismatch when absent from that set. Unresolved work remains distinguishable from confirmed order state, and a valid intent-to-order link retires its pending record.

## ERR-002 — Terminal Orders Could Reopen and Cumulative Fills Could Decrease

**Affected baseline:** [`LiveState.ingest_order_event`, lines 131–136](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/src/kaze_archive/live_state.py#L131-L136).

**Old behavior:** An event was accepted whenever its timestamp was not older than the stored event. For the same order, a `FILLED` event with quantity `1` and cumulative filled quantity `1` could be overwritten by a later `RESTING` event with cumulative filled quantity `0`. The example both reopened a completed order and forgot its fills.

**Correct behavior:** A timestamp is only one validity check. A replacement event must respect the permitted status transitions, preserve the identity and terms of the modeled order, and never reduce its cumulative filled quantity. Fill totals must agree with status: `FILLED` requires the complete quantity, `PARTIAL_FILL` requires a positive quantity smaller than the order quantity, and `CANCEL_PENDING` requires some quantity to remain unfilled. Invalid events must leave the stored snapshot unchanged. Terminal orders cannot become open again through an ordinary update.

Identical repeated order events are no-ops. Older events, conflicting events with the same timestamp, and invalid transitions raise `ValueError` without mutation. Side and quantity are fixed for each modeled order ID, and terminal state is immutable.

This is a deliberately limited model. Real exchange corrections, trade busts, order replacement, and out-of-order evidence need explicit semantics; this example does not implement them by permitting arbitrary state replacement.

**Regression checks:** Reject `FILLED → RESTING`, reject cumulative-fill decreases during an otherwise active lifecycle, and verify that rejected updates do not mutate state. Retain valid partial-fill and completion paths and consistent handling of repeated evidence.

## ERR-003 — Future Timestamps Passed Freshness Checks

**Affected baseline:** [`StateSnapshot.account_is_fresh` and `market_is_fresh`, lines 85–95](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/src/kaze_archive/live_state.py#L85-L95).

**Old behavior:** Freshness tested only `snapshot_time - update_time <= max_age`. For a snapshot at time `100`, an account update or market receipt at time `110` had age `-10`, so it passed a nonnegative freshness budget.

**Correct behavior:** Fresh data must exist and satisfy both age bounds:

```text
0 <= snapshot_time - update_time <= max_age
max_age >= 0
```

An update from the future is invalid for that snapshot. A negative freshness budget raises `ValueError`. Age zero and age exactly equal to the maximum are valid boundaries; older data is stale. Market freshness in this example uses receipt time, while account freshness uses its recorded update time. The clock values must be comparable; these checks alone do not validate event-time provenance or sequence completeness, or solve clock synchronization.

**Regression checks:** Reject future account and market timestamps as fresh; check zero age, the inclusive maximum-age boundary, stale and missing state, and negative budgets.

## DOC-001 — Every Transition Requires Exchange Evidence

**Affected baseline:** [Architecture, lines 70–87](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/docs/ARCHITECTURE.md#L70-L87). The contradicting local operation was [`record_intent`, lines 138–158](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/src/kaze_archive/live_state.py#L138-L158).

**Old wording:** “Every transition requires exchange evidence.” Applied literally, this would require an exchange event to establish that the local strategy created an intent. It also obscured the distinction between requesting cancellation and confirming it.

**Correct wording:** Evidence must match the fact. Local strategy and transport records establish intent creation, submission, and cancellation requests. Exchange acknowledgments, order/fill events, or authoritative reconciliation establish acceptance, resting status, execution, cancellation, and exchange rejection. A timeout establishes uncertainty rather than rejection or successful cancellation.

The [corrected architecture](ARCHITECTURE.md#order-state-is-not-boolean) also shows rejection as a possible submission result and makes `UNKNOWN` a state of unresolved knowledge requiring reconciliation. Cancel rejection does not mean the original order was rejected; fills may race with cancellation. These are conceptual distinctions, not a claim that the educational module implements every exchange path.

**Related evidence clarification:** The earlier architecture's [quote/cancel illustration, lines 41–58](https://github.com/rymqmcxg2b-bot/kaze-g1-g53/blob/7c6f248821ed1d138e1d3090986c9f5d14e7495f/docs/ARCHITECTURE.md#L41-L58) described split state too categorically as the underlying cause. It now identifies that sequence as a possible mechanism. Proving the cause of a historical incident would require correlated decision, account, order, and risk evidence.

The [historical quote equations](THEORETICAL_FOUNDATIONS.md#3-selected-equations-from-one-reviewed-historical-quote-configuration) also now define `inventory_ratio` and the reviewed normal/watch multipliers explicitly. This completes variable definitions without changing the historical parameter values or presenting them as validated trading parameters.

## Verification and Remaining Boundaries

The correction targets are [the educational implementation](../src/kaze_archive/live_state.py), [the errata regression tests](../tests/test_errata.py), [the original invariant tests](../tests/test_live_state.py), and [the architecture description](ARCHITECTURE.md). Run the checks from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m kaze_archive.demo
python scripts/public_safety_scan.py
```

The example assumes a single-threaded caller. Copying currently stored fields into one snapshot does not make independently received streams transactionally coherent. Passing these checks verifies selected behavior of the public example. It does not verify the private historical runtime, real exchange reconciliation, order placement, a complete event journal, or positive after-cost expectancy.
