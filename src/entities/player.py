import pygame
import math

from settings import *

from src.core.spritesheet import SpriteSheet
from src.core.animation import Animation


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x,
            y,
            40,
            40
        )

        self.score = 0

        self.attack_damage = 25

        self.max_stamina = 100
        self.stamina = 100

        self.stamina_recovery = 25
        self.dash_cost = 30

        self.sprite_offset_y = 125

        self.velocity_y = 0

        self.speed = 6

        self.max_health = 100
        self.health = 100

        self.dead = False

        self.direction = 1

        self.state = "idle"

        self.invulnerable = False
        self.invulnerability_timer = 0

        self.combo_multiplier = 1
        self.combo_decay = 0

        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 0.15
        self.dash_speed = 18

        self.attack_timer = 0

        self.animations = {}

        self.load_animations()

        self.current_animation = self.animations["idle"]
      

    def death_animation_finished(self):

        return (
            self.dead
            and
            self.current_animation == self.animations["death"]
            and
            self.current_animation.finished
        )


    def get_attack_hitbox(self):

        if self.direction == 1:

            return pygame.Rect(
                self.rect.right,
                self.rect.y,
                80,
                self.rect.height
            )

        return pygame.Rect(
            self.rect.left - 80,
            self.rect.y,
            80,
            self.rect.height
        )

    def load_animations(self):

        self.animations["idle"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_idle.png"
            ).get_frames(144, 144),
            0.12
        )

        self.animations["run"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_run.png"
            ).get_frames(144, 144),
            0.08
        )

        self.animations["jump"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_jump.png"
            ).get_frames(144, 144),
            0.12
        )

        self.animations["fall"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_fall.png"
            ).get_frames(144, 144),
            0.12
        )

        self.animations["dash"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_dash.png"
            ).get_frames(144, 144),
            0.06,
            False
        )

        self.animations["attack1"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_attack.png"
            ).get_frames(144, 144),
            0.06,
            False
        )

        self.animations["attack2"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_attack2.png"
            ).get_frames(144, 144),
            0.06,
            False
        )

        self.animations["hurt"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_hurt.png"
            ).get_frames(144, 144),
            0.08,
            False
        )

        self.animations["death"] = Animation(
            SpriteSheet(
                "assets/sprites/player/platform_death.png"
            ).get_frames(144, 144),
            0.12,
            False
        )

    def take_damage(self, amount):

        if self.invulnerable or self.dead:
            return

        self.health -= amount

        self.state = "hurt"


        self.current_animation = self.animations["hurt"]

        self.current_animation.reset()

        self.invulnerable = True
        self.invulnerability_timer = 1

        self.combo_multiplier = 1

        if self.health <= 0:
            self.dead = True
            self.state = "death"

    def update(
        self,
        dt,
        world_manager,
        platforms,
        obstacles
    ):

        if self.state in [
            "attack1",
            "attack2",
            "dash",
            "hurt"
        ]:

            self.current_animation.update(dt)

            if self.current_animation.finished:
                self.state = "idle"
                self.current_animation = self.animations["idle"]
            else:
                return

        if self.current_animation.finished:
            self.state = "idle"

        if self.dead:
            self.current_animation = self.animations["death"]
            self.current_animation.update(dt)
            return

        self.stamina += self.stamina_recovery * dt

        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina

        keys = pygame.key.get_pressed()

        self.attack_timer -= dt

        if self.invulnerable:
            self.invulnerability_timer -= dt

            if self.invulnerability_timer <= 0:
                self.invulnerable = False

        if self.combo_decay > 0:
            self.combo_decay -= dt
        else:
            self.combo_multiplier = 1

        if world_manager.current_world == world_manager.PLATFORMER:
            self.platformer_update(
                dt,
                keys,
                platforms
            )
        else:
            self.shooter_update(keys, obstacles)

        self.current_animation.update(dt)

    def shooter_update(self, keys, obstacles):

        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx -= self.speed
            self.direction = -1

        if keys[pygame.K_d]:
            dx += self.speed
            self.direction = 1

        if keys[pygame.K_w]:
            dy -= self.speed

        if keys[pygame.K_s]:
            dy += self.speed

        # ---- collision-safe movement (X) ----
        self.rect.x += dx

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if dx > 0:
                    self.rect.right = obstacle.rect.left
                elif dx < 0:
                    self.rect.left = obstacle.rect.right

        # ---- collision-safe movement (Y) ----
        self.rect.y += dy

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if dy > 0:
                    self.rect.bottom = obstacle.rect.top
                elif dy < 0:
                    self.rect.top = obstacle.rect.bottom

        # animation
        if dx != 0 or dy != 0:
            self.current_animation = self.animations["run"]
        else:
            self.current_animation = self.animations["idle"]

    def platformer_update(
        self,
        dt,
        keys,
        platforms
    ):

        moving = False

        if not self.dashing:

            if keys[pygame.K_a]:
                self.rect.x -= self.speed
                self.direction = -1
                moving = True

            if keys[pygame.K_d]:
                self.rect.x += self.speed
                self.direction = 1
                moving = True

        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.dashing and self.stamina >= self.dash_cost:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.state = "dash"
            self.stamina -= self.dash_cost

        if self.dashing:

            self.dash_timer -= dt

            self.rect.x += (
                self.direction *
                self.dash_speed
            )

            self.current_animation = self.animations["dash"]

            if self.dash_timer <= 0:
                self.dashing = False

        # =========================
        # VERTICAL MOVEMENT
        # =========================

        old_bottom = self.rect.bottom
        old_top = self.rect.top

        self.velocity_y += GRAVITY

        self.rect.y += self.velocity_y

        # =========================
        # COLLISION RESOLUTION
        # =========================

        for platform in platforms:

            if self.rect.colliderect(platform.rect):

                # Landing on platform

                if (
                    self.velocity_y >= 0
                    and old_bottom <= platform.rect.top
                ):

                    self.rect.bottom = platform.rect.top

                    self.velocity_y = 0

                # Hitting platform from below

                elif (
                    self.velocity_y < 0
                    and old_top >= platform.rect.bottom
                ):

                    self.rect.top = platform.rect.bottom

                    self.velocity_y = 0

        # =========================
        # GROUND CHECK
        # =========================

        grounded = False

        feet_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.bottom - 2,
            self.rect.width - 10,
            6
        )

        for platform in platforms:

            if feet_rect.colliderect(platform.rect):

                grounded = True
                break

        self.grounded = grounded

        if grounded:

            print(self.state)

            if moving:

                if self.state != "run":
                    self.state = "run"
                    self.current_animation = self.animations["run"]
                    self.current_animation.reset()

            else:

                if self.state != "idle":
                    self.state = "idle"
                    self.current_animation = self.animations["idle"]
                    self.current_animation.reset()

            if keys[pygame.K_SPACE]:
                self.velocity_y = PLAYER_JUMP

        else:

            if self.velocity_y < 0:
                self.state = "jump"
                self.current_animation = self.animations["jump"]

            else:
                self.state = "fall"
                self.current_animation = self.animations["fall"]


        print("grounded: ", grounded)

        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pressed[0] and self.attack_timer <= 0:

            self.state = "attack1"

            self.current_animation = self.animations["attack1"]

            self.current_animation.reset()

            self.attack_timer = 0.4

        elif mouse_pressed[2] and self.attack_timer <= 0:

            self.state = "attack2"

            self.current_animation = self.animations["attack2"]

            self.current_animation.reset()

            self.attack_timer = 0.5

        self.rect.clamp_ip(
            pygame.Rect(
                0,
                0,
                WIDTH,
                HEIGHT
            )
        )

    def render(self, screen):

        frame = self.current_animation.get_frame()

        if self.direction == -1:

            frame = pygame.transform.flip(
                frame,
                True,
                False
            )

        SPRITE_SIZE = 288

        scaled = pygame.transform.scale(
            frame,
            (
                SPRITE_SIZE,
                SPRITE_SIZE
            )
        )

        draw_x = (
            self.rect.centerx
            - SPRITE_SIZE // 2
        )

        draw_y = (
            self.rect.bottom
            - SPRITE_SIZE
            + self.sprite_offset_y
        )

        screen.blit(
            scaled,
            (draw_x, draw_y)
        )

        pygame.draw.rect(
            screen,
            (0, 255, 0),
            self.rect,
            2
        )

        # Background
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (
                20,
                20,
                300,
                20
            )
        )

        # Health
        pygame.draw.rect(
            screen,
            (50, 255, 50),
            (
                20,
                20,
                300 * (self.health / self.max_health),
                20
            )
        )

        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (
                20,
                50,
                300,
                15
            )
        )

        pygame.draw.rect(
            screen,
            (50, 150, 255),
            (
                20,
                50,
                300 * (self.stamina / self.max_stamina),
                15
            )
        )