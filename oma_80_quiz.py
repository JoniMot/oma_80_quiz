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
UNLOCK_FUN_STUFF_IMMEDIATELY = True

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
IMAGE_CANDIDATES = [
    "oma.JPG",
    "oma.jpg",
    "oma.jpeg",
    "oma.png",
]

# ---------- Sound files ----------
# Each variable is just the filename inside the assets/ folder.
# Swap them around as you like.
PATH_PREFIX = "sound/"
SND_OPENING_THEME = PATH_PREFIX + "opening_theme.mp3"  # Eröffnungsmelodie
SND_INTRO = PATH_PREFIX + "intro.mp3"  # Einleitung
SND_CANDIDATE_ENTER = PATH_PREFIX + "candidate_enter.mp3"  # Kandidat kommt
SND_ANSWER_LOCKIN = PATH_PREFIX + "answer_lockin.mp3"  # Antwort einloggen
SND_ANSWER_CORRECT = PATH_PREFIX + "answer_correct.mp3"  # Antwort richtig
SND_ANSWER_WRONG = PATH_PREFIX + "answer_wrong.mp3"  # Antwort falsch
SND_TIME_UP = PATH_PREFIX + "time_up.mp3"  # Zeit vorbei
SND_JOKER_50_50 = PATH_PREFIX + "joker_50_50.mp3"  # 50:50 Joker
SND_JOKER_AUDIENCE = PATH_PREFIX + "joker_audience.mp3"  # Publikumsjoker
SND_JOKER_PHONE = PATH_PREFIX + "joker_phone.mp3"  # Telefonjoker

# Which sound plays before each question
QUESTION_INTRO_SOUND = SND_INTRO
# Which sound plays on the title screen (None = silent)
TITLE_SOUND = SND_OPENING_THEME
# Played on the first click (selection step)
LOCKIN_SOUND = SND_ANSWER_LOCKIN
# Played on the second click (reveal step)
CORRECT_SOUND = SND_ANSWER_CORRECT
WRONG_SOUND = SND_ANSWER_WRONG
# Jokers
JOKER_AUDIENCE_SOUND = SND_JOKER_AUDIENCE
JOKER_PHONE_SOUND = SND_JOKER_PHONE
JOKER_50_50_SOUND = SND_JOKER_50_50
# Bars in the audience joker reveal only after this many total votes
AUDIENCE_REVEAL_AT = 5

# ---------- Millionenshow palette ----------
STAGE_BLUE = (9, 22, 56)  # deep studio blue
PANEL_BLUE = (17, 39, 85)  # dark panel blue
TEXT_DARK = (5, 22, 61)
TEXT_LIGHT = (246, 252, 255)
SUCCESS_GREEN = (0, 132, 92)  # muted quiz-show green
SUCCESS_GREEN_DARK = (0, 82, 67)
SUCCESS_GREEN_LIGHT = (76, 194, 143)
ANSWER_BLUE = (31, 78, 154)  # rich answer blue
DEEP_BLUE = (10, 24, 70)
ACCENT_BLUE = (53, 121, 198)  # restrained blue accent
ACCENT_BLUE_DARK = (25, 57, 129)
ACCENT_BLUE_LIGHT = (108, 164, 226)
GREEN_ACCENT = (0, 150, 116)
WHITE = (246, 252, 255)
GOLD = (218, 231, 154)
GOLD_LIGHT = (245, 250, 215)
MUTED_TEXT = (135, 160, 196)
WRONG_RED = (150, 48, 74)

# ---------- Quiz content — edit freely ----------
# 4 categories × 5 questions. Question 1 = easiest, question 5 = hardest.
# Set "answer" to the 0-based index of the correct option.
# Picture questions:
# {
#     "type": "picture",
#     "q": "Wer ist auf diesem Bild?",
#     "picture": "bildname.jpg",  # place in assets/
#     "options": ["A", "B", "C", "D"],
#     "answer": 0,
# }
# Fun photo text questions:
# {
#     "type": "fun_photo",
#     "q": "Was wurde hier verändert?",
#     "photo": "haare",  # expects assets/fun_fotos/haare.* and haare_og.*
#     "answers": ["Haare", "Frisur"],  # any of these words is accepted
# }
# Video challenge questions:
# {
#     "type": "video_challenge",
#     "video": "beer_pong.MOV",
#     "challenge": "Zeig uns, dass dieses Video nicht gefälscht ist!",
# }
# Sudoku questions:
# {
#     "type": "sudoku",
#     "q": "Welche Zahlen fehlen?",
#     "picture": "sudoku.png",
#     "answer": ["5", "6", "3"],  # question marks from left to right
# }
CATEGORIES = [
    {
        "name": "Allgemeines",
        "color": SUCCESS_GREEN,
        "questions": [
            {
                "q": "Wie viele Tage hat ein Schaltjahr?",
                "options": ["364", "365", "366", "367"],
                "answer": 2,
            },
            {
                "q": "Wann wurde in Österreich offiziell der Euro eingeführt?",
                "options": ["2000", "2001", "2002", "1999"],
                "answer": 2,
            },
            {
                "q": "In welchem Jahr fiel die Berliner Mauer?",
                "options": ["1987", "1988", "1989", "1990"],
                "answer": 2,
            },
            {
                "q": "Wie heißt die Meeresströmung im Atlantik, die warmes Wasser aus dem Golf von Mexiko nach Europa transportiert?",
                "options": ["Golfstrom", "Kuroshio", "Labradorstrom", "Canarystrom"],
                "answer": 0,
            },
            {
                "q": "Welcher Kontinent hat die meisten Einwohner?",
                "options": ["Asien", "Afrika", "Europa", "Nordamerika"],
                "answer": 0,
            },
            {
                "q": "Woher hat der Flohmarkt seinen Namen?",
                "options": [
                    "Weil dort früher Flohfänger arbeiteten",
                    "Weil auf den Märkten oft gebrauchte Kleidung mit Flöhen verkauft wurde",
                    "Weil Flöhe dort als Haustiere gehandelt wurden",
                    "Weil der Organisator des erste Flohmarktes Chuck Floh hieß",
                ],
                "answer": 1,
            },
            {
                "q": "Welcher internationale Politiker wird 2026 auch 80 Jahre alt?",
                "options": [
                    "Heinz Fischer",
                    "Angela Merkel",
                    "Donald Trump",
                    "Vladimir Putin",
                ],
                "answer": 2,
            },
            {
                "q": "Welcher Planet ist der Sonne am nächsten?",
                "options": ["Erde", "Merkur", "Mars", "Saturn"],
                "answer": 1,
            },
            {
                "q": "Welches Vitamin bildet der menschliche Körper hauptsächlich durch Sonnenlicht?",
                "options": ["Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D"],
                "answer": 3,
            },
            {
                "q": "Wie nennt man den großen rotierenden Teil an der Vorderseite einer Tunnelbohrmaschine, der das Gestein abträgt?",
                "options": [
                    "Schildmantel",
                    "Bohrkopf",
                    "Hydraulikring",
                    "Förderkammer",
                ],
                "answer": 1,
            },
            {
                "q": "Wie breit ist die sogenannte Normalspur, die bei den meisten Eisenbahnstrecken in Europa verwendet wird?",
                "options": ["1000 mm", "1435 mm", "1520mm", "1600 mm"],
                "answer": 1,
            },
            {
                "q": "Aus welchem Land stammt Sudoku in seiner heute bekannten Form?",
                "options": ["China", "Japan", "Südkorea", "Thailand"],
                "answer": 1,
            },
        ],
    },
    {
        "name": "Nerd Stuff",
        "color": ANSWER_BLUE,
        "questions": [
            {
                "q": "Welche Zutat sorgt bei Brandteig dafür, dass der Teig beim Backen stark aufgeht und innen hohl wird?",
                "options": ["Backpulver", "Wasserdampf", "Hefe", "Natron"],
                "answer": 1,
            },
            {
                "q": "Welche Temperatur sollte geschmolzene Butter ungefähr haben, wenn sie unter geschlagenes Eiweiß gehoben wird, damit dieses nicht zusammenfällt?",
                "options": ["Etwa 30 °C", "Etwa 60 °C", "Etwa 90 °C", "Direkt kochend"],
                "answer": 0,
            },
            {
                "q": "Was bewirkt das sogenannte „Blindbacken“?",
                "options": [
                    "Der Teig wird ohne Rezept hergestellt",
                    "Der Boden wird ohne Belag vorgebacken",
                    "Der Kuchen wird ohne Oberhitze gebacken",
                    "Der Teig ruht im Dunkeln",
                ],
                "answer": 1,
            },
            {
                "q": "Was beschreibt in der Bäckerei der Begriff 'Autolyse'?",
                "options": [
                    "Das Ruhen von Mehl und Wasser vor dem Kneten",
                    "Das Einfrieren des Teigs",
                    "Das Gehenlassen nach dem Formen",
                    "Das Backen mit Dampf",
                ],
                "answer": 0,
            },
            {
                "q": "Wie nennt man das gezielte Reduzieren von Maschen in einer Häkelarbeit?",
                "options": ["Abnehmen", "Verkürzen", "Stauchen", "Zusammenziehen"],
                "answer": 0,
            },
            {
                "q": 'Im Buch "Die kleine Hexe": Wie heißt das große Hexenfest im Wald, bei dem alle Hexen zusammenkommen und feiern?',
                "options": [
                    "Mondzaubernacht",
                    "Waldburgisnacht",
                    "Hexenfeuerfest",
                    "Zauberball",
                ],
                "answer": 1,
            },
            {
                "q": "Welche dieser Blumen gehört botanisch zur Familie der Korbblütler?",
                "options": ["Zinnie", "Tulpe", "Lilie", "Narzisse"],
                "answer": 0,
            },
            {
                "q": "Warum schneidet man Zinnien für die Vase idealerweise am frühen Morgen?",
                "options": [
                    "Dann enthalten die Stängel besonders viel Wasser",
                    "Dann sind die Blüten intensiver gefärbt",
                    "Dann duften sie stärker",
                    "Dann lassen sie sich leichter schneiden",
                ],
                "answer": 0,
            },
            {
                "q": "Welcher Pflanzennährstoff ist hauptsächlich für die Blütenbildung verantwortlich?",
                "options": ["Stickstoff", "Phosphor", "Schwefel", "Magnesium"],
                "answer": 1,
            },
            {
                "q": "Wie viele Felder besitzt ein klassisches Sudoku insgesamt?",
                "options": ["64", "72", "81", "99"],
                "answer": 2,
            },
        ],
    },
    {
        "name": "Persönliches",
        "color": ACCENT_BLUE,
        "questions": [
            {
                "q": "Welches Modell war euer erstes gemeinsames Auto?",
                "options": ["VW Käfer", "Ford 12M", "Opel Kadett", "Peugeot 104"],
                "answer": 1,
            },
            {
                "q": "In welcher Silvesternacht hast du Gerda nach Hause gefahren?",
                "options": ["1985", "1989", "1995", "1998"],
                "answer": 1,
            },
            {
                "q": "Welches Moped hatte Reini gegen ein Rennrad eingestauscht?",
                "options": [
                    "KTM Comet 50",
                    "Puch MV50",
                    "Zündapp GTS 50",
                    "Puch Monza",
                ],
                "answer": 3,
            },
            {
                "q": "Wo hättest du Jakobs Rasierer suchen müssen, als Jakob im Frühlings 2026 im Krankenhaus war?",
                "options": [
                    "bei Jakobs Computer",
                    "unter Jakobs Bett",
                    "im Badezimmer",
                    "auf der Terrasse",
                ],
                "answer": 0,
            },
            {
                "q": "Was sagte Thomas im Februar 1979, als Jakob von Salzburg nach Holzleiten heimkam, Klemens aber noch nicht geboren war?",
                "options": [
                    "das Baby wird super!",
                    "mei, ich freu mich schon so auf das Baby",
                    "jetzt ist das Scheißbaby noch immer nicht da!",
                    "Wo ist Mutti?",
                ],
                "answer": 2,
            },
            {
                "q": "Was hat Helga in ihrer Kindheit, gemeinsam mit ihrer Schwester Herta in Braunau in den Inn geworfen, weil sie es zu wenig gut kannte?",
                "options": ["Schnitzel", "Banane", "Handy", "eine Weintraube"],
                "answer": 1,
            },
            {
                "q": "Was bestellte Jakob beim Cafe, wo ihr euch kennengelernt habt?",  # TODO bei opa nachfragen
                "options": [
                    "Sachertorte & Apfelsaft",
                    "Cremeschnitte & Bier",
                    "Topfenkuchen & Kaffee",
                    "Apfelkuchen & Radler",
                ],
                "answer": 1,
            },
            {
                "q": "Welche Zigarettenmarke rauchte Opa Max?",
                "options": ["Malboro", "Memphis", "Smart", "Ernte"],
                "answer": 2,
            },
            {
                "q": "Welche Eismarke hatte Cafe Edtbauer?",
                "options": ["Schöller", "Eskimo", "Langnese", "Cornetto"],
                "answer": 0,
            },
            {
                "q": "Mit was wurde das frischgemähte Heu gegen Regenfälle geschützt?",
                "options": ["Stickstoff", "Heuhiefler", "Schwefel", "Magnesium"],
                "answer": 1,
            },
        ],
    },
    {
        "name": "Fun Stuff",
        "color": GREEN_ACCENT,
        "questions": [
            {
                "type": "sudoku",
                "q": "Welche Zahlen fehlen?",
                "picture": "sudoku.png",
                "answer": ["5", "6", "3"],
            },
            {
                "type": "video_challenge",
                "video": "beer_pong.MOV",
                "challenge": "Zeig uns, dass dieses Video nicht gefälscht ist! 3 Becher, 3 Versuche einen zu treffen",
            },
            {
                "type": "fun_photo",
                "q": "Was stimmt hier nicht?",
                "photo": "haare",
                "answers": [
                    "Haare",
                    "Haare von Klemens",
                    "Frisur",
                    "Klemens Haare",
                    "Klemens Glatze",
                    "Glatze",
                ],
            },
            {
                "type": "fun_photo",
                "q": "Was stimmt hier nicht?",
                "photo": "handy",
                "answers": ["Handy", "Telefon"],
            },
            {
                "type": "fun_photo",
                "q": "Was stimmt hier nicht?",
                "photo": "hund",
                "answers": ["Hund", "Katze", "Tier", "Tier in der Hand"],
            },
            {
                "type": "fun_photo",
                "q": "Was stimmt hier nicht?",
                "photo": "pyjama",
                "answers": ["Pyjama", "Pyjamas", "Schlafanzug"],
            },
            {
                "type": "fun_photo",
                "q": "Was stimmt hier nicht?",
                "photo": "schnaps",
                "answers": ["Schnaps", "Alkohol"],
            },
            {
                "type": "fun_photo",
                "q": "Was stimmt hier nicht?",
                "photo": "tragen",
                "answers": ["Tragen", "Vertauscht", "Anders herum"],
            },
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
                "video": "sturz.mp4",  # place in assets/
                "audio": "sturz.mp3",  # optional: extracted audio (ffmpeg -i sturz.mp4 sturz.mp3)
                "pause_at": 09.0,  # seconds where video freezes
                "options": [
                    "Läuft nochmal zur Kamera hin",
                    "Macht einen Köpfler",
                    "Läuft weiter",
                    "Fällt hin",
                ],
                "answer": 3,
            },
            {
                "type": "video",
                "q": "Was macht Klara als nächstes?",
                "video": "cam_schlag.mp4",  # place in assets/
                "audio": "cam_schlag.mp3",  # optional: extracted audio (ffmpeg -i leck_mich.mp4 leck_mich.mp3)
                "pause_at": 06.0,  # seconds where video freezes
                "options": [
                    "Erschrickt und Kreischt",
                    "Erschrickt und schlägt die Kamera",
                    "Erwartet die Kamera und erschrickt nicht",
                    "Nimmt die Kamera in die Hand und filmt weiter",
                ],
                "answer": 1,
            },
            {
                "type": "video",
                "q": "Welches Buch von Dan Brown las Klara zu diesem Zeitpunkt?",
                "video": "illuminati.mp4",  # place in assets/
                "audio": "illuminati.mp3",  # optional: extracted audio (ffmpeg -i illuminati.mp4 illuminati.mp3)
                "pause_at": 59.5,  # seconds where video freezes
                "stop_at": 65.0,  # optional: seconds where video stops after answer
                "options": ["Inferno", "Illuminati", "Der Da Vinci Code", "Sakrileg"],
                "answer": 1,
            },
            {
                "type": "video",
                "q": "Was sagt Klara als nächstes?",
                "video": "leck_mich.mp4",  # place in assets/
                "audio": "leck_mich.mp3",  # optional: extracted audio (ffmpeg -i leck_mich.mp4 leck_mich.mp3)
                "pause_at": 67.0,  # seconds where video freezes
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
    if UNLOCK_FUN_STUFF_IMMEDIATELY:
        return True
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
display_surface = pygame.display.set_mode(
    (DISPLAY_WIDTH, DISPLAY_HEIGHT), display_flags
)
screen = (
    display_surface
    if (WIDTH, HEIGHT) == (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    else pygame.Surface((WIDTH, HEIGHT))
)
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
            attrs["pos"] = (
                event.pos[0] - SCREEN_OFFSET_X,
                event.pos[1] - SCREEN_OFFSET_Y,
            )
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
FONT_TITLE = pygame.font.SysFont(SERIF, scaled_font(68), bold=True)
FONT_SUB = pygame.font.SysFont(SERIF, scaled_font(26), bold=True)
FONT_BTN = pygame.font.SysFont(SERIF, scaled_font(26), bold=True)
FONT_Q = pygame.font.SysFont(SERIF, scaled_font(34), bold=True)
FONT_OPT = pygame.font.SysFont(SERIF, scaled_font(24))
FONT_OPT_BD = pygame.font.SysFont(SERIF, scaled_font(26), bold=True)
FONT_SMALL = pygame.font.SysFont(SERIF, scaled_font(18), bold=True)


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
    pygame.draw.circle(surf, PANEL_BLUE, (center, center), center - scaled(2))
    pygame.draw.circle(
        surf, SUCCESS_GREEN, (center, center), center - scaled(2), max(1, scaled(2))
    )
    label = FONT_SMALL.render("add oma.jpg", True, MUTED_TEXT)
    surf.blit(label, label.get_rect(center=(center, center)))
    return surf


def load_title_photo(size):
    for filename in ("oma.jpg", "oma.JPG", "oma.jpeg", "oma.png"):
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, (size, size))
            except pygame.error:
                pass

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    pygame.draw.circle(surf, PANEL_BLUE, (center, center), center)
    pygame.draw.circle(
        surf, ACCENT_BLUE_LIGHT, (center, center), center - scaled(2), max(1, scaled(2))
    )
    label = FONT_SMALL.render("add oma.jpg", True, MUTED_TEXT)
    surf.blit(label, label.get_rect(center=(center, center)))
    return surf


def load_title_logo():
    path = os.path.join(ASSETS_DIR, "millionenshow.png")
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Could not load image 'millionenshow.png': {e}")
    else:
        print(f"[hint] missing image file: {path}")
    return None


def load_question_picture(filename, max_w, max_h):
    if not filename:
        return None

    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            iw, ih = img.get_size()
            scale = min(max_w / iw, max_h / ih)
            size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            return pygame.transform.smoothscale(img, size)
        except pygame.error as e:
            print(f"Could not load question picture '{filename}': {e}")
    else:
        print(f"[hint] missing question picture: {path}")

    surf = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
    surf.fill(PANEL_BLUE)
    pygame.draw.rect(surf, MUTED_TEXT, surf.get_rect(), max(1, scaled(2)))
    label = FONT_SMALL.render(f"add assets/{filename}", True, MUTED_TEXT)
    surf.blit(label, label.get_rect(center=surf.get_rect().center))
    return surf


def load_sound(filename):
    if not filename:
        return None
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        sound_path = os.path.join(ASSETS_DIR, "sound", filename)
        if os.path.exists(sound_path):
            path = sound_path
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Could not load sound '{filename}': {e}")
    else:
        print(f"[hint] missing sound file: {path}")
    return None


PORTRAIT = load_portrait()
TITLE_PHOTO = load_title_photo(scaled(220))
TITLE_LOGO = load_title_logo()
INTRO_SOUND = load_sound(QUESTION_INTRO_SOUND)
TITLE_MUSIC = load_sound(TITLE_SOUND)
LOCKIN_SFX = load_sound(LOCKIN_SOUND)
CORRECT_SFX = load_sound(CORRECT_SOUND)
WRONG_SFX = load_sound(WRONG_SOUND)
JOKER_AUDIENCE_SFX = load_sound(JOKER_AUDIENCE_SOUND)
JOKER_PHONE_SFX = load_sound(JOKER_PHONE_SOUND)
JOKER_50_50_SFX = load_sound(JOKER_50_50_SOUND)
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
def draw_studio_background(surf, emblem=False):
    """Simple dark blue stage background."""
    surf.fill(STAGE_BLUE)
    for y in range(0, HEIGHT, max(1, scaled(3))):
        t = y / max(1, HEIGHT - 1)
        r = int(9 + 5 * (1 - t))
        g = int(22 + 24 * (1 - t))
        b = int(56 + 46 * (1 - t))
        pygame.draw.rect(surf, (r, g, b), (0, y, WIDTH, max(1, scaled(3))))

    cx, cy = WIDTH // 2, HEIGHT // 2
    if TITLE_LOGO is not None:
        logo_size = scaled(780)
        logo = pygame.transform.smoothscale(TITLE_LOGO, (logo_size, logo_size))
        logo.set_alpha(54)
        surf.blit(logo, logo.get_rect(center=(cx, cy)))

    if emblem:
        draw_millionenshow_emblem(surf, cx, cy + scaled(8), scaled(230), alpha=42)

    pygame.draw.rect(
        surf, ACCENT_BLUE_DARK, (24, 24, WIDTH - 48, HEIGHT - 48), 2, border_radius=18
    )
    pygame.draw.rect(
        surf, ACCENT_BLUE_LIGHT, (34, 34, WIDTH - 68, HEIGHT - 68), 1, border_radius=14
    )


def draw_millionenshow_emblem(surf, cx, cy, radius, alpha=220, title_text=""):
    """Circular blue-green show emblem inspired by the reference image."""
    size = radius * 2 + scaled(34)
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    ox = oy = size // 2

    pygame.draw.circle(layer, (2, 8, 38, alpha), (ox, oy), radius)
    pygame.draw.circle(layer, (19, 42, 118, alpha), (ox, oy), radius, max(1, scaled(6)))
    pygame.draw.circle(
        layer,
        (42, 96, 150, min(255, alpha + 16)),
        (ox, oy),
        radius + scaled(3),
        max(1, scaled(1)),
    )

    inner_r = int(radius * 0.64)
    loops = 10
    for i in range(loops):
        angle = 2 * math.pi * i / loops
        x1 = ox + math.cos(angle) * inner_r
        y1 = oy + math.sin(angle) * inner_r
        x2 = ox + math.cos(angle + math.pi * 0.78) * inner_r
        y2 = oy + math.sin(angle + math.pi * 0.78) * inner_r
        pygame.draw.line(
            layer,
            (130, 205, 255, min(255, alpha + 18)),
            (x1, y1),
            (x2, y2),
            max(1, scaled(1)),
        )
        x3 = ox + math.cos(angle + math.pi * 0.22) * inner_r
        y3 = oy + math.sin(angle + math.pi * 0.22) * inner_r
        pygame.draw.line(
            layer,
            (76, 194, 143, min(255, alpha + 16)),
            (x1, y1),
            (x3, y3),
            max(1, scaled(2)),
        )

    for i in range(10):
        angle = 2 * math.pi * i / 10 + math.pi / 10
        x = ox + math.cos(angle) * (radius - scaled(20))
        y = oy + math.sin(angle) * (radius - scaled(20))
        pygame.draw.rect(
            layer,
            (218, 231, 154, min(255, alpha + 22)),
            (x - scaled(3), y - scaled(3), scaled(6), scaled(6)),
        )

    if title_text:
        text = FONT_TITLE.render(title_text, True, WHITE)
        shadow = FONT_TITLE.render(title_text, True, (0, 0, 0))
        layer.blit(shadow, shadow.get_rect(center=(ox + scaled(4), oy + scaled(4))))
        layer.blit(text, text.get_rect(center=(ox, oy)))

    surf.blit(layer, (cx - ox, cy - oy))


def draw_string_lights(surf, y_anchor=28, sag=22, bulbs=14):
    """Subtle top stage line."""
    x_start, x_end = scaled(70), WIDTH - scaled(70)
    pygame.draw.line(
        surf,
        ACCENT_BLUE_DARK,
        (x_start, scaled(y_anchor)),
        (x_end, scaled(y_anchor)),
        max(1, scaled(2)),
    )


def draw_leaf(surf, cx, cy, angle_deg, length=22, width=9, color=SUCCESS_GREEN):
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
    pygame.draw.line(surf, ACCENT_BLUE_LIGHT, (x, y), (end_x, end_y), 2)
    for i in range(1, leaves + 1):
        t = i / (leaves + 1)
        lx = x + (end_x - x) * t
        ly = y + (end_y - y) * t
        side = 1 if (i % 2 == 0) ^ flip else -1
        leaf_angle = angle_deg + side * 38
        ox = lx + math.cos(math.radians(leaf_angle)) * 11
        oy = ly + math.sin(math.radians(leaf_angle)) * 11
        draw_leaf(surf, ox, oy, leaf_angle, length=22, width=8, color=SUCCESS_GREEN)
    pygame.draw.circle(surf, SUCCESS_GREEN_LIGHT, (int(x), int(y)), scaled(5))


def draw_stage_accent(surf, cx, cy, r=11):
    """Small concentric Millionenshow-style accent."""
    pygame.draw.circle(surf, ACCENT_BLUE_DARK, (cx, cy), r)
    pygame.draw.circle(surf, DEEP_BLUE, (cx, cy), max(1, r - 4))
    pygame.draw.circle(surf, SUCCESS_GREEN, (cx, cy), max(1, r - 8))
    pygame.draw.circle(surf, ACCENT_BLUE_LIGHT, (cx, cy), r, 1)


def draw_heart(surf, cx, cy, size=10, color=ANSWER_BLUE):
    """Small diamond light used as an accent."""
    pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, WHITE, pts, 1)


def draw_show_bar(surf, cx, cy, w=110, h=16):
    """Blue-green answer-bar accent."""
    cy = scaled(cy) if cy <= BASE_HEIGHT else cy
    w, h = scaled(w), scaled(h)
    x = cx - w // 2
    pygame.draw.rect(surf, DEEP_BLUE, (x, cy - h // 2, w, h), border_radius=scaled(8))
    pygame.draw.rect(
        surf,
        ACCENT_BLUE,
        (x + scaled(8), cy - h // 2 + scaled(3), w - scaled(16), h - scaled(6)),
        border_radius=scaled(6),
    )
    pygame.draw.rect(
        surf,
        SUCCESS_GREEN,
        (x + w // 2 - scaled(18), cy - h // 2, scaled(36), h),
        border_radius=scaled(6),
    )
    pygame.draw.rect(
        surf, WHITE, (x, cy - h // 2, w, h), max(1, scaled(1)), border_radius=scaled(8)
    )


def draw_divider(surf, y, width=240):
    y = scaled(y) if y <= BASE_HEIGHT else y
    width = scaled(width)
    draw_divider_px(surf, y, width)


def draw_divider_px(surf, y, width=240):
    cx = WIDTH // 2
    pygame.draw.line(
        surf,
        ACCENT_BLUE_LIGHT,
        (cx - width // 2, y),
        (cx - scaled(26), y),
        max(1, scaled(2)),
    )
    pygame.draw.line(
        surf,
        ACCENT_BLUE_LIGHT,
        (cx + scaled(26), y),
        (cx + width // 2, y),
        max(1, scaled(2)),
    )
    draw_stage_accent(surf, cx, y, r=scaled(10))


def draw_corner_decorations(surf):
    """No extra corner shapes on the simple stage."""
    return


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
        base = ANSWER_BLUE if self.primary else ACCENT_BLUE
        hi = DEEP_BLUE if self.primary else ACCENT_BLUE_DARK
        color = hi if self.hover else base
        pygame.draw.rect(surf, color, self.rect, border_radius=scaled(14))
        pygame.draw.rect(
            surf, TEXT_LIGHT, self.rect, max(1, scaled(1)), border_radius=scaled(14)
        )
        # small stage-light accents on the sides
        draw_stage_accent(
            surf, self.rect.x + scaled(30), self.rect.centery, r=scaled(8)
        )
        draw_stage_accent(
            surf, self.rect.right - scaled(30), self.rect.centery, r=scaled(8)
        )
        txt = FONT_BTN.render(self.label, True, WHITE)
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
            pygame.draw.rect(surf, DEEP_BLUE, self.rect, border_radius=scaled(12))
            pygame.draw.rect(
                surf,
                ACCENT_BLUE_DARK,
                self.rect,
                max(1, scaled(1)),
                border_radius=scaled(12),
            )
            return
        if self.state == "correct":
            fill, border, fg, badge_fg = SUCCESS_GREEN, SUCCESS_GREEN_DARK, WHITE, WHITE
        elif self.state == "wrong":
            fill, border, fg, badge_fg = WRONG_RED, DEEP_BLUE, WHITE, WHITE
        elif self.state == "dimmed":
            fill, border, fg, badge_fg = PANEL_BLUE, MUTED_TEXT, MUTED_TEXT, MUTED_TEXT
        elif self.state == "selected":
            fill, border, fg, badge_fg = ACCENT_BLUE, ACCENT_BLUE_LIGHT, WHITE, WHITE
        else:
            fill = ANSWER_BLUE if not self.hover else ACCENT_BLUE_DARK
            border = ACCENT_BLUE_LIGHT if not self.hover else SUCCESS_GREEN_LIGHT
            fg = WHITE
            badge_fg = GOLD if not self.hover else SUCCESS_GREEN_LIGHT
        border_w = scaled(3) if self.state == "selected" else scaled(2)
        pygame.draw.rect(surf, fill, self.rect, border_radius=scaled(12))
        pygame.draw.rect(
            surf, border, self.rect, max(1, border_w), border_radius=scaled(12)
        )

        # letter badge (circle)
        bx = self.rect.x + scaled(38)
        by = self.rect.centery
        pygame.draw.circle(
            surf, DEEP_BLUE if self.state == "idle" else fill, (bx, by), scaled(20)
        )
        pygame.draw.circle(surf, badge_fg, (bx, by), scaled(20), max(1, scaled(2)))
        letter_surf = FONT_OPT_BD.render(self.letter, True, badge_fg)
        surf.blit(letter_surf, letter_surf.get_rect(center=(bx, by - scaled(1))))

        text_surf = FONT_OPT.render(self.text, True, fg)
        surf.blit(
            text_surf,
            (self.rect.x + scaled(78), self.rect.centery - text_surf.get_height() // 2),
        )

    def handle(self, event):
        if (
            self.state not in ("idle", "selected", "correct")
            or self.state == "eliminated"
        ):
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
    pygame.draw.rect(
        surf, SUCCESS_GREEN, outer, max(1, scaled(2)), border_radius=scaled(10)
    )
    pygame.draw.rect(
        surf, SUCCESS_GREEN_LIGHT, inner, max(1, scaled(1)), border_radius=scaled(8)
    )
    surf.blit(PORTRAIT, rect)


def draw_show_title_emblem(surf, cx, cy):
    photo_size = scaled(275)
    photo = pygame.transform.smoothscale(TITLE_PHOTO, (photo_size, photo_size))
    masked = pygame.Surface((photo_size, photo_size), pygame.SRCALPHA)
    pygame.draw.circle(
        masked,
        (255, 255, 255, 255),
        (photo_size // 2, photo_size // 2),
        photo_size // 2,
    )
    masked.blit(photo, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    rect = masked.get_rect(center=(cx, cy))
    surf.blit(masked, rect)


# ---------- Screens ----------
def title_screen():
    btn = Button(
        (WIDTH // 2 - 200, HEIGHT - 130, 400, 68), "Start the Game", primary=True
    )
    start_title_music()

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if btn.handle(event):
                return

        draw_studio_background(screen, emblem=False)

        draw_show_title_emblem(screen, WIDTH // 2, scaled(230))

        draw_centered_text(screen, "Omas 80er Quiz", FONT_TITLE, WHITE, 410)
        draw_show_bar(screen, WIDTH // 2, 470, w=150, h=10)
        draw_centered_text(screen, "Omillionenshow", FONT_SUB, MUTED_TEXT, 515)

        btn.draw(screen)

        update_display()
        clock.tick(FPS)


def play_intro_sound():
    if INTRO_SOUND is None:
        for _ in range(36):
            draw_studio_background(screen)
            draw_corner_decorations(screen)
            draw_centered_text_px(
                screen, "♪  ♪  ♪", FONT_TITLE, ANSWER_BLUE, HEIGHT // 2 - scaled(20)
            )
            draw_centered_text_px(
                screen,
                "(add assets/millionaire.mp3)",
                FONT_SMALL,
                MUTED_TEXT,
                HEIGHT // 2 + scaled(50),
            )
            update_display()
            clock.tick(FPS)
        return

    INTRO_SOUND.play()
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1500:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        draw_studio_background(screen)
        draw_corner_decorations(screen)
        draw_centered_text_px(screen, "♪", FONT_TITLE, ANSWER_BLUE, HEIGHT // 2)
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

_JOKER_RADIUS = scaled(31)
_JOKER_CENTERS = [
    (WIDTH - scaled(254), scaled(72)),  # index 0 — Publikum
    (WIDTH - scaled(188), scaled(72)),  # index 1 — Gatte
    (WIDTH - scaled(122), scaled(72)),  # index 2 — Kinder
    (WIDTH - scaled(56), scaled(72)),  # index 3 — 50:50
]
_JOKER_COLORS = [SUCCESS_GREEN, ACCENT_BLUE, GREEN_ACCENT, ANSWER_BLUE]
_JOKER_LABELS = ["PUB", "GATTE", "KIDS", "50:50"]


def draw_joker_icons(surf, used):
    for i, (cx, cy) in enumerate(_JOKER_CENTERS):
        active = not used[i]
        color = _JOKER_COLORS[i] if active else MUTED_TEXT
        pygame.draw.circle(surf, color, (cx, cy), _JOKER_RADIUS)
        pygame.draw.circle(surf, STAGE_BLUE, (cx, cy), _JOKER_RADIUS, 1)
        lbl = FONT_SMALL.render(_JOKER_LABELS[i], True, WHITE if active else PANEL_BLUE)
        surf.blit(lbl, lbl.get_rect(center=(cx, cy)))
        if not active:
            d = _JOKER_RADIUS - 8
            pygame.draw.line(surf, PANEL_BLUE, (cx - d, cy - d), (cx + d, cy + d), 2)
            pygame.draw.line(surf, PANEL_BLUE, (cx + d, cy - d), (cx - d, cy + d), 2)


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
    pygame.draw.rect(surf, STAGE_BLUE, (px, py, pw, ph), border_radius=scaled(18))
    pygame.draw.rect(
        surf,
        SUCCESS_GREEN,
        (px, py, pw, ph),
        max(1, scaled(2)),
        border_radius=scaled(18),
    )
    pygame.draw.rect(
        surf,
        SUCCESS_GREEN_LIGHT,
        (px + scaled(7), py + scaled(7), pw - scaled(14), ph - scaled(14)),
        max(1, scaled(1)),
        border_radius=scaled(13),
    )
    return px, py, pw, ph


def show_publikum_joker(surf_behind):
    """Live vote overlay — bars are hidden until AUDIENCE_REVEAL_AT total votes."""
    if JOKER_AUDIENCE_SFX:
        JOKER_AUDIENCE_SFX.play()

    votes = [0, 0, 0, 0]
    letters = ["A", "B", "C", "D"]
    btn = None

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    votes[0] += 1
                if event.key in (pygame.K_2, pygame.K_KP2):
                    votes[1] += 1
                if event.key in (pygame.K_3, pygame.K_KP3):
                    votes[2] += 1
                if event.key in (pygame.K_4, pygame.K_KP4):
                    votes[3] += 1
            if btn is not None and btn.handle(event):
                return

        screen.blit(surf_behind, (0, 0))
        px, py, pw, ph = draw_modal_base(screen, height=470)
        if btn is None:
            btn = Button(
                (BASE_WIDTH // 2 - 130, BASE_HEIGHT // 2 + 185, 260, 58),
                "Fertig!",
                primary=True,
            )

        draw_centered_text_px(
            screen, "Publikums-Joker", FONT_Q, TEXT_LIGHT, py + scaled(52)
        )
        draw_divider_px(screen, py + scaled(78), width=scaled(200))

        total = sum(votes)
        revealed = total >= AUDIENCE_REVEAL_AT

        if not revealed:
            draw_centered_text_px(
                screen,
                "Drückt 1, 2, 3 oder 4 zum Abstimmen!",
                FONT_SUB,
                SUCCESS_GREEN_DARK,
                py + scaled(115),
            )
            draw_centered_text_px(
                screen,
                f"{total} Stimme{'n' if total != 1 else ''} abgegeben",
                FONT_SMALL,
                MUTED_TEXT,
                py + scaled(158),
            )
            dots = "." * ((pygame.time.get_ticks() // 500) % 4)
            draw_centered_text_px(
                screen,
                f"Warte auf Stimmen{dots}",
                FONT_SMALL,
                MUTED_TEXT,
                py + scaled(184),
            )
        else:
            draw_centered_text_px(
                screen,
                "Drückt 1, 2, 3 oder 4 zum Abstimmen!",
                FONT_SMALL,
                MUTED_TEXT,
                py + scaled(98),
            )
            bar_x = px + scaled(120)
            bar_max_w = pw - scaled(260)
            bar_h, gap = scaled(34), scaled(13)
            bar_start = py + scaled(122)
            for i in range(4):
                by = bar_start + i * (bar_h + gap)
                pct = votes[i] / total
                filled = int(bar_max_w * pct)
                lbl = FONT_OPT_BD.render(letters[i], True, SUCCESS_GREEN_DARK)
                screen.blit(
                    lbl, (bar_x - scaled(50), by + bar_h // 2 - lbl.get_height() // 2)
                )
                pygame.draw.rect(
                    screen,
                    PANEL_BLUE,
                    (bar_x, by, bar_max_w, bar_h),
                    border_radius=scaled(8),
                )
                if filled > 0:
                    pygame.draw.rect(
                        screen,
                        SUCCESS_GREEN,
                        (bar_x, by, filled, bar_h),
                        border_radius=scaled(8),
                    )
                pygame.draw.rect(
                    screen,
                    SUCCESS_GREEN_DARK,
                    (bar_x, by, bar_max_w, bar_h),
                    max(1, scaled(1)),
                    border_radius=scaled(8),
                )
                pct_lbl = FONT_SMALL.render(f"{round(pct*100)} %", True, TEXT_LIGHT)
                screen.blit(
                    pct_lbl,
                    (
                        bar_x + bar_max_w + scaled(10),
                        by + bar_h // 2 - pct_lbl.get_height() // 2,
                    ),
                )
            draw_centered_text_px(
                screen,
                f"{total} Stimmen abgegeben",
                FONT_SMALL,
                MUTED_TEXT,
                btn.rect.y - scaled(16),
            )

        btn.draw(screen)
        update_display()
        clock.tick(FPS)


def show_parent_joker(surf_behind, joker_name, prompt):
    """Simple popup — no game logic, just a reminder to ask someone."""
    if JOKER_PHONE_SFX:
        JOKER_PHONE_SFX.play()

    btn = Button(
        (WIDTH // 2 - 160, HEIGHT // 2 + 110, 320, 58), "Fertig", primary=False
    )

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn.handle(event):
                return

        screen.blit(surf_behind, (0, 0))
        px, py, pw, ph = draw_modal_base(screen)

        draw_centered_text_px(
            screen, f"{joker_name}-Joker", FONT_Q, TEXT_LIGHT, py + scaled(52)
        )
        draw_divider_px(screen, py + scaled(78), width=scaled(200))
        draw_centered_text_px(screen, prompt, FONT_TITLE, TEXT_LIGHT, py + scaled(170))
        draw_centered_text_px(
            screen,
            "(und dann schnell antworten)",
            FONT_SMALL,
            MUTED_TEXT,
            py + scaled(228),
        )

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
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if btn.handle(event):
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_centered_text(screen, "So geht's", FONT_TITLE, TEXT_LIGHT, 110)
        draw_divider(screen, 148, width=220)

        # Game structure
        draw_centered_text(
            screen,
            f"{len(CATEGORIES)} Kategorien · {sum(len(c['questions']) for c in CATEGORIES)} Fragen · von leicht bis schwer",
            FONT_SUB,
            ACCENT_BLUE_LIGHT,
            188,
        )
        draw_centered_text(
            screen,
            "Du wählst die Reihenfolge der Kategorien selbst.",
            FONT_SUB,
            TEXT_LIGHT,
            224,
        )

        # Joker explanation — centred columns (icon on top, text below)
        circle_y = scaled(308)
        label_y = scaled(352)
        desc_y = scaled(378)
        block_cxs = [
            WIDTH // 2 - scaled(315),
            WIDTH // 2 - scaled(105),
            WIDTH // 2 + scaled(105),
            WIDTH // 2 + scaled(315),
        ]
        labels = ["PUB", "GATTE", "KIDS", "50:50"]
        colors = [SUCCESS_GREEN, ACCENT_BLUE, GREEN_ACCENT, ANSWER_BLUE]
        titles = ["Publikum", "Gatte", "Kinder", "50 : 50"]
        descs = [
            "Gäste tippen 1–4.\nBalken erscheinen\nnach 5 Stimmen.",
            "Frag deinen Gatten.",
            "Frag die Kinder\ngemeinsam.",
            "Zwei falsche\nAntworten\nverschwinden.",
        ]

        for bcx, lbl, col, title, desc in zip(block_cxs, labels, colors, titles, descs):
            # Icon circle (centred on bcx)
            pygame.draw.circle(screen, col, (bcx, circle_y), scaled(28))
            pygame.draw.circle(
                screen, STAGE_BLUE, (bcx, circle_y), scaled(28), max(1, scaled(1))
            )
            lbl_s = FONT_SMALL.render(lbl, True, WHITE)
            screen.blit(lbl_s, lbl_s.get_rect(center=(bcx, circle_y)))
            # Title centred
            t_s = FONT_OPT_BD.render(title, True, TEXT_LIGHT)
            screen.blit(t_s, t_s.get_rect(center=(bcx, label_y)))
            # Description lines centred
            for di, dline in enumerate(desc.split("\n")):
                d_s = FONT_SMALL.render(dline, True, TEXT_LIGHT)
                screen.blit(d_s, d_s.get_rect(center=(bcx, desc_y + di * scaled(20))))

        # Click mechanic reminder
        draw_divider(screen, 430, width=300)
        draw_centered_text(
            screen,
            "Jeder Joker kann nur einmal pro Spiel verwendet werden.",
            FONT_SMALL,
            MUTED_TEXT,
            486,
        )
        draw_centered_text(
            screen,
            "Fun Stuff kommt zuletzt und wird erst nach den anderen Kategorien freigeschaltet.",
            FONT_SMALL,
            MUTED_TEXT,
            512,
        )
        draw_centered_text(
            screen,
            "In Fun Stuff sind alle Joker deaktiviert.",
            FONT_SMALL,
            MUTED_TEXT,
            536,
        )

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
        (margin_x, margin_y),
        (margin_x + card_w + gap_x, margin_y),
        (margin_x, margin_y + card_h + gap_y),
        (margin_x + card_w + gap_x, margin_y + card_h + gap_y),
    ]
    hover_idx = -1

    while True:
        mx, my = mouse_pos()
        hover_idx = -1
        for i, (cx, cy) in enumerate(positions):
            locked = is_fun_stuff_category(i) and not fun_stuff_unlocked(done)
            if (
                i not in done
                and not locked
                and pygame.Rect(cx, cy, card_w, card_h).collidepoint(mx, my)
            ):
                hover_idx = i

        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (cx, cy) in enumerate(positions):
                    locked = is_fun_stuff_category(i) and not fun_stuff_unlocked(done)
                    if (
                        i not in done
                        and not locked
                        and pygame.Rect(cx, cy, card_w, card_h).collidepoint(mx, my)
                    ):
                        return i

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        remaining = len(CATEGORIES) - len(done)
        draw_centered_text(screen, "Wähle eine Kategorie", FONT_Q, WHITE, 98)
        draw_centered_text(
            screen,
            f"Noch {remaining} von {len(CATEGORIES)} offen",
            FONT_SMALL,
            MUTED_TEXT,
            128,
        )

        for i, (cx, cy) in enumerate(positions):
            cat = CATEGORIES[i]
            color = cat["color"]
            done_ = i in done
            locked = is_fun_stuff_category(i) and not fun_stuff_unlocked(done)
            hover = i == hover_idx
            r = pygame.Rect(cx, cy, card_w, card_h)

            if done_:
                bg, border, bw = PANEL_BLUE, SUCCESS_GREEN_LIGHT, 2
            elif locked:
                bg, border, bw = PANEL_BLUE, MUTED_TEXT, 2
            elif hover:
                bg, border, bw = ACCENT_BLUE_DARK, color, 3
            else:
                bg, border, bw = DEEP_BLUE, ACCENT_BLUE_LIGHT, 2

            pygame.draw.rect(screen, bg, r, border_radius=16)
            pygame.draw.rect(screen, border, r, bw, border_radius=16)

            # Coloured top bar
            top_bar = pygame.Rect(cx, cy, card_w, 8)
            top_col = SUCCESS_GREEN_LIGHT if done_ else MUTED_TEXT if locked else color
            pygame.draw.rect(
                screen,
                top_col,
                top_bar,
                border_top_left_radius=16,
                border_top_right_radius=16,
            )

            if done_:
                check = FONT_TITLE.render("✓", True, SUCCESS_GREEN)
                screen.blit(
                    check, check.get_rect(center=(r.centerx, r.centery - scaled(18)))
                )
                lbl = FONT_SMALL.render(cat["name"], True, MUTED_TEXT)
                screen.blit(
                    lbl, lbl.get_rect(center=(r.centerx, r.centery + scaled(36)))
                )
            elif locked:
                name_s = pygame.font.SysFont(
                    SERIF, scaled_font(36), bold=True, italic=True
                ).render(cat["name"], True, MUTED_TEXT)
                screen.blit(
                    name_s, name_s.get_rect(center=(r.centerx, r.centery - scaled(22)))
                )
                sub_s = FONT_SMALL.render(
                    "Erst nach den anderen Kategorien", True, MUTED_TEXT
                )
                screen.blit(
                    sub_s, sub_s.get_rect(center=(r.centerx, r.centery + scaled(22)))
                )
                lock_s = FONT_OPT_BD.render("Gesperrt", True, MUTED_TEXT)
                screen.blit(
                    lock_s, lock_s.get_rect(center=(r.centerx, r.centery + scaled(62)))
                )
            else:
                name_s = pygame.font.SysFont(
                    SERIF, scaled_font(36), bold=True, italic=True
                ).render(cat["name"], True, WHITE)
                screen.blit(
                    name_s, name_s.get_rect(center=(r.centerx, r.centery - scaled(22)))
                )
                sub_s = FONT_SMALL.render(
                    f"{len(cat['questions'])} Fragen · leicht  →  schwer",
                    True,
                    MUTED_TEXT,
                )
                screen.blit(
                    sub_s, sub_s.get_rect(center=(r.centerx, r.centery + scaled(22)))
                )
                # difficulty dots
                for d in range(5):
                    dot_x = r.centerx - scaled(40) + d * scaled(20)
                    dot_y = r.centery + scaled(60)
                    dot_c = color if not hover else SUCCESS_GREEN_LIGHT
                    pygame.draw.circle(screen, dot_c, (dot_x, dot_y), scaled(5))
                    pygame.draw.circle(
                        screen, PANEL_BLUE, (dot_x, dot_y), scaled(5), max(1, scaled(1))
                    )

        update_display()
        clock.tick(FPS)


def category_intro_screen(cat):
    """Full-screen splash with the category name. Click anywhere to begin."""
    color = cat["color"]
    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_centered_text(screen, "Kategorie", FONT_SUB, MUTED_TEXT, 270)
        draw_centered_text(screen, cat["name"], FONT_TITLE, color, 340)
        draw_divider(screen, 390, width=200)
        draw_centered_text(
            screen,
            f"{len(cat['questions'])} Fragen · leicht bis schwer",
            FONT_SUB,
            SUCCESS_GREEN_LIGHT,
            428,
        )
        draw_centered_text(
            screen, "Klick irgendwo zum Starten", FONT_SMALL, MUTED_TEXT, 490
        )

        update_display()
        clock.tick(FPS)


def question_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
    options = []
    letters = ["A", "B", "C", "D"]
    picture_name = question.get("picture") or question.get("image")
    is_picture_question = question.get("type") in ("picture", "picutre") or bool(
        picture_name
    )
    picture = (
        load_question_picture(picture_name, scaled(500), scaled(210))
        if is_picture_question
        else None
    )
    opt_w = 880
    opt_h = 56 if is_picture_question else 68
    gap = 10 if is_picture_question else 16
    start_y = 430 if is_picture_question else 320
    for i, text in enumerate(question["options"]):
        rect = ((WIDTH - opt_w) // 2, start_y + i * (opt_h + gap), opt_w, opt_h)
        options.append(OptionButton(rect, letters[i], text))

    selected = None
    revealed = False
    correct = question["answer"]
    award_point_on_wrong = question.get("award_point_on_wrong", False)

    while True:
        # Draw base frame first so overlays can snapshot it
        draw_studio_background(screen)
        draw_corner_decorations(screen)
        hdr_color = category_color if category_color else ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 78
        )
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)
        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for i, line in enumerate(lines):
            line_y = (135 + i * 38) if is_picture_question else (180 + i * 44)
            draw_centered_text(screen, line, FONT_Q, TEXT_LIGHT, line_y)
        if question.get("description"):
            desc_lines = wrap_text(question["description"], FONT_SMALL, WIDTH - 240)
            desc_y = (
                135 + len(lines) * 38 + 4
                if is_picture_question
                else 180 + len(lines) * 44 + 8
            )
            for i, line in enumerate(desc_lines):
                draw_centered_text(
                    screen, line, FONT_SMALL, MUTED_TEXT, desc_y + i * 22
                )
        if picture is not None:
            pic_rect = picture.get_rect(center=(WIDTH // 2, scaled(290)))
            frame = pic_rect.inflate(scaled(14), scaled(14))
            pygame.draw.rect(screen, PANEL_BLUE, frame, border_radius=scaled(10))
            pygame.draw.rect(
                screen,
                SUCCESS_GREEN_LIGHT,
                frame,
                max(1, scaled(2)),
                border_radius=scaled(10),
            )
            screen.blit(picture, pic_rect)
        for opt in options:
            opt.draw(screen)
        if revealed:
            hint_y = options[-1].rect.bottom + 28
            if award_point_on_wrong and selected != correct:
                draw_centered_text(
                    screen,
                    question.get(
                        "wrong_point_message",
                        "Falsch - aber es gibt dafür einen Punkt.",
                    ),
                    FONT_SMALL,
                    ACCENT_BLUE_LIGHT,
                    hint_y,
                )
                hint_y += 24
            draw_centered_text(
                screen,
                "Click the correct answer to continue",
                FONT_SMALL,
                ACCENT_BLUE_LIGHT,
                hint_y,
            )
        update_display()

        behind = screen.copy()  # snapshot for overlay compositing

        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Joker icon clicks — only before reveal, only if not yet used
            if not revealed:
                ji = joker_clicked(event)
                if ji == 0 and not joker_used[0]:  # Publikum
                    joker_used[0] = True
                    show_publikum_joker(behind)
                elif ji == 1 and not joker_used[1]:  # Gatte
                    joker_used[1] = True
                    show_parent_joker(behind, "Gatte", "Frag den Gatten!")
                elif ji == 2 and not joker_used[2]:  # Kinder
                    joker_used[2] = True
                    show_parent_joker(behind, "Kinder", "Frag die Kinder!")
                elif ji == 3 and not joker_used[3]:  # 50:50
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
                        return selected == correct or (
                            award_point_on_wrong and selected != correct
                        )

        clock.tick(FPS)


# ---------- Audio + free-text question ----------


def _normalize_text_answer(text):
    return "".join(ch for ch in text.lower().strip() if ch.isalnum())


def audio_text_question_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
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
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                stop_audio()
                pygame.quit()
                sys.exit()

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
                        is_correct = _normalize_text_answer(
                            answer_text
                        ) == _normalize_text_answer(question["answer"])
                    elif (
                        event.unicode
                        and event.unicode.isprintable()
                        and len(answer_text) < 40
                    ):
                        answer_text += event.unicode
                        stop_audio()

                if btn_fertig.handle(event):
                    submitted = True
                    stop_audio()
                    is_correct = _normalize_text_answer(
                        answer_text
                    ) == _normalize_text_answer(question["answer"])
            else:
                if btn_weiter.handle(event):
                    stop_audio()
                    return is_correct

        btn_audio.label = "Stop" if playing else "Play"

        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 78
        )
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)

        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for i, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, TEXT_LIGHT, 180 + i * 44)

        btn_audio.draw(screen)

        pygame.draw.rect(screen, WHITE, input_rect, border_radius=12)
        pygame.draw.rect(
            screen,
            SUCCESS_GREEN if not submitted else MUTED_TEXT,
            input_rect,
            2,
            border_radius=12,
        )
        shown_text = answer_text if answer_text else "Antwort eintippen..."
        text_col = TEXT_DARK if answer_text else MUTED_TEXT
        text_surf = FONT_OPT.render(shown_text[-34:], True, text_col)
        screen.blit(
            text_surf,
            text_surf.get_rect(midleft=(input_rect.x + 22, input_rect.centery)),
        )

        if not submitted and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = input_rect.x + 24 + FONT_OPT.size(answer_text[-34:])[0]
            pygame.draw.line(
                screen,
                TEXT_DARK,
                (cursor_x, input_rect.y + 18),
                (cursor_x, input_rect.bottom - 18),
                2,
            )

        if submitted:
            result_col = SUCCESS_GREEN if is_correct else ANSWER_BLUE
            result_txt = (
                "Richtig!"
                if is_correct
                else f"Falsch - richtig ist: {question['answer']}"
            )
            draw_centered_text(screen, result_txt, FONT_OPT_BD, result_col, 480)
            btn_weiter.draw(screen)
        else:
            btn_fertig.draw(screen)

        update_display()
        clock.tick(FPS)


# ---------- Fun photo text question ----------

FUN_PHOTO_DIR = os.path.join(ASSETS_DIR, "fun_fotos")
FUN_PHOTO_EXTS = ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG")


def _find_fun_photo(prefix, original=False):
    suffix = "_og" if original else ""
    for ext in FUN_PHOTO_EXTS:
        path = os.path.join(FUN_PHOTO_DIR, f"{prefix}{suffix}.{ext}")
        if os.path.exists(path):
            return path
    print(f"[hint] missing fun photo: assets/fun_fotos/{prefix}{suffix}.*")
    return None


def _load_scaled_photo_path(path, max_w, max_h, label):
    if path and os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            iw, ih = img.get_size()
            scale = min(max_w / iw, max_h / ih)
            size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            return pygame.transform.smoothscale(img, size)
        except pygame.error as e:
            print(f"Could not load fun photo '{path}': {e}")

    surf = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
    surf.fill(PANEL_BLUE)
    pygame.draw.rect(surf, MUTED_TEXT, surf.get_rect(), max(1, scaled(2)))
    text = FONT_SMALL.render(label, True, MUTED_TEXT)
    surf.blit(text, text.get_rect(center=surf.get_rect().center))
    return surf


def _answer_matches_any_word(answer_text, accepted_words):
    normalized_answer = _normalize_text_answer(answer_text)
    return any(
        word and _normalize_text_answer(word) in normalized_answer
        for word in accepted_words
    )


def fun_photo_question_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
    prefix = question["photo"]
    modified_path = _find_fun_photo(prefix, original=False)
    original_path = _find_fun_photo(prefix, original=True)
    max_photo_w, max_photo_h = scaled(680), scaled(360)
    modified_photo = _load_scaled_photo_path(
        modified_path, max_photo_w, max_photo_h, f"add {prefix}.*"
    )
    original_photo = _load_scaled_photo_path(
        original_path, max_photo_w, max_photo_h, f"add {prefix}_og.*"
    )

    accepted_words = question.get("answers", question.get("answer", []))
    if isinstance(accepted_words, str):
        accepted_words = [accepted_words]

    answer_text = ""
    revealed = False
    showing_original = False
    is_correct = False

    input_w, input_h = scaled(640), scaled(58)
    input_rect = pygame.Rect(WIDTH // 2 - input_w // 2, scaled(565), input_w, input_h)
    btn_weiter = Button((WIDTH // 2 - 130, 642, 260, 52), "Weiter", primary=False)

    def reveal_answer():
        nonlocal revealed, showing_original, is_correct
        if revealed or not answer_text.strip():
            return
        revealed = True
        showing_original = True
        is_correct = _answer_matches_any_word(answer_text, accepted_words)
        sfx = CORRECT_SFX if is_correct else WRONG_SFX
        if sfx:
            sfx.play()

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if not revealed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        answer_text = answer_text[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        reveal_answer()
                    elif (
                        event.unicode
                        and event.unicode.isprintable()
                        and len(answer_text) < 50
                    ):
                        answer_text += event.unicode
            elif btn_weiter.handle(event):
                return is_correct

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current_photo = original_photo if showing_original else modified_photo
                photo_rect = current_photo.get_rect(center=(WIDTH // 2, scaled(350)))
                if photo_rect.collidepoint(event.pos):
                    if revealed:
                        showing_original = not showing_original
                    else:
                        reveal_answer()

        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 78
        )
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)

        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for i, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, TEXT_LIGHT, 135 + i * 38)

        photo = original_photo if showing_original else modified_photo
        photo_rect = photo.get_rect(center=(WIDTH // 2, scaled(350)))
        frame = photo_rect.inflate(scaled(14), scaled(14))
        border_col = SUCCESS_GREEN if revealed and is_correct else ACCENT_BLUE_LIGHT
        if revealed and not is_correct:
            border_col = WRONG_RED
        pygame.draw.rect(screen, PANEL_BLUE, frame, border_radius=scaled(10))
        pygame.draw.rect(
            screen, border_col, frame, max(1, scaled(2)), border_radius=scaled(10)
        )
        screen.blit(photo, photo_rect)

        pygame.draw.rect(screen, WHITE, input_rect, border_radius=12)
        pygame.draw.rect(
            screen,
            MUTED_TEXT if revealed else SUCCESS_GREEN,
            input_rect,
            2,
            border_radius=12,
        )
        shown_text = answer_text if answer_text else "Antwort eintippen..."
        text_col = TEXT_DARK if answer_text else MUTED_TEXT
        text_surf = FONT_OPT.render(shown_text[-38:], True, text_col)
        screen.blit(
            text_surf,
            text_surf.get_rect(midleft=(input_rect.x + scaled(22), input_rect.centery)),
        )

        if not revealed and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = input_rect.x + scaled(24) + FONT_OPT.size(answer_text[-38:])[0]
            pygame.draw.line(
                screen,
                TEXT_DARK,
                (cursor_x, input_rect.y + scaled(15)),
                (cursor_x, input_rect.bottom - scaled(15)),
                2,
            )

        if revealed:
            result_txt = "Richtig!" if is_correct else "Falsch"
            result_col = SUCCESS_GREEN if is_correct else WRONG_RED
            draw_centered_text(screen, result_txt, FONT_OPT_BD, result_col, 632)
            btn_weiter.draw(screen)
        else:
            draw_centered_text(
                screen,
                "Nach der Antwort auf das Bild klicken",
                FONT_SMALL,
                MUTED_TEXT,
                642,
            )

        update_display()
        clock.tick(FPS)


# ---------- Sudoku number question ----------


def sudoku_question_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
    picture = load_question_picture(question.get("picture"), scaled(390), scaled(390))
    answers = [str(x) for x in question["answer"]]
    values = ["", "", ""]
    active = 0
    submitted = False
    is_correct = False

    box_size = scaled(68)
    box_gap = scaled(24)
    total_w = 3 * box_size + 2 * box_gap
    input_y = scaled(555)
    input_rects = [
        pygame.Rect(
            WIDTH // 2 - total_w // 2 + i * (box_size + box_gap),
            input_y,
            box_size,
            box_size,
        )
        for i in range(3)
    ]
    button_y = input_y + box_size + scaled(30)
    btn_fertig = Button(
        (WIDTH // 2 - scaled(130), button_y, scaled(260), scaled(52)),
        "Fertig!",
        True,
        raw=True,
    )
    btn_weiter = Button(
        (WIDTH // 2 - scaled(130), button_y, scaled(260), scaled(52)),
        "Weiter",
        False,
        raw=True,
    )

    def delete_last_digit():
        nonlocal active
        filled = [i for i, value in enumerate(values) if value]
        if not filled:
            active = 0
            return
        idx_to_clear = filled[-1]
        values[idx_to_clear] = ""
        active = idx_to_clear

    def submit():
        nonlocal submitted, is_correct
        if submitted or any(not value for value in values):
            return
        submitted = True
        is_correct = values == answers
        sfx = CORRECT_SFX if is_correct else WRONG_SFX
        if sfx:
            sfx.play()

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if not submitted:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(input_rects):
                        if rect.collidepoint(event.pos):
                            active = i
                            break
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        delete_last_digit()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        submit()
                    elif event.unicode in "123456789":
                        values[active] = event.unicode
                        active = min(2, active + 1)
                if btn_fertig.handle(event):
                    submit()
            elif btn_weiter.handle(event):
                return is_correct

        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 78
        )
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)

        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for i, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, TEXT_LIGHT, 135 + i * 38)

        if picture is not None:
            pic_rect = picture.get_rect(center=(WIDTH // 2, scaled(355)))
            frame = pic_rect.inflate(scaled(12), scaled(12))
            pygame.draw.rect(screen, PANEL_BLUE, frame, border_radius=scaled(10))
            pygame.draw.rect(
                screen,
                ACCENT_BLUE_LIGHT,
                frame,
                max(1, scaled(2)),
                border_radius=scaled(10),
            )
            screen.blit(picture, pic_rect)

        for i, rect in enumerate(input_rects):
            if submitted:
                border = SUCCESS_GREEN if values[i] == answers[i] else WRONG_RED
            else:
                border = SUCCESS_GREEN_LIGHT if i == active else MUTED_TEXT
            pygame.draw.rect(screen, WHITE, rect, border_radius=scaled(10))
            pygame.draw.rect(
                screen, border, rect, max(2, scaled(2)), border_radius=scaled(10)
            )
            label = FONT_TITLE.render(
                values[i] if values[i] else "?",
                True,
                TEXT_DARK if values[i] else MUTED_TEXT,
            )
            screen.blit(label, label.get_rect(center=rect.center))

        if submitted:
            result_txt = (
                "Richtig!"
                if is_correct
                else f"Falsch - richtig ist: {' '.join(answers)}"
            )
            result_col = SUCCESS_GREEN if is_correct else WRONG_RED
            draw_centered_text_px(
                screen,
                result_txt,
                FONT_OPT_BD,
                result_col,
                button_y - scaled(18),
            )
            btn_weiter.draw(screen)
        else:
            btn_fertig.draw(screen)

        update_display()
        clock.tick(FPS)


# ---------- Photo-ordering question ----------

_OTILE_W = scaled(90)
_OTILE_IMGH = scaled(68)
_OTILE_H = _OTILE_IMGH
_OTILE_GAP = scaled(8)
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
    count = question.get("count", 10)
    prefix = question.get("photo_prefix", "foto_")
    photos = []
    for i in range(1, count + 1):
        loaded = False
        for ext in ("jpg", "jpeg", "png"):
            path = os.path.join(ASSETS_DIR, f"{prefix}{i}.{ext}")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    photos.append(
                        pygame.transform.smoothscale(img, (_OTILE_W, _OTILE_IMGH))
                    )
                    loaded = True
                    break
                except pygame.error:
                    pass
        if not loaded:
            surf = pygame.Surface((_OTILE_W, _OTILE_IMGH))
            surf.fill(PANEL_BLUE)
            pygame.draw.rect(surf, MUTED_TEXT, (0, 0, _OTILE_W, _OTILE_IMGH), 1)
            lbl = FONT_SMALL.render(f"Foto {i}", True, TEXT_LIGHT)
            surf.blit(lbl, lbl.get_rect(center=(_OTILE_W // 2, _OTILE_IMGH // 2)))
            photos.append(surf)
    return photos


def _draw_order_tile(surf, x, y, photo, number, state="idle"):
    if state == "correct":
        border, bw = SUCCESS_GREEN_DARK, 3
    elif state == "wrong":
        border, bw = DEEP_BLUE, 3
    elif state == "dragging":
        border, bw = ACCENT_BLUE_DARK, 3
    else:
        border, bw = SUCCESS_GREEN, 2

    surf.blit(photo, (x, y))
    pygame.draw.rect(surf, border, (x, y, _OTILE_W, _OTILE_IMGH), bw)


def ordering_question_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
    photos = _load_order_photos(question)
    count = len(photos)
    answer = [x - 1 for x in question["answer"]]  # 0-based correct order
    pass_at = question.get("pass_at", round(count * 0.6))

    cols = min(_OTILE_COLS, count)
    rows = math.ceil(count / cols)
    total_w = cols * _OTILE_W + (cols - 1) * _OTILE_GAP
    total_h = rows * _OTILE_H + (rows - 1) * _OTILE_ROW_GAP
    start_x = (WIDTH - total_w) // 2
    tile_y = scaled(285)

    order = list(range(count))
    random.shuffle(order)
    dragging = None  # slot index being dragged
    grab_dx = 0  # mouse_x minus tile left-x at drag start
    grab_dy = 0  # mouse_y minus tile top-y at drag start
    drag_mx = 0
    drag_my = 0
    confirmed = False

    button_w, button_h = scaled(260), scaled(56)
    button_y = tile_y + total_h + scaled(74)
    btn_fertig = Button(
        (WIDTH // 2 - button_w // 2, button_y, button_w, button_h),
        "Fertig!",
        primary=True,
        raw=True,
    )
    btn_weiter = Button(
        (WIDTH // 2 - button_w // 2, button_y, button_w, button_h),
        "Weiter",
        primary=False,
        raw=True,
    )

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if not confirmed:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for s in range(count):
                        tx, ty = _order_slot_pos(s, start_x, tile_y, cols)
                        if pygame.Rect(tx, ty, _OTILE_W, _OTILE_H).collidepoint(mx, my):
                            dragging = s
                            grab_dx = mx - tx
                            grab_dy = my - ty
                            drag_mx = mx
                            drag_my = my
                            break
                    if btn_fertig.handle(event):
                        confirmed = True

                if event.type == pygame.MOUSEMOTION and dragging is not None:
                    drag_mx = event.pos[0]
                    drag_my = event.pos[1]
                    tile_cx = drag_mx - grab_dx + _OTILE_W // 2
                    tile_cy = drag_my - grab_dy + _OTILE_H // 2
                    new_slot = _nearest_order_slot(
                        tile_cx, tile_cy, count, start_x, tile_y, cols
                    )
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
                    correct_count = sum(
                        1 for s in range(count) if order[s] == answer[s]
                    )
                    return correct_count >= pass_at

        # ---- Draw ----
        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 78
        )
        draw_joker_icons(screen, joker_used)
        draw_divider(screen, 108, width=260)

        lines = wrap_text(question["q"], FONT_Q, WIDTH - 200)
        for li, line in enumerate(lines):
            draw_centered_text(screen, line, FONT_Q, TEXT_LIGHT, 165 + li * 44)

        # Position numbers above each slot
        for s in range(count):
            tx, ty = _order_slot_pos(s, start_x, tile_y, cols)
            sx = tx + _OTILE_W // 2
            n = FONT_SMALL.render(str(s + 1), True, MUTED_TEXT)
            screen.blit(n, n.get_rect(center=(sx, ty - scaled(16))))

        # Draw non-dragged tiles first
        for s, photo_idx in enumerate(order):
            if s == dragging:
                continue
            state = "idle"
            if confirmed:
                state = "correct" if order[s] == answer[s] else "wrong"
            tx, ty = _order_slot_pos(s, start_x, tile_y, cols)
            _draw_order_tile(screen, tx, ty, photos[photo_idx], photo_idx + 1, state)

        # Dragged tile on top (floats with mouse)
        if dragging is not None:
            _draw_order_tile(
                screen,
                drag_mx - grab_dx,
                drag_my - grab_dy,
                photos[order[dragging]],
                order[dragging] + 1,
                "dragging",
            )

        if not confirmed:
            draw_centered_text_px(
                screen,
                "Ziehe die Fotos in die richtige Reihenfolge",
                FONT_SMALL,
                MUTED_TEXT,
                tile_y + total_h + scaled(34),
            )
            btn_fertig.draw(screen)
        else:
            correct_count = sum(1 for s in range(count) if order[s] == answer[s])
            result_col = SUCCESS_GREEN if correct_count >= pass_at else ANSWER_BLUE
            draw_centered_text_px(
                screen,
                f"{correct_count} / {count} richtig positioniert",
                FONT_Q,
                result_col,
                tile_y + total_h + scaled(34),
            )
            btn_weiter.draw(screen)

        update_display()
        clock.tick(FPS)


# ---------- Video question ----------

_VID_W = scaled(640)
_VID_H = scaled(360)  # 16:9
_VID_X = (WIDTH - _VID_W) // 2  # 230
_VID_Y = scaled(65)


import atexit
import shutil
import subprocess
import tempfile

_VIDEO_AUDIO_CACHE: dict = {}  # video_path → resolved audio path
_TEMP_AUDIO_FILES: list = []  # temp files to delete on exit


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
    for cand in (
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/opt/local/bin/ffmpeg",
    ):
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
                [ffmpeg_cmd, "-y", "-i", video_path, "-vn", "-q:a", "2", tmp.name],
                capture_output=True,
                timeout=60,
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
    rgb = _cv2.cvtColor(frame_bgr, _cv2.COLOR_BGR2RGB)
    scaled = _cv2.resize(rgb, (_VID_W, _VID_H))
    return pygame.surfarray.make_surface(scaled.swapaxes(0, 1))


def _make_frame_surface_fit(frame_bgr, max_w, max_h):
    """Convert an OpenCV frame to a pygame Surface while preserving aspect ratio."""
    rgb = _cv2.cvtColor(frame_bgr, _cv2.COLOR_BGR2RGB)
    ih, iw = rgb.shape[:2]
    scale = min(max_w / iw, max_h / ih)
    size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    scaled_frame = _cv2.resize(rgb, size)
    return pygame.surfarray.make_surface(scaled_frame.swapaxes(0, 1))


def video_question_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
    # ---- Graceful degradation if OpenCV is missing ----
    if not _CV2_OK:
        print("[warn] opencv-python not installed — falling back to multiple-choice")
        mc_q = {k: v for k, v in question.items()}
        mc_q.pop("video", None)
        mc_q.pop("audio", None)
        mc_q.pop("pause_at", None)
        mc_q.pop("stop_at", None)
        mc_q.pop("type", None)
        return question_screen(
            idx, mc_q, total, joker_used, category_name, category_color
        )

    video_path = os.path.join(ASSETS_DIR, question["video"])
    pause_at = float(question["pause_at"])
    stop_at = question.get("stop_at")
    stop_at = float(stop_at) if stop_at is not None else None
    correct = question["answer"]

    # ---- Open video ----
    if not os.path.exists(video_path):
        print(f"[warn] video not found: {video_path}")
        mc_q = {
            k: v
            for k, v in question.items()
            if k not in ("video", "audio", "pause_at", "stop_at", "type")
        }
        return question_screen(
            idx, mc_q, total, joker_used, category_name, category_color
        )

    cap = _cv2.VideoCapture(video_path)
    vid_fps = cap.get(_cv2.CAP_PROP_FPS) or 30.0
    frame_ms = 1000.0 / vid_fps

    # ---- Audio — load now (but don't play yet — user clicks ▶ to start) ----
    has_audio = False
    audio_file = _resolve_video_audio(video_path, question.get("audio", ""))
    if audio_file:
        try:
            pygame.mixer.music.load(audio_file)
            has_audio = True
        except Exception as e:
            print(f"[warn] audio load failed: {e}")

    # ---- Option buttons ----
    letters = ["A", "B", "C", "D"]
    opt_w, opt_h, opt_gap = 640, 52, 10
    opt_y0 = 65 + 360 + 46  # below video + question line
    options = []
    for i, text in enumerate(question["options"]):
        rect = ((BASE_WIDTH - opt_w) // 2, opt_y0 + i * (opt_h + opt_gap), opt_w, opt_h)
        options.append(OptionButton(rect, letters[i], text))

    # small restart button — lives inside video frame bottom-right
    btn_restart = Button(
        ((BASE_WIDTH - 640) // 2 + 640 - 126, 65 + 360 - 40, 120, 34),
        "↺ Neustart",
        primary=False,
    )
    # advance button — shown after video ends
    btn_weiter = Button(
        (BASE_WIDTH // 2 - 120, opt_y0 + 4 * (opt_h + opt_gap) + 10, 240, 52),
        "Weiter",
        primary=False,
    )

    # ---- State ----
    # Show the first frame as a "poster" with a ▶ overlay — click to start.
    poster_frame = None
    ret0, frm0 = cap.read()
    if ret0:
        poster_frame = _make_frame_surface(frm0)
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)  # rewind so playback starts at 0

    frame_surf = poster_frame
    not_started = True  # waiting for the user to click ▶
    play_start = 0
    elapsed_ms = 0
    last_read_ms = 0
    playing = False
    paused = False
    vid_ended = False
    selected = None
    answered = False  # True after the 2nd click — video keeps playing
    revealed = False  # True after the video ends — colors + sound

    video_rect = pygame.Rect(_VID_X, _VID_Y, _VID_W, _VID_H)

    def start_playback():
        nonlocal play_start, elapsed_ms, last_read_ms, playing, not_started
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)
        if has_audio:
            pygame.mixer.music.play()
        play_start = pygame.time.get_ticks()
        elapsed_ms = 0
        # Anchor the frame clock to wall time so the first read fires at play_start,
        # not at "tick 0 since pygame init".
        last_read_ms = play_start - frame_ms
        playing = True
        not_started = False

    def do_restart():
        nonlocal frame_surf, play_start, elapsed_ms, last_read_ms
        nonlocal playing, paused, vid_ended, selected, answered, revealed, not_started
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)
        if has_audio:
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
        play_start = pygame.time.get_ticks()
        elapsed_ms = 0
        last_read_ms = play_start - frame_ms
        playing = True
        paused = False
        vid_ended = False
        not_started = False
        selected = None
        answered = False
        revealed = False
        for o in options:
            o.state = "idle"
            o.hover = False

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
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if has_audio:
                    pygame.mixer.music.stop()
                cap.release()
                pygame.quit()
                sys.exit()

            # Click on video poster → start playback
            if (
                not_started
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
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
                            if LOCKIN_SFX:
                                LOCKIN_SFX.play()
                        else:
                            # 2nd click — resume video; the reveal waits for the video to end
                            if LOCKIN_SFX:
                                LOCKIN_SFX.stop()
                            answered = True
                            # lock the choice visually: dim every non-selected option
                            for j, o in enumerate(options):
                                if o.state == "eliminated":
                                    continue
                                if j != selected:
                                    o.state = "dimmed"
                                # the selected one keeps its lock-in colour.
                            # Resume both video AND audio from pause_at − 3 s
                            resume_s = max(0.0, pause_at - 3.0)
                            cap.set(_cv2.CAP_PROP_POS_MSEC, resume_s * 1000)
                            if has_audio:
                                # play(start=…) seeks AND resumes in one call.
                                # plain play() after set_pos() rewinds to 0 — that was the bug.
                                pygame.mixer.music.play(start=resume_s)
                            elapsed_ms = int(resume_s * 1000)
                            play_start = now - elapsed_ms
                            last_read_ms = now - frame_ms
                            paused = False
                            playing = True

            # Advance after the reveal: click the correct (green) answer
            if revealed:
                for i, opt in enumerate(options):
                    if opt.handle(event) and i == correct:
                        if has_audio:
                            pygame.mixer.music.stop()
                        cap.release()
                        return selected == correct

        # ---- Video update ----
        if playing and not paused:
            elapsed_ms = now - play_start
            elapsed_s = elapsed_ms / 1000.0

            # Pause at the designated timestamp
            if elapsed_s >= pause_at and not answered:
                paused = True
                playing = False
                if has_audio:
                    pygame.mixer.music.pause()
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
                        playing = False
                        # When the video finishes, NOW reveal the answer
                        if answered and not revealed:
                            reveal_answer()
                        break
                    latest_frm = frm
                    last_read_ms += frame_ms  # accumulate, NOT reset to now
                if latest_frm is not None:
                    frame_surf = _make_frame_surface(latest_frm)

        # ---- Draw ----
        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 40
        )
        draw_joker_icons(screen, joker_used)

        # Video frame
        if frame_surf:
            screen.blit(frame_surf, (_VID_X, _VID_Y))
        else:
            pygame.draw.rect(screen, TEXT_LIGHT, (_VID_X, _VID_Y, _VID_W, _VID_H))
            draw_centered_text_px(
                screen, "Wird geladen …", FONT_SMALL, MUTED_TEXT, _VID_Y + _VID_H // 2
            )
        # border
        pygame.draw.rect(screen, SUCCESS_GREEN, (_VID_X, _VID_Y, _VID_W, _VID_H), 2)

        # ▶ Play overlay before user starts the video
        if not_started:
            veil = pygame.Surface((_VID_W, _VID_H), pygame.SRCALPHA)
            veil.fill((0, 0, 0, 100))
            screen.blit(veil, (_VID_X, _VID_Y))
            # big triangle play icon, centered
            cx, cy = _VID_X + _VID_W // 2, _VID_Y + _VID_H // 2
            r = 44
            pygame.draw.circle(screen, (0, 0, 0, 0), (cx, cy), r + 4)
            pygame.draw.circle(screen, WHITE, (cx, cy), r)
            pygame.draw.circle(screen, SUCCESS_GREEN_DARK, (cx, cy), r, 3)
            tri = [
                (cx - 14, cy - 22),
                (cx - 14, cy + 22),
                (cx + 22, cy),
            ]
            pygame.draw.polygon(screen, SUCCESS_GREEN_DARK, tri)
            hint = FONT_SUB.render("Klick zum Starten", True, WHITE)
            shade = pygame.Surface(
                (hint.get_width() + 20, hint.get_height() + 10), pygame.SRCALPHA
            )
            shade.fill((0, 0, 0, 160))
            shade_pos = (cx - shade.get_width() // 2, cy + r + 14)
            screen.blit(shade, shade_pos)
            screen.blit(hint, (shade_pos[0] + 10, shade_pos[1] + 5))

        # Pause banner inside video
        if paused and not revealed:
            banner = FONT_SMALL.render("▐▐  Antworte jetzt!", True, WHITE)
            bx = _VID_X + _VID_W // 2 - banner.get_width() // 2 - 8
            by = _VID_Y + _VID_H - 30
            shade = pygame.Surface(
                (banner.get_width() + 16, banner.get_height() + 8), pygame.SRCALPHA
            )
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
                draw_centered_text_px(
                    screen,
                    line,
                    FONT_Q,
                    TEXT_LIGHT,
                    _VID_Y + _VID_H + scaled(22) + li * scaled(38),
                )
            for opt in options:
                opt.draw(screen)

        # After the reveal: hint that clicking the correct answer advances
        if revealed:
            draw_centered_text_px(
                screen,
                "Click the correct answer to continue",
                FONT_SMALL,
                SUCCESS_GREEN_DARK,
                options[-1].rect.bottom + scaled(16),
            )
        elif vid_ended and not answered:
            # Edge case: video ended before the user answered
            draw_centered_text_px(
                screen,
                "Wähle eine Antwort",
                FONT_SMALL,
                MUTED_TEXT,
                options[-1].rect.bottom + scaled(16),
            )

        update_display()
        clock.tick(FPS)


def video_challenge_screen(
    idx, question, total, joker_used, category_name="", category_color=None
):
    video_path = os.path.join(ASSETS_DIR, question["video"])
    challenge_text = question.get("challenge", "")
    chal_w, chal_h = scaled(330), scaled(440)
    chal_x = (WIDTH - chal_w) // 2
    chal_y = scaled(78)
    video_rect = pygame.Rect(chal_x, chal_y, chal_w, chal_h)
    prompt_y = video_rect.bottom + scaled(24)
    button_y = video_rect.bottom + scaled(112)
    btn_success = Button(
        (WIDTH // 2 - scaled(280), button_y, scaled(240), scaled(48)),
        "Geschafft",
        True,
        raw=True,
    )
    btn_failure = Button(
        (WIDTH // 2 + scaled(40), button_y, scaled(240), scaled(48)),
        "Nicht geschafft",
        False,
        raw=True,
    )

    cap = None
    frame_surf = None
    vid_fps = 30.0
    frame_ms = 1000.0 / vid_fps
    has_audio = False

    if not _CV2_OK:
        print("[warn] opencv-python not installed — video challenge will skip playback")
        vid_ended = True
        not_started = False
        playing = False
    elif not os.path.exists(video_path):
        print(f"[warn] video not found: {video_path}")
        vid_ended = True
        not_started = False
        playing = False
    else:
        cap = _cv2.VideoCapture(video_path)
        vid_fps = cap.get(_cv2.CAP_PROP_FPS) or 30.0
        frame_ms = 1000.0 / vid_fps

        ret0, frm0 = cap.read()
        if ret0:
            frame_surf = _make_frame_surface_fit(frm0, chal_w, chal_h)
            cap.set(_cv2.CAP_PROP_POS_MSEC, 0)

        audio_file = _resolve_video_audio(video_path, question.get("audio", ""))
        if audio_file:
            try:
                pygame.mixer.music.load(audio_file)
                has_audio = True
            except Exception as e:
                print(f"[warn] audio load failed: {e}")

        vid_ended = False
        not_started = True
        playing = False

    play_start = 0
    last_read_ms = 0

    def start_playback():
        nonlocal play_start, last_read_ms, playing, not_started, vid_ended
        if cap is None:
            return
        cap.set(_cv2.CAP_PROP_POS_MSEC, 0)
        if has_audio:
            pygame.mixer.music.play()
        play_start = pygame.time.get_ticks()
        last_read_ms = play_start - frame_ms
        playing = True
        not_started = False
        vid_ended = False

    def finish_video():
        nonlocal playing, vid_ended
        playing = False
        vid_ended = True
        if has_audio:
            pygame.mixer.music.stop()

    while True:
        now = pygame.time.get_ticks()

        for event in get_events():
            if event.type == pygame.QUIT:
                if has_audio:
                    pygame.mixer.music.stop()
                if cap is not None:
                    cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if has_audio:
                    pygame.mixer.music.stop()
                if cap is not None:
                    cap.release()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if video_rect.collidepoint(event.pos) and (not_started or vid_ended):
                    start_playback()
                    continue

            if vid_ended:
                if btn_success.handle(event):
                    if cap is not None:
                        cap.release()
                    return True
                if btn_failure.handle(event):
                    if cap is not None:
                        cap.release()
                    return False

        if playing and cap is not None and now - last_read_ms >= frame_ms:
            latest_frm = None
            while now - last_read_ms >= frame_ms:
                ret, frm = cap.read()
                if not ret:
                    finish_video()
                    break
                latest_frm = frm
                last_read_ms += frame_ms
            if latest_frm is not None:
                frame_surf = _make_frame_surface_fit(latest_frm, chal_w, chal_h)

        draw_studio_background(screen)
        draw_corner_decorations(screen)

        hdr_color = category_color or ACCENT_BLUE_LIGHT
        cat_lbl = f"{category_name}  ·  " if category_name else ""
        draw_centered_text(
            screen, f"{cat_lbl}Frage  {idx + 1}  /  {total}", FONT_SMALL, hdr_color, 40
        )
        draw_joker_icons(screen, joker_used)

        if frame_surf:
            frame_rect = frame_surf.get_rect(center=video_rect.center)
            screen.blit(frame_surf, frame_rect)
        else:
            pygame.draw.rect(screen, TEXT_LIGHT, video_rect)
            draw_centered_text_px(
                screen, "Wird geladen …", FONT_SMALL, MUTED_TEXT, video_rect.centery
            )
        pygame.draw.rect(screen, SUCCESS_GREEN, video_rect, 2)

        if not_started:
            veil = pygame.Surface((video_rect.w, video_rect.h), pygame.SRCALPHA)
            veil.fill((0, 0, 0, 100))
            screen.blit(veil, video_rect)
            cx, cy = video_rect.center
            r = 44
            pygame.draw.circle(screen, WHITE, (cx, cy), r)
            pygame.draw.circle(screen, SUCCESS_GREEN_DARK, (cx, cy), r, 3)
            tri = [(cx - 14, cy - 22), (cx - 14, cy + 22), (cx + 22, cy)]
            pygame.draw.polygon(screen, SUCCESS_GREEN_DARK, tri)
            hint = FONT_SUB.render("Klick zum Starten", True, WHITE)
            shade = pygame.Surface(
                (hint.get_width() + 20, hint.get_height() + 10), pygame.SRCALPHA
            )
            shade.fill((0, 0, 0, 160))
            shade_pos = (cx - shade.get_width() // 2, cy + r + 14)
            screen.blit(shade, shade_pos)
            screen.blit(hint, (shade_pos[0] + 10, shade_pos[1] + 5))

        if vid_ended:
            prompt_lines = wrap_text(challenge_text, FONT_Q, WIDTH - scaled(180))
            for i, line in enumerate(prompt_lines):
                draw_centered_text_px(
                    screen,
                    line,
                    FONT_Q,
                    TEXT_LIGHT,
                    prompt_y + i * scaled(34),
                )
            btn_success.draw(screen)
            btn_failure.draw(screen)

        update_display()
        clock.tick(FPS)


def end_screen(score, total):
    btn = Button((WIDTH // 2 - 200, HEIGHT - 130, 400, 68), "Ende", primary=False)

    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if btn.handle(event):
                return

        draw_studio_background(screen)
        draw_string_lights(screen, y_anchor=52, sag=24, bulbs=14)
        draw_corner_decorations(screen)

        draw_centered_text(screen, "Finale!", FONT_TAGLINE, ACCENT_BLUE_LIGHT, 220)
        draw_centered_text(screen, "Happy Birthday, Oma", FONT_TITLE, TEXT_LIGHT, 290)

        draw_show_bar(screen, WIDTH // 2, 340, w=140, h=14)

        draw_centered_text(
            screen, f"Score:  {score}  /  {total}", FONT_Q, ACCENT_BLUE_LIGHT, 400
        )
        draw_centered_text(screen, "Da ist dein Preis!", FONT_SUB, TEXT_LIGHT, 450)

        # decorative studio-light row
        cx = WIDTH // 2
        palette = [
            ANSWER_BLUE,
            ACCENT_BLUE,
            GREEN_ACCENT,
            SUCCESS_GREEN,
            ANSWER_BLUE,
            ACCENT_BLUE,
            GREEN_ACCENT,
        ]
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
                pygame.quit()
                sys.exit()
        draw_studio_background(screen)
        draw_corner_decorations(screen)
        update_display()
        clock.tick(FPS)


def main():
    total_questions = sum(len(c["questions"]) for c in CATEGORIES)
    while True:
        title_screen()
        info_screen()

        score = 0
        joker_used = [False, False, False, False]  # once per full game
        done_cats = set()
        first_question_pending = True

        while len(done_cats) < len(CATEGORIES):
            cat_idx = category_selection_screen(done_cats)
            if cat_idx is None:
                break
            cat = CATEGORIES[cat_idx]
            category_joker_used = (
                [True, True, True, True]
                if cat["name"] == FUN_STUFF_CATEGORY
                else joker_used
            )

            category_intro_screen(cat)

            for qi, q in enumerate(cat["questions"]):
                if first_question_pending:
                    stop_title_music(0)
                    first_question_pending = False
                play_intro_sound()
                kwargs = dict(
                    joker_used=category_joker_used,
                    category_name=cat["name"],
                    category_color=cat["color"],
                )
                qtype = q.get("type")
                if qtype == "ordering":
                    result = ordering_question_screen(
                        qi, q, len(cat["questions"]), **kwargs
                    )
                elif qtype == "audio_text":
                    result = audio_text_question_screen(
                        qi, q, len(cat["questions"]), **kwargs
                    )
                elif qtype == "fun_photo":
                    result = fun_photo_question_screen(
                        qi, q, len(cat["questions"]), **kwargs
                    )
                elif qtype == "sudoku":
                    result = sudoku_question_screen(
                        qi, q, len(cat["questions"]), **kwargs
                    )
                elif qtype == "video":
                    result = video_question_screen(
                        qi, q, len(cat["questions"]), **kwargs
                    )
                elif qtype == "video_challenge":
                    result = video_challenge_screen(
                        qi, q, len(cat["questions"]), **kwargs
                    )
                else:
                    result = question_screen(qi, q, len(cat["questions"]), **kwargs)
                if result:
                    score += 1
                between_questions_pause(1000)

            done_cats.add(cat_idx)

        end_screen(score, total_questions)


if __name__ == "__main__":
    main()
