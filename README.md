# repo-workflow-frame

Khung workflow mặc định cho agent làm việc trong một repo: `AGENTS.md` +
`docs/WORKFLOW.md` + `docs/plans/` + `docs/decisions/`.

## Khung này là gì

Một repo mà agent (người hoặc AI) cùng làm việc lâu dài cần ba thứ:

1. **Điểm vào duy nhất** — `AGENTS.md`: agent mở repo là biết đọc gì trước,
   ranh giới thẩm quyền ở đâu, kỷ luật làm việc ra sao.
2. **Cách chọn hình thức việc** — `docs/WORKFLOW.md`: việc nào làm trực tiếp,
   việc nào cần plan bền vững, khi nào phải dừng hỏi người, cái gì chứng minh
   hành vi, invariant nào phải giữ.
3. **Trí nhớ bền vững** — `docs/plans/` cho việc nhiều session, `docs/decisions/`
   (ADR) cho quyết định kiến trúc. Session sau đọc lại là tiếp tục được, không
   phụ thuộc vào context chat.

## Triết lý: "đường ray + đầu máy"

- **Khung này là đường ray**: nó quy định việc nằm ở đâu, kỷ luật thế nào,
  chuẩn hoàn tất ra sao. Nó không dạy cách làm từng việc cụ thể.
- **Skill là đầu máy** chạy trên đường ray đó: ví dụ bộ skill
  [mattpocock/skills](https://github.com/mattpocock/skills) (`to-spec`,
  `implement`, `code-review`, `diagnosing-bugs`...) dạy *cách làm* từng việc;
  output của chúng được đặt đúng chỗ mà khung quy định
  (xem `docs/pairing-mattpocock.md`).

Đường ray không thay đầu máy, đầu máy không thay đường ray.

## Cấu trúc

```
AGENTS.md                     # điểm vào: khối HARNESS + quy tắc riêng của repo
docs/
├── WORKFLOW.md               # cách chọn hình thức việc, task flows, chuẩn hoàn tất
├── README.md                 # bản đồ docs
├── plans/
│   ├── active/               # plan đang làm (1 việc = 1 file)
│   └── completed/            # plan đã xong + verify
├── decisions/                # ADR đánh số (0001-...)
├── templates/
│   ├── exec-plan.md          # mẫu plan
│   └── decision.md           # mẫu ADR
├── patterns/
│   └── encoding-invariants.md # pattern mã hóa invariant thành check cơ học
└── pairing-mattpocock.md     # bảng ghép skill mattpocock vào khung
scripts/
└── install.sh                # dựng khung vào repo bất kỳ
```

## Dùng nhanh

Dựng khung vào một repo có sẵn (idempotent — chạy nhiều lần an toàn):

```bash
./scripts/install.sh /đường/dẫn/tới/repo
```

Script sẽ tạo cây `docs/{plans/{active,completed},decisions,templates,patterns}`,
copy các mẫu vào; với `AGENTS.md`: chưa có thì tạo từ mẫu, có rồi thì chỉ
prepend khối HARNESS (không ghi đè nội dung cũ).

Sau đó tùy biến:

1. Điền các placeholder `[ĐIỀN]` trong `docs/WORKFLOW.md` (nguồn verify của
   repo bạn là gì? ranh giới cấm nào?).
2. Viết quy tắc riêng của repo vào `AGENTS.md` dưới khối HARNESS.
3. Việc đầu tiên kéo dài nhiều session → tạo plan theo
   `docs/templates/exec-plan.md`.

## Kỷ luật cốt lõi (tóm tắt)

- Mơ hồ về product/policy → dừng, hỏi quyết định nhỏ nhất. Không tự bịa.
- Báo xong chỉ với bằng chứng chạy được hoặc quan sát được (test/CI/log).
  Mô tả không thay thế bằng chứng.
- Việc vặt một lần thì khỏi dựng plan — overhead không đáng.

Chi tiết đầy đủ ở `docs/WORKFLOW.md`.

## Nguồn gốc & License

Khung này được chuyển thể (adapt) từ
[repository-harness](https://github.com/hoangnb24/repository-harness)
của hoangnb24 (MIT), viết lại theo cấu trúc và kinh nghiệm vận hành thực tế.

MIT License — xem `LICENSE`.
