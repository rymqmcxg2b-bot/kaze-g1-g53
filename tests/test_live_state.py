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


class LiveStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = LiveState()
        self.state.ingest_market(
            MarketState(
                bid=Decimal("99"),
                ask=Decimal("101"),
                event_time_ns=100,
                receive_time_ns=110,
            )
        )
        self.state.ingest_account(
            AccountState(
                position=Decimal("0.25"),
                equity=Decimal("1000"),
                available_balance=Decimal("800"),
                update_time_ns=120,
            )
        )

    def test_order_intent_never_predicts_position(self) -> None:
        before = self.state.snapshot(created_time_ns=130).account.position
        self.state.record_intent(
            intent_id="synthetic-1",
            side=Side.SELL,
            quantity=Decimal("0.05"),
            created_time_ns=140,
        )
        after = self.state.snapshot(created_time_ns=150).account.position
        self.assertEqual(before, after)

    def test_open_order_state_follows_exchange_event(self) -> None:
        self.state.ingest_order_event(
            OrderEvent(
                order_id="synthetic-2",
                side=Side.BUY,
                quantity=Decimal("0.10"),
                filled_quantity=Decimal("0"),
                status=OrderStatus.RESTING,
                update_time_ns=140,
            )
        )
        self.assertEqual(len(self.state.snapshot(created_time_ns=150).open_orders), 1)

        self.state.ingest_order_event(
            OrderEvent(
                order_id="synthetic-2",
                side=Side.BUY,
                quantity=Decimal("0.10"),
                filled_quantity=Decimal("0.10"),
                status=OrderStatus.FILLED,
                update_time_ns=160,
            )
        )
        self.assertEqual(len(self.state.snapshot(created_time_ns=170).open_orders), 0)

    def test_reconciliation_reports_both_state_mismatches(self) -> None:
        # ERR-001: only venue-confirmed membership can disagree with venue open IDs.
        self.state.ingest_order_event(
            OrderEvent(
                order_id="synthetic-3",
                side=Side.SELL,
                quantity=Decimal("0.05"),
                filled_quantity=Decimal("0"),
                status=OrderStatus.RESTING,
                update_time_ns=140,
            )
        )
        differences = self.state.reconciliation_differences(
            authoritative_position=Decimal("0.20"),
            authoritative_open_order_ids=set(),
        )
        self.assertEqual(
            differences,
            ("POSITION_MISMATCH", "OPEN_ORDER_SET_MISMATCH"),
        )

    def test_stale_account_is_explicit(self) -> None:
        snapshot = self.state.snapshot(created_time_ns=1_000)
        self.assertFalse(snapshot.account_is_fresh(max_age_ns=500))
        self.assertTrue(snapshot.market_is_fresh(max_age_ns=1_000))

    def test_updates_cannot_move_backwards(self) -> None:
        with self.assertRaises(ValueError):
            self.state.ingest_account(
                AccountState(
                    position=Decimal("0"),
                    equity=Decimal("1000"),
                    available_balance=Decimal("1000"),
                    update_time_ns=119,
                )
            )


if __name__ == "__main__":
    unittest.main()
