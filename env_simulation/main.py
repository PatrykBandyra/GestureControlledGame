import pygame as pg
import sys
from settings import *
from sprites import *
from os import path, environ
from tilemap import *
from threading import Thread


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


# Hud functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = int(pct * BAR_LENGTH)
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game:
    def __init__(self):
        environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (275, 40)
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.load_data()
        self.targets = []
        # self.path = {}
        # self.last_path_update = 0

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, "img")
        snd_folder = path.join(game_folder, "snd")
        music_folder = path.join(game_folder, "music")
        m_flash_folder = path.join(img_folder, "muzzle_flashes")
        blood_folder = path.join(img_folder, "blood_splats")
        self.map_folder = path.join(game_folder, "maps")
        self.title_font = path.join(img_folder, "ZOMBIE.TTF")
        self.hud_font = path.join(img_folder, "Impacted2.0.ttf")
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))    # the 4 value is alpha channel - closer to 255 -> darker
        self.player_image = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images["lg"] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images["sm"] = pg.transform.scale(self.bullet_images["lg"], (10, 10))
        self.mob_image = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_image = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_image = pg.transform.scale(self.wall_image, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.gun_flashes = [pg.image.load(path.join(m_flash_folder, img)).convert_alpha() for img in MUZZLE_FLASHES]
        self.blood_anim = {str(i): []
                           for i in range(1, (len(BLOOD_ANIM)+1))
                           }
        for i in range(1, len(BLOOD_ANIM)+1):
            for filename in BLOOD_ANIM[str(i)]:
                self.blood_anim[str(i)].append(pg.image.load(path.join(path.join(blood_folder, str(i)), filename)).convert_alpha())
        self.item_images = {item: pg.image.load(path.join(img_folder, ITEMS_IMAGES[item])).convert_alpha()
                            for item in ITEMS_IMAGES}
        # Light effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()
        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {type: pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
                        for type in EFFECTS_SOUNDS
                        }
        self.weapon_sounds = {}
        self.weapon_sounds["gun"] = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        self.zombie_hit_sounds = [pg.mixer.Sound(path.join(snd_folder, snd))
                                  for snd in ZOMBIE_HIT_SOUNDS
                                  ]
        self.player_hit_sounds = [pg.mixer.Sound(path.join(snd_folder, snd))
                                  for snd in PLAYER_HIT_SOUNDS
                                  ]

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()   # just like Group(), but has layer property - draws in order
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        # Load fresh map (without blood splats)
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map_image = self.map.make_map()
        self.map_rect = self.map_image.get_rect()
        ############################################
        # self.squared_grid = SquareGrid(self.map_rect.width, self.map_rect.height)
        ############################################
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x+tile_object.width/2, tile_object.y+tile_object.height/2)
            if tile_object.name == "player":
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == "target":
                self.targets.append(vec(tile_object.x, tile_object.y))
            if tile_object.name == "zombie":
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                ############################################################
                # self.squared_grid.walls.append((tile_object.x, tile_object.y, tile_object.width, tile_object.height))
                ############################################################
            if tile_object.name in ITEMS_IMAGES.keys():
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.effects_sounds["level_start"].set_volume(0.4)
        self.effects_sounds["level_start"].play()

    def run(self):
        # Game loop
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def threaded_bfs(self):
        self.path = breadth_first_search(self.squared_grid, calculate_closest_tile_center(self.player.pos))
        print(len(self.path))

    def update(self):
        # Game loop - update
        self.all_sprites.update()
        self.camera.update(self.player)
        # Game over ?
        if len(self.mobs) == 0:
            self.playing = False
        # Player hits item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == "health" and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds["health_up"].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == "shotgun":
                hit.kill()
                self.effects_sounds["gun_pickup"].play()
                self.player.weapon = "shotgun"
                self.player.weapons_list.append(self.player.weapon)
                self.player.ammo[self.player.weapon] = SHOTGUN_AMMO
            if hit.type == "pistol_ammo":
                if "pistol" in self.player.ammo.keys():
                    hit.kill()
                    self.effects_sounds["ammo_pickup"].play()
                    self.player.ammo["pistol"] += PISTOL_AMMO_BOX
            if hit.type == "shotgun_ammo":
                if "shotgun" in self.player.ammo.keys():
                    hit.kill()
                    self.effects_sounds["ammo_pickup"].play()
                    self.player.ammo["shotgun"] += SHOTGUN_AMMO_BOX
            if hit.type == "mask_potion":
                hit.kill()
                self.effects_sounds["potion"].play()
                self.player.visible = False
                self.player.invisibility_timer = pg.time.get_ticks()
        # Mob hits player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
            if hits:
                self.player.hit()
                self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # Bullet hits mob
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            BloodSplat(self, mob.pos)
            # hit.health -= WEAPONS[self.player.weapon]["damage"] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # Draw light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        pg.display.set_caption(f"{round(self.clock.get_fps(), 2)}")
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_image, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                if not isinstance(sprite, (MuzzleFlash, BloodSplat)):
                    pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
        if self.night:
            self.render_fog()
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health/PLAYER_HEALTH)
        self.draw_text(f"Zombies: {len(self.mobs)}", self.hud_font, 30, WHITE, WIDTH-10, 10, "ne")
        self.draw_text(f"{self.player.weapon}: {self.player.ammo[self.player.weapon]}", self.hud_font, 20, WHITE, 10, self.player.health/PLAYER_HEALTH+30)
        if not self.player.visible:
            self.draw_text(f"Masking potion: {(INVISIBILITY_TIME - (pg.time.get_ticks() - self.player.invisibility_timer))//1000} s", self.hud_font, 25, RED, WIDTH//2-150, 20, "nw")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH//2, HEIGHT//2, "center")
        pg.display.flip()

    def events(self):
        # Game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night
            # Weapon change
            if event.type == pg.KEYUP:
                if event.key == pg.K_c:
                    if len(self.player.weapons_list) > 1:
                        self.effects_sounds["weapon_change"].play()
                        self.player.weapon = next(self.player.weapon_iterator)

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH // 2, HEIGHT // 2, "center")
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH//2, HEIGHT//2, "center")
        self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH//2, HEIGHT*3/4, "center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()     # Start new event queue
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

    def main_menu(self):
        in_menu = True
        click = False
        while in_menu:
            self.screen.fill(BLACK)
            self.draw_text("Zombie Shooter", self.title_font, 70, RED, WIDTH//2, HEIGHT//4, "center")
            mx, my = pg.mouse.get_pos()
            play_button = pg.Rect(WIDTH//2-100, HEIGHT*3/4, 200, 50)
            pg.draw.rect(self.screen, RED, play_button)
            font = pg.font.Font(self.title_font, 26)
            text_surface = font.render("PLAY", True, WHITE)
            text_rect = text_surface.get_rect()
            text_rect.center = play_button.center
            self.screen.blit(text_surface, text_rect)

            if play_button.collidepoint((mx, my)):
                if click:
                    in_menu = False
            click = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True

            pg.display.flip()
            self.clock.tick(FPS)


def main():
    g = Game()
    g.main_menu()
    g.show_start_screen()
    while True:
        g.new()
        g.run()
        g.show_go_screen()


if __name__ == '__main__':
    main()

