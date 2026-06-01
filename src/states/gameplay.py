import pygame
import random
import math

from settings import *

from src.core.state_machine import State

from src.core.fonts import FONT_MEDIUM
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
from src.core.audio import AudioManager


class GameplayState(State):

    def __init__(self, game):
        super().__init__(game)

        self.wave_config = {
            1: {"basic": 5},
            2: {"basic": 10},
            3: {"basic": 15, "shooter": 5},
            4: {"basic": 17, "shooter": 8},
            5: {"basic": 20, "shooter": 9, "tank": 3},
        }

        self.crosshair_sprite = pygame.transform.scale(
            pygame.image.load(
                "assets/sprites/ui/crosshair.png"
            ).convert_alpha(),
            (40, 40)
        )

        pygame.mouse.set_visible(False)

        AudioManager.load()

        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.8  # start small like 1.2–1.5
        self.target_zoom = 2.0

        self.wave_started = False

        self.wave_remaining_spawns = {}

        self.show_tutorial_message = True

        self.wave_active_timer = 0

        self.wave = 0
        self.wave_state = "countdown"
        self.wave_timer = 1.0
        self.wave_countdown = 3
        self.wave_transitioning = False

        self.player = Player(500, WORLD_HEIGHT - 200)

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

        self.last_world = self.world_manager.current_world


        self.generate_world()

        AudioManager.play_music(
            "assets/audio/battle.mp3"
        )

    def generate_world(self):

        self.platforms.clear()
        self.obstacles.clear()

        # =========================
        # GROUND
        # =========================

        ground = Platform(
            0,
            WORLD_HEIGHT - 40,
            WORLD_WIDTH,
            40
        )

        self.platforms.append(ground)

        # =========================
        # MAIN PLATFORM PATH
        # =========================

        last_x = 150
        last_y = WORLD_HEIGHT - 180

        for _ in range(12):

            for attempt in range(100):

                width = random.randint(140, 260)

                x = last_x + random.randint(-250, 250)
                y = last_y + random.randint(-120, 120)

                x = max(
                    0,
                    min(
                        x,
                        WORLD_WIDTH - width
                    )
                )

                y = max(
                    120,
                    min(
                        y,
                        WORLD_HEIGHT - 200
                    )
                )

                candidate = pygame.Rect(
                    x,
                    y,
                    width,
                    30
                )

                overlap = False

                for platform in self.platforms:

                    if candidate.colliderect(
                        platform.rect.inflate(30, 30)
                    ):
                        overlap = True
                        break

                if overlap:
                    continue

                self.platforms.append(
                    Platform(
                        x,
                        y,
                        width,
                        30
                    )
                )

                last_x = x
                last_y = y

                break

        # =========================
        # EXTRA PLATFORMS
        # =========================

        for _ in range(6):

            for attempt in range(100):

                width = random.randint(120, 220)

                x = random.randint(
                    0,
                    WORLD_WIDTH - width
                )

                y = random.randint(
                    120,
                    WORLD_HEIGHT - 200
                )

                candidate = pygame.Rect(
                    x,
                    y,
                    width,
                    30
                )

                overlap = False

                for platform in self.platforms:

                    if candidate.colliderect(
                        platform.rect.inflate(30, 30)
                    ):
                        overlap = True
                        break

                if overlap:
                    continue

                self.platforms.append(
                    Platform(
                        x,
                        y,
                        width,
                        30
                    )
                )

                break

        # =========================
        # OBSTACLES
        # =========================

        for _ in range(10):

            for attempt in range(100):

                x = random.randint(
                    0,
                    WORLD_WIDTH - 80
                )

                y = random.randint(
                    0,
                    WORLD_HEIGHT - 80
                )

                candidate = pygame.Rect(
                    x,
                    y,
                    80,
                    80
                )

                blocked = False

                # player

                if candidate.colliderect(
                    self.player.rect.inflate(200, 200)
                ):
                    blocked = True

                # enemies

                if not blocked:

                    for enemy in self.enemies:

                        if candidate.colliderect(
                            enemy.rect.inflate(50, 50)
                        ):
                            blocked = True
                            break

                # platforms

                if not blocked:

                    for platform in self.platforms:

                        if candidate.colliderect(platform.rect):
                            blocked = True
                            break

                # obstacles

                if not blocked:

                    for obstacle in self.obstacles:

                        if candidate.colliderect(
                            obstacle.rect.inflate(40, 40)
                        ):
                            blocked = True
                            break

                if blocked:
                    continue

                self.obstacles.append(
                    Obstacle(
                        x,
                        y,
                        80,
                        80,
                        self.obstacle_sprite
                    )
                )

                break

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
            x = random.randint(0, WORLD_WIDTH - 40)
            y = random.randint(0, WORLD_HEIGHT - 40)

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

                    #if self.world_manager.current_world == self.last_world:
                    #    self.camera_zoom = 1.6
                    #else:
                    #    self.camera_zoom = 1.1

            if event.type == pygame.MOUSEBUTTONDOWN:

                if (
                    event.button == 1 and
                    self.world_manager.current_world ==
                    self.world_manager.SHOOTER
                ):
                    AudioManager.play("shot")

                    mouse_pos = pygame.mouse.get_pos()

                    player_screen_x = (
                        (self.player.rect.centerx - self.camera_x)
                        * self.camera_zoom
                    )

                    player_screen_y = (
                        (self.player.rect.centery - self.camera_y)
                        * self.camera_zoom
                    )

                    dx = mouse_pos[0] - player_screen_x
                    dy = mouse_pos[1] - player_screen_y

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

        visible_width = WIDTH / self.camera_zoom
        visible_height = HEIGHT / self.camera_zoom

        target_x = self.player.rect.centerx - visible_width / 2
        target_y = self.player.rect.centery - visible_height / 2

        target_x = max(
            0,
            min(target_x, WORLD_WIDTH - visible_width)
        )

        target_y = max(
            0,
            min(target_y, WORLD_HEIGHT - visible_height)
        )

        self.camera_x += (target_x - self.camera_x) * 0.08
        self.camera_y += (target_y - self.camera_y) * 0.08

        if self.player.state in [
            "attack1",
            "attack2"
        ]:
            AudioManager.play("hit")

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

            last_world = self.world_manager.current_world



    def render(self, screen):

        pygame.mouse.set_visible(False)

        offset_x, offset_y = (
            self.screenshake.update()
        )

        world_surface = pygame.Surface(
            (WORLD_WIDTH, WORLD_HEIGHT)
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

        self.player.render(world_surface, screen, self)

        score_text = FONT_MEDIUM.render(
            f"Score: {self.score}",
            True,
            (255, 255, 255)
        )

        wave_text = FONT_MEDIUM.render(
            f"Horda {self.wave}",
            True,
            (255, 200, 80)
        )

        combo_text = FONT_MEDIUM.render(
            f"Combo x{self.player.combo_multiplier}",
            True,
            (255, 255, 100)
        )

        zoomed_world = pygame.transform.scale(
            world_surface,
            (
                int(WORLD_WIDTH * self.camera_zoom),
                int(WORLD_HEIGHT * self.camera_zoom)
            )
        )

        screen.blit(
            zoomed_world,
            (
                -self.camera_x * self.camera_zoom + offset_x,
                -self.camera_y * self.camera_zoom + offset_y
            )
        )

        screen.blit(score_text, (20, 120))
        screen.blit(wave_text, (20, 180))
        screen.blit(combo_text, (20, 80))

        if self.show_tutorial_message:

            tutorial = FONT_MEDIUM.render(
                "TAB swap | WASD andar | LMB atacar | SHIFT dash",
                True,
                (255, 255, 255)
            )

            screen.blit(
                tutorial,
                (50, HEIGHT - 80)
            )

        if self.wave_state == "countdown" and self.wave != 0:
            if self.wave_countdown > 0:
                msg = f"HORDA {self.wave}"
                sub = str(self.wave_countdown)
            else:
                msg = "HORDA INICIANDO"
                sub = "LUTE PARA SOBREVIVER!"

            title = FONT_MEDIUM.render(msg, True, (255, 200, 80))
            subtext = FONT_MEDIUM.render(sub, True, (255, 255, 255))

            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 40))
            screen.blit(subtext, (WIDTH//2 - subtext.get_width()//2, HEIGHT//2 + 10))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        crosshair = pygame.transform.scale(
            self.crosshair_sprite,
            (120, 120)
        )

        crosshair_rect = crosshair.get_rect(
            center=(mouse_x, mouse_y)
        )
        screen.blit(
            crosshair,
            crosshair_rect
        )

        # HP background
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (20, 20, 300, 20)
        )

        # HP fill
        pygame.draw.rect(
            screen,
            (50, 255, 50),
            (
                20,
                20,
                300 * (self.player.health / self.player.max_health),
                20
            )
        )

        # Stamina background
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (20, 50, 300, 15)
        )

        # Stamina fill
        pygame.draw.rect(
            screen,
            (50, 150, 255),
            (
                20,
                50,
                300 * (self.player.stamina / self.player.max_stamina),
                15
            )
        )