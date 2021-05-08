import time

import pygame as pg
from random import uniform, choice, randint, random
from settings import *
from main import collide_hit_rect
import pytweening as tween
from itertools import chain, cycle
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    """
    Deals with sprite's collisions with walls.

    :param sprite:
    :param group: walls
    :param dir: which direction is tested
    :return: none
    """
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = "pistol"
        self.weapons_list = ["pistol"]
        self.weapon_iterator = cycle(self.weapons_list)
        self.ammo = {"pistol": PISTOL_AMMO}
        self.damaged = False
        self.visible = True
        self.invisibility_timer = 0

    def get_keys(self):
        """
        Player's actions. Some are also in Game.events().

        :return: none
        """
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED/2, 0).rotate(-self.rot)    # down movement 2 times slower
        if keys[pg.K_SPACE] or keys[pg.K_v]:
            self.shoot()

    def shoot(self):
        """
        Spawns appropriate bullets. Deals with fire rate, spread, kickback of given weapon, sound and visual effects.

        :return: none
        """
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]["rate"]:
            if self.ammo[self.weapon] > 0:
                self.ammo[self.weapon] -= 1
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                self.vel = vec(-WEAPONS[self.weapon]["kickback"], 0).rotate(-self.rot)

                for i in range(WEAPONS[self.weapon]["bullet_count"]):
                    spread = uniform(-WEAPONS[self.weapon]["spread"], WEAPONS[self.weapon]["spread"])
                    Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]["damage"])
                    snd = choice(self.game.weapon_sounds[self.weapon])
                    if snd.get_num_channels() > 2:
                        snd.stop()
                    snd.play()
                MuzzleFlash(self.game, pos)
            else:
                self.last_shot = now
                self.game.effects_sounds["no_ammo"].play()

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 3)

    def update(self):
        """
        Updates player's state: rotation, position, etc.

        :return: none
        """

        # Get input
        self.get_keys()
        ####################################################################
        # Good place to ask for input from the class storing hand commends received from the server
        # print(round(time.time() * 1000))
        # It takes 14-18 milliseconds
        ####################################################################

        # Rotation
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_image, self.rot)

        # Damage
        if self.damaged:
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False

        # Position
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        now = pg.time.get_ticks()

        # Invisibility potion behaviour
        if now - self.invisibility_timer > INVISIBILITY_TIME:
            self.visible = True

    def add_health(self, amount):
        """
        Adds HP to Player's health.

        :param amount: HP
        :return: none
        """
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEED)
        self.target = game.player
        self.wander_target = self.pos
        self.last_update = 0
        self.visited_targets = []

    def avoid_mobs(self):
        """
        Scatters mobs if they are too close to each other.

        :return: none
        """
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update_target(self):
        """
        If Mob does not follow the Player, it looks for a closest target to go to. Targets are points placed on map.

        :return: none
        """
        now = pg.time.get_ticks()
        if (self.wander_target.x - 10 < self.pos.x < self.wander_target.x + 10 and
                self.wander_target.y - 10 < self.pos.y < self.wander_target.y + 10) or \
                now - self.last_update > WANDER_TARGET_CHANGE_FREQ or self.vel == (0, 0):
            self.last_update = now
            closest_wander_target = choice(self.game.targets)

            for target in self.game.targets:
                if target not in self.visited_targets:
                    target_vector = target - self.pos
                    distance = target_vector.x**2 + target_vector.y**2
                    if distance < (closest_wander_target.x**2 + closest_wander_target.y**2):
                        closest_wander_target = target

            self.wander_target = closest_wander_target
            self.visited_targets.append(self.wander_target)
            if len(self.visited_targets) > 20:      # Remembers 20 visited targets
                self.visited_targets.pop(0)

    def move(self, target_dist):
        """
        Deals with Mob's movement: rotation, acceleration, etc.

        :param target_dist: vector
        :return: none
        """
        self.rot = target_dist.angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def update(self):
        """
        Updates Mob's state.

        :return: none
        """
        target_dist = self.target.pos - self.pos

        # Chase the player
        if target_dist.length_squared() < DETECT_RADIUS**2 and self.game.player.visible:     # Better performance without extraction of a root
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.move(target_dist)
        else:
            self.update_target()
            target_dist = self.wander_target - self.pos
            self.move(target_dist)

        # Dead?
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_image.blit(self.game.splat, self.pos - vec(32, 32))

    def draw_health(self):
        """
        Draws health bar above Mob's head.

        :return: none
        """
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.bullet_images[WEAPONS[game.player.weapon]["bullet_size"]]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]["bullet_speed"] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        """
        Updates Bullet's position.

        :return: none
        """
        # Movement
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        # Kill after collision
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()

        # Kill after certain amount of time
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]["bullet_lifetime"]:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        """
        Kills flash after certain amount of time.

        :return: none
        """
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class BloodSplat(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.size = randint(30, 50)
        self.index = choice(['1', '2', '3'])
        self.image = pg.transform.scale(self.game.blood_anim[self.index][0], (self.size, self.size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.last_update = pg.time.get_ticks()
        self.frame = 0

    def update(self):
        """
        Creates animation of blood splat.

        :return: none
        """
        now = pg.time.get_ticks()
        if pg.time.get_ticks() - self.last_update > BLOOD_FRAME_DURATION:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.blood_anim[self.index]):
                self.kill()
            else:
                center = self.rect.center
                self.image = pg.transform.scale(self.game.blood_anim[self.index][self.frame], (self.size, self.size))
                self.rect = self.image.get_rect()
                self.rect.center = center


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.hit_rect = self.rect
        self.tween = tween.easeInOutSine
        self.bob_range = BOB_RANGE
        self.step = 0
        self.dir = 1

    def update(self):
        """
        Deals with Item's bobbing motion.

        :return: none
        """
        offset = BOB_RANGE * (self.tween(self.step/BOB_RANGE)-0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
