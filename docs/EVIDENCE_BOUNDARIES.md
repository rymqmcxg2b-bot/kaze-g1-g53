# 證據邊界

## 可以說的

- kaZe 經歷 G1–G53 的研究與工程迭代。
- 部分 controlled-live 階段確實產生過訂單、fills、reconciliation 與事故 evidence。
- G20 找到 quote placement、cancel-first lifecycle 與 quote availability 的具體問題。
- G51 的 forward evidence 不支持低延遲 taker candidate；成本明顯壓過短週期訊號。
- G52 建立了嚴格的 after-cost evaluation contract，但可用資料不足以回答正期望問題。
- G53 建立 no-write shadow 與 strict replay evidence；完整性檢查可通過，但 causal coverage 與 outcome labels 不足。
- Account/order/live-state 的一致性是未解決且會污染策略結論的核心工程問題。

## 不可以說的

- kaZe 已找到正期望或可盈利策略。
- 任何 generation 的回測、shadow 或小樣本結果代表未來績效。
- Public market trades 是 kaZe fills。
- Service active 代表正在正常交易。
- Open orders = 0 代表 position = 0，或反過來。
- 通過 hash、schema、unit test、benchmark 或部署驗證代表經濟假設成立。
- G52 的結果是「策略已證明為負」。正確結論是 evaluation unavailable。
- G53 選出了可實盤的 RL/ML execution model。

## 幾個重要數字如何解讀

### 86 fills / 34 cycles

這是一個早期、受控實盤的小樣本，合計淨結果為負。它能證明某些 execution paths 曾工作，也能提供事故與成本線索；不能可靠估計長期期望值。

### G52 的大量 market rows

它們是 ingestion events，不是獨立 strategy observations。若沒有每次 decision、被拒 action、attempt、no-fill/partial/full-fill、費用、退出與 capital-time，就不能拿 event count 當樣本數。

### G53 的 35 次 activation / 4 次 usable

Replay binding 與完整性檢查通過，但多數 activation 因缺少完整 causal 後續而 right-censored。可用資料太少，且沒有 actual execution outcome，所以沒有模型選擇或正期望結論。

## 對原始資料的處理

這個公開 repo 是從私人工作區以 allowlist 方式重新撰寫：

- 不繼承原始 Git history。
- 不含帳戶地址、position 明細、equity、entry price、fees、funding 或逐筆 IDs。
- 不含 API token、private key、credential-bearing URL、雲端 account/resource identifiers 或主機路徑。
- 不含 deployment receipts、owner authorization、service unit 與可操作 live endpoint。
- 只保留合成、不可交易的程式範例。

因此這裡可供學習與審查，但不是完整 forensic archive。若未來要做學術式重現，需要另行建立經同意、去識別化且可驗證的資料集。
