# 架構與資料流：最後才看清楚的核心問題

kaZe 最重要的架構教訓不是某個 spread 參數，而是：**策略、風控與 execution 必須讀同一份、帶 freshness 與 provenance 的 live state。**

## 理想資料流

```text
Market stream ───────┐
                     │
Account stream ──────┼──> Authoritative Live State ──> Strategy
                     │           │                        │
Order/fill events ───┘           │                        v
                                 │                   Quote intent
REST reconciliation ─────────────┤                        │
                                 │                        v
                                 │                    Execution
                                 │                        │
                                 └<── ACK / fill / reject┘
```

每一個 decision 應該綁定一個不可混淆的 snapshot：

```text
S(t) = {
  market: bid, ask, depth, trades, volatility, event_time, receive_time,
  account: equity, available_balance, position, margin, unrealized_pnl,
  orders: exchange_open_orders, pending_new, pending_cancel, last_ack,
  execution: last_fill, last_cancel, last_reject,
  provenance: source, sequence, freshness, reconciliation_version
}
```

策略只輸出 intent：

```text
A(t) = policy(S(t))
```

`A(t)` 不是成交，也不能直接修改 position。

## 歷史上容易出現的鬆散架構

```text
Market WebSocket ──> fast strategy loop

Account REST ──────> slower cache ──> risk module

Local order table ─> execution assumptions
```

若三條路徑的時間不同，可能形成：

1. Strategy 看到 position = 0，決定掛 bid。
2. Risk 稍後讀到 position != 0，立刻 cancel。
3. 下一個 strategy tick 又讀到舊 cache，再次 quote。
4. 系統進入 `QUOTE → CANCEL → QUOTE → CANCEL`。

表面像是 cancel threshold 太敏感，實際上是不同模組活在不同時間點。

## Authoritative owner

| 狀態 | 即時主來源 | 次要來源 | 不可接受的做法 |
|---|---|---|---|
| BBO / L2 / trades | market stream | bounded public snapshot | 讓 ping 或另一頻道掩蓋 stale book |
| Position / balance | account stream | periodic authenticated REST reconciliation | 送出 buy intent 後直接 `position += qty` |
| Open orders | order/account stream | exchange REST reconciliation | 只信 local `submitted` row |
| Order lifecycle | exchange ACK/fill/cancel/reject | reconciliation result | 把 `sent` 當成 `resting` |
| PnL / costs | decision-linked fills、fees、funding、exit | independently reconstructed ledger | 用 public trade 或 equity delta 代替策略歸因 |

## 訂單狀態不是布林值

```text
INTENT
  ↓
SUBMITTED
  ↓
ACKNOWLEDGED
  ↓
RESTING ───────> CANCEL_PENDING ───────> CANCELED
  │
  ├──> PARTIAL_FILL
  │         │
  │         └──> FILLED
  └──> REJECTED / UNKNOWN → RECONCILE
```

每個 transition 都需要 exchange evidence。Timeout 只能把結果標成 unknown，不能自行判定失敗或重試 signed write。

## WebSocket 與 REST 的角色

- WebSocket / account stream：低延遲 live truth。
- REST：啟動、週期性與異常時的 reconciliation。
- Strategy：只讀一個一致 snapshot，不直接向多個 client 拉狀態。
- Execution：提交 intent，等待 ACK/fill，將事件回灌 live state。

REST 不能在每個 decision tick 阻塞策略，但 WebSocket 也不能被假設永遠完整；兩者需要明確的 freshness、sequence/gap 與 conflict policy。

## 暫停前仍未完成的核心

kaZe 建立過許多局部 reconciliation 與 fail-closed gates，但沒有持續做到下面四件事同時成立：

1. Account、orders、fills 與 market state 有唯一 snapshot identity。
2. 每個 decision 都能追到完整 action complement 與 terminal outcome。
3. Live、shadow 與 replay 真正共享同一個 verified transition path。
4. 任何策略結論都能從 after-cost、capital-time、不可刪除的完整 population 重算。

本 repo 的 `src/kaze_archive/live_state.py` 是對這個教訓的最小、不可交易示例。
