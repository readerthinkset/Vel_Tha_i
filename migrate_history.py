"""
ย้ายประวัติวลีจากรูปแบบญี่ปุ่น/เกาหลีเป็นรูปแบบไทย
แปลง 'korean'/'japanese' -> 'thai' และ 'romanization'/'romaji' -> 'transliteration'
"""
import json
from pathlib import Path

HISTORY_FILE = Path("output/history/all_generated_phrases.json")

if HISTORY_FILE.exists():
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    for phrase in data.get("phrases", []):
        if "korean" in phrase:
            phrase["thai"] = phrase.pop("korean")
            phrase["is_legacy_korean"] = True
            updated_count += 1
        elif "japanese" in phrase and "thai" not in phrase:
            phrase["thai"] = phrase.pop("japanese")
            phrase["is_legacy_japanese"] = True
            updated_count += 1
        if "romanization" in phrase:
            phrase["transliteration"] = phrase.pop("romanization")
            updated_count += 1
        elif "romaji" in phrase and "transliteration" not in phrase:
            phrase["transliteration"] = phrase.pop("romaji")
            updated_count += 1

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ ย้าย {updated_count} วลีเป็นรูปแบบไทย")
    print(f"   - 'korean'/'japanese' → 'thai'")
    print(f"   - 'romanization'/'romaji' → 'transliteration'")
    print(f"   - วลีเก่าถูกทำเครื่องหมายด้วย 'is_legacy_korean' หรือ 'is_legacy_japanese'")
    print(f"\n💡 วลีเก่าเหล่านี้จะไม่ขัดขวางการสร้างเนื้อหาภาษาไทยใหม่")
else:
    print("ไม่พบประวัติวลีที่จะย้าย")