---
name: architecture-map
description: "Tạo và cập nhật một file kiến trúc sống (thường docs/architecture.md hoặc docs/ARCHITECTURE.md) — freshness header, ranh giới hệ thống, authority model, runtime topology, entry points, component map, jump table, các luồng chính, và khi cần dùng thêm repository workflow, change-coupling guide, documentation map. Dùng skill này khi làm việc trên một repo lạ cần định hướng nhanh, khi user yêu cầu tài liệu hoá kiến trúc, luồng dữ liệu, hoặc quy trình đóng góp của repo, khi cấu trúc hoặc authority model vừa đổi, hoặc khi phát hiện đã có docs/architecture.md, ARCHITECTURE.md, docs/ARCHITECTURE.md hay docs/CODEMAPS/architecture.md cần refresh. Bao gồm template đầy đủ (assets/architecture-template.md) theo pattern của một architecture map chất lượng cao, nhiều lớp, nhiều nguồn authority. KHÔNG dùng để tạo CLAUDE.md/AGENTS.md, không tách sẵn backend.md/frontend.md riêng, và không viết map cho script hay throwaway."
disable-model-invocation: true
---

# Architecture Map

Một map kiến trúc sống giúp định hướng nhanh trong một repo lạ, thay vì phải
đoán tên file hay lục lọi từng thư mục. Nó khác với onboarding doc: đây là
cấu trúc hệ thống (ranh giới, authority, entry point, data flow), không phải
hướng dẫn "cách bắt đầu".

## Khi nào dùng

Dùng skill này khi:
- Bắt đầu làm việc sâu trên một repo lạ và cần một map định hướng nhanh, token-lean.
- User yêu cầu tài liệu hoá kiến trúc, authority model, luồng dữ liệu, hoặc quy trình đóng góp của repo.
- Cấu trúc repo hoặc mô hình authority vừa đổi (module mới, entry point mới, nguồn sự thật mới) và map cũ có thể sai.

Không dùng cho script một lần, tool nhỏ, hay throwaway code — chi phí duy trì map không đáng cho những thứ này.

## Việc cần làm

1. **Inventory trước khi tạo mới.** Tìm xem repo đã có `docs/architecture.md`, `ARCHITECTURE.md`, `docs/ARCHITECTURE.md`, hoặc `docs/CODEMAPS/architecture.md` chưa. Nếu có, cập nhật đúng file đó — không tạo file cạnh tranh.
2. **Nếu chưa có, tạo mới trong `docs/`.** Không thả file kiến trúc ở root repo.
3. **Đọc `assets/architecture-template.md` trước khi viết.** File đó chứa toàn bộ cấu trúc section theo đúng thứ tự và định dạng bảng đã chứng minh hiệu quả — đừng tự bịa cấu trúc mới mỗi lần.
4. **Chọn section theo mức độ phức tạp của repo** — xem bảng "Section nào luôn có" bên dưới. Đừng thêm section mở rộng chỉ để cho đủ bộ; mỗi section rỗng hoặc gượng ép làm giảm giá trị của cả file.
5. **Cập nhật khi structure/authority đổi.** Nếu diff sẽ lớn (nhiều phần bị viết lại), hỏi user trước khi ghi đè.
6. **Chỉ thêm 1 dòng signpost** trong `AGENTS.md` / `CLAUDE.md` — và chỉ khi file đó đã tồn tại sẵn. Đừng copy nội dung map vào đó.
7. **Verify mọi path trước khi giao.** Mọi đường dẫn file/thư mục nêu trong map phải tồn tại thật trong repo (kiểm tra bằng `ls` hoặc `git ls-files`) — path nào không verify được thì đánh dấu `unverified`, không đoán mò.

## Section nào luôn có, section nào mở rộng

| Section | Luôn có? | Khi nào thêm |
|---|---|---|
| Freshness header (`Last verified`) | Có | Luôn — không có freshness header thì map không đáng tin |
| System Purpose And Boundaries | Có | Luôn — kể cả phần "không làm gì" |
| Entry Points | Có | Luôn |
| Component Map | Có | Luôn |
| Jump Table | Có | Luôn — phần giá trị nhất cho người/AI mới vào repo |
| Ít nhất 1 Primary Flow | Có | Luôn — chọn luồng quan trọng nhất, không cần liệt kê hết |
| Authority Model | Mở rộng | Khi có ≥2 nguồn sự thật cạnh tranh (docs, code, tests, runtime state, plan file...) và dễ nhầm ai đúng |
| Runtime Topology (ASCII diagram) | Mở rộng | Khi runtime có nhiều lớp (interface/application/domain/infra) khó diễn tả bằng câu chữ |
| Persistence And Generated Data | Mở rộng | Khi state được lưu ở nhiều nơi cần một bảng tra cứu |
| Repository Workflow (Orient→Prepare→Implement→Validate→Complete) | Mở rộng | Khi repo có quy trình đóng góp/validate riêng ngoài git thường — ladder phân biệt theo *scope thay đổi*, không phải chỗ dump mọi lệnh lint/test có trong package.json |
| Change-Coupling Guide | Mở rộng | Khi sửa 1 thành phần thường kéo theo phải sửa thành phần khác |
| Documentation Map | Mở rộng | Khi repo có nhiều doc khác (`README`, `workflow/*`, `skills/*/SKILL.md`...) cần một chỗ tra ai sở hữu doc nào |

## Việc không làm

- Không generate `CLAUDE.md` / `AGENTS.md`.
- Không tách sẵn nhiều file (`backend.md`, `frontend.md`, codemap riêng) — giữ một file duy nhất, dùng section để chia.
- Không liệt kê rời rạc mọi lệnh test/lint vào Validate ladder — ladder chỉ có giá trị khi nó trả lời "sửa cái gì thì cần proof gì", không phải bản sao `package.json#scripts`.
- Không viết map cho script/throwaway.
- Không copy nội dung map vào `AGENTS.md`/`CLAUDE.md` — chỉ 1 dòng signpost trỏ tới.

## Nguyên tắc chung khi viết nội dung

- Đánh dấu rõ "unverified" ở bất kỳ phần nào chưa xác nhận trực tiếp trong source — một map sai còn tệ hơn không có map.
- Kết thúc bằng quy tắc giải quyết mâu thuẫn: khi các document/nguồn sự thật bất đồng, kiểm tra artifact nào *sở hữu* claim đang tranh chấp rồi verify lại với code/test/runtime/Git hiện tại — không để bản ghi cũ (plan cũ, checkpoint, memory) override sự thật hiện tại.

## Vị trí skill

Thư mục skill này — đặt cạnh các skill khác trong load path, dùng chung cho mọi repo, không riêng cho một dự án nào. Lý do skill này tồn tại: nỗi đau kiểu "không biết `ChatMessageItem.kt` liên quan gì tới `ActivityFeed`" xảy ra khi làm việc trên một codebase lạ nói chung — không phải vì thiếu docs trong một repo cụ thể.

## Impact / Recovery

- Nếu skill này không chạy: mất định hướng trong repo lạ, phải đoán tên file, tốn thời gian dò dẫm.
- Nếu map bị viết sai: xoá hoặc revert đúng 1 file kiến trúc và gỡ dòng signpost trong `AGENTS.md`/`CLAUDE.md` — rollback rẻ vì phạm vi thay đổi nhỏ.
- Rủi ro chính: map bị mục (lỗi thời) nếu không refresh sau khi structure/authority đổi. Luôn ghi rõ "unverified" khi không chắc, thay vì khẳng định sai.
