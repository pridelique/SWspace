# คู่มือการใช้งาน understand-anything

Plugin สำหรับวิเคราะห์โครงสร้าง codebase และสร้าง knowledge graph แบบ interactive

---

## คำสั่งหลัก

| คำสั่ง | ทำอะไร |
|---|---|
| `/understand` | วิเคราะห์ codebase (อัตโนมัติว่าจะ full หรือ incremental) |
| `/understand --full` | บังคับวิเคราะห์ใหม่ทั้งหมด |
| `/understand-dashboard` | เปิด dashboard (ใช้ graph ที่มีอยู่แล้ว) |
| `/understand /path/to/repo` | วิเคราะห์โปรเจกต์จาก path ที่ระบุ |
| `/understand --language th` | สร้าง graph เป็นภาษาไทย |

---

## ขั้นตอนการทำงาน (7 Phase)

```
Phase 0    Pre-flight        ตรวจ graph เดิม / เปรียบ git commit
Phase 0.5  Ignore Config     อ่าน .understandignore (ไฟล์ที่ข้ามได้)
Phase 1    Scan              สแกนไฟล์ทั้งหมด + import map
Phase 1.5  Batch             จัดกลุ่มไฟล์ตาม semantic relationship
Phase 2    Analyze           LLM วิเคราะห์แต่ละกลุ่ม → nodes + edges
Phase 3    Assemble          รวม batch → assembled-graph.json
Phase 4    Architecture      จัดไฟล์เป็น layer (API / Data / UI / ...)
Phase 5    Tour              สร้าง guided tour 5-15 ขั้นตอน
Phase 6    Review            ตรวจความถูกต้องของ graph
Phase 7    Save              เขียน knowledge-graph.json + เปิด dashboard
```

**Incremental update:** ถ้า git commit ไม่เปลี่ยน จะไม่วิเคราะห์ซ้ำ — Phase 0 จะถามแทนว่าต้องการทำอะไร

---

## Workflow ที่แนะนำ

### เมื่อเริ่มโปรเจกต์ใหม่ (ครั้งแรก)
```
/understand
```
รอจนครบทุก Phase แล้วเปิด dashboard ที่ URL ที่แสดง

### ระหว่างพัฒนา (ทุกวัน)
```
/understand-dashboard
```
เปิด dashboard ที่มีอยู่ — ไม่ต้องวิเคราะห์ใหม่

### หลัง commit ฟีเจอร์ใหม่
```
/understand --full
```
อัปเดต graph ให้สะท้อนโค้ดล่าสุด

### ถ้า dashboard server ปิดไป
```
/understand-dashboard
```
หรือรันเองใน terminal:
```powershell
$env:GRAPH_DIR = "D:\path\to\project"
cd "C:\Users\<user>\.claude\plugins\cache\understand-anything\understand-anything\2.8.1\packages\dashboard"
npx vite --host 127.0.0.1
```
ดู URL พร้อม token ในเทอร์มินัล บรรทัด `Dashboard URL: http://127.0.0.1:...?token=...`

---

## Output ที่ได้

```
.understand-anything/
├── knowledge-graph.json      ← graph หลัก (185 nodes, 258 edges สำหรับ SWspace)
├── meta.json                 ← commit hash + timestamp
├── .understandignore         ← ไฟล์ที่ข้ามจากการวิเคราะห์
└── intermediate/
    └── scan-result.json      ← รายการไฟล์ทั้งหมด (เก็บไว้)
```

### โครงสร้าง knowledge-graph.json

```json
{
  "nodes": [...],    // ไฟล์, functions, classes, configs, documents
  "edges": [...],    // imports, calls, depends_on, related, contains
  "layers": [...],   // API / Data / UI / Service / Config / Test / Docs
  "tour":  [...]     // 15 ขั้นตอน guided tour
}
```

---

## ตัวอย่าง: เพิ่มฟีเจอร์ใหม่

สมมติจะเพิ่มระบบ "ประกาศ" (Announcement)

**1. เปิด dashboard ดูโครงสร้างก่อน**
```
/understand-dashboard
```
ดูที่ Data Layer → portal/models.py มีโมเดลอะไรอยู่แล้ว
ดูที่ API Layer → portal/views.py ใช้ pattern อะไร

**2. ถามฉัน (Claude) โดยตรง**
```
ถ้าจะเพิ่มโมเดล Announcement เหมือน News ต้องแตะไฟล์ไหนบ้าง?
```
ฉันใช้ graph ตอบได้ทันที ไม่ต้องสแกนโค้ดซ้ำ

**3. เขียนโค้ด + commit**

**4. อัปเดต graph**
```
/understand --full
```

---

## ตัวอย่าง: เข้าโปรเจกต์คนอื่น

```
/understand /path/to/other-project
```

เปิด dashboard → กด "Start Tour" → เดินผ่านโค้ดตาม guided tour ที่ generate ไว้

---

## ไฟล์ .understandignore

สร้างอัตโนมัติตอนรัน `/understand` ครั้งแรก ใช้ syntax เดียวกับ `.gitignore`

```
# ตัวอย่าง: ข้ามไฟล์ test ทั้งหมด
# *.test.*
# *.spec.*

# ข้ามไฟล์ที่ generate อัตโนมัติ
# *.pyc
# migrations/
```

uncomment บรรทัดที่ต้องการ แล้วรัน `/understand --full` ใหม่

---

## ปรับภาษา Output

```
/understand --language th    # ภาษาไทย
/understand --language en    # ภาษาอังกฤษ (default)
/understand --language ja    # ภาษาญี่ปุ่น
```

ค่าที่เลือกจะถูกบันทึกลง `.understand-anything/config.json` ใช้ต่อใน session ถัดไปโดยอัตโนมัติ

---

## เมื่อ graph ช่วยอะไรได้บ้าง

| สถานการณ์ | วิธีใช้ |
|---|---|
| เข้าโปรเจกต์ใหม่ ไม่รู้จะเริ่มจากไหน | Start Tour ใน dashboard |
| จะแก้ bug ไม่รู้ว่าแตะไฟล์ไหน | ดู edges ของไฟล์นั้น |
| จะเพิ่มฟีเจอร์ อยากรู้ pattern ที่ใช้อยู่ | ดู layer ที่เกี่ยวข้อง |
| ถาม Claude เรื่องโค้ด | Claude ใช้ graph ตอบได้แม่นขึ้น ไม่ต้อง grep ซ้ำ |
| Refactor ใหญ่ อยากรู้ impact | ดู edges แบบ depends_on / imports |

---

## หมายเหตุ

- Dashboard token เปลี่ยนทุกครั้งที่ start server ใหม่ — ดู URL ใหม่ในเทอร์มินัลเสมอ
- `knowledge-graph.json` ควร commit เข้า git เพื่อให้ทีมใช้ร่วมกันได้
- ไฟล์ใน `intermediate/` (ยกเว้น `scan-result.json`) ถูกลบอัตโนมัติหลังวิเคราะห์เสร็จ
