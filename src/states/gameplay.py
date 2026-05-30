import pygame
import random
import math

from settings import *

from src.core.state_machine import State

from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.enemy import ShooterEnemy
from src.entities.enemy import TankEnemy
from src.entities.platform import Platform
from src.entities.obstacle import Obstacle
from src.entities.projectile import Projectile

from src.worlds.world_manager import WorldManager

from src.systems.hitstop import Hitstop
from src.systems.screenshake import ScreenShake
from src.systems.instability import Instability


class GameplayState(State):

    def __init__(self, game):
        super().__init__(game)

        self.wave_config = {
            1: {"basic": 5},
            2: {"basic": 8},
            3: {"basic": 6, "shooter": 3},
            4: {"basic": 10, "shooter": 4},
            5: {"basic": 8, "shooter": 5, "tank": 2},
        }

        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.3  # start small like 1.2–1.5

        self.wave_started = False

        self.wave_remaining_spawns = {}

        self.show_tutorial_message = True

        self.wave_active_timer = 0

        self.wave = 0
        self.wave_state = "countdown"
        self.wave_timer = 1.0
        self.wave_countdown = 3
        self.wave_transitioning = False

        self.player = Player(500, 300)

        self.world_manager = WorldManager()

        self.hitstop = Hitstop()

        self.screenshake = ScreenShake()

        self.instability = Instability()

        self.projectiles = []

        self.enemies = []

        self.platforms = []

        self.obstacles = []

        self.obstacle_sprite = pygame.image.load(
            "assets/sprites/obstacles/wall.png"
        ).convert_alpha()

        self.score = 0

        self.spawn_timer = 0

        self.font = pygame.font.SysFont(
            "consolas",
            30
        )

        self.generate_world()

    def generate_world(self):

        self.platforms.clear()
        self.obstacles.clear()

        for i in range(8):

            self.platforms.append(
                Platform(
                    random.randint(0, WIDTH - 200),
                    random.randint(150, HEIGHT - 100),
                    random.randint(120, 240),
                    30
                )
            )

            self.platforms.append(
                Platform(
                    0,
                    HEIGHT - 40,
                    WIDTH,
                    40
                )
            )

        for i in range(10):

            self.obstacles.append(
                Obstacle(
                    random.randint(0, WIDTH - 100),
                    random.randint(0, HEIGHT - 100),
                    80,
                    80,
                    self.obstacle_sprite
                )
            )

    def spawn_enemy(self):

        if self.wave_state != "active":
            return

        available_types = []

        if self.wave_remaining_spawns.get("basic", 0) > 0:
            available_types.append(("basic", Enemy))

        if self.wave_remaining_spawns.get("shooter", 0) > 0:
            available_types.append(("shooter", ShooterEnemy))

        if self.wave_remaining_spawns.get("tank", 0) > 0:
            available_types.append(("tank", TankEnemy))

        if not available_types:
            return

        enemy_key, enemy_class = random.choice(available_types)

        # find position (keep your safe spawn logic)
        for _ in range(50):
            x = random.randint(0, WIDTH - 40)
            y = random.randint(0, HEIGHT - 40)

            candidate = pygame.Rect(x, y, 40, 40)

            if candidate.colliderect(self.player.rect.inflate(200, 200)):
                continue

            if any(candidate.colliderect(o.rect) for o in (self.obstacles + self.platforms)):
                continue

            self.enemies.append(enemy_class(x, y))

            self.wave_remaining_spawns[enemy_key] -= 1
            return

    def handle_events(self, events):

        for event in events:
            

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from src.states.pause import PauseState
                    self.game.state_machine.change_state(
                        PauseState(self.game, self)
                    )

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_TAB:

                    self.world_manager.swap_world()

                    self.generate_world()

                    self.screenshake.trigger(15)

            if event.type == pygame.MOUSEBUTTONDOWN:

                if (
                    event.button == 1 and
                    self.world_manager.current_world ==
                    self.world_manager.SHOOTER
                ):

                    mouse_pos = pygame.mouse.get_pos()

                    dx = (
                        mouse_pos[0] -
                        self.player.rect.centerx
                    )

                    dy = (
                        mouse_pos[1] -
                        self.player.rect.centery
                    )

                    angle = math.atan2(dy, dx)

                    self.projectiles.append(
                        Projectile(
                            self.player.rect.centerx,
                            self.player.rect.centery,
                            angle
                        )
                    )

    def start_wave(self):
        self.wave_state = "countdown"
        self.wave_countdown = 3
        self.wave_timer = 1.0
        self.spawn_timer = float("inf")

        self.enemies.clear()
        self.wave_transitioning = False
        self.wave_active_timer = 0

        self.wave_remaining_spawns = self.wave_config.get(self.wave, {"basic": 5}).copy()

        self.wave_started = False


    def apply_camera(self, pos):
        x, y = pos
        return (
            (x - self.camera_x) * self.camera_zoom,
            (y - self.camera_y) * self.camera_zoom
        )

    def update(self, dt):

        self.world_manager.update(dt)

        if self.hitstop.update(dt):
            return

        self.instability.update(dt)

        if self.wave_state == "countdown":

            self.spawn_timer = 999999  # hard freeze

            self.wave_timer -= dt

            if self.wave_timer <= 0:
                self.wave_timer = 1
                self.wave_countdown -= 1

                if self.wave_countdown <= 0:
                    self.wave_state = "active"
                    self.show_tutorial_message = False
                    self.spawn_timer = 1.0

                    self.wave_transitioning = False
                    self.wave_active_timer = 0

                    self.wave_started = True


        if self.wave_state == "active":
            self.wave_active_timer += dt
            self.spawn_timer -= dt

            if self.spawn_timer <= 0:

                if len(self.enemies) < min(8, sum(self.wave_remaining_spawns.values())):
                    self.spawn_enemy()

                self.spawn_timer = max(
                    1.5,
                    4 - self.instability.level * 0.01
                )

        self.player.update(
            dt,
            self.world_manager,
            self.platforms,
            self.obstacles
        )

        target_x = self.player.rect.centerx - WIDTH // 2
        target_y = self.player.rect.centery - HEIGHT // 2

        # smooth follow
        self.camera_x += (target_x - self.camera_x) * 0.08
        self.camera_y += (target_y - self.camera_y) * 0.08

        if self.player.state in [
            "attack1",
            "attack2"
        ]:

            attack_box = self.player.get_attack_hitbox()

            for enemy in self.enemies:

                if attack_box.colliderect(enemy.rect):

                    enemy.take_damage(
                        self.player.attack_damage,
                        self.player.direction
                    )

                    if enemy.health <= 0 and not enemy.score_given:
                        enemy.score_given = True

                        self.score += 100 * self.player.combo_multiplier
                        self.player.score += 100 * self.player.combo_multiplier

                        self.player.combo_multiplier += 1
                        self.player.combo_decay = 3

        for platform in self.platforms:
            platform.update()

        for projectile in self.projectiles:
            projectile.update()

        for enemy in self.enemies:
            enemy.update(
                dt,
                self.player,
                self.world_manager,
                self.platforms,
                self.obstacles
            )            

        for projectile in self.projectiles:

            for enemy in self.enemies:

                if (
                    projectile.rect.colliderect(enemy.rect)
                    and not enemy.dead
                ):

                    enemy.take_damage(
                        self.player.attack_damage,
                        self.player.direction
                    )

                    projectile.dead = True

                    self.hitstop.trigger(0.05)

                    self.screenshake.trigger(6)

                    if enemy.health <= 0:

                        enemy.dead = True

                        self.score += (
                            100 *
                            self.player.combo_multiplier
                        )

                        self.player.score += (
                            100 *
                            self.player.combo_multiplier
                        )

                        self.player.combo_multiplier += 1

                        self.player.combo_decay = 3

        self.projectiles = [
            p for p in self.projectiles
            if not p.dead
        ]

        self.enemies = [
            e for e in self.enemies
            if not (
                e.dead
                and
                e.current_animation.finished
            )
        ]

        for e in self.enemies:
            print(e.dead, e.current_animation.finished)

        if self.player.death_animation_finished():

            from src.states.death import DeathState

            self.game.state_machine.change_state(
                DeathState(self.game)
            )

            return

        if (
            self.wave_state == "active"
            and self.wave_started
            and self.wave_active_timer > 1.0
            and len(self.enemies) == 0
            and all(v <= 0 for v in self.wave_remaining_spawns.values())
        ):
            self.wave += 1
            self.start_wave()



    def render(self, screen):

        offset_x, offset_y = (
            self.screenshake.update()
        )

        world_surface = pygame.Surface(
            screen.get_size()
        )

        self.world_manager.render_background(
            world_surface
        )

        if (
            self.world_manager.current_world ==
            self.world_manager.PLATFORMER
        ):

            for platform in self.platforms:
                platform.render(world_surface)

        else:

            for obstacle in self.obstacles:
                obstacle.render(world_surface)

        for projectile in self.projectiles:
            projectile.render(world_surface)

        for enemy in self.enemies:
            enemy.render(
                world_surface,
                self.world_manager
            )

        self.player.render(world_surface, screen)

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (255, 255, 255)
        )

        wave_text = self.font.render(
            f"WAVE {self.wave}",
            True,
            (255, 200, 80)
        )

        combo_text = self.font.render(
            f"Combo x{self.player.combo_multiplier}",
            True,
            (255, 255, 100)
        )

        health_text = self.font.render(
            f"HP: {self.player.health}",
            True,
            (255, 80, 80)
        )

        instability_text = self.font.render(
            f"Instability: {int(self.instability.level)}",
            True,
            (100, 180, 255)
        )


        screen.blit(
            world_surface,
            self.apply_camera((offset_x, offset_y))
        )

        screen.blit(score_text, (20, 20))
        screen.blit(wave_text, (20, 180))
        screen.blit(combo_text, (20, 60))
        screen.blit(health_text, (20, 100))
        screen.blit(instability_text, (20, 140))


        if self.show_tutorial_message:

            tutorial = self.font.render(
                "TAB swap | WASD move | LMB attack | SHIFT dash",
                True,
                (255, 255, 255)
            )

            screen.blit(
                tutorial,
                (50, HEIGHT - 80)
            )

        if self.wave_state == "countdown" and self.wave != 0:
            if self.wave_countdown > 0:
                msg = f"WAVE {self.wave}"
                sub = str(self.wave_countdown)
            else:
                msg = "WAVE START"
                sub = "FIGHT"

            title = self.font.render(msg, True, (255, 200, 80))
            subtext = self.font.render(sub, True, (255, 255, 255))

            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 40))
            screen.blit(subtext, (WIDTH//2 - subtext.get_width()//2, HEIGHT//2 + 10))