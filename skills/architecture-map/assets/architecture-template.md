# Architecture, Repository Workflow, And Documentation Map
> Last verified: <YYYY-MM-DD> — inspected current `<key dirs/files, vd: src/, package.json, skills/, AGENTS.md>`.

This document is the contributor-facing map for `<repo/package name>`.
`<AGENTS.md hoặc CLAUDE.md>` is the compact entrypoint; this file explains how
the repository is structured, where authority lives, how work moves through
the repository, and which documents must change together.

## System Purpose And Boundaries

<Mô tả ngắn gọn hệ thống làm gì — liệt kê các capability/component chính nếu
có nhiều (đánh số). Nêu rõ boundary: hệ thống KHÔNG làm gì / không thay thế
cái gì, để người đọc không hiểu lầm phạm vi.>

## Authority Model
*(Mở rộng — chỉ thêm khi có ≥2 nguồn sự thật có thể mâu thuẫn: docs, code,
tests, runtime state, plan file, config...)*

Different artifacts answer different questions:

- `<artifact A>` defines <câu hỏi nó trả lời, vd "what work is allowed">.
- `<artifact B>` is the system of record for <loại sự thật, vd "product/task truth">.
- `<artifact C>` owns <phạm vi hẹp hơn, vd "install/release contract">.
- <thêm artifact khác nếu cần>

Một câu chốt: khi hai artifact mâu thuẫn, artifact nào thắng và tại sao.

## Runtime Topology
*(Mở rộng — chỉ thêm khi luồng runtime có nhiều lớp, khó diễn tả bằng câu chữ)*

```text
<entry point: event/request/command>
            |
            v
    <composition root>          <vai trò: nơi wiring, policy>
       |        |        |
       v        v        v
  <layer 1>  <layer 2>  <layer 3>     <vd: interface / domain / infra>
```

<1-2 câu nêu rule của từng layer, vd "domain phải pure/deterministic và
testable; side effect (filesystem, network, DB) chỉ nằm ở boundary/infra">.

## Entry Points

| Surface | Path |
|---|---|
| <tên entry point, vd "Extension registration"> | `<path>` |
| <tên entry point khác> | `<path>` |

## Component Map

| Area | Responsibility | Key files |
|---|---|---|
| <tên component> | <trách nhiệm, 1 câu ngắn> | `<path>` |

## Jump Table

| Want to… | Go to | Verify with |
|---|---|---|
| <việc người đọc muốn làm> | <section hoặc file liên quan> | `<cách verify — file test, lệnh chạy, path cụ thể>` |

Đây thường là phần giá trị nhất cho người/AI mới vào repo — ưu tiên đầu tư ở
đây trước các section mở rộng bên dưới.

## Primary Runtime Flows
*(Chọn 1–3 luồng quan trọng nhất; không cần liệt kê mọi luồng có thể)*

### <Tên luồng, vd "Session Startup And Recovery">

1. <bước 1 — file/hàm cụ thể chịu trách nhiệm>
2. <bước 2>
3. <bước 3 — điểm cần chú ý, edge case quan trọng>

## Persistence And Generated Data
*(Mở rộng — chỉ thêm khi state được lưu ở nhiều nơi khác nhau)*

| Data | Default location or owner | Authority |
|---|---|---|
| <tên data> | `<path/location>` | <ý nghĩa/thẩm quyền của data này> |

## Repository Workflow
*(Mở rộng — chỉ thêm khi repo có quy trình đóng góp riêng ngoài git thường,
vd durable task tracking, managed validation. Đây không phải chỗ liệt kê hết
mọi lệnh lint/test có trong package.json — chỉ đưa vào khi nó thực sự phân
biệt "sửa loại gì thì cần loại proof gì".)*

### 1. Orient
- <việc cần đọc/kiểm tra trước khi bắt đầu>

### 2. Prepare By Work Shape

| Shape | Repository document | Rule |
|---|---|---|
| Read-only | None | <rule> |
| <shape khác, vd "Durable mutation"> | <doc cần tạo/bind> | <rule> |

### 3. Implement
- <nguyên tắc code/style/layering cần giữ nguyên>

### 4. Validate

| Change scope | Minimum focused proof | Broader gate when applicable |
|---|---|---|
| <loại thay đổi> | <proof tối thiểu> | <gate rộng hơn khi cần> |

### 5. Complete And Deliver
- <điều kiện coi là xong; ai được phép commit/push/deploy>

## Change-Coupling Guide
*(Mở rộng — chỉ thêm khi sửa 1 thành phần thường kéo theo phải sửa thành phần khác)*

| If changing… | Inspect or update together | Required proof emphasis |
|---|---|---|
| <thành phần> | <những gì cần soát lại cùng lúc> | <proof cần nhấn mạnh> |

## Documentation Map
*(Mở rộng — chỉ thêm khi repo có nhiều doc khác cần một chỗ tra ai sở hữu gì)*

| Document | Audience and ownership |
|---|---|
| `<path>` | <ai đọc, ai sở hữu nội dung> |

---

Khi các document mâu thuẫn nhau: kiểm tra artifact nào sở hữu claim đang
tranh chấp, rồi verify lại với code, test, runtime, và Git hiện tại. Không để
một plan cũ, kết quả release cũ, checkpoint, hay memory record nào override
sự thật hiện tại của repo.
