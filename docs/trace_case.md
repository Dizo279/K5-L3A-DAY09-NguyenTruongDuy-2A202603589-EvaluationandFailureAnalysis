# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case đã tái hiện: seeded_regression C-002@55

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@55`; bằng chứng JSON: `src/data/eval/trace_evidence/seeded_regression-C-002-s55.json` |
| Triệu chứng | Grader báo `status resolved != denied`; ledger hoàn 20.000đ, nhãn kỳ vọng 0đ/denied. Reply cũng thông báo đã hoàn 20.000đ. |
| Bước sai đầu tiên | Event 3 `model_override`: model ghi `delay_days=5`. |
| Vì sao là bước *đầu tiên* | Event 2 lookup DB đúng: order O-202 giao trễ 2 ngày. Event 3 thay dữ kiện đó; event 4 quote và event 6 reply tiếp tục dựa trên số ngày sai. |
| Failure mode | FM-03 `ticket_trust`. |
| Đối chứng | Cùng claim/seed với shape `fixed`: không có `model_override`, status và ledger khớp nhãn denied/0đ. |
| Regression test | `tests/test_lab9_trace_case.py::test_ticket_trust_trace_is_regression_and_fixed_control_passes`; kiểm tra event override, status và ledger ở variant lỗi lẫn fixed. |
| Chưa chắc chắn | Case xác nhận đường lỗi này trên MockLLM/seed 55; không ước lượng tần suất trên model hoặc traffic thật. |

Tạo lại bằng `python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 55 --out data/eval/trace_evidence/seeded_regression-C-002-s55.json`.

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
