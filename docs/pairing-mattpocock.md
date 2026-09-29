# Ghép skill mattpocock vào khung

Khung này là **đường ray** (việc nằm ở đâu, kỷ luật thế nào).
Bộ skill [mattpocock/skills](https://github.com/mattpocock/skills) là
**đầu máy** (cách làm từng việc cụ thể). Bảng ghép:

| Skill | Vai trò trong khung | Output đặt ở đâu |
|---|---|---|
| `to-spec` | Biến conversation/request thành spec | Spec là plan → `docs/plans/active/` |
| `to-tickets` | Chia spec thành ticket có thứ tự | Trong cùng file plan |
| `wayfinder` | Plan việc rất dài, nhiều decision | `docs/plans/active/` + ADR khi chốt |
| `implement` | Thực thi theo spec/tickets | Luồng "Thay đổi bền vững có plan" |
| `diagnosing-bugs` | Chẩn đoán bug khó | Luồng read-only: chẩn đoán trước, không mặc nhiên được sửa |
| `code-review` | Review diff trước merge | Báo cáo review; findings fix theo luồng bounded change |
| `triage` | Phân loại issue/ticket | Quyết định triage ghi trong plan hoặc issue tracker |
| `research` | Research từ nguồn đáng tin | Kết quả link trong plan; thay vì đoán |
| `domain-modeling` | Làm rõ domain model / thuật ngữ | ADR trong `docs/decisions/` nếu là quyết định lasting |
| `resolving-merge-conflicts` | Gỡ conflict | Luồng bounded change |
| `grilling` | Stress-test một quyết định | Trước khi ghi ADR — quyết định đã qua grill thì vững hơn |
| `handoff` | Compact conversation cho agent khác | Kèm link tới plan hiện tại |
| `wizard` | Dẫn người qua bước chỉ họ làm được | Không thay runbook đã verify |
| `writing-for-agents` | Viết/sửa skill và AGENTS.md | Sửa đúng `AGENTS.md` / skill của repo |

## Nguyên tắc ghép

1. Skill quyết định **cách làm**; khung quyết định **output nằm ở đâu** và
   **chuẩn hoàn tất** (bằng chứng chạy được, không phải lời báo).
2. Quyết định lasting nảy sinh trong lúc dùng skill → promote thành ADR trong
   `docs/decisions/`, không để chôn trong chat.
3. Skill không thay thế ranh giới cấm của repo (`AGENTS.md` mục "Quy tắc bắt
   buộc") — ví dụ skill không cho phép tự tạo tag/release hay chạm production
   nếu repo cấm.
