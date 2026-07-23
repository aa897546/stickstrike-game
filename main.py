import math
import os
import random
from array import array
from pathlib import Path
import pygame

WIDTH, HEIGHT, FLOOR, FPS = 960, 540, 445, 60
WHITE, CYAN, PINK, GOLD = (238, 247, 255), (99, 245, 255), (255, 77, 145), (255, 211, 78)
PALETTE = [CYAN, PINK, GOLD, (139, 255, 129), (181, 128, 255), (255, 126, 75)]
DIFFICULTIES = [("EASY", .010, 2.4, 6), ("NORMAL", .018, 3.4, 8), ("HARD", .030, 4.5, 10)]
LEVELS = [
    {"name": "NEON DOJO", "enemies": 1, "time": 75, "target": 700, "color": CYAN},
    {"name": "ROOFTOP RUSH", "enemies": 2, "time": 90, "target": 1500, "color": GOLD},
    {"name": "VOID CHAMPION", "enemies": 3, "time": 110, "target": 2600, "color": PINK},
]
WEAPONS = {
    "BAT": {"damage": 17, "range": 112, "uses": 7, "color": GOLD},
    "SWORD": {"damage": 22, "range": 132, "uses": 5, "color": CYAN},
    "BLADE": {"damage": 20, "range": 118, "uses": 6, "color": WHITE},
    "HAMMER": {"damage": 29, "range": 104, "uses": 3, "color": PINK},
    "SPEAR": {"damage": 24, "range": 158, "uses": 4, "color": (139,255,129)},
}
MOVES = {
    "LP": {"damage": 8, "range": 86, "duration": 16, "active": (5, 10), "knock": 6, "meter": 7},
    "HP": {"damage": 16, "range": 98, "duration": 27, "active": (9, 16), "knock": 11, "meter": 12},
    "LK": {"damage": 11, "range": 105, "duration": 20, "active": (6, 12), "knock": 8, "meter": 9},
    "HK": {"damage": 20, "range": 124, "duration": 31, "active": (11, 18), "knock": 14, "meter": 14},
    "ULT": {"damage": 38, "range": 175, "duration": 42, "active": (14, 25), "knock": 20, "meter": 0},
}
COMBOS = {
    ("LP", "LP", "HP"): ("RAPID BREAK", 8),
    ("LK", "LK", "HK"): ("CYCLONE KICK", 10),
    ("LP", "LK", "HP"): ("NEON FINISH", 12),
}
LANGUAGES = ["English", "繁體中文", "简体中文", "日本語", "한국어", "Español", "Français", "Deutsch", "Italiano", "Português", "Русский", "العربية", "हिन्दी", "ไทย", "Tiếng Việt", "Bahasa Indonesia"]
LANGUAGE_CODES = ["EN", "ZH-TW", "ZH-CN", "JA", "KO", "ES", "FR", "DE", "IT", "PT", "RU", "AR", "HI", "TH", "VI", "ID"]
TEXT = {
    "English": {"level_mode":"LEVEL MODE","arcade":"ARCADE FIGHT","options":"OPTIONS","custom":"CUSTOMIZE","quit":"QUIT","back":"BACK","language":"Language","difficulty":"Difficulty","rounds":"Rounds to win","music":"Music volume","sfx":"Sound volume","select_level":"SELECT LEVEL","start_level":"START LEVEL","pause":"PAUSED","resume":"RESUME","restart":"RESTART","main_menu":"MAIN MENU","complete":"LEVEL COMPLETE","failed":"MISSION FAILED","score":"SCORE","retry":"RETRY LEVEL","level_select":"LEVEL SELECT","pickup":"PICK UP"},
    "繁體中文": {"level_mode":"關卡模式","arcade":"街機對戰","options":"選項","custom":"角色外觀","quit":"離開","back":"返回","language":"語言","difficulty":"難度","rounds":"勝利回合數","music":"音樂音量","sfx":"音效音量","select_level":"選擇關卡","start_level":"開始關卡","pause":"遊戲暫停","resume":"繼續","restart":"重新開始","main_menu":"主選單","complete":"關卡完成","failed":"任務失敗","score":"分數","retry":"重新挑戰","level_select":"關卡選擇","pickup":"拾取"},
    "简体中文": {"level_mode":"关卡模式","arcade":"街机对战","options":"选项","custom":"角色外观","quit":"退出","back":"返回","language":"语言","difficulty":"难度","rounds":"胜利回合数","music":"音乐音量","sfx":"音效音量","select_level":"选择关卡","start_level":"开始关卡","pause":"游戏暂停","resume":"继续","restart":"重新开始","main_menu":"主菜单","complete":"关卡完成","failed":"任务失败","score":"分数","retry":"重新挑战","level_select":"关卡选择","pickup":"拾取"},
    "日本語": {"level_mode":"ステージモード","arcade":"アーケード対戦","options":"オプション","custom":"カスタマイズ","quit":"終了","back":"戻る","language":"言語","difficulty":"難易度","rounds":"勝利ラウンド","music":"音楽音量","sfx":"効果音音量","select_level":"ステージ選択","start_level":"開始","pause":"一時停止","resume":"再開","restart":"やり直す","main_menu":"メインメニュー","complete":"ステージクリア","failed":"ミッション失敗","score":"スコア","retry":"再挑戦","level_select":"ステージ選択","pickup":"拾う"},
    "한국어": {"level_mode":"레벨 모드","arcade":"아케이드 대전","options":"옵션","custom":"캐릭터 설정","quit":"종료","back":"뒤로","language":"언어","difficulty":"난이도","rounds":"승리 라운드","music":"음악 음량","sfx":"효과음 음량","select_level":"레벨 선택","start_level":"레벨 시작","pause":"일시 정지","resume":"계속","restart":"다시 시작","main_menu":"메인 메뉴","complete":"레벨 완료","failed":"미션 실패","score":"점수","retry":"재도전","level_select":"레벨 선택","pickup":"줍기"},
    "Español": {"level_mode":"MODO NIVELES","arcade":"LUCHA ARCADE","options":"OPCIONES","custom":"PERSONALIZAR","quit":"SALIR","back":"VOLVER","language":"Idioma","difficulty":"Dificultad","rounds":"Rondas para ganar","music":"Volumen música","sfx":"Volumen efectos","select_level":"ELEGIR NIVEL","start_level":"INICIAR NIVEL","pause":"PAUSA","resume":"CONTINUAR","restart":"REINICIAR","main_menu":"MENÚ PRINCIPAL","complete":"NIVEL COMPLETADO","failed":"MISIÓN FALLIDA","score":"PUNTOS","retry":"REINTENTAR","level_select":"ELEGIR NIVEL","pickup":"RECOGER"},
    "Français": {"level_mode":"MODE NIVEAUX","arcade":"COMBAT ARCADE","options":"OPTIONS","custom":"PERSONNALISER","quit":"QUITTER","back":"RETOUR","language":"Langue","difficulty":"Difficulté","rounds":"Manches gagnantes","music":"Volume musique","sfx":"Volume effets","select_level":"CHOISIR NIVEAU","start_level":"COMMENCER","pause":"PAUSE","resume":"REPRENDRE","restart":"RECOMMENCER","main_menu":"MENU PRINCIPAL","complete":"NIVEAU TERMINÉ","failed":"MISSION ÉCHOUÉE","score":"SCORE","retry":"RÉESSAYER","level_select":"CHOISIR NIVEAU","pickup":"RAMASSER"},
    "Deutsch": {"level_mode":"LEVELMODUS","arcade":"ARCADE-KAMPF","options":"OPTIONEN","custom":"ANPASSEN","quit":"BEENDEN","back":"ZURÜCK","language":"Sprache","difficulty":"Schwierigkeit","rounds":"Siegrunden","music":"Musiklautstärke","sfx":"Effektlautstärke","select_level":"LEVEL WÄHLEN","start_level":"LEVEL STARTEN","pause":"PAUSE","resume":"FORTSETZEN","restart":"NEUSTART","main_menu":"HAUPTMENÜ","complete":"LEVEL GESCHAFFT","failed":"MISSION FEHLGESCHLAGEN","score":"PUNKTE","retry":"WIEDERHOLEN","level_select":"LEVEL WÄHLEN","pickup":"AUFHEBEN"},
    "Italiano": {"level_mode":"MODALITÀ LIVELLI","arcade":"LOTTA ARCADE","options":"OPZIONI","custom":"PERSONALIZZA","quit":"ESCI","back":"INDIETRO","language":"Lingua","difficulty":"Difficoltà","rounds":"Round da vincere","music":"Volume musica","sfx":"Volume effetti","select_level":"SCEGLI LIVELLO","start_level":"INIZIA LIVELLO","pause":"PAUSA","resume":"CONTINUA","restart":"RICOMINCIA","main_menu":"MENU PRINCIPALE","complete":"LIVELLO COMPLETATO","failed":"MISSIONE FALLITA","score":"PUNTEGGIO","retry":"RIPROVA","level_select":"SCEGLI LIVELLO","pickup":"RACCOGLI"},
    "Português": {"level_mode":"MODO DE FASES","arcade":"LUTA ARCADE","options":"OPÇÕES","custom":"PERSONALIZAR","quit":"SAIR","back":"VOLTAR","language":"Idioma","difficulty":"Dificuldade","rounds":"Rounds para vencer","music":"Volume da música","sfx":"Volume dos efeitos","select_level":"ESCOLHER FASE","start_level":"INICIAR FASE","pause":"PAUSADO","resume":"CONTINUAR","restart":"REINICIAR","main_menu":"MENU PRINCIPAL","complete":"FASE CONCLUÍDA","failed":"MISSÃO FALHOU","score":"PONTOS","retry":"TENTAR NOVAMENTE","level_select":"ESCOLHER FASE","pickup":"PEGAR"},
    "Русский": {"level_mode":"РЕЖИМ УРОВНЕЙ","arcade":"АРКАДНЫЙ БОЙ","options":"НАСТРОЙКИ","custom":"ПЕРСОНАЖ","quit":"ВЫХОД","back":"НАЗАД","language":"Язык","difficulty":"Сложность","rounds":"Раундов для победы","music":"Громкость музыки","sfx":"Громкость эффектов","select_level":"ВЫБОР УРОВНЯ","start_level":"НАЧАТЬ УРОВЕНЬ","pause":"ПАУЗА","resume":"ПРОДОЛЖИТЬ","restart":"ЗАНОВО","main_menu":"ГЛАВНОЕ МЕНЮ","complete":"УРОВЕНЬ ПРОЙДЕН","failed":"МИССИЯ ПРОВАЛЕНА","score":"СЧЁТ","retry":"ПОВТОРИТЬ","level_select":"ВЫБОР УРОВНЯ","pickup":"ПОДОБРАТЬ"},
    "العربية": {"level_mode":"وضع المراحل","arcade":"قتال أركيد","options":"الإعدادات","custom":"تخصيص","quit":"خروج","back":"رجوع","language":"اللغة","difficulty":"الصعوبة","rounds":"جولات الفوز","music":"صوت الموسيقى","sfx":"صوت المؤثرات","select_level":"اختر المرحلة","start_level":"ابدأ المرحلة","pause":"توقف مؤقت","resume":"متابعة","restart":"إعادة","main_menu":"القائمة الرئيسية","complete":"اكتملت المرحلة","failed":"فشلت المهمة","score":"النقاط","retry":"إعادة المحاولة","level_select":"اختيار المرحلة","pickup":"التقاط"},
    "हिन्दी": {"level_mode":"लेवल मोड","arcade":"आर्केड लड़ाई","options":"विकल्प","custom":"रूप बदलें","quit":"बाहर","back":"वापस","language":"भाषा","difficulty":"कठिनाई","rounds":"जीत के राउंड","music":"संगीत आवाज़","sfx":"ध्वनि आवाज़","select_level":"लेवल चुनें","start_level":"लेवल शुरू","pause":"रुका हुआ","resume":"जारी रखें","restart":"फिर शुरू","main_menu":"मुख्य मेनू","complete":"लेवल पूरा","failed":"मिशन असफल","score":"स्कोर","retry":"फिर प्रयास","level_select":"लेवल चुनें","pickup":"उठाएँ"},
    "ไทย": {"level_mode":"โหมดด่าน","arcade":"ต่อสู้อาร์เคด","options":"ตัวเลือก","custom":"ปรับแต่ง","quit":"ออก","back":"กลับ","language":"ภาษา","difficulty":"ความยาก","rounds":"รอบที่ต้องชนะ","music":"ระดับเสียงเพลง","sfx":"ระดับเสียงเอฟเฟกต์","select_level":"เลือกด่าน","start_level":"เริ่มด่าน","pause":"หยุดชั่วคราว","resume":"เล่นต่อ","restart":"เริ่มใหม่","main_menu":"เมนูหลัก","complete":"ผ่านด่าน","failed":"ภารกิจล้มเหลว","score":"คะแนน","retry":"ลองใหม่","level_select":"เลือกด่าน","pickup":"เก็บ"},
    "Tiếng Việt": {"level_mode":"CHẾ ĐỘ MÀN","arcade":"ĐẤU ARCADE","options":"TÙY CHỌN","custom":"TÙY BIẾN","quit":"THOÁT","back":"QUAY LẠI","language":"Ngôn ngữ","difficulty":"Độ khó","rounds":"Số hiệp thắng","music":"Âm lượng nhạc","sfx":"Âm lượng hiệu ứng","select_level":"CHỌN MÀN","start_level":"BẮT ĐẦU","pause":"TẠM DỪNG","resume":"TIẾP TỤC","restart":"CHƠI LẠI","main_menu":"MENU CHÍNH","complete":"HOÀN THÀNH","failed":"NHIỆM VỤ THẤT BẠI","score":"ĐIỂM","retry":"THỬ LẠI","level_select":"CHỌN MÀN","pickup":"NHẶT"},
    "Bahasa Indonesia": {"level_mode":"MODE LEVEL","arcade":"TARUNG ARCADE","options":"PENGATURAN","custom":"KUSTOMISASI","quit":"KELUAR","back":"KEMBALI","language":"Bahasa","difficulty":"Kesulitan","rounds":"Ronde kemenangan","music":"Volume musik","sfx":"Volume efek","select_level":"PILIH LEVEL","start_level":"MULAI LEVEL","pause":"DIJEDA","resume":"LANJUT","restart":"ULANGI","main_menu":"MENU UTAMA","complete":"LEVEL SELESAI","failed":"MISI GAGAL","score":"SKOR","retry":"COBA LAGI","level_select":"PILIH LEVEL","pickup":"AMBIL"},
}
MUSIC_TEXT = {
    "English": ("CUSTOM MUSIC", "No tracks in music folder", "Built-in soundtrack"),
    "繁體中文": ("切換自訂音樂", "music 資料夾內沒有音樂", "內建背景音樂"),
    "简体中文": ("切换自定义音乐", "music 文件夹内没有音乐", "内置背景音乐"),
    "日本語": ("カスタム音楽", "musicフォルダーに曲がありません", "内蔵BGM"),
    "한국어": ("사용자 음악", "music 폴더에 음악이 없습니다", "기본 배경음악"),
    "Español": ("MÚSICA PERSONAL", "No hay pistas en music", "Música integrada"),
    "Français": ("MUSIQUE PERSONNELLE", "Aucune piste dans music", "Musique intégrée"),
    "Deutsch": ("EIGENE MUSIK", "Keine Titel im music-Ordner", "Integrierte Musik"),
    "Italiano": ("MUSICA PERSONALE", "Nessun brano in music", "Musica integrata"),
    "Português": ("MÚSICA PERSONALIZADA", "Sem faixas na pasta music", "Música integrada"),
    "Русский": ("СВОЯ МУЗЫКА", "В папке music нет файлов", "Встроенная музыка"),
    "العربية": ("موسيقى مخصصة", "لا توجد ملفات في music", "الموسيقى المدمجة"),
    "हिन्दी": ("अपना संगीत", "music फ़ोल्डर खाली है", "अंतर्निहित संगीत"),
    "ไทย": ("เพลงที่กำหนดเอง", "ไม่มีเพลงในโฟลเดอร์ music", "เพลงในเกม"),
    "Tiếng Việt": ("NHẠC TÙY CHỌN", "Không có nhạc trong thư mục music", "Nhạc mặc định"),
    "Bahasa Indonesia": ("MUSIK KUSTOM", "Tidak ada musik di folder music", "Musik bawaan"),
}
CUSTOM_TEXT = {
    "English": ("HEAD","BODY","EYES","AURA","HEADBAND","CAPE","ENERGY RING","OPEN MUSIC FOLDER","NEXT TRACK"),
    "繁體中文": ("頭型","身形","眼睛","光環","頭帶","披風","能量環","開啟音樂資料夾","下一首"),
    "简体中文": ("头型","身形","眼睛","光环","头带","披风","能量环","打开音乐文件夹","下一首"),
    "日本語": ("頭","体型","目","オーラ","鉢巻","マント","エナジーリング","音楽フォルダーを開く","次の曲"),
    "한국어": ("머리","체형","눈","오라","머리띠","망토","에너지 링","음악 폴더 열기","다음 곡"),
}

def custom_labels(language): return CUSTOM_TEXT.get(language,CUSTOM_TEXT["English"])
MUSIC_DIR = Path(__file__).resolve().parent / "music"
MUSIC_EXTENSIONS = {".wav", ".ogg", ".mp3"}
FONT_FILES = {
    "繁體中文": "NotoSansTC-VF.ttf", "简体中文": "NotoSansSC-VF.ttf", "日本語": "NotoSansJP-VF.ttf", "한국어": "NotoSansKR-VF.ttf",
    "العربية": "Nirmala.ttc", "हिन्दी": "Nirmala.ttc", "ไทย": "LeelawUI.ttf",
}

def font_candidates(language):
    if language in ("繁體中文",): return ["microsoftjhenghei", "mingliuextb", "segoeui"]
    if language in ("简体中文",): return ["microsoftyahei", "simsun", "segoeui"]
    if language == "日本語": return ["yugothic", "meiryo", "msgothic"]
    if language == "한국어": return ["malgungothic", "gulim", "segoeui"]
    if language in ("العربية", "हिन्दी"): return ["nirmalaui", "segoeui", "arial"]
    if language == "ไทย": return ["leelawadeeui", "tahoma", "segoeui"]
    return ["segoeui", "arial", "dejavusans"]

def ui_font(language, size, bold=False):
    direct=Path("C:/Windows/Fonts")/FONT_FILES.get(language,"")
    if direct.is_file(): return pygame.font.Font(str(direct),size)
    for candidate in font_candidates(language):
        path=pygame.font.match_font(candidate,bold=bold)
        if path: return pygame.font.Font(path,size)
    return pygame.font.Font(None,size)

def draw_weapon(surface,x,y,kind,facing=1,scale=1):
    x,y=int(x),int(y); s=max(1,int(scale)); color=WEAPONS[kind]["color"]
    def rect(dx,dy,w,h,c): pygame.draw.rect(surface,c,(x+dx*facing-(w if facing<0 else 0),y+dy,w,h))
    if kind=="SWORD":
        rect(-4,-3,10*s,6*s,(112,72,35)); rect(3,-2,25*s,4*s,color); rect(27,-4,8*s,8*s,WHITE)
    elif kind=="BLADE":
        rect(-5,-3,10*s,6*s,(95,60,32)); pygame.draw.polygon(surface,color,[(x+4*facing,y-2),(x+28*facing,y-5),(x+35*facing,y),(x+28*facing,y+5),(x+4*facing,y+2)])
    elif kind=="HAMMER":
        rect(-2,-2,28*s,4*s,(126,78,38)); rect(22,-13,15*s,24*s,color)
    elif kind=="SPEAR":
        rect(-5,-2,42*s,4*s,(125,82,42)); pygame.draw.polygon(surface,color,[(x+36*facing,y-8),(x+52*facing,y),(x+36*facing,y+8)])
    else:
        rect(-4,-4,38*s,8*s,color); rect(27,-6,10*s,12*s,(116,72,34))

def available_music():
    MUSIC_DIR.mkdir(exist_ok=True)
    return sorted(p for p in MUSIC_DIR.iterdir() if p.is_file() and p.suffix.lower() in MUSIC_EXTENSIONS)

def make_tone(frequency, duration=.12, volume=.35):
    rate=22050; frames=int(rate*duration); samples=array("h")
    for i in range(frames):
        fade=max(0,1-i/frames); value=int(32767*volume*fade*math.sin(math.tau*frequency*i/rate))
        samples.extend((value,value))
    return pygame.mixer.Sound(buffer=samples.tobytes())

def make_music():
    rate=22050; samples=array("h"); notes=[110,138.59,164.81,220,164.81,138.59]
    for note in notes:
        frames=int(rate*.32)
        for i in range(frames):
            value=int(5000*math.sin(math.tau*note*i/rate)+2200*math.sin(math.tau*note*2*i/rate))
            samples.extend((value,value))
    return pygame.mixer.Sound(buffer=samples.tobytes())


class WeaponPickup:
    def __init__(self, x, kind):
        self.x, self.y, self.kind = float(x), FLOOR - 13, kind
        self.phase = random.random() * math.tau

    def draw(self, surface, ticks, font):
        y = int(self.y + math.sin(ticks * .006 + self.phase) * 5)
        color = WEAPONS[self.kind]["color"]
        pygame.draw.circle(surface, (*color, 30), (int(self.x), y), 25)
        draw_weapon(surface,int(self.x)-12,y,self.kind,1,1)
        label = font.render(self.kind, True, color)
        surface.blit(label, label.get_rect(center=(int(self.x), y - 28)))


class Fighter:
    def __init__(self, x, color, facing, style=None):
        self.spawn_x, self.color, self.spawn_facing = x, color, facing
        self.style = style or {"head":0,"aura":True,"band":False,"body":0,"eyes":0,"cape":False,"ring":False}
        self.reset()

    def reset(self):
        self.x, self.y, self.vx, self.vy = float(self.spawn_x), float(FLOOR), 0.0, 0.0
        self.hp, self.facing, self.attack_timer = 100, self.spawn_facing, 0
        self.attack_hit, self.hurt_timer = False, 0
        self.weapon, self.weapon_uses = None, 0
        self.action, self.guard = None, False
        self.ultimate, self.combo_bonus = 0, 0
        self.combo_name, self.combo_display = "", 0
        self.combo_buffer, self.combo_timer = [], 0

    @property
    def grounded(self): return self.y >= FLOOR

    def jump(self):
        if self.grounded and self.hurt_timer <= 0: self.vy = -13.5

    def attack(self, move="LP"):
        if move == "ULT" and self.ultimate < 100: return False
        if self.attack_timer <= 0 and self.hurt_timer <= 0:
            data = MOVES[move]
            self.action, self.attack_timer, self.attack_hit = move, data["duration"], False
            self.guard = False
            if move == "ULT": self.ultimate = 0
            else:
                self.combo_buffer.append(move); self.combo_buffer = self.combo_buffer[-3:]; self.combo_timer = 45
                key = tuple(self.combo_buffer)
                if key in COMBOS:
                    self.combo_name, self.combo_bonus = COMBOS[key]
                    self.combo_display, self.combo_buffer = 75, []
            return True
        return False

    def pickup(self, item):
        self.weapon = item.kind
        self.weapon_uses = WEAPONS[item.kind]["uses"]

    def update(self):
        self.vy += .72; self.x += self.vx; self.y += self.vy; self.vx *= .76
        if self.y >= FLOOR: self.y, self.vy = FLOOR, 0
        self.x = max(55, min(WIDTH - 55, self.x))
        self.attack_timer = max(0, self.attack_timer - 1)
        self.hurt_timer = max(0, self.hurt_timer - 1)
        self.combo_timer = max(0, self.combo_timer - 1); self.combo_display = max(0, self.combo_display - 1)
        if self.combo_timer == 0: self.combo_buffer = []
        if self.attack_timer == 0: self.action = None

    def try_hit(self, target, base_damage):
        if not self.action: return 0
        move = MOVES[self.action]
        weapon = WEAPONS.get(self.weapon, {})
        attack_range = max(move["range"], weapon.get("range", 0))
        damage = move["damage"] + self.combo_bonus
        if self.weapon and self.action != "ULT": damage += max(0, weapon["damage"] - 10)
        elapsed = move["duration"] - self.attack_timer
        active = move["active"][0] <= elapsed <= move["active"][1]
        if active and not self.attack_hit and abs(self.x-target.x) < attack_range and abs(self.y-target.y) < 65:
            self.attack_hit = True
            blocked = target.guard and target.hurt_timer <= 0 and target.facing == -self.facing
            actual = max(1, int(damage * .22)) if blocked else damage
            target.hp = max(0, target.hp-actual); target.hurt_timer = 4 if blocked else 12
            target.vx, target.vy = self.facing * (3 if blocked else move["knock"]), -1 if blocked else -4
            self.ultimate = min(100, self.ultimate + move["meter"] + (4 if blocked else 8))
            target.ultimate = min(100, target.ultimate + actual * .7)
            if self.weapon:
                self.weapon_uses -= 1
                if self.weapon_uses <= 0: self.weapon = None
            self.combo_bonus = 0
            return actual
        return 0

    def draw(self, surface, ticks):
        x, y = int(self.x), int(self.y)
        stride = math.sin(ticks*.018)*13 if self.grounded and abs(self.vx)>.3 else 0
        lean = -self.facing*10 if self.hurt_timer else self.vx*.6
        progress = math.sin(math.pi * (1-self.attack_timer/max(1,MOVES.get(self.action,{"duration":1})["duration"]))) if self.attack_timer else 0
        punch = max(0, progress) * (55 if self.weapon else 43)
        color = WHITE if self.hurt_timer and (ticks//60)%2 else self.color
        def pt(dx, dy): return int(x+dx*self.facing), int(y+dy)
        line_width=(5,8,11)[self.style.get("body",1)%3]
        if self.style.get("cape"):
            pygame.draw.polygon(surface,(*self.color[:3],),[pt(-3,-62),pt(-35,-42),pt(-25,-4),pt(2,-22)])
        if self.style.get("ring"):
            pygame.draw.ellipse(surface,self.color,(x-46,y-18,92,18),3)
        if self.style["aura"]:
            aura = pygame.Surface((150,150), pygame.SRCALPHA)
            pygame.draw.circle(aura, (*self.color, 26), (75,75), 55); surface.blit(aura,(x-75,y-125))
        if self.action == "ULT":
            pygame.draw.circle(surface, WHITE, (x,y-55), 72, 3); pygame.draw.circle(surface, self.color, (x,y-55), 62, 5)
        head = pt(lean,-82)
        if self.style["head"] == 0:
            pygame.draw.circle(surface,(8,11,18),head,16); pygame.draw.circle(surface,color,head,16,7)
        elif self.style["head"] == 1:
            pygame.draw.rect(surface,(8,11,18),(head[0]-15,head[1]-15,30,30),border_radius=3); pygame.draw.rect(surface,color,(head[0]-15,head[1]-15,30,30),7,border_radius=3)
        else:
            pts=[(head[0],head[1]-19),(head[0]+18,head[1]+15),(head[0]-18,head[1]+15)]
            pygame.draw.polygon(surface,(8,11,18),pts); pygame.draw.polygon(surface,color,pts,7)
        if self.style.get("eyes"):
            eye_color=GOLD if self.style["eyes"]==1 else PINK
            pygame.draw.circle(surface,eye_color,pt(6+lean,-84),3)
            if self.style["eyes"]==2: pygame.draw.line(surface,eye_color,pt(2+lean,-88),pt(12+lean,-82),3)
        if self.style["band"]:
            pygame.draw.line(surface,PINK,pt(lean-18,-85),pt(lean+18,-85),5); pygame.draw.line(surface,PINK,pt(lean-17,-85),pt(lean-32,-75),4)
        is_kick = self.action in ("LK","HK")
        is_heavy = self.action in ("HP","HK","ULT")
        arm_reach = 0 if is_kick else punch * (1.35 if is_heavy else 1)
        kick_reach = max(0,progress) * (78 if is_heavy else 58) if is_kick else stride
        hand = pt(20+arm_reach,-43-arm_reach*.12)
        guard_arm = (8,-68) if self.guard else (20+arm_reach,-43-arm_reach*.12)
        for a,b in [((lean,-65),(0,-20)),((lean-1,-55),guard_arm),((lean-2,-53),(-8,-70) if self.guard else (-22,-34)),((0,-20),(20+kick_reach,-34 if is_kick else 0)),((0,-20),(-18-stride,0))]:
            pygame.draw.line(surface,color,pt(*a),pt(*b),line_width)
        if self.weapon:
            draw_weapon(surface,hand[0],hand[1],self.weapon,self.facing,1)


class Button:
    def __init__(self, rect, text, action): self.rect, self.text, self.action = pygame.Rect(rect), text, action
    def draw(self, screen, font, mouse):
        hover=self.rect.collidepoint(mouse)
        pygame.draw.rect(screen,(18,31,48) if hover else (12,20,33),self.rect,border_radius=5)
        pygame.draw.rect(screen,CYAN if hover else (47,69,94),self.rect,2,border_radius=5)
        label=font.render(self.text,True,WHITE if hover else (184,201,219)); screen.blit(label,label.get_rect(center=self.rect.center))


def background(screen, accent=CYAN):
    screen.fill((7,12,23))
    for y in range(HEIGHT):
        shade=int(9+y/HEIGHT*10); pygame.draw.line(screen,(shade,shade+3,shade+14),(0,y),(WIDTH,y))
    for x in range(0,WIDTH,48): pygame.draw.line(screen,(17,34,50),(x,0),(x,HEIGHT))
    for y in range(0,HEIGHT,48): pygame.draw.line(screen,(17,34,50),(0,y),(WIDTH,y))
    pygame.draw.circle(screen,(42,18,42),(WIDTH//2,225),132); pygame.draw.circle(screen,accent,(WIDTH//2,225),88,3)
    pygame.draw.rect(screen,(5,7,13),(0,FLOOR+3,WIDTH,HEIGHT-FLOOR)); pygame.draw.line(screen,accent,(0,FLOOR+2),(WIDTH,FLOOR+2),4)


def centered(screen,font,text,y,color=WHITE):
    img=font.render(text,True,color); screen.blit(img,img.get_rect(center=(WIDTH//2,y)))


def draw_star(surface, center, radius, filled):
    pts=[]
    for i in range(10):
        angle=-math.pi/2+i*math.pi/5; r=radius if i%2==0 else radius*.45
        pts.append((center[0]+math.cos(angle)*r,center[1]+math.sin(angle)*r))
    pygame.draw.polygon(surface,GOLD if filled else (48,55,70),pts)
    pygame.draw.polygon(surface,GOLD,pts,2)


def hud(screen,player,enemy,font,small,score,time_left,level,score_label="SCORE"):
    pygame.draw.rect(screen,(9,13,22),(0,0,WIDTH,78)); pygame.draw.line(screen,(34,48,71),(0,78),(WIDTH,78))
    screen.blit(small.render(f"{score_label} {score:05d}",True,GOLD),(28,13))
    screen.blit(small.render(f"LEVEL {level+1}: {LEVELS[level]['name']}",True,LEVELS[level]["color"]),(28,35))
    weapon=f"{player.weapon} x{player.weapon_uses}" if player.weapon else "UNARMED"
    screen.blit(small.render(weapon,True,player.color),(28,56))
    pygame.draw.rect(screen,(23,32,49),(245,50,255,9)); pygame.draw.rect(screen,GOLD,(248,53,int(249*player.ultimate/100),3))
    pygame.draw.rect(screen,(23,32,49),(245,25,255,17)); pygame.draw.rect(screen,player.color,(248,28,int(249*player.hp/100),11))
    pygame.draw.rect(screen,(23,32,49),(WIDTH-355,25,255,17)); ew=int(249*enemy.hp/100); pygame.draw.rect(screen,enemy.color,(WIDTH-103-ew,28,ew,11))
    timer=font.render(str(max(0,int(time_left))),True,WHITE); screen.blit(timer,timer.get_rect(center=(WIDTH//2,58)))

def arcade_hud(screen,player,enemy,font,small,wins,rounds):
    pygame.draw.rect(screen,(9,13,22),(0,0,WIDTH,78)); pygame.draw.line(screen,(34,48,71),(0,78),(WIDTH,78))
    screen.blit(small.render(f"PLAYER  {wins[0]}/{rounds}",True,player.color),(28,14))
    cpu=small.render(f"CPU  {wins[1]}/{rounds}",True,enemy.color); screen.blit(cpu,(WIDTH-28-cpu.get_width(),14))
    pygame.draw.rect(screen,(23,32,49),(28,42,365,18),border_radius=5)
    pygame.draw.rect(screen,player.color,(32,46,int(357*player.hp/100),10),border_radius=4)
    pygame.draw.rect(screen,(23,32,49),(WIDTH-393,42,365,18),border_radius=5)
    ew=int(357*enemy.hp/100); pygame.draw.rect(screen,enemy.color,(WIDTH-32-ew,46,ew,10),border_radius=4)
    pygame.draw.rect(screen,(23,32,49),(360,65,240,7),border_radius=3)
    pygame.draw.rect(screen,GOLD,(360,65,int(240*player.ultimate/100),7),border_radius=3)
    versus=font.render("VS",True,WHITE); screen.blit(versus,versus.get_rect(center=(WIDTH//2,34)))


def main():
    pygame.mixer.pre_init(22050,-16,2,512); pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT)); pygame.display.set_caption("STICKSTRIKE")
    clock=pygame.time.Clock(); title=pygame.font.SysFont("arialblack",68,bold=True)
    state,difficulty,rounds,color_index,selected_level="menu",1,2,0,0
    language_index,music_volume,sfx_volume=0,.45,.65
    large=ui_font(LANGUAGES[language_index],34,True); font=ui_font(LANGUAGES[language_index],22,True); small=ui_font(LANGUAGES[language_index],14,True)
    audio_enabled=pygame.mixer.get_init() is not None
    sounds={"light":make_tone(420),"heavy":make_tone(180,.18),"kick":make_tone(270,.15),"hit":make_tone(90,.2),"pickup":make_tone(720,.2),"ultimate":make_tone(70,.5)} if audio_enabled else {}
    music=make_music() if audio_enabled else None; music_tracks=available_music(); music_track_index=-1; music_status=MUSIC_TEXT[LANGUAGES[language_index]][2]
    if music: music.set_volume(music_volume); music.play(loops=-1)
    def tr(key): return TEXT[LANGUAGES[language_index]].get(key,TEXT["English"].get(key,key))
    def play(name):
        if name in sounds: sounds[name].set_volume(sfx_volume); sounds[name].play()
    def apply_music_volume():
        if music: music.set_volume(music_volume)
        if audio_enabled: pygame.mixer.music.set_volume(music_volume)
    style={"head":0,"aura":True,"band":False,"body":1,"eyes":0,"cape":False,"ring":False}; wins=[0,0]; round_done=False
    score,stars,level_start,enemies_left=0,0,0,0; pickups=[]; next_drop=0; level_complete=False
    player=Fighter(245,PALETTE[color_index],1,style); enemy=Fighter(715,PINK,-1,{"head":1,"aura":True,"band":False})

    def new_match():
        nonlocal wins,round_done,player,enemy,enemies_left
        wins=[0,0]; round_done=False; enemies_left=0
        player=Fighter(245,PALETTE[color_index],1,style); enemy=Fighter(715,PINK,-1,{"head":1,"aura":True,"band":False})

    def new_level():
        nonlocal player,enemy,score,stars,level_start,enemies_left,pickups,next_drop,level_complete,round_done
        cfg=LEVELS[selected_level]; player=Fighter(180,PALETTE[color_index],1,style)
        enemy=Fighter(750,PINK,-1,{"head":(selected_level+1)%3,"aura":True,"band":selected_level==2})
        score,stars,level_start,enemies_left=0,0,pygame.time.get_ticks(),cfg["enemies"]
        pickups=[WeaponPickup(480,random.choice(list(WEAPONS)))]; next_drop=pygame.time.get_ticks()+9000
        level_complete=False; round_done=False

    running=True
    while running:
        mouse=pygame.mouse.get_pos(); click=None; pickup_pressed=False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1: click=event.pos
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: state="pause" if state in ("game","level_game") else ("level_game" if state=="pause" and enemies_left else "game" if state=="pause" else "menu")
                if state in ("game","level_game") and not round_done and not level_complete:
                    if event.key in (pygame.K_w,pygame.K_UP): player.jump()
                    if event.key in (pygame.K_j,pygame.K_SPACE) and player.attack("LP"): play("light")
                    if event.key==pygame.K_k and player.attack("HP"): play("heavy")
                    if event.key==pygame.K_u and player.attack("LK"): play("kick")
                    if event.key==pygame.K_i and player.attack("HK"): play("heavy")
                    if event.key==pygame.K_o and player.attack("ULT"): play("ultimate")
                    if event.key in (pygame.K_e,pygame.K_DOWN): pickup_pressed=True

        accent=LEVELS[selected_level]["color"] if state in ("levels","level_game","level_result") else CYAN
        background(screen,accent); buttons=[]
        if state=="menu":
            centered(screen,title,"STICKSTRIKE",105); centered(screen,small,"NEON STICK FIGHTER",150,CYAN)
            buttons=[Button((350,190,260,48),tr("level_mode"),"levels"),Button((350,248,260,48),tr("arcade"),"start"),Button((350,306,260,48),tr("options"),"options"),Button((350,364,260,48),tr("custom"),"custom"),Button((350,422,260,48),tr("quit"),"quit")]
        elif state=="levels":
            centered(screen,large,tr("select_level"),62)
            for i,cfg in enumerate(LEVELS):
                r=pygame.Rect(135+i*235,135,220,235); selected=i==selected_level
                pygame.draw.rect(screen,(18,28,44) if selected else (10,17,29),r,border_radius=8); pygame.draw.rect(screen,cfg["color"] if selected else (48,61,81),r,3,border_radius=8)
                centered_x=r.centerx; n=large.render(str(i+1),True,cfg["color"]); screen.blit(n,n.get_rect(center=(centered_x,180)))
                name=small.render(cfg["name"],True,WHITE); screen.blit(name,name.get_rect(center=(centered_x,225)))
                info=small.render(f"{cfg['enemies']} ENEMIES",True,(150,166,185)); screen.blit(info,info.get_rect(center=(centered_x,270)))
                target=small.render(f"3 STAR: {cfg['target']}",True,GOLD); screen.blit(target,target.get_rect(center=(centered_x,305)))
                if click and r.collidepoint(click): selected_level=i
            buttons=[Button((350,400,260,48),tr("start_level"),"level_start"),Button((350,460,260,42),tr("back"),"menu")]
        elif state=="options":
            centered(screen,large,tr("options"),45)
            centered(screen,font,tr("language"),95,(160,178,201)); centered(screen,font,f"{LANGUAGES[language_index]}  [{LANGUAGE_CODES[language_index]}]",125,CYAN)
            centered(screen,font,tr("difficulty"),170,(160,178,201)); centered(screen,font,DIFFICULTIES[difficulty][0],200,PINK)
            centered(screen,font,tr("rounds"),245,(160,178,201)); centered(screen,font,str(rounds),275,GOLD)
            centered(screen,font,f"{tr('music')}: {int(music_volume*100)}%",325,(160,178,201))
            pygame.draw.rect(screen,(31,43,61),(310,350,340,10),border_radius=5); pygame.draw.rect(screen,CYAN,(310,350,int(340*music_volume),10),border_radius=5)
            centered(screen,font,f"{tr('sfx')}: {int(sfx_volume*100)}%",395,(160,178,201))
            pygame.draw.rect(screen,(31,43,61),(310,420,340,10),border_radius=5); pygame.draw.rect(screen,PINK,(310,420,int(340*sfx_volume),10),border_radius=5)
            status=small.render(music_status,True,(136,154,177)); screen.blit(status,status.get_rect(center=(WIDTH//2,447)))
            labels=custom_labels(LANGUAGES[language_index])
            buttons=[Button((245,105,50,38),"<","lang-"),Button((665,105,50,38),">","lang+"),Button((245,180,50,38),"<","diff-"),Button((665,180,50,38),">","diff+"),Button((245,255,50,38),"-","round-"),Button((665,255,50,38),"+","round+"),Button((245,338,50,38),"-","music-"),Button((665,338,50,38),"+","music+"),Button((245,408,50,38),"-","sfx-"),Button((665,408,50,38),"+","sfx+"),Button((155,458,300,34),labels[7],"open-music"),Button((465,458,150,34),labels[8],"custom-music"),Button((625,458,180,34),tr("back"),"menu")]
        elif state=="custom":
            labels=custom_labels(LANGUAGES[language_index]); centered(screen,large,tr("custom"),48); preview=Fighter(WIDTH//2,PALETTE[color_index],1,style); preview.y=300; preview.draw(screen,pygame.time.get_ticks())
            centered(screen,font,"COLOR",338)
            for i,c in enumerate(PALETTE):
                r=pygame.Rect(322+i*54,358,38,38); pygame.draw.circle(screen,c,r.center,16); pygame.draw.circle(screen,WHITE,r.center,19,3 if i==color_index else 1)
                if click and r.collidepoint(click): color_index=i
            buttons=[Button((80,410,150,34),labels[0],"head"),Button((240,410,150,34),labels[1],"body"),Button((400,410,150,34),labels[2],"eyes"),Button((560,410,150,34),labels[3],"aura"),Button((720,410,150,34),labels[4],"band"),Button((160,458,180,34),labels[5],"cape"),Button((350,458,220,34),labels[6],"ring"),Button((580,458,180,34),tr("back"),"menu")]
        elif state in ("game","level_game","pause"):
            level_mode=state=="level_game" or (state=="pause" and enemies_left>0)
            if state!="pause" and not round_done and not level_complete:
                keys=pygame.key.get_pressed(); direction=int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT])
                player.guard=bool(keys[pygame.K_l] or keys[pygame.K_RSHIFT]) and player.attack_timer<=0 and player.hurt_timer<=0
                player.vx=max(-6,min(6,player.vx+direction*.85)); gap=player.x-enemy.x; player.facing=1 if enemy.x>player.x else -1; enemy.facing=1 if gap>0 else -1
                chance,speed,damage=DIFFICULTIES[difficulty][1:]
                if level_mode: speed+=selected_level*.45; damage+=selected_level*2
                if abs(gap)>82 and enemy.hurt_timer<=0: enemy.vx=max(-speed,min(speed,enemy.vx+(1 if gap>0 else -1)*.42))
                enemy.guard=enemy.attack_timer<=0 and enemy.hurt_timer<=0 and player.attack_timer>0 and random.random()<(.06+selected_level*.02 if level_mode else .05)
                if abs(gap)<125 and enemy.attack_timer<=0 and enemy.hurt_timer<=0 and not enemy.guard and random.random()<chance:
                    if enemy.ultimate>=100 and random.random()<.45: enemy.attack("ULT")
                    else: enemy.attack(random.choices(["LP","HP","LK","HK"],[4,2,3,1])[0])
                player.update(); enemy.update(); dealt=player.try_hit(enemy,10); received=enemy.try_hit(player,damage)
                if dealt: score+=dealt*6+(40 if player.weapon else 0); play("hit")
                if received: play("hit")
                if level_mode:
                    now=pygame.time.get_ticks(); time_left=LEVELS[selected_level]["time"]-(now-level_start)/1000
                    if now>=next_drop and len(pickups)<2: pickups.append(WeaponPickup(random.randint(180,780),random.choice(list(WEAPONS)))); next_drop=now+random.randint(8000,12000)
                    if pickup_pressed:
                        for item in pickups[:]:
                            if abs(player.x-item.x)<55: player.pickup(item); pickups.remove(item); score+=75; play("pickup"); break
                    if enemy.hp<=0:
                        score+=300+int(max(0,time_left)*5); enemies_left-=1
                        if enemies_left<=0:
                            level_complete=True; ratio=score/LEVELS[selected_level]["target"]; stars=3 if ratio>=1 else 2 if ratio>=.6 else 1
                        else:
                            enemy=Fighter(760,PINK,-1,{"head":random.randrange(3),"aura":True,"band":selected_level==2}); player.hp=min(100,player.hp+25)
                    if player.hp<=0 or time_left<=0: level_complete=True; stars=1
                elif player.hp<=0 or enemy.hp<=0:
                    round_done=True; wins[0 if player.hp>0 else 1]+=1
            if level_mode:
                time_left=LEVELS[selected_level]["time"]-(pygame.time.get_ticks()-level_start)/1000
                for item in pickups: item.draw(screen,pygame.time.get_ticks(),small)
                hud(screen,player,enemy,font,small,score,time_left,selected_level,tr("score"))
            else:
                arcade_hud(screen,player,enemy,font,small,wins,rounds)
            player.draw(screen,pygame.time.get_ticks()); enemy.draw(screen,pygame.time.get_ticks())
            help_text="J/K PUNCH  U/I KICK  L GUARD  O ULT  E PICKUP" if level_mode else "J/K PUNCH  U/I KICK  L GUARD  O ULT"
            screen.blit(small.render(help_text,True,(135,150,173)),(22,HEIGHT-28))
            if player.combo_display:
                centered(screen,large,player.combo_name,118,GOLD)
            if player.ultimate>=100:
                ready=small.render("ULTIMATE READY [O]",True,GOLD); screen.blit(ready,ready.get_rect(center=(WIDTH//2,92)))
            if round_done:
                match_over=max(wins)>=rounds; centered(screen,title,"YOU WIN" if wins[0]>wins[1] else "K.O.",260); buttons=[Button((350,330,260,48),tr("main_menu") if match_over else "NEXT ROUND","menu" if match_over else "next")]
            if level_complete: state="level_result"
            if state=="pause":
                shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); shade.fill((2,5,10,210)); screen.blit(shade,(0,0)); centered(screen,large,tr("pause"),180)
                buttons=[Button((350,240,260,50),tr("resume"),"resume_level" if level_mode else "resume"),Button((350,305,260,50),tr("restart"),"level_start" if level_mode else "restart"),Button((350,370,260,50),tr("main_menu"),"menu")]
        elif state=="level_result":
            centered(screen,large,tr("complete") if player.hp>0 else tr("failed"),110,accent)
            centered(screen,font,LEVELS[selected_level]["name"],155); centered(screen,large,f"{tr('score')} {score}",225,GOLD)
            for i in range(3): draw_star(screen,(WIDTH//2-80+i*80,300),30,i<stars)
            target=LEVELS[selected_level]["target"]; centered(screen,small,f"1 STAR: COMPLETE   2 STARS: {int(target*.6)}   3 STARS: {target}",355,(156,171,190))
            buttons=[Button((350,400,260,48),tr("retry"),"level_start"),Button((350,460,260,42),tr("level_select"),"levels")]

        for b in buttons:
            b.draw(screen,font,mouse)
            if click and b.rect.collidepoint(click):
                a=b.action
                if a=="start": new_match(); state="game"
                elif a=="levels": state="levels"
                elif a=="level_start": new_level(); state="level_game"
                elif a=="options": state="options"
                elif a=="custom": state="custom"
                elif a=="menu": state="menu"
                elif a=="quit": running=False
                elif a=="diff-": difficulty=(difficulty-1)%3
                elif a=="diff+": difficulty=(difficulty+1)%3
                elif a in ("lang-","lang+"):
                    language_index=(language_index+(-1 if a=="lang-" else 1))%len(LANGUAGES)
                    large=ui_font(LANGUAGES[language_index],34,True); font=ui_font(LANGUAGES[language_index],22,True); small=ui_font(LANGUAGES[language_index],14,True)
                    music_status=(music_tracks[music_track_index].name if music_track_index>=0 and music_tracks else MUSIC_TEXT[LANGUAGES[language_index]][2])
                elif a=="round-": rounds=max(1,rounds-1)
                elif a=="round+": rounds=min(5,rounds+1)
                elif a=="music-": music_volume=max(0,round(music_volume-.1,1)); apply_music_volume()
                elif a=="music+": music_volume=min(1,round(music_volume+.1,1)); apply_music_volume()
                elif a=="sfx-": sfx_volume=max(0,round(sfx_volume-.1,1)); play("light")
                elif a=="sfx+": sfx_volume=min(1,round(sfx_volume+.1,1)); play("light")
                elif a=="open-music":
                    MUSIC_DIR.mkdir(exist_ok=True)
                    try:
                        os.startfile(str(MUSIC_DIR))
                    except OSError:
                        music_status=str(MUSIC_DIR)
                elif a=="custom-music":
                    music_tracks=available_music()
                    if music_tracks and audio_enabled:
                        music_track_index=(music_track_index+1)%len(music_tracks); music.stop() if music else None
                        try:
                            pygame.mixer.music.load(str(music_tracks[music_track_index])); pygame.mixer.music.set_volume(music_volume); pygame.mixer.music.play(-1)
                            music_status=music_tracks[music_track_index].name
                        except pygame.error:
                            music_status=f"Unsupported: {music_tracks[music_track_index].name}"
                    else:
                        music_status=MUSIC_TEXT[LANGUAGES[language_index]][1]
                elif a=="head": style["head"]=(style["head"]+1)%3
                elif a=="body": style["body"]=(style["body"]+1)%3
                elif a=="eyes": style["eyes"]=(style["eyes"]+1)%3
                elif a=="aura": style["aura"]=not style["aura"]
                elif a=="band": style["band"]=not style["band"]
                elif a=="cape": style["cape"]=not style["cape"]
                elif a=="ring": style["ring"]=not style["ring"]
                elif a=="resume": state="game"
                elif a=="resume_level": state="level_game"
                elif a=="restart": new_match(); state="game"
                elif a=="next": player.reset(); enemy.reset(); round_done=False
        pygame.display.flip(); clock.tick(FPS)
    pygame.quit()

if __name__=="__main__": main()
