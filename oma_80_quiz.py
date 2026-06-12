"""
Oma's 80er Millionenshow
A birthday quiz game styled like a blue-green TV quiz show.

Requirements:
    pip install pygame

Folder layout:
    oma_80_quiz.py
    assets/
        oma.jpg              (or .png) — picture of the birthday guest
        millionaire.mp3      — short intro sound played before each question

If a file is missing, the game still runs with a placeholder.
"""

import os
import sys
import math
import random
import pygame

# Optional: pip install opencv-python  (required for "type": "video" questions)
try:
    import cv2 as _cv2
    _CV2_OK = True
except ImportError:
    _cv2 = None
    _CV2_OK = False
    print("[hint] pip install opencv-python  for video question support")

# ---------- Configuration ----------
BASE_WIDTH, BASE_HEIGHT = 1100, 720
WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
FPS = 60
FULLSCREEN = True
UI_SCALE = 1.0

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
IMAGE_CANDIDATES = [
    "oma.JPG", "oma.jpg", "oma.jpeg", "oma.png",
    "klara.JPG", "klara.jpg", "klara.jpeg", "klara.png",
]

# ---------- Sound files ----------
# Each variable is just the filename inside the assets/ folder.
# Swap them around as you like.
SND_OPENING_THEME   = "opening_theme.mp3"    # Eröffnungsmelodie
SND_INTRO           = "intro.mp3"            # Einleitung
SND_CANDIDATE_ENTER = "candidate_enter.mp3"  # Kandidat kommt
SND_ANSWER_LOCKIN   = "answer_lockin.mp3"    # Antwort einloggen
SND_ANSWER_CORRECT  = "answer_correct.mp3"   # Antwort richtig
SND_ANSWER_WRONG    = "answer_wrong.mp3"     # Antwort falsch
SND_TIME_UP         = "time_up.mp3"          # Zeit vorbei
SND_JOKER_50_50     = "joker_50_50.mp3"      # 50:50 Joker
SND_JOKER_AUDIENCE  = "joker_audience.mp3"   # Publikumsjoker
SND_JOKER_PHONE     = "joker_phone.mp3"      # Telefonjoker

# Which sound plays before each question
QUESTION_INTRO_SOUND = SND_INTRO
# Which sound plays on the title screen (None = silent)
TITLE_SOUND          = SND_OPENING_THEME
# Played on the first click (selection step)
LOCKIN_SOUND         = SND_ANSWER_LOCKIN
# Played on the second click (reveal step)
CORRECT_SOUND        = SND_ANSWER_CORRECT
WRONG_SOUND          = SND_ANSWER_WRONG
# Jokers
JOKER_AUDIENCE_SOUND = SND_JOKER_AUDIENCE
JOKER_PHONE_SOUND    = SND_JOKER_PHONE
JOKER_50_50_SOUND    = SND_JOKER_50_50
# Bars in the audience joker reveal only after this many total votes
AUDIENCE_REVEAL_AT   = 5

# ---------- Millionenshow palette ----------
PARCHMENT       = (218, 235, 250)    # blue studio surface
PARCHMENT_DARK  = (176, 207, 236)    # panel blue
INK             = (5, 22, 61)
OLIVE           = (0, 166, 121)     # quiz-show green
OLIVE_DARK      = (0, 104, 92)
OLIVE_LIGHT     = (58, 214, 174)
RED             = (29, 92, 180)     # rich answer blue
RED_DARK        = (12, 50, 130)
APEROL          = (0, 128, 184)     # cyan accent
APEROL_DARK     = (0, 77, 130)
APEROL_LIGHT    = (96, 205, 238)
LEMON           = (93, 232, 176)
LEMON_LIGHT     = (162, 255, 219)
LEMON_PEEL      = (0, 188, 142)
CREAM_WHITE     = (246, 252, 255)
BULB            = (96, 205, 238)
BULB_HI         = (190, 255, 235)
MUTED           = (150, 178, 205)

# ---------- Quiz content — edit freely ----------
# 4 categories × 5 questions. Question 1 = easiest, question 5 = hardest.
# Set "answer" to the 0-based index of the correct option.
CATEGORIES = [
    {
        "name": "Allgemeines",
        "color": OLIVE,
        "questions": [
            {"q": "In welchem Jahr fiel die Berliner Mauer?",
             "options": ["1987", "1988", "1989", "1990"], "answer": 2},
            {"q": "Wie heißt die Meeresströmung im Atlantik, die warmes Wasser aus dem Golf von Mexiko nach Europa transportiert?",
             "options": ["Golfstrom", "Kuroshio", "Labradorstrom", "Canarystrom"], "answer": 0},
            {"q": "Welcher Kontinent hat die meisten Einwohner?",
             "options": ["Asien", "Afrika", "Europa", "Nordamerika"], "answer": 0},
            {"q": "Wie nennt man die Angst vor engen Räumen?",
                "options": ["Agoraphobie", "Arachnophobie", "Akrophobie", "Klaustrophobie"], "answer": 3},
            {"q": "Welcher Celebrity ist auch im Jahr 1996 geboren?",
                "options": ["Sydney Sweeney", "Dua Lipa", "Justin Bieber", "Zendaya"], "answer": 3},
            {"q": "Welche Sprache hat weltweit die meisten Muttersprachler?",
                "options": ["Englisch", "Spanisch", "Mandarin", "Hindi"], "answer": 2},
            {"q": "Welches Vitamin bildet der menschliche Körper hauptsächlich durch Sonnenlicht?",
                "options": ["Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D"], "answer": 3},
            {"q": "Wie nennt man den großen rotierenden Teil an der Vorderseite einer Tunnelbohrmaschine, der das Gestein abträgt?",
             "options": ["Schildmantel", "Bohrkopf", "Hydraulikring", "Förderkammer"], "answer": 1},
            {"q": "Welche Hauptaufgabe hat eine Dialysebehandlung?",
             "options": ["Die Produktion roter Blutkörperchen erhöhen", "Den Blutzucker dauerhaft senken", "Sauerstoff direkt ins Blut pumpen", "Das Blut von Abfallstoffen und überschüssigem Wasser reinigen"], "answer": 3},
            {"q": "Zu welchem Reich gehörte Triest über viele Jahrhunderte bis zum Ende des Ersten Weltkriegs?",
                "options": ["Habsburgerreich / Österreich-Ungarn", "Osmanisches Reich", "Französisches Kaiserreich", "Byzantinisches Reich"], "answer": 0},
            {"q": "Seit wann gehört Triest zu Italien?",
                "options": ["1918", "1914", "1933", "1945"], "answer": 0},
            {"q": "Wie viel Prozent Alkohol hat Aperol?",
                "options": ["11%", "15%", "18%", "21%"], "answer": 0}
        ],
    },
    {
        "name": "Nerd Stuff",
        "color": RED,
        "questions": [
            {"q": "Wie heißt der Bruder von Hannah Montana in der gleichnamigen Serie?",
             "options": ["Oliver", "Jackson", "Justin", "Max"], "answer": 1},
            {"q": "Wie lautet der vollständige Name von Detective Ryan in Castle?",
                "options": ["Patrick Ryan", "Sean Ryan", "Kevin Ryan", "Daniel Ryan"], "answer": 2},
            {"q": "Wie heißt Katniss Everdeens jüngere Schwester?",
                "options": ["Primrose", "Rue", "Petunia", "Penelope"], "answer": 0},
            {"q": "Welches Tier erscheint in Patronus-Form von Luna Lovegood?",
             "options": ["Hase", "Fuchs", "Eule", "Kaninchen"], "answer": 0},
            {"q": "Welcher Zaubertrank wird beim Vielsafttrank als letztes hinzugefügt?",
             "options": ["Fluxweed", "Das Körperteil der Zielperson", "Boomslang-Haut", "Florfliegen"], "answer": 1},
            {"q": "Wie lautet der vollständige Name von Dumbledores Phönix?",
             "options": ["Fawkes", "Ferox", "Flame", "Felix"], "answer": 0},
            {"q": "Was befindet sich im Kern von Hermine Grangers Zauberstab?",
             "options": ["Einhornhaar", "Phönixfeder", "Drachenherzfaser", "Veela-Haar"], "answer": 2},
            {"q": "Wie lautet der vollständige Name von Sirius Blacks Bruder?",
             "options": ["Reginald Alphard Black", "Regulus Orion Black", "Rabastan Cygnus Black", "Regulus Arcturus Black"], "answer": 3},
        ],
    },
    {
        "name": "Persönliches",
        "color": APEROL,
        "questions": [
            {"q": "Aus welchem Land hat Papa den Teddybären OTTO mitgebracht?",
             "options": ["Deutschland", "Hongkong", "Italien", "Türkei"], "answer": 1},
            {"q": "An welchem Tag im Jahr hat Jonas seinen Führerschein erhalten?",
             "options": ["17. März", "11. Mai", "7. Jänner", "8. Mai"], "answer": 1},
            {"q": "In welchem Jahr hat Papa den Teddybären OTTO mitgebracht?",
             "options": ["1995", "1996", "1997", "1998"], "answer": 2},
            {"q": "In welchem Jahr hat Klara Chi kennengelernt?",
             "options": ["2000", "2001", "2002", "2003"], "answer": 2},
            {"q": "In welchem Jahr ist Klara in ihre jetzige Wohnung gezogen?",
             "options": ["2010", "2011", "2012", "2013"], "answer": 2},
            {"q": "Um wie viel Uhr ist Klara geboren?",
             "options": ["07:01", "06:59", "07:05", "06:57"], "answer": 0},
            {"q": "Wie war der Name unseres ersten Katers?",
             "options": ["Hera", "Henry", "Zeus", "Harald"], "answer": 2},
            {"q": "Wo haben wir 2013 unsere Sommerurlaub gemacht?",
             "options": ["Hvar", "Toskana", "Sardinien", "Côte d'Azur"], "answer": 3}
        ],
    },
    {
        "name": "Fun Stuff",
        "color": LEMON_PEEL,
        "questions": [
             {
                "type": "ordering",
                "q": "Ordne die Fotos chronologisch – von alt nach neu!",
                "count": 14,
                "photo_prefix": "foto_",   # expects assets/foto_1.jpg … foto_14.jpg
                # correct order: photo numbers from left (oldest) to right (newest)
                "answer": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                "pass_at": 6,              # ≥6 correct positions = point
            },
            {"q": "In welchem Glas ist Alkohol?",
             "description": "Diese Frage beantwortet jemand anders.",
             "options": ["1.", "2.", "3.", "4."], "answer": 1,
             "award_point_on_wrong": True,
             "wrong_point_message": "Falsch - aber Klara bekommt dafür einen Punkt."},
            {
                "type": "audio_text",
                "q": "Wie heißt dieser Song?",
                "audio": "pferd.mp3",
                "answer": "Mädchen auf dem Pferd",
            },
            {
                "type": "audio_text",
                "q": "Wie lautet der Vorname der Künsterlin dieses Songs?",
                "audio": "murderon.mp3",
                "answer": "Sophie",
            },
            {
                "type": "video",
                "q": "Was macht Klara als nächstes?",
                "video": "sturz.mp4",   # place in assets/
                "audio": "sturz.mp3",   # optional: extracted audio (ffmpeg -i sturz.mp4 sturz.mp3)
                "pause_at": 09.0,             # seconds where video freezes
                "options": ["Läuft nochmal zur Kamera hin", "Macht einen Köpfler", "Läuft weiter", "Fällt hin"],
                "answer": 3,
            },
            {
                "type": "video",
                "q": "Was macht Klara als nächstes?",
                "video": "cam_schlag.mp4",   # place in assets/
                "audio": "cam_schlag.mp3",   # optional: extracted audio (ffmpeg -i leck_mich.mp4 leck_mich.mp3)
                "pause_at": 06.0,             # seconds where video freezes
                "options": ["Erschrickt und Kreischt", "Erschrickt und schlägt die Kamera", "Erwartet die Kamera und erschrickt nicht", "Nimmt die Kamera in die Hand und filmt weiter"],
                "answer": 1,
            },
            {
                "type": "video",
                "q": "Welches Buch von Dan Brown las Klara zu diesem Zeitpunkt?",
                "video": "illuminati.mp4",   # place in assets/
                "audio": "illuminati.mp3",   # optional: extracted audio (ffmpeg -i illuminati.mp4 illuminati.mp3)
                "pause_at": 59.5,             # seconds where video freezes
                "stop_at": 65.0,              # optional: seconds where video stops after answer
                "options": ["Inferno", "Illuminati", "Der Da Vinci Code", "Sakrileg"],
                "answer": 1,
            },
            {
                "type": "video",
                "q": "Was sagt Klara als nächstes?",
                "video": "leck_mich.mp4",   # place in assets/
                "audio": "leck_mich.mp3",   # optional: extracted audio (ffmpeg -i leck_mich.mp4 leck_mich.mp3)
                "pause_at": 67.0,             # seconds where video freezes
                "options": ["Gute Nacht", "Nichts", "Sei Leise", "Leck mich"],
                "answer": 3,
            },
           
        ],
    },
]

FUN_STUFF_CATEGORY = "Fun Stuff"


def is_fun_stuff_category(idx):
    return CATEGORIES[idx]["name"] == FUN_STUFF_CATEGORY


def fun_stuff_unlocked(done):
    return all(
        i in done
        for i, category in enumerate(CATEGORIES)
        if category["name"] != FUN_STUFF_CATEGORY
    )

# ---------- Pygame setup ----------
pygame.init()
pygame.mixer.init()
if FULLSCREEN:
    display_info = pygame.display.Info()
    DISPLAY_WIDTH, DISPLAY_HEIGHT = display_info.current_w, display_info.current_h
    UI_SCALE = min(DISPLAY_WIDTH / BASE_WIDTH, DISPLAY_HEIGHT / BASE_HEIGHT)
    WIDTH = int(round(BASE_WIDTH * UI_SCALE))
    HEIGHT = int(round(BASE_HEIGHT * UI_SCALE))
    display_flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
else:
    DISPLAY_WIDTH, DISPLAY_HEIGHT = BASE_WIDTH, BASE_HEIGHT
    WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
    UI_SCALE = 1.0
    display_flags = 0
display_surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), display_flags)
screen = display_surface if (WIDTH, HEIGHT) == (DISPLAY_WIDTH, DISPLAY_HEIGHT) else pygame.Surface((WIDTH, HEIGHT))
SCREEN_OFFSET_X = (DISPLAY_WIDTH - WIDTH) // 2
SCREEN_OFFSET_Y = (DISPLAY_HEIGHT - HEIGHT) // 2
pygame.display.set_caption("Oma's 80er Millionenshow")
clock = pygame.time.Clock()


def scaled(value):
    return int(round(value * UI_SCALE))


def scaled_font(size):
    return max(1, scaled(size))


def get_events():
    events = []
    for event in pygame.event.get():
        if hasattr(event, "pos"):
            attrs = event.dict.copy()
            attrs["pos"] = (event.pos[0] - SCREEN_OFFSET_X,
                            event.pos[1] - SCREEN_OFFSET_Y)
            event = pygame.event.Event(event.type, attrs)
        events.append(event)
    return events


def mouse_pos():
    mx, my = pygame.mouse.get_pos()
    return mx - SCREEN_OFFSET_X, my - SCREEN_OFFSET_Y


def update_display():
    if screen is not display_surface:
        display_surface.fill((0, 0, 0))
        display_surface.blit(screen, (SCREEN_OFFSET_X, SCREEN_OFFSET_Y))
    pygame.display.flip()

# Bold TV-show typography.
SERIF = "arial,helvetica,sans"
FONT_TAGLINE = pygame.font.SysFont(SERIF, scaled_font(30), bold=True)
FONT_TITLE   = pygame.font.SysFont(SERIF, scaled_font(68), bold=True)
FONT_SUB     = pygame.font.SysFont(SERIF, scaled_font(26), bold=True)
FONT_BTN     = pygame.font.SysFont(SERIF, scaled_font(26), bold=True)
FONT_Q       = pygame.font.SysFont(SERIF, scaled_font(34), bold=True)
FONT_OPT     = pygame.font.SysFont(SERIF, scaled_font(24))
FONT_OPT_BD  = pygame.font.SysFont(SERIF, scaled_font(26), bold=True)
FONT_SMALL   = pygame.font.SysFont(SERIF, scaled_font(18), bold=True)


# ---------- Asset loading ----------
def load_portrait():
    portrait_size = scaled(300)
    for name in IMAGE_CANDIDATES:
        path = os.path.join(ASSETS_DIR, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, (portrait_size, portrait_size))
            except pygame.error:
                pass
    surf = pygame.Surface((portrait_size, portrait_size), pygame.SRCALPHA)
    center = portrait_size // 2
    pygame.draw.circle(surf, PARCHMENT_DARK, (center, center), center - scaled(2))
    pygame.draw.circle(surf, OLIVE, (center, center), center - scaled(2), max(1, scaled(2)))
    label = FONT_SMALL.render("add oma.jpg", True, MUTED)
    surf.blit(label, label.get_rect(center=(center, center)))
    return surf


def load_sound(filename):
    if not filename:
        return None
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Could not load sound '{filename}': {e}")
    else:
        print(f"[hint] missing sound file: {path}")
    return None


PORTRAIT      = load_portrait()
INTRO_SOUND   = load_sound(QUESTION_INTRO_SOUND)
TITLE_MUSIC   = load_sound(TITLE_SOUND)
LOCKIN_SFX          = load_sound(LOCKIN_SOUND)
CORRECT_SFX         = load_sound(CORRECT_SOUND)
WRONG_SFX           = load_sound(WRONG_SOUND)
JOKER_AUDIENCE_SFX  = load_sound(JOKER_AUDIENCE_SOUND)
JOKER_PHONE_SFX     = load_sound(JOKER_PHONE_SOUND)
JOKER_50_50_SFX     = load_sound(JOKER_50_50_SOUND)
CANDIDATE_ENTER_SFX = load_sound(SND_CANDIDATE_ENTER)
TITLE_MUSIC_CHANNEL = None


def start_title_music():
    global TITLE_MUSIC_CHANNEL
    if TITLE_MUSIC is None:
        return
    if TITLE_MUSIC_CHANNEL is None or not TITLE_MUSIC_CHANNEL.get_busy():
        TITLE_MUSIC_CHANNEL = TITLE_MUSIC.play(loops=-1)


def stop_title_music(fade_ms=400):
    global TITLE_MUSIC_CHANNEL
    if TITLE_MUSIC_CHANNEL is not None and TITLE_MUSIC_CHANNEL.get_busy():
        TITLE_MUSIC_CHANNEL.fadeout(fade_ms)
    TITLE_MUSIC_CHANNEL = None


def stop_parent_joker_music():
    if JOKER_PHONE_SFX:
        JOKER_PHONE_SFX.stop()


# ---------- Decorative drawing ----------
def draw_studio_background(surf):
    """Blue studio background with a subtle glow and frame."""
    surf.fill(PARCHMENT)
    for y in range(0, HEIGHT, max(1, scaled(3))):
        t = y / max(1, HEIGHT - 1)
        r = int(218 - 42 * t)
        g = int(235 - 58 * t)
        b = int(250 - 55 * t)
        pygame.draw.rect(surf, (r, g, b), (0, y, WIDTH, max(1, scaled(3))))

    cx, cy = WIDTH // 2, HEIGHT // 2
    for radius, alpha in ((scaled(390), 32), (scaled(270), 44), (scaled(150), 56)):
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*OLIVE_LIGHT, alpha), (radius, radius), radius)
        surf.blit(glow, (cx - radius, cy - radius), special_flags=pygame.BLEND_RGBA_ADD)

    grid_col = (26, 80, 150)
    for x in range(scaled(70), WIDTH, scaled(110)):
        pygame.draw.line(surf, grid_col, (x, scaled(110)), (x, HEIGHT - scaled(80)), 1)
    for y in range(scaled(120), HEIGHT - scaled(70), scaled(82)):
        pygame.draw.line(surf, grid_col, (scaled(42), y), (WIDTH - scaled(42), y), 1)

    pygame.draw.rect(surf, OLIVE, (24, 24, WIDTH - 48, HEIGHT - 48), 2, border_radius=18)
    pygame.draw.rect(surf, APEROL_LIGHT, (34, 34, WIDTH - 68, HEIGHT - 68), 1, border_radius=14)


def draw_string_lights(surf, y_anchor=28, sag=22, bulbs=14):
    """Row of studio lights across the top."""
    x_start, x_end = scaled(70), WIDTH - scaled(70)
    pygame.draw.line(surf, APEROL_LIGHT, (x_start, scaled(y_anchor)),
                     (x_end, scaled(y_anchor)), max(1, scaled(2)))
    for i in range(bulbs):
        t = (i + 0.5) / bulbs
        x = int(x_start + (x_end - x_start) * t)
        y = scaled(y_anchor + 6)
        pygame.draw.circle(surf, RED_DARK, (x, y), scaled(10))
        pygame.draw.circle(surf, BULB, (x, y), scaled(6))
        pygame.draw.circle(surf, BULB_HI, (x - scaled(2), y - scaled(2)), scaled(2))


def draw_leaf(surf, cx, cy, angle_deg, length=22, width=9, color=OLIVE):
    """Small light beam used as an accent."""
    beam = pygame.Surface((length, width), pygame.SRCALPHA)
    pygame.draw.ellipse(beam, (*color, 140), (0, 0, length, width))
    rotated = pygame.transform.rotate(beam, -angle_deg)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_light_beams(surf, x, y, angle_deg=0, length=160, leaves=9, flip=False):
    """Fan of studio light beams."""
    rad = math.radians(angle_deg)
    end_x = x + length * math.cos(rad)
    end_y = y + length * math.sin(rad)
    pygame.draw.line(surf, APEROL_LIGHT, (x, y), (end_x, end_y), 2)
    for i in range(1, leaves + 1):
        t = i / (leaves + 1)
        lx = x + (end_x - x) * t
        ly = y + (end_y - y) * t
        side = 1 if (i % 2 == 0) ^ flip else -1
        leaf_angle = angle_deg + side * 38
        ox = lx + math.cos(math.radians(leaf_angle)) * 11
        oy = ly + math.sin(math.radians(leaf_angle)) * 11
        draw_leaf(surf, ox, oy, leaf_angle, length=22, width=8, color=OLIVE)
    pygame.draw.circle(surf, OLIVE_LIGHT, (int(x), int(y)), scaled(5))


def draw_glow_orb(surf, cx, cy, size=18, tilt=-20):
    """Small glowing quiz-show orb."""
    body = pygame.Surface((size * 2, int(size * 1.4)), pygame.SRCALPHA)
    pygame.draw.ellipse(body, LEMON, (0, 0, body.get_width(), body.get_height()))
    pygame.draw.ellipse(body, LEMON_LIGHT, (3, 3, body.get_width() - 8, body.get_height() - 8))
    pygame.draw.ellipse(body, OLIVE_DARK, (0, 0, body.get_width(), body.get_height()), 1)
    rot = pygame.transform.rotate(body, -tilt)
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


def draw_stage_accent(surf, cx, cy, r=11):
    """Small concentric Millionenshow-style accent."""
    pygame.draw.circle(surf, APEROL, (cx, cy), r)
    pygame.draw.circle(surf, RED_DARK, (cx, cy), max(1, r - 4))
    pygame.draw.circle(surf, OLIVE_LIGHT, (cx, cy), max(1, r - 8))
    pygame.draw.circle(surf, APEROL_LIGHT, (cx, cy), r, 1)


def draw_heart(surf, cx, cy, size=10, color=RED):
    """Small diamond light used as an accent."""
    pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, CREAM_WHITE, pts, 1)


def draw_show_bar(surf, cx, cy, w=110, h=16):
    """Blue-green answer-bar accent."""
    cy = scaled(cy) if cy <= BASE_HEIGHT else cy
    w, h = scaled(w), scaled(h)
    x = cx - w // 2
    pygame.draw.rect(surf, RED_DARK, (x, cy - h // 2, w, h), border_radius=scaled(8))
    pygame.draw.rect(surf, APEROL, (x + scaled(8), cy - h // 2 + scaled(3),
                                    w - scaled(16), h - scaled(6)), border_radius=scaled(6))
    pygame.draw.rect(surf, OLIVE_LIGHT, (x + w // 2 - scaled(18), cy - h // 2,
                                         scaled(36), h), border_radius=scaled(6))
    pygame.draw.rect(surf, CREAM_WHITE, (x, cy - h // 2, w, h), max(1, scaled(1)), border_radius=scaled(8))


def draw_divider(surf, y, width=240):
    y = scaled(y) if y <= BASE_HEIGHT else y
    width = scaled(width)
    draw_divider_px(surf, y, width)


def draw_divider_px(surf, y, width=240):
    cx = WIDTH // 2
    pygame.draw.line(surf, APEROL_LIGHT, (cx - width // 2, y), (cx - scaled(26), y), max(1, scaled(2)))
    pygame.draw.line(surf, APEROL_LIGHT, (cx + scaled(26), y), (cx + width // 2, y), max(1, scaled(2)))
    draw_stage_accent(surf, cx, y, r=scaled(10))


def draw_corner_decorations(surf):
    """Stage-light accents in the lower corners."""
    draw_light_beams(surf, 60,        HEIGHT - 70, angle_deg=-25, length=170, leaves=9)
    draw_light_beams(surf, WIDTH - 60, HEIGHT - 70, angle_deg=205, length=170, leaves=9, flip=True)
    draw_glow_orb(surf, 110, HEIGHT - 132, size=18, tilt=-25)
    draw_glow_orb(surf, WIDTH - 110, HEIGHT - 132, size=18, tilt=25)


# ---------- UI helpers ----------
class Button:
    def __init__(self, rect, label, primary=True, raw=False):
        x, y, w, h = rect
        cx, cy = x + w / 2, y + h / 2
        if not raw and x + w <= BASE_WIDTH and abs(cx - WIDTH / 2) > 2:
            cx = scaled(cx)
        if not raw and y + h <= BASE_HEIGHT and y < BASE_HEIGHT * 0.85:
            cy = scaled(cy)
        if not raw:
            w, h = scaled(w), scaled(h)
        self.rect = pygame.Rect(round(cx - w / 2), round(cy - h / 2), w, h)
        self.label = label
        self.hover = False
        self.primary = primary  # primary=blue, secondary=green/cyan

    def draw(self, surf):
        base = RED if self.primary else APEROL
        hi   = RED_DARK if self.primary else APEROL_DARK
        color = hi if self.hover else base
        pygame.draw.rect(surf, color, self.rect, border_radius=scaled(14))
        pygame.draw.rect(surf, INK,   self.rect, max(1, scaled(1)), border_radius=scaled(14))
        # small stage-light accents on the sides
        draw_stage_accent(surf, self.rect.x + scaled(30), self.rect.centery,
                          r=scaled(8))
        draw_stage_accent(surf, self.rect.right - scaled(30), self.rect.centery,
                          r=scaled(8))
        txt = FONT_BTN.render(self.label, True, CREAM_WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class OptionButton:
    def __init__(self, rect, letter, text):
        x, y, w, h = rect
        cx, cy = x + w / 2, y + h / 2
        if x + w <= BASE_WIDTH and abs(cx - WIDTH / 2) > 2:
            cx = scaled(cx)
        if y + h <= BASE_HEIGHT:
            cy = scaled(cy)
        w, h = scaled(w), scaled(h)
        self.rect = pygame.Rect(round(cx - w / 2), round(cy - h / 2), w, h)
        self.letter = letter
        self.text = text
        self.hover = False
        self.state = "idle"  # idle | selected | correct | wrong | dimmed | eliminated

    def draw(self, surf):
        if self.state == "eliminated":
            pygame.draw.rect(surf, PARCHMENT, self.rect, border_radius=scaled(12))
            pygame.draw.rect(surf, PARCHMENT_DARK, self.rect, max(1, scaled(1)), border_radius=scaled(12))
            return
        if self.state == "correct":
            fill, border, fg, badge_fg = OLIVE,         OLIVE_DARK, CREAM_WHITE, CREAM_WHITE
        elif self.state == "wrong":
            fill, border, fg, badge_fg = RED,           RED_DARK,   CREAM_WHITE, CREAM_WHITE
        elif self.state == "dimmed":
            fill, border, fg, badge_fg = PARCHMENT_DARK, MUTED,     MUTED,       MUTED
        elif self.state == "selected":
            fill, border, fg, badge_fg = APEROL_LIGHT,  APEROL_DARK, INK,        APEROL_DARK
        else:
            fill   = CREAM_WHITE if not self.hover else (250, 244, 226)
            border = OLIVE if not self.hover else RED
            fg     = INK
            badge_fg = RED if not self.hover else OLIVE
        border_w = scaled(3) if self.state == "selected" else scaled(2)
        pygame.draw.rect(surf, fill, self.rect, border_radius=scaled(12))
        pygame.draw.rect(surf, border, self.rect, max(1, border_w), border_radius=scaled(12))

        # letter badge (circle)
        bx = self.rect.x + scaled(38)
        by = self.rect.centery
        pygame.draw.circle(surf, PARCHMENT if self.state == "idle" else fill, (bx, by), scaled(20))
        pygame.draw.circle(surf, badge_fg, (bx, by), scaled(20), max(1, scaled(2)))
        letter_surf = FONT_OPT_BD.render(self.letter, True, badge_fg)
        surf.blit(letter_surf, letter_surf.get_rect(center=(bx, by - scaled(1))))

        text_surf = FONT_OPT.render(self.text, True, fg)
        surf.blit(text_surf, (self.rect.x + scaled(78), self.rect.centery - text_surf.get_height() // 2))

    def handle(self, event):
        if self.state not in ("idle", "selected", "correct") or self.state == "eliminated":
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def draw_centered_text(surf, text, font, color, y):
    rendered = font.render(text, True, color)
    draw_y = scaled(y) if y <= BASE_HEIGHT else y
    surf.blit(rendered, rendered.get_rect(center=(WIDTH // 2, draw_y)))


def draw_centered_text_px(surf, text, font, color, y):
    rendered = font.render(text, True, color)
    surf.blit(rendered, rendered.get_rect(center=(WIDTH // 2, y)))


def draw_portrait_framed(surf, center):
    cx, cy = center
    cy = scaled(cy) if cy <= BASE_HEIGHT else cy
    rect = PORTRAIT.get_rect(center=(cx, cy))
    # double frame: outer green, inner cyan
    outer = rect.inflate(scaled(22), scaled(22))
    inner = rect.inflate(scaled(10), scaled(10))
    pygame.draw.rect(surf, OLIVE,    outer, max(1, scaled(2)), border_radius=scaled(10))
    pygame.draw.rect(surf, OLIVE_LIGHT, inner, max(1, scaled(1)), border_radius=scaled(8))
    surf.blit(PORTRAIT, rect)


# ---------- Screens ----------
def title_screen():
    btn = Button((WIDTH // 2 - 200, HEIGHT - 130, 400, 68), "Start the Game", primary=True)
    start_title_music()

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if btn.handle(event):
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_portrait_framed(screen, (WIDTH // 2, 230))

        # Tagline
        draw_centered_text(screen, "Willkommen!", FONT_TAGLINE, OLIVE_DARK, 410)

        # Main title in two lines.
        draw_centered_text(screen, "Welcome to the", FONT_SUB, OLIVE_DARK, 446)
        draw_centered_text(screen, "Millionenshow", FONT_TITLE, RED_DARK, 498)

        # Blue-green accent + subtitle
        draw_show_bar(screen, WIDTH // 2, 542, w=140, h=14)
        draw_centered_text(screen, "Omas 80er Quiz", FONT_SUB, OLIVE_DARK, 580)

        btn.draw(screen)

        update_display()
        clock.tick(FPS)


def play_intro_sound():
    if INTRO_SOUND is None:
        for _ in range(36):
            draw_studio_background(screen)
            draw_corner_decorations(screen)
            draw_centered_text_px(screen, "♪  ♪  ♪", FONT_TITLE, RED, HEIGHT // 2 - scaled(20))
            draw_centered_text_px(screen, "(add assets/millionaire.mp3)", FONT_SMALL, MUTED, HEIGHT // 2 + scaled(50))
            update_display()
            clock.tick(FPS)
        return

    INTRO_SOUND.play()
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1500:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        draw_studio_background(screen)
        draw_corner_decorations(screen)
        draw_centered_text_px(screen, "♪", FONT_TITLE, RED, HEIGHT // 2)
        update_display()
        clock.tick(FPS)


def wrap_text(text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        candidate = (current + " " + w).strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


# ---------- Joker system ----------

_JOKER_RADIUS  = scaled(26)
_JOKER_CENTERS = [
    (WIDTH - scaled(254), scaled(72)),   # index 0 — Publikum
    (WIDTH - scaled(188), scaled(72)),   # index 1 — Mama
    (WIDTH - scaled(122), scaled(72)),   # index 2 — Papa
    (WIDTH - scaled(56),  scaled(72)),   # index 3 — 50:50
]
_JOKER_COLORS  = [OLIVE, APEROL, LEMON_PEEL, RED]
_JOKER_LABELS  = ["PUB", "MAMA", "PAPA", "50:50"]


def draw_joker_icons(surf, used):
    for i, (cx, cy) in enumerate(_JOKER_CENTERS):
        active = not used[i]
        color  = _JOKER_COLORS[i] if active else MUTED
        pygame.draw.circle(surf, color,     (cx, cy), _JOKER_RADIUS)
        pygame.draw.circle(surf, PARCHMENT, (cx, cy), _JOKER_RADIUS, 1)
        lbl = FONT_SMALL.render(_JOKER_LABELS[i], True,
                                CREAM_WHITE if active else PARCHMENT_DARK)
        surf.blit(lbl, lbl.get_rect(center=(cx, cy)))
        if not active:
            d = _JOKER_RADIUS - 8
            pygame.draw.line(surf, PARCHMENT_DARK, (cx-d, cy-d), (cx+d, cy+d), 2)
            pygame.draw.line(surf, PARCHMENT_DARK, (cx+d, cy-d), (cx-d, cy+d), 2)


def joker_clicked(event):
    """Returns joker index if a joker circle was clicked, else -1."""
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return -1
    for i, (cx, cy) in enumerate(_JOKER_CENTERS):
        if math.hypot(event.pos[0] - cx, event.pos[1] - cy) <= _JOKER_RADIUS:
            return i
    return -1


def draw_modal_base(surf, height=420):
    """Semi-transparent veil + quiz-show panel. Returns (px, py, pw, ph)."""
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((18, 15, 10, 170))
    surf.blit(veil, (0, 0))
    pw, ph = scaled(760), scaled(height)
    px, py = (WIDTH - pw) // 2, (HEIGHT - ph) // 2
    pygame.draw.rect(surf, PARCHMENT,    (px, py, pw, ph), border_radius=scaled(18))
    pygame.draw.rect(surf, OLIVE,        (px, py, pw, ph), max(1, scaled(2)), border_radius=scaled(18))
    pygame.draw.rect(surf, OLIVE_LIGHT,  (px + scaled(7), py + scaled(7),
                                          pw - scaled(14), ph - scaled(14)),
                     max(1, scaled(1)), border_radius=scaled(13))
    return px, py, pw, ph


def show_publikum_joker(surf_behind):
    """Live vote overlay — bars are hidden until AUDIENCE_REVEAL_AT total votes."""
    if JOKER_AUDIENCE_SFX:
        JOKER_AUDIENCE_SFX.play()

    votes   = [0, 0, 0, 0]
    letters = ["A", "B", "C", "D"]
    btn     = None

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1): votes[0] += 1
                if event.key in (pygame.K_2, pygame.K_KP2): votes[1] += 1
                if event.key in (pygame.K_3, pygame.K_KP3): votes[2] += 1
                if event.key in (pygame.K_4, pygame.K_KP4): votes[3] += 1
            if btn is not None and btn.handle(event):
                return

        screen.blit(surf_behind, (0, 0))
        px, py, pw, ph = draw_modal_base(screen, height=470)
        if btn is None:
            btn = Button((BASE_WIDTH // 2 - 130, BASE_HEIGHT // 2 + 185,
                          260, 58), "Fertig!", primary=True)

        draw_centered_text_px(screen, "Publikums-Joker", FONT_Q, RED_DARK, py + scaled(52))
        draw_divider_px(screen, py + scaled(78), width=scaled(200))

        total    = sum(votes)
        revealed = total >= AUDIENCE_REVEAL_AT

        if not revealed:
            draw_centered_text_px(screen, "Drückt 1, 2, 3 oder 4 zum Abstimmen!",
                                  FONT_SUB, OLIVE_DARK, py + scaled(115))
            draw_centered_text_px(screen,
                                  f"{total} Stimme{'n' if total != 1 else ''} abgegeben",
                                  FONT_SMALL, MUTED, py + scaled(158))
            dots = "." * ((pygame.time.get_ticks() // 500) % 4)
            draw_centered_text_px(screen, f"Warte auf Stimmen{dots}",
                                  FONT_SMALL, MUTED, py + scaled(184))
        else:
            draw_centered_text_px(screen, "Drückt 1, 2, 3 oder 4 zum Abstimmen!",
                                  FONT_SMALL, MUTED, py + scaled(98))
            bar_x      = px + scaled(120)
            bar_max_w  = pw - scaled(260)
            bar_h, gap = scaled(34), scaled(13)
            bar_start  = py + scaled(122)
            for i in range(4):
                by  = bar_start + i * (bar_h + gap)
                pct = votes[i] / total
                filled = int(bar_max_w * pct)
                lbl = FONT_OPT_BD.render(letters[i], True, OLIVE_DARK)
                screen.blit(lbl, (bar_x - scaled(50), by + bar_h//2 - lbl.get_height()//2))
                pygame.draw.rect(screen, PARCHMENT_DARK, (bar_x, by, bar_max_w, bar_h), border_radius=scaled(8))
                if filled > 0:
                    pygame.draw.rect(screen, OLIVE, (bar_x, by, filled, bar_h), border_radius=scaled(8))
                pygame.draw.rect(screen, OLIVE_DARK, (bar_x, by, bar_max_w, bar_h), max(1, scaled(1)), border_radius=scaled(8))
                pct_lbl = FONT_SMALL.render(f"{round(pct*100)} %", True, INK)
                screen.blit(pct_lbl, (bar_x + bar_max_w + scaled(10),
                                      by + bar_h//2 - pct_lbl.get_height()//2))
            draw_centered_text_px(screen, f"{total} Stimmen abgegeben",
                                  FONT_SMALL, MUTED, btn.rect.y - scaled(16))

        btn.draw(screen)
        update_display()
        clock.tick(FPS)


def show_parent_joker(surf_behind, parent_name):
    """Simple popup — no game logic, just a reminder to ask one parent."""
    if JOKER_PHONE_SFX:
        JOKER_PHONE_SFX.play()

    btn = Button((WIDTH // 2 - 160, HEIGHT // 2 + 110, 320, 58),
                 "Fertig", primary=False)

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn.handle(event):
                return

        screen.blit(surf_behind, (0, 0))
        px, py, pw, ph = draw_modal_base(screen)

        draw_centered_text_px(screen, f"{parent_name}-Joker", FONT_Q, APEROL_DARK, py + scaled(52))
        draw_divider_px(screen, py + scaled(78), width=scaled(200))
        draw_centered_text_px(screen, f"Frag {parent_name}!", FONT_TITLE, INK, py + scaled(170))
        draw_centered_text_px(screen, "(und dann schnell antworten)",
                              FONT_SMALL, MUTED, py + scaled(228))

        btn.draw(screen)
        update_display()
        clock.tick(FPS)


def apply_50_50(options, correct):
    """Eliminate 2 random wrong answers in-place."""
    if JOKER_50_50_SFX:
        JOKER_50_50_SFX.play()
    wrong = [i for i in range(len(options)) if i != correct]
    for i in random.sample(wrong, 2):
        options[i].state = "eliminated"


def info_screen():
    """Rules screen shown once after Start."""
    btn = Button((WIDTH // 2 - 200, HEIGHT - 118, 400, 62), "Los geht's!", primary=True)

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if btn.handle(event):
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_centered_text(screen, "So geht's", FONT_TITLE, RED_DARK, 110)
        draw_divider(screen, 148, width=220)

        # Game structure
        draw_centered_text(screen,
            f"{len(CATEGORIES)} Kategorien · {sum(len(c['questions']) for c in CATEGORIES)} Fragen · von leicht bis schwer",
            FONT_SUB, OLIVE_DARK, 188)
        draw_centered_text(screen,
            "Du wählst die Reihenfolge der Kategorien selbst.",
            FONT_SUB, INK, 224)

        # Joker explanation — centred columns (icon on top, text below)
        circle_y = scaled(308)
        label_y  = scaled(352)
        desc_y   = scaled(378)
        block_cxs = [WIDTH // 2 - scaled(315), WIDTH // 2 - scaled(105),
                     WIDTH // 2 + scaled(105), WIDTH // 2 + scaled(315)]
        labels  = ["PUB",      "MAMA",       "PAPA",       "50:50"]
        colors  = [OLIVE,      APEROL,       LEMON_PEEL,   RED]
        titles  = ["Publikum", "Mama",       "Papa",       "50 : 50"]
        descs   = [
            "Gäste tippen 1–4.\nBalken erscheinen\nnach 5 Stimmen.",
            "Frag Mama\nallein.",
            "Frag Papa\nallein.",
            "Zwei falsche\nAntworten\nverschwinden.",
        ]

        for bcx, lbl, col, title, desc in zip(block_cxs, labels, colors, titles, descs):
            # Icon circle (centred on bcx)
            pygame.draw.circle(screen, col,      (bcx, circle_y), scaled(28))
            pygame.draw.circle(screen, PARCHMENT,(bcx, circle_y), scaled(28), max(1, scaled(1)))
            lbl_s = FONT_SMALL.render(lbl, True, CREAM_WHITE)
            screen.blit(lbl_s, lbl_s.get_rect(center=(bcx, circle_y)))
            # Title centred
            t_s = FONT_OPT_BD.render(title, True, col)
            screen.blit(t_s, t_s.get_rect(center=(bcx, label_y)))
            # Description lines centred
            for di, dline in enumerate(desc.split("\n")):
                d_s = FONT_SMALL.render(dline, True, INK)
                screen.blit(d_s, d_s.get_rect(center=(bcx, desc_y + di * scaled(20))))

        # Click mechanic reminder
        draw_divider(screen, 430, width=300)
        draw_centered_text(screen,
            "Jeder Joker kann nur einmal pro Spiel verwendet werden.",
            FONT_SMALL, MUTED, 486)
        draw_centered_text(screen,
            "Fun Stuff kommt zuletzt und wird erst nach den anderen Kategorien freigeschaltet.",
            FONT_SMALL, MUTED, 512)
        draw_centered_text(screen,
            "In Fun Stuff sind alle Joker deaktiviert.",
            FONT_SMALL, MUTED, 536)

        btn.draw(screen)
        update_display()
        clock.tick(FPS)


def category_selection_screen(done):
    """
    Shows 4 category cards. done = set of completed category indices.
    Returns the chosen category index, or None if all are done.
    """
    if len(done) == len(CATEGORIES):
        return None

    card_w, card_h = scaled(460), scaled(210)
    margin_x, gap_x = scaled(70), scaled(40)
    margin_y, gap_y = scaled(155), scaled(30)
    positions = [
        (margin_x,              margin_y),
        (margin_x + card_w + gap_x, margin_y),
        (margin_x,              margin_y + card_h + gap_y),
        (margin_x + card_w + gap_x, margin_y + card_h + gap_y),
    ]
    hover_idx = -1

    while True:
        mx, my = mouse_pos()
        hover_idx = -1
        for i, (cx, cy) in enumerate(positions):
            locked = is_fun_stuff_category(i) and not fun_stuff_unlocked(done)
            if (i not in done and not locked and
                    pygame.Rect(cx, cy, card_w, card_h).collidepoint(mx, my)):
                hover_idx = i

        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (cx, cy) in enumerate(positions):
                    locked = is_fun_stuff_category(i) and not fun_stuff_unlocked(done)
                    if (i not in done and not locked and
                            pygame.Rect(cx, cy, card_w, card_h).collidepoint(mx, my)):
                        return i

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        remaining = len(CATEGORIES) - len(done)
        draw_centered_text(screen, "Wähle eine Kategorie",
                           FONT_Q, RED_DARK, 98)
        draw_centered_text(screen,
                           f"Noch {remaining} von {len(CATEGORIES)} offen",
                           FONT_SMALL, MUTED, 128)

        for i, (cx, cy) in enumerate(positions):
            cat   = CATEGORIES[i]
            color = cat["color"]
            done_ = i in done
            locked = is_fun_stuff_category(i) and not fun_stuff_unlocked(done)
            hover = (i == hover_idx)
            r     = pygame.Rect(cx, cy, card_w, card_h)

            if done_:
                bg, border, bw = PARCHMENT_DARK, OLIVE_LIGHT, 2
            elif locked:
                bg, border, bw = PARCHMENT_DARK, MUTED, 2
            elif hover:
                bg, border, bw = CREAM_WHITE, color, 3
            else:
                bg, border, bw = CREAM_WHITE, color, 2

            pygame.draw.rect(screen, bg, r, border_radius=16)
            pygame.draw.rect(screen, border, r, bw, border_radius=16)

            # Coloured top bar
            top_bar = pygame.Rect(cx, cy, card_w, 8)
            top_col = OLIVE_LIGHT if done_ else MUTED if locked else color
            pygame.draw.rect(screen, top_col, top_bar,
                             border_top_left_radius=16, border_top_right_radius=16)

            if done_:
                check = FONT_TITLE.render("✓", True, OLIVE)
                screen.blit(check, check.get_rect(center=(r.centerx, r.centery - scaled(18))))
                lbl = FONT_SMALL.render(cat["name"], True, MUTED)
                screen.blit(lbl, lbl.get_rect(center=(r.centerx, r.centery + scaled(36))))
            elif locked:
                name_s = pygame.font.SysFont(SERIF, scaled_font(36), bold=True, italic=True)\
                             .render(cat["name"], True, MUTED)
                screen.blit(name_s, name_s.get_rect(center=(r.centerx, r.centery - scaled(22))))
                sub_s = FONT_SMALL.render("Erst nach den anderen Kategorien", True, MUTED)
                screen.blit(sub_s, sub_s.get_rect(center=(r.centerx, r.centery + scaled(22))))
                lock_s = FONT_OPT_BD.render("Gesperrt", True, MUTED)
                screen.blit(lock_s, lock_s.get_rect(center=(r.centerx, r.centery + scaled(62))))
            else:
                name_s = pygame.font.SysFont(SERIF, scaled_font(36), bold=True, italic=True)\
                             .render(cat["name"], True, color if not hover else INK)
                screen.blit(name_s, name_s.get_rect(center=(r.centerx, r.centery - scaled(22))))
                sub_s = FONT_SMALL.render(f"{len(cat['questions'])} Fragen · leicht  →  schwer", True, MUTED)
                screen.blit(sub_s, sub_s.get_rect(center=(r.centerx, r.centery + scaled(22))))
                # difficulty dots
                for d in range(5):
                    dot_x = r.centerx - scaled(40) + d * scaled(20)
                    dot_y = r.centery + scaled(60)
                    dot_c = color if not hover else INK
                    pygame.draw.circle(screen, dot_c, (dot_x, dot_y), scaled(5))
                    pygame.draw.circle(screen, PARCHMENT_DARK, (dot_x, dot_y), scaled(5), max(1, scaled(1)))

        update_display()
        clock.tick(FPS)


def category_intro_screen(cat):
    """Full-screen splash with the category name. Click anywhere to begin."""
    color = cat["color"]
    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_centered_text(screen, "Kategorie", FONT_SUB, MUTED, 270)
        draw_centered_text(screen, cat["name"], FONT_TITLE, color, 340)
        draw_divider(screen, 390, width=200)
        draw_centered_text(screen, f"{len(cat['questions'])} Fragen · leicht bis schwer",
                           FONT_SUB, OLIVE_DARK, 428)
        draw_centered_text(screen, "Klick irgendwo zum Starten",
                           FONT_SMALL, MUTED, 490)

        update_display()
        clock.tick(FPS)


def question_screen(idx, question, total, joker_used, category_name="", category_color=None):
    options = []
    letters = ["A", "B", "C", "D"]
    opt_w, opt_h, gap = 880, 68, 16
    start_y = 320
    for i, text in enumerate(question["options"]):
        rect = ((WIDTH - opt_w) // 2, start_y + i * (opt_h + gap), opt_w, opt_h)
        options.append(OptionButton(rect, letters[i], text))

    selected = None
    revealed = False
    correct  = question["answer"]
    award_point_on_wrong = question.get("award_point_on_wrong", False)

    while True:
        # Draw base frame first so overlays can snapshot it
        draw_studio_background(screen)
        draw_corner_decorations(screen)
        hdr_color = category_color if category_color else OLIVE_DARK
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}",
                           FONT_SMALL, hdr_color, 78)
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)
        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for i, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, INK, 180 + i * 44)
        if question.get("description"):
            desc_lines = wrap_text(question["description"], FONT_SMALL, WIDTH - 240)
            desc_y = 180 + len(lines) * 44 + 8
            for i, line in enumerate(desc_lines):
                draw_centered_text(screen, line, FONT_SMALL, MUTED, desc_y + i * 22)
        for opt in options:
            opt.draw(screen)
        if revealed:
            hint_y = options[-1].rect.bottom + 28
            if award_point_on_wrong and selected != correct:
                draw_centered_text(screen, question.get("wrong_point_message",
                                                        "Falsch - aber es gibt dafür einen Punkt."),
                                   FONT_SMALL, RED_DARK, hint_y)
                hint_y += 24
            draw_centered_text(screen, "Click the correct answer to continue",
                               FONT_SMALL, OLIVE_DARK, hint_y)
        update_display()

        behind = screen.copy()   # snapshot for overlay compositing

        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            # Joker icon clicks — only before reveal, only if not yet used
            if not revealed:
                ji = joker_clicked(event)
                if ji == 0 and not joker_used[0]:      # Publikum
                    joker_used[0] = True
                    show_publikum_joker(behind)
                elif ji == 1 and not joker_used[1]:    # Mama
                    joker_used[1] = True
                    show_parent_joker(behind, "Mama")
                elif ji == 2 and not joker_used[2]:    # Papa
                    joker_used[2] = True
                    show_parent_joker(behind, "Papa")
                elif ji == 3 and not joker_used[3]:    # 50:50
                    joker_used[3] = True
                    apply_50_50(options, correct)
                    # deselect if the locked answer was eliminated
                    if selected is not None and options[selected].state == "eliminated":
                        selected = None

            # Answer option clicks
            for i, opt in enumerate(options):
                if opt.handle(event):
                    if not revealed:
                        if selected != i:
                            # First click → lock in
                            selected = i
                            for j, o in enumerate(options):
                                if o.state != "eliminated":
                                    o.state = "selected" if j == i else "idle"
                            stop_parent_joker_music()
                            if LOCKIN_SFX:
                                LOCKIN_SFX.play()
                        else:
                            # Second click → reveal
                            if LOCKIN_SFX:
                                LOCKIN_SFX.stop()
                            revealed = True
                            for j, o in enumerate(options):
                                if o.state == "eliminated":
                                    continue
                                if j == correct:
                                    o.state = "correct"
                                elif j == i:
                                    o.state = "wrong"
                                else:
                                    o.state = "dimmed"
                            sfx = CORRECT_SFX if i == correct else WRONG_SFX
                            if sfx:
                                sfx.play()
                    elif i == correct:
                        # Third click on correct answer → advance
                        return selected == correct or (award_point_on_wrong and selected != correct)

        clock.tick(FPS)


# ---------- Audio + free-text question ----------

def _normalize_text_answer(text):
    return "".join(ch for ch in text.lower().strip() if ch.isalnum())


def audio_text_question_screen(idx, question, total, joker_used,
                               category_name="", category_color=None):
    audio_path = os.path.join(ASSETS_DIR, question["audio"])
    audio = None
    if os.path.exists(audio_path):
        try:
            audio = pygame.mixer.Sound(audio_path)
        except pygame.error as e:
            print(f"Could not load sound '{question['audio']}': {e}")
    else:
        print(f"[hint] missing sound file: {audio_path}")

    answer_text = ""
    submitted = False
    is_correct = False
    audio_channel = None
    playing = False

    btn_audio = Button((WIDTH // 2 - 110, 282, 220, 56), "Play", primary=False)
    input_w, input_h = scaled(640), scaled(66)
    input_rect = pygame.Rect(WIDTH // 2 - input_w // 2, scaled(380), input_w, input_h)
    btn_fertig = Button((WIDTH // 2 - 130, 492, 260, 56), "Fertig!", primary=True)
    btn_weiter = Button((WIDTH // 2 - 130, 570, 260, 56), "Weiter", primary=False)

    def stop_audio():
        nonlocal audio_channel, playing
        if audio_channel is not None:
            audio_channel.stop()
        audio_channel = None
        playing = False

    def toggle_audio():
        nonlocal audio_channel, playing
        if audio is None:
            return
        if playing:
            stop_audio()
        else:
            audio_channel = audio.play()
            playing = audio_channel is not None

    while True:
        if playing and (audio_channel is None or not audio_channel.get_busy()):
            playing = False
            audio_channel = None

        for event in get_events():
            if event.type == pygame.QUIT:
                stop_audio()
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                stop_audio()
                pygame.quit(); sys.exit()

            if btn_audio.handle(event):
                toggle_audio()

            if not submitted:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if answer_text:
                            answer_text = answer_text[:-1]
                            stop_audio()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        submitted = True
                        stop_audio()
                        is_correct = (_normalize_text_answer(answer_text) ==
                                      _normalize_text_answer(question["answer"]))
                    elif event.unicode and event.unicode.isprintable() and len(answer_text) < 40:
                        answer_text += event.unicode
                        stop_audio()

                if btn_fertig.handle(event):
                    submitted = True
                    stop_audio()
                    is_correct = (_normalize_text_answer(answer_text) ==
                                  _normalize_text_answer(question["answer"]))
            else:
                if btn_weiter.handle(event):
                    stop_audio()
                    return is_correct

        btn_audio.label = "Stop" if playing else "Play"

        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or OLIVE_DARK
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}",
                           FONT_SMALL, hdr_color, 78)
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)

        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for i, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, INK, 180 + i * 44)

        btn_audio.draw(screen)

        pygame.draw.rect(screen, CREAM_WHITE, input_rect, border_radius=12)
        pygame.draw.rect(screen, OLIVE if not submitted else MUTED,
                         input_rect, 2, border_radius=12)
        shown_text = answer_text if answer_text else "Antwort eintippen..."
        text_col = INK if answer_text else MUTED
        text_surf = FONT_OPT.render(shown_text[-34:], True, text_col)
        screen.blit(text_surf, text_surf.get_rect(midleft=(input_rect.x + 22, input_rect.centery)))

        if not submitted and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = input_rect.x + 24 + FONT_OPT.size(answer_text[-34:])[0]
            pygame.draw.line(screen, INK, (cursor_x, input_rect.y + 18),
                             (cursor_x, input_rect.bottom - 18), 2)

        if submitted:
            result_col = OLIVE if is_correct else RED
            result_txt = "Richtig!" if is_correct else f"Falsch - richtig ist: {question['answer']}"
            draw_centered_text(screen, result_txt, FONT_OPT_BD, result_col, 480)
            btn_weiter.draw(screen)
        else:
            btn_fertig.draw(screen)

        update_display()
        clock.tick(FPS)


# ---------- Photo-ordering question ----------

_OTILE_W    = scaled(90)
_OTILE_IMGH = scaled(68)
_OTILE_H    = _OTILE_IMGH
_OTILE_GAP  = scaled(8)
_OTILE_ROW_GAP = scaled(30)
_OTILE_COLS = 7
_OTILE_STEP_X = _OTILE_W + _OTILE_GAP
_OTILE_STEP_Y = _OTILE_H + _OTILE_ROW_GAP


def _order_slot_pos(slot, start_x, start_y, cols):
    row, col = divmod(slot, cols)
    return start_x + col * _OTILE_STEP_X, start_y + row * _OTILE_STEP_Y


def _nearest_order_slot(mx, my, count, start_x, start_y, cols):
    nearest = 0
    nearest_dist = float("inf")
    for slot in range(count):
        x, y = _order_slot_pos(slot, start_x, start_y, cols)
        cx = x + _OTILE_W // 2
        cy = y + _OTILE_H // 2
        dist = (mx - cx) ** 2 + (my - cy) ** 2
        if dist < nearest_dist:
            nearest = slot
            nearest_dist = dist
    return nearest


def _load_order_photos(question):
    count  = question.get("count", 10)
    prefix = question.get("photo_prefix", "foto_")
    photos = []
    for i in range(1, count + 1):
        loaded = False
        for ext in ("jpg", "jpeg", "png"):
            path = os.path.join(ASSETS_DIR, f"{prefix}{i}.{ext}")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    photos.append(pygame.transform.smoothscale(img, (_OTILE_W, _OTILE_IMGH)))
                    loaded = True
                    break
                except pygame.error:
                    pass
        if not loaded:
            surf = pygame.Surface((_OTILE_W, _OTILE_IMGH))
            surf.fill(PARCHMENT_DARK)
            pygame.draw.rect(surf, MUTED, (0, 0, _OTILE_W, _OTILE_IMGH), 1)
            lbl = FONT_SMALL.render(f"Foto {i}", True, INK)
            surf.blit(lbl, lbl.get_rect(center=(_OTILE_W // 2, _OTILE_IMGH // 2)))
            photos.append(surf)
    return photos


def _draw_order_tile(surf, x, y, photo, number, state="idle"):
    if state == "correct":
        border, bw = OLIVE_DARK,  3
    elif state == "wrong":
        border, bw = RED_DARK,    3
    elif state == "dragging":
        border, bw = APEROL_DARK, 3
    else:
        border, bw = OLIVE,       2

    surf.blit(photo, (x, y))
    pygame.draw.rect(surf, border, (x, y, _OTILE_W, _OTILE_IMGH), bw)


def ordering_question_screen(idx, question, total, joker_used,
                              category_name="", category_color=None):
    photos  = _load_order_photos(question)
    count   = len(photos)
    answer  = [x - 1 for x in question["answer"]]  # 0-based correct order
    pass_at = question.get("pass_at", round(count * 0.6))

    cols = min(_OTILE_COLS, count)
    rows = math.ceil(count / cols)
    total_w = cols * _OTILE_W + (cols - 1) * _OTILE_GAP
    total_h = rows * _OTILE_H + (rows - 1) * _OTILE_ROW_GAP
    start_x = (WIDTH - total_w) // 2
    tile_y  = scaled(285)

    order     = list(range(count))
    random.shuffle(order)
    dragging  = None   # slot index being dragged
    grab_dx   = 0      # mouse_x minus tile left-x at drag start
    grab_dy   = 0      # mouse_y minus tile top-y at drag start
    drag_mx   = 0
    drag_my   = 0
    confirmed = False

    button_w, button_h = scaled(260), scaled(56)
    button_y = tile_y + total_h + scaled(74)
    btn_fertig = Button((WIDTH // 2 - button_w // 2, button_y, button_w, button_h),
                        "Fertig!", primary=True, raw=True)
    btn_weiter = Button((WIDTH // 2 - button_w // 2, button_y, button_w, button_h),
                        "Weiter",  primary=False, raw=True)

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            if not confirmed:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for s in range(count):
                        tx, ty = _order_slot_pos(s, start_x, tile_y, cols)
                        if pygame.Rect(tx, ty, _OTILE_W, _OTILE_H).collidepoint(mx, my):
                            dragging = s
                            grab_dx  = mx - tx
                            grab_dy  = my - ty
                            drag_mx  = mx
                            drag_my  = my
                            break
                    if btn_fertig.handle(event):
                        confirmed = True

                if event.type == pygame.MOUSEMOTION and dragging is not None:
                    drag_mx  = event.pos[0]
                    drag_my  = event.pos[1]
                    tile_cx  = drag_mx - grab_dx + _OTILE_W // 2
                    tile_cy  = drag_my - grab_dy + _OTILE_H // 2
                    new_slot = _nearest_order_slot(tile_cx, tile_cy, count, start_x, tile_y, cols)
                    if new_slot != dragging:
                        item = order.pop(dragging)
                        order.insert(new_slot, item)
                        dragging = new_slot

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if dragging is not None:
                        dragging = None
                    else:
                        btn_fertig.handle(event)

            else:
                if btn_weiter.handle(event):
                    correct_count = sum(1 for s in range(count) if order[s] == answer[s])
                    return correct_count >= pass_at

        # ---- Draw ----
        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or OLIVE_DARK
        cat_lbl   = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}",
                           FONT_SMALL, hdr_color, 78)
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)

        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for li, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, INK, 165 + li * 44)

        # Position numbers above each slot
        for s in range(count):
            tx, ty = _order_slot_pos(s, start_x, tile_y, cols)
            sx = tx + _OTILE_W // 2
            n  = FONT_SMALL.render(str(s + 1), True, MUTED)
            screen.blit(n, n.get_rect(center=(sx, ty - scaled(16))))

        # Draw non-dragged tiles first
        for s, photo_idx in enumerate(order):
            if s == dragging:
                continue
            state = "idle"
            if confirmed:
                state = "correct" if order[s] == answer[s] else "wrong"
            tx, ty = _order_slot_pos(s, start_x, tile_y, cols)
            _draw_order_tile(screen, tx, ty,
                             photos[photo_idx], photo_idx + 1, state)

        # Dragged tile on top (floats with mouse)
        if dragging is not None:
            _draw_order_tile(screen, drag_mx - grab_dx, drag_my - grab_dy,
                             photos[order[dragging]], order[dragging] + 1, "dragging")

        if not confirmed:
            draw_centered_text_px(screen,
                                  "Ziehe die Fotos in die richtige Reihenfolge",
                                  FONT_SMALL, MUTED, tile_y + total_h + scaled(34))
            btn_fertig.draw(screen)
        else:
            correct_count = sum(1 for s in range(count) if order[s] == answer[s])
            result_col = OLIVE if correct_count >= pass_at else RED
            draw_centered_text_px(screen,
                                  f"{correct_count} / {count} richtig positioniert",
                                  FONT_Q, result_col, tile_y + total_h + scaled(34))
            btn_weiter.draw(screen)

        update_display()
        clock.tick(FPS)


# ---------- Video question ----------

_VID_W  = scaled(640)
_VID_H  = scaled(360)   # 16:9
_VID_X  = (WIDTH  - _VID_W) // 2   # 230
_VID_Y  = scaled(65)


import atexit
import shutil
import subprocess
import tempfile

_VIDEO_AUDIO_CACHE: dict = {}   # video_path → resolved audio path
_TEMP_AUDIO_FILES:  list = []   # temp files to delete on exit

@atexit.register
def _cleanup_temp_audio():
    for f in _TEMP_AUDIO_FILES:
        try:
            os.unlink(f)
        except OSError:
            pass


def _find_ffmpeg():
    """Locate an ffmpeg binary by any reasonable means. Returns path or None."""
    # System PATH
    p = shutil.which("ffmpeg")
    if p:
        return p
    # Common Homebrew locations on macOS
    for cand in ("/opt/homebrew/bin/ffmpeg",
                 "/usr/local/bin/ffmpeg",
                 "/opt/local/bin/ffmpeg"):
        if os.path.exists(cand):
            return cand
    # imageio-ffmpeg bundles its own binary — `pip install imageio-ffmpeg`
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _resolve_video_audio(video_path, explicit_audio_name=""):
    """
    Returns a playable audio path for *video_path*, or None on total failure.

    Priority:
      1. Explicit audio file in assets/ (e.g. 'leck_mich.mp3')
      2. Auto-extract with ffmpeg → temp MP3 (cached per video path)
    """
    if video_path in _VIDEO_AUDIO_CACHE:
        return _VIDEO_AUDIO_CACHE[video_path]

    # 1 — explicit file
    if explicit_audio_name:
        p = os.path.join(ASSETS_DIR, explicit_audio_name)
        if os.path.exists(p):
            _VIDEO_AUDIO_CACHE[video_path] = p
            return p

    # 2 — extract with ffmpeg
    ffmpeg_cmd = _find_ffmpeg()
    if ffmpeg_cmd:
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.close()
            r = subprocess.run(
                [ffmpeg_cmd, "-y", "-i", video_path,
                 "-vn", "-q:a", "2", tmp.name],
                capture_output=True, timeout=60,
            )
            if r.returncode == 0:
                _TEMP_AUDIO_FILES.append(tmp.name)
                _VIDEO_AUDIO_CACHE[video_path] = tmp.name
                return tmp.name
            os.unlink(tmp.name)
            print(f"[warn] ffmpeg failed:\n{r.stderr.decode(errors='ignore')[:400]}")
        except Exception as e:
            print(f"[hint] ffmpeg audio extraction failed: {e}")
    else:
        print("[error] No ffmpeg found — video audio will be silent.")
        print("        Fix with EITHER:")
        print("            brew install ffmpeg")
        print("        OR:")
        print("            pip install imageio-ffmpeg")

    _VIDEO_AUDIO_CACHE[video_path] = None
    return None


def _make_frame_surface(frame_bgr):
    """Convert an OpenCV BGR frame to a scaled pygame Surface."""
    rgb    = _cv2.cvtColor(frame_bgr, _cv2.COLOR_BGR2RGB)
    scaled = _cv2.resize(rgb, (_VID_W, _VID_H))
    return pygame.surfarray.make_surface(scaled.swapaxes(0, 1))


def video_question_screen(idx, question, total, joker_used,
                           category_name="", category_color=None):
    # ---- Graceful degradation if OpenCV is missing ----
    if not _CV2_OK:
        print("[warn] opencv-python not installed — falling back to multiple-choice")
        mc_q = {k: v for k, v in question.items()}
        mc_q.pop("video", None); mc_q.pop("audio", None)
        mc_q.pop("pause_at", None); mc_q.pop("stop_at", None); mc_q.pop("type", None)
        return question_screen(idx, mc_q, total, joker_used,
                                category_name, category_color)

    video_path = os.path.join(ASSETS_DIR, question["video"])
    pause_at = float(question["pause_at"])
    stop_at = question.get("stop_at")
    stop_at = float(stop_at) if stop_at is not None else None
    correct  = question["answer"]

    # ---- Open video ----
    if not os.path.exists(video_path):
        print(f"[warn] video not found: {video_path}")
        mc_q = {k: v for k, v in question.items()
                if k not in ("video","audio","pause_at","stop_at","type")}
        return question_screen(idx, mc_q, total, joker_used,
                                category_name, category_color)

    cap      = _cv2.VideoCapture(video_path)
    vid_fps  = cap.get(_cv2.CAP_PROP_FPS) or 30.0
    frame_ms = 1000.0 / vid_fps

    # ---- Audio — load now (but don't play yet — user clicks ▶ to start) ----
    has_audio  = False
    audio_file = _resolve_video_audio(video_path, question.get("audio", ""))
    if audio_file:
        try:
            pygame.mixer.music.load(audio_file)
            has_audio = True
        except Exception as e:
            print(f"[warn] audio load failed: {e}")

    # ---- Option buttons ----
    letters   = ["A", "B", "C", "D"]
    opt_w, opt_h, opt_gap = 640, 52, 10
    opt_y0 = 65 + 360 + 46        # below video + question line
    options = []
    for i, text in enumerate(question["options"]):
        rect = ((BASE_WIDTH - opt_w) // 2, opt_y0 + i * (opt_h + opt_gap), opt_w, opt_h)
        options.append(OptionButton(rect, letters[i], text))

    # small restart button — lives inside video frame bottom-right
    btn_restart = Button(
        ((BASE_WIDTH - 640) // 2 + 640 - 126, 65 + 360 - 40, 120, 34),
        "↺ Neustart", primary=False)
    # advance button — shown after video ends
    btn_weiter  = Button(
        (BASE_WIDTH // 2 - 120, opt_y0 + 4 * (opt_h + opt_gap) + 10, 240, 52),
        "Weiter", primary=False)

    # ---- State ----
    # Show the first frame as a "poster" with a ▶ overlay — click to start.
    poster_frame   = None
    ret0, frm0 = cap.read()
    if ret0:
        poster_frame = _make_frame_surface(frm0)
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)   # rewind so playback starts at 0

    frame_surf     = poster_frame
    not_started    = True            # waiting for the user to click ▶
    play_start     = 0
    elapsed_ms     = 0
    last_read_ms   = 0
    playing        = False
    paused         = False
    vid_ended      = False
    selected       = None
    answered       = False     # True after the 2nd click — video keeps playing
    revealed       = False     # True after the video ends — colors + sound

    video_rect = pygame.Rect(_VID_X, _VID_Y, _VID_W, _VID_H)

    def start_playback():
        nonlocal play_start, elapsed_ms, last_read_ms, playing, not_started
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)
        if has_audio:
            pygame.mixer.music.play()
        play_start   = pygame.time.get_ticks()
        elapsed_ms   = 0
        # Anchor the frame clock to wall time so the first read fires at play_start,
        # not at "tick 0 since pygame init".
        last_read_ms = play_start - frame_ms
        playing      = True
        not_started  = False

    def do_restart():
        nonlocal frame_surf, play_start, elapsed_ms, last_read_ms
        nonlocal playing, paused, vid_ended, selected, answered, revealed, not_started
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)
        if has_audio:
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
        play_start   = pygame.time.get_ticks()
        elapsed_ms   = 0
        last_read_ms = play_start - frame_ms
        playing  = True
        paused   = False
        vid_ended = False
        not_started = False
        selected = None
        answered = False
        revealed = False
        for o in options:
            o.state = "idle"; o.hover = False

    def reveal_answer():
        nonlocal revealed
        if revealed:
            return
        revealed = True
        for j, o in enumerate(options):
            if o.state == "eliminated":
                continue
            if j == correct:
                o.state = "correct"
            elif j == selected:
                o.state = "wrong"
            else:
                o.state = "dimmed"
        sfx = CORRECT_SFX if selected == correct else WRONG_SFX
        if sfx:
            sfx.play()

    # ---- Main loop ----
    while True:
        now = pygame.time.get_ticks()

        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if has_audio: pygame.mixer.music.stop()
                cap.release(); pygame.quit(); sys.exit()

            # Click on video poster → start playback
            if not_started and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if video_rect.collidepoint(event.pos):
                    start_playback()
                    continue

            # Restart (available when paused or ended)
            if (paused or vid_ended) and btn_restart.handle(event):
                do_restart()
                continue

            # Answers (only during pause, before reveal)
            if paused and not revealed:
                for i, opt in enumerate(options):
                    if opt.handle(event):
                        if selected != i:
                            # 1st click — lock in
                            selected = i
                            for j, o in enumerate(options):
                                if o.state != "eliminated":
                                    o.state = "selected" if j == i else "idle"
                            if LOCKIN_SFX: LOCKIN_SFX.play()
                        else:
                            # 2nd click — resume video; the reveal waits for the video to end
                            if LOCKIN_SFX: LOCKIN_SFX.stop()
                            answered = True
                            # lock the choice visually: dim every non-selected option
                            for j, o in enumerate(options):
                                if o.state == "eliminated": continue
                                if j != selected: o.state = "dimmed"
                                # the selected one keeps its lock-in colour.
                            # Resume both video AND audio from pause_at − 3 s
                            resume_s = max(0.0, pause_at - 3.0)
                            cap.set(_cv2.CAP_PROP_POS_MSEC, resume_s * 1000)
                            if has_audio:
                                # play(start=…) seeks AND resumes in one call.
                                # plain play() after set_pos() rewinds to 0 — that was the bug.
                                pygame.mixer.music.play(start=resume_s)
                            elapsed_ms   = int(resume_s * 1000)
                            play_start   = now - elapsed_ms
                            last_read_ms = now - frame_ms
                            paused  = False
                            playing = True

            # Advance after the reveal: click the correct (green) answer
            if revealed:
                for i, opt in enumerate(options):
                    if opt.handle(event) and i == correct:
                        if has_audio: pygame.mixer.music.stop()
                        cap.release()
                        return selected == correct

        # ---- Video update ----
        if playing and not paused:
            elapsed_ms = now - play_start
            elapsed_s = elapsed_ms / 1000.0

            # Pause at the designated timestamp
            if elapsed_s >= pause_at and not answered:
                paused  = True
                playing = False
                if has_audio: pygame.mixer.music.pause()
                # Freeze on the exact pause frame
                cap.set(_cv2.CAP_PROP_POS_MSEC, pause_at * 1000)
                ret, frm = cap.read()
                if ret:
                    frame_surf = _make_frame_surface(frm)
            elif stop_at is not None and answered and elapsed_s >= stop_at:
                playing = False
                vid_ended = True
                if has_audio:
                    pygame.mixer.music.stop()
                cap.set(_cv2.CAP_PROP_POS_MSEC, stop_at * 1000)
                ret, frm = cap.read()
                if ret:
                    frame_surf = _make_frame_surface(frm)
                reveal_answer()
            elif now - last_read_ms >= frame_ms:
                # Catch up: read every frame whose scheduled time has passed,
                # but only render the latest (huge CPU win when we're behind).
                latest_frm = None
                while now - last_read_ms >= frame_ms:
                    ret, frm = cap.read()
                    if not ret:
                        vid_ended = True
                        playing   = False
                        # When the video finishes, NOW reveal the answer
                        if answered and not revealed:
                            reveal_answer()
                        break
                    latest_frm    = frm
                    last_read_ms += frame_ms     # accumulate, NOT reset to now
                if latest_frm is not None:
                    frame_surf = _make_frame_surface(latest_frm)

        # ---- Draw ----
        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or OLIVE_DARK
        cat_lbl   = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}",
                           FONT_SMALL, hdr_color, 40)
        draw_joker_icons(screen, joker_used)

        # Video frame
        if frame_surf:
            screen.blit(frame_surf, (_VID_X, _VID_Y))
        else:
            pygame.draw.rect(screen, INK, (_VID_X, _VID_Y, _VID_W, _VID_H))
            draw_centered_text_px(screen, "Wird geladen …",
                                  FONT_SMALL, MUTED, _VID_Y + _VID_H // 2)
        # border
        pygame.draw.rect(screen, OLIVE, (_VID_X, _VID_Y, _VID_W, _VID_H), 2)

        # ▶ Play overlay before user starts the video
        if not_started:
            veil = pygame.Surface((_VID_W, _VID_H), pygame.SRCALPHA)
            veil.fill((0, 0, 0, 100))
            screen.blit(veil, (_VID_X, _VID_Y))
            # big triangle play icon, centered
            cx, cy = _VID_X + _VID_W // 2, _VID_Y + _VID_H // 2
            r      = 44
            pygame.draw.circle(screen, (0, 0, 0, 0), (cx, cy), r + 4)
            pygame.draw.circle(screen, CREAM_WHITE, (cx, cy), r)
            pygame.draw.circle(screen, OLIVE_DARK,  (cx, cy), r, 3)
            tri = [
                (cx - 14, cy - 22),
                (cx - 14, cy + 22),
                (cx + 22, cy),
            ]
            pygame.draw.polygon(screen, OLIVE_DARK, tri)
            hint = FONT_SUB.render("Klick zum Starten", True, CREAM_WHITE)
            shade = pygame.Surface((hint.get_width() + 20, hint.get_height() + 10),
                                   pygame.SRCALPHA)
            shade.fill((0, 0, 0, 160))
            shade_pos = (cx - shade.get_width() // 2, cy + r + 14)
            screen.blit(shade, shade_pos)
            screen.blit(hint, (shade_pos[0] + 10, shade_pos[1] + 5))

        # Pause banner inside video
        if paused and not revealed:
            banner = FONT_SMALL.render("▐▐  Antworte jetzt!", True, CREAM_WHITE)
            bx = _VID_X + _VID_W // 2 - banner.get_width() // 2 - 8
            by = _VID_Y + _VID_H - 30
            shade = pygame.Surface((banner.get_width() + 16, banner.get_height() + 8),
                                   pygame.SRCALPHA)
            shade.fill((0, 0, 0, 140))
            screen.blit(shade, (bx, by - 4))
            screen.blit(banner, (bx + 8, by))

        # Restart button (when paused or ended)
        if paused or vid_ended:
            btn_restart.draw(screen)

        # Question text + options (shown once video pauses)
        if paused or answered or revealed:
            q_lines = wrap_text(question["q"], FONT_Q, _VID_W)
            for li, line in enumerate(q_lines):
                draw_centered_text_px(screen, line, FONT_Q, INK,
                                      _VID_Y + _VID_H + scaled(22) + li * scaled(38))
            for opt in options:
                opt.draw(screen)

        # After the reveal: hint that clicking the correct answer advances
        if revealed:
            draw_centered_text_px(screen,
                                  "Click the correct answer to continue",
                                  FONT_SMALL, OLIVE_DARK,
                                  options[-1].rect.bottom + scaled(16))
        elif vid_ended and not answered:
            # Edge case: video ended before the user answered
            draw_centered_text_px(screen, "Wähle eine Antwort",
                                  FONT_SMALL, MUTED,
                                  options[-1].rect.bottom + scaled(16))

        update_display()
        clock.tick(FPS)


def end_screen(score, total):
    btn = Button((WIDTH // 2 - 200, HEIGHT - 130, 400, 68), "Ende", primary=False)

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if btn.handle(event):
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_centered_text(screen, "Finale!", FONT_TAGLINE, OLIVE_DARK, 220)
        draw_centered_text(screen, "Happy Birthday, Oma", FONT_TITLE, RED_DARK, 290)

        draw_show_bar(screen, WIDTH // 2, 340, w=140, h=14)

        draw_centered_text(screen, f"Score:  {score}  /  {total}", FONT_Q, APEROL_DARK, 400)
        draw_centered_text(screen, "Da ist dein Preis!", FONT_SUB, INK, 450)

        # decorative studio-light row
        cx = WIDTH // 2
        palette = [RED, APEROL, LEMON_PEEL, OLIVE, RED, APEROL, LEMON_PEEL]
        for i, dx in enumerate([-90, -60, -30, 0, 30, 60, 90]):
            draw_heart(screen, cx + dx, 495, size=8, color=palette[i])

        btn.draw(screen)
        update_display()
        clock.tick(FPS)


# ---------- Main loop ----------
def between_questions_pause(ms=2000):
    """Blank quiz-show pause between questions."""
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < ms:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        draw_studio_background(screen)
        draw_corner_decorations(screen)
        update_display()
        clock.tick(FPS)


def main():
    total_questions = sum(len(c["questions"]) for c in CATEGORIES)
    while True:
        title_screen()
        info_screen()

        score      = 0
        joker_used = [False, False, False, False]   # once per full game
        done_cats  = set()
        first_question_pending = True

        while len(done_cats) < len(CATEGORIES):
            cat_idx = category_selection_screen(done_cats)
            if cat_idx is None:
                break
            cat = CATEGORIES[cat_idx]
            category_joker_used = [True, True, True, True] if cat["name"] == FUN_STUFF_CATEGORY else joker_used

            category_intro_screen(cat)

            for qi, q in enumerate(cat["questions"]):
                if first_question_pending:
                    stop_title_music(0)
                    first_question_pending = False
                play_intro_sound()
                kwargs = dict(joker_used=category_joker_used,
                              category_name=cat["name"],
                              category_color=cat["color"])
                qtype = q.get("type")
                if qtype == "ordering":
                    result = ordering_question_screen(qi, q, len(cat["questions"]), **kwargs)
                elif qtype == "audio_text":
                    result = audio_text_question_screen(qi, q, len(cat["questions"]), **kwargs)
                elif qtype == "video":
                    result = video_question_screen(qi, q, len(cat["questions"]), **kwargs)
                else:
                    result = question_screen(qi, q, len(cat["questions"]), **kwargs)
                if result:
                    score += 1
                between_questions_pause(1000)

            done_cats.add(cat_idx)

        end_screen(score, total_questions)


if __name__ == "__main__":
    main()
