"""AI phrase generation with permanent no-repeat history."""

from __future__ import annotations

import json
import random
import time
from datetime import datetime

import requests

import config
from config import CATEGORIES, CATEGORIES_NATIVE, HISTORY_DIR, MAX_RECENT_CATEGORIES

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"

PHRASE_KEY = config.LANGUAGE["history_key"]
LANGUAGE_NAME = config.LANGUAGE["name"]
NATIVE_NAME = config.LANGUAGE["native_name"]

# ==== FALLBACK PHRASES START ====
FALLBACK_PHRASES = [
    {"english": "Hello, nice to meet you.", "native": "สวัสดีครับ ยินดีที่ได้รู้จัก", "transliteration": "Sawatdee krub, yindee thee dai roojak"},
    {"english": "Good morning!", "native": "สวัสดีตอนเช้าครับ!", "transliteration": "Sawatdee ton chao krub!"},
    {"english": "Good evening, how are you?", "native": "สวัสดีตอนเย็นครับ สบายดีไหม?", "transliteration": "Sawatdee ton yen krub, sabai dee mai?"},
    {"english": "See you tomorrow!", "native": "พบกันใหม่พรุ่งนี้!", "transliteration": "Phop kan mai prungnee!"},
    {"english": "Goodbye, take care.", "native": "ลาก่อนครับ โชคดี", "transliteration": "La gon krub, chok dee"},
    {"english": "Thank you very much.", "native": "ขอบคุณมากครับ", "transliteration": "Kob khun mak krub"},
    {"english": "You're welcome, no problem.", "native": "ไม่เป็นไรครับ", "transliteration": "Mai pen rai krub"},
    {"english": "I'm sorry, excuse me.", "native": "ขอโทษครับ", "transliteration": "Khor thot krub"},
    {"english": "Yes, that's correct.", "native": "ใช่ครับ ถูกต้อง", "transliteration": "Chai krub, thuk tong"},
    {"english": "No, I don't think so.", "native": "ไม่ใช่ครับ", "transliteration": "Mai chai krub"},
    {"english": "How are you doing today?", "native": "วันนี้เป็นอย่างไรบ้างครับ?", "transliteration": "Wan nee pen yang rai bang krub?"},
    {"english": "I'm fine, thank you.", "native": "สบายดีครับ ขอบคุณ", "transliteration": "Sabai dee krub, kob khun"},
    {"english": "What's your name?", "native": "คุณชื่ออะไรครับ?", "transliteration": "Khun cheu arai krub?"},
    {"english": "My name is...", "native": "ผมชื่อ...ครับ", "transliteration": "Phom cheu... krub"},
    {"english": "Nice to meet you too.", "native": "ยินดีที่ได้รู้จักเช่นกันครับ", "transliteration": "Yindee thee dai roojak chen kan krub"},
    {"english": "Where is the bathroom?", "native": "ห้องน้ำอยู่ที่ไหนครับ?", "transliteration": "Hong nam yu thee nai krub?"},
    {"english": "How do I get there?", "native": "ไปที่นั่นอย่างไรครับ?", "transliteration": "Pai thee nan yang rai krub?"},
    {"english": "I need a taxi, please.", "native": "ผมต้องการแท็กซี่ครับ", "transliteration": "Phom tongkan thaeksi krub"},
    {"english": "Take me to the hotel.", "native": "ไปโรงแรมครับ", "transliteration": "Pai rong raem krub"},
    {"english": "How much does it cost?", "native": "ราคาเท่าไหร่ครับ?", "transliteration": "Raka thao rai krub?"},
    {"english": "Can I see the menu?", "native": "ขอดูเมนูได้ไหมครับ?", "transliteration": "Khor du menu dai mai krub?"},
    {"english": "This looks delicious!", "native": "ดูน่าอร่อยมากครับ!", "transliteration": "Du na aroy mak krub!"},
    {"english": "Water, please.", "native": "ขอน้ำดื่มครับ", "transliteration": "Khor nam duem krub"},
    {"english": "Check, please.", "native": "ขอเช็คบิลครับ", "transliteration": "Khor chek bin krub"},
    {"english": "It was delicious!", "native": "อร่อยมากครับ!", "transliteration": "Aroy mak krub!"},
    {"english": "How much is this?", "native": "อันนี้ราคาเท่าไหร่ครับ?", "transliteration": "An nee raka thao rai krub?"},
    {"english": "Can I try this on?", "native": "ลองใส่ได้ไหมครับ?", "transliteration": "Long sai dai mai krub?"},
    {"english": "Do you have a smaller size?", "native": "มีขนาดเล็กกว่านี้ไหมครับ?", "transliteration": "Mee khanaat lek gua nee mai krub?"},
    {"english": "I'll take this one.", "native": "ผมเอาอันนี้ครับ", "transliteration": "Phom ao an nee krub"},
    {"english": "Can I pay by card?", "native": "จ่ายด้วยบัตรได้ไหมครับ?", "transliteration": "Jai duai bat dai mai krub?"},
    {"english": "Help me, please!", "native": "ช่วยด้วยครับ!", "transliteration": "Chuay duay krub!"},
    {"english": "Call the police!", "native": "เรียกตำรวจครับ!", "transliteration": "Riak tamruat krub!"},
    {"english": "I need a doctor.", "native": "ผมต้องการหมอครับ", "transliteration": "Phom tongkan mor krub"},
    {"english": "Where is the hospital?", "native": "โรงพยาบาลอยู่ที่ไหนครับ?", "transliteration": "Rong phayaban yu thee nai krub?"},
    {"english": "I'm lost, can you help?", "native": "ผมหลงทางครับ ช่วยได้ไหม?", "transliteration": "Phom long thang krub, chuay dai mai?"},
    {"english": "This is my mother.", "native": "นี่คือคุณแม่ครับ", "transliteration": "Nee khue khun mae krub"},
    {"english": "This is my father.", "native": "นี่คือคุณพ่อครับ", "transliteration": "Nee khue khun pho krub"},
    {"english": "I have an older brother.", "native": "ผมมีพี่ชายครับ", "transliteration": "Phom mee phi chai krub"},
    {"english": "I have a younger sister.", "native": "ผมมีน้องสาวครับ", "transliteration": "Phom mee nong sao krub"},
    {"english": "These are my parents.", "native": "นี่คือพ่อแม่ครับ", "transliteration": "Nee khue pho mae krub"},
    {"english": "One, two, three.", "native": "หนึ่ง สอง สาม", "transliteration": "Neung, song, sam"},
    {"english": "Four, five, six.", "native": "สี่ ห้า หก", "transliteration": "See, ha, hok"},
    {"english": "Seven, eight, nine, ten.", "native": "เจ็ด แปด เก้า สิบ", "transliteration": "Jet, paet, kao, sip"},
    {"english": "What number is this?", "native": "นี่เลขอะไรครับ?", "transliteration": "Nee lek arai krub?"},
    {"english": "Give me two, please.", "native": "ขอสองอันครับ", "transliteration": "Khor song an krub"},
    {"english": "What time is it?", "native": "กี่โมงแล้วครับ?", "transliteration": "Kee mong laew krub?"},
    {"english": "It's three o'clock.", "native": "สามโมงแล้วครับ", "transliteration": "Sam mong laew krub"},
    {"english": "See you at noon.", "native": "พบกันตอนเที่ยงครับ", "transliteration": "Phop kan ton thiang krub"},
    {"english": "I'll be there in five minutes.", "native": "ผมจะไปถึงในห้านาทีครับ", "transliteration": "Phom ja pai theung nai ha na-thee krub"},
    {"english": "What day is today?", "native": "วันนี้วันอะไรครับ?", "transliteration": "Wan nee wan arai krub?"},
    {"english": "Believe in yourself.", "native": "เชื่อมั่นในตัวเอง", "transliteration": "Cheua man nai tua eng"},
    {"english": "You are capable of amazing things.", "native": "คุณทำสิ่งยอดเยี่ยมได้", "transliteration": "Khun tham sing yot yiam dai"},
    {"english": "Dream big, start small.", "native": "ฝันใหญ่ เริ่มจากเล็ก", "transliteration": "Fan yai, term jak lek"},
    {"english": "Your future is created by your actions.", "native": "อนาคตของคุณสร้างจากการกระทำ", "transliteration": "Anakhot khong khun sang jak kan gratham"},
    {"english": "Never give up on your dreams.", "native": "อย่าเคยยอมแพ้กับความฝัน", "transliteration": "Yai khoey yom phae kua khwam fan"},
    {"english": "Love yourself first.", "native": "รักตัวเองก่อน", "transliteration": "Rak tua eng gon"},
    {"english": "Love makes everything possible.", "native": "ความรักทำให้ทุกอย่างเป็นไปได้", "transliteration": "Khwam rak tham hai thuk yang pen pai dai"},
    {"english": "You are loved more than you know.", "native": "คุณถูกรักมากกว่าที่คิด", "transliteration": "Khun thuek rak mak gua thee khit"},
    {"english": "Love is the greatest power.", "native": "ความรักคือพลังที่ยิ่งใหญ่ที่สุด", "transliteration": "Khwam rak khue plang thee ying yai thee sut"},
    {"english": "Spread love everywhere you go.", "native": "แผ่ความรักไปทุกที่ที่คุณไป", "transliteration": "Phae khwam rak pai thuk thee thee khun pai"},
    {"english": "Success comes from hard work.", "native": "ความสำเร็จมาจากความขยัน", "transliteration": "Khwam samret ma jak khwam khayan"},
    {"english": "Keep going, you're getting there.", "native": "ทำต่อไป คุณใกล้จะถึงแล้ว", "transliteration": "Tham toe pai, khun klai ja theung laew"},
    {"english": "Every step counts toward success.", "native": "ทุกก้าวมีค่าสู่ความสำเร็จ", "transliteration": "Thuk kao mee kha soo khwam samret"},
    {"english": "Your effort will pay off.", "native": "ความพยายามของคุณจะไม่สูญเปล่า", "transliteration": "Khwam phayayam khong khun ja mai suen plao"},
    {"english": "Success is a journey, not a destination.", "native": "ความสำเร็จคือการเดินทาง ไม่ใช่จุดหมายปลายทาง", "transliteration": "Khwam samret khue kan dern thang, mai chai jut mai plai thang"},
    {"english": "Knowledge is power.", "native": "ความรู้คือพลัง", "transliteration": "Khwam ru khue plang"},
    {"english": "Learn from yesterday, live for today.", "native": "เรียนรู้จากเมื่อวาน มีชีวิตเพื่อวันนี้", "transliteration": "Rian ru jak muan wan, mee chiwit phuea wan nee"},
    {"english": "The wise learn from others' mistakes.", "native": "คนฉลาดเรียนรู้จากความผิดของคนอื่น", "transliteration": "Khon chalat rian ru jak khwam phit khong khon uen"},
    {"english": "Experience is the best teacher.", "native": "ประสบการณ์เป็นครูที่ดีที่สุด", "transliteration": "Prasopkan khue khru thee dee thee sut"},
    {"english": "Wisdom comes with age.", "native": "ภูมิปัญญามาพร้อมกับวัย", "transliteration": "Phoompanya ma phrom gap wai"},
    {"english": "Happiness is a choice.", "native": "ความสุขคือการเลือก", "transliteration": "Khwam suk khue kan lueak"},
    {"english": "Find joy in the little things.", "native": "หาความสุขจากสิ่งเล็กๆ", "transliteration": "Ha khwam suk jak sing lek lek"},
    {"english": "Your happiness matters most.", "native": "ความสุขของคุณสำคัญที่สุด", "transliteration": "Khwam suk khong khun samkan thee sut"},
    {"english": "Smile, it makes others happy.", "native": "ยิ้มสิ มันทำให้คนอื่นมีความสุข", "transliteration": "Yim si, man tham hai khon uen mee khwam suk"},
    {"english": "Happiness is contagious, spread it.", "native": "ความสุขติดต่อได้ แผ่มันออกไป", "transliteration": "Khwam suk tit to dai, phae man ok pai"},
    {"english": "Better today than yesterday.", "native": "วันนี้ดีกว่าเมื่อวาน", "transliteration": "Wan nee dee gua muan wan"},
    {"english": "Small steps lead to big changes.", "native": "ก้าวเล็กๆ นำไปสู่การเปลี่ยนแปลงครั้งใหญ่", "transliteration": "Kao lek lek nam pai soo kan plian plaeng khrang yai"},
    {"english": "Invest in yourself daily.", "native": "ลงทุนในตัวเองทุกวัน", "transliteration": "Longthun nai tua eng thuk wan"},
    {"english": "Growth requires discomfort.", "native": "การเติบโตต้องการความไม่สบายใจ", "transliteration": "Kan tertbo tongkan khwam mai sabai jai"},
    {"english": "Be your own competition.", "native": "เป็นคู่แข่งของตัวเอง", "transliteration": "Pen khoo khaeng khong tua eng"},
    {"english": "I am grateful for today.", "native": "ผมขอบคุณสำหรับวันนี้", "transliteration": "Phom kobkhun samrap wan nee"},
    {"english": "Thank you for everything.", "native": "ขอบคุณสำหรับทุกอย่าง", "transliteration": "Kobkhun samrap thuk yang"},
    {"english": "Gratitude turns what we have into enough.", "native": "ความกตัญญูเปลี่ยนสิ่งที่เรามีให้เพียงพอ", "transliteration": "Khwam katanyu plian sing thee rao mee hai phiang po"},
    {"english": "Count your blessings daily.", "native": "นับความโชคดีของคุณทุกวัน", "transliteration": "Nap khwam chok dee khong khun thuk wan"},
    {"english": "A grateful heart is a happy heart.", "native": "ใจที่กตัญญูคือใจที่มีความสุข", "transliteration": "Jai thee katanyu khue jai thee mee khwam suk"},
    {"english": "Friends make life better.", "native": "เพื่อนทำให้ชีวิตดีขึ้น", "transliteration": "Phuean tham hai chiwit dee khuen"},
    {"english": "A true friend is always there.", "native": "เพื่อนแท้มีให้เสมอ", "transliteration": "Phuean thae mee hai samoe"},
    {"english": "Friendship is a precious gift.", "native": "มิตรภาพเป็นของขวัญล้ำค่า", "transliteration": "Mittraphap khue khong khwan lam kha"},
    {"english": "Good friends are like stars.", "native": "เพื่อนที่ดีเหมือนดวงดาว", "transliteration": "Phuean thee dee muean duang dao"},
    {"english": "Cherish your true friends.", "native": "ทนุทะนุมเพื่อนแท้ของคุณ", "transliteration": "Thanusnu phuean thae khong khun"},
    {"english": "Hope never dies.", "native": "ความหวังไม่เคยดับสูญ", "transliteration": "Khwam wang mai khoey dap suen"},
    {"english": "Tomorrow is a new beginning.", "native": "พรุ่งนี้คือการเริ่มต้นใหม่", "transliteration": "Prung nee khue kan term ton mai"},
    {"english": "Keep hope alive in your heart.", "native": "รักษาความหวังไว้ในใจ", "transliteration": "Raksa khwam wang wai nai jai"},
    {"english": "Hope is the light in darkness.", "native": "ความหวังคือแสงสว่างในความมืด", "transliteration": "Khwam wang khue saeng suwang nai khwam mue"},
    {"english": "Where there's hope, there's life.", "native": "ที่ไหนมีความหวัง ที่นั่นมีชีวิต", "transliteration": "Thee nai mee khwam wang, thee nan mee chiwit"},
    {"english": "Create something beautiful today.", "native": "สร้างสิ่งที่สวยงามวันนี้", "transliteration": "Sang sing thee suay ngam wan nee"},
    {"english": "Your creativity is unique.", "native": "ความคิดสร้างสรรค์ของคุณไม่เหมือนใคร", "transliteration": "Khwam khid sang san khong khun mai muean khrai"},
    {"english": "Let your imagination run wild.", "native": "ปล่อยให้จินตนาการไปกับมัน", "transliteration": "Ploi hai jintanakan pai gap man"},
    {"english": "Art comes from the heart.", "native": "ศิลปะมาจากหัวใจ", "transliteration": "Sinlapa ma jak hua jai"},
    {"english": "Every day is a canvas.", "native": "ทุกวันคือผ้าใบ", "transliteration": "Thuk wan khue pha pai"},
    {"english": "Find peace within yourself.", "native": "หาความสงบจากภายในตัวคุณ", "transliteration": "Ha khwam sa-ngop jak phai nai tua khun"},
    {"english": "Calm mind, happy heart.", "native": "ใจสงบ หัวใจมีความสุข", "transliteration": "Jai sa-ngop, hua jai mee khwam suk"},
    {"english": "Peace begins with a smile.", "native": "สันติภาพเริ่มต้นจากรอยยิ้ม", "transliteration": "Santiparb term ton jak roi yim"},
    {"english": "Breathe deeply, let go.", "native": "หายใจลึกๆ แล้วปล่อยวาง", "transliteration": "Hai jai luek luek laew ploi wang"},
    {"english": "Your inner peace is precious.", "native": "ความสงบภายในของคุณมีค่า", "transliteration": "Khwam sa-ngop phai nai khong khun mee kha"},
    {"english": "Believe you can, you're right.", "native": "เชื่อว่าคุณทำได้ คุณก็ทำได้จริง", "transliteration": "Cheua wa khun tham dai, khun ko tham dai jing"},
    {"english": "You are stronger than you think.", "native": "คุณแข็งแกร่งกว่าที่คิด", "transliteration": "Khun khaeng kraeng gua thee khit"},
    {"english": "Confidence comes from within.", "native": "ความมั่นใจมาจากภายใน", "transliteration": "Khwam man jai ma jak phai nai"},
    {"english": "Stand tall, be proud.", "native": "ยืดอกตรง และภูมิใจ", "transliteration": "Yeut ok tong, lae phoom jai"},
    {"english": "You have what it takes.", "native": "คุณมีสิ่งที่จำเป็น", "transliteration": "Khun mee sing thee jam pen"},
    {"english": "Never give up, keep going.", "native": "อย่ายอมแพ้ ทำต่อไป", "transliteration": "Yai yom phae, tham toe pai"},
    {"english": "Persistence beats talent.", "native": "ความอดทนชนะพรสวรรค์", "transliteration": "Khwam od ton chana phorasoan"},
    {"english": "Fall seven times, rise eight.", "native": "ล้มเจ็ดครั้ง ลุกแปดครั้ง", "transliteration": "Lom jet khrang, luk paet khrang"},
    {"english": "Hard work pays off eventually.", "native": "ความขยันมีผลตอบแทนในที่สุด", "transliteration": "Khwam khayan mee phon thop than nai thee sut"},
    {"english": "Stay the course, don't quit.", "native": "มุมมั่นอย่าท้อถอย", "transliteration": "Mum man yai to thoi"},
    {"english": "Let inspiration guide you.", "native": "ให้แรงบันดาลใจนำทางคุณ", "transliteration": "Hai rang bandal jai nam thang khun"},
    {"english": "Be the inspiration others need.", "native": "เป็นแรงบันดาลใจที่คนอื่นต้องการ", "transliteration": "Pen rang bandal jai thee khon uen tongkan"},
    {"english": "Inspire by example, not words.", "native": "สร้างแรงบันดาลใจด้วยการกระทำ ไม่ใช่คำพูด", "transliteration": "Sang rang bandal jai duay kan gratham, mai chai kham phut"},
    {"english": "Your story inspires others.", "native": "เรื่องราวของคุณสร้างแรงบันดาลใจให้คนอื่น", "transliteration": "Rueang rao khong khun sang rang bandal jai hai khon uen"},
    {"english": "Find inspiration in nature.", "native": "หาแรงบันดาลใจจากธรรมชาติ", "transliteration": "Ha rang bandal jai jak tham machat"},
    {"english": "Choose positivity every day.", "native": "เลือกความเชิงบวกทุกวัน", "transliteration": "Lueak khwam choeng buak thuk wan"},
    {"english": "Positive thoughts create positive life.", "native": "ความคิดเชิงบวกสร้างชีวิตเชิงบวก", "transliteration": "Khwam khid choeng buak sang chiwit choeng buak"},
    {"english": "Surround yourself with positivity.", "native": "ล้อมรอบตัวด้วยสิ่งเชิงบวก", "transliteration": "Lorm rop tua duay sing choeng buak"},
    {"english": "Every day is a fresh start.", "native": "ทุกวันคือการเริ่มต้นใหม่", "transliteration": "Thuk wan khue kan term ton mai"},
    {"english": "Live life with a positive heart.", "native": "ใช้ชีวิตด้วยใจเชิงบวก", "transliteration": "Chai chiwit duay jai choeng buak"},
    {"english": "Be brave, take the leap.", "native": "กล้าๆ เสี่ยงๆ", "transliteration": "Kla kla, sieng sieng"},
    {"english": "Courage is not absence of fear.", "native": "ความกล้าไม่ใช่การไม่กลัว", "transliteration": "Khwam kla mai chai kan mai klua"},
    {"english": "Face your fears with courage.", "native": "เผชิญความกลัวด้วยความกล้า", "transliteration": "Phachoen khwam klua duay khwam kla"},
    {"english": "Brave hearts change the world.", "native": "หัวใจกล้าเปลี่ยนโลก", "transliteration": "Hua jai kla plian lok"},
    {"english": "Courage grows with use.", "native": "ความกล้าเติบโตด้วยการใช้", "transliteration": "Khwam kla tert bo duay kan chai"},
    {"english": "Be kind to everyone you meet.", "native": "ใจดีกับทุกคนที่คุณพบ", "transliteration": "Jai dee gap thuk khon thee khun phop"},
    {"english": "Kindness costs nothing, means everything.", "native": "ความเมตตาไม่ต้องใช้เงิน แต่มีค่าทุกอย่าง", "transliteration": "Khwam metta mai tong chai ngoen, tae mee kha thuk yang"},
    {"english": "A kind word warms the heart.", "native": "คำดีๆ อบอุ่นหัวใจ", "transliteration": "Kham dee dee, op un hua jai"},
    {"english": "Spread kindness wherever you go.", "native": "แผ่ความเมตตาไปทุกที่", "transliteration": "Phae khwam metta pai thuk thee"},
    {"english": "Kindness makes the world better.", "native": "ความเมตตาทำให้โลกดีขึ้น", "transliteration": "Khwam metta tham hai lok dee khuen"},
    {"english": "Good things come to those who wait.", "native": "สิ่งดีๆ มาถึงคนที่รอคอย", "transliteration": "Sing dee dee ma theung khon thee ro koi"},
    {"english": "Patience is a virtue.", "native": "ความอดทนเป็นคุณธรรม", "transliteration": "Khwam od ton khue khun tham"},
    {"english": "Take your time, don't rush.", "native": "ใช้เวลาของคุณ อย่าเร่งรีบ", "transliteration": "Chai wela khong khun, yai reng rip"},
    {"english": "Patience brings peace of mind.", "native": "ความอดทนนำมาซึ่งสันติสุขในใจ", "transliteration": "Khwam od ton nam ma sue khwam sa-ngop nai jai"},
    {"english": "Wait patiently, trust the process.", "native": "รอด้วยความอดทน เชื่อมั่นในขั้นตอน", "transliteration": "Ro duay khwam od ton, cheua man nai kan ton"},
    {"english": "Forgive and set yourself free.", "native": "ให้อภัยและปลดปล่อยตัวเอง", "transliteration": "Hai a-phai lap plot ploi tua eng"},
    {"english": "Forgiveness is a gift to yourself.", "native": "การให้อภัยเป็นของขวัญให้ตัวเอง", "transliteration": "Kan hai a-phai khue khong khwan hai tua eng"},
    {"english": "Let go of grudges, find peace.", "native": "ปล่อยวางความโกรธ หาสันติสุข", "transliteration": "Ploi wang khwam groat, ha khwam sa-ngop"},
    {"english": "To err is human, to forgive divine.", "native": "มนุษย์ย่อมผิดพลาด การให้อภัยคือสิ่งศักดิ์สิทธิ์", "transliteration": "Manut yom phit phlad, kan hai a-phai khue sing saksit"},
    {"english": "Forgiveness heals all wounds.", "native": "การให้อภัยรักษาบาดแผลทั้งหมด", "transliteration": "Kan hai a-phai raksa bat phaloe thang mot"},
    {"english": "You are stronger than you know.", "native": "คุณแข็งแกร่งกว่าที่คิด", "transliteration": "Khun khaeng kraeng gua thee khit"},
    {"english": "Strength comes from within.", "native": "ความแข็งแกร่งมาจากภายใน", "transliteration": "Khwam khaeng kraeng ma jak phai nai"},
    {"english": "Your struggles develop your strength.", "native": "การต่อสู้พัฒนาความแข็งแกร่งของคุณ", "transliteration": "Kan to-su phatthana khwam khaeng kraeng khong khun"},
    {"english": "Be strong, stay steady.", "native": "เข้มแข็งและมั่นคง", "transliteration": "Khem khaeng lae man khong"},
    {"english": "Inner strength conquers all.", "native": "พลังภายในพิชิตทุกสิ่ง", "transliteration": "Plang phai nai phichit thuk sing"},
    {"english": "Find joy in every moment.", "native": "หาความปีติยินดีในทุกช่วงเวลา", "transliteration": "Ha khwam pi-ti-yin-dee nai thuk chuang we-la"},
    {"english": "Joy is contagious, spread it.", "native": "ความปีติยินดีติดต่อกันได้ แผ่ออกไป", "transliteration": "Khwam pi-ti-yin-dee tit to gan dai, phae ok pai"},
    {"english": "Let joy fill your heart today.", "native": "ให้ความปีติยินดีเติมเต็มหัวใจวันนี้", "transliteration": "Hai khwam pi-ti-yin-dee term tem hua jai wan nee"},
    {"english": "Choose joy over worry.", "native": "เลือกความปีติยินดีแทนความกังวล", "transliteration": "Lueak khwam pi-ti-yin-dee thaen khwam gang-won"},
    {"english": "Joy is the simplest form of gratitude.", "native": "ความปีติยินดีคือรูปธรรมของความกตัญญูที่เรียบง่ายที่สุด", "transliteration": "Khwam pi-ti-yin-dee khue rup tham khong khwam katanyu thee riap ngai thee sut"},
    {"english": "Find balance in your life.", "native": "หาความสมดุลในชีวิต", "transliteration": "Ha khwam som-dun nai chiwit"},
    {"english": "Balance is the key to happiness.", "native": "ความสมดุลคือกุญแจสู่ความสุข", "transliteration": "Khwam som-dun khue kun-jae soo khwam suk"},
    {"english": "Work hard, rest well.", "native": "ทำงานหนัก พักผ่อนให้เพียงพอ", "transliteration": "Tham ngan nak, phak-phon hai phiang po"},
    {"english": "A balanced life is a peaceful life.", "native": "ชีวิตที่สมดุลคือชีวิตที่สงบ", "transliteration": "Chiwit thee som-dun khue chiwit thee sa-ngop"},
    {"english": "Prioritize what matters most.", "native": "ให้ความสำคัญกับสิ่งที่สำคัญที่สุด", "transliteration": "Hai khwam sam-kan gap sing thee sam-kan thee sut"},
    {"english": "Growth happens outside your comfort zone.", "native": "การเติบโตเกิดขึ้นนอกเขตความสบาย", "transliteration": "Kan tert-bo koed khuen nok khaet khwam sa-bai"},
    {"english": "Embrace change, grow stronger.", "native": "ยอมรับการเปลี่ยนแปลง เติบโตให้แข็งแกร่ง", "transliteration": "Yom-rap kan plian-plaeng, tert-bo hai khaeng-kraeng"},
    {"english": "Every challenge is a growth opportunity.", "native": "ทุกความท้าทายคือโอกาสพัฒนา", "transliteration": "Thuk khwam tha-thai khue o-kat phatthana"},
    {"english": "Grow through what you go through.", "native": "เติบโตผ่านสิ่งที่คุณเผชิญ", "transliteration": "Tert-bo phan sing thee khun pha-choen"},
    {"english": "Personal growth is a lifelong journey.", "native": "การพัฒนาตนเองเป็นการเดินทางตลอดชีวิต", "transliteration": "Kan phatthana ton eng pen kan dern thang ta-lot chi-wit"},
    {"english": "Find your purpose, live it.", "native": "ค้นหาจุดมุ่งหมาย และใช้ชีวิตตามนั้น", "transliteration": "Khon ha jut mung-mai, lae chai chi-wit tam nan"},
    {"english": "Purpose gives life meaning.", "native": "จุดมุ่งหมายให้ความหมายกับชีวิต", "transliteration": "Jut mung-mai hai khwam mai gap chiwit"},
    {"english": "Live with purpose and passion.", "native": "ใช้ชีวิตด้วยจุดมุ่งหมายและความหลงใหล", "transliteration": "Chai chiwit duay jut mung mai lae khwam long-lai"},
    {"english": "Your purpose is your calling.", "native": "จุดมุ่งหมายของคุณคือภารกิจ", "transliteration": "Jut mung-mai khong khun khue pha-ra-kit"},
    {"english": "Discover purpose in everyday moments.", "native": "ค้นพบจุดมุ่งหมายในช่วงเวลาประจำวัน", "transliteration": "Khon phop jut mung-mai nai chuang we-la pra-jam wan"},
    {"english": "Be present in this moment.", "native": "อยู่กับปัจจุบัน", "transliteration": "Yu gap pat-ju-ban"},
    {"english": "Mindfulness brings inner peace.", "native": "สตินำมาซึ่งความสงบภายใน", "transliteration": "Sat-ti nam ma sue-sang khwam sa-ngop phai nai"},
    {"english": "Breathe deeply, stay mindful.", "native": "หายใจลึกๆ ตั้งสติให้ดี", "transliteration": "Hai jai luek-luek, tang sat-ti hai dee"},
    {"english": "The present moment is all we have.", "native": "ปัจจุบันคือสิ่งที่เรามี", "transliteration": "Pat-ju-ban khue sing thee rao mee"},
    {"english": "Practice mindfulness daily.", "native": "ฝึกสติทุกวัน", "transliteration": "Fuek sat-ti thuk wan"},
]
# ==== FALLBACK PHRASES END ====


def _load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_phrase_history():
    data = _load_json(PHRASE_HISTORY_FILE, {"phrases": [], "last_updated": None})
    data.setdefault("phrases", [])
    return data


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    _save_json(PHRASE_HISTORY_FILE, data)


def is_phrase_used(english):
    english_lower = english.lower().strip()
    for p in load_phrase_history()["phrases"]:
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def _history_native(p):
    for key in (PHRASE_KEY, "vietnamese", "native", "translation", "target"):
        value = p.get(key)
        if value:
            return str(value)
    return ""


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            PHRASE_KEY: phrase["native"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat(),
        })
    save_phrase_history(history)
    print(f"[content] Saved {len(phrases)} phrases (history total: {len(history['phrases'])})")


def get_available_category():
    data = _load_json(RECENT_CATEGORIES_FILE, {"recent_categories": [], "last_updated": None})
    recent = data.get("recent_categories", [])
    available = [c for c in CATEGORIES if c not in recent]
    if not available:
        recent = recent[-5:]
        available = [c for c in CATEGORIES if c not in recent]
        print("[rotation] Reset recent categories")
    selected = random.choice(available)
    recent.append(selected)
    data["recent_categories"] = recent[-MAX_RECENT_CATEGORIES:]
    data["last_updated"] = datetime.now().isoformat()
    _save_json(RECENT_CATEGORIES_FILE, data)
    print(f"[rotation] Category: {selected} ({len(available)} available)")
    return selected


def _normalize_phrase(item):
    if not isinstance(item, dict):
        return None
    english = str(item.get("english", "")).strip()
    native = str(
        item.get(PHRASE_KEY)
        or item.get("native")
        or item.get("vietnamese")
        or item.get("translation")
        or ""
    ).strip()
    translit = str(item.get("transliteration") or item.get("romanization") or item.get("romaji") or "").strip()
    if not english or not native:
        return None
    if len(english.split()) > 16:
        return None
    if "/" in native or "|" in native:
        native = native.split("/")[0].split("|")[0].strip()
    return {
        "english": english.replace("  ", " ").strip(),
        "native": native.strip(),
        "transliteration": translit.strip().strip("[]"),
    }


def _history_keys(history):
    used_en = set()
    used_nat = set()
    for p in history.get("phrases", []):
        en = str(p.get("english", "")).lower().strip()
        nat = _history_native(p).lower().strip()
        if en:
            used_en.add(en)
        if nat:
            used_nat.add(nat)
    return used_en, used_nat


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    history = load_phrase_history()
    used_en, used_nat = _history_keys(history)
    recent_english = [
        p["english"] for p in history["phrases"] if p.get("category") == category_english
    ][-30:]

    models = [config.AI_MODEL]
    if "gemini-fast" not in models:
        models.append("gemini-fast")

    if config.POLLINATIONS_API_KEY:
        for attempt in range(5):
            model = models[0] if attempt < 3 else models[-1]
            try:
                phrases = _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model)
                unique = []
                for item in phrases:
                    p = _normalize_phrase(item)
                    if not p:
                        continue
                    key_en = p["english"].lower().strip()
                    key_nat = p["native"].lower().strip()
                    if key_en in used_en or key_nat in used_nat:
                        continue
                    if any(key_en == u["english"].lower().strip() for u in unique):
                        continue
                    used_en.add(key_en)
                    used_nat.add(key_nat)
                    unique.append(p)
                    if len(unique) >= num_phrases:
                        break
                if len(unique) >= num_phrases:
                    add_phrases_to_history(unique[:num_phrases], category_english)
                    return unique[:num_phrases]
                print(f"[content] Attempt {attempt + 1}: only {len(unique)} fresh phrases (need {num_phrases})")
            except Exception as exc:  # noqa: BLE001 - network boundary
                print(f"[content] Attempt {attempt + 1} failed ({model}): {exc}")
            time.sleep(1.5 * (attempt + 1))
    else:
        print("[content] No POLLINATIONS_API_KEY, using fallback phrases")

    fresh_fallback = []
    for p in FALLBACK_PHRASES:
        if p["english"].lower().strip() in used_en or p["native"].lower().strip() in used_nat:
            continue
        fresh_fallback.append(p)
    if not fresh_fallback:
        raise RuntimeError("Phrase API unavailable and no unused fallback phrases left; refusing to reuse phrases")
    chosen = fresh_fallback[:num_phrases]
    if len(chosen) < num_phrases:
        print(f"[content] Only {len(chosen)} fresh fallback phrases; building a shorter lesson")
    add_phrases_to_history(chosen, category_english)
    return chosen


def _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model=None):
    avoid = ""
    if recent_english:
        avoid = "\nDo NOT reuse any of these phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

    prompt = f"""Create {num_phrases * 6} unique {category_english} phrases for English speakers learning {LANGUAGE_NAME}.
{avoid}

Rules:
1. Keep every phrase short and natural (4-11 words in English).
2. Use natural commas for TTS breathing pauses.
3. Each phrase must be speakable in 2-4 seconds.
4. Write clean {LANGUAGE_NAME} in {NATIVE_NAME} with correct accents and orthography. One translation only, no slashes.
5. Transliteration is a friendly Roman-script pronunciation guide for English speakers (not IPA).
6. Vary the sentence patterns and emotions. No duplicates.
7. Phrases must feel like real everyday language, not textbook filler.

Return ONLY a JSON array:
[{{"english": "...", "native": "...", "transliteration": "..."}}]"""

    response = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.POLLINATIONS_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model or config.AI_MODEL,
            "messages": [
                {"role": "system", "content": f"You are a {LANGUAGE_NAME} teacher creating short, natural, varied bilingual phrases. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": min(0.95 + attempt * 0.02, 1.0),
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()

    start = content.find("[")
    end = content.rfind("]")
    if start >= 0 and end > start:
        content = content[start:end + 1]

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("AI did not return a JSON array")
    return data
