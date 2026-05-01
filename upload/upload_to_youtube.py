"""
สคริปต์อัปโหลด YouTube - อัปเดตสำหรับปี 2025

ใช้ refresh token จาก GitHub Secrets เพื่ออัปโหลดวิดีโอ
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime

load_dotenv()

def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else "MISSING"
    print(f"[youtube] Client ID: {mask(client_id)}")
    print(f"[youtube] Client Secret: {mask(client_secret)}")
    print(f"[youtube] Refresh Token: {mask(refresh_token)}")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "ข้อมูลรับรองขาดหายไป! กรุณาตั้งค่าตัวแปรสภาพแวดล้อมเหล่านี้:\n"
            "  - YOUTUBE_CLIENT_ID\n"
            "  - YOUTUBE_CLIENT_SECRET\n"
            "  - YOUTUBE_REFRESH_TOKEN"
        )

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    try:
        creds.refresh(Request())
    except Exception as e:
        if "invalid_grant" in str(e).lower():
            print("\n❌ [youtube] ข้อผิดพลาดการยืนยันตัวตน: Refresh token หมดอายุหรือถูกเพิกถอน")
            print("💡 วิธีแก้ไข: คุณต้องสร้าง refresh token ใหม่")
            print("   1. ไปที่ Google Cloud Console")
            print("   2. ตรวจสอบว่า 'OAuth Consent Screen' อยู่ใน 'Production' หรือเพิ่มตัวเองเป็นผู้ทดสอบ")
            print("   3. รันสคริปต์ภายในเพื่อรับ refresh token ใหม่")
        raise

    return build('youtube', 'v3', credentials=creds)

def generate_video_metadata(category: str, num_phrases: int, phrases: list = None):
    """สร้างชื่อ คำอธิบาย และแท็กภาษาไทยสำหรับวิดีโอ"""

    title = f"Thai Learning: {num_phrases} Essential {category} Phrases 🇹🇭"

    description_lines = [
        f"🇹🇭 เรียนภาษาไทยกับ Velocity Thai! 🇹🇭",
        f"",
        f"📚 หมวดหมู่: {category}",
        f"",
        f"🎯 เรียนภาษาไทยทีละวลี! บทเรียน{category}วันนี้:",
        f""
    ]

    if phrases:
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i, phrase in enumerate(phrases[:5], 0):
            emoji = emojis[i] if i < len(emojis) else f"{i+1}."
            description_lines.append(f"{emoji} {phrase['english']}")
            description_lines.append(f"   📍 {phrase['thai']}")
            transliteration = phrase.get('transliteration') or phrase.get('romaji', '')
            description_lines.append(f"   🔊 [{transliteration}]")
            description_lines.append("")

    description_lines.extend([
        f"💡 เคล็ดลับ: ท่องซ้ำแต่ละวลี 3 ครั้ง!",
        f"👍 กดไลค์ถ้าคุณได้เรียนรู้สิ่งใหม่!",
        f"💬 คอมเมนต์วลีที่คุณชอบด้านล่าง!",
        f"🔔 ติดตามเพื่อเรียนภาษาไทยทุกวัน!",
        f"",
        f"📖 คู่มือการออกเสียง:",
        f"   การสะกดแบบออกเสียงในวงเล็บช่วยให้คุณออกเสียงถูกต้อง!",
        f"",
        f"#LearnThai #ThaiLessons #ThaiForBeginners #LanguageLearning",
        f"#Thai #Education #Tutorial #DailyThai #{category.replace(' ', '')}",
        f"#VelocityThai #ThaiPhrases #SpeakThai"
    ])

    description = "\n".join(description_lines)

    tags = [
        "learn thai",
        "thai lessons",
        "thai for beginners",
        "thai phrases",
        "language learning",
        "thai tutorial",
        "speak thai",
        category.lower(),
        "education",
        "daily thai",
        "velocity thai",
        "thai learning"
    ]

    return title, description, tags

def upload_to_youtube(video_path, title, description, tags=None, category_id='22'):
    if tags is None:
        tags = ['slapstick', 'animation', 'funny']
    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }

    if '#Shorts' not in body['snippet']['description']:
        body['snippet']['description'] += '\n\n#Shorts'

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True,
        mimetype='video/mp4'
    )

    print(f"[youtube] กำลังอัปโหลด: {title}")
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] ความคืบหน้า: {int(status.progress() * 100)}%")

    print(f"[youtube] ✅ อัปโหลดสำเร็จ! Video ID: {response['id']}")
    print(f"[youtube] URL: https://youtube.com/shorts/{response['id']}")

    return response

def main():
    video_file = Path('final_video.mp4')

    if not video_file.exists():
        print("[youtube] ❌ ไม่พบวิดีโอที่ final_video.mp4")
        return

    title = "Velocity Thai Daily"
    description = "#shorts #thai #languagelearning"
    tags = ['thai', 'language', 'learning']

    try:
        upload_to_youtube(
            video_path=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id='22'
        )
    except Exception as e:
        print(f"[youtube] ❌ อัปโหลดล้มเหลว: {e}")
        raise

if __name__ == '__main__':
    main()