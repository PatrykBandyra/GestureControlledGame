import pygame as pg
vec = pg.math.Vector2

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# Game settings
WIDTH = 1024    # 32 * 32
HEIGHT = 768    # 32 * 24
FPS = 60
TITLE = "Tile Game"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

WALL_IMG = "tileGreen_39.png"

# Player settings
PLAYER_SPEED = 300
PLAYER_ROT_SPEED = 250
PLAYER_IMG = "manBlue_gun.png"
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)
PLAYER_HEALTH = 100

# Weapons settings
BULLET_IMG = "bullet.png"
WEAPONS = {}
WEAPONS["pistol"] = {"bullet_speed": 500,
                     "bullet_lifetime": 1000,
                     "rate": 250,
                     "kickback": 200,
                     "spread": 5,
                     "damage": 10,
                     "bullet_size": "lg",
                     "bullet_count": 1}
WEAPONS["shotgun"] = {"bullet_speed": 400,
                      "bullet_lifetime": 500,
                      "rate": 900,
                      "kickback": 300,
                      "spread": 20,
                      "damage": 5,
                      "bullet_size": "sm",
                      "bullet_count": 12}

# Mob settings
MOB_IMG = "zombie1_hold.png"
MOB_SPEED = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 600
WANDER_TARGET_CHANGE_FREQ = 15000
WANDER_RING_DISTANCE = 150
WANDER_RING_RADIUS = 50

# Effects
MUZZLE_FLASHES = ["whitePuff15.png", "whitePuff16.png", "whitePuff17.png", "whitePuff18.png"]
FLASH_DURATION = 40
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]
LIGHT_MASK = "light_350_med.png"
NIGHT_COLOR = (30, 30, 30)
LIGHT_RADIUS = (600, 600)
# Blood
SPLAT = "splat_red.png"
BLOOD_ANIM = {'1': ["bloodsplats_0001.png", "bloodsplats_0002.png", "bloodsplats_0003.png", "bloodsplats_0004.png",
                    "bloodsplats_0005.png", "bloodsplats_0006.png", "bloodsplats_0007.png", "bloodsplats_0008.png",
                    "bloodsplats_0009.png", "bloodsplats_0010.png", "bloodsplats_0011.png", "bloodsplats_0012.png",
                    "bloodsplats_0013.png", "bloodsplats_0014.png", "bloodsplats_0015.png", "bloodsplats_0016.png"],
              '2': ["bloodsplats_0018.png", "bloodsplats_0019.png", "bloodsplats_0020.png", "bloodsplats_0021.png",
                    "bloodsplats_0022.png", "bloodsplats_0023.png", "bloodsplats_0024.png", "bloodsplats_0025.png",
                    "bloodsplats_0025.png", "bloodsplats_0026.png", "bloodsplats_0027.png", "bloodsplats_0028.png",
                    "bloodsplats_0029.png", "bloodsplats_0030.png"],
              '3': ["bloodsplats_0032.png", "bloodsplats_0033.png", "bloodsplats_0034.png", "bloodsplats_0035.png",
                    "bloodsplats_0036.png", "bloodsplats_0037.png", "bloodsplats_0038.png", "bloodsplats_0039.png",
                    "bloodsplats_0040.png", "bloodsplats_0041.png", "bloodsplats_0042.png", "bloodsplats_0043.png",
                    "bloodsplats_0044.png", "bloodsplats_0045.png", "bloodsplats_0046.png"]}
BLOOD_FRAME_DURATION = 10

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Items
ITEMS_IMAGES = {"health": "health_pack.png",
                "shotgun": "obj_shotgun.png",
                "shotgun_ammo": "shotgun_ammo.png",
                "pistol_ammo": "pistol_ammo.png",
                "mask_potion": "mask_potion.png"}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 15
BOB_SPEED = 0.4
INVISIBILITY_TIME = 10000
# Weapons
PISTOL_AMMO = 30
PISTOL_AMMO_BOX = 40
SHOTGUN_AMMO = 20
SHOTGUN_AMMO_BOX = 10

# Sounds
BG_MUSIC = "espionage.ogg"
PLAYER_HIT_SOUNDS = ["pain/8.wav", "pain/9.wav", "pain/10.wav", "pain/11.wav"]
ZOMBIE_MOAN_SOUNDS = ["brains2.wav", "brains3.wav", "zombie-roar-1.wav", "zombie-roar-2.wav", "zombie-roar-3.wav",
                      "zombie-roar-5.wav", "zombie-roar-6.wav", "zombie-roar-7.wav"]
ZOMBIE_HIT_SOUNDS = ["splat-15.wav"]
WEAPON_SOUNDS = {"pistol": ["pistol.wav"],
                 "shotgun": ["shotgun.wav"]
                 }
EFFECTS_SOUNDS = {"level_start": "level_start.wav",
                  "health_up": "health_pack.wav",
                  "gun_pickup": "gun_pickup.wav",
                  "weapon_change": "weapon_change.wav",
                  "potion": "potion.wav",
                  "no_ammo": "no_ammo.wav",
                  "ammo_pickup": "ammo_pickup.wav"}
