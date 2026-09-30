# Execution Plan: <tiêu đề>

Ngày: YYYY-MM-DD

## Trạng thái

Active | Blocked | Completed

## Outcome

Kết quả quan sát được mà việc này phải tạo ra.

## Ngữ cảnh

Link tới product, kiến trúc, decision, code và validation liên quan.

## Phạm vi

Trong phạm vi:

- ...

Ngoài phạm vi:

- ...

## Cách làm

Chuỗi bước nhỏ nhất thành một khối coherent. Cập nhật khi bằng chứng làm
đổi cách làm.

## Rủi ro và khôi phục

- Rủi ro và cách giảm thiểu.
- Quy trình recovery/rollback.

## Tiến độ

- [ ] Bước...

## Quyết định

- YYYY-MM-DD: quyết định cục bộ trong lúc làm + lý do.
- Decision có dùng `judge` (typed): ghi thêm `choice` + `confidence`
  (vd: `choice: A — dùng plan file; confidence: 0.9`) để không mất dữ liệu typed.

Promote quyết định lasting về sản phẩm/kiến trúc thành ADR trong
`docs/decisions/`.

## Validation

- Proof focused:
- Proof integration hoặc end-to-end:
- Check bắt buộc của repo:

## Kết quả

Ghi sau khi implement: outcome đã verify, giới hạn, việc tiếp theo — rồi
move plan sang `docs/plans/completed/`.
