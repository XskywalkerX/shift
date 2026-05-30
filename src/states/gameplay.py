import pygame
import random
import math

from settings import *

from src.core.state_machine import State

from src.entities.player import Player
from src.entities.enemy import Enemy
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

        for _ in range(50):  # tries

            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)

            candidate = pygame.Rect(x, y, 40, 40)

            # avoid player too close
            if candidate.colliderect(self.player.rect.inflate(200, 200)):
                continue

            # avoid obstacles
            blocked = False
            for o in self.obstacles:
                if candidate.colliderect(o.rect):
                    blocked = True
                    break

            if blocked:
                continue

            self.enemies.append(Enemy(x, y))
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

    def update(self, dt):

        self.world_manager.update(dt)

        if self.hitstop.update(dt):
            return

        self.instability.update(dt)

        self.spawn_timer -= dt

        if self.spawn_timer <= 0:

            if len(self.enemies) < 8:
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

        if self.player.state in [
            "attack1",
            "attack2"
        ]:

            attack_box = self.player.get_attack_hitbox()

            for enemy in self.enemies:

                if attack_box.colliderect(enemy.rect):

                    enemy.health -= self.player.attack_damage

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

        self.player.render(world_surface)

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (255, 255, 255)
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

        world_surface.blit(score_text, (20, 20))
        world_surface.blit(combo_text, (20, 60))
        world_surface.blit(health_text, (20, 100))
        world_surface.blit(instability_text, (20, 140))

        screen.blit(
            world_surface,
            (offset_x, offset_y)
        )