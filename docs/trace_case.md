# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case đã audit (`seeded_regression C-002@11`)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261118-3305` |
| Triệu chứng | `lab8 grader` (`pass_rate`), `db_fact_kept`, `refund_amount_correct` fail (`status resolved != denied`); reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` trong khi nhãn yêu cầu `denied`, `refund_vnd=0`, `refund_count=0`, còn ledger thực tế ghi `refund_vnd=20000`, `refund_count=1` |
| Bước sai đầu tiên | Event `3` `model_override` — `{"delay_days": 5}` (dùng số ngày trễ từ ticket thay cho `delay_days: 2` trong DB) |
| Vì sao là bước *đầu tiên* | Event `1` (`handoff`) giao đúng `principal_scope: "owner_order_only"` và `allowed_tools` hợp lệ; Event `2` (`investigator`) truy vấn `lookup_order` trả đúng bản ghi DB (`O-202`, `status: "delivered"`, `delay_days: 2`). Đến trước event `3`, toàn bộ dữ kiện đều chính xác |
| Failure mode | `FM-03` (`ticket_trust`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên `fixed C-002@11`: không có event `model_override`; ngay sau event `2` (`investigator`), event `3` (`quote`) dùng `delay_days=2` của DB ra `{"amount_vnd": 0, "reason": "no_entitlement"}`, event `4` (`reply`) trả `status=denied` và `refund_vnd=0` |
| Regression test | `test_trace_case_c002_seed11_regression` trong `src/tests/test_lab9_regression.py` kiểm tra `DbFactKept` và `RefundAmountCorrect`; đã xác nhận FAIL trên `seeded_regression` và PASS trên `fixed` |
| Chưa chắc chắn | Trace dùng `MockLLM`; chưa chứng minh được khi thay bằng LLM thật với cách diễn đạt ticket tự nhiên hơn thì prompt/ràng buộc hiện tại có ngăn được việc mô hình tự suy diễn `delay_days` hay không |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
