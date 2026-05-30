import pygame
import math

from settings import *

from src.core.spritesheet import SpriteSheet
from src.core.animation import Animation

from src.entities.enemy_projectile import EnemyProjectile


class Enemy:

    FRAMES = {
        "idle": (96, 96),
        "run": (96, 96),
        "attack": (96, 96),
        "shoot": (96, 96),
        "hurt": (96, 96),
        "death": (96, 96)
    }

    SPRITE_FOLDER = "basic"

    FRAME_SIZE = 96

    SPRITE_SIZE = 180

    SPRITE_OFFSET_Y = 60

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            x,
            y,
            40,
            40
        )

        self.velocity_y = 0

        self.health = 50
        self.max_health = 50

        self.speed = 3

        self.damage = 10

        self.attack_range = 70

        self.attack_cooldown = 0

        self.knockback_velocity = 0

        self.dead = False
        self.dying = False

        self.direction = 1

        self.state = "idle"

        self.animations = {}

        self.load_animations()

        self.current_animation = self.animations["idle"]

    def load_animation(
        self,
        name,
        speed,
        loop=True
    ):

        width, height = self.FRAMES.get(
            name,
            (96, 96)
        )

        return Animation(
            SpriteSheet(
                f"assets/sprites/enemies/{self.SPRITE_FOLDER}/{name}.png"
            ).get_frames(
                width,
                height
            ),
            speed,
            loop
        )

    def load_animations(self):

        try:

            self.animations["idle"] = self.load_animation(
                "idle",
                0.12
            )

            self.animations["run"] = self.load_animation(
                "run",
                0.08
            )

            self.animations["attack"] = self.load_animation(
                "attack",
                0.08,
                False
            )

            self.animations["hurt"] = self.load_animation(
                "hurt",
                0.08,
                False
            )

            self.animations["death"] = self.load_animation(
                "death",
                0.12,
                False
            )

        except Exception as e:

            print("Enemy animation error:", e)

            dummy = pygame.Surface(
                (
                    self.SPRITE_SIZE,
                    self.SPRITE_SIZE
                )
            )

            dummy.fill((255, 80, 80))

            for state in [
                "idle",
                "run",
                "attack",
                "hurt",
                "death"
            ]:

                self.animations[state] = Animation(
                    [dummy],
                    1
                )

    def take_damage(
        self,
        damage,
        direction
    ):

        if self.dead:
            return

        self.health -= damage

        self.knockback_velocity = (
            direction * 10
        )

        self.state = "hurt"

        self.current_animation = (
            self.animations["hurt"]
        )

        self.current_animation.reset()

        if self.health <= 0:

            self.dying = True

            self.state = "death"

            self.current_animation = (
                self.animations["death"]
            )

            self.current_animation.reset()

    def update_platform_physics(
        self,
        platforms
    ):

        self.velocity_y += GRAVITY

        self.rect.y += self.velocity_y

        for platform in platforms:

            if self.rect.colliderect(
                platform.rect
            ):

                if self.velocity_y > 0:

                    self.rect.bottom = (
                        platform.rect.top
                    )

                    self.velocity_y = 0

    def update(
        self,
        dt,
        player,
        world_manager,
        platforms,
        obstacles
    ):

        if self.dying:
            self.current_animation.update(dt)

            if self.current_animation.finished:
                self.dead = True  # NOW we remove it
            return

        if self.dead:
            return

        if self.state in [
            "hurt",
            "attack"
        ] and not self.dying:

            self.current_animation.update(dt)

            if not self.current_animation.finished:
                return

            self.state = "idle"

        self.attack_cooldown -= dt

        self.rect.x += (
            self.knockback_velocity
        )

        self.knockback_velocity *= 0.85

        dx = (
            player.rect.centerx -
            self.rect.centerx
        )

        dy = (
            player.rect.centery -
            self.rect.centery
        )

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        self.direction = (
            1 if dx > 0 else -1
        )

        if distance <= self.attack_range:

            if self.attack_cooldown <= 0:

                self.state = "attack"

                self.current_animation = (
                    self.animations["attack"]
                )

                self.current_animation.reset()

                player.take_damage(
                    self.damage
                )

                self.attack_cooldown = 1.5

        else:

            if (
                world_manager.current_world
                ==
                world_manager.SHOOTER
            ):

                # --- shooter movement with obstacle collision ---
                move_x = 0
                move_y = 0

                if distance != 0:
                    move_x = (dx / distance) * self.speed
                    move_y = (dy / distance) * self.speed

                # try X movement
                test_rect = self.rect.copy()
                test_rect.x += move_x

                blocked = False
                for obstacle in obstacles:
                    if test_rect.colliderect(obstacle.rect):
                        blocked = True
                        break

                if not blocked:
                    self.rect.x += move_x

                # try Y movement
                test_rect = self.rect.copy()
                test_rect.y += move_y

                blocked = False
                for obstacle in obstacles:
                    if test_rect.colliderect(obstacle.rect):
                        blocked = True
                        break

                if not blocked:
                    self.rect.y += move_y

                self.state = "run"
                self.current_animation = self.animations["run"]

            else:

                if dx > 0:
                    self.rect.x += self.speed
                else:
                    self.rect.x -= self.speed
            if self.state != "run":

                self.state = "run"

                self.current_animation = (
                    self.animations["run"]
                )

        if (
            world_manager.current_world
            ==
            world_manager.PLATFORMER
        ):

            self.update_platform_physics(
                platforms
            )

            if self.dying:
                return

        self.current_animation.update(dt)

    def render(
        self,
        screen,
        world_manager
    ):

        frame = (
            self.current_animation.get_frame()
        )

        if self.direction < 0:

            frame = pygame.transform.flip(
                frame,
                True,
                False
            )

        scaled = pygame.transform.scale(
            frame,
            (
                self.SPRITE_SIZE,
                self.SPRITE_SIZE
            )
        )

        draw_x = (
            self.rect.centerx
            -
            self.SPRITE_SIZE // 2
        )

        draw_y = (
            self.rect.bottom
            -
            self.SPRITE_SIZE
            +
            self.SPRITE_OFFSET_Y
        )

        screen.blit(
            scaled,
            (
                draw_x,
                draw_y
            )
        )

        pygame.draw.rect(
            screen,
            (255, 0, 0),
            self.rect,
            2
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (
                self.rect.x,
                self.rect.y - 10,
                self.rect.width,
                6
            )
        )

        pygame.draw.rect(
            screen,
            (255, 60, 60),
            (
                self.rect.x,
                self.rect.y - 10,
                self.rect.width *
                (
                    self.health /
                    self.max_health
                ),
                6
            )
        )


class TankEnemy(Enemy):

    FRAMES = {
        "idle": (36, 28),
        "run": (47, 28),
        "attack": (64, 35),
        "hurt": (36, 28),
        "death": (36, 28)
    }

    SPRITE_FOLDER = "tank"

    FRAME_SIZE = 64

    SPRITE_SIZE = 180

    SPRITE_OFFSET_Y = 0

    def __init__(self, x, y):

        super().__init__(x, y)

        self.rect.width = 80
        self.rect.height = 60

        self.health = 150
        self.max_health = 150

        self.damage = 20

        self.speed = 1.5


class ShooterEnemy(Enemy):

    SPRITE_FOLDER = "shooter"

    FRAMES = {
        "idle": (48, 48),
        "run": (48, 48),
        "attack": (48, 48),
        "shoot": (48, 48),
        "hurt": (48, 48),
        "death": (48, 48)
    }

    SPRITE_SIZE = 180

    SPRITE_OFFSET_Y = 60

    def __init__(self, x, y):

        super().__init__(x, y)

        self.projectiles = []

        self.shoot_timer = 0

        self.shoot_cooldown = 2

        self.damage = 15

        self.attack_range = 600

    def load_animations(self):

        super().load_animations()

        try:

            self.animations["shoot"] = (
                self.load_animation(
                    "shoot",
                    0.08,
                    False
                )
            )

        except Exception:

            self.animations["shoot"] = (
                self.animations["attack"]
            )

    def update(
        self,
        dt,
        player,
        world_manager,
        platforms,
        obstacles
    ):

        if self.dead:
            return

        self.shoot_timer -= dt

        dx = (
            player.rect.centerx
            - self.rect.centerx
        )

        dy = (
            player.rect.centery
            - self.rect.centery
        )

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        self.direction = (
            1 if dx > 0 else -1
        )

        # Shoot

        if (
            distance <= self.attack_range
            and
            self.shoot_timer <= 0
        ):

            angle = math.atan2(
                dy,
                dx
            )

            self.projectiles.append(
                EnemyProjectile(
                    self.rect.centerx,
                    self.rect.centery,
                    angle,
                    self.damage
                )
            )

            self.state = "shoot"

            self.current_animation = (
                self.animations["shoot"]
            )

            self.current_animation.reset()

            self.shoot_timer = (
                self.shoot_cooldown
            )

        # Return to idle after shooting animation

        if self.state == "shoot":

            self.current_animation.update(dt)

            if self.current_animation.finished:

                self.state = "idle"

                self.current_animation = (
                    self.animations["idle"]
                )

        else:

            self.current_animation.update(dt)

        # Platform physics

        if (
            world_manager.current_world
            ==
            world_manager.PLATFORMER
        ):

            self.update_platform_physics(
                platforms
            )

        # Update projectiles

        for projectile in self.projectiles:

            projectile.update()

            if (
                projectile.rect.colliderect(
                    player.rect
                )
                and
                not projectile.dead
            ):

                player.take_damage(
                    projectile.damage
                )

                projectile.dead = True

        self.projectiles = [
            p for p in self.projectiles
            if not p.dead
        ]

    def render(
        self,
        screen,
        world_manager
    ):

        super().render(
            screen,
            world_manager
        )

        for projectile in self.projectiles:

            projectile.render(
                screen
            )