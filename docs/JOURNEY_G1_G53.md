# kaZe G1–G53：逐代研究索引

這份索引是從保留下來的設計審查、事故紀錄、測試結果、release 名稱與研究報告重建的公開時間線。它不是原始操作日誌的逐字副本。

## 怎麼讀這張表

- **直接**：有該代命名的設計、release、事故或評估材料支撐。
- **部分**：有相鄰版本或後期材料可確認大方向，但不足以重建完整差異。
- **未保存**：公開資料不足；不為了故事完整而補寫不存在的細節。
- 每一列描述的是研究/工程焦點，不代表成功、盈利或正式部署。

## G1–G15：早期探索

| 代 | 公開可確認的經過 | 證據信心 |
|---:|---|---|
| G1 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G2 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G3 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G4 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G5 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G6 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G7 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G8 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G9 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G10 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G11 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G12 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G13 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G14 | 個別差異未保存；屬於早期資料與策略探索。 | 未保存 |
| G15 | 後期材料顯示已形成初步 controlled-live 基線；個別設計差異未完整保存。 | 部分 |

後期 repo 可確認這一階段逐步建立了 P0–P6 工程骨架：來源唯讀、資料 lineage、replay bundle、shadow runtime、fail-closed risk gate、audit JSONL、paper execution 與 phase/capability 分離。但無法把每個元件可靠地對應到 G1–G15 的特定一代。

## G16–G22：讓 runtime 對「現在」有一致理解

| 代 | 公開可確認的經過 | 結果 / 學到的事 | 信心 |
|---:|---|---|---|
| G16 | 修正 BBO/L2 freshness 與初始 inventory baseline 的 fill attribution。 | Market heartbeat 與 position conservation 必須分別被證明。 | 直接 |
| G17 | 用 durable fill ledger 做持續 protective attribution，處理前代 latch 後的恢復。 | 不能只靠當下查詢視窗推回完整持倉歷史。 | 直接 |
| G18 | 縮短 reconciliation 範圍，並在任何 dispatch 前再次核對 position/open orders。 | 查詢本身可以健康，但本機資料路徑仍可能把系統卡住。 | 直接 |
| G19 | 修正恢復與保護性退出的 execution-layer 狀態。 | 一次 protective attempt 的結果必須 terminal，不能因重啟默默重試。 | 直接 |
| G20 | 在成功 flatten 後，以新 generation 解除 latency latch；同時做 fill-rate 數學審計。 | 策略多數時間會產生 quote，但 cancel-first lifecycle、離 touch 太遠與短 quote age 共同壓低成交。 | 直接 |
| G21 | 單一參數實驗：調整最小 half-spread floor，其餘策略與限制不變。 | 參數改動必須和 execution availability 分開歸因。 | 直接 |
| G22 | 修正 service stop 契約，讓正常停止能完成 graceful cancel。 | 作業系統如何終止程序也是交易狀態機的一部分。 | 直接 |

## G23–G30：從「會決策」走向「訂單真的能留在市場」

| 代 | 公開可確認的經過 | 結果 / 學到的事 | 信心 |
|---:|---|---|---|
| G23 | 將 market-data path 拉進 hot path review，整理 L2/BBO 更新與決策延遲。 | 資料頻率、去重與 freshness 定義會直接改變 quote 行為。 | 直接 |
| G24 | Capital-utilization candidate 與情境測試。 | 提高資金使用率不能脫離成交機率、退出成本與 inventory dwell。 | 直接 |
| G25 | Request-budget recovery 與策略理論/執行審計。 | API budget、重試與 quote replacement 會形成隱性策略約束。 | 直接 |
| G26 | Cycle-throughput candidate、保護性 scope 修正與 quote-availability incident。 | 追求更高循環頻率若沒有狀態一致性，只會更快製造空窗。 | 直接 |
| G27 | Quote-availability redesign。 | 應量測每一側 resting 的 time-weighted availability，而不只看 decision count。 | 直接 |
| G28 | Atomic modify、dust recovery、post-fill ALO rejection 與 reduction cost-basis gap。 | Cancel/reinsert 不是原子的；最小量、成本基礎與保護性退出都會破壞理論假設。 | 直接 |
| G29 | 從 G27/G28 事故恢復並用新 generation re-arm。 | Recovery generation 的存在是證據，不是新 alpha。 | 部分 |
| G30 | 完成 G28 atomic-modify 系列的合併部署/穩定性觀察。 | 工程恢復不能被當成策略進步。 | 部分 |

## G31–G37：after-cost EV 遇上真實 runtime

| 代 | 公開可確認的經過 | 結果 / 學到的事 | 信心 |
|---:|---|---|---|
| G31 | Capital-aware EV candidate；後續處理 Decimal representation、reconciliation 與 startup timeout。 | 把成本寫進公式只是開始，數值表示與啟動狀態也會改變決策。 | 直接 |
| G32 | 將大型 SQLite ledger 驗證改為 streaming。 | 完整性檢查若把整份 ledger 載入記憶體，會在小型主機上成為可用性故障。 | 直接 |
| G33 | 調整資源 envelope；遇到 bounded-restore 啟動與 stop-protection 問題。 | 換較大 instance 能緩解症狀，但不能取代 bounded algorithm。 | 直接 |
| G34 | 建立 bounded restore gate 與 release。 | Recovery 必須有明確工作上限，且不能因歷史越長就無限變慢。 | 直接 |
| G35 | Reverse scan、empty-history gate 與 delayed-health race。 | 空歷史不是 corruption；健康檢查與啟動程序需要同一套語義。 | 直接 |
| G36 | Quiescent acceptance、stopped-state persistence 與 unresolved-intent checks。 | 「現在沒有動作」可能是有效狀態，也可能是未知狀態，兩者必須可區分。 | 直接 |
| G37 | Resting intent acceptance、single-intent reconciliation 與權限事故。 | 本機 intent 只有和 exchange order 對上，才有資格成為真實狀態。 | 直接 |

## G38–G44：把啟動與恢復做成 state-aware

| 代 | 公開可確認的經過 | 結果 / 學到的事 | 信心 |
|---:|---|---|---|
| G38 | Episode fill window、rate-budgeted startup、ledger/test gate 與 delayed health。 | 啟動查詢也會消耗 request budget；診斷不能和執行互相搶資源。 | 直接 |
| G39 | State-aware startup/acceptance。 | Acceptance 必須依真實 exchange state 判斷，不能要求所有情境都長得像 flat cold start。 | 直接 |
| G40 | First coherent startup 與 known-inventory resume。 | 已知 inventory 應成為啟動輸入，不該被當成異常或被忽略。 | 直接 |
| G41 | Known-fill reconciliation resume。 | 已知 fill 必須和 local lifecycle、position 及 order history 同時閉合。 | 直接 |
| G42 | Protective-flat re-arm。 | Flatten 是一個有證據鏈的 execution episode，不是把記憶體 position 設成零。 | 直接 |
| G43 | Operator-stopped live resume。 | 人工停止是正式狀態；恢復必須能區分 operator stop、crash 與 risk latch。 | 直接 |
| G44 | State-aware live resume 與 zero-position row reconciliation。 | `position = 0` 也是一筆權威狀態，不能因為數值為零而被過濾掉。 | 直接 |

## G45–G50：重新追求 maker 的可用性與經濟性

| 代 | 公開可確認的經過 | 結果 / 學到的事 | 信心 |
|---:|---|---|---|
| G45 | Position quote availability、inventory acquisition 與 wide-stop design。 | 有 inventory 時不送 quote 可能失去 skew/退出能力；但 quote 的存在仍不等於有正 EV。 | 直接 |
| G46 | Bounded initialization 與 profit-throughput local candidate。 | 必須同時約束啟動成本、有效報價時間與每單 after-cost economics。 | 直接 |
| G47 | Loss-averse inventory accumulation；處理 state-aware resume、unresolved intent、release unit binding 與檔案權限事故。 | 策略語義與包裝/權限是兩條都可能讓 live 結果失真的鏈。 | 直接 |
| G48 | Adverse-selection-guarded profit capture。 | 減少 toxic fills 也會犧牲 fill rate；兩者要用同一個 after-cost objective 評估。 | 直接 |
| G49 | Bounded startup。 | 再次收斂 recovery 的時間、查詢與歷史掃描上限。 | 直接 |
| G50 | Continuous resume 與跨 episode 持續運行。 | 能連續恢復是一項工程成果，仍不是盈利證據。 | 直接 |

## G51–G53：從「做更多」轉向「證據到底能回答什麼」

| 代 | 公開可確認的經過 | 結果 / 學到的事 | 信心 |
|---:|---|---|---|
| G51 | 低延遲 pure-taker、streaming pre-trade、production shadow 與 forward calibration。 | Hot-path benchmark 可通過，但完整 round-trip cost 約一個數量級高於短週期訊號；候選被拒絕。 | 直接 |
| G52 | 五通道 public collector、sealed storage、typed attestation、lifecycle ledger、untouched after-cost policy 與 action-shadow preregistration。 | 大量 market rows 不是策略 observations；缺少完整 decision/attempt/outcome population，正期望狀態為 unavailable。 | 直接 |
| G53 | 回到 maker；public no-write shadow、activation-L2 capture、strict replay、Colab 模型比較、歷史資料研究與多次 live-continuation/reconciliation。 | Strict replay 35 次 activation 僅 4 次 usable，沒有正 hypothetical fill、markout、完整 reward 或 actual execution outcomes；live continuation 又暴露多重 state/packaging 問題。計畫暫停。 | 直接 |

## 這份時間線刻意沒有做的事

- 不把檔案存在、release 打包或 service active 說成成功交易。
- 不把 public trades 當 kaZe fills。
- 不把 hypothetical replay 當實盤績效。
- 不把通過工程測試說成策略有正期望。
- 不公開私人帳戶、逐筆交易、order identifiers、雲端拓撲或授權 receipts。
- 不替早期缺失的 G1–G15 補造技術故事。
