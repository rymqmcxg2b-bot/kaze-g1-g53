"""A tiny authoritative-live-state example with no exchange connectivity.

The important invariant is that an order intent never changes account position.
Only an authoritative account update may do that. The module is intentionally
incomplete as a trading system: it has no networking, credentials, signing,
order submission, persistence, pricing model, or live adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    INTENT = "INTENT"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESTING = "RESTING"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    CANCEL_PENDING = "CANCEL_PENDING"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MarketState:
    bid: Decimal
    ask: Decimal
    event_time_ns: int
    receive_time_ns: int
    source: str = "market_stream"

    def __post_init__(self) -> None:
        if self.bid <= 0 or self.ask <= 0 or self.bid >= self.ask:
            raise ValueError("market state requires 0 < bid < ask")


@dataclass(frozen=True)
class AccountState:
    position: Decimal
    equity: Decimal
    available_balance: Decimal
    update_time_ns: int
    source: str = "account_stream"


@dataclass(frozen=True)
class OrderEvent:
    order_id: str
    side: Side
    quantity: Decimal
    filled_quantity: Decimal
    status: OrderStatus
    update_time_ns: int
    source: str = "order_stream"

    def __post_init__(self) -> None:
        if not self.order_id:
            raise ValueError("order_id must not be empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if not Decimal("0") <= self.filled_quantity <= self.quantity:
            raise ValueError("filled_quantity must be between zero and quantity")


@dataclass(frozen=True)
class StateSnapshot:
    version: int
    created_time_ns: int
    market: MarketState | None
    account: AccountState | None
    orders: Mapping[str, OrderEvent]

    def account_is_fresh(self, max_age_ns: int) -> bool:
        return (
            self.account is not None
            and self.created_time_ns - self.account.update_time_ns <= max_age_ns
        )

    def market_is_fresh(self, max_age_ns: int) -> bool:
        return (
            self.market is not None
            and self.created_time_ns - self.market.receive_time_ns <= max_age_ns
        )

    @property
    def open_orders(self) -> tuple[OrderEvent, ...]:
        terminal = {
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.REJECTED,
        }
        return tuple(order for order in self.orders.values() if order.status not in terminal)


class LiveState:
    """Single in-memory owner for a coherent educational snapshot."""

    def __init__(self) -> None:
        self._version = 0
        self._market: MarketState | None = None
        self._account: AccountState | None = None
        self._orders: dict[str, OrderEvent] = {}

    def _advance(self) -> None:
        self._version += 1

    def ingest_market(self, state: MarketState) -> None:
        if self._market and state.receive_time_ns < self._market.receive_time_ns:
            raise ValueError("market update moved backwards")
        self._market = state
        self._advance()

    def ingest_account(self, state: AccountState) -> None:
        if self._account and state.update_time_ns < self._account.update_time_ns:
            raise ValueError("account update moved backwards")
        self._account = state
        self._advance()

    def ingest_order_event(self, event: OrderEvent) -> None:
        previous = self._orders.get(event.order_id)
        if previous and event.update_time_ns < previous.update_time_ns:
            raise ValueError("order update moved backwards")
        self._orders[event.order_id] = event
        self._advance()

    def record_intent(
        self,
        *,
        intent_id: str,
        side: Side,
        quantity: Decimal,
        created_time_ns: int,
    ) -> None:
        """Record intent without predicting an exchange result or position."""

        self.ingest_order_event(
            OrderEvent(
                order_id=intent_id,
                side=side,
                quantity=quantity,
                filled_quantity=Decimal("0"),
                status=OrderStatus.INTENT,
                update_time_ns=created_time_ns,
                source="strategy_intent",
            )
        )

    def snapshot(self, *, created_time_ns: int) -> StateSnapshot:
        return StateSnapshot(
            version=self._version,
            created_time_ns=created_time_ns,
            market=self._market,
            account=self._account,
            orders=MappingProxyType(dict(self._orders)),
        )

    def reconciliation_differences(
        self,
        *,
        authoritative_position: Decimal,
        authoritative_open_order_ids: set[str],
    ) -> tuple[str, ...]:
        """Compare, but never guess or silently repair, authoritative state."""

        differences: list[str] = []
        local_position = self._account.position if self._account else None
        if local_position != authoritative_position:
            differences.append("POSITION_MISMATCH")

        local_open_ids = {order.order_id for order in self.snapshot(created_time_ns=0).open_orders}
        if local_open_ids != authoritative_open_order_ids:
            differences.append("OPEN_ORDER_SET_MISMATCH")
        return tuple(differences)
