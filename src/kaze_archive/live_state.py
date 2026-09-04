"""A tiny authoritative-live-state example with no exchange connectivity.

The important invariant is that an order intent never changes account position.
Only an authoritative account update may do that. The module is intentionally
incomplete as a trading system: it has no networking, credentials, signing,
order submission, persistence, pricing model, or live adapter.

Corrected after the public-example review; see docs/ERRATA.md, ERR-001 through
ERR-003. Events are normalized inputs from a trusted caller, not authenticated
exchange messages. This single-caller example has no venue correction protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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


_TERMINAL = frozenset({OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED})
_CONFIRMED_OPEN = frozenset(
    {OrderStatus.RESTING, OrderStatus.PARTIAL_FILL, OrderStatus.CANCEL_PENDING}
)
_PENDING_NEW = frozenset(
    {OrderStatus.INTENT, OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED}
)
# A normalized snapshot may skip intermediate events. Same-state updates are
# allowed below; terminal corrections and same-order amendments are out of scope.
_NEXT_STATUSES = {
    OrderStatus.INTENT: {
        OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED, OrderStatus.RESTING,
        OrderStatus.PARTIAL_FILL, OrderStatus.FILLED, OrderStatus.CANCELED,
        OrderStatus.REJECTED, OrderStatus.UNKNOWN,
    },
    OrderStatus.SUBMITTED: {
        OrderStatus.ACKNOWLEDGED, OrderStatus.RESTING, OrderStatus.PARTIAL_FILL,
        OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED,
        OrderStatus.UNKNOWN,
    },
    OrderStatus.ACKNOWLEDGED: {
        OrderStatus.RESTING, OrderStatus.PARTIAL_FILL, OrderStatus.FILLED,
        OrderStatus.CANCELED, OrderStatus.REJECTED, OrderStatus.UNKNOWN,
    },
    OrderStatus.RESTING: {
        OrderStatus.PARTIAL_FILL, OrderStatus.FILLED, OrderStatus.CANCEL_PENDING,
        OrderStatus.CANCELED, OrderStatus.UNKNOWN,
    },
    OrderStatus.PARTIAL_FILL: {
        OrderStatus.FILLED, OrderStatus.CANCEL_PENDING, OrderStatus.CANCELED,
        OrderStatus.UNKNOWN,
    },
    OrderStatus.CANCEL_PENDING: {
        OrderStatus.RESTING, OrderStatus.PARTIAL_FILL, OrderStatus.FILLED,
        OrderStatus.CANCELED, OrderStatus.UNKNOWN,
    },
    OrderStatus.UNKNOWN: {
        OrderStatus.ACKNOWLEDGED, OrderStatus.RESTING, OrderStatus.PARTIAL_FILL,
        OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED,
    },
}


def _is_fresh(created_time_ns: int, update_time_ns: int | None, max_age_ns: int) -> bool:
    """ERR-003: future updates are not fresh; all clocks must share a domain."""
    if max_age_ns < 0:
        raise ValueError("max_age_ns must be non-negative")
    return update_time_ns is not None and 0 <= created_time_ns - update_time_ns <= max_age_ns


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
    """Local ID while pending, venue ID after explicit intent_id linkage.

    ACKNOWLEDGED alone does not establish resting membership. RESTING and
    PARTIAL_FILL must represent venue-confirmed membership supplied by the caller.
    CANCEL_PENDING keeps prior confirmed membership until an outcome arrives.
    """
    order_id: str
    side: Side
    quantity: Decimal
    filled_quantity: Decimal
    status: OrderStatus
    update_time_ns: int
    source: str = "order_stream"
    intent_id: str | None = None

    def __post_init__(self) -> None:
        if not self.order_id:
            raise ValueError("order_id must not be empty")
        if not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if (
            not self.filled_quantity.is_finite()
            or not Decimal("0") <= self.filled_quantity <= self.quantity
        ):
            raise ValueError("filled_quantity must be between zero and quantity")
        if self.intent_id == "":
            raise ValueError("intent_id must not be empty")
        if self.status is OrderStatus.FILLED and self.filled_quantity != self.quantity:
            raise ValueError("FILLED requires the full quantity")
        if self.status is OrderStatus.PARTIAL_FILL and not (
            Decimal("0") < self.filled_quantity < self.quantity
        ):
            raise ValueError("PARTIAL_FILL requires a partial quantity")
        if self.status is OrderStatus.CANCEL_PENDING and self.filled_quantity == self.quantity:
            raise ValueError("CANCEL_PENDING requires remaining quantity")
        unfilled = _PENDING_NEW | {OrderStatus.RESTING, OrderStatus.REJECTED}
        if self.status in unfilled and self.filled_quantity != 0:
            raise ValueError("unfilled status cannot have cumulative fills")


@dataclass(frozen=True)
class StateSnapshot:
    version: int
    created_time_ns: int
    market: MarketState | None
    account: AccountState | None
    orders: Mapping[str, OrderEvent]

    def account_is_fresh(self, max_age_ns: int) -> bool:
        return _is_fresh(
            self.created_time_ns,
            self.account.update_time_ns if self.account is not None else None,
            max_age_ns,
        )

    def market_is_fresh(self, max_age_ns: int) -> bool:
        """Receive-time freshness only; this is not a sequence/gap guarantee."""
        return _is_fresh(
            self.created_time_ns,
            self.market.receive_time_ns if self.market is not None else None,
            max_age_ns,
        )

    @property
    def open_orders(self) -> tuple[OrderEvent, ...]:
        """ERR-001: last confirmed open membership, not all nonterminal records."""
        return tuple(order for order in self.orders.values() if order.status in _CONFIRMED_OPEN)

    @property
    def pending_new(self) -> tuple[OrderEvent, ...]:
        return tuple(order for order in self.orders.values() if order.status in _PENDING_NEW)

    @property
    def unknown_orders(self) -> tuple[OrderEvent, ...]:
        return tuple(order for order in self.orders.values() if order.status is OrderStatus.UNKNOWN)


class LiveState:
    """Single-caller store; a snapshot does not make asynchronous feeds simultaneous."""

    def __init__(self) -> None:
        self._version = 0
        self._market: MarketState | None = None
        self._account: AccountState | None = None
        self._orders: dict[str, OrderEvent] = {}
        self._intent_order_ids: dict[str, str] = {}

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
        """Validate a normalized event before changing records or snapshot version."""
        linked_id = self._intent_order_ids.get(event.order_id)
        if linked_id is not None and linked_id != event.order_id:
            raise ValueError("retired local identity requires its linked venue order ID")
        previous = self._orders.get(event.order_id)
        # Preserve a known identity link on subsequent venue messages.
        if previous and previous.intent_id is not None:
            if event.intent_id is None:
                event = replace(event, intent_id=previous.intent_id)
            elif event.intent_id != previous.intent_id:
                raise ValueError("order intent identity changed")

        pending = None
        if event.intent_id is not None:
            linked_order = self._intent_order_ids.get(event.intent_id)
            if linked_order is not None and linked_order != event.order_id:
                raise ValueError("intent is already linked to another order")
            if linked_order is None:
                pending = self._orders.get(event.intent_id)
                if pending is None or pending.status not in _PENDING_NEW | {OrderStatus.UNKNOWN}:
                    raise ValueError("intent link requires a known pending record")
                if previous is not None and event.order_id != event.intent_id:
                    raise ValueError("venue order identity already exists")
                if event.status in {OrderStatus.INTENT, OrderStatus.SUBMITTED, OrderStatus.UNKNOWN}:
                    raise ValueError("intent link requires a venue outcome")

        baseline = previous if previous is not None else pending
        if baseline is not None:
            # ERR-002: retries are no-ops; conflicting ties have no safe ordering.
            if event == baseline:
                return
            if event.update_time_ns <= baseline.update_time_ns:
                raise ValueError("order update is older or conflicts at the same timestamp")
            if event.side != baseline.side or event.quantity != baseline.quantity:
                raise ValueError("order side and quantity must remain unchanged")
            if event.filled_quantity < baseline.filled_quantity:
                raise ValueError("cumulative filled quantity moved backwards")
            if baseline.status in _TERMINAL:
                if event.status != baseline.status or event.filled_quantity != baseline.filled_quantity:
                    raise ValueError("terminal order cannot change or reopen")
            elif event.status != baseline.status and event.status not in _NEXT_STATUSES[baseline.status]:
                raise ValueError("invalid normalized order transition")
        if event.status is OrderStatus.CANCEL_PENDING and (
            baseline is None or baseline.status not in _CONFIRMED_OPEN
        ):
            raise ValueError("cancel pending requires a previously confirmed open order")

        # All validation precedes mutation, including retirement of the local ID.
        if pending is not None and event.intent_id != event.order_id:
            del self._orders[event.intent_id]
        if event.intent_id is not None:
            self._intent_order_ids[event.intent_id] = event.order_id
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

        if intent_id in self._intent_order_ids:
            raise ValueError("intent identity has already been used")
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

        snapshot = self.snapshot(created_time_ns=0)
        local_open_ids = {order.order_id for order in snapshot.open_orders}
        if local_open_ids != authoritative_open_order_ids:
            differences.append("OPEN_ORDER_SET_MISMATCH")
        if any(order.status is not OrderStatus.INTENT for order in snapshot.pending_new):
            differences.append("PENDING_ORDER_CONFIRMATION")
        if snapshot.unknown_orders:
            differences.append("ORDER_STATE_UNKNOWN")
        return tuple(differences)
