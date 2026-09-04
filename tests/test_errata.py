"""Regression cases for ERR-001 through ERR-003 in docs/ERRATA.md."""

from dataclasses import FrozenInstanceError
from decimal import Decimal
import unittest

from kaze_archive.live_state import (
    AccountState,
    LiveState,
    MarketState,
    OrderEvent,
    OrderStatus,
    Side,
)


class ErrataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = LiveState()
        self.state.ingest_account(
            AccountState(
                position=Decimal("0"),
                equity=Decimal("1000"),
                available_balance=Decimal("1000"),
                update_time_ns=100,
            )
        )
        self.state.ingest_market(
            MarketState(
                bid=Decimal("99"),
                ask=Decimal("101"),
                event_time_ns=90,
                receive_time_ns=100,
            )
        )

    def event(self, status=OrderStatus.RESTING, **changes) -> OrderEvent:
        values = {
            "order_id": "synthetic-exchange-1",
            "side": Side.BUY,
            "quantity": Decimal("1"),
            "filled_quantity": Decimal("0"),
            "status": status,
            "update_time_ns": 200,
        }
        values.update(changes)
        return OrderEvent(**values)

    def record_intent(self) -> None:
        self.state.record_intent(
            intent_id="synthetic-intent-1",
            side=Side.BUY,
            quantity=Decimal("1"),
            created_time_ns=150,
        )

    def differences(self, open_ids=None) -> tuple[str, ...]:
        return self.state.reconciliation_differences(
            authoritative_position=Decimal("0"),
            authoritative_open_order_ids=set() if open_ids is None else open_ids,
        )

    def assert_rejected_without_mutation(self, event: OrderEvent) -> None:
        before = self.state.snapshot(created_time_ns=500)
        with self.assertRaises(ValueError):
            self.state.ingest_order_event(event)
        self.assertEqual(self.state.snapshot(created_time_ns=500), before)

    def test_err001_unsent_intent_is_pending_without_reconciliation_mismatch(self):
        self.record_intent()
        snapshot = self.state.snapshot(created_time_ns=200)

        self.assertEqual(snapshot.open_orders, ())
        self.assertEqual(
            {order.order_id for order in snapshot.pending_new},
            {"synthetic-intent-1"},
        )
        self.assertEqual(self.differences(), ())
        self.assertEqual(snapshot.account.position, Decimal("0"))

    def test_err001_submission_and_acknowledgment_still_need_open_confirmation(self):
        for status in (OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED):
            with self.subTest(status=status):
                state = LiveState()
                state.ingest_account(self.state.snapshot(created_time_ns=200).account)
                state.ingest_order_event(self.event(status))
                snapshot = state.snapshot(created_time_ns=250)

                self.assertEqual(snapshot.open_orders, ())
                self.assertEqual(len(snapshot.pending_new), 1)
                self.assertEqual(
                    state.reconciliation_differences(
                        authoritative_position=Decimal("0"),
                        authoritative_open_order_ids=set(),
                    ),
                    ("PENDING_ORDER_CONFIRMATION",),
                )

    def test_err001_only_confirmed_open_ids_are_compared(self):
        self.record_intent()
        self.state.ingest_order_event(self.event())

        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())
        self.assertEqual(self.differences(), ("OPEN_ORDER_SET_MISMATCH",))

    def test_err001_unknown_is_explicit_without_becoming_an_open_order(self):
        self.state.ingest_order_event(self.event(OrderStatus.UNKNOWN))
        snapshot = self.state.snapshot(created_time_ns=250)

        self.assertEqual(snapshot.open_orders, ())
        self.assertEqual(snapshot.pending_new, ())
        self.assertEqual(len(snapshot.unknown_orders), 1)
        self.assertEqual(self.differences(), ("ORDER_STATE_UNKNOWN",))

    def test_err001_explicit_exchange_binding_retires_local_intent(self):
        self.record_intent()
        before = self.state.snapshot(created_time_ns=160)
        linked = self.event(intent_id="synthetic-intent-1")
        self.state.ingest_order_event(linked)
        after = self.state.snapshot(created_time_ns=250)

        self.assertEqual(set(before.orders), {"synthetic-intent-1"})
        self.assertEqual(set(after.orders), {"synthetic-exchange-1"})
        self.assertEqual(after.pending_new, ())
        self.assertEqual(after.open_orders, (linked,))
        self.assertEqual(after.account, before.account)
        self.assertEqual(after.version, before.version + 1)
        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())

    def test_err001_invalid_binding_keeps_pending_intent_and_version(self):
        self.record_intent()
        for changes in (
            {"intent_id": "synthetic-missing-intent"},
            {"intent_id": "synthetic-intent-1", "side": Side.SELL},
            {"intent_id": "synthetic-intent-1", "quantity": Decimal("2")},
            {"intent_id": "synthetic-intent-1", "update_time_ns": 149},
        ):
            with self.subTest(changes=changes):
                self.assert_rejected_without_mutation(self.event(**changes))

        self.state.ingest_order_event(self.event(intent_id="synthetic-intent-1"))
        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())

    def test_err001_intent_cannot_be_rebound_to_another_exchange_order(self):
        self.record_intent()
        self.state.ingest_order_event(self.event(intent_id="synthetic-intent-1"))
        self.state.ingest_order_event(
            self.event(
                OrderStatus.FILLED,
                filled_quantity=Decimal("1"),
                update_time_ns=250,
                intent_id="synthetic-intent-1",
            )
        )

        self.assert_rejected_without_mutation(
            self.event(
                order_id="synthetic-exchange-2",
                update_time_ns=300,
                intent_id="synthetic-intent-1",
            )
        )

    def test_err001_binding_survives_followups_without_repeating_intent_id(self):
        self.record_intent()
        self.state.ingest_order_event(
            self.event(OrderStatus.ACKNOWLEDGED, intent_id="synthetic-intent-1")
        )
        self.assertEqual(self.differences(), ("PENDING_ORDER_CONFIRMATION",))

        resting = self.event(update_time_ns=250)
        self.state.ingest_order_event(resting)
        before_retry = self.state.snapshot(created_time_ns=300)
        self.assertEqual(
            before_retry.orders["synthetic-exchange-1"].intent_id,
            "synthetic-intent-1",
        )
        self.assertEqual(before_retry.pending_new, ())
        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())

        self.state.ingest_order_event(resting)
        self.assertEqual(self.state.snapshot(created_time_ns=300), before_retry)
        self.assert_rejected_without_mutation(
            self.event(update_time_ns=350, intent_id="synthetic-other-intent")
        )

    def test_err001_retired_intent_identifier_cannot_be_reused(self):
        self.record_intent()
        self.state.ingest_order_event(self.event(intent_id="synthetic-intent-1"))
        before = self.state.snapshot(created_time_ns=500)

        with self.assertRaises(ValueError):
            self.state.record_intent(
                intent_id="synthetic-intent-1",
                side=Side.BUY,
                quantity=Decimal("1"),
                created_time_ns=300,
            )

        self.assertEqual(self.state.snapshot(created_time_ns=500), before)

    def test_err001_ingest_cannot_resurrect_retired_local_identity(self):
        self.record_intent()
        self.state.ingest_order_event(self.event(intent_id="synthetic-intent-1"))

        for status in (OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED):
            for update_time_ns in (175, 300):
                with self.subTest(status=status, update_time_ns=update_time_ns):
                    self.assert_rejected_without_mutation(
                        self.event(
                            status,
                            order_id="synthetic-intent-1",
                            update_time_ns=update_time_ns,
                        )
                    )

        snapshot = self.state.snapshot(created_time_ns=500)
        self.assertEqual(set(snapshot.orders), {"synthetic-exchange-1"})
        self.assertEqual(snapshot.pending_new, ())
        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())

    def test_err001_unknown_local_submission_can_reconcile_to_venue_identity(self):
        self.record_intent()
        self.state.ingest_order_event(
            self.event(OrderStatus.SUBMITTED, order_id="synthetic-intent-1")
        )
        self.state.ingest_order_event(
            self.event(
                OrderStatus.UNKNOWN,
                order_id="synthetic-intent-1",
                update_time_ns=250,
            )
        )
        before = self.state.snapshot(created_time_ns=275)
        self.assertEqual(self.differences(), ("ORDER_STATE_UNKNOWN",))

        for changes in ({"side": Side.SELL}, {"quantity": Decimal("2")}):
            with self.subTest(changes=changes):
                self.assert_rejected_without_mutation(
                    self.event(
                        intent_id="synthetic-intent-1",
                        update_time_ns=300,
                        **changes,
                    )
                )

        linked = self.event(intent_id="synthetic-intent-1", update_time_ns=300)
        self.state.ingest_order_event(linked)
        after = self.state.snapshot(created_time_ns=350)
        self.assertEqual(set(after.orders), {"synthetic-exchange-1"})
        self.assertEqual(after.open_orders, (linked,))
        self.assertEqual(after.pending_new, ())
        self.assertEqual(after.unknown_orders, ())
        self.assertEqual(after.account, before.account)
        self.assertEqual(after.version, before.version + 1)
        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())
        self.assertEqual(
            before.unknown_orders[0].order_id,
            "synthetic-intent-1",
        )

    def test_err001_unknown_new_venue_id_cannot_establish_an_intent_link(self):
        self.record_intent()
        self.assert_rejected_without_mutation(
            self.event(OrderStatus.UNKNOWN, intent_id="synthetic-intent-1")
        )
        snapshot = self.state.snapshot(created_time_ns=250)
        self.assertEqual(set(snapshot.orders), {"synthetic-intent-1"})
        self.assertEqual(len(snapshot.pending_new), 1)
        self.assertEqual(snapshot.unknown_orders, ())

        self.state.ingest_order_event(
            self.event(
                order_id="synthetic-exchange-2",
                intent_id="synthetic-intent-1",
                update_time_ns=300,
            )
        )
        self.assertEqual(self.differences({"synthetic-exchange-2"}), ())

    def test_err002_exact_duplicate_is_idempotent_including_linked_events(self):
        self.record_intent()
        linked = self.event(intent_id="synthetic-intent-1")
        self.state.ingest_order_event(linked)
        before = self.state.snapshot(created_time_ns=250)

        self.state.ingest_order_event(linked)

        self.assertEqual(self.state.snapshot(created_time_ns=250), before)

    def test_err002_conflicting_equal_time_and_older_events_are_atomic(self):
        self.state.ingest_order_event(self.event())
        for candidate in (
            self.event(OrderStatus.PARTIAL_FILL, filled_quantity=Decimal("0.2")),
            self.event(update_time_ns=199),
        ):
            with self.subTest(candidate=candidate):
                self.assert_rejected_without_mutation(candidate)

    def test_err002_side_and_quantity_do_not_change_for_an_order_id(self):
        self.state.ingest_order_event(self.event())
        for changes in ({"side": Side.SELL}, {"quantity": Decimal("2")}):
            with self.subTest(changes=changes):
                self.assert_rejected_without_mutation(
                    self.event(update_time_ns=250, **changes)
                )

    def test_err002_cumulative_fill_cannot_decrease(self):
        self.state.ingest_order_event(
            self.event(OrderStatus.PARTIAL_FILL, filled_quantity=Decimal("0.6"))
        )
        self.assert_rejected_without_mutation(
            self.event(
                OrderStatus.PARTIAL_FILL,
                filled_quantity=Decimal("0.4"),
                update_time_ns=250,
            )
        )

    def test_err002_canceled_and_rejected_orders_cannot_reopen(self):
        for terminal in (OrderStatus.CANCELED, OrderStatus.REJECTED):
            with self.subTest(terminal=terminal):
                order_id = f"synthetic-{terminal.value.lower()}"
                self.state.ingest_order_event(self.event(terminal, order_id=order_id))
                self.assert_rejected_without_mutation(
                    self.event(order_id=order_id, update_time_ns=250)
                )

    def test_err002_filled_order_cannot_return_to_zero_fill_resting(self):
        self.state.ingest_order_event(
            self.event(OrderStatus.FILLED, filled_quantity=Decimal("1"))
        )
        self.assert_rejected_without_mutation(self.event(update_time_ns=250))

    def test_err002_open_order_cannot_revert_to_acknowledgment_or_submission(self):
        self.state.ingest_order_event(self.event())
        for status in (OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED):
            with self.subTest(status=status):
                self.assert_rejected_without_mutation(
                    self.event(status, update_time_ns=250)
                )

    def test_err002_status_and_filled_quantity_must_agree(self):
        for status, filled in (
            (OrderStatus.PARTIAL_FILL, "0"),
            (OrderStatus.PARTIAL_FILL, "1"),
            (OrderStatus.FILLED, "0.8"),
        ):
            with self.subTest(status=status, filled=filled):
                before = self.state.snapshot(created_time_ns=500)
                with self.assertRaises(ValueError):
                    self.state.ingest_order_event(
                        self.event(status, filled_quantity=Decimal(filled))
                    )
                self.assertEqual(self.state.snapshot(created_time_ns=500), before)

    def test_err002_initial_cancel_pending_does_not_invent_an_open_order(self):
        self.assert_rejected_without_mutation(self.event(OrderStatus.CANCEL_PENDING))

    def test_err002_cancel_pending_allows_partial_fill_but_rejects_full_fill(self):
        self.state.ingest_order_event(
            self.event(OrderStatus.PARTIAL_FILL, filled_quantity=Decimal("0.4"))
        )
        partial_cancel = self.event(
            OrderStatus.CANCEL_PENDING,
            filled_quantity=Decimal("0.4"),
            update_time_ns=250,
        )
        self.state.ingest_order_event(partial_cancel)
        before = self.state.snapshot(created_time_ns=400)
        self.assertEqual(before.open_orders, (partial_cancel,))

        with self.assertRaises(ValueError):
            self.state.ingest_order_event(
                self.event(
                    OrderStatus.CANCEL_PENDING,
                    filled_quantity=Decimal("1"),
                    update_time_ns=300,
                )
            )

        self.assertEqual(self.state.snapshot(created_time_ns=400), before)

    def test_err002_cancel_request_allows_later_partial_and_full_fills(self):
        self.state.ingest_order_event(self.event())
        self.state.ingest_order_event(
            self.event(OrderStatus.CANCEL_PENDING, update_time_ns=250)
        )
        self.assertEqual(self.differences({"synthetic-exchange-1"}), ())

        self.state.ingest_order_event(
            self.event(
                OrderStatus.PARTIAL_FILL,
                filled_quantity=Decimal("0.4"),
                update_time_ns=300,
            )
        )
        partial_snapshot = self.state.snapshot(created_time_ns=310)
        self.assertEqual(len(partial_snapshot.open_orders), 1)

        self.state.ingest_order_event(
            self.event(
                OrderStatus.FILLED,
                filled_quantity=Decimal("1"),
                update_time_ns=350,
            )
        )
        self.assertEqual(self.differences(), ())
        self.assertEqual(self.state.snapshot(created_time_ns=400).account.position, Decimal("0"))
        self.assertEqual(
            partial_snapshot.orders["synthetic-exchange-1"].filled_quantity,
            Decimal("0.4"),
        )

    def test_snapshots_prevent_external_order_mutation(self):
        self.state.ingest_order_event(self.event())
        snapshot = self.state.snapshot(created_time_ns=250)
        with self.assertRaises(TypeError):
            snapshot.orders["synthetic-exchange-2"] = self.event()
        with self.assertRaises(FrozenInstanceError):
            snapshot.orders["synthetic-exchange-1"].status = OrderStatus.FILLED

    def test_err003_future_timestamps_are_not_fresh(self):
        snapshot = self.state.snapshot(created_time_ns=99)
        self.assertFalse(snapshot.account_is_fresh(max_age_ns=1000))
        self.assertFalse(snapshot.market_is_fresh(max_age_ns=1000))

    def test_err003_freshness_includes_zero_and_maximum_age(self):
        for created, max_age, expected in (
            (100, 0, True),
            (150, 50, True),
            (151, 50, False),
        ):
            with self.subTest(created=created, max_age=max_age):
                snapshot = self.state.snapshot(created_time_ns=created)
                self.assertEqual(snapshot.account_is_fresh(max_age), expected)
                self.assertEqual(snapshot.market_is_fresh(max_age), expected)

    def test_err003_negative_freshness_limit_is_rejected_even_without_data(self):
        for state in (self.state, LiveState()):
            snapshot = state.snapshot(created_time_ns=100)
            with self.subTest(has_account=snapshot.account is not None):
                with self.assertRaises(ValueError):
                    snapshot.account_is_fresh(-1)
                with self.assertRaises(ValueError):
                    snapshot.market_is_fresh(-1)

    def test_err003_absent_sources_are_not_fresh(self):
        snapshot = LiveState().snapshot(created_time_ns=100)
        self.assertFalse(snapshot.account_is_fresh(1000))
        self.assertFalse(snapshot.market_is_fresh(1000))


if __name__ == "__main__":
    unittest.main()
