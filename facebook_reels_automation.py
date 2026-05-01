"""
Velocity Thai - สคริปต์สร้างคอนเทนต์ภาษาไทยอัตโนมัติสำหรับ Facebook Reels
เวอร์ชันปรับปรุง: พื้นหลังสวยขึ้น, หมวดหมู่ภาษาอังกฤษ, ไม่ซ้ำ, แบรนด์ Velocity Thai
"""

import os
import sys
import json
import random
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

if not AI_MODEL:
    raise ValueError(
        "AI_MODEL not set! Please add 'AI_MODEL=gemini-fast' to your .env file. "
        "For GitHub Actions: Add AI_MODEL to repository secrets."
    )

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

FONTS_DIR = BASE_DIR / "fonts"
NOTO_THAI_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf"


def ensure_thai_font():
    font_file = FONTS_DIR / "NotoSansThai-Bold.ttf"
    if font_file.exists() and _is_valid_font_file(font_file):
        print(f"[font] Using local: {font_file} ({font_file.stat().st_size/1024:.1f} KB)")
        return str(font_file)
    FONTS_DIR.mkdir(exist_ok=True)
    for url in [NOTO_THAI_FONT_URL,
                "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf",
                "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansThai/NotoSansThai-Bold.ttf",
                "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansThai/NotoSansThai-Regular.ttf"]:
        try:
            import urllib.request
            print(f"[font] Downloading from: {url}")
            urllib.request.urlretrieve(url, str(font_file))
            if font_file.exists() and _is_valid_font_file(font_file):
                print(f"[font] ✓ Valid font: {font_file} ({font_file.stat().st_size/1024:.1f} KB)")
                return str(font_file)
            else:
                print(f"[font] ✗ Downloaded file is not a valid font, trying next URL...")
        except Exception as e:
            print(f"[font] Download failed: {e}")
    return None


def _is_valid_font_file(path):
    """Check if file is a valid TrueType/OpenType font by examining header"""
    if not path.exists() or path.stat().st_size < 50000:
        return False
    try:
        with open(path, 'rb') as f:
            header = f.read(4)
        # TrueType: 0x00010000, OpenType: 'OTTO', Apple TrueType: 'true' or 'ttcf'
        valid_headers = [b'\x00\x01\x00\x00', b'OTTO', b'true', b'ttcf']
        return header in valid_headers
    except Exception:
        return False


def _find_thai_font_file():
    candidates = [
        str(FONTS_DIR / "NotoSansThai-Bold.ttf"),
        str(FONTS_DIR / "NotoSansThai-Regular.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansThai-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/thai/Garuda-Bold.ttf",
        "/usr/share/fonts/truetype/thai/Garuda.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for path in candidates:
        if _is_valid_font_file(Path(path)):
            return path
    for search_dir in ["/usr/share/fonts", "/usr/local/share/fonts", "C:/Windows/Fonts"]:
        if not Path(search_dir).exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            for fname in files:
                fl = fname.lower()
                if any(t in fl for t in ["notosansthai", "garuda", "tahoma", "angsana", "cordia"]):
                    fpath = Path(root) / fname
                    if _is_valid_font_file(fpath):
                        return str(fpath)
    return None


def _render_text_harfbuzz(text, font_path, font_size, fill_color, stroke_color=None, stroke_width=0):
    import uharfbuzz as hb
    import freetype as ft
    from PIL import Image, ImageDraw, ImageChops

    blob = hb.Blob.from_file_path(font_path)
    hb_face = hb.Face(blob)
    hb_font = hb.Font(hb_face)
    hb_font.scale = (font_size * 64, font_size * 64)

    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hb_font, buffer)

    infos = buffer.glyph_infos
    positions = buffer.glyph_positions

    ft_face = ft.Face(font_path)
    ft_face.set_char_size(font_size * 64)

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    x_cursor = 0.0
    y_cursor = 0.0
    glyph_metrics = []

    for info, pos in zip(infos, positions):
        ft_face.load_glyph(info.codepoint)
        bitmap = ft_face.glyph.bitmap
        bitmap_left = ft_face.glyph.bitmap_left
        bitmap_top = ft_face.glyph.bitmap_top
        x_off = pos.x_offset / 64.0
        y_off = pos.y_offset / 64.0
        x_adv = pos.x_advance / 64.0

        px = x_cursor + x_off + bitmap_left
        py = y_cursor + y_off - bitmap_top

        if bitmap.width > 0 and bitmap.rows > 0:
            min_x = min(min_x, px - stroke_width)
            min_y = min(min_y, py - stroke_width)
            max_x = max(max_x, px + bitmap.width + stroke_width)
            max_y = max(max_y, py + bitmap.rows + stroke_width)

        glyph_metrics.append({
            'codepoint': info.codepoint,
            'x': px, 'y': py,
            'width': bitmap.width, 'height': bitmap.rows,
            'x_advance': x_adv,
        })
        x_cursor += x_adv

    if min_x == float('inf'):
        total_width = max(x_cursor, 50)
        total_height = int(font_size * 1.5)
        min_x = 0
        min_y = 0
    else:
        total_width = max(max_x - min_x + stroke_width * 2, x_cursor + stroke_width * 2)
        total_height = max_y - min_y + stroke_width * 2

    total_width = int(total_width) + stroke_width * 2 + 4
    total_height = int(total_height) + stroke_width * 2 + 4

    img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

    def _draw_glyphs(target_img, color):
        for gm in glyph_metrics:
            ft_face.load_glyph(gm['codepoint'])
            bitmap = ft_face.glyph.bitmap
            if bitmap.width > 0 and bitmap.rows > 0:
                glyph_img = Image.frombytes('L', (bitmap.width, bitmap.rows), bytes(bitmap.buffer))
                paste_x = int(gm['x'] - min_x + stroke_width)
                paste_y = int(gm['y'] - min_y + stroke_width)
                if color[-1] == 255:
                    colored_glyph = Image.new('RGBA', glyph_img.size, color)
                    colored_glyph.putalpha(glyph_img)
                    target_img.paste(colored_glyph, (paste_x, paste_y), glyph_img)
                else:
                    blended = Image.new('RGBA', glyph_img.size, color)
                    mask = glyph_img.point(lambda p: min(255, int(p * color[-1] / 255)))
                    blended.putalpha(mask)
                    target_img.paste(blended, (paste_x, paste_y), blended)

    if stroke_width > 0 and stroke_color:
        stroke_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx * dx + dy * dy <= stroke_width * stroke_width + 1:
                    shifted = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
                    _draw_glyphs(shifted, stroke_color)
                    stroke_img = Image.alpha_composite(stroke_img, ImageChops.offset(shifted, dx, dy))
        img = Image.alpha_composite(img, stroke_img)

    fill_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    _draw_glyphs(fill_img, fill_color)
    img = Image.alpha_composite(img, fill_img)

    return img, int(x_cursor)


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# หมวดหมู่ภาษาอังกฤษ (สำหรับผู้เรียนชาวอเมริกัน/ยุโรป)
# หมวดหมู่เรียนภาษาไทยเชิงสำคัญ + หมวดหมู่แรงบันดาลใจ
CATEGORIES_ENGLISH = [
    # หมวดหมู่เรียนภาษาไทยเชิงสำคัญ (จัดลำดับความสำคัญ)
    "Greetings", "Basic Phrases", "Common Expressions", "Travel Thai", "Restaurant Thai",
    "Shopping Thai", "Emergency Thai", "Family Terms", "Numbers Thai", "Time Thai",
    # หมวดหมู่แรงบันดาลใจ
    "Motivation", "Love", "Success", "Wisdom", "Happiness",
    "Self Improvement", "Gratitude", "Friendship", "Hope", "Creativity",
    "Inner Peace", "Confidence", "Perseverance", "Inspiration", "Positive Life",
    "Courage", "Kindness", "Patience", "Forgiveness", "Strength",
    "Joy", "Balance", "Growth", "Purpose", "Mindfulness",
]

# คำแปลภาษาไทยสำหรับแสดงผล
CATEGORIES_THAI = {
    # หมวดหมู่เรียนภาษาไทยเชิงสำคัญ (จัดลำดับความสำคัญ)
    "Greetings": "คำทักทาย",
    "Basic Phrases": "ประโยคพื้นฐาน",
    "Common Expressions": "สำนวนทั่วไป",
    "Travel Thai": "ภาษาไทยสำหรับท่องเที่ยว",
    "Restaurant Thai": "ภาษาไทยสำหรับร้านอาหาร",
    "Shopping Thai": "ภาษาไทยสำหรับช้อปปิ้ง",
    "Emergency Thai": "ภาษาไทยฉุกเฉิน",
    "Family Terms": "คำเรียกญาติสมาชิก",
    "Numbers Thai": "ตัวเลขภาษาไทย",
    "Time Thai": "เวลาภาษาไทย",
    # หมวดหมู่แรงบันดาลใจ
    "Motivation": "แรงบันดาลใจ",
    "Love": "ความรัก",
    "Success": "ความสำเร็จ",
    "Wisdom": "ภูมิปัญญา",
    "Happiness": "ความสุข",
    "Self Improvement": "พัฒนาตนเอง",
    "Gratitude": "ความกตัญญู",
    "Friendship": "มิตรภาพ",
    "Hope": "ความหวัง",
    "Creativity": "ความคิดสร้างสรรค์",
    "Inner Peace": "สันติสุขภายใน",
    "Confidence": "ความมั่นใจ",
    "Perseverance": "ความอดทน",
    "Inspiration": "แรงดลใจ",
    "Positive Life": "ชีวิตเชิงบวก",
    "Courage": "ความกล้าหาญ",
    "Kindness": "ความเมตตา",
    "Patience": "ความอดกลั้น",
    "Forgiveness": "การให้อภัย",
    "Strength": "ความแข็งแกร่ง",
    "Joy": "ความปีติยินดี",
    "Balance": "ความสมดุล",
    "Growth": "การเติบโต",
    "Purpose": "จุดมุ่งหมาย",
    "Mindfulness": "สติ",
}

# เสียง TTS ภาษาไทยและภาษาอังกฤษ
ENGLISH_VOICE = "en-US-GuyNeural"
THAI_VOICE = "th-TH-NiwatNeural"

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"

RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"
MAX_RECENT_CATEGORIES = 15


# ============== จัดการประวัติวลี (ป้องกันการซ้ำ) ==============

def load_phrase_history():
    if PHRASE_HISTORY_FILE.exists():
        with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"phrases": [], "last_updated": None}


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_phrase_used(english_phrase):
    history = load_phrase_history()
    english_lower = english_phrase.lower().strip()
    for p in history.get("phrases", []):
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            "thai": phrase["thai"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat()
        })
    save_phrase_history(history)
    print(f"[history] เพิ่ม {len(phrases)} วลีลงประวัติ (รวมทั้งหมด: {len(history['phrases'])})")


# ============== จัดการหมุนเวียนหมวดหมู่ (ป้องกันการซ้ำ) ==============

def load_recent_categories():
    if RECENT_CATEGORIES_FILE.exists():
        with open(RECENT_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"recent_categories": [], "last_updated": None}


def save_recent_categories(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(RECENT_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_available_category():
    recent_data = load_recent_categories()
    recent = recent_data.get("recent_categories", [])

    available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent]

    if not available:
        recent_data["recent_categories"] = recent[-5:]
        save_recent_categories(recent_data)
        available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent_data["recent_categories"]]
        print(f"[rotation] หมวดหมู่ถูกใช้ล่าสุดทั้งหมดแล้ว - ล้างรายการเก่า, เหลือ {len(available)} หมวดหมู่")

    selected = random.choice(available)

    recent.append(selected)

    if len(recent) > MAX_RECENT_CATEGORIES:
        recent = recent[-MAX_RECENT_CATEGORIES:]

    recent_data["recent_categories"] = recent
    save_recent_categories(recent_data)

    print(f"[rotation] เลือก '{selected}' (เหลือ {len(available)} หมวดหมู่, {len(recent)} ในประวัติล่าสุด)")
    return selected


# ============== สร้างเนื้อหา ==============

def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_thai = CATEGORIES_THAI[category_english]

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            import requests
            url = "https://gen.pollinations.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
                "Content-Type": "application/json"
            }

            prompt = f"""Create {num_phrases * 2} unique {category_english} phrases for English speakers learning Thai.

IMPORTANT RULES FOR NATURAL SPEECH:
1. Keep phrases SHORT (5-12 words max per language)
2. Add NATURAL PAUSES using commas (e.g., "Dream big, start small")
3. Use punctuation for breathing room in TTS
4. Avoid long run-on sentences
5. Each phrase should be speakable in 3-5 seconds
6. Thai text should be CLEAN - use standard Thai script
7. Do NOT include multiple versions or slashes - just ONE clean Thai translation
8. For the transliteration field, use simple English phonetics (no special characters)
   Example: "Sawatdee krub" not "Sà-wàt-dee khrap"

For each phrase:
1. English phrase (with commas for natural pauses)
2. Thai translation (natural Thai with appropriate script)
3. Transliteration guide (simple English pronunciation, e.g., "Sawatdee krub")

Return as JSON array:
[{{"english": "...", "thai": "...", "transliteration": "..."}}]

IMPORTANT: Create FRESH, UNIQUE phrases that haven't been used before.
IMPORTANT: Thai text must be clean - no slashes, no multiple versions.
IMPORTANT: Use "thai" as the key instead of "japanese", and "transliteration" instead of "romaji"."""

            payload = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a Thai language teacher. Create short, natural phrases with pauses."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.9
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            phrases = json.loads(content)

            # แปลง "japanese" หรือ "romaji" เป็น "thai" และ "transliteration"
            for phrase in phrases:
                if "japanese" in phrase and "thai" not in phrase:
                    phrase["thai"] = phrase.pop("japanese")
                if "romaji" in phrase and "transliteration" not in phrase:
                    phrase["transliteration"] = phrase.pop("romaji")

            unique_phrases = []
            for phrase in phrases:
                if len(phrase.get("english", "").split()) > 15:
                    continue
                if not is_phrase_used(phrase.get("english", "")):
                    unique_phrases.append(phrase)
                if len(unique_phrases) >= num_phrases:
                    break

            if len(unique_phrases) >= num_phrases:
                add_phrases_to_history(unique_phrases[:num_phrases], category_english)
                return unique_phrases[:num_phrases]

        except Exception as e:
            print(f"[content] ความพยายามที่ {attempt + 1} ล้มเหลว: {e}")

    print("[content] ใช้วลีสำรอง...")
    return get_fresh_fallback_phrases(category_english, num_phrases)


def get_fresh_fallback_phrases(category: str, num_phrases: int) -> list:
    all_fallbacks = {
        # หมวดหมู่เรียนภาษาไทยเชิงสำคัญ
        "Greetings": [
            {"english": "Hello, nice to meet you.", "thai": "สวัสดีครับ ยินดีที่ได้รู้จัก", "transliteration": "Sawatdee krub, yindee thee dai roojak"},
            {"english": "Good morning!", "thai": "สวัสดีตอนเช้าครับ!", "transliteration": "Sawatdee ton chao krub!"},
            {"english": "Good evening, how are you?", "thai": "สวัสดีตอนเย็นครับ สบายดีไหม?", "transliteration": "Sawatdee ton yen krub, sabai dee mai?"},
            {"english": "See you tomorrow!", "thai": "พบกันใหม่พรุ่งนี้!", "transliteration": "Phop kan mai prungnee!"},
            {"english": "Goodbye, take care.", "thai": "ลาก่อนครับ โชคดี", "transliteration": "La gon krub, chok dee"},
        ],
        "Basic Phrases": [
            {"english": "Thank you very much.", "thai": "ขอบคุณมากครับ", "transliteration": "Kob khun mak krub"},
            {"english": "You're welcome, no problem.", "thai": "ไม่เป็นไรครับ", "transliteration": "Mai pen rai krub"},
            {"english": "I'm sorry, excuse me.", "thai": "ขอโทษครับ", "transliteration": "Khor thot krub"},
            {"english": "Yes, that's correct.", "thai": "ใช่ครับ ถูกต้อง", "transliteration": "Chai krub, thuk tong"},
            {"english": "No, I don't think so.", "thai": "ไม่ใช่ครับ", "transliteration": "Mai chai krub"},
        ],
        "Common Expressions": [
            {"english": "How are you doing today?", "thai": "วันนี้เป็นอย่างไรบ้างครับ?", "transliteration": "Wan nee pen yang rai bang krub?"},
            {"english": "I'm fine, thank you.", "thai": "สบายดีครับ ขอบคุณ", "transliteration": "Sabai dee krub, kob khun"},
            {"english": "What's your name?", "thai": "คุณชื่ออะไรครับ?", "transliteration": "Khun cheu arai krub?"},
            {"english": "My name is...", "thai": "ผมชื่อ...ครับ", "transliteration": "Phom cheu... krub"},
            {"english": "Nice to meet you too.", "thai": "ยินดีที่ได้รู้จักเช่นกันครับ", "transliteration": "Yindee thee dai roojak chen kan krub"},
        ],
        "Travel Thai": [
            {"english": "Where is the bathroom?", "thai": "ห้องน้ำอยู่ที่ไหนครับ?", "transliteration": "Hong nam yu thee nai krub?"},
            {"english": "How do I get there?", "thai": "ไปที่นั่นอย่างไรครับ?", "transliteration": "Pai thee nan yang rai krub?"},
            {"english": "I need a taxi, please.", "thai": "ผมต้องการแท็กซี่ครับ", "transliteration": "Phom tongkan thaeksi krub"},
            {"english": "Take me to the hotel.", "thai": "ไปโรงแรมครับ", "transliteration": "Pai rong raem krub"},
            {"english": "How much does it cost?", "thai": "ราคาเท่าไหร่ครับ?", "transliteration": "Raka thao rai krub?"},
        ],
        "Restaurant Thai": [
            {"english": "Can I see the menu?", "thai": "ขอดูเมนูได้ไหมครับ?", "transliteration": "Khor du menu dai mai krub?"},
            {"english": "This looks delicious!", "thai": "ดูน่าอร่อยมากครับ!", "transliteration": "Du na aroy mak krub!"},
            {"english": "Water, please.", "thai": "ขอน้ำดื่มครับ", "transliteration": "Khor nam duem krub"},
            {"english": "Check, please.", "thai": "ขอเช็คบิลครับ", "transliteration": "Khor chek bin krub"},
            {"english": "It was delicious!", "thai": "อร่อยมากครับ!", "transliteration": "Aroy mak krub!"},
        ],
        "Shopping Thai": [
            {"english": "How much is this?", "thai": "อันนี้ราคาเท่าไหร่ครับ?", "transliteration": "An nee raka thao rai krub?"},
            {"english": "Can I try this on?", "thai": "ลองใส่ได้ไหมครับ?", "transliteration": "Long sai dai mai krub?"},
            {"english": "Do you have a smaller size?", "thai": "มีขนาดเล็กกว่านี้ไหมครับ?", "transliteration": "Mee khanaat lek gua nee mai krub?"},
            {"english": "I'll take this one.", "thai": "ผมเอาอันนี้ครับ", "transliteration": "Phom ao an nee krub"},
            {"english": "Can I pay by card?", "thai": "จ่ายด้วยบัตรได้ไหมครับ?", "transliteration": "Jai duai bat dai mai krub?"},
        ],
        "Emergency Thai": [
            {"english": "Help me, please!", "thai": "ช่วยด้วยครับ!", "transliteration": "Chuay duay krub!"},
            {"english": "Call the police!", "thai": "เรียกตำรวจครับ!", "transliteration": "Riak tamruat krub!"},
            {"english": "I need a doctor.", "thai": "ผมต้องการหมอครับ", "transliteration": "Phom tongkan mor krub"},
            {"english": "Where is the hospital?", "thai": "โรงพยาบาลอยู่ที่ไหนครับ?", "transliteration": "Rong phayaban yu thee nai krub?"},
            {"english": "I'm lost, can you help?", "thai": "ผมหลงทางครับ ช่วยได้ไหม?", "transliteration": "Phom long thang krub, chuay dai mai?"},
        ],
        "Family Terms": [
            {"english": "This is my mother.", "thai": "นี่คือคุณแม่ครับ", "transliteration": "Nee khue khun mae krub"},
            {"english": "This is my father.", "thai": "นี่คือคุณพ่อครับ", "transliteration": "Nee khue khun pho krub"},
            {"english": "I have an older brother.", "thai": "ผมมีพี่ชายครับ", "transliteration": "Phom mee phi chai krub"},
            {"english": "I have a younger sister.", "thai": "ผมมีน้องสาวครับ", "transliteration": "Phom mee nong sao krub"},
            {"english": "These are my parents.", "thai": "นี่คือพ่อแม่ครับ", "transliteration": "Nee khue pho mae krub"},
        ],
        "Numbers Thai": [
            {"english": "One, two, three.", "thai": "หนึ่ง สอง สาม", "transliteration": "Neung, song, sam"},
            {"english": "Four, five, six.", "thai": "สี่ ห้า หก", "transliteration": "See, ha, hok"},
            {"english": "Seven, eight, nine, ten.", "thai": "เจ็ด แปด เก้า สิบ", "transliteration": "Jet, paet, kao, sip"},
            {"english": "What number is this?", "thai": "นี่เลขอะไรครับ?", "transliteration": "Nee lek arai krub?"},
            {"english": "Give me two, please.", "thai": "ขอสองอันครับ", "transliteration": "Khor song an krub"},
        ],
        "Time Thai": [
            {"english": "What time is it?", "thai": "กี่โมงแล้วครับ?", "transliteration": "Kee mong laew krub?"},
            {"english": "It's three o'clock.", "thai": "สามโมงแล้วครับ", "transliteration": "Sam mong laew krub"},
            {"english": "See you at noon.", "thai": "พบกันตอนเที่ยงครับ", "transliteration": "Phop kan ton thiang krub"},
            {"english": "I'll be there in five minutes.", "thai": "ผมจะไปถึงในห้านาทีครับ", "transliteration": "Phom ja pai theung nai ha na-thee krub"},
            {"english": "What day is today?", "thai": "วันนี้วันอะไรครับ?", "transliteration": "Wan nee wan arai krub?"},
        ],
        # หมวดหมู่แรงบันดาลใจ
        "Motivation": [
            {"english": "Believe in yourself.", "thai": "เชื่อมั่นในตัวเอง", "transliteration": "Cheua man nai tua eng"},
            {"english": "You are capable of amazing things.", "thai": "คุณทำสิ่งยอดเยี่ยมได้", "transliteration": "Khun tham sing yot yiam dai"},
            {"english": "Dream big, start small.", "thai": "ฝันใหญ่ เริ่มจากเล็ก", "transliteration": "Fan yai, term jak lek"},
            {"english": "Your future is created by your actions.", "thai": "อนาคตของคุณสร้างจากการกระทำ", "transliteration": "Anakhot khong khun sang jak kan gratham"},
            {"english": "Never give up on your dreams.", "thai": "อย่าเคยยอมแพ้กับความฝัน", "transliteration": "Yai khoey yom phae kua khwam fan"},
        ],
        "Love": [
            {"english": "Love yourself first.", "thai": "รักตัวเองก่อน", "transliteration": "Rak tua eng gon"},
            {"english": "Love makes everything possible.", "thai": "ความรักทำให้ทุกอย่างเป็นไปได้", "transliteration": "Khwam rak tham hai thuk yang pen pai dai"},
            {"english": "You are loved more than you know.", "thai": "คุณถูกรักมากกว่าที่คิด", "transliteration": "Khun thuek rak mak gua thee khit"},
            {"english": "Love is the greatest power.", "thai": "ความรักคือพลังที่ยิ่งใหญ่ที่สุด", "transliteration": "Khwam rak khue plang thee ying yai thee sut"},
            {"english": "Spread love everywhere you go.", "thai": "แผ่ความรักไปทุกที่ที่คุณไป", "transliteration": "Phae khwam rak pai thuk thee thee khun pai"},
        ],
        "Success": [
            {"english": "Success comes from hard work.", "thai": "ความสำเร็จมาจากความขยัน", "transliteration": "Khwam samret ma jak khwam khayan"},
            {"english": "Keep going, you're getting there.", "thai": "ทำต่อไป คุณใกล้จะถึงแล้ว", "transliteration": "Tham toe pai, khun klai ja theung laew"},
            {"english": "Every step counts toward success.", "thai": "ทุกก้าวมีค่าสู่ความสำเร็จ", "transliteration": "Thuk kao mee kha soo khwam samret"},
            {"english": "Your effort will pay off.", "thai": "ความพยายามของคุณจะไม่สูญเปล่า", "transliteration": "Khwam phayayam khong khun ja mai suen plao"},
            {"english": "Success is a journey, not a destination.", "thai": "ความสำเร็จคือการเดินทาง ไม่ใช่จุดหมายปลายทาง", "transliteration": "Khwam samret khue kan dern thang, mai chai jut mai plai thang"},
        ],
        "Wisdom": [
            {"english": "Knowledge is power.", "thai": "ความรู้คือพลัง", "transliteration": "Khwam ru khue plang"},
            {"english": "Learn from yesterday, live for today.", "thai": "เรียนรู้จากเมื่อวาน มีชีวิตเพื่อวันนี้", "transliteration": "Rian ru jak muan wan, mee chiwit phuea wan nee"},
            {"english": "The wise learn from others' mistakes.", "thai": "คนฉลาดเรียนรู้จากความผิดของคนอื่น", "transliteration": "Khon chalat rian ru jak khwam phit khong khon uen"},
            {"english": "Experience is the best teacher.", "thai": "ประสบการณ์เป็นครูที่ดีที่สุด", "transliteration": "Prasopkan khue khru thee dee thee sut"},
            {"english": "Wisdom comes with age.", "thai": "ภูมิปัญญามาพร้อมกับวัย", "transliteration": "Phoompanya ma phrom gap wai"},
        ],
        "Happiness": [
            {"english": "Happiness is a choice.", "thai": "ความสุขคือการเลือก", "transliteration": "Khwam suk khue kan lueak"},
            {"english": "Find joy in the little things.", "thai": "หาความสุขจากสิ่งเล็กๆ", "transliteration": "Ha khwam suk jak sing lek lek"},
            {"english": "Your happiness matters most.", "thai": "ความสุขของคุณสำคัญที่สุด", "transliteration": "Khwam suk khong khun samkan thee sut"},
            {"english": "Smile, it makes others happy.", "thai": "ยิ้มสิ มันทำให้คนอื่นมีความสุข", "transliteration": "Yim si, man tham hai khon uen mee khwam suk"},
            {"english": "Happiness is contagious, spread it.", "thai": "ความสุขติดต่อได้ แผ่มันออกไป", "transliteration": "Khwam suk tit to dai, phae man ok pai"},
        ],
        "Self Improvement": [
            {"english": "Better today than yesterday.", "thai": "วันนี้ดีกว่าเมื่อวาน", "transliteration": "Wan nee dee gua muan wan"},
            {"english": "Small steps lead to big changes.", "thai": "ก้าวเล็กๆ นำไปสู่การเปลี่ยนแปลงครั้งใหญ่", "transliteration": "Kao lek lek nam pai soo kan plian plaeng khrang yai"},
            {"english": "Invest in yourself daily.", "thai": "ลงทุนในตัวเองทุกวัน", "transliteration": "Longthun nai tua eng thuk wan"},
            {"english": "Growth requires discomfort.", "thai": "การเติบโตต้องการความไม่สบายใจ", "transliteration": "Kan tertbo tongkan khwam mai sabai jai"},
            {"english": "Be your own competition.", "thai": "เป็นคู่แข่งของตัวเอง", "transliteration": "Pen khoo khaeng khong tua eng"},
        ],
        "Gratitude": [
            {"english": "I am grateful for today.", "thai": "ผมขอบคุณสำหรับวันนี้", "transliteration": "Phom kobkhun samrap wan nee"},
            {"english": "Thank you for everything.", "thai": "ขอบคุณสำหรับทุกอย่าง", "transliteration": "Kobkhun samrap thuk yang"},
            {"english": "Gratitude turns what we have into enough.", "thai": "ความกตัญญูเปลี่ยนสิ่งที่เรามีให้เพียงพอ", "transliteration": "Khwam katanyu plian sing thee rao mee hai phiang po"},
            {"english": "Count your blessings daily.", "thai": "นับความโชคดีของคุณทุกวัน", "transliteration": "Nap khwam chok dee khong khun thuk wan"},
            {"english": "A grateful heart is a happy heart.", "thai": "ใจที่กตัญญูคือใจที่มีความสุข", "transliteration": "Jai thee katanyu khue jai thee mee khwam suk"},
        ],
        "Friendship": [
            {"english": "Friends make life better.", "thai": "เพื่อนทำให้ชีวิตดีขึ้น", "transliteration": "Phuean tham hai chiwit dee khuen"},
            {"english": "A true friend is always there.", "thai": "เพื่อนแท้มีให้เสมอ", "transliteration": "Phuean thae mee hai samoe"},
            {"english": "Friendship is a precious gift.", "thai": "มิตรภาพเป็นของขวัญล้ำค่า", "transliteration": "Mittraphap khue khong khwan lam kha"},
            {"english": "Good friends are like stars.", "thai": "เพื่อนที่ดีเหมือนดวงดาว", "transliteration": "Phuean thee dee muean duang dao"},
            {"english": "Cherish your true friends.", "thai": "ทนุทะนุมเพื่อนแท้ของคุณ", "transliteration": "Thanusnu phuean thae khong khun"},
        ],
        "Hope": [
            {"english": "Hope never dies.", "thai": "ความหวังไม่เคยดับสูญ", "transliteration": "Khwam wang mai khoey dap suen"},
            {"english": "Tomorrow is a new beginning.", "thai": "พรุ่งนี้คือการเริ่มต้นใหม่", "transliteration": "Prung nee khue kan term ton mai"},
            {"english": "Keep hope alive in your heart.", "thai": "รักษาความหวังไว้ในใจ", "transliteration": "Raksa khwam wang wai nai jai"},
            {"english": "Hope is the light in darkness.", "thai": "ความหวังคือแสงสว่างในความมืด", "transliteration": "Khwam wang khue saeng suwang nai khwam mue"},
            {"english": "Where there's hope, there's life.", "thai": "ที่ไหนมีความหวัง ที่นั่นมีชีวิต", "transliteration": "Thee nai mee khwam wang, thee nan mee chiwit"},
        ],
        "Creativity": [
            {"english": "Create something beautiful today.", "thai": "สร้างสิ่งที่สวยงามวันนี้", "transliteration": "Sang sing thee suay ngam wan nee"},
            {"english": "Your creativity is unique.", "thai": "ความคิดสร้างสรรค์ของคุณไม่เหมือนใคร", "transliteration": "Khwam khid sang san khong khun mai muean khrai"},
            {"english": "Let your imagination run wild.", "thai": "ปล่อยให้จินตนาการไปกับมัน", "transliteration": "Ploi hai jintanakan pai gap man"},
            {"english": "Art comes from the heart.", "thai": "ศิลปะมาจากหัวใจ", "transliteration": "Sinlapa ma jak hua jai"},
            {"english": "Every day is a canvas.", "thai": "ทุกวันคือผ้าใบ", "transliteration": "Thuk wan khue pha pai"},
        ],
        "Inner Peace": [
            {"english": "Find peace within yourself.", "thai": "หาความสงบจากภายในตัวคุณ", "transliteration": "Ha khwam sa-ngop jak phai nai tua khun"},
            {"english": "Calm mind, happy heart.", "thai": "ใจสงบ หัวใจมีความสุข", "transliteration": "Jai sa-ngop, hua jai mee khwam suk"},
            {"english": "Peace begins with a smile.", "thai": "สันติภาพเริ่มต้นจากรอยยิ้ม", "transliteration": "Santiparb term ton jak roi yim"},
            {"english": "Breathe deeply, let go.", "thai": "หายใจลึกๆ แล้วปล่อยวาง", "transliteration": "Hai jai luek luek laew ploi wang"},
            {"english": "Your inner peace is precious.", "thai": "ความสงบภายในของคุณมีค่า", "transliteration": "Khwam sa-ngop phai nai khong khun mee kha"},
        ],
        "Confidence": [
            {"english": "Believe you can, you're right.", "thai": "เชื่อว่าคุณทำได้ คุณก็ทำได้จริง", "transliteration": "Cheua wa khun tham dai, khun ko tham dai jing"},
            {"english": "You are stronger than you think.", "thai": "คุณแข็งแกร่งกว่าที่คิด", "transliteration": "Khun khaeng kraeng gua thee khit"},
            {"english": "Confidence comes from within.", "thai": "ความมั่นใจมาจากภายใน", "transliteration": "Khwam man jai ma jak phai nai"},
            {"english": "Stand tall, be proud.", "thai": "ยืดอกตรง และภูมิใจ", "transliteration": "Yeut ok tong, lae phoom jai"},
            {"english": "You have what it takes.", "thai": "คุณมีสิ่งที่จำเป็น", "transliteration": "Khun mee sing thee jam pen"},
        ],
        "Perseverance": [
            {"english": "Never give up, keep going.", "thai": "อย่ายอมแพ้ ทำต่อไป", "transliteration": "Yai yom phae, tham toe pai"},
            {"english": "Persistence beats talent.", "thai": "ความอดทนชนะพรสวรรค์", "transliteration": "Khwam od ton chana phorasoan"},
            {"english": "Fall seven times, rise eight.", "thai": "ล้มเจ็ดครั้ง ลุกแปดครั้ง", "transliteration": "Lom jet khrang, luk paet khrang"},
            {"english": "Hard work pays off eventually.", "thai": "ความขยันมีผลตอบแทนในที่สุด", "transliteration": "Khwam khayan mee phon thop than nai thee sut"},
            {"english": "Stay the course, don't quit.", "thai": "มุมมั่นอย่าท้อถอย", "transliteration": "Mum man yai to thoi"},
        ],
        "Inspiration": [
            {"english": "Let inspiration guide you.", "thai": "ให้แรงบันดาลใจนำทางคุณ", "transliteration": "Hai rang bandal jai nam thang khun"},
            {"english": "Be the inspiration others need.", "thai": "เป็นแรงบันดาลใจที่คนอื่นต้องการ", "transliteration": "Pen rang bandal jai thee khon uen tongkan"},
            {"english": "Inspire by example, not words.", "thai": "สร้างแรงบันดาลใจด้วยการกระทำ ไม่ใช่คำพูด", "transliteration": "Sang rang bandal jai duay kan gratham, mai chai kham phut"},
            {"english": "Your story inspires others.", "thai": "เรื่องราวของคุณสร้างแรงบันดาลใจให้คนอื่น", "transliteration": "Rueang rao khong khun sang rang bandal jai hai khon uen"},
            {"english": "Find inspiration in nature.", "thai": "หาแรงบันดาลใจจากธรรมชาติ", "transliteration": "Ha rang bandal jai jak tham machat"},
        ],
        "Positive Life": [
            {"english": "Choose positivity every day.", "thai": "เลือกความเชิงบวกทุกวัน", "transliteration": "Lueak khwam choeng buak thuk wan"},
            {"english": "Positive thoughts create positive life.", "thai": "ความคิดเชิงบวกสร้างชีวิตเชิงบวก", "transliteration": "Khwam khid choeng buak sang chiwit choeng buak"},
            {"english": "Surround yourself with positivity.", "thai": "ล้อมรอบตัวด้วยสิ่งเชิงบวก", "transliteration": "Lorm rop tua duay sing choeng buak"},
            {"english": "Every day is a fresh start.", "thai": "ทุกวันคือการเริ่มต้นใหม่", "transliteration": "Thuk wan khue kan term ton mai"},
            {"english": "Live life with a positive heart.", "thai": "ใช้ชีวิตด้วยใจเชิงบวก", "transliteration": "Chai chiwit duay jai choeng buak"},
        ],
        "Courage": [
            {"english": "Be brave, take the leap.", "thai": "กล้าๆ เสี่ยงๆ", "transliteration": "Kla kla, sieng sieng"},
            {"english": "Courage is not absence of fear.", "thai": "ความกล้าไม่ใช่การไม่กลัว", "transliteration": "Khwam kla mai chai kan mai klua"},
            {"english": "Face your fears with courage.", "thai": "เผชิญความกลัวด้วยความกล้า", "transliteration": "Phachoen khwam klua duay khwam kla"},
            {"english": "Brave hearts change the world.", "thai": "หัวใจกล้าเปลี่ยนโลก", "transliteration": "Hua jai kla plian lok"},
            {"english": "Courage grows with use.", "thai": "ความกล้าเติบโตด้วยการใช้", "transliteration": "Khwam kla tert bo duay kan chai"},
        ],
        "Kindness": [
            {"english": "Be kind to everyone you meet.", "thai": "ใจดีกับทุกคนที่คุณพบ", "transliteration": "Jai dee gap thuk khon thee khun phop"},
            {"english": "Kindness costs nothing, means everything.", "thai": "ความเมตตาไม่ต้องใช้เงิน แต่มีค่าทุกอย่าง", "transliteration": "Khwam metta mai tong chai ngoen, tae mee kha thuk yang"},
            {"english": "A kind word warms the heart.", "thai": "คำดีๆ อบอุ่นหัวใจ", "transliteration": "Kham dee dee, op un hua jai"},
            {"english": "Spread kindness wherever you go.", "thai": "แผ่ความเมตตาไปทุกที่", "transliteration": "Phae khwam metta pai thuk thee"},
            {"english": "Kindness makes the world better.", "thai": "ความเมตตาทำให้โลกดีขึ้น", "transliteration": "Khwam metta tham hai lok dee khuen"},
        ],
        "Patience": [
            {"english": "Good things come to those who wait.", "thai": "สิ่งดีๆ มาถึงคนที่รอคอย", "transliteration": "Sing dee dee ma theung khon thee ro koi"},
            {"english": "Patience is a virtue.", "thai": "ความอดทนเป็นคุณธรรม", "transliteration": "Khwam od ton khue khun tham"},
            {"english": "Take your time, don't rush.", "thai": "ใช้เวลาของคุณ อย่าเร่งรีบ", "transliteration": "Chai wela khong khun, yai reng rip"},
            {"english": "Patience brings peace of mind.", "thai": "ความอดทนนำมาซึ่งสันติสุขในใจ", "transliteration": "Khwam od ton nam ma sue khwam sa-ngop nai jai"},
            {"english": "Wait patiently, trust the process.", "thai": "รอด้วยความอดทน เชื่อมั่นในขั้นตอน", "transliteration": "Ro duay khwam od ton, cheua man nai kan ton"},
        ],
        "Forgiveness": [
            {"english": "Forgive and set yourself free.", "thai": "ให้อภัยและปลดปล่อยตัวเอง", "transliteration": "Hai a-phai lap plot ploi tua eng"},
            {"english": "Forgiveness is a gift to yourself.", "thai": "การให้อภัยเป็นของขวัญให้ตัวเอง", "transliteration": "Kan hai a-phai khue khong khwan hai tua eng"},
            {"english": "Let go of grudges, find peace.", "thai": "ปล่อยวางความโกรธ หาสันติสุข", "transliteration": "Ploi wang khwam groat, ha khwam sa-ngop"},
            {"english": "To err is human, to forgive divine.", "thai": "มนุษย์ย่อมผิดพลาด การให้อภัยคือสิ่งศักดิ์สิทธิ์", "transliteration": "Manut yom phit phlad, kan hai a-phai khue sing saksit"},
            {"english": "Forgiveness heals all wounds.", "thai": "การให้อภัยรักษาบาดแผลทั้งหมด", "transliteration": "Kan hai a-phai raksa bat phaloe thang mot"},
        ],
        "Strength": [
            {"english": "You are stronger than you know.", "thai": "คุณแข็งแกร่งกว่าที่คิด", "transliteration": "Khun khaeng kraeng gua thee khit"},
            {"english": "Strength comes from within.", "thai": "ความแข็งแกร่งมาจากภายใน", "transliteration": "Khwam khaeng kraeng ma jak phai nai"},
            {"english": "Your struggles develop your strength.", "thai": "การต่อสู้พัฒนาความแข็งแกร่งของคุณ", "transliteration": "Kan to-su phatthana khwam khaeng kraeng khong khun"},
            {"english": "Be strong, stay steady.", "thai": "เข้มแข็งและมั่นคง", "transliteration": "Khem khaeng lae man khong"},
            {"english": "Inner strength conquers all.", "thai": "พลังภายในพิชิตทุกสิ่ง", "transliteration": "Plang phai nai phichit thuk sing"},
        ],
        "Joy": [
            {"english": "Find joy in every moment.", "thai": "หาความปีติยินดีในทุกช่วงเวลา", "transliteration": "Ha khwam pi-ti-yin-dee nai thuk chuang we-la"},
            {"english": "Joy is contagious, spread it.", "thai": "ความปีติยินดีติดต่อกันได้ แผ่ออกไป", "transliteration": "Khwam pi-ti-yin-dee tit to gan dai, phae ok pai"},
            {"english": "Let joy fill your heart today.", "thai": "ให้ความปีติยินดีเติมเต็มหัวใจวันนี้", "transliteration": "Hai khwam pi-ti-yin-dee term tem hua jai wan nee"},
            {"english": "Choose joy over worry.", "thai": "เลือกความปีติยินดีแทนความกังวล", "transliteration": "Lueak khwam pi-ti-yin-dee thaen khwam gang-won"},
            {"english": "Joy is the simplest form of gratitude.", "thai": "ความปีติยินดีคือรูปธรรมของความกตัญญูที่เรียบง่ายที่สุด", "transliteration": "Khwam pi-ti-yin-dee khue rup tham khong khwam katanyu thee riap ngai thee sut"},
        ],
        "Balance": [
            {"english": "Find balance in your life.", "thai": "หาความสมดุลในชีวิต", "transliteration": "Ha khwam som-dun nai chiwit"},
            {"english": "Balance is the key to happiness.", "thai": "ความสมดุลคือกุญแจสู่ความสุข", "transliteration": "Khwam som-dun khue kun-jae soo khwam suk"},
            {"english": "Work hard, rest well.", "thai": "ทำงานหนัก พักผ่อนให้เพียงพอ", "transliteration": "Tham ngan nak, phak-phon hai phiang po"},
            {"english": "A balanced life is a peaceful life.", "thai": "ชีวิตที่สมดุลคือชีวิตที่สงบ", "transliteration": "Chiwit thee som-dun khue chiwit thee sa-ngop"},
            {"english": "Prioritize what matters most.", "thai": "ให้ความสำคัญกับสิ่งที่สำคัญที่สุด", "transliteration": "Hai khwam sam-kan gap sing thee sam-kan thee sut"},
        ],
        "Growth": [
            {"english": "Growth happens outside your comfort zone.", "thai": "การเติบโตเกิดขึ้นนอกเขตความสบาย", "transliteration": "Kan tert-bo koed khuen nok khaet khwam sa-bai"},
            {"english": "Embrace change, grow stronger.", "thai": "ยอมรับการเปลี่ยนแปลง เติบโตให้แข็งแกร่ง", "transliteration": "Yom-rap kan plian-plaeng, tert-bo hai khaeng-kraeng"},
            {"english": "Every challenge is a growth opportunity.", "thai": "ทุกความท้าทายคือโอกาสพัฒนา", "transliteration": "Thuk khwam tha-thai khue o-kat phatthana"},
            {"english": "Grow through what you go through.", "thai": "เติบโตผ่านสิ่งที่คุณเผชิญ", "transliteration": "Tert-bo phan sing thee khun pha-choen"},
            {"english": "Personal growth is a lifelong journey.", "thai": "การพัฒนาตนเองเป็นการเดินทางตลอดชีวิต", "transliteration": "Kan phatthana ton eng pen kan dern thang ta-lot chi-wit"},
        ],
        "Purpose": [
            {"english": "Find your purpose, live it.", "thai": "ค้นหาจุดมุ่งหมาย และใช้ชีวิตตามนั้น", "transliteration": "Khon ha jut mung-mai, lae chai chi-wit tam nan"},
            {"english": "Purpose gives life meaning.", "thai": "จุดมุ่งหมายให้ความหมายกับชีวิต", "transliteration": "Jut mung-mai hai khwam mai gap chiwit"},
            {"english": "Live with purpose and passion.", "thai": "ใช้ชีวิตด้วยจุดมุ่งหมายและความหลงใหล", "transliteration": "Chai chiwit duay jut mung mai lae khwam long-lai"},
            {"english": "Your purpose is your calling.", "thai": "จุดมุ่งหมายของคุณคือภารกิจ", "transliteration": "Jut mung-mai khong khun khue pha-ra-kit"},
            {"english": "Discover purpose in everyday moments.", "thai": "ค้นพบจุดมุ่งหมายในช่วงเวลาประจำวัน", "transliteration": "Khon phop jut mung-mai nai chuang we-la pra-jam wan"},
        ],
        "Mindfulness": [
            {"english": "Be present in this moment.", "thai": "อยู่กับปัจจุบัน", "transliteration": "Yu gap pat-ju-ban"},
            {"english": "Mindfulness brings inner peace.", "thai": "สตินำมาซึ่งความสงบภายใน", "transliteration": "Sat-ti nam ma sue-sang khwam sa-ngop phai nai"},
            {"english": "Breathe deeply, stay mindful.", "thai": "หายใจลึกๆ ตั้งสติให้ดี", "transliteration": "Hai jai luek-luek, tang sat-ti hai dee"},
            {"english": "The present moment is all we have.", "thai": "ปัจจุบันคือสิ่งที่เรามี", "transliteration": "Pat-ju-ban khue sing thee rao mee"},
            {"english": "Practice mindfulness daily.", "thai": "ฝึกสติทุกวัน", "transliteration": "Fuek sat-ti thuk wan"},
        ],
    }

    fallbacks = all_fallbacks.get(category, all_fallbacks["Motivation"])
    fresh_phrases = [p for p in fallbacks if not is_phrase_used(p["english"])]
    return fresh_phrases[:num_phrases]


# ============== สร้างเสียง ==============

async def generate_single_audio(text: str, voice: str, output_path: str):
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  ข้อผิดพลาด TTS: {e}")
        return False


def generate_all_audio(phrases: list, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        thai_file = output_dir / f"thai_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  วลีที่ {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    TH: {phrase['thai']}")

        en_success = asyncio.run(generate_single_audio(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    ✓ ภาษาอังกฤษ: {english_file.name}")
        else:
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        th_success = asyncio.run(generate_single_audio(phrase["thai"], THAI_VOICE, str(thai_file)))
        if th_success:
            print(f"    ✓ ภาษาไทย: {thai_file.name}")
        else:
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(thai_file)]
            subprocess.run(cmd, capture_output=True)

        en_duration = get_audio_duration(str(english_file))
        th_duration = get_audio_duration(str(thai_file))

        pause_between = 0.5
        total_duration = en_duration + pause_between + th_duration

        print(f"    ⏱️  รวม: {total_duration:.2f}s (EN: {en_duration:.2f}s + หยุด: {pause_between}s + TH: {th_duration:.2f}s)")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(thai_file),
            "-filter_complex", f"[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{thai_file.as_posix()}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    ✓ ยืนยันไฟล์รวม: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "thai": str(thai_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "th_duration": th_duration
        })

    print(f"\n[audio] ✓ สร้างเสียง {len(audio_files)} วลีสำเร็จ")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    n = len(audio_files)
    print(f"[audio] รวมไฟล์เสียง {n} ไฟล์...")

    concat_file = Path(output_file).parent / "narration_list.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if concat_file.exists():
        concat_file.unlink()

    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] ✓ เสียงบรรยายสุดท้าย: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True

    return False


# ============== สร้างภาพ ==============

def create_impressive_background(category_english: str):
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    # ไล่เฉดสีคอนทราสต์สูงสำหรับทุก 35 หมวดหมู่
    category_colors = {
        "Motivation": [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)],
        "Love": [(255, 0, 100), (139, 0, 0), (255, 105, 180), (255, 192, 203)],
        "Success": [(255, 215, 0), (0, 100, 0), (255, 140, 0), (34, 139, 34)],
        "Wisdom": [(0, 0, 139), (255, 215, 0), (70, 130, 180), (255, 255, 0)],
        "Happiness": [(255, 255, 0), (255, 0, 255), (255, 165, 0), (147, 112, 219)],
        "Self Improvement": [(0, 128, 0), (255, 215, 0), (0, 255, 0), (255, 140, 0)],
        "Gratitude": [(255, 127, 80), (75, 0, 130), (255, 160, 122), (138, 43, 226)],
        "Friendship": [(255, 192, 203), (0, 100, 80), (255, 105, 180), (0, 200, 160)],
        "Hope": [(0, 0, 100), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
        "Creativity": [(255, 0, 127), (0, 0, 139), (255, 20, 147), (75, 0, 130)],
        "Inner Peace": [(135, 206, 235), (0, 0, 100), (176, 224, 230), (75, 0, 130)],
        "Confidence": [(255, 69, 0), (0, 0, 139), (255, 140, 0), (70, 130, 180)],
        "Perseverance": [(139, 69, 19), (255, 215, 0), (160, 82, 45), (255, 140, 0)],
        "Inspiration": [(255, 0, 255), (75, 0, 130), (255, 20, 147), (0, 0, 139)],
        "Positive Life": [(50, 205, 50), (255, 0, 127), (144, 238, 144), (255, 20, 147)],
        "Courage": [(178, 34, 34), (255, 215, 0), (220, 20, 60), (255, 140, 0)],
        "Kindness": [(255, 182, 193), (138, 43, 226), (255, 160, 122), (75, 0, 130)],
        "Patience": [(34, 139, 34), (255, 255, 0), (60, 179, 113), (255, 215, 0)],
        "Forgiveness": [(230, 230, 250), (75, 0, 130), (216, 191, 216), (138, 43, 226)],
        "Strength": [(100, 100, 100), (255, 69, 0), (150, 150, 150), (255, 140, 0)],
        "Joy": [(255, 255, 0), (255, 0, 127), (255, 215, 0), (147, 112, 219)],
        "Balance": [(60, 179, 113), (138, 43, 226), (152, 251, 152), (75, 0, 130)],
        "Growth": [(0, 100, 0), (255, 215, 0), (34, 139, 34), (255, 140, 0)],
        "Purpose": [(75, 0, 130), (255, 215, 0), (138, 43, 226), (255, 140, 0)],
        "Mindfulness": [(210, 180, 140), (75, 0, 130), (245, 245, 220), (138, 43, 226)],
        # หมวดหมู่เรียนภาษาไทยเชิงสำคัญ
        "Greetings": [(70, 130, 180), (255, 140, 0), (255, 255, 0), (255, 99, 71)],
        "Basic Phrases": [(60, 179, 113), (255, 215, 0), (144, 238, 144), (255, 140, 0)],
        "Common Expressions": [(138, 43, 226), (255, 20, 147), (75, 0, 130), (255, 105, 180)],
        "Travel Thai": [(0, 191, 255), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
        "Restaurant Thai": [(255, 69, 0), (255, 215, 0), (220, 20, 60), (255, 140, 0)],
        "Shopping Thai": [(255, 105, 180), (0, 100, 80), (255, 192, 203), (0, 200, 160)],
        "Emergency Thai": [(255, 0, 0), (139, 0, 0), (255, 69, 0), (220, 20, 60)],
        "Family Terms": [(255, 182, 193), (138, 43, 226), (255, 160, 122), (75, 0, 130)],
        "Numbers Thai": [(255, 215, 0), (0, 0, 139), (255, 140, 0), (70, 130, 180)],
        "Time Thai": [(0, 0, 100), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
    }

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    # สร้างไล่เฉดสีแบบหลายจุดหยุด
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    # เพิ่มลวดลายเรขาคณิตเพื่อความลึก
    for i in range(0, VIDEO_WIDTH, 120):
        for j in range(0, VIDEO_HEIGHT, 120):
            draw.ellipse(
                [(i + 30, j + 30), (i + 90, j + 90)],
                outline=(255, 255, 255, 20),
                width=1
            )

    # เพิ่มเอฟเฟกต์แสงเรืองจากศูนย์กลาง
    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)

    return img


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("ไม่พบ PIL กรุณาติดตั้ง: pip install Pillow")
        return None

    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    downloaded = ensure_thai_font()
    if not downloaded:
        print("[font] Local font missing, will search system fonts...")

    english_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    # ฟอนต์ภาษาไทย
    thai_font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansThai-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/thai/Garuda-Bold.ttf",
        "/usr/share/fonts/truetype/thai/Garuda.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/angsana.ttc",
        "C:/Windows/Fonts/cordia.ttc",
    ]

    def load_font(font_paths, size):
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (IOError, OSError):
                continue
        return ImageFont.load_default()

    # ฟอนต์ข้อความภาษาอังกฤษ (ตัวหนา)
    font_category = load_font(english_font_paths, 60)
    font_large = load_font(english_font_paths, 85)
    font_branding = load_font(english_font_paths, 52)

    # ฟอนต์ภาษาไทย (รองรับอักขระไทย) - เพิ่มขนาดให้ใหญ่ขึ้นมาก
    font_thai = load_font(thai_font_paths, 120)

    # ฟอนต์การถอดเสียงภาษาไทยเป็นอักษรโรมัน
    font_transliteration = load_font(english_font_paths, 55)

    english = phrase_data.get("english", "")
    thai = phrase_data.get("thai", "")
    transliteration = phrase_data.get("transliteration", phrase_data.get("romaji", ""))

    def wrap_text(text, font, max_width):
        lines = []

        # ตรวจสอบว่าเป็นภาษาไทยหรือไม่
        is_thai = any('\u0e00' <= c <= '\u0e7f' for c in text)

        if is_thai:
            # ภาษาไทย: แบ่งตามจำนวนอักขระ (14 ตัวอักษรต่อบรรทัด)
            max_chars = 14
            for i in range(0, len(text), max_chars):
                lines.append(text[i:i + max_chars])
        else:
            # ภาษาอังกฤษ: แบ่งตามคำ
            words = text.split()
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

        return lines

    # หมวดหมู่ด้านบน
    category_text = category_english.upper()
    category_bbox = draw.textbbox((VIDEO_WIDTH // 2, 140), category_text, font=font_category, anchor="mm")
    padding = 25
    draw.rectangle(
        [(category_bbox[0] - padding, category_bbox[1] - padding),
         (category_bbox[2] + padding, category_bbox[3] + padding)],
        fill=(0, 0, 0, 200)
    )
    draw.text(
        (VIDEO_WIDTH // 2, 140),
        category_text,
        fill=(255, 255, 255),
        font=font_category,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # ข้อความภาษาอังกฤษ
    english_y = 470
    english_lines = wrap_text(english, font_large, VIDEO_WIDTH - 140)
    total_height = len(english_lines) * 95

    draw.rectangle(
        [(60, english_y - 55), (VIDEO_WIDTH - 60, english_y + total_height + 15)],
        fill=(20, 30, 80, 220)
    )

    for i, line in enumerate(english_lines):
        y_pos = english_y + (i * 95)
        draw.text(
            (VIDEO_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 255),
            font=font_large,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    # ข้อความภาษาไทย - ใช้ HarfBuzz สำหรับการเรนเดอร์ที่ถูกต้อง
    thai_y = english_y + total_height + 110
    thai_font_path = _find_thai_font_file()
    use_harfbuzz = thai_font_path is not None

    if use_harfbuzz:
        try:
            import uharfbuzz as hb
            import freetype as ft
        except ImportError:
            use_harfbuzz = False
            print("  [WARNING] uharfbuzz/freetype not available, falling back to Pillow")

    if use_harfbuzz:
        try:
            max_thai_width = VIDEO_WIDTH - 200
            thai_words = thai.split(' ')
            thai_lines = []
            current_line_words = []

            for word in thai_words:
                test_line = ' '.join(current_line_words + [word]) if current_line_words else word
                _, test_w = _render_text_harfbuzz(
                    test_line, thai_font_path, 65,
                    fill_color=(255, 255, 0, 255)
                )

                if test_w <= max_thai_width or not current_line_words:
                    current_line_words.append(word)
                else:
                    thai_lines.append(' '.join(current_line_words))
                    current_line_words = [word]

            if current_line_words:
                thai_lines.append(' '.join(current_line_words))

            if not thai_lines:
                thai_lines = [thai]

            line_spacing = 85
            total_height = len(thai_lines) * line_spacing

            thai_padding = 60
            draw.rectangle(
                [(50, thai_y - thai_padding), (VIDEO_WIDTH - 50, thai_y + total_height + thai_padding - 10)],
                fill=(80, 30, 30, 220)
            )

            for i, line in enumerate(thai_lines):
                rendered, text_w = _render_text_harfbuzz(
                    line, thai_font_path, 65,
                    fill_color=(255, 255, 0, 255),
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=2
                )
                x_pos = (VIDEO_WIDTH - rendered.width) // 2
                y_pos = thai_y + (i * line_spacing) - rendered.height // 2
                img.paste(rendered, (x_pos, y_pos), rendered)
        except Exception as e:
            print(f"  [WARNING] HarfBuzz rendering failed ({e}), falling back to Pillow")
            use_harfbuzz = False

    if not use_harfbuzz:
        thai_lines = wrap_text(thai, font_thai, VIDEO_WIDTH - 200)
        total_height = len(thai_lines) * 75

        thai_padding = 60
        draw.rectangle(
            [(50, thai_y - thai_padding), (VIDEO_WIDTH - 50, thai_y + total_height + thai_padding - 10)],
            fill=(80, 30, 30, 220)
        )

        for i, line in enumerate(thai_lines):
            y_pos = thai_y + (i * 75)
            draw.text(
                (VIDEO_WIDTH // 2, y_pos),
                line,
                fill=(255, 255, 0),
                font=font_thai,
                anchor="mm",
                stroke_width=3,
                stroke_fill=(0, 0, 0)
            )

    # การถอดเสียงภาษาไทยเป็นอักษรโรมัน (ในกล่องสี่เหลี่ยม)
    transliteration_y = thai_y + total_height + 90
    transliteration_text = f"[{transliteration}]"
    transliteration_lines = wrap_text(transliteration_text, font_transliteration, VIDEO_WIDTH - 160)

    if transliteration_lines:
        transliteration_total_height = len(transliteration_lines) * 60
        draw.rectangle(
            [(70, transliteration_y - 25), (VIDEO_WIDTH - 70, transliteration_y + transliteration_total_height + 15)],
            fill=(40, 40, 40, 230)
        )

        for i, transliteration_line in enumerate(transliteration_lines):
            y_pos = transliteration_y + (i * 60)
            draw.text(
                (VIDEO_WIDTH // 2, y_pos),
                transliteration_line,
                fill=(255, 255, 255),
                font=font_transliteration,
                anchor="mm",
                stroke_width=3,
                stroke_fill=(0, 0, 0, 220)
            )

    # แบรนด์ดิ้ง
    branding_y = VIDEO_HEIGHT - 100
    draw.rectangle(
        [(0, branding_y - 30), (VIDEO_WIDTH, branding_y + 50)],
        fill=(0, 0, 0, 180)
    )
    draw.text(
        (VIDEO_WIDTH // 2, branding_y),
        "VELOCITY THAI",
        fill=(255, 255, 255),
        font=font_branding,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  ✓ ภาพ: {Path(output_path).name}")
    return output_path


# ============== สร้างวิดีโอ ==============

def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    print(f"\n[video] สร้างวิดีโอจาก {len(image_files)} ภาพ...")
    print(f"[video] รับรองการเล่นเสียงครบถ้วนและซิงค์...")

    temp_clips = []

    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"  ภาพ {i+1}/{len(image_files)}: {duration:.2f}s (EN: {audio_info.get('en_duration', 0):.1f}s + TH: {audio_info.get('th_duration', 0):.1f}s)")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    # รวมคลิป
    print("[video] กำลังรวมคลิป...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    concat_file = Path(output_file).parent / "concat_list.txt"

    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(temp_video)]
    subprocess.run(cmd, check=True, capture_output=True)

    # เพิ่มเสียง
    print("[video] เพิ่มเสียง (รับรองการเล่นครบถ้วน)...")
    audio_duration = get_audio_duration(combined_audio)
    print(f"[video] ความยาวเสียง: {audio_duration:.2f}s")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # ตรวจสอบ
    video_duration = get_audio_duration(str(output_file).replace(".mp4", ".mp4"))
    print(f"[video] ✓ สร้างวิดีโอสำเร็จ: {Path(output_file).name} ({video_duration:.2f}s)")

    # ลบไฟล์ชั่วคราว
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()


# ============== เวิร์กโฟลว์หลัก ==============

def generate_reel(category_english: str = None):
    if not category_english:
        category_english = get_available_category()

    print(f"\n{'='*80}")
    print(f"หมวดหมู่: {category_english} ({CATEGORIES_THAI[category_english]})")
    print(f"{'='*80}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reel_dir = VIDEO_DIR / f"{category_english}_{timestamp}"
    reel_dir.mkdir(exist_ok=True)

    # ขั้นตอนที่ 1: สร้างวลีไม่ซ้ำ
    print("[1/4] สร้างวลีไม่ซ้ำ (ตรวจสอบประวัติ)...")
    phrases = generate_phrases(category_english, num_phrases=5)

    for i, phrase in enumerate(phrases, 1):
        print(f"  {i}. {phrase['english']} → {phrase['thai']}")

    # ขั้นตอนที่ 2: สร้างภาพ
    print("\n[2/4] สร้างภาพด้วยพื้นหลังที่สวยงาม...")
    for i, phrase in enumerate(phrases):
        output_path = reel_dir / f"phrase_{i:02d}.jpg"
        generate_complete_image(phrase, category_english, str(output_path))
        print(f"  ✓ ภาพ {i+1}: {phrase['english'][:40]}...")

    # ขั้นตอนที่ 3: สร้างเสียง
    print("\n[3/4] สร้างเสียง (ภาษาอังกฤษ + ภาษาไทย พร้อมหยุด 500ms)...")
    audio_files = generate_all_audio(phrases, str(reel_dir))

    final_audio = reel_dir / "narration.mp3"
    create_final_narration(audio_files, str(final_audio))

    # ขั้นตอนที่ 4: สร้างวิดีโอ
    print("\n[4/4] สร้างวิดีโอ...")
    output_video = reel_dir / "final_reel.mp4"

    image_files = sorted([str(p) for p in reel_dir.glob("phrase_*.jpg")])

    create_video_from_images_audio(
        image_files,
        audio_files,
        str(final_audio),
        str(output_video)
    )

    # บันทึกข้อมูลเมตา
    metadata = {
        "category_english": category_english,
        "category_thai": CATEGORIES_THAI[category_english],
        "timestamp": timestamp,
        "phrases": phrases,
        "video": str(output_video),
        "audio": str(final_audio)
    }

    with open(reel_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ สร้าง REEL เสร็จสมบูรณ์!")
    print(f"  📁 {reel_dir}")
    print(f"  🎬 {output_video.name}")
    print(f"  🏷️  แบรนด์: Velocity Thai")
    print(f"{'='*80}\n")

    return metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🇹🇭 VELOCITY THAI - สร้าง FACEBOOK REELS อัตโนมัติ 🇹🇭")
    print("="*80)
    print("\n✨ ฟีเจอร์ปรับปรุง:")
    print("  ✓ เพิ่มจังหวะหยุดตามธรรมชาติด้วยเครื่องหมายจุลภาค (TTS ไม่เหมือนหุ่นยกระทำ)")
    print("  ✓ ซิงค์เสียงและวิดีโออย่างสมบูรณ์แบบ")
    print("  ✓ รับรองการเล่นเสียงครบถ้วน")
    print("  ✓ หมวดหมู่ภาษาอังกฤษ (สำหรับผู้เรียนชาวอเมริกัน/ยุโรป)")
    print("  ✓ แบรนด์ Velocity Thai ด้านล่าง")
    print("  ✓ ไม่ซ้ำวลีตลอดกาล (ติดตามประวัติถาวร)")
    print(f"\n📊 หมวดหมู่ทั้งหมด ({len(CATEGORIES_ENGLISH)} หมวดหมู่):")
    for i, cat in enumerate(CATEGORIES_ENGLISH, 1):
        print(f"   {i:2d}. {cat} ({CATEGORIES_THAI[cat]})")
    print(f"\n📅 ความจุวันละ:")
    print(f"  • 4 reels ต่อวัน = 20 วลีไม่ซ้ำทุกวัน")
    print(f"  • {len(CATEGORIES_ENGLISH)} หมวดหมู่ = มากกว่า 6 วันก่อนหมวดหมู่จะซ้ำ")
    print(f"  • ประวัติวลีเป็นถาวร (ไม่ลบเลย)")
    print(f"  • AI สร้างวลีใหม่ทุกครั้ง")
    print("="*80)

    generate_reel()

    print("\n" + "="*80)
    print("✅ พร้อมสำหรับระบบอัตโนมัติรายวัน!")
    print("="*80)
    print("\nวิธีสร้าง 4 reels สำหรับวันนี้:")
    print("  from facebook_reels_automation import generate_daily_content")
    print("  generate_daily_content(times_per_day=4)")
    print("\nวิธีสร้าง reel เดียว:")
    print("  generate_reel('Love')  # หรือหมวดหมู่ใดก็ได้จากรายการด้านบน")
    print("="*80)