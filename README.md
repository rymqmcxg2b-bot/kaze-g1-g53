# kaZe：53 次迭代後，我暫停了一個沒有證明能盈利的交易系統

> **Status: PAUSED / RESEARCH ARCHIVE**
>
> kaZe 沒有證明正期望值，也不是可直接投入資金的交易產品。這個公開版本不含憑證、帳戶識別、雲端資源識別、私人交易資料或可直接連到交易所的執行器。

kaZe 是我用 vibe coding 探索市場微結構、自動交易、資料完整性與實盤執行的學習專案。它從 G1 走到 G53，留下的不是一條成功的獲利曲線，而是一條逐漸學會分辨「程式能跑」、「訂單能送」與「策略真的有可信優勢」的路。

[English summary](#english-summary) · [G1–G53 完整索引](docs/JOURNEY_G1_G53.md) · [架構與資料流](docs/ARCHITECTURE.md) · [失敗與學習](docs/FAILURES_AND_LESSONS.md) · [證據邊界](docs/EVIDENCE_BOUNDARIES.md) · [還想請教的問題](docs/OPEN_QUESTIONS.md)

## 為什麼我要公開 kaZe

我做 kaZe 的起點其實很單純：我對市場怎麼運作非常好奇，也很想知道，一個普通人能不能靠著現在的 AI 工具，把腦中的交易想法一步一步變成真正會讀行情、管理庫存、送出訂單並面對真實結果的系統。

Vibe coding 給了我以前沒有的能力。很多原本遙不可及的東西——WebSocket、order book、replay、風控、雲端部署、狀態機、模型訓練——忽然都可以開始動手做。我很投入，也真的享受每一次「原來這裡還有一層」的發現。kaZe 就這樣從 G1 一路走到 G53。

但這段經驗也讓我看見自己的不足。

我一度把版本增加、測試通過和工程變複雜，誤認成系統正在接近盈利。後來才逐漸明白：交易系統最難的，不只是把程式寫出來，而是確定資料代表什麼、成本怎麼進入結果、公開成交是不是自己的成交、position 和 open orders 是否真的同步，以及策略、風控和執行模組看到的究竟是不是同一個世界。

kaZe 沒有證明正期望值。短週期 taker 訊號被成本吃掉；maker 的 fill、queue、adverse selection 和完整 reward 資料不足；實盤工程也反覆暴露 account state、reconciliation、啟動、權限與資源限制的問題。有些地方完成了很嚴格的測試，卻仍然不能回答最基本的問題：這個策略在真實成本與真實執行下，究竟有沒有賺錢的能力？

所以我決定先暫停這個計畫。

這不是因為我對它失去興趣，而是因為我不想再用更多程式碼掩蓋自己在市場微結構、統計驗證、實驗設計與分散式系統上的基礎缺口。我需要先把這些東西學得更扎實，再決定 kaZe 是否值得繼續。

我把它公開，不是要展示一個成功的交易機器，也不是要提供任何人拿去投入資金。我想分享的是一個真實、混亂、有熱情也有錯誤的學習過程。如果這套失敗的系統、留下來的測試、事故紀錄或資料契約，剛好能幫助某個人少踩一個坑，我會非常開心。

如果你願意指出我哪裡想錯了、推薦我應該補的基礎、一起研究某個問題，甚至只是聊聊你做系統時遇過的失敗，都很歡迎。我也希望能在這裡認識朋友，和願意認真求證、也願意承認不知道的人一起學習。

謝謝你來看 kaZe。這裡沒有獲利承諾，只有 53 次嘗試後留下的問題、證據，以及還沒有消失的好奇心。

## kaZe 想探索什麼

- BTC 永續合約的 maker / inventory market making。
- 用 order flow、imbalance、volatility 與 adverse selection 判斷是否報價。
- 讓 inventory skew 影響雙邊價格與尺寸。
- 讓 replay、shadow 與 live 盡量共享同一條 decision path。
- 用 reconciliation、append-only evidence 與 fail-closed gates 管理真實狀態。
- 在有限硬體資源下，維持可以觀察、回復與重現的 24/7 runtime。

這些是逐步嘗試過的目標，不代表全部已完成。

## 53 代濃縮地圖

| 階段 | 發生了什麼 |
|---|---|
| G1–G15 | 早期探索與 P0–P6 基礎：唯讀資料、lineage、replay bundle、shadow runtime、risk gate、execution state machine。現存材料不足以可靠區分每一代，公開版不虛構細節。 |
| G16–G22 | 面對 BBO/L2 freshness、fill attribution、reconciliation、latency latch、spread floor 與停止契約。第一次清楚看到「有行情」不等於所有模組看到同一個即時世界。 |
| G23–G30 | 追求熱路徑、資金利用率、request budget、cycle throughput、quote availability 與 atomic modify；也遇到 cancel-to-reinsert 空窗、dust recovery 與 cost-basis 缺口。 |
| G31–G37 | 把 after-cost EV 納入決策，同時被 Decimal、SQLite、記憶體、啟動恢復、權限與 resting intent reconciliation 反覆擊中。 |
| G38–G44 | 讓啟動、健康檢查、known fill、protective flatten、operator stop 與 zero-position row 變成 state-aware reconciliation。核心問題變成「系統知道什麼、何時知道」。 |
| G45–G50 | 回到 maker quote availability、inventory acquisition、loss-aware accumulation、adverse-selection guard、bounded startup 與 continuous resume。工程更嚴謹，盈利仍未成立。 |
| G51 | 嘗試低延遲 taker。工程 benchmark 通過，但 untouched forward evidence 顯示交易成本遠大於可預測訊號，因此拒絕候選。 |
| G52 | 建立更嚴格的正期望測試契約、五通道資料、sealed cohort 與 action shadow；結果是資料與 decision-to-outcome population 不完整，不能回答正期望問題。 |
| G53 | 改回 maker，做 public shadow、activation-L2、strict replay、歷史資料與模型候選分析；可用 causal replay 覆蓋太低，沒有形成正 hypothetical fill、完整 reward 或可信訓練資料。後續 live continuation 又暴露 packaging、權限、SQLite identity、啟動等待與 account/order reconciliation 問題。 |

逐代資料、日期與證據信心見 [G1–G53 完整索引](docs/JOURNEY_G1_G53.md)。

## 最誠實的結果

kaZe **沒有找到或證明一個可重複、成本後為正的交易策略**。

- 一組早期 controlled-live 小樣本出現 86 fills、34 completed cycles，合計淨結果為負；樣本不足以外推。
- G51 taker 的短週期訊號幅度小於完整交易成本，候選被拒絕。
- G52 雖收集大量公開市場事件，但缺少完整的 strategy decision、attempt、fill/no-fill 與 after-cost outcome population，因此不能做正期望判定。
- G53 strict replay 的 35 次 activation 只有 4 次可用；沒有正 hypothetical fill，也沒有完整 reward 或可訓練 outcome population。
- 實盤工程曾成功送出、維護與對帳部分訂單，但 account state、open orders、positions 與多模組 freshness 沒有一直形成可靠的 single source of truth。

所以「有程式、有測試、有資料、有實盤紀錄」不等於「有可信的策略績效」。

## 我真正學到的事

1. **成本可能比短週期 alpha 大一個數量級。** 費用、spread、slippage、adverse selection、funding 與退出成本必須在研究開始前進入定義。
2. **公開市場成交不是自己的 fill。** 沒有 decision → order → ack/fill → position → PnL 的完整鏈，績效分析就不可信。
3. **order sent 不是 order accepted。** Accepted、resting、partial fill、filled、cancel pending、canceled 都是不同狀態。
4. **account state 必須有唯一權威來源。** 多份不同 freshness 的 position、balance 與 open-order snapshot，會讓策略和風控互相打架。
5. **執行機制也是策略。** Cancel policy、queue position、request budget、rate limit、cold start 和 recovery 都會改變經濟結果。
6. **更多版本不等於更好的研究設計。** 如果每看一次結果就改規則，就沒有 untouched evidence。
7. **fail-closed 也有代價。** 它能避免未知狀態下亂送單，也可能在有 inventory 時撤掉保護性 maker orders；必須把風險界線與策略語義一起設計。
8. **vibe coding 是放大器。** 它放大了我的好奇心和實作速度，也放大了我尚未察覺的知識缺口。

## 這個 repo 有什麼

這不是原始 production repository 的 dump，而是一份 **allowlist 重建、去識別化的公開研究檔案**：

- `docs/JOURNEY_G1_G53.md`：每一代的焦點、結果與證據信心。
- `docs/ARCHITECTURE.md`：最後理解到的 authoritative live-state 資料流。
- `docs/FAILURES_AND_LESSONS.md`：失敗模式、因果關係與現在會怎麼重做。
- `docs/EVIDENCE_BOUNDARIES.md`：哪些結果成立、哪些不能宣稱。
- `docs/OPEN_QUESTIONS.md`：如果你想教我或一起研究，可以從這裡開始。
- `src/kaze_archive/`：不連網、不送單的教育性狀態機範例。
- `tests/`：驗證「送出 intent 不得自行改 position」等關鍵不變量。

原始 runtime、部署 receipts、帳戶資料、wallet/order/fill identifiers、雲端拓撲、秘密與舊 Git 歷史刻意不公開。範例是依學到的原則重寫，不是 production executor。

## 本機執行教育性範例

需要 Python 3.11+，不需要第三方套件，也不會存取網路：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m kaze_archive.demo
python scripts/public_safety_scan.py
```

## 想一起研究或教我嗎？

歡迎開 Issue 或 Discussion。現在最想得到幫助的方向包括：

- market microstructure 與 maker queue mechanics；
- after-cost 統計驗證、selection bias 與 leakage review；
- execution state machine 與 exchange reconciliation；
- data lineage、causal replay 與可重現實驗；
- 小型雲端 instance 上的可靠 runtime 工程；
- 適合補足基礎的書、paper、課程與練習路線。

請參考 [CONTRIBUTING.md](CONTRIBUTING.md)。善意但直接的批評很歡迎。

## English summary

kaZe is a personal learning project exploring market microstructure, maker/taker execution, inventory-aware quoting, data lineage, reconciliation, and controlled live trading.

After 53 generations, it did not establish positive after-cost expectancy. Some engineering components worked, but incomplete decision-to-outcome data, trading costs, execution-state drift, limited causal replay coverage, and gaps in my own foundations prevented a trustworthy profitability conclusion.

I am pausing the project to study market microstructure, statistics, experimental design, and distributed systems more seriously. I am publishing this sanitized research archive because the failed experiments, tests, and incident patterns may still help someone else. Feedback, teaching, research conversations, and new friendships are warmly welcome.

This repository is for education and research. It is not investment advice, a profitable strategy, a production trading system, or authorization to trade. Historical and hypothetical results must not be interpreted as future performance.

## License

Code is released under the [MIT License](LICENSE). Documentation is shared under the same terms for simplicity. Attribution and links back to this archive are appreciated.
