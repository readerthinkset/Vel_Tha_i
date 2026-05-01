# 🇹🇭 Velocity Thai - สคริปต์สร้าง Facebook Reels อัตโนมัติ

**สคริปต์สร้างคอนเทนต์เรียนภาษาไทยอัตโนมัติสำหรับโซเชียลมีเดีย**

สร้างและโพสต์ 4 ครั้งต่อวันไปยัง Facebook, Instagram และแพลตฟอร์มอื่นๆ ด้วย:
- ✅ วลีภาษาไทยที่สร้างโดย AI พร้อมคำแปลภาษาอังกฤษ
- ✅ ระบบแปลงข้อความเป็นเสียงระดับมืออาชีพ (Edge TTS)
- ✅ พื้นหลังไล่เฉดสีสวยงามพร้อมข้อความซ้อน
- ✅ การซิงค์เสียง-วิดีโออย่างสมบูรณ์แบบ
- ✅ แบรนด์ Velocity Thai
- ✅ **ไม่ซ้ำวลีตลอดกาล** (ติดตามประวัติถาวร)

---

## 📅 ตารางเวลาประจำวัน (เวลาอเมริกัน EST/EDT)

| โพสต์ | เวลา (EST) | เวลา (UTC) | ธีม |
|------|------------|------------|-------|
| 1 | 9:00 AM | 14:00 UTC | แรงบันดาลใจตอนเช้า |
| 2 | 12:00 PM | 17:00 UTC | พักกลางวัน |
| 3 | 3:00 PM | 20:00 UTC | ช่วงบ่าย |
| 4 | 7:00 PM | 00:00 UTC | แรงบันดาลใจตอนเย็น |

---

## 🎬 หมวดหมู่ทั้งหมด (35 หมวดหมู่)

### หมวดหมู่เรียนภาษาไทยเชิงสำคัญ
1. Greetings (คำทักทาย)
2. Basic Phrases (ประโยคพื้นฐาน)
3. Common Expressions (สำนวนทั่วไป)
4. Travel Thai (ภาษาไทยสำหรับท่องเที่ยว)
5. Restaurant Thai (ภาษาไทยสำหรับร้านอาหาร)
6. Shopping Thai (ภาษาไทยสำหรับช้อปปิ้ง)
7. Emergency Thai (ภาษาไทยฉุกเฉิน)
8. Family Terms (คำเรียกญาติสมาชิก)
9. Numbers Thai (ตัวเลขภาษาไทย)
10. Time Thai (เวลาภาษาไทย)

### หมวดหมู่แรงบันดาลใจ
11. Motivation (แรงบันดาลใจ)
12. Love (ความรัก)
13. Success (ความสำเร็จ)
14. Wisdom (ภูมิปัญญา)
15. Happiness (ความสุข)
16. Self Improvement (พัฒนาตนเอง)
17. Gratitude (ความกตัญญู)
18. Friendship (มิตรภาพ)
19. Hope (ความหวัง)
20. Creativity (ความคิดสร้างสรรค์)
21. Inner Peace (สันติสุขภายใน)
22. Confidence (ความมั่นใจ)
23. Perseverance (ความอดทน)
24. Inspiration (แรงดลใจ)
25. Positive Life (ชีวิตเชิงบวก)
26. Courage (ความกล้าหาญ)
27. Kindness (ความเมตตา)
28. Patience (ความอดกลั้น)
29. Forgiveness (การให้อภัย)
30. Strength (ความแข็งแกร่ง)
31. Joy (ความปีติยินดี)
32. Balance (ความสมดุล)
33. Growth (การเติบโต)
34. Purpose (จุดมุ่งหมาย)
35. Mindfulness (สติ)

---

## 🚀 การตั้งค่า GitHub Actions

### ขั้นตอนที่ 1: เพิ่ม Secrets ใน GitHub Repository

ไปที่ GitHub repository → Settings → Secrets and variables → Actions

**Secrets ที่จำเป็น:**

```bash
# Pollinations AI (สำหรับสร้างเนื้อหา)
POLLINATIONS_API_KEY=sk_your_api_key_here

# Facebook (สำหรับอัปโหลด Reels)
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id

# Instagram (สำหรับอัปโหลด Reels)
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id

# ตัวเลือก: แพลตฟอร์มอื่นๆ
VK_ACCESS_TOKEN=your_token
VK_GROUP_ID=your_group_id
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret
```

### ขั้นตอนที่ 2: เปิดใช้งาน GitHub Actions

1. ไปที่แท็บ Actions ใน GitHub repository
2. เปิดใช้งาน workflows ถ้ายังไม่ได้เปิด
3. Workflow จะทำงานอัตโนมัติ 4 ครั้งต่อวัน

### ขั้นตอนที่ 3: ทดสอบด้วยตนเอง

คุณสามารถเรียกใช้ workflow ด้วยตนเองได้:
1. ไปที่ Actions → "Velocity Thai - Daily 5x Upload"
2. คลิก "Run workflow"
3. เลือก branch (main/master)
4. คลิก "Run workflow"

---

## 💻 ทดสอบภายในเครื่อง

### ข้อกำหนดเบื้องต้น

```bash
# ติดตั้ง Python 3.11+
# ติดตั้ง FFmpeg
# ติดตั้ง dependencies
pip install -r requirements.txt
```

### สร้าง Reel เดียว

```bash
python facebook_reels_automation.py
```

### สร้างคอนเทนต์ประจำวัน (4 reels)

```bash
python -c "from facebook_reels_automation import generate_daily_content; generate_daily_content(times_per_day=4)"
```

### อัปโหลดไปยังโซเชียลมีเดีย

```bash
cd upload
python ../upload_all_platforms.py
```

---

## 📁 โครงสร้างโปรเจกต์

```
Velocity Thai/
├── .env                              # คีย์ API และข้อมูลรับรอง
├── .github/
│   └── workflows/
│       └── daily_5x_upload.yml      # GitHub Actions workflow
├── facebook_reels_automation.py     # สคริปต์สร้างหลัก
├── upload_all_platforms.py          # สคริปต์อัปโหลดรวม
├── upload/
│   ├── upload_facebook.py
│   ├── upload_instagram.py
│   ├── upload_vk.py
│   └── ...
├── output/
│   ├── video/                       # Reels ที่สร้างขึ้น
│   ├── history/                     # ประวัติวลี (ห้ามลบ!)
│   └── daily_summary_*.json        # บันทึกการสร้างรายวัน
└── requirements.txt
```

---

## 🔧 การตั้งค่า

### ปรับเขตเวลา

Workflow ใช้ EST/EDT (UTC-5) หากต้องการเปลี่ยนเขตเวลา:

1. แก้ไข `.github/workflows/daily_5x_upload.yml`
2. แก้ไข cron schedules:
   ```yaml
   # สำหรับ PST (UTC-8):
   - cron: '0 17 * * *'  # 9 AM PST
   - cron: '0 20 * * *'  # 12 PM PST
   - cron: '0 23 * * *'  # 3 PM PST
   - cron: '0 3 * * *'   # 7 PM PST
   ```

### ความถี่ในการโพสต์

หากต้องการเปลี่ยนจาก 4 เป็น 3 ครั้งต่อวัน:

1. แก้ไข `.github/workflows/daily_5x_upload.yml`
2. ลบ cron schedule ออก 1 อัน
3. อัปเดต `generate_daily_content(times_per_day=3)` ในสคริปต์

---

## 🎬 ข้อมูลจำเพาะวิดีโอ

- **ความละเอียด:** 1080x1920 (9:16 แนวตั้ง)
- **รูปแบบ:** MP4 (H.264 + AAC)
- **ความยาว:** ~30-50 วินาที (5 วลี)
- **อัตราเฟรม:** 30 FPS
- **เสียง:** Edge TTS (GuyNeural EN, NiwatNeural TH)

---

## 📊 ประวัติวลี

วลีที่สร้างขึ้นทั้งหมดจะถูกเก็บไว้ใน:
```
output/history/all_generated_phrases.json
```

**ไฟล์นี้เป็นถาวรและไม่ควรถูกลบ**

ช่วยให้:
- ✅ ไม่มีวลีซ้ำเลย
- ✅ เนื้อหาใหม่ทุกวัน
- ✅ ติดตามเนื้อหาที่สร้างทั้งหมด

---

## 🐛 การแก้ไขปัญหา

### การสร้างวิดีโอล้มเหลว

```bash
# ตรวจสอบการติดตั้ง FFmpeg
ffmpeg -version

# ติดตั้งใหม่ถ้าจำเป็น
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
```

### การอัปโหลดเสียงล้มเหลว

```bash
# ตรวจสอบไฟล์ .env
cat .env | grep FACEBOOK
cat .env | grep INSTAGRAM

# ยืนยันว่าโทเค็นยังใช้ได้
# สร้างใหม่ถ้าหมดอายุ
```

### GitHub Actions ล้มเหลว

1. ตรวจสอบแท็บ Actions สำหรับบันทึกข้อผิดพลาด
2. ยืนยันว่า secrets ทั้งหมดตั้งค่าถูกต้อง
3. ตรวจสอบ artifact uploads สำหรับไฟล์ที่สร้างขึ้น
4. ตรวจสอบบันทึกสำหรับข้อความแสดงข้อผิดพลาดเฉพาะ

---

## 📈 ประสิทธิภาพ

- **เวลาสร้าง:** ~2-3 นาทีต่อ reel
- **เวลาอัปโหลด:** ~1-2 นาทีต่อแพลตฟอร์ม
- **เวิร์กโฟลว์ทั้งหมด:** ~5-10 นาทีต่อโพสต์
- **ความจุรายวัน:** 4 โพสต์ × 5 วลี = 20 วลี/วัน
- **การหมุนเวียนหมวดหมู่:** 35 หมวดหมู่ = มากกว่า 8 วันก่อนจะซ้ำ

---

## 🎯 ฟีเจอร์หลัก

### ✅ ซิงค์เสียง-วิดีโออย่างสมบูรณ์แบบ
- แต่ละภาพแสดงตามระยะเวลาเสียงที่แม่นยำ
- การจับเวลา ภาษาอังกฤษ + หยุด 500ms + ภาษาไทย ถูกต้อง
- ไม่มีการเปลี่ยนภาพก่อนเวลาหรือตัดเสียง

### ✅ เสียงที่เป็นธรรมชาติ
- วลีมีเครื่องหมายจุลภาคเพื่อจังหวะหยุด
- ตัวอย่าง: "Dream big, start small"
- TTS ฟังเป็นธรรมชาติ ไม่เหมือนหุ่นยกระทำ

### ✅ การออกแบบระดับมืออาชีพ
- พื้นหลังไล่เฉดสีหลายจุดหยุด
- สีที่โดดเด่น: น้ำเงินเข้ม (EN) / น้ำตาลแดง (TH) / เทาเข้ม (การถอดเสียง)
- แบรนด์ Velocity Thai บนทุกเฟรม

### ✅ ไม่ซ้ำวลีตลอดกาล
- ติดตามประวัติวลีถาวร
- AI สร้างเนื้อหาใหม่ทุกครั้ง
- ตรวจสอบวลีทั้งหมดก่อนสร้าง

---

## 📞 การสนับสนุน

หากมีปัญหาหรือคำถาม:
1. ตรวจสอบบันทึก GitHub Actions
2. ตรวจสอบข้อความแสดงข้อผิดพลาดใน output
3. ยืนยันข้อมูลรับรอง API ทั้งหมด
4. ตรวจสอบประวัติวลีสำหรับรายการซ้ำ

---

## 📄 สัญญาอนุญาต

โปรเจกต์นี้มีไว้เพื่อวัตถุประสงค์ทางการศึกษา กรุณาเคารพข้อกำหนดการใช้งาน API ของแพลตฟอร์ม

---

**สร้างด้วย ❤️ สำหรับผู้เรียนภาษาไทยทั่วโลก**

🇹🇭 เรียนภาษาไทยกับ Velocity Thai! 🇹🇭