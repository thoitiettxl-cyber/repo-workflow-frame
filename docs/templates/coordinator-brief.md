# Coordinator Brief Template

Mỗi chiến dịch subagent copy brief này vào `brief/BRIEF.md` của campaign-plan,
điền các mục [ĐIỀN], rồi mới spawn coordinator. Các mục luật đứng không sửa
khi copy.

## Mở đầu: campaign-plan trong repo (luật đứng)

Mọi chiến dịch mở một campaign-plan trong repo TRƯỚC KHI dispatch worker đầu
tiên — không chạy campaign "ngoài harness" (bài học 2026-10-04: 3 chiến dịch
chạy bằng brief/report riêng ngoài `docs/plans/` → 2 nguồn sự thật song song).

Layout (`<repo>/docs/plans/active/<slug>/`):

- `PLAN.md` — outcome, danh sách batch, nhật ký tiến độ (mục 2 ghi vào đây),
  quyết định. Dùng `docs/templates/exec-plan.md` làm khung.
- `brief/BRIEF.md` — bản brief đã điền (copy từ template này).
- `batches/` — `<batch>-<role>-result.md`, `<batch>-fable-check.md` (chỉ khi
  có finding). Là audit trail → commit vào repo.
- `scratch/` — file transient (edit-script, log nháp); gitignored, không commit.
- `REPORT.md` — viết khi chiến dịch xong; rồi move cả thư mục sang
  `docs/plans/completed/`.

Ngoại lệ: việc cross-repo/meta (không thuộc về repo nào cụ thể) mới dùng
`~/workspace/workflow-runs/`.

## 0. Kênh kết quả: FILE là chính, handoff chỉ là chuông báo

Handoff giữa các agent có thể mất do lỗi runtime (đã xảy ra 3 lần trong một
chiến dịch, 2026-10-02). Thiết kế này coi handoff là best-effort:

- Mọi worker, TRƯỚC KHI kết thúc, phải ghi kết quả cuối ra file
  `batches/<batch>-<role>-result.md` (vd `batches/batch2-writer-result.md`).
  Nội dung: đã làm gì, file nào đổi, diff tóm tắt, verdict/kết luận, việc còn dở.
- Coordinator KHÔNG BAO GIỜ chờ handoff để lấy kết quả — đọc FILE.
- Worker xong việc mà chưa ghi file = coi như chưa xong.

## 1. Tự đánh thức khi worker xong (KHÔNG trông chờ handoff runtime)

Handoff runtime đã chứng minh mất tin (2026-10-03: 8/8 completion messages
`delivered_at=null` trên coordinator contradiction-sweep, truy vết bằng
`muse.db`). Quy tắc:

- Worker "POST" bằng cách ghi file `*-result.md` vào `batches/` (filesystem
  chính là API — không cần HTTP server riêng).
- Sau khi dispatch worker, coordinator chạy background exec để tự đánh thức:
  `~/workspace/repo-workflow-frame/scripts/campaign-wait.sh <campaign-dir>/batches 600 [--expect f1,f2] [--count N]`
  (background — runtime giao kết quả exec về sẽ đánh thức coordinator khi có
  file mới/sửa, hoặc hết 600s). KHÔNG ngồi chờ handoff. (Script watch
  non-recursive: trỏ đúng vào `batches/`.)
  - `--expect`: liệt kê đúng file result mong đợi (vd `--expect b4d-writer-result.md`)
    → chỉ wake trên file đó, tránh wake giả; file nào đã "tươi" (<300s) lúc arm
    thì báo ngay (đóng race worker viết xong trước khi waiter snapshot).
  - `--count N`: dispatch nhiều worker thì đợi đủ N file mới wake một lần.
  - Re-dispatch cùng tên file: xóa/đổi tên file cũ trước khi dispatch lại.
- Khi được đánh thức: đọc result file → tiếp tục batch. Hết timeout mà chưa
  có file → kiểm tra worker một lần theo checklist cũ bên dưới rồi arm lại.

Checklist khi phải kiểm tra thủ công (dự phòng):

1. `subagent.list` xem trạng thái worker.
2. Worker `done` → đọc result file. Có file → tiếp tục. Không file → worker
   chết trước khi ghi, dispatch lại phần việc.
3. Worker `interrupted`/`failed` → đọc file (nếu có) rồi dispatch lại phần
   còn thiếu.
4. Worker vẫn `running` nhưng im lặng → `subagent.send` nudge một lần; thêm
   10 phút vẫn im thì đánh giá lại (kill + dispatch lại nếu cần).

Không chờ mù quá 10 phút trong bất kỳ trường hợp nào.

## 2. Nhật ký tiến độ (để root resume khi coordinator chết)

Sau MỖI batch, coordinator append vào mục Tiến độ trong `PLAN.md`:
thời gian, batch, SHA commit, CI run id + trạng thái, verdict review.
Coordinator chết giữa chừng (runtime hiccup) → root đọc `PLAN.md` là
biết đang ở đâu, không dựng lại từ chat.

## 3. Batch idempotent

Đầu mỗi batch: `git log` + `git status` + check remote. Việc nào xong rồi
(commit đã có, CI đã xanh) thì bỏ qua, không làm lại. Dispatch lại worker
không bao giờ gây trùng việc.

## 4. Kỷ luật edit → review

- Worker KHÔNG tự sửa file: nộp edit-script → coordinator chạy
  `preflight-edit check --cwd <repo>` → pass mới `apply`.
- Sau apply: reviewer fresh-eyes (khác writer) soi diff theo skill
  `review-loop`: rubric chung + `REVIEW_GUIDELINES.md` (fallback `REVIEW.md`)
  ở repo root; verdict `correct`/`needs attention`; blocking
  (`[P0]/[P1]/[P2]`) → writer fix theo Fix Queue, tối đa 3 pass; hết pass
  vẫn blocking → dừng, báo Boss.
- Reviewer phải verify API/framework lạ qua source-jar, docs chính thức hoặc
  Context7 — không tin lời writer hay trí nhớ training
  (bài học `LocaleList.getEmpty()`, 2026-10-02).
- Mỗi batch một writer tại một thời điểm. Chỉ commit khi review approve.
  Mọi commit local; push/PR/dispatch workflow chỉ khi Boss lệnh rõ.
- Sau `git add`, trước `git commit`: chạy `scripts/githooks/stamp.sh` để đóng
  dấu staged diff (pre-commit hook verify; enforcing mode chặn commit không dấu).
  Worker KHÔNG BAO GIỜ dùng `git commit --no-verify`.
- **Thanh kiểm duyệt cực nghiêm (mặc định từ 2026-10-05, Boss duyệt):** reviewer
  áp dụng `review-loop` §8 — API phải có citation (không bịa), comment khớp code
  1-1, literal chính xác từng ký tự, không code chết; reviewer verify độc lập,
  không tin lời writer. Brief chiến dịch nào muốn hạ thanh phải ghi rõ lý do và
  được Boss duyệt — reviewer không bao giờ tự hạ.
- CI đỏ → writer fix, nhưng phân biệt (bài học hma-essence B4, 2026-10-04):
  **cùng 1 lỗi đỏ 3 lần liên tiếp** → DỪNG, báo root/Boss ngay (going nowhere,
  cấm attempt thứ 4 y hệt). **Mỗi lần 1 lỗi khác nhau** → được tiếp tục fix
  (đó là tiến triển, không phải kẹt), nhưng mỗi attempt phải ghi chú
  "lỗi cũ → lỗi mới" vào nhật ký batch. Trần cứng: 5 attempt/batch —
  quá thì dừng, báo root/Boss.
- "Báo root/Boss" = **ghi file** `batches/<batch>-escalation.md` (trạng thái
  batch, lỗi từng attempt, chẩn đoán của coordinator, đề xuất) TRƯỚC khi báo
  bằng lời — báo miệng không tính. Root/Boss **đọc file xong mới quyết định**,
  không hành động chỉ dựa vào preview hay chẩn đoán riêng
  (bài học hma-essence B4, 2026-10-04: coordinator báo miệng, root fix theo ý
  mình mà chưa đọc báo cáo — bước escalation thành diễn).

## 5. Watchdog cron (dự phòng, root tạo trong chat của chiến dịch)

- Job id: `campaign-watchdog-<campaign-id>`; owner: `goal:<goal-slug>`;
  schedule: interval 15 phút; delivery: chat của chiến dịch.
- Mỗi lần chạy: `git log --since="35 minutes ago"` trên nhánh chiến dịch +
  `gh run list` xem CI. Có commit mới HOẶC có CI đang chạy → im lặng.
  Không commit mới VÀ không CI nào chạy → báo vào chat để root kiểm tra
  coordinator (có thể đang kẹt chờ handoff mất).
- Chiến dịch xong → root xóa cron ngay.

---

## 6. Fable-check sau mỗi batch (completion honesty — bài học agent-stack 4 tầng, Boss duyệt 2026-10-03)

Reviewer fresh-eyes (review-loop) soi DIFF — đúng code chưa. Fable-check soi
CLAIM — batch có thực sự xong không. Hai lớp độc lập, không thay nhau. Chạy
TRƯỚC khi commit batch, theo checklist:

1. Result file của batch tồn tại và liệt kê **evidence cụ thể** (SHA commit /
   đường dẫn file / output test) — không chấp nhận claim bằng chữ suông.
2. Mỗi acceptance criterion trong batch contract map được tới 1 artifact cụ thể.
3. Mục nào **skipped** phải liệt kê tường minh + lý do (câu hỏi "anything skipped?").
4. Batch trước fail thì failure lần này có **khác** failure lần trước không?
   Giống hệt 2 lần liên tiếp → "going nowhere": CẤM retry y hệt, phải đổi cách
   (redispatch worker khác / đổi chiến thuật / escalate lên root).
5. **Im lặng khi tất cả pass** — chỉ ghi finding khi có vấn đề (kỷ luật
   "says nothing unless it's actually wrong").

Cách làm mặc định: coordinator tự chạy checklist (inline, cost ~0). Chiến dịch
lớn/nhiều batch: spawn 1 checker fresh-eyes riêng (tránh bias coordinator tự
kiểm tra việc mình điều phối). Finding ghi vào `batches/<batch>-fable-check.md`
— chỉ tạo file khi có finding, pass thì im lặng.

---

## 7. Smoke test chuyên sâu cho chiến dịch thêm script/tool

(Bài học chiến dịch ghidra 2026-10-06: 5 script headless mới — smoke test phát
hiện 1 bug crash thật (`AddressFactory.getAddress()` trả `null` chứ không
throw → NPE mất output) và 1 bug wrapper (unquoted args expansion làm quote
lọt vào regex → example SKILL.md sai thầm lặng). Cả hai chỉ lộ ra nhờ edge
cases + persistence, happy path không bắt được.)

Checklist 4 lớp, chạy trên binary/input thật, mỗi claim kèm evidence
(log/output trích — không chấp nhận "chạy được" bằng lời):

1. **Happy path** — mỗi script/tool mới chạy thành công, output đúng schema,
   giá trị đúng (rename → đọc lại thấy tên mới; comment → read-back verified).
2. **Edge cases** — input sai phải báo lỗi RÕ RÀNG, KHÔNG crash, exit code hợp
   lý: địa chỉ không tồn tại, args thiếu/sai format, regex lỗi, range đảo
   ngược, enum/type không hợp lệ. Đặc biệt: API nào **"trả null thay vì
   throw"** thì bắt buộc null-check + message nêu rõ input lỗi.
3. **Persistence** (nếu tool có state) — state ghi ở run N phải còn ở run N+1
   (project kept, DB, file). Lớp này đã phát hiện wrapper silent-fail
   (exit 0 trong khi import conflict, không output).
4. **Regression** — chạy lại ít nhất 1 script/tool cũ → behavior không đổi;
   checksum baseline các file cũ trước/sau phải khớp (trừ phần append có chủ ý).

- Chạy tuần tự nếu VM yếu (bài học: >2 `analyzeHeadless` song song trên VM
  7.7Gi RAM → OOM kill exit 137).
- Bug tìm được → 1 file trong `~/workspace/bug-patterns/` ngay (theo
  `RULES.md`), fix qua vòng edit→review như batch thường; gate phase tiếp
  theo chỉ mở khi hết bug crash.

---

## [ĐIỀN] Thông tin chiến dịch

- Campaign id / plan slug:
- Goal slug:
- Repo + nhánh:
- Các batch (mỗi batch: mục tiêu, file được phép đụng, non-goals, acceptance):
- Tiêu chí hoàn thành chiến dịch:
