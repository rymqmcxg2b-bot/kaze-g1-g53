# 失敗與學習

這不是事故清單的完整原始副本，而是把重複出現的問題整理成可以被別人重用的模式。

## 1. 把工程進度誤認成經濟進度

通過單元測試、降低延遲、成功部署、service active、甚至真的有 fills，都不能單獨證明策略有正期望。kaZe 很長一段時間把「更多綠燈」感覺成「更靠近盈利」，但缺少的是預先固定、完整成本後的 untouched outcome population。

現在會怎麼做：先寫明研究問題、population、成本、censoring、promotion rule，再寫執行器。

## 2. 成本吃掉短週期訊號

G51 顯示一個很直接的事實：hot path 可以很快，但預測訊號若只有很小的 bps，而 round-trip fee、spread、slippage 與 exit cost 明顯更大，延遲優化無法把負經濟性變成正經濟性。

現在會怎麼做：任何模型比較一律以 net EV / attempted action 與 net EV / capital-time 評估，且在訓練前固定成本契約。

## 3. Public trade 被誤用成 execution evidence 的誘惑

看到市場在 quote price 成交，不代表 kaZe 的單排到隊首、仍在簿上、沒有被 cancel，也不代表成交量屬於自己。

現在會怎麼做：public trade 只能更新 queue model 或 hypothetical label；actual fill 必須來自帳戶/訂單事件，並連回自己的 order identity。

## 4. Cancel-first lifecycle 製造零單空窗

G20 的審計顯示 quote 常被週期性撤掉，resting tenure 被丟失；同步網路與 reconciliation 又吃掉顯著時間。策略雖頻繁產生兩側候選，市場上實際兩側同時存在的時間少很多。

現在會怎麼做：把 time-weighted quote availability、queue tenure、cancel reason、replacement gap 與 request budget 變成一等指標。

## 5. 多份「真相」讓策略和風控互相打架

Market、account、orders、local ledger 更新頻率不同。只要 position 或 open orders 在某個模組落後，就可能發生 quote/cancel 抖動、錯誤 block，或有 inventory 卻沒有可管理它的 orders。

現在會怎麼做：單一 authoritative live state；每個 snapshot 帶 timestamp、source、sequence、freshness、reconciliation version。

## 6. `sent`、`accepted`、`resting`、`filled` 被混成一件事

在分散式系統裡，timeout 後的結果是 unknown，不是 failed。自動重試 signed write 可能產生重複訂單；先預測 position 則會讓 local state 漂移。

現在會怎麼做：狀態機只接受有證據的 transition；unknown 先 reconciliation，不用猜測補狀態。

## 7. Recovery 成本隨歷史無上限增長

完整掃描 SQLite ledger、一次把資料載進記憶體，或啟動時做過多遠端查詢，會讓小 instance 卡死、timeout 或和策略競爭 request budget。

現在會怎麼做：checkpoint、reverse/streaming scan、明確 work bound、獨立 health budget，並測試長歷史與空歷史。

## 8. Fail-closed 不是免費的

Fail-closed 適合未知 credentials、stale market、unknown position 等情境；但如果遇到延遲就撤掉全部 orders，又讓有 inventory 的系統長時間無法報價，防護本身可能增加暴露。

現在會怎麼做：區分「不可增加風險」與「不可管理既有風險」。風險 gate 可以限制 action set，但不應默默改寫已測策略，再沿用原本的績效宣稱。

## 9. Replay integrity 通過，仍可能沒有可用 label

G53 strict replay 能驗證 hashes、references、causal clocks 與 no-write boundary，卻只有很少 activation 有完整市場後續，且沒有 actual outcomes。資料完整性成功，不等於研究問題可回答。

現在會怎麼做：同時追蹤 integrity、coverage、identifiability、sample size 與 economic labels；任何一項不足都明確回傳 unavailable。

## 10. Vibe coding 造成版本與意圖漂移

快速迭代容易讓每次對話都新增參數、gate、release 或「暫時修正」。當模型、prompt 與上下文都會變，最後很難說哪一份策略被測過、哪一份正在跑。

現在會怎麼做：

- 策略 identity 由 code、features、labels、costs、risk limits、residual-position policy 與 execution semantics 的 hashes 共同決定。
- 任何一項變更就是新 candidate。
- 研究、部署與 owner authorization 分離。
- AI 可以提案與寫程式，不能自己擴張任務或更改已授權策略。

## 11. 手動交易會破壞簡單 equity-delta 歸因

帳戶資產變化可能同時包含策略交易、手動交易、funding、fees、轉帳與未實現損益。只看期初期末 asset，不能回答某一代策略賺了多少。

現在會怎麼做：用 decision/order/fill 級 ledger 做策略歸因；外部持倉與人工行為明確標記為 inherited/external state。

## 12. 「暫停」也是研究成果

G53 的結論不是「再調一個 threshold」。在沒有可信 account/order truth、完整 outcomes 與足夠基礎時，繼續加程式會增加不確定性。暫停讓這條路徑保持誠實，也留下未來能從更好問題重新開始的可能。
