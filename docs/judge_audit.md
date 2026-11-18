# Judge audit

Chạy:
```bash
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (κ=0.757, P=0.857, R=0.800) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không (κ=0.375 < 0.6, R=0.300 < 0.7) | loại |

- `tone_ok` confusion matrix: `{'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66}`; observed fail rate `0.28` → Rogan-Gladen corrected `0.30`.
- `helpful` confusion matrix: `{'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}`; observed fail rate `0.09` → Rogan-Gladen corrected `0.30`.

## ≥5 case audit thủ công (`tone_ok` + đối chiếu `helpful`)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) | PASS | FAIL | Người đúng | `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` — xưng `'em' + 'nha'` quá suồng sã; judge nhầm là thân thiện |
| 2 | `H-017` (`tone_ok`) | PASS | FAIL | Người đúng | `"Dạ, bạn ơi LogiX đã hoàn 25.000đ..."` — xưng `'bạn'` với khách hàng; judge bỏ sót |
| 3 | `H-029` (`tone_ok`) | PASS | FAIL | Người đúng | `"...không cần nhắn thêm."` — giọng ra lệnh; judge bị đánh lừa bởi cụm `"Dạ, vui lòng"` |
| 4 | `H-042` (`tone_ok`) | FAIL | PASS | Người đúng | `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` — ngắn nhưng đủ ý và lịch sự; judge phạt oan vì thiếu lời xin lỗi |
| 5 | `H-051` (`tone_ok`) | FAIL | PASS | Người đúng | `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` — dùng từ `"refund"` được CS LogiX cho phép; judge phạt vì xen tiếng Anh |
| 6 | `HL-015` / `HL-016` (`helpful`) | PASS | FAIL | Người đúng | Judge chỉ thấy lời văn xin lỗi dài và lịch sự nên chấm PASS, bỏ sót việc reply báo `55.000đ` trong khi ledger ghi `40.000đ` (`HL-015`) và `35.000đ` (`HL-016`) |

## Kết luận
- **Tiêu chí bị loại:** `helpful` bị loại vì `κ = 0.375` (< 0.6) và `Recall = 0.300` (< 0.7). Theo ma trận nhầm lẫn (`fn = 21` trên tổng `30` ca FAIL thực tế), judge bỏ lọt tới 70% ca lỗi — chủ yếu là các reply văn phong rất lịch sự nhưng **báo sai số tiền so với ledger** (`HL-015`, `HL-016`, `HL-020`, `HL-028`, `HL-035`, ...) hoặc sai xưng hô. Điều này khẳng định lại quy tắc: tiền phải chấm bằng code (`ReplyMatchesLedger` / `RefundAmountCorrect`), không dùng judge.
- **Rủi ro còn lại:** `tone_ok` chỉ được kiểm trên dữ liệu replay đã công khai (`judge_tone_public.csv`); cần nhãn người mới để có tập held-out thật, và vẫn cần rà lại nhãn mẫu (`H-081` nhãn người đọc nhầm ticket).
