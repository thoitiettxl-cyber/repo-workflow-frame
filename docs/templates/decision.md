# NNNN Tiêu đề quyết định

Ngày: YYYY-MM-DD

Người quyết định: <tên/role người chốt>

## Trạng thái

Proposed | Accepted | Deprecated | Superseded (bởi ADR-NNNN) | Rejected

Vòng đời: `proposed → accepted → [deprecated | superseded]`.
Quyết định bị thay thế phải link tới ADR thay thế.

## Khi nào thì ghi ADR

Chỉ ghi ADR khi cả 3 điều đúng (gộp từ domain-modeling):

1. **Khó đảo ngược**: đổi ý sau này tốn kém đáng kể.
2. **Khó hiểu nếu thiếu ngữ cảnh**: người đọc tương lai sẽ hỏi "sao lại làm thế này?".
3. **Là kết quả của trade-off thật**: có phương án khác thật sự, đã chọn vì lý do cụ thể.

Thiếu 1 trong 3 → không ghi ADR, để trong plan file là đủ.

## Dấu hiệu nhận biết (gộp từ architecture-decision-records)

- Rõ ràng: "chốt dùng X", "chọn X thay vì Y vì...", "ghi lại quyết định này".
- Ngầm (đề xuất ghi, không tự tạo): so sánh 2 framework/library rồi chốt; chọn
  schema DB có lý do; chọn pattern kiến trúc; chốt chiến lược auth; chọn infra
  deploy sau khi đánh giá.

## Ngữ cảnh

Vấn đề, ràng buộc hay điểm mơ hồ nào buộc phải quyết? (2-5 câu: tình huống,
ràng buộc, các lực tác động.)

## Quyết định

Đã quyết gì? (1-3 câu, rõ ràng, thì hiện tại: "Dùng X", không phải "Sẽ dùng X".)

## Các phương án đã cân nhắc

### Phương án 1: <tên>

- **Ưu**: ...
- **Nhược**: ...
- **Vì sao loại**: <lý do cụ thể, không phải "tự nhiên chọn vậy">

### Phương án 2: <tên>

- **Ưu**: ...
- **Nhược**: ...
- **Vì sao loại**: ...

## Hệ quả

Được:

- ...

Đánh đổi:

- ...

Rủi ro:

- <rủi ro + cách giảm thiểu>

## Kỷ luật thuật ngữ (gộp từ domain-modeling)

Khi thảo luận, gọi tên ngay khi thuật ngữ vênh nhau ("glossary định nghĩa
'cancellation' là X, nhưng bạn đang dùng theo nghĩa Y — chốt nghĩa nào?"),
đề xuất từ chuẩn khi ngôn ngữ mơ hồ, và đối chiếu với code
("code cancel cả Order nhưng bạn nói partial được — cái nào đúng?").
Thuật ngữ đã chốt ghi vào plan file (mục Ngữ cảnh), không tạo file ngoài khung.

## ADR tốt

- Cụ thể ("Dùng Prisma ORM", không phải "dùng ORM"); ghi cái **tại sao**,
  quan trọng hơn cái gì; đọc xong trong 2 phút.
- Không ghi quyết định vặt (đặt tên biến, format); không viết luận văn
  (Ngữ cảnh quá 10 dòng là dài); quyết định cũ ghi bù thì nêu ngày gốc.

## Việc tiếp theo

- ...
