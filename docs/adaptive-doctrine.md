# Học thuyết thích nghi (Adaptive Doctrine)

> Thực tế đứng trên tài liệu. Khi nền tảng, runtime hay công cụ không làm
> đúng như nó hứa, đừng ngồi chờ bản fix chính thức — hãy tự tiến hoá.

Học thuyết này áp dụng cho mọi dự án dùng khung: nó là cách khung tự sửa
mình khi thế giới bên ngoài không hợp tác.

## 1. Nguyên tắc

1. **Không trông chờ upstream.** Lỗi runtime / nền tảng / công cụ là việc của
   họ; tiến độ của bạn là việc của bạn. Workaround là của mình, mình tự tiến
   hoá nó.
2. **Workaround tối thiểu có thể.** Đủ để việc chạy tiếp, không hơn. Phức tạp
   hoá workaround là tạo nợ mới.
3. **Coi workaround như code của mình.** Nó cần test, cần review, cần tiến hoá
   — không phải miếng vá tạm "để đó rồi quên".
4. **Ghi lại mọi thứ.** Cái gì hỏng, mình đã giả định gì, workaround làm gì,
   giới hạn đã biết của nó. Người sau (hay session sau) phải tìm thấy trong
   repo, không phải trong đoạn chat đã trôi.
5. **Promote dần dần.** Quan sát trước (warn / log-only), enforce sau — chỉ
   khi đã chứng minh qua chạy thật không false positive. Smoke test trên task
   nhỏ nhất trước khi thành mặc định.

## 2. Vòng tiến hoá (sau mỗi lần chạy)

Áp dụng cho mọi workflow, script, hook, cơ chế tự chế:

1. **Thu hoạch:** lần chạy vừa rồi lộ điểm yếu gì — kể cả khi thành công.
2. **Ghi:** vào "Bài học đã trả giá" (AGENTS.md) / `docs/patterns/` +
   CHANGELOG của công cụ liên quan.
3. **Sửa:** update workaround / workflow.
4. **Smoke test:** chạy thử trên task nhỏ nhất.
5. **Promote:** chỉ khi pass mới thành chuẩn.

## 3. Ví dụ

- **Runtime mất handoff:** 8/8 completion message không tới được. Không chờ
  team nền tảng — dùng filesystem làm API (worker ghi file kết quả,
  coordinator tự đánh thức qua exec-completion). Sau mỗi chiến dịch audit
  script và cải tiến (đóng race, đếm đủ file, fail-fast đúng path).
- **Gác cổng pre-commit:** luật "không tự sửa file" chỉ nằm trong brief thì
  vẫn bị lén qua. Lắp hook thật nhưng chạy `warn` trước (chỉ log), lên
  `enforcing` khi pipeline đã chứng minh không false positive.
- **Docs bị gitignore nuốt:** khung yêu cầu check `git check-ignore` trước khi
  viết plan/ADR — vấn đề của nền tảng (git) được khung thích nghi bằng một
  check cơ học, không phải bằng lời nhắc.

## 4. Anti-patterns

- "Để đó, chờ bản fix chính thức" — trong khi việc đứng im.
- Workaround không ai ghi lại — vài tuần sau không ai nhớ vì sao nó tồn tại.
- Enforce ngay từ ngày đầu — false positive chặn việc thật, mất niềm tin vào
  chính cơ chế bảo vệ.
- Vá triệu chứng thay vì cơ chế — cùng một lỗi quay lại dưới hình thức khác.
- Trông chờ "ai đó" cải tiến workaround — người chịu trách nhiệm là người
  đang dùng nó.
