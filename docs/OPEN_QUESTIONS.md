# 我還想請教的問題

暫停不是把問題丟掉。以下是我現在還不會、但很想真正弄懂的事。如果你熟悉其中任何一題，歡迎開 Issue、推薦材料，或把問題改寫得更精確。

## Market microstructure

1. 在沒有 venue queue-position feed 的情況下，maker fill probability 最誠實的可識別範圍是什麼？
2. 如何把 queue depletion、cancel/reinsert tenure 與 adverse selection 放進同一個 survival / competing-risk model？
3. 用 public trades 做 hypothetical maker labels 時，哪些假設最常讓結果過度樂觀？

## 實驗與統計

1. Attempted action 包含大量 no-trade、no-fill 與 right-censoring 時，after-cost EV 的 lower confidence bound 應怎麼設計？
2. 每兩週再校調一次時，如何避免 repeated testing 把偶然結果變成「正期望」？
3. Regime 很少、樣本相依且 non-stationary 時，什麼樣的 blocked bootstrap 或 sequential test 比較合理？

## Execution 與分散式狀態

1. Account stream 和 REST snapshot 衝突時，live state 應採用什麼版本/事件規則，才能兼顧低延遲與可證明性？
2. Signed request timeout 後，如何設計 no-blind-retry 的 order reconciliation state machine？
3. 有既有 inventory、但 account/order state freshness 不足時，如何區分「不增加風險」與「繼續管理既有風險」？

## RL / ML

1. 如何讓 RL 只負責 execution policy，而保留可解釋、經過審查的 quote/risk theory？
2. Action space 應只包含 join/improve/widen/cancel/hold，還是連 size 與 inventory skew 都交給模型？
3. 在 fill outcome 部分可觀察、counterfactual 不可觀察的情況下，什麼 offline-RL evaluation 才不會假裝知道未執行 action 的 reward？

## 有限資源

1. 在小型 instance 上，怎麼分配 market ingest、account reconciliation、strategy loop、audit ledger 與 health checks 的 CPU/IO budget？
2. 哪些資料一定要在線保留，哪些可以 append-only rotation 到冷儲存，仍不破壞可重現性？

我特別珍惜能把「問題其實問錯了」講清楚的回饋。答案不需要替 kaZe 辯護；推翻它也很有價值。
