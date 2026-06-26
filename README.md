# Website for Satriwithaya Students

ระบบเว็บไซต์กลางสำหรับนักเรียนโรงเรียนสตรีวิทยา

## วิธีรันโปรเจกต์

### 1. ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

### 2. สร้างฐานข้อมูล

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. สร้าง superuser (สำหรับเข้า Admin และ Committee Dashboard)

```bash
python manage.py createsuperuser
```

> ใส่ email ที่ลงท้าย @satriwit.ac.th เท่านั้น

### 4. รันเซิร์ฟเวอร์

```bash
python manage.py runserver
```

เปิดเบราว์เซอร์ที่ http://127.0.0.1:8000/

ถ้า server ค้าง รัน:

# ดู process ที่ใช้ port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# หยุด (แทน PID ที่เห็น)
Stop-Process -Id <PID> -Force

---

## Verification Codes

| รหัส | Role | ระดับชั้น |
|------|------|-----------|
| `SW127` | student | ม.1 |
| `SW126` | student | ม.2 |
| `SW125` | student | ม.3 |
| `SW124` | student | ม.4 |
| `SW123` | student | ม.5 |
| `SW122` | student | ม.6 |
| *(ดูใน settings.py)* | committee | — |

> **หมายเหตุ:** รหัส committee ถูก hardcode ไว้ใน `config/settings.py`
> ในระบบจริงควรเก็บ COMMITTEE_VERIFICATION_CODE ใน environment variable หรือ secret manager

---

## สร้าง Test Account สำหรับ Committee (Django Shell)

กรณีต้องการสร้าง committee account โดยไม่ผ่านการ register (เช่น สำหรับทดสอบ):

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# สร้าง committee account
User.objects.create_user(
    email='committee@satriwit.ac.th',
    password='YourPassword123!',
    full_name='ชื่อ คณะกรรมการ',
    role='committee',
)

# สร้าง student account พร้อม grade_level
User.objects.create_user(
    email='student@satriwit.ac.th',
    password='YourPassword123!',
    full_name='ชื่อ นักเรียน',
    role='student',
    grade_level='ม.5',
)
```

> `is_staff=True` ให้สิทธิ์เข้า Django Admin (`/admin/`) เท่านั้น
> สิทธิ์ Committee Dashboard ขึ้นอยู่กับ `role='committee'` ไม่ใช่ `is_staff`

---

## โครงสร้างโปรเจกต์

```
SW Website/
├── config/          # Django project settings & URLs
├── accounts/        # User model, auth views, registration
├── portal/          # Feature views & models
├── templates/
│   ├── base.html
│   ├── accounts/    # login.html, register.html
│   └── portal/      # dashboard, news, volunteer, competitions,
│                    # study_notes, problem_reports, committee
├── static/
├── manage.py
└── requirements.txt
```

---

## URL Routes

| URL | หน้า |
|-----|------|
| `/accounts/login/` | หน้าเข้าสู่ระบบ |
| `/accounts/register/` | หน้าสมัครสมาชิก |
| `/accounts/logout/` | ออกจากระบบ (POST) |
| `/dashboard/` | หน้าหลัก |
| `/news/` | ข่าวสาร |
| `/volunteer/` | จิตอาสา |
| `/competitions/` | การแข่งขัน |
| `/study-notes/` | แชร์สรุป |
| `/problem-reports/` | แจ้งปัญหา |
| `/committee/` | Committee Dashboard (committee only) |
| `/admin/` | Django Admin |

---

---

## Google Drive Upload Setup (Phase 6)

รูปภาพของ News และ Competition สามารถอัปโหลดจากเครื่องไปยัง Google Drive ได้ผ่าน Service Account

### ขั้นตอน

1. **สร้างหรือเลือก Google Cloud Project**
   - ไปที่ [console.cloud.google.com](https://console.cloud.google.com)
   - สร้าง Project ใหม่หรือเลือก Project ที่มีอยู่

2. **Enable Google Drive API**
   - ใน Project เปิด "APIs & Services" > "Library"
   - ค้นหา "Google Drive API" แล้วกด Enable

3. **สร้าง Service Account**
   - ไปที่ "APIs & Services" > "Credentials" > "Create Credentials" > "Service Account"
   - ตั้งชื่อ แล้วกด Create
   - บันทึก **Service Account email** ไว้ (ใช้ในขั้นตอนที่ 7)

4. **ดาวน์โหลด Service Account JSON**
   - คลิก Service Account ที่สร้าง > แท็บ "Keys" > "Add Key" > "JSON"
   - บันทึกไฟล์ที่ดาวน์โหลดได้

5. **วางไฟล์ JSON ไว้ใน root project**
   - เปลี่ยนชื่อเป็น `service-account.json` หรือ path ที่กำหนดใน `.env`
   - ไฟล์นี้อยู่ใน `.gitignore` แล้ว **ห้าม commit เด็ดขาด**

6. **สร้าง Google Drive Folder สำหรับเก็บรูป**
   - สร้าง Folder ใน Google Drive
   - คัดลอก **Folder ID** จาก URL: `drive.google.com/drive/folders/<FOLDER_ID>`

7. **แชร์ Folder ให้ Service Account**
   - คลิกขวาที่ Folder > Share
   - ใส่ Service Account email (จากขั้นตอนที่ 3) แล้วให้สิทธิ์ **Editor**
   - > ถ้าไม่แชร์ Folder ให้ Service Account จะ upload ไม่สำเร็จ

8. **ตั้งค่า .env**
   - คัดลอก `.env.example` เป็น `.env`
   - กรอก `GOOGLE_DRIVE_FOLDER_ID` และ `GOOGLE_SERVICE_ACCOUNT_FILE`
   - ตั้ง `GOOGLE_DRIVE_MAKE_PUBLIC=true` เพื่อให้รูปแสดงในหน้าเว็บ
   - > ถ้าไม่ตั้ง `GOOGLE_DRIVE_MAKE_PUBLIC=true` รูปจะไม่แสดงสำหรับผู้ใช้ทั่วไป

9. **รัน server ใหม่**
   ```bash
   python manage.py runserver
   ```

### หมายเหตุสำคัญ

- ในระบบ production ให้ตั้ง env vars ผ่าน hosting platform (Heroku Config Vars, Railway Variables, ฯลฯ) ไม่ใช่ไฟล์ .env
- URL รูปแบบ `drive.google.com/uc?export=view&id=<id>` อาจ redirect ไปยังหน้า virus-scan สำหรับไฟล์ขนาดใหญ่ หาก `drive_file_id` ถูกเก็บไว้แล้ว สามารถเปลี่ยน URL format ได้ภายหลังโดยไม่ต้อง re-upload
- Service Account ไม่มี Google Drive quota ของตัวเอง ไฟล์จะนับ quota ของ Google Workspace Shared Drive หากใช้ My Drive อาจเกิด `storageQuotaExceeded` ในการ deploy จริงควรใช้ Shared Drive แทน

---

## Phase 2 TODOs

- CRUD สำหรับทุก feature ใน Committee Dashboard
- ฟอร์มแจ้งปัญหาสำหรับนักเรียน
- ฟอร์มแชร์สรุป (Google Drive link submission)
- Google Drive API integration สำหรับ upload ไฟล์
- เปลี่ยนลิงก์ "ห้องเช่าดูกันยัง" เป็น URL จริง
