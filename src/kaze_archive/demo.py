"""Run a synthetic demonstration of the live-state invariants."""

from decimal import Decimal

from .live_state import AccountState, LiveState, MarketState, Side


def main() -> None:
    state = LiveState()
    state.ingest_market(
        MarketState(
            bid=Decimal("99.9"),
            ask=Decimal("100.1"),
            event_time_ns=1_000,
            receive_time_ns=1_010,
        )
    )
    state.ingest_account(
        AccountState(
            position=Decimal("0.25"),
            equity=Decimal("1000"),
            available_balance=Decimal("800"),
            update_time_ns=1_020,
        )
    )

    before = state.snapshot(created_time_ns=1_030)
    state.record_intent(
        intent_id="synthetic-intent-1",
        side=Side.SELL,
        quantity=Decimal("0.05"),
        created_time_ns=1_040,
    )
    after = state.snapshot(created_time_ns=1_050)

    print("Synthetic, no-network demonstration")
    print(f"position before intent: {before.account.position}")
    print(f"position after intent:  {after.account.position}")
    print(f"pending local intents:  {len(after.pending_new)}")
    print(f"confirmed open orders:  {len(after.open_orders)}")
    print("Position is unchanged until an authoritative account update arrives.")


if __name__ == "__main__":
    main()
