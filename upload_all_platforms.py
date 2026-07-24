"""
Velocity Thai - สคริปต์อัปโหลดไปยังโซเชียลมีเดียทุกแพลตฟอร์ม
อัปโหลด reels ที่สร้างขึ้นไปยังทุกแพลตฟอร์มโซเชียลมีเดียที่เชื่อมต่อ
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

upload_dir = Path(__file__).parent / "upload"
if upload_dir.exists() and str(upload_dir) not in sys.path:
    sys.path.insert(0, str(upload_dir))

upload_to_facebook = None
upload_to_instagram = None
upload_to_youtube = None

try:
    from upload_facebook import upload_to_facebook as fb_upload
    upload_to_facebook = fb_upload
except ImportError as e:
    print(f"[!] โมดูลอัปโหลด Facebook ไม่พร้อมใช้งาน: {e}")

try:
    from upload_instagram import upload_to_instagram as ig_upload
    upload_to_instagram = ig_upload
except ImportError as e:
    print(f"[!] โมดูลอัปโหลด Instagram ไม่พร้อมใช้งาน: {e}")

try:
    from upload_to_youtube import upload_to_youtube as yt_upload
    upload_to_youtube = yt_upload
except ImportError as e:
    print(f"[!] โมดูลอัปโหลด YouTube ไม่พร้อมใช้งาน: {e}")


def get_latest_reel():
    video_dir = Path("output/video")

    if not video_dir.exists():
        print("❌ ไม่พบโฟลเดอร์ output/video")
        return None

    reels = list(video_dir.glob("*/final_reel.mp4"))

    if not reels:
        print("❌ ไม่พบ reels ในโฟลเดอร์ output/video")
        return None

    latest = max(reels, key=lambda p: p.stat().st_mtime)

    metadata_file = latest.parent / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return {
        "video_path": str(latest),
        "metadata": metadata,
        "category": metadata.get("category_english", "Thai Learning"),
        "phrases": metadata.get("phrases", [])
    }


def generate_caption(phrases, category, platform="facebook"):

    if platform == "facebook":
        caption_lines = [
            f"🇹🇭 เรียนภาษาไทยกับ Velocity Thai! 🇹🇭",
            f"",
            f"📚 หมวดหมู่: {category}",
            f"",
            f"🎯 เรียนภาษาไทยทีละวลี! บทเรียน{category}วันนี้:",
            f""
        ]

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i, phrase in enumerate(phrases[:5], 0):
            emoji = emojis[i] if i < len(emojis) else f"{i+1}."
            caption_lines.append(f"{emoji} {phrase['english']}")
            caption_lines.append(f"   📍 {phrase['thai']}")
            transliteration = phrase.get('transliteration') or phrase.get('romaji', '')
            caption_lines.append(f"   🔊 [{transliteration}]")
            caption_lines.append("")

        caption_lines.extend([
            f"💡 เคล็ดลับ: ท่องซ้ำแต่ละวลี 3 ครั้ง!",
            f"👍 กดไลค์ถ้าคุณได้เรียนรู้สิ่งใหม่!",
            f"💬 คอมเมนต์วลีที่คุณชอบด้านล่าง!",
            f"🔔 ติดตามเพื่อเรียนภาษาไทยทุกวัน!",
            f"",
            f"📖 คู่มือการออกเสียง:",
            f"   การสะกดแบบออกเสียงในวงเล็บช่วยให้คุณออกเสียงถูกต้อง!",
            f"",
        ])

        hashtags = [
            "#learnthai",
            "#thailessons",
            "#thaiforbeginners",
            "#languagelearning",
            "#thaivocabulary",
            "#velocitythai",
            "#dailythai",
            "#thai",
            "#learnlanguages",
            "#thailanguage",
            "#speakthai",
            "#thaipractice",
            "#bilingual",
            "#thaiwords",
            "#languagetips"
        ]

        caption_lines.extend(hashtags)

    else:
        caption_lines = [
            f"🇹🇭 เรียนภาษาไทยกับ Velocity Thai! 🇹🇭",
            f"",
            f"หมวดหมู่: {category}",
            f"",
            f"วลีวันนี้:",
            f""
        ]

        for i, phrase in enumerate(phrases[:3], 1):
            caption_lines.append(f"{i}. {phrase['english']}")
            caption_lines.append(f"   → {phrase['thai']}")
            caption_lines.append("")

        hashtags = [
            "#learnthai",
            "#thailessons",
            "#thaiforbeginners",
            "#languagelearning",
            "#thaivocabulary",
            "#velocitythai",
            "#dailythai",
            "#thai",
            "#learnlanguages",
            "#thailanguage"
        ]

        caption_lines.extend(hashtags)

    return "\n".join(caption_lines)


def upload_to_all_platforms(video_path, caption, category, phrases=None):

    results = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "video": video_path,
        "uploads": {},
        "platforms_attempted": [],
        "platforms_successful": [],
        "platforms_skipped": [],
        "platforms_failed": []
    }

    print("\n" + "="*80)
    print("🚀 VELOCITY THAI - อัปโหลดหลายแพลตฟอร์ม")
    print("="*80)
    print(f"วิดีโอ: {video_path}")
    print(f"หมวดหมู่: {category}")
    print(f"ความยาวแคปชัน: {len(caption)} ตัวอักษร")
    print("="*80)

    if not Path(video_path).exists():
        print(f"❌ ไม่พบไฟล์วิดีโอ: {video_path}")
            # === UPLOAD STATUS REPORT ===
    print("\n" + "=" * 60)
    print("UPLOAD STATUS REPORT")
    print("=" * 60)
    success_list = [p.lower() for p in results.get("platforms_successful", [])]
    failed_list = [p.lower() for p in results.get("platforms_failed", [])]
    skipped_list = [p.lower() for p in results.get("platforms_skipped", [])]
    for pname in ["INSTAGRAM", "FACEBOOK", "YOUTUBE", "THREADS", "TIKTOK", "TWITTER", "VK", "TELEGRAM"]:
        pl = pname.lower()
        if pl in success_list: status = "SUCCESS"
        elif pl in failed_list: status = "FAILED"
        elif pl in skipped_list: status = "SKIPPED"
        else: status = "-"
        print(f"{pname}: {status}")
    print("=" * 60)
    return results

    platforms = [
        ("facebook", upload_to_facebook, "📘 Facebook"),
        ("instagram", upload_to_instagram, "📸 Instagram"),
        ("youtube", upload_to_youtube, "📺 YouTube"),
    ]

    for platform_name, upload_func, display_name in platforms:
        print(f"\n{display_name} กำลังอัปโหลด...")
        results["platforms_attempted"].append(platform_name)

        if upload_func:
            try:
                upload_result = None

                if platform_name == "facebook":
                    upload_result = upload_func(
                        video_path=video_path,
                        description=caption,
                        title=f"Thai: {category}"
                    )
                elif platform_name == "instagram":
                    upload_result = upload_func(
                        video_path=video_path,
                        caption=caption,
                        is_story=False
                    )
                elif platform_name == "youtube":
                    num_phrases = len(phrases) if phrases else 5
                    from upload_to_youtube import generate_video_metadata
                    yt_title, yt_description, yt_tags = generate_video_metadata(category, num_phrases, phrases)

                    upload_result = upload_func(
                        video_path=video_path,
                        title=yt_title,
                        description=yt_description,
                        tags=yt_tags,
                        category_id='22'
                    )

                if upload_result:
                    results["uploads"][platform_name] = upload_result
                    results["platforms_successful"].append(platform_name)
                    print(f"✅ {display_name} อัปโหลดสำเร็จ")
                else:
                    results["uploads"][platform_name] = {"status": "failed", "error": "Upload function returned None"}
                    results["platforms_failed"].append(platform_name)
                    print(f"❌ {display_name} อัปโหลดล้มเหลว: ไม่มีผลลัพธ์")

            except Exception as e:
                error_msg = str(e)
                results["uploads"][platform_name] = {"status": "failed", "error": error_msg}
                results["platforms_failed"].append(platform_name)
                print(f"❌ {display_name} อัปโหลดล้มเหลว: {error_msg}")
        else:
            print(f"⚠️  {display_name} อัปโหลดถูกข้าม (โมดูลไม่พร้อมใช้งาน)")
            results["uploads"][platform_name] = {"status": "skipped", "reason": "Module not available"}
            results["platforms_skipped"].append(platform_name)

    # ===== สรุปผลการอัปโหลด =====
    print("\n" + "="*80)
    print("📊 สรุปผลการอัปโหลด")
    print("="*80)

    total_attempted = len(results["platforms_attempted"])
    successful_count = len(results["platforms_successful"])
    failed_count = len(results["platforms_failed"])
    skipped_count = len(results["platforms_skipped"])

    print(f"\n📈 สถานะโดยรวม:")
    print(f"   ├─ แพลตฟอร์มทั้งหมด: {total_attempted}")
    print(f"   ├─ ✅ สำเร็จ: {successful_count}")
    print(f"   ├─ ❌ ล้มเหลว: {failed_count}")
    print(f"   └─ ⚠️  ถูกข้าม: {skipped_count}")

    if total_attempted > 0:
        success_rate = (successful_count / total_attempted) * 100
        print(f"\n🎯 อัตราความสำเร็จ: {success_rate:.0f}%")

    if results["platforms_successful"]:
        print(f"\n✅ อัปโหลดสำเร็จ ({len(results['platforms_successful'])}):")
        for platform in results["platforms_successful"]:
            platform_data = results["uploads"].get(platform, {})
            video_id = platform_data.get("video_id", "N/A")
            print(f"   ✅ {platform.upper()}: สำเร็จ (Video ID: {video_id})")

    if results["platforms_failed"]:
        print(f"\n❌ อัปโหลดล้มเหลว ({len(results['platforms_failed'])}):")
        for platform in results["platforms_failed"]:
            platform_data = results["uploads"].get(platform, {})
            error = platform_data.get("error", "Unknown error")
            print(f"   ❌ {platform.upper()}: ล้มเหลว - {error[:80]}...")

    if results["platforms_skipped"]:
        print(f"\n⚠️  แพลตฟอร์มที่ถูกข้าม ({len(results['platforms_skipped'])}):")
        skipped_list = ", ".join([p.upper() for p in results["platforms_skipped"]])
        print(f"   ⚠️  {skipped_list}")
        print(f"   💡 เพิ่มข้อมูลรับรองเพื่อเปิดใช้งานแพลตฟอร์มเหล่านี้")

    print("\n" + "="*80)

    results_file = Path("output") / f"upload_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 บันทึกผลลัพธ์: {results_file}")
    print("="*80)

        # === UPLOAD STATUS REPORT ===
    print("\n" + "=" * 60)
    print("UPLOAD STATUS REPORT")
    print("=" * 60)
    success_list = [p.lower() for p in results.get("platforms_successful", [])]
    failed_list = [p.lower() for p in results.get("platforms_failed", [])]
    skipped_list = [p.lower() for p in results.get("platforms_skipped", [])]
    for pname in ["INSTAGRAM", "FACEBOOK", "YOUTUBE", "THREADS", "TIKTOK", "TWITTER", "VK", "TELEGRAM"]:
        pl = pname.lower()
        if pl in success_list: status = "SUCCESS"
        elif pl in failed_list: status = "FAILED"
        elif pl in skipped_list: status = "SKIPPED"
        else: status = "-"
        print(f"{pname}: {status}")
    print("=" * 60)
    return results


def main():
    print("\n" + "="*80)
    print("🇹🇭 VELOCITY THAI - อัปโหลดอัตโนมัติ 🇹🇭")
    print("="*80)

    reel = get_latest_reel()

    if not reel:
        print("\n❌ ไม่พบ reel! กรุณารัน facebook_reels_automation.py ก่อน")
        sys.exit(1)

    print(f"\n✅ พบ reel ล่าสุด:")
    print(f"   หมวดหมู่: {reel['category']}")
    print(f"   วิดีโอ: {reel['video_path']}")
    print(f"   วลี: {len(reel['phrases'])}")

    caption = generate_caption(reel['phrases'], reel['category'], platform="facebook")
    print(f"\n📝 สร้างแคปชัน ({len(caption)} ตัวอักษร):")
    print("-"*80)
    print(caption[:500] + "..." if len(caption) > 500 else caption)
    print("-"*80)

    results = upload_to_all_platforms(
        reel['video_path'],
        caption,
        reel['category'],
        reel['phrases']
    )

    results["phrases"] = reel['phrases']

    successful = len(results.get("platforms_successful", []))
    failed = len(results.get("platforms_failed", []))
    skipped = len(results.get("platforms_skipped", []))

    if successful > 0:
        print(f"\n✅ อัปโหลดเสร็จสมบูรณ์! {successful} แพลตฟอร์มสำเร็จ")
        if skipped > 0:
            print(f"💡 {skipped} แพลตฟอร์มถูกข้าม - เพิ่มข้อมูลรับรองเพื่อเปิดใช้งาน")
        sys.exit(0)
    elif failed > 0:
        print(f"\n⚠️  อัปโหลดทั้งหมดล้มเหลว ({failed} ล้มเหลว, {skipped} ถูกข้าม)")
        print("💡 ตรวจสอบข้อความแสดงข้อผิดพลาดด้านบนและยืนยันข้อมูลรับรองของคุณ")
        sys.exit(1)
    else:
        print(f"\n⚠️  อัปโหลดทั้งหมดถูกข้าม ({skipped} ถูกข้าม)")
        print("💡 เพิ่มข้อมูลรับรองใน GitHub Secrets เพื่อเปิดใช้งานการอัปโหลด")
        sys.exit(1)


if __name__ == "__main__":
    main()