"""VELOCITY THAI - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY THAI"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "THAI"
HANDLE = "@velocitythai"
MASCOT_NAME = "Velo"

# ==== LANGUAGE PACK START ====
LANGUAGE = {
    "code": "th",
    "name": "Thai",
    "native_name": "ไทย",
    "history_key": "thai",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "th-TH-NiwatNeural",
    "native_fallback_voice": "th-TH-PremwadeeNeural",
    "native_engine": "edge",
    "native_lang_code": "th",
    "english_rate": "-2%",
    "native_rate": "-6%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "ไทย",
    "translit_label": "SAY IT LIKE",
    "greeting": "สวัสดี!",
    "encouragement": "เยี่ยม!",
    "rtl": False,
    "char_tiles": False,
    "script_font": "NotoSansThai-Bold.ttf",
}
# ==== LANGUAGE PACK END ====

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4
MAX_REEL_DURATION = 88.0

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, native, icon, accent)

# ==== CATEGORY TABLE START ====
CATEGORY_TABLE = [
    ("Greetings", "คำทักทาย", "hand", "#1CB0F6"),
    ("Basic Phrases", "ประโยคพื้นฐาน", "chat", "#58CC02"),
    ("Common Expressions", "สำนวนทั่วไป", "chat", "#1CB0F6"),
    ("Travel", "การเดินทาง", "plane", "#1CB0F6"),
    ("Restaurant", "ร้านอาหาร", "fork", "#FF7A00"),
    ("Shopping", "การช้อปปิ้ง", "bag", "#E056A0"),
    ("Emergency", "ฉุกเฉิน", "siren", "#FF4B4B"),
    ("Family Terms", "คำเรียกญาติสมาชิก", "heart", "#E056A0"),
    ("Numbers", "ตัวเลข", "hash", "#A560E8"),
    ("Time", "เวลา", "clock", "#00A889"),
    ("Motivation", "แรงบันดาลใจ", "rocket", "#A560E8"),
    ("Love", "ความรัก", "heart", "#FF4B4B"),
    ("Success", "ความสำเร็จ", "trophy", "#F5A700"),
    ("Wisdom", "ภูมิปัญญา", "book", "#A560E8"),
    ("Happiness", "ความสุข", "smile", "#F5A700"),
    ("Self Improvement", "พัฒนาตนเอง", "leaf", "#58CC02"),
    ("Gratitude", "ความกตัญญู", "heart", "#FF7A00"),
    ("Friendship", "มิตรภาพ", "users", "#00A889"),
    ("Hope", "ความหวัง", "sun", "#FF7A00"),
    ("Creativity", "ความคิดสร้างสรรค์", "palette", "#E056A0"),
    ("Inner Peace", "สันติสุขภายใน", "lotus", "#00A889"),
    ("Confidence", "ความมั่นใจ", "shield", "#1CB0F6"),
    ("Perseverance", "ความอดทน", "mountain", "#FF7A00"),
    ("Inspiration", "แรงดลใจ", "sparkles", "#A560E8"),
    ("Positive Life", "ชีวิตเชิงบวก", "sun", "#58CC02"),
    ("Courage", "ความกล้าหาญ", "shield", "#FF4B4B"),
    ("Kindness", "ความเมตตา", "heart", "#E056A0"),
    ("Patience", "ความอดกลั้น", "hourglass", "#00A889"),
    ("Forgiveness", "การให้อภัย", "hands", "#FF7A00"),
    ("Strength", "ความแข็งแกร่ง", "dumbbell", "#FF4B4B"),
    ("Joy", "ความปีติยินดี", "smile", "#F5A700"),
    ("Balance", "ความสมดุล", "scale", "#00A889"),
    ("Growth", "การเติบโต", "sprout", "#58CC02"),
    ("Purpose", "จุดมุ่งหมาย", "target", "#A560E8"),
    ("Mindfulness", "สติ", "lotus", "#00A889"),
]
# ==== CATEGORY TABLE END ====

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

# ==== HASHTAGS START ====
HASHTAGS = [
    "#learnthai",
    "#thailessons",
    "#thaiforbeginners",
    "#languagelearning",
    "#thaivocabulary",
    "#velocitythai",
    "#dailythai",
    "#thai",
    "#learnlanguages",
    "#speakthai",
    "#bilingual",
    "#languagetips",
]
# ==== HASHTAGS END ====
