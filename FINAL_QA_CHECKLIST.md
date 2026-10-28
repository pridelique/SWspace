# FINAL QA CHECKLIST — SWspace

ใช้เป็น checklist สำหรับกรรมการนักเรียนทดสอบระบบก่อน launch

---

## 1. Project Setup

- [ ] `pip install -r requirements.txt` สำเร็จ ไม่มี error
- [ ] `python manage.py migrate` สำเร็จ ไม่มี error
- [ ] `python manage.py create_test_accounts` สร้างบัญชีทดสอบได้ถูกต้อง
- [ ] `python manage.py runserver` เปิดได้ที่ http://127.0.0.1:8000/
- [ ] `/` redirect ไป `/dashboard/` (ต้อง login ก่อน → redirect ไป login)
- [ ] Static CSS โหลด (navbar, ปุ่ม, ตาราง แสดงผลถูกต้อง)

---

## 2. Registration

- [ ] สมัครด้วยรหัส committee (ผู้ดูแลแจ้ง) → role=committee
- [ ] สมัครด้วยรหัสผิด → แสดง error ไม่สร้างบัญชี
- [ ] สมัครด้วย email ที่ไม่ใช่ @satriwit.ac.th → แสดง error
- [ ] สมัครด้วย email ซ้ำ → แสดง error
- [ ] สมัครด้วย password ไม่ตรงกัน → แสดง error
- [ ] สมัครสำเร็จ → redirect ไป /dashboard/

---

## 3. Login / Logout

- [ ] login ด้วย credential ถูกต้อง → redirect ไป /dashboard/
- [ ] login ด้วย password ผิด → แสดง error อยู่หน้าเดิม
- [ ] login ด้วย email ที่ไม่มีในระบบ → แสดง error
- [ ] login แล้ว GET /accounts/login/ → redirect ไป /dashboard/
- [ ] login แล้ว GET /accounts/register/ → redirect ไป /dashboard/
- [ ] `?next=/news/` หลัง login → redirect ไป /news/
- [ ] `?next=https://evil.com` หลัง login → redirect ไป /dashboard/ (ไม่ตาม)
- [ ] POST /accounts/logout/ → redirect ไป /accounts/login/
- [ ] GET /accounts/logout/ (ไม่ใช่ form) → redirect ไป /dashboard/

---

## 4. Dashboard

- [ ] นักเรียน: เห็น dashboard, ไม่เห็น "Committee Dashboard" badge
- [ ] committee: เห็น "Committee" badge และลิงก์ Committee Dashboard
- [ ] ลิงก์ Roomsible เปิด https://roomsible.vercel.app/ ในแท็บใหม่

---

## 5. ข่าวสาร (News)

- [ ] /news/ แสดงข่าวที่ is_published=True
- [ ] ข่าวที่ is_published=False ไม่แสดง
- [ ] filter ตามหมวดหมู่ (ภายใน / ภายนอก / ประชาสัมพันธ์) ทำงาน
- [ ] [Committee] สร้างข่าวพร้อมรูป JPG → บันทึกและแสดงรูป
- [ ] [Committee] สร้างข่าวพร้อมรูป PNG → บันทึกและแสดงรูป
- [ ] [Committee] สร้างข่าวไม่มีรูป → บันทึกได้
- [ ] [Committee] แก้ไขข่าว → บันทึกได้
- [ ] [Committee] ลบข่าว → ยืนยันแล้วลบจริง

---

## 6. จิตอาสา (Volunteer Links)

- [ ] /volunteer/ แสดงกิจกรรมที่ is_published=True
- [ ] ลิงก์ภายนอกเปิดได้
- [ ] deadline แสดงวันที่ถูกต้อง
- [ ] [Committee] สร้าง / แก้ไข / ลบ → ทำงานได้
- [ ] [Committee] ตั้ง deadline ผ่าน date picker → บันทึกวันที่ถูกต้อง

---

## 7. การแข่งขัน (Competitions)

- [ ] /competitions/ แสดงรายการที่ is_published=True
- [ ] [Committee] สร้างพร้อมรูป WEBP → บันทึกและแสดงรูป
- [ ] [Committee] สร้างพร้อม application_url → ลิงก์แสดงถูกต้อง
- [ ] [Committee] แก้ไข / ลบ → ทำงานได้

---

## 8. แชร์สรุป (Study Notes)

- [ ] นักเรียนโพสต์สรุปด้วย Google Drive URL → บันทึกและแสดงใน /study-notes/
- [ ] URL ที่ไม่ใช่ Google → แสดง error
- [ ] is_anonymous=True → แสดง "ไม่ระบุตัวตน" แทนชื่อ
- [ ] [Committee] เข้า /committee/study-notes/ → เห็น list ทั้งหมด
- [ ] [Committee] ลบสรุป → ยืนยันแล้วลบจริง

---

## 9. แจ้งปัญหา (Problem Reports)

- [ ] นักเรียนโพสต์ปัญหา (รายละเอียด ≥ 10 ตัวอักษร) → บันทึกสำเร็จ
- [ ] รายละเอียด < 10 ตัวอักษร → แสดง error
- [ ] นักเรียนเห็นเฉพาะปัญหาของตัวเองใน /problem-reports/
- [ ] [Committee] อนุมัติ → status เปลี่ยนเป็น approved
- [ ] [Committee] ปฏิเสธพร้อมหมายเหตุ → status เปลี่ยนเป็น rejected, admin_note บันทึก
- [ ] [Committee] ลบ → ยืนยันแล้วลบจริง

---

## 10. ระบบสะสมแต้ม (Points)

- [ ] [Committee] สร้าง PointActivity → แสดงในหน้า /points/ ของนักเรียน
- [ ] นักเรียนส่งหลักฐาน JPG ≤5MB → status=pending
- [ ] นักเรียนส่งซ้ำ (pending อยู่) → ถูกบล็อก แสดง error
- [ ] [Committee] อนุมัติ → แต้มนักเรียนเพิ่ม, status=approved
- [ ] [Committee] อนุมัติซ้ำ (approved แล้ว) → แต้มไม่เพิ่มอีก
- [ ] นักเรียนส่งซ้ำ (approved แล้ว) → ถูกบล็อก แสดง error
- [ ] [Committee] ปฏิเสธ → status=rejected
- [ ] [Committee] ปฏิเสธ submission ที่ approved แล้ว → ถูกบล็อก
- [ ] นักเรียนส่งซ้ำ (rejected แล้ว) → ทำได้ (ส่ง request ใหม่ได้)
- [ ] /point-history/ แสดงประวัติและแต้มสะสมถูกต้อง

---

## 11. Committee Dashboard Access Control

- [ ] นักเรียน GET /committee/ → redirect (ไม่ใช่ 200 หรือ 403)
- [ ] นักเรียน GET /committee/news/ → redirect
- [ ] นักเรียน GET /committee/competitions/ → redirect
- [ ] นักเรียน GET /committee/volunteer/ → redirect
- [ ] นักเรียน GET /committee/study-notes/ → redirect
- [ ] นักเรียน GET /committee/problem-reports/ → redirect
- [ ] นักเรียน GET /committee/points/ → redirect
- [ ] ผู้ไม่ได้ login GET /committee/ → redirect ไป login

---

## 12. File Upload Security

- [ ] อัปโหลด .exe หรือ .pdf เป็นรูป News → ถูก reject (server-side)
- [ ] อัปโหลด .exe หรือ .pdf เป็นรูป Competition → ถูก reject (server-side)
- [ ] อัปโหลดรูป >5MB เป็นหลักฐานแต้ม → ถูก reject
- [ ] อัปโหลดรูป >5MB เป็นรูป News → ถูก reject
- [ ] อัปโหลดรูป >5MB เป็นรูป Competition → ถูก reject
- [ ] อัปโหลด JPG/PNG/WEBP ≤5MB → ผ่านทุกกรณี

---

## 13. Media & Archive

- [ ] รูปที่อัปโหลดแสดงใน browser ผ่าน /media/...
- [ ] `media/` ไม่ถูก commit ใน git (ตรวจด้วย `git status`)
- [ ] `python manage.py archive_old_media --dry-run` รันได้ ไม่ error
- [ ] `venv/` ไม่ถูก commit ใน git (ตรวจด้วย `git status`)

---

**เมื่อ checklist ผ่านทุกข้อ ระบบพร้อมส่งทดสอบ**
