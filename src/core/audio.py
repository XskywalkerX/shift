import pygame

class AudioManager:

    music_volume = 0.5
    sfx_volume = 0.5

    sounds = {}

    @classmethod
    def load(cls):

        cls.sounds["menu_move"] = pygame.mixer.Sound(
            "assets/audio/menu_move.ogg"
        )

        cls.sounds["menu_select"] = pygame.mixer.Sound(
            "assets/audio/menu_select.ogg"
        )

        cls.sounds["hit"] = pygame.mixer.Sound(
            "assets/audio/hit.wav"
        )

        cls.sounds["shot"] = pygame.mixer.Sound(
            "assets/audio/shot.wav"
        )

        cls.sounds["hurt"] = pygame.mixer.Sound(
            "assets/audio/hurt.wav"
        )

        cls.sounds["death"] = pygame.mixer.Sound(
            "assets/audio/death.wav"
        )
        cls.sounds["dash"] = pygame.mixer.Sound(
            "assets/audio/dash.mp3"
        )

        cls.update_volumes()

    @classmethod
    def update_volumes(cls):

        pygame.mixer.music.set_volume(
            cls.music_volume
        )

        for sound in cls.sounds.values():

            sound.set_volume(
                cls.sfx_volume
            )

    @classmethod
    def play(cls, sound_name):

        if sound_name in cls.sounds:

            cls.sounds[sound_name].play()

    @classmethod
    def play_music(cls, file):

        pygame.mixer.music.load(file)

        pygame.mixer.music.set_volume(
            cls.music_volume
        )

        pygame.mixer.music.play(-1)